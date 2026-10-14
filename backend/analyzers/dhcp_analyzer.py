import ipaddress


def analyze_dhcp(dhcp):
    findings = []

    if not dhcp:
        return findings

    # The parser returns a list, but also accept {"pools": [...]}.
    if isinstance(dhcp, dict):
        pools = dhcp.get("pools", [])
    elif isinstance(dhcp, list):
        pools = dhcp
    else:
        return findings

    for pool in pools:
        pool_name = pool.get("name") or "Unnamed"
        network = pool.get("network")
        subnet_mask = pool.get("subnet_mask")
        default_router = pool.get("default_router")
        dns_servers = pool.get("dns_servers", [])

        if not default_router:
            findings.append({
                "severity": "warning",
                "category": "dhcp",
                "device": f"DHCP pool {pool_name}",
                "finding": "DHCP pool has no default gateway configured.",
                "recommendation": (
                    "Configure the appropriate default-router "
                    "for the DHCP pool."
                ),
            })

        elif network and subnet_mask:
            try:
                subnet = ipaddress.IPv4Network(
                    f"{network}/{subnet_mask}",
                    strict=False,
                )
                gateway = ipaddress.IPv4Address(default_router)

                if gateway not in subnet:
                    findings.append({
                        "severity": "high",
                        "category": "dhcp",
                        "device": f"DHCP pool {pool_name}",
                        "finding": (
                            f"Default gateway {gateway} is outside "
                            f"the configured subnet {subnet}."
                        ),
                        "recommendation": (
                            "Configure a gateway within the DHCP pool's "
                            "the DHCP pool's subnet and verify the router interface."
                        ),
                    })
                elif gateway in {
                    subnet.network_address,
                    subnet.broadcast_address,
                }:
                    findings.append({
                        "severity": "high",
                        "category": "dhcp",
                        "device": f"DHCP pool {pool_name}",
                        "finding": (
                            f"Default gateway {gateway} is a network "
                            "or broadcast address, not a usable host address."
                        ),
                        "recommendation": (
                            "Configure a usable host address as the "
                            "default gateway."
                        ),
                    })

            except ValueError:
                findings.append({
                    "severity": "high",
                    "category": "dhcp",
                    "device": f"DHCP pool {pool_name}",
                    "finding": (
                        "The DHCP pool contains an invalid IPv4 network, "
                        "subnet mask, or default gateway."
                    ),
                    "recommendation": (
                        "Verify the network, subnet mask, and "
                        "default-router address."
                    ),
                })

        if not dns_servers:
            findings.append({
                "severity": "warning",
                "category": "dhcp",
                "device": f"DHCP pool {pool_name}",
                "finding": "DHCP pool has no DNS server configured.",
                "recommendation": (
                    "Configure one or more DNS servers for the pool."
                ),
            })

    return findings

