
def analyze_vlans(vlans, interfaces=None):
    findings = []
    interfaces = interfaces or []

    # Build a set of VLAN IDs that are actually defined.
    defined_vlans = {
        str(vlan.get("id"))
        for vlan in vlans
        if vlan.get("id") is not None
    }

    # Preserve the existing VLAN definition checks.
    for vlan in vlans:
        vlan_id = str(vlan.get("id", "unknown"))
        vlan_name = vlan.get("name")

        if vlan_id == "1":
            findings.append({
                "severity": "warning",
                "category": "vlan",
                "device": f"VLAN {vlan_id}",
                "finding": "Default VLAN 1 is configured.",
                "recommendation": (
                    "Avoid using VLAN 1 for normal user or "
                    "management traffic where possible."
                ),
            })

        if not vlan_name:
            findings.append({
                "severity": "info",
                "category": "vlan",
                "device": f"VLAN {vlan_id}",
                "finding": "VLAN has no descriptive name.",
                "recommendation": (
                    "Assign a meaningful VLAN name for easier "
                    "network documentation."
                ),
            })

    # Check VLAN references on interfaces.
    for interface in interfaces:
        interface_name = interface.get("name", "Unknown interface")

        # Access VLAN
        access_vlan = interface.get("access_vlan")

        if (
            access_vlan is not None
            and str(access_vlan) not in defined_vlans
        ):
            findings.append({
                "severity": "high",
                "category": "vlan",
                "device": interface_name,
                "finding": (
                    f"Access VLAN {access_vlan} is referenced "
                    "but is not defined in the configuration."
                ),
                "recommendation": (
                    f"Create VLAN {access_vlan} if it is required, "
                    "or assign the interface to an existing VLAN."
                ),
            })

        # Voice VLAN
        voice_vlan = interface.get("voice_vlan")

        if (
            voice_vlan is not None
            and str(voice_vlan) not in defined_vlans
        ):
            findings.append({
                "severity": "high",
                "category": "vlan",
                "device": interface_name,
                "finding": (
                    f"Voice VLAN {voice_vlan} is referenced "
                    "but is not defined in the configuration."
                ),
                "recommendation": (
                    f"Create VLAN {voice_vlan} if it is required, "
                    "or correct the voice VLAN assignment."
                ),
            })

        # Trunk allowed VLANs.
        allowed_vlans = interface.get("allowed_vlans")

        if allowed_vlans:
            allowed_ids = set()

            # Handle lists such as 10,20,30 and ranges such as 10-15.
            for item in str(allowed_vlans).split(","):
                item = item.strip()

                if not item:
                    continue

                if "-" in item:
                    parts = item.split("-", 1)

                    try:
                        start = int(parts[0].strip())
                        end = int(parts[1].strip())

                        if 1 <= start <= end <= 4094:
                            allowed_ids.update(
                                str(vlan_id)
                                for vlan_id in range(start, end + 1)
                            )
                    except ValueError:
                        findings.append({
                            "severity": "warning",
                            "category": "vlan",
                            "device": interface_name,
                            "finding": (
                                f"Could not interpret trunk VLAN "
                                f"range '{item}'."
                            ),
                            "recommendation": (
                                "Check the allowed VLAN list and "
                                "use valid VLAN IDs or ranges."
                            ),
                        })
                else:
                    try:
                        vlan_number = int(item)

                        if 1 <= vlan_number <= 4094:
                            allowed_ids.add(str(vlan_number))
                        else:
                            findings.append({
                                "severity": "warning",
                                "category": "vlan",
                                "device": interface_name,
                                "finding": (
                                    f"Trunk allowed VLAN ID "
                                    f"{vlan_number} is outside "
                                    "the valid range 1-4094."
                                ),
                                "recommendation": (
                                    "Correct the trunk allowed VLAN "
                                    "list to use valid VLAN IDs."
                                ),
                            })
                    except ValueError:
                        findings.append({
                            "severity": "warning",
                            "category": "vlan",
                            "device": interface_name,
                            "finding": (
                                f"Could not interpret trunk VLAN "
                                f"entry '{item}'."
                            ),
                            "recommendation": (
                                "Check the trunk allowed VLAN list."
                            ),
                        })

            for vlan_id in sorted(
                allowed_ids - defined_vlans,
                key=int,
            ):
                findings.append({
                    "severity": "warning",
                    "category": "vlan",
                    "device": interface_name,
                    "finding": (
                        f"Trunk allows VLAN {vlan_id}, but that "
                        "VLAN is not defined in the configuration."
                    ),
                    "recommendation": (
                        f"Create VLAN {vlan_id} if it is required, "
                        "or remove it from the trunk allowed VLAN list."
                    ),
                })

    return findings
