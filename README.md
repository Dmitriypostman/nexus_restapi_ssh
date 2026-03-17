# Network Automation Portal (NX-API + SSH)

This application automates VLAN provisioning across multiple Cisco devices 
(Nexus via NX-API and Catalyst via SSH) using a centralized web interface.

It allows:
- Creating VLANs
- Automatically adding VLANs to trunk interfaces
- Managing multiple devices from inventory
- Using different connection methods (NX-API / SSH)

Components:
- FastAPI (Web API)
- NX-API driver (for Nexus devices)
- SSH driver (Netmiko for Catalyst)
- Inventory (JSON-based device source)
- Service layer (business logic)

Project Structure:
project/
├─ app.py                # API entry point
├─ inventory.json       # Device inventory
├─ drivers/             # Device communication
├─ services/            # Business logic
├─ templates/           # Web UI

How to Run:
git clone https://github.com/Dmitriypostman/network-automation-portal
cd nexus_restapi_ssh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# fill credentials
Update the inventory.json file
uvicorn app:app --reload

What I learned:
- Difference between NX-API and SSH automation
- Handling multiple device types
- Structuring code into drivers/services
- Using environment variables securely
- Building reusable automation architecture
