
def parse_nat(config: str):
    nat = {
        "inside_interfaces": [],
        "outside_interfaces": [],
        "static": [],
        "dynamic": [],
        "overload": [],
        "pools": [],
    }

    current_interface = None

    for raw_line in config.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        if line == "!":
            current_interface = None
            continue

        if line.startswith("interface "):
            current_interface = line.split(" ", 1)[1]
            continue

        # Global commands must not inherit interface context.
        if not raw_line[0].isspace():
            current_interface = None

        if current_interface:
            if line == "ip nat inside":
                if current_interface not in nat["inside_interfaces"]:
                    nat["inside_interfaces"].append(current_interface)
                continue

            if line == "ip nat outside":
                if current_interface not in nat["outside_interfaces"]:
                    nat["outside_interfaces"].append(current_interface)
                continue

        if line.startswith("ip nat pool "):
            parts = line.split()

            if len(parts) >= 8 and parts[6] == "netmask":
                nat["pools"].append({
                    "name": parts[3],
                    "start": parts[4],
                    "end": parts[5],
                    "netmask": parts[7],
                })
            continue

        if not line.startswith("ip nat inside source "):
            continue

        parts = line.split()

        if "static" in parts:
            nat["static"].append({"command": line})
            continue

        entry = {"command": line}

        if "pool" in parts:
            pool_index = parts.index("pool")
            if pool_index + 1 < len(parts):
                entry["pool_name"] = parts[pool_index + 1]

        if "interface" in parts:
            interface_index = parts.index("interface")
            if interface_index + 1 < len(parts):
                entry["interface_name"] = parts[interface_index + 1]

        if "overload" in parts:
            nat["overload"].append(entry)
        elif "pool" in parts or "interface" in parts:
            nat["dynamic"].append(entry)

    return nat
