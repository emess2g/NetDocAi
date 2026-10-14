
def analyze_nat(nat):
    findings = []

    if not nat:
        return findings

    inside_interfaces = nat.get("inside_interfaces", [])
    outside_interfaces = nat.get("outside_interfaces", [])
    static_entries = nat.get("static", [])
    dynamic_entries = nat.get("dynamic", [])
    overload_entries = nat.get("overload", [])
    pools = nat.get("pools", [])

    # Collect configured pool names for reference validation.
    configured_pool_names = {
        pool.get("name")
        for pool in pools
        if pool.get("name")
    }

    # Check NAT interface roles.
    if inside_interfaces and not outside_interfaces:
        findings.append({
            "severity": "warning",
            "category": "nat",
            "device": "NAT",
            "finding": (
                "NAT inside interfaces are configured but no NAT "
                "outside interface was detected."
            ),
            "recommendation": (
                "Verify that the correct external interface is "
                "configured with ip nat outside."
            )
        })

    if outside_interfaces and not inside_interfaces:
        findings.append({
            "severity": "warning",
            "category": "nat",
            "device": "NAT",
            "finding": (
                "NAT outside interface is configured but no NAT "
                "inside interface was detected."
            ),
            "recommendation": (
                "Verify that the internal interfaces are configured "
                "with ip nat inside."
            )
        })

    # Validate pool references in dynamic NAT rules.
    referenced_pool_names = set()

    for entry in dynamic_entries:
        pool_name = entry.get("pool_name")

        # Backward compatibility with entries containing only commands.
        if not pool_name:
            command = entry.get("command", "")
            parts = command.split()

            if "pool" in parts:
                pool_index = parts.index("pool")
                if pool_index + 1 < len(parts):
                    pool_name = parts[pool_index + 1]

        if pool_name:
            referenced_pool_names.add(pool_name)

            if pool_name not in configured_pool_names:
                findings.append({
                    "severity": "warning",
                    "category": "nat",
                    "device": "NAT",
                    "finding": (
                        f"Dynamic NAT references pool '{pool_name}', "
                        "but that pool was not found in the configuration."
                    ),
                    "recommendation": (
                        f"Configure NAT pool '{pool_name}' or correct "
                        "the pool name in the dynamic NAT rule."
                    )
                })

    # Check for pools that are configured but not referenced.
    if pools and not referenced_pool_names and not dynamic_entries:
        findings.append({
            "severity": "info",
            "category": "nat",
            "device": "NAT",
            "finding": (
                "A NAT pool is configured but no dynamic NAT rule "
                "was detected."
            ),
            "recommendation": (
                "Verify whether the NAT pool is intended to be used "
                "by a dynamic NAT rule."
            )
        })

    # Check NAT overload configuration.
    if overload_entries and not inside_interfaces:
        findings.append({
            "severity": "warning",
            "category": "nat",
            "device": "NAT",
            "finding": (
                "NAT overload is configured without a detected "
                "NAT inside interface."
            ),
            "recommendation": (
                "Verify the NAT inside interface configuration."
            )
        })

    return findings
