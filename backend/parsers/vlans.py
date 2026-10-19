
def parse_vlans(config: str):
    vlans = []
    current_vlan = None

    for raw_line in config.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        # End of a configuration section.
        if line == "!":
            current_vlan = None
            continue

        # Start VLAN configuration.
        if line.startswith("vlan "):
            parts = line.split()

            current_vlan = None

            if len(parts) < 2:
                continue

            vlan_id = parts[1]

            # Accept only valid numeric VLAN IDs.
            try:
                vlan_number = int(vlan_id)
            except ValueError:
                continue

            if not 1 <= vlan_number <= 4094:
                continue

            current_vlan = {
                "id": vlan_id,
                "name": None,
            }

            vlans.append(current_vlan)
            continue

        # Only process VLAN commands inside a valid VLAN section.
        if current_vlan is None:
            continue

        if line.startswith("name "):
            current_vlan["name"] = line.split(" ", 1)[1].strip()

    return vlans
