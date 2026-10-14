
def parse_ospf_processes(config: str):
    """Parse all Cisco IOS OSPF process sections."""
    processes = []
    current_ospf = None

    section_starters = (
        "router ",
        "interface ",
        "ip ",
        "ipv6 ",
        "line ",
        "vlan ",
        "hostname ",
        "access-list ",
        "spanning-tree ",
        "banner ",
        "control-plane",
    )

    for raw_line in config.splitlines():
        line = raw_line.strip()

        if not line or line == "!":
            continue

        if line.startswith("router ospf "):
            parts = line.split()
            process_id = parts[2] if len(parts) >= 3 else None

            current_ospf = {
                "process_id": process_id,
                "router_id": None,
                "networks": [],
                "passive_interfaces": [],
            }
            processes.append(current_ospf)
            continue

        if current_ospf is None:
            continue

        # Stop at any new top-level configuration section.
        if line.startswith(section_starters):
            current_ospf = None
            continue

        if line.startswith("router-id "):
            parts = line.split()
            if len(parts) >= 2:
                current_ospf["router_id"] = parts[1]

        elif line.startswith("network "):
            parts = line.split()
            if len(parts) >= 5 and parts[3] == "area":
                current_ospf["networks"].append({
                    "network": parts[1],
                    "wildcard": parts[2],
                    "area": parts[4],
                })

        elif line.startswith("passive-interface "):
            parts = line.split(maxsplit=1)
            if len(parts) == 2:
                current_ospf["passive_interfaces"].append(parts[1])

    return processes


def parse_ospf(config: str):
    """Backward-compatible parser returning the first OSPF process."""
    processes = parse_ospf_processes(config)
    return processes[0] if processes else None


def parse_eigrp_processes(config: str):
    """Parse all classic Cisco IOS EIGRP process sections."""
    processes = []
    current_eigrp = None

    section_starters = (
        "router ",
        "interface ",
        "ip ",
        "ipv6 ",
        "line ",
        "vlan ",
        "hostname ",
        "access-list ",
        "spanning-tree ",
        "banner ",
        "control-plane",
    )

    for raw_line in config.splitlines():
        line = raw_line.strip()

        if not line or line == "!":
            continue

        if line.startswith("router eigrp "):
            parts = line.split()

            current_eigrp = {
                "as_number": parts[2],
                "networks": [],
                "passive_interfaces": [],
            }
            processes.append(current_eigrp)
            continue

        if current_eigrp is None:
            continue

        if line.startswith(section_starters):
            current_eigrp = None
            continue

        if line.startswith("network "):
            parts = line.split()
            if len(parts) >= 2:
                current_eigrp["networks"].append(parts[1])

        elif line.startswith("passive-interface "):
            parts = line.split(maxsplit=1)
            if len(parts) == 2:
                current_eigrp["passive_interfaces"].append(parts[1])

    return processes


def parse_eigrp(config: str):
    """Backward-compatible parser returning the first EIGRP process."""
    processes = parse_eigrp_processes(config)
    return processes[0] if processes else None




def parse_static_routes(config: str):
    routes = []

    for raw_line in config.splitlines():
        line = raw_line.strip()

        if not line.startswith("ip route "):
            continue

        parts = line.split()

        if len(parts) < 4:
            continue

        route = {
            "destination": parts[2],
            "mask": parts[3],
            "next_hop": None,
            "exit_interface": None,
        }

        remaining = parts[4:]

        for value in remaining:
            if value.startswith((
                "GigabitEthernet",
                "FastEthernet",
                "Ethernet",
                "Serial",
                "Loopback",
                "Port-channel",
                "Vlan",
            )):
                route["exit_interface"] = value
                break

            elif route["next_hop"] is None:
                route["next_hop"] = value

        routes.append(route)

    return routes


def parse_bgp(config: str):
    bgp = None
    current_bgp = False

    for raw_line in config.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        # Enter BGP configuration mode
        if line.startswith("router bgp "):
            bgp = {
                "as": line.split()[-1],
                "router_id": None,
                "neighbors": [],
                "networks": [],
            }

            current_bgp = True
            continue

        if not current_bgp:
            continue

        # End of BGP section
        if line == "!":
            current_bgp = False
            continue

        # Another top-level configuration section
        if line.startswith((
            "router ",
            "interface ",
            "line ",
            "vlan ",
            "ip ",
            "access-list ",
            "spanning-tree ",
            "cdp ",
            "hostname ",
        )):
            current_bgp = False
            continue

        # BGP router ID
        if line.startswith("bgp router-id "):
            bgp["router_id"] = line.split()[-1]
            continue

        # BGP neighbor
        if line.startswith("neighbor "):
            parts = line.split()

            if len(parts) >= 4 and parts[2] == "remote-as":
                bgp["neighbors"].append({
                    "address": parts[1],
                    "remote_as": parts[3],
                })

            continue

        # BGP network
        if line.startswith("network "):
            parts = line.split()

            if len(parts) >= 2:
                network = {
                    "network": parts[1],
                    "mask": None,
                }

                if "mask" in parts:
                    mask_index = parts.index("mask")

                    if mask_index + 1 < len(parts):
                        network["mask"] = parts[mask_index + 1]

                bgp["networks"].append(network)

    return bgp
