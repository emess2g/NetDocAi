
import re


def normalize_interface_name(name: str) -> str:
    """Expand common Cisco interface abbreviations."""
    name = name.strip()

    patterns = [
        (r"^fa(?=\d)", "FastEthernet"),
        (r"^f(?=\d)", "FastEthernet"),
        (r"^gi(?=\d)", "GigabitEthernet"),
        (r"^g(?=\d)", "GigabitEthernet"),
        (r"^te(?=\d)", "TenGigabitEthernet"),
        (r"^tu(?=\d)", "Tunnel"),
        (r"^lo(?=\d)", "Loopback"),
        (r"^vl(?=\d)", "Vlan"),
        (r"^po(?=\d)", "Port-channel"),
    ]

    for pattern, replacement in patterns:
        name = re.sub(pattern, replacement, name, count=1, flags=re.I)
        if name.lower().startswith(replacement.lower()):
            break

    return name


def create_interface(name: str) -> dict:
    """Return a consistently structured interface record."""
    return {
        "name": name,
        "description": None,
        "ip_address": None,
        "subnet_mask": None,
        "status": "up",
        "mode": None,
        "access_vlan": None,
        "voice_vlan": None,
        "allowed_vlans": None,
        "native_vlan": None,
        "portfast": False,
        "encapsulation_vlan": None,
    }


def expand_interface_range(expression: str) -> list[str]:
    """Expand Cisco interface ranges, including two- and three-part ports."""
    result = []

    def add(name):
        name = normalize_interface_name(name.strip())
        if name and name not in result:
            result.append(name)

    def expand(start_name, end_name):
        start_name = normalize_interface_name(start_name.strip())
        end_name = normalize_interface_name(end_name.strip())

        start_match = re.fullmatch(r"(.*/)(\d+)", start_name)
        end_match = re.fullmatch(r"(.*/)(\d+)", end_name)

        if not start_match or not end_match:
            add(start_name)
            return

        start_prefix, start_number = start_match.groups()
        end_prefix, end_number = end_match.groups()

        start_number = int(start_number)
        end_number = int(end_number)

        if (
            start_prefix != end_prefix
            or end_number < start_number
            or end_number - start_number > 256
        ):
            add(start_name)
            return

        for number in range(start_number, end_number + 1):
            add(f"{start_prefix}{number}")

    for item in expression.split(","):
        item = item.strip()

        if not item:
            continue

        # Full range: Gi1/0/1 - Gi1/0/4
        full_range = re.fullmatch(
            r"([A-Za-z-]+\d+(?:/\d+){1,2})"
            r"\s*-\s*"
            r"([A-Za-z-]+\d+(?:/\d+){1,2})",
            item,
            flags=re.I,
        )

        if full_range:
            expand(full_range.group(1), full_range.group(2))
            continue

        # Short range: Gi0/1-4, Gi1/0/1-4, or Fa0/3-4
        short_range = re.fullmatch(
            r"([A-Za-z-]+\d+(?:/\d+){1,2})"
            r"\s*-\s*(\d+)",
            item,
            flags=re.I,
        )

        if short_range:
            start_name, end_number = short_range.groups()
            start_name = normalize_interface_name(start_name)
            start_match = re.fullmatch(r"(.*/)(\d+)", start_name)

            if start_match:
                prefix, _ = start_match.groups()
                expand(start_name, f"{prefix}{end_number}")
            else:
                add(start_name)

            continue

        add(item)

    return result


def normalize_command(line: str) -> str:
    """Normalize common IOS abbreviations without altering descriptions."""
    line = line.strip()
    lower = line.lower()

    # Interface declarations
    if lower.startswith("int r "):
        return "interface range " + line[6:].strip()

    if lower.startswith("int "):
        return "interface " + line[4:].strip()

    replacements = [
        (r"^sw\s+mo\s+tr(?:\s.*)?$", "switchport mode trunk"),
        (
            r"^sw\s+tr\s+allow\s+vlan\s+(.+)$",
            r"switchport trunk allowed vlan \1",
        ),
        (r"^sw\s+mo\s+acc$", "switchport mode access"),
        (r"^sw\s+acc\s+vlan\s+(.+)$", r"switchport access vlan \1"),
        (r"^sw\s+voice\s+vlan\s+(.+)$", r"switchport voice vlan \1"),
        (r"^no\s+sh$", "no shutdown"),
        (r"^ip\s+add\s+(.+)$", r"ip address \1"),
        (r"^spanning\s+portfast$", "spanning-tree portfast"),
    ]

    for pattern, replacement in replacements:
        normalized = re.sub(pattern, replacement, line, flags=re.I)
        if normalized != line:
            return normalized

    return line


def parse_interfaces(config: str):
    """Parse interface configuration into consistently structured records."""
    interfaces = {}
    current_interfaces = []

    for raw_line in config.splitlines():
        line = raw_line.strip()

        if not line or line.startswith("!"):
            current_interfaces = []
            continue

        # Ignore common CLI session commands.
        if line.lower() in {
            "en",
            "enable",
            "conf t",
            "configure terminal",
            "end",
            "exit",
        }:
            if line.lower() in {"end", "exit"}:
                current_interfaces = []
            continue

        normalized = normalize_command(line)
        lower = normalized.lower()

        # Interface range declaration.
        if lower.startswith("interface range "):
            expression = normalized[len("interface range "):].strip()
            current_interfaces = expand_interface_range(expression)

            for name in current_interfaces:
                interfaces.setdefault(name, create_interface(name))

            continue

        # Single interface declaration.
        if lower.startswith("interface "):
            name = normalize_interface_name(
                normalized[len("interface "):].strip()
            )
            current_interfaces = [name]
            interfaces.setdefault(name, create_interface(name))
            continue

        if not current_interfaces:
            continue

        # Apply commands to each interface in the current range.
        for name in current_interfaces:
            interface = interfaces[name]

            if lower.startswith("description "):
                interface["description"] = normalized.split(" ", 1)[1].strip()

            elif lower.startswith("ip address "):
                parts = normalized.split()

                if len(parts) >= 4:
                    ip, mask = parts[2], parts[3]
                    ipv4_pattern = r"\d{1,3}(?:\.\d{1,3}){3}"

                    if (
                        re.fullmatch(ipv4_pattern, ip)
                        and re.fullmatch(ipv4_pattern, mask)
                    ):
                        octets = [int(part) for part in ip.split(".")]

                        if all(0 <= octet <= 255 for octet in octets):
                            try:
                                import ipaddress

                                ipaddress.IPv4Network(
                                    f"0.0.0.0/{mask}",
                                    strict=False,
                                )

                                interface["ip_address"] = ip
                                interface["subnet_mask"] = mask
                                interface["mode"] = "layer3"

                            except ValueError:
                                pass

            elif lower == "shutdown":
                interface["status"] = "shutdown"

            elif lower == "no shutdown":
                interface["status"] = "up"

            elif lower == "no switchport":
                interface["mode"] = "layer3"

            elif lower == "switchport":
                if interface["mode"] is None:
                    interface["mode"] = "access"

            elif lower == "switchport mode access":
                interface["mode"] = "access"

            elif lower == "switchport mode trunk":
                interface["mode"] = "trunk"

            elif lower.startswith("switchport access vlan "):
                interface["access_vlan"] = normalized.split()[-1]

            elif lower.startswith("switchport voice vlan "):
                interface["voice_vlan"] = normalized.split()[-1]

            elif lower.startswith("switchport trunk allowed vlan "):
                interface["allowed_vlans"] = normalized.split(
                    "vlan ", 1
                )[1].strip()

            elif lower.startswith("switchport trunk native vlan "):
                interface["native_vlan"] = normalized.split()[-1]

            elif lower == "spanning-tree portfast":
                interface["portfast"] = True

            elif lower.startswith("encapsulation dot1q "):
                parts = normalized.split()

                if len(parts) >= 3 and parts[2].isdigit():
                    vlan_id = int(parts[2])

                    if 1 <= vlan_id <= 4094:
                        interface["encapsulation_vlan"] = vlan_id

    return list(interfaces.values())
