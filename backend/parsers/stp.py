def parse_stp(config: str):
    stp = {
        "mode": None,
        "priority": None,
        "portfast_interfaces": [],
        "bpdu_guard_interfaces": [],
        "bpdu_filter_interfaces": [],
        "root_guard_interfaces": [],
        "loop_guard_interfaces": [],
    }

    current_interface = None

    for line in config.splitlines():
        line = line.strip()

        if line.startswith("spanning-tree mode "):
            stp["mode"] = line.split()[-1]

        elif line.startswith("spanning-tree vlan ") and " priority " in line:
            parts = line.split()
            priority_index = parts.index("priority")

            if priority_index + 1 < len(parts):
                stp["priority"] = parts[priority_index + 1]

        elif line.startswith("interface "):
            current_interface = line.split(" ", 1)[1]

        elif current_interface and line == "spanning-tree portfast":
            stp["portfast_interfaces"].append(current_interface)

        elif current_interface and line == "spanning-tree bpduguard enable":
            stp["bpdu_guard_interfaces"].append(current_interface)

        elif current_interface and line == "spanning-tree bpdufilter enable":
            stp["bpdu_filter_interfaces"].append(current_interface)

        elif current_interface and line == "spanning-tree guard root":
            stp["root_guard_interfaces"].append(current_interface)

        elif current_interface and line == "spanning-tree guard loop":
            stp["loop_guard_interfaces"].append(current_interface)

    return stp
