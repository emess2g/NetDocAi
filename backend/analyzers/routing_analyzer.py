import ipaddress


def analyze_ospf_processes(ospf_processes):
    """Analyze every parsed OSPF process."""
    findings = []

    for ospf in ospf_processes or []:
        process_id = ospf.get("process_id", "unknown")

        if not ospf.get("router_id"):
            findings.append({
                "severity": "warning",
                "category": "routing",
                "device": f"OSPF process {process_id}",
                "finding": (
                    f"OSPF process {process_id} "
                    "has no explicitly configured router ID."
                ),
                "recommendation": (
                    "Configure a stable OSPF router ID "
                    f"for process {process_id}."
                ),
            })

        if not ospf.get("networks"):
            findings.append({
                "severity": "warning",
                "category": "routing",
                "device": f"OSPF process {process_id}",
                "finding": (
                    f"OSPF process {process_id} "
                    "has no network statements."
                ),
                "recommendation": (
                    "Verify that the intended networks are "
                    f"included in OSPF process {process_id}."
                ),
            })

    return findings


def analyze_eigrp_processes(eigrp_processes):
    """Analyze every parsed classic EIGRP process."""
    findings = []

    for eigrp in eigrp_processes or []:
        as_number = eigrp.get("as_number", "unknown")

        if not eigrp.get("networks"):
            findings.append({
                "severity": "warning",
                "category": "routing",
                "device": f"EIGRP AS {as_number}",
                "finding": (
                    f"EIGRP AS {as_number} "
                    "has no network statements."
                ),
                "recommendation": (
                    "Verify that the intended networks are "
                    f"included in EIGRP AS {as_number}."
                ),
            })

    return findings


def analyze_routing(ospf, eigrp, static_routes, bgp):
    """Analyze OSPF, EIGRP, static routes, and BGP."""
    findings = []

    # OSPF checks.
    if ospf:
        if not ospf.get("router_id"):
            findings.append({
                "severity": "warning",
                "category": "routing",
                "device": "OSPF",
                "finding": "OSPF router ID is not explicitly configured.",
                "recommendation": "Configure a stable OSPF router ID.",
            })

        if not ospf.get("networks"):
            findings.append({
                "severity": "warning",
                "category": "routing",
                "device": "OSPF",
                "finding": "OSPF has no network statements.",
                "recommendation": (
                    "Verify that the intended networks are included in OSPF."
                ),
            })

    # EIGRP checks.
    if eigrp:
        if not eigrp.get("networks"):
            findings.append({
                "severity": "warning",
                "category": "routing",
                "device": "EIGRP",
                "finding": "EIGRP has no network statements.",
                "recommendation": (
                    "Verify that the intended networks are included in EIGRP."
                ),
            })

    # Static-route checks.
    for route in static_routes or []:
        destination = route.get("destination")
        mask = route.get("mask")
        next_hop = route.get("next_hop")
        exit_interface = route.get("exit_interface")

        # Validate the destination IPv4 address.
        destination_valid = True

        try:
            destination_ip = ipaddress.IPv4Address(destination)
        except (ipaddress.AddressValueError, TypeError):
            destination_valid = False
            destination_ip = None

            findings.append({
                "severity": "warning",
                "category": "routing",
                "device": "Static route",
                "finding": (
                    "Static route has an invalid destination IPv4 address."
                ),
                "recommendation": (
                    "Configure a valid IPv4 destination address."
                ),
            })

        # Validate the subnet mask and ensure it is contiguous.
        mask_valid = True

        try:
            ipaddress.IPv4Network(
                f"0.0.0.0/{mask}",
                strict=False,
            )
        except (
            ipaddress.NetmaskValueError,
            ipaddress.AddressValueError,
            TypeError,
        ):
            mask_valid = False

            findings.append({
                "severity": "warning",
                "category": "routing",
                "device": "Static route",
                "finding": (
                    "Static route has an invalid or non-contiguous subnet mask."
                ),
                "recommendation": (
                    "Configure a valid contiguous IPv4 subnet mask."
                ),
            })

        # Verify that the destination matches its network address.
        if destination_valid and mask_valid:
            network = ipaddress.IPv4Network(
                f"{destination}/{mask}",
                strict=False,
            )

            if destination_ip != network.network_address:
                findings.append({
                    "severity": "warning",
                    "category": "routing",
                    "device": "Static route",
                    "finding": (
                        "Static route destination is not the correct "
                        "network address for its subnet mask."
                    ),
                    "recommendation": (
                        f"Use network address {network.network_address} "
                        f"for subnet mask {mask}."
                    ),
                })

        # Validate the next-hop IPv4 address when provided.
        if next_hop:
            try:
                ipaddress.IPv4Address(next_hop)
            except (ipaddress.AddressValueError, TypeError):
                findings.append({
                    "severity": "warning",
                    "category": "routing",
                    "device": "Static route",
                    "finding": (
                        "Static route has an invalid next-hop IPv4 address."
                    ),
                    "recommendation": (
                        "Configure a valid next-hop IPv4 address "
                        "or use an appropriate exit interface."
                    ),
                })

        # Require either a next hop or an exit interface.
        if not next_hop and not exit_interface:
            findings.append({
                "severity": "warning",
                "category": "routing",
                "device": "Static route",
                "finding": (
                    "Static route has no next-hop or exit interface."
                ),
                "recommendation": (
                    "Configure a valid next-hop address or exit interface."
                ),
            })

    # BGP checks.
    if bgp:
        if not bgp.get("router_id"):
            findings.append({
                "severity": "warning",
                "category": "routing",
                "device": "BGP",
                "finding": "BGP router ID is not explicitly configured.",
                "recommendation": "Configure a stable BGP router ID.",
            })

        if not bgp.get("neighbors"):
            findings.append({
                "severity": "warning",
                "category": "routing",
                "device": "BGP",
                "finding": "BGP has no neighbors configured.",
                "recommendation": "Configure the required BGP neighbors.",
            })

    return findings

