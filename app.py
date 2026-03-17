import json
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from services.vlan_service import add_vlan_to_device

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
INVENTORY_FILE = BASE_DIR / "inventory.json"
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
AUDIT_LOG = LOG_DIR / "audit.log"

logging.basicConfig(
    filename=str(AUDIT_LOG),
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

NXAPI_USERNAME = os.getenv("NXAPI_USERNAME")
NXAPI_PASSWORD = os.getenv("NXAPI_PASSWORD")
SSH_USERNAME = os.getenv("SSH_USERNAME")
SSH_PASSWORD = os.getenv("SSH_PASSWORD")

app = FastAPI(title="nexus_restapi_ssh")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def load_inventory() -> dict:
    if not INVENTORY_FILE.exists():
        raise FileNotFoundError(f"Inventory file not found: {INVENTORY_FILE}")

    with open(INVENTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_device_by_name(device_name: str) -> dict | None:
    inventory = load_inventory()
    for device in inventory.get("devices", []):
        if device.get("device_name") == device_name:
            return device
    return None


def check_credentials() -> None:
    missing = []

    if not NXAPI_USERNAME:
        missing.append("NXAPI_USERNAME")
    if not NXAPI_PASSWORD:
        missing.append("NXAPI_PASSWORD")
    if not SSH_USERNAME:
        missing.append("SSH_USERNAME")
    if not SSH_PASSWORD:
        missing.append("SSH_PASSWORD")

    if missing:
        raise ValueError(f"Missing environment variables: {', '.join(missing)}")


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    inventory = load_inventory()
    devices = inventory.get("devices", [])
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "devices": devices,
            "message": None,
            "error": None,
            "result": None
        }
    )


@app.post("/add-vlan", response_class=HTMLResponse)
def add_vlan(
    request: Request,
    device_name: str = Form(...),
    vlan_id: int = Form(...),
    vlan_name: str = Form(...)
):
    inventory = load_inventory()
    devices = inventory.get("devices", [])
    device = get_device_by_name(device_name)

    if not device:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "devices": devices,
                "message": None,
                "error": f"Device {device_name} not found.",
                "result": None
            }
        )

    try:
        check_credentials()

        result = add_vlan_to_device(
            device=device,
            vlan_id=vlan_id,
            vlan_name=vlan_name,
            nxapi_username=NXAPI_USERNAME,
            nxapi_password=NXAPI_PASSWORD,
            ssh_username=SSH_USERNAME,
            ssh_password=SSH_PASSWORD,
        )

        logging.info(
            "VLAN %s (%s) added to %s on trunk interfaces: %s",
            vlan_id,
            vlan_name,
            device_name,
            ", ".join(result["trunk_interfaces"])
        )

        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "devices": devices,
                "message": f"VLAN {vlan_id} ({vlan_name}) was successfully added to all trunk interfaces on {device_name}.",
                "error": None,
                "result": result
            }
        )

    except Exception as e:
        logging.exception("Failed to add VLAN")
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "devices": devices,
                "message": None,
                "error": str(e),
                "result": None
            }
        )