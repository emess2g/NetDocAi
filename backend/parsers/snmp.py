"""Parse Cisco SNMP configuration without returning community strings or credentials."""
import re


def parse_snmp(config: str) -> dict:
    snmp = {
        "enabled": False,
        "communities": [],
        "hosts": [],
        "v3_groups": [],
        "v3_users": [],
        "traps_enabled": False,
    }

    for raw_line in config.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("!"):
            continue

        if line.startswith("snmp-server community "):
            parts = line.split()
            if len(parts) < 3:
                continue
            snmp["enabled"] = True
            permission_index = next(
                (index for index, part in enumerate(parts[3:], start=3)
                 if part.upper() in {"RO", "RW"}),
                None,
            )
            access = parts[permission_index].upper() if permission_index is not None else "RO"
            acl = parts[permission_index + 1] if permission_index is not None and len(parts) > permission_index + 1 else None
            snmp["communities"].append({
                "access": access,
                "has_acl": bool(acl),
                "evidence": re.sub(
                    r"^(snmp-server\s+community\s+)\S+",
                    r"\1<REDACTED>",
                    line,
                    flags=re.IGNORECASE,
                ),
            })
        elif line.startswith("snmp-server host "):
            parts = line.split()
            if len(parts) < 3:
                continue
            snmp["enabled"] = True
            host = parts[2]
            version = "1"
            if "version" in [part.lower() for part in parts]:
                version_index = [part.lower() for part in parts].index("version")
                if version_index + 1 < len(parts):
                    version = parts[version_index + 1].lower()
            snmp["hosts"].append({
                "host": host,
                "version": version,
                # Synthesize evidence because Cisco host commands may include community strings.
                "evidence": f"snmp-server host {host} version {version} <REDACTED>",
            })
        elif line.startswith("snmp-server group "):
            parts = line.split()
            if len(parts) >= 5 and parts[3].lower() == "v3":
                snmp["enabled"] = True
                snmp["v3_groups"].append({
                    "name": parts[2],
                    "security_level": next(
                        (part.lower() for part in parts[4:] if part.lower() in {"noauth", "auth", "priv"}),
                        "noauth",
                    ),
                })
        elif line.startswith("snmp-server user "):
            parts = line.split()
            if len(parts) >= 5 and parts[4].lower() == "v3":
                snmp["enabled"] = True
                tail = [part.lower() for part in parts[5:]]
                snmp["v3_users"].append({
                    "username": parts[2],
                    "group": parts[3],
                    "auth_enabled": "auth" in tail,
                    "privacy_enabled": "priv" in tail,
                })
        elif line.startswith("snmp-server enable traps"):
            snmp["enabled"] = True
            snmp["traps_enabled"] = True
        elif line.startswith("snmp-server "):
            snmp["enabled"] = True

    return snmp
