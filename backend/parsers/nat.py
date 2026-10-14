
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

        # End the current interface context at section boundaries.
        if line == "!":
            current_interface = None
            continue

        # Interface context
        if line.startswith("interface "):
            current_interface = line.split(" ", 1)[1]
            continue

        # Global configuration commands must not inherit interface context.
        if not raw_line[0].isspace():
            current_interface = None

        # NAT roles on interfaces
        if current_interface:
            if line == "ip nat inside":
                if current_interface not in nat["inside_interfaces"]:
                    nat["inside_interfaces"].append(current_interface)
                continue

            if line == "ip nat outside":
                if current_interface not in nat["outside_interfaces"]:
                    nat["outside_interfaces"].append(current_interface)
                continue

        # NAT pool definitions
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

        # NAT translation rules
        if line.startswith("ip nat inside source "):
            parts = line.split()

            if " static " in f" {line} ":
                nat["static"].append({"command": line})
                continue

            if " overload" in line:
                nat["overload"].append({"command": line})
                continue

            if " pool " in f" {line} ":
                pool_index = parts.index("pool") if "pool" in parts else None

                entry = {"command": line}

                if pool_index is not None and pool_index + 1 < len(parts):
                    entry["pool_name"] = parts[pool_index + 1]

                nat["dynamic"].append(entry)
                continue

            if " interface " in f" {line} ":
                interface_index = parts.index("interface")

                entry = {"command": line}

                if interface_index + 1 < len(parts):
                    entry["interface_name"] = parts[interface_index + 1]

                nat["dynamic"].append(entry)


    return nat
