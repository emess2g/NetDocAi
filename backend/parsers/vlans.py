def parse_vlans(config: str):
    vlans = []
    current_vlan = None

    for raw_line in config.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        # End of a configuration section
        if line == "!":
            current_vlan = None
            continue

        # Start VLAN configuration
        if line.startswith("vlan "):
            parts = line.split()

            if len(parts) >= 2:
                vlan_id = parts[1]

                current_vlan = {
                    "id": vlan_id,
                    "name": None
                }

                vlans.append(current_vlan)

            continue

        # Only process VLAN commands while inside a VLAN section
        if not current_vlan:
            continue

        if line.startswith("name "):
            current_vlan["name"] = line.split(" ", 1)[1].strip()

    return vlans
