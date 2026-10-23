"""Generate security findings from parsed SNMP configuration."""


def analyze_snmp(snmp: dict) -> list[dict]:
    findings = []
    if not snmp:
        return findings

    for community in snmp.get("communities", []):
        access = str(community.get("access", "RO")).upper()
        if access == "RW":
            findings.append({
                "severity": "high",
                "category": "security",
                "device": "SNMP",
                "finding": "An SNMP community has read-write access.",
                "impact": "A client that knows this community may be able to change managed device settings.",
                "evidence": [community.get("evidence", "snmp-server community <REDACTED> RW")],
                "recommendation": "Prefer SNMPv3 with authentication and privacy; remove read-write community access unless it is explicitly required.",
            })
        elif not community.get("has_acl"):
            findings.append({
                "severity": "warning",
                "category": "security",
                "device": "SNMP",
                "finding": "An SNMP community is configured without an access-class restriction.",
                "impact": "SNMP access may be available to a broader set of source addresses than intended.",
                "evidence": [community.get("evidence", "snmp-server community <REDACTED> RO")],
                "recommendation": "Restrict SNMP sources with an access list and migrate to SNMPv3 authPriv where supported.",
            })

    for host in snmp.get("hosts", []):
        version = str(host.get("version", "1")).lower()
        if version in {"1", "2", "2c"}:
            findings.append({
                "severity": "warning",
                "category": "security",
                "device": host.get("host", "SNMP manager"),
                "finding": f"SNMP notifications are configured with SNMPv{version}.",
                "impact": "SNMPv1/v2c use community strings and do not provide SNMPv3's message authentication and privacy protections.",
                "evidence": [host.get("evidence", f"snmp-server host {host.get('host', '<manager>')} version {version} <REDACTED>")],
                "recommendation": "Use SNMPv3 with authentication and privacy (authPriv) when the manager and device support it.",
            })

    for user in snmp.get("v3_users", []):
        if user.get("auth_enabled") and not user.get("privacy_enabled"):
            findings.append({
                "severity": "warning",
                "category": "security",
                "device": "SNMP",
                "finding": "An SNMPv3 user has authentication configured without privacy.",
                "impact": "Messages may be authenticated but are not encrypted in transit.",
                "evidence": [f"snmp-server user {user.get('username', '<user>')} {user.get('group', '<group>')} v3 auth <REDACTED>"],
                "recommendation": "Configure SNMPv3 authPriv with approved authentication and privacy algorithms.",
            })

    return findings
