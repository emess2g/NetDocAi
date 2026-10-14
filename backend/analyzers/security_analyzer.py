def analyze_security(security):
    findings = []

    if not security:
        return findings

    if security.get("telnet"):
        findings.append({
            "severity": "high",
            "category": "security",
            "device": "management",
            "finding": "Telnet access is enabled.",
            "impact": "Telnet sends management traffic without encryption, which can expose credentials and sensitive administrative sessions.",
            "evidence": security.get("vty_transport", []),
            "recommendation": "Disable Telnet and allow SSH only for secure remote management.",
            "remediation": "Configure the affected VTY lines with 'transport input ssh'."
        })

    if security.get("http"):
        findings.append({
            "severity": "warning",
            "category": "security",
            "device": "management",
            "finding": "HTTP server is enabled.",
            "recommendation": "Disable HTTP or use HTTPS for secure device management."
        })

    if not security.get("https") and security.get("http"):
        findings.append({
            "severity": "warning",
            "category": "security",
            "device": "management",
            "finding": "HTTP is enabled without HTTPS.",
            "recommendation": "Enable HTTPS and disable plain HTTP where possible."
        })

    if not security.get("ssh"):
        findings.append({
            "severity": "warning",
            "category": "security",
            "device": "management",
            "finding": "SSH is not detected.",
            "recommendation": "Configure SSH for secure remote management."
        })

    if not security.get("enable_secret"):
        findings.append({
            "severity": "warning",
            "category": "security",
            "device": "management",
            "finding": "No enable secret is configured.",
            "recommendation": "Configure an enable secret to protect privileged EXEC access."
        })

    if security.get("plaintext_passwords"):
        findings.append({
            "severity": "high",
            "category": "security",
            "device": "management",
            "finding": "Plaintext passwords are configured.",
            "recommendation": "Use secure password mechanisms and avoid plaintext passwords."
        })

    if security.get("vty_access_class"):
        findings.append({
            "severity": "info",
            "category": "security",
            "device": "VTY",
            "finding": "An access-class is applied to VTY lines.",
            "recommendation": "Verify that the management access restriction matches the intended policy."
        })

    return findings
