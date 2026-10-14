def analyze_stp(stp):
    findings = []

    if not stp:
        return findings

    mode = stp.get("mode")
    priority = stp.get("priority")
    bpdu_filter = stp.get("bpdu_filter_interfaces", [])
    bpdu_guard = stp.get("bpdu_guard_interfaces", [])
    portfast = stp.get("portfast_interfaces", [])

    # Only analyze missing STP mode when there is
    # evidence that STP is actually being configured.
    stp_configured = (
        mode
        or priority is not None
        or bpdu_filter
        or bpdu_guard
        or portfast
    )

    if not mode and stp_configured:
        findings.append({
            "severity": "info",
            "category": "stp",
            "device": "STP",
            "finding": "STP mode is not explicitly configured.",
            "recommendation": "Verify the intended spanning-tree mode."
        })

    if priority == "0":
        findings.append({
            "severity": "info",
            "category": "stp",
            "device": "STP",
            "finding": "STP priority is configured as 0.",
            "recommendation": (
                "Verify that this device is intentionally configured "
                "with the lowest priority."
            )
        })

    if bpdu_filter:
        for interface in bpdu_filter:
            findings.append({
                "severity": "warning",
                "category": "stp",
                "device": interface,
                "finding": "BPDU filtering is enabled on this interface.",
                "recommendation": (
                    "Verify that BPDU filtering is intentionally "
                    "configured because it can prevent STP BPDUs "
                    "from being processed."
                )
            })

    if portfast and not bpdu_guard:
        findings.append({
            "severity": "warning",
            "category": "stp",
            "device": "STP",
            "finding": (
                "PortFast is configured but no BPDU Guard "
                "interfaces were detected."
            ),
            "recommendation": (
                "Consider enabling BPDU Guard on PortFast edge ports."
            )
        })

    return findings
