
import ipaddress


def analyze_dhcp_interface_consistency(dhcp, interfaces):
    """Compare DHCP pool subnets with configured Layer 3 interface subnets."""
    findings = []

    if isinstance(dhcp, dict):
        pools = dhcp.get("pools", [])
    elif isinstance(dhcp, list):
        pools = dhcp
    else:
        return findings

    if not isinstance(pools, list):
        return findings

    if not isinstance(interfaces, list):
        interfaces = []

    interface_subnets = []

    for interface in interfaces:
        if not isinstance(interface, dict):
            continue

        ip_address = interface.get("ip_address")
        subnet_mask = interface.get("subnet_mask")

        if not ip_address or not subnet_mask:
            continue

        try:
            network = ipaddress.IPv4Network(
                f"{ip_address}/{subnet_mask}",
                strict=False,
            )
        except (ipaddress.AddressValueError, ipaddress.NetmaskValueError):
            continue

        interface_subnets.append({
            "name": interface.get("name", "Unknown interface"),
            "network": str(network),
        })

    if not interface_subnets:
        return findings

    for pool in pools:
        if not isinstance(pool, dict):
            continue

        network = pool.get("network")
        subnet_mask = pool.get("subnet_mask")

        if not network or not subnet_mask:
            continue

        try:
            pool_network = ipaddress.IPv4Network(
                f"{network}/{subnet_mask}",
                strict=False,
            )
        except (ipaddress.AddressValueError, ipaddress.NetmaskValueError):
            continue

        matching_interfaces = [
            item
            for item in interface_subnets
            if item["network"] == str(pool_network)
        ]

        if matching_interfaces:
            continue

        findings.append({
            "severity": "warning",
            "category": "cross_feature",
            "device": pool.get("name", "DHCP pool"),
            "finding": (
                f"DHCP pool {pool.get('name', 'Unknown')} uses subnet "
                f"{pool_network}, which does not match any configured "
                "Layer 3 interface subnet."
            ),
            "recommendation": (
                "Verify that the DHCP pool serves the intended client "
                "network and that its gateway is reachable through the "
                "appropriate routed interface or DHCP relay."
            ),
            "evidence": {
                "dhcp_pool": pool.get("name", "Unknown"),
                "dhcp_subnet": str(pool_network),
                "interface_subnets": [
                    item["network"] for item in interface_subnets
                ],
            },
        })

    return findings


def analyze_nat_interface_consistency(nat, interfaces):
    """Check NAT interface roles and references against parsed interfaces."""
    findings = []

    if not isinstance(nat, dict):
        return findings

    if not isinstance(interfaces, list):
        interfaces = []

    configured_interfaces = {
        interface["name"].strip().lower(): interface["name"].strip()
        for interface in interfaces
        if (
            isinstance(interface, dict)
            and isinstance(interface.get("name"), str)
            and interface["name"].strip()
        )
    }

    inside_interfaces = nat.get("inside_interfaces", [])
    if not isinstance(inside_interfaces, list):
        inside_interfaces = []

    outside_interfaces = nat.get("outside_interfaces", [])
    if not isinstance(outside_interfaces, list):
        outside_interfaces = []

    inside_names = {
        name.strip().lower()
        for name in inside_interfaces
        if isinstance(name, str) and name.strip()
    }

    outside_names = {
        name.strip().lower()
        for name in outside_interfaces
        if isinstance(name, str) and name.strip()
    }

    # Detect interfaces assigned both NAT roles.
    for name in sorted(inside_names & outside_names):
        display_name = next(
            (
                item.strip()
                for item in inside_interfaces
                if isinstance(item, str)
                and item.strip().lower() == name
            ),
            name,
        )

        findings.append({
            "severity": "warning",
            "category": "cross_feature",
            "device": display_name,
            "finding": (
                f"Interface {display_name} is configured as both "
                "NAT inside and NAT outside."
            ),
            "recommendation": (
                "Verify the intended NAT boundary and correct the interface "
                "roles if this overlap is not intentional."
            ),
        })

    # Normalize NAT command collections before combining them.
    dynamic_commands = nat.get("dynamic", [])
    if not isinstance(dynamic_commands, list):
        dynamic_commands = []

    overload_commands = nat.get("overload", [])
    if not isinstance(overload_commands, list):
        overload_commands = []

    nat_commands = dynamic_commands + overload_commands

    # Detect NAT commands referencing interfaces absent from parsed config.
    for entry in nat_commands:
        if not isinstance(entry, dict):
            continue

        command = entry.get("command")
        if not isinstance(command, str):
            continue

        tokens = command.split()

        for index, token in enumerate(tokens[:-1]):
            if token.lower() != "interface":
                continue

            interface_name = tokens[index + 1]
            if interface_name.lower() in configured_interfaces:
                continue

            findings.append({
                "severity": "warning",
                "category": "cross_feature",
                "device": interface_name,
                "finding": (
                    f"NAT configuration references interface "
                    f"{interface_name}, which was not found in the "
                    "parsed interface configuration."
                ),
                "recommendation": (
                    "Verify the interface name and confirm that the "
                    "interface configuration was included in the input."
                ),
            })

    # Check overload rules against the configured NAT inside interfaces.
    for entry in overload_commands:
        if not isinstance(entry, dict):
            continue

        command = entry.get("command")
        if not isinstance(command, str):
            continue

        tokens = command.split()
        lowered_tokens = [token.lower() for token in tokens]

        if "overload" not in lowered_tokens or "interface" not in lowered_tokens:
            continue

        for index, token in enumerate(lowered_tokens[:-1]):
            if token != "interface":
                continue

            interface_name = tokens[index + 1]
            normalized_name = interface_name.strip().lower()

            if (
                normalized_name in configured_interfaces
                and normalized_name in inside_names
            ):
                findings.append({
                    "severity": "warning",
                    "category": "cross_feature",
                    "device": interface_name,
                    "finding": (
                        f"NAT overload uses interface {interface_name}, "
                        "which is configured as NAT inside rather than NAT outside."
                    ),
                    "recommendation": (
                        "Verify that the overload rule references the intended "
                        "NAT outside interface."
                    ),
                })
    return findings


def analyze_dhcp_gateway_interface_consistency(dhcp, interfaces):
    """Compare DHCP default gateways with interface IPs on matching subnets."""
    findings = []

    if isinstance(dhcp, dict):
        pools = dhcp.get("pools", [])
    elif isinstance(dhcp, list):
        pools = dhcp
    else:
        return findings

    if not isinstance(pools, list):
        return findings

    if not isinstance(interfaces, list):
        interfaces = []

    interface_addresses = []

    for interface in interfaces:
        if not isinstance(interface, dict):
            continue

        ip_address = interface.get("ip_address")
        subnet_mask = interface.get("subnet_mask")

        if not ip_address or not subnet_mask:
            continue

        try:
            interface_ip = ipaddress.IPv4Address(ip_address)
            interface_network = ipaddress.IPv4Network(
                f"{ip_address}/{subnet_mask}",
                strict=False,
            )
        except (ipaddress.AddressValueError, ipaddress.NetmaskValueError):
            continue

        interface_addresses.append({
            "name": interface.get("name", "Unknown interface"),
            "ip_address": str(interface_ip),
            "network": str(interface_network),
        })

    for pool in pools:
        if not isinstance(pool, dict):
            continue

        network = pool.get("network")
        subnet_mask = pool.get("subnet_mask")
        gateways = pool.get("default_router")

        if not network or not subnet_mask or not gateways:
            continue

        try:
            pool_network = ipaddress.IPv4Network(
                f"{network}/{subnet_mask}",
                strict=False,
            )
        except (ipaddress.AddressValueError, ipaddress.NetmaskValueError):
            continue

        if isinstance(gateways, str):
            gateways = [gateways]

        if not isinstance(gateways, list):
            continue

        matching_interfaces = [
            item
            for item in interface_addresses
            if item["network"] == str(pool_network)
        ]

        # Only compare gateways when an interface has the same subnet.
        # The gateway may legitimately reside on another router or L3 device.
        if not matching_interfaces:
            continue

        interface_ips = {
            item["ip_address"] for item in matching_interfaces
        }

        for gateway in gateways:
            if not isinstance(gateway, str):
                continue

            try:
                gateway_ip = ipaddress.IPv4Address(gateway)


            except ipaddress.AddressValueError:
                continue

            if str(gateway_ip) in interface_ips:
                continue

            findings.append({
                "severity": "warning",
                "category": "cross_feature",
                "device": pool.get("name", "DHCP pool"),
                "finding": (
                    f"DHCP gateway {gateway_ip} in pool "
                    f"{pool.get('name', 'Unknown')} does not match any configured "
                    f"interface IP on subnet {pool_network}."
                ),
                "recommendation": (
                    "Verify the DHCP default gateway. It may belong to a "
                    "separate router or Layer 3 device on the same subnet."
                ),
                "evidence": {
                    "dhcp_pool": pool.get("name", "Unknown"),
                    "dhcp_subnet": str(pool_network),
                    "dhcp_gateway": str(gateway_ip),
                    "interface_ips": sorted(interface_ips),
                },
            })

    return findings
