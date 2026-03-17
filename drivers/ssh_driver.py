from netmiko import ConnectHandler


def send_ssh_commands(device: dict, commands: list[str], username: str, password: str) -> str:
    conn = ConnectHandler(
        device_type="cisco_ios",
        host=device["ip_address"],
        username=username,
        password=password,
    )

    output = conn.send_config_set(commands)
    conn.save_config()
    conn.disconnect()
    return output