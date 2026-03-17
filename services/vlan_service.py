from drivers.nxapi_driver import send_nxapi_commands
from drivers.ssh_driver import send_ssh_commands


def build_vlan_commands(vlan_id: int, vlan_name: str, trunk_interfaces: list[str]) -> list[str]:
    commands = [
        f"vlan {vlan_id}",
        f"name {vlan_name}"
    ]

    for interface in trunk_interfaces:
        commands.extend([
            f"interface {interface}",
            f"switchport trunk allowed vlan add {vlan_id}"
        ])

    return commands


def add_vlan_to_device(
    device: dict,
    vlan_id: int,
    vlan_name: str,
    nxapi_username: str,
    nxapi_password: str,
    ssh_username: str,
    ssh_password: str,
) -> dict:
    trunk_interfaces = device.get("trunk_interfaces", [])
    if not trunk_interfaces:
        raise ValueError(f"Device {device['device_name']} has no trunk interfaces in inventory.")

    commands = build_vlan_commands(vlan_id, vlan_name, trunk_interfaces)
    method = device.get("connection_method", "").lower()

    if method == "nxapi":
        result = send_nxapi_commands(
            device=device,
            commands=commands,
            username=nxapi_username,
            password=nxapi_password
        )
        return {
            "device": device["device_name"],
            "method": "nxapi",
            "trunk_interfaces": trunk_interfaces,
            "commands": commands,
            "result": result
        }

    if method == "ssh":
        result = send_ssh_commands(
            device=device,
            commands=commands,
            username=ssh_username,
            password=ssh_password
        )
        return {
            "device": device["device_name"],
            "method": "ssh",
            "trunk_interfaces": trunk_interfaces,
            "commands": commands,
            "result": result
        }

    raise ValueError(f"Unsupported connection method: {method}")