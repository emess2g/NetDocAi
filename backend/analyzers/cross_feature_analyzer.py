
import ipaddress


def analyze_dhcp_interface_consistency(dhcp, interfaces):
    """Compare DHCP pool subnets with configured Layer 3 interfaces."""
    findings = []

    if isinstance(dhcp, dict):
        pools = dhcp.get("pools", [])
    elif isinstance(dhcp, list):
        pools = dhcp
    else:
        return findings

    interfaces = interfaces or []

    # Build subnets only from interfaces with valid IPv4 addressing.
    interface_subnets = []

    for interface in interfaces:
        ip_address = interface.get("ip_address")
        subnet_mask = interface.get("subnet_mask")

        if not ip_address or not subnet_mask:
            continue

        try:
            subnet = ipaddress.IPv4Network(
                f"{ip_address}/{subnet_mask}",
                strict=False,
            )
        except (ipaddress.AddressValueError, ipaddress.NetmaskValueError):
            continue

        interface_subnets.append({
            "name": interface.get("name", "Unknown interface"),
            "subnet": subnet,
        })

    # Without any parsed Layer 3 addressing, there is insufficient
    # evidence to make a useful comparison.
    if not interface_subnets:
        return findings

    for pool in pools:
        pool_name = pool.get("name") or "Unnamed DHCP pool"
        network = pool.get("network")
        subnet_mask = pool.get("subnet_mask")

        if not network or not subnet_mask:
            continue

        try:
            pool_subnet = ipaddress.IPv4Network(
                f"{network}/{subnet_mask}",
                strict=False,
            )
        except (ipaddress.AddressValueError, ipaddress.NetmaskValueError):
            # The DHCP analyzer handles invalid pool addressing.
            continue

        matching_interfaces = [
            item
            for item in interface_subnets
            if item["subnet"] == pool_subnet
        ]

        if matching_interfaces:
            continue

        findings.append({
            "severity": "warning",
            "category": "cross_feature",
            "device": f"DHCP pool {pool_name}",
            "finding": (
                f"DHCP pool subnet {pool_subnet} does not match "
                "any configured Layer 3 interface subnet."
            ),
            "recommendation": (
                "Verify that the DHCP pool subnet matches the intended "
                "client network and that its gateway is reachable through "
                "the appropriate routed interface or gateway device."
            ),
            "evidence": {
                "dhcp_pool": pool_name,
                "dhcp_subnet": str(pool_subnet),
                "configured_interface_subnets": [
                    {
                        "interface": item["name"],
                        "subnet": str(item["subnet"]),
                    }
                    for item in interface_subnets
                ],
            },
        })

    return findings
 
def analyze_nat_interface_consistency(nat, interfaces):
    """Check NAT interface roles and references against parsed interfaces."""
    findings = []

    if not isinstance(nat, dict):
        return findings

    interfaces = interfaces or []

    configured_interfaces = {
        interface.get("name", "").strip().lower(): interface.get("name", "").strip()
        for interface in interfaces
        if isinstance(interface, dict) and interface.get("name")
    }

    inside_interfaces = nat.get("inside_interfaces", []) or []
    outside_interfaces = nat.get("outside_interfaces", []) or []

    inside_names = {
        name.strip().lower()
        for name in inside_interfaces
        if isinstance(name, str)
    }
    outside_names = {
        name.strip().lower()
        for name in outside_interfaces
        if isinstance(name, str)
    }

    # Detect interfaces assigned both NAT roles.
    for name in sorted(inside_names & outside_names):
        display_name = next(
            (
                item for item in inside_interfaces
                if isinstance(item, str) and item.strip().lower() == name
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

    # Collect NAT commands containing interface references.
    nat_commands = (
        (nat.get("dynamic", []) or [])
        + (nat.get("overload", []) or [])
    )

    referenced_interfaces = set()

    for entry in nat_commands:
        if not isinstance(entry, dict):
            continue

        command = entry.get("command", "")
        if not isinstance(command, str):
            continue

        parts = command.split()

        for index, token in enumerate(parts[:-1]):
            if token.lower() == "interface":
                referenced_interfaces.add(parts[index + 1])

    # Warn when a referenced interface is absent from parsed configuration.
    for referenced_name in sorted(referenced_interfaces):
        if referenced_name.strip().lower() in configured_interfaces:
            continue

        findings.append({
            "severity": "warning",
            "category": "cross_feature",
            "device": f"NAT rule referencing {referenced_name}",
            "finding": (
                f"NAT references interface {referenced_name}, "
                "but that interface was not found in the parsed configuration."
            ),
            "recommendation": (
                "Verify the interface name and confirm that the supplied "
                "configuration includes the relevant interface definition."
            ),
        })

    # Check the role of interfaces used by PAT overload rules.
    for entry in nat_commands:
        if not isinstance(entry, dict):
            continue

        command = entry.get("command", "")
        if not isinstance(command, str):
            continue

        parts = command.split()
        lowered_parts = [part.lower() for part in parts]

        if "overload" not in lowered_parts or "interface" not in lowered_parts:
            continue

        interface_index = lowered_parts.index("interface")

        if interface_index + 1 >= len(parts):
            continue

        referenced_name = parts[interface_index + 1]
        normalized_name = referenced_name.strip().lower()

        # The missing-interface check above already handles this case.
        if normalized_name not in configured_interfaces:
            continue

        configured_name = configured_interfaces[normalized_name]

        if (
            normalized_name in inside_names
            and normalized_name not in outside_names
        ):
            findings.append({
                "severity": "warning",
                "category": "cross_feature",
                "device": configured_name,
                "finding": (
                    f"NAT overload references interface {configured_name}, "
                    "but it is configured as NAT inside rather than NAT outside."
                ),
                "recommendation": (
                    "Verify the PAT interface selection. The interface used "
                    "by an interface-based NAT overload rule should normally "
                    "be configured with ip nat outside."
                ),
            })

    return findings


def analyze_dhcp_gateway_interface_consistency(dhcp, interfaces):
    """Compare DHCP pool default gateways with interface addresses."""
    findings = []

    if isinstance(dhcp, dict):
        pools = dhcp.get("pools", [])
    elif isinstance(dhcp, list):
        pools = dhcp
    else:
        return findings

    interfaces = interfaces or []

    # Index valid interface addresses by subnet.
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
            "ip_address": interface_ip,
            "network": interface_network,
        })

    for pool in pools:
        if not isinstance(pool, dict):
            continue

        pool_name = pool.get("name") or "Unnamed DHCP pool"
        network = pool.get("network")
        subnet_mask = pool.get("subnet_mask")
        gateways = pool.get("default_router", [])

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

        matching_interfaces = [
            item for item in interface_addresses
            if item["network"] == pool_network
        ]

        # Only compare gateways when an interface has the exact pool subnet.
        if not matching_interfaces:
            continue

        interface_ips = {
            item["ip_address"] for item in matching_interfaces
        }

        for gateway in gateways:
            try:
                gateway_ip = ipaddress.IPv4Address(gateway)
            except (ipaddress.AddressValueError, TypeError):
                continue

            if gateway_ip in interface_ips:
                continue

            findings.append({
                "severity": "warning",
                "category": "cross_feature",
                "device": f"DHCP pool {pool_name}",
                "finding": (
                    f"DHCP gateway {gateway_ip} for pool {pool_name} "
                    "does not match any interface address on subnet "
                    f"{pool_network}."
                ),
                "recommendation": (
                    "Verify the DHCP default-router address and confirm "
                    "that it identifies the intended gateway for this "
                    "client subnet. The gateway may also be a separate "
                    "router or Layer 3 device."
                ),
                "evidence": {
                    "dhcp_pool": pool_name,
                    "dhcp_subnet": str(pool_network),
                    "dhcp_gateway": str(gateway_ip),
                    "interface_addresses": [
                        {
                            "interface": item["name"],
                            "ip_address": str(item["ip_address"]),
                        }
                        for item in matching_interfaces
                    ],
                },
            })

    return findings
