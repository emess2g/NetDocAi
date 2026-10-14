def calculate_summary(
    findings,
    hostname=None,
    interfaces=None,
    vlans=None,
    ospf=None,
    eigrp=None,
    static_routes=None,
    bgp=None,
    security=None,
    dhcp=None,
    nat=None,
    cdp=None,
    acls=None,
):
    interfaces = interfaces or []
    vlans = vlans or []
    security = security or {}
    dhcp = dhcp or []
    nat = nat or {}
    cdp = cdp or {}
    acls = acls or []

    summary = {
        "total_findings": len(findings),
        "critical": 0,
        "high": 0,
        "warning": 0,
        "info": 0,
    }

    for finding in findings:
        severity = finding.get("severity", "").lower()

        if severity in summary:
            summary[severity] += 1

    # -----------------------------------------
    # Routing summary
    # -----------------------------------------

    routing = []

    if ospf:
        routing.append("OSPF")

    if eigrp:
        routing.append("EIGRP")

    if static_routes:
        routing.append("Static routing")

    if bgp:
        routing.append("BGP")

    routing_text = (
        ", ".join(routing)
        if routing
        else "No dynamic routing protocol detected"
    )


    # services summary
    services = []
    if security.get("ssh"):
        services.append("SSH")
    if security.get("telnet"):
        services.append("Telnet")
    if security.get("http"):
        services.append("HTTP")
    if security.get("https"):
        services.append("HTTPS")

    # DHCP parser may return either a list or a dictionary.
    if isinstance(dhcp, dict):
        dhcp_pools = dhcp.get("pools", [])
    elif isinstance(dhcp, list):
        dhcp_pools = dhcp
    else:
        dhcp_pools = []

    if dhcp_pools:
        services.append("DHCP")

    if nat.get("inside_interfaces") or nat.get("outside_interfaces"):
        services.append("NAT")
    if cdp.get("enabled"):
        services.append("CDP")

    services_text = ", ".join(
        services) if services else "No major services detected"


    # -----------------------------------------
    # Interface metrics
    # -----------------------------------------

    device_name = hostname or "This device"

    active_interfaces = sum(
        1
        for interface in interfaces
        if interface.get("status") == "up"
    )

    shutdown_interfaces = sum(
        1
        for interface in interfaces
        if interface.get("status") == "shutdown"
    )

    # -----------------------------------------
    # Routing metrics
    # -----------------------------------------

    routing_protocols = 0

    if ospf:
        routing_protocols += 1

    if eigrp:
        routing_protocols += 1

    if static_routes:
        routing_protocols += 1

    if bgp:
        routing_protocols += 1

    # -----------------------------------------
    # NAT metrics
    # -----------------------------------------

    nat_rules = (
        len(nat.get("static", []))
        + len(nat.get("dynamic", []))
        + len(nat.get("overload", []))
    )

    # -----------------------------------------
    # ACL metrics
    # -----------------------------------------

    acl_count = len(
        set(
            acl.get("number")
            for acl in acls
            if acl.get("number") is not None
        )
    )

    acl_entries = 0

    for acl in acls:
        if acl.get("entries"):
            acl_entries += len(acl["entries"])
        else:
            acl_entries += 1

    # -----------------------------------------
    # Metrics
    # -----------------------------------------

    summary["metrics"] = {
        "interfaces": len(interfaces),
        "active_interfaces": active_interfaces,
        "shutdown_interfaces": shutdown_interfaces,
        "vlans": len(vlans),
        "routing_protocols": routing_protocols,
        "dhcp_pools": len(dhcp.get("pools", [])) if isinstance(dhcp, dict) else len(dhcp) if isinstance(dhcp, list) else 0,
        "nat_rules": nat_rules,
        "acls": acl_count,
        "acl_entries": acl_entries,
        "ssh_enabled": security.get("ssh", False),
        "cdp_enabled": cdp.get("enabled", False),
    }

    # -----------------------------------------
    # Overview
    # -----------------------------------------

    interface_word = (
        "interface"
        if len(interfaces) == 1
        else "interfaces"
    )

    vlan_word = (
        "VLAN"
        if len(vlans) == 1
        else "VLANs"
    )

    summary["overview"] = (
        f"{device_name} has {len(interfaces)} {interface_word} and "
        f"{len(vlans)} {vlan_word} configured. "
        f"Routing: {routing_text}. "
        f"Active services: {services_text}. "
        f"{summary['critical']} critical and "
        f"{summary['high']} high-severity findings were detected."
    )

    return summary
