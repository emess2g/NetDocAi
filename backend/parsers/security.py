import re


def parse_security(config: str):
    security = {
        "ssh": False,
        "telnet": False,
        "http": False,
        "https": False,
        "enable_secret": False,
        "plaintext_passwords": False,
        "ssh_domain": None,
        "ssh_rsa": False,
        "local_users": [],
        "vty_lines": [],
        "vty_transport": [],
        "vty_access_class": [],
        "service_password_encryption": False,
    }

    # Global security settings
    for line in config.splitlines():
        line = line.strip()

        if line.startswith("ip ssh version"):
            security["ssh"] = True

        elif line.startswith("ip ssh "):
            security["ssh"] = True

        elif line.startswith("ip http secure-server"):
            security["https"] = True

        elif line.startswith("ip http server"):
            security["http"] = True

        elif line.startswith("enable secret "):
            security["enable_secret"] = True

        elif line.startswith("enable password "):
            security["plaintext_passwords"] = True

        elif line == "service password-encryption":
            security["service_password_encryption"] = True

        elif line.startswith("ip domain-name "):
            security["ssh_domain"] = line.split(" ", 2)[2]

        elif line.startswith("crypto key generate rsa"):
            security["ssh_rsa"] = True

        elif line.startswith("username "):
            parts = line.split()

            if len(parts) >= 2:
                security["local_users"].append(parts[1])

    # VTY blocks
    lines = config.splitlines()
    current_vty = None

    for raw_line in lines:
        stripped = raw_line.strip()

        if stripped.startswith("line vty "):
            current_vty = stripped[len("line vty "):]

            if current_vty not in security["vty_lines"]:
                security["vty_lines"].append(current_vty)

            continue

        # A new top-level configuration section ends the VTY block.
        if (
            stripped.startswith("line ")
            and not stripped.startswith("line vty ")
        ):
            current_vty = None
            continue

        if current_vty is None:
            continue

        if stripped.startswith("transport input "):
            transport = stripped[len("transport input "):]

            security["vty_transport"].append({
                "line": current_vty,
                "transport": transport,
            })

            transport_methods = transport.split()

            if "ssh" in transport_methods:
                security["ssh"] = True

            if "telnet" in transport_methods:
                security["telnet"] = True

        elif stripped.startswith("access-class "):
            parts = stripped.split()

            if len(parts) >= 2:
                security["vty_access_class"].append({
                    "line": current_vty,
                    "access_class": parts[1],
                })

    return security
