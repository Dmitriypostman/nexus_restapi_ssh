import requests


def send_nxapi_commands(device: dict, commands: list[str], username: str, password: str) -> dict:
    url = f"http://{device['ip_address']}/ins"

    payload = {
        "ins_api": {
            "version": "1.0",
            "type": "cli_conf",
            "chunk": "0",
            "sid": "1",
            "input": " ; ".join(commands),
            "output_format": "json"
        }
    }

    response = requests.post(
        url,
        json=payload,
        auth=(username, password),
        headers={"content-type": "application/json"},
        timeout=15
    )
    response.raise_for_status()
    return response.json()