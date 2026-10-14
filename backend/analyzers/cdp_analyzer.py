def analyze_cdp(cdp):
    findings = []

    if not cdp:
        return findings

    if not cdp.get("enabled"):
        findings.append({
            "severity": "info",
            "category": "cdp",
            "device": "CDP",
            "finding": "CDP is disabled.",
            "recommendation": "Verify whether CDP is intentionally disabled. Enable it where neighbor discovery is required."
        })

    return findings
