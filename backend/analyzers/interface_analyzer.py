
def analyze_interfaces(interfaces):
    findings = []

    for interface in interfaces:
        name = interface.get("name")
        description = interface.get("description")
        status = interface.get("status")
        mode = interface.get("mode")
        access_vlan = interface.get("access_vlan")
        allowed_vlans = interface.get("allowed_vlans")
        native_vlan = interface.get("native_vlan")
        ip_address = interface.get("ip_address")

        # Administratively shutdown interface
        if status == "shutdown":
            findings.append({
                "severity": "info",
                "category": "interface",
                "device": name,
                "finding": "Interface is administratively shutdown.",
                "recommendation": "Verify that the interface is intentionally disabled."
            })

        # Missing interface description
        if not description:
            findings.append({
                "severity": "info",
                "category": "interface",
                "device": name,
                "finding": "Interface has no description configured.",
                "recommendation": "Add a description that identifies the interface's purpose or connected device."
            })

        # Access port without VLAN
        if mode == "access" and access_vlan is None:
            findings.append({
                "severity": "warning",
                "category": "interface",
                "device": name,
                "finding": "Access port has no access VLAN configured.",
                "recommendation": "Assign the interface to the appropriate access VLAN."
            })

        # Access port using default VLAN 1
        if mode == "access" and access_vlan == "1":
            findings.append({
                "severity": "warning",
                "category": "interface",
                "device": name,
                "finding": "Access port is assigned to the default VLAN 1.",
                "recommendation": "Consider assigning the port to a dedicated user or device VLAN."
            })

        # Trunk without explicit allowed VLANs
        if mode == "trunk" and not allowed_vlans:
            findings.append({
                "severity": "warning",
                "category": "interface",
                "device": name,
                "finding": "Trunk port has no explicit allowed VLAN list.",
                "recommendation": "Configure an explicit allowed VLAN list containing only the VLANs required on the trunk."
            })

        # Trunk using native VLAN 1
        if mode == "trunk" and native_vlan == "1":
            findings.append({
                "severity": "warning",
                "category": "interface",
                "device": name,
                "finding": "Trunk port uses native VLAN 1.",
                "recommendation": "Consider using a dedicated non-default native VLAN."
            })

        # Layer-3 interface without an IP address
        if (
            mode is None
            and status != "shutdown"
            and not ip_address
            and name
            and (
                name.startswith("GigabitEthernet")
                or name.startswith("FastEthernet")
                or name.startswith("TenGigabitEthernet")
                or name.startswith("Ethernet")
            )
        ):
            findings.append({
                "severity": "info",
                "category": "interface",
                "device": name,
                "finding": "Physical interface has no IP address configured.",
                "recommendation": "Verify whether this interface is intended to operate as a Layer-2 or Layer-3 interface."
            })

    return findings


