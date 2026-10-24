def analyze_security(security):
    findings = []

    if not security:
        return findings

    vty_lines = security.get("vty_lines", [])
    vty_transport = security.get("vty_transport", [])
    transport_configured_lines = {
        entry.get("line")
        for entry in vty_transport
        if isinstance(entry, dict) and entry.get("line") is not None
    }
    transport_unspecified_lines = [
        line for line in vty_lines
        if line not in transport_configured_lines
    ]

    if transport_unspecified_lines:
        findings.append({
            "severity": "warning",
            "category": "security",
            "device": "VTY",
            "finding": (
                "VTY transport input is not explicitly configured for all "
                "declared line ranges."
            ),
            "impact": (
                "The supplied configuration does not establish which remote "
                "protocols those VTY ranges accept. Effective defaults vary by "
                "IOS release and platform, so Telnet exposure cannot be ruled "
                "out from this input alone."
            ),
            "evidence": [
                {"line": line, "transport": "not specified"}
                for line in transport_unspecified_lines
            ],
            "recommendation": (
                "Explicitly configure 'transport input ssh' on VTY ranges that "
                "require secure remote management, or disable incoming transport "
                "where remote access is not needed. Verify the effective setting "
                "on the target platform."
            ),
        })

    if security.get("telnet"):
        findings.append({
            "severity": "high",
            "category": "security",
            "device": "management",
            "finding": "Telnet access is enabled.",
            "impact": (
                "Telnet does not encrypt the management session, so credentials "
                "and commands may be exposed to anyone able to observe the traffic."
            ),
            "evidence": [
                entry
                for entry in security.get("vty_transport", [])
                if "telnet" in entry.get("transport", "").split()
            ],
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
        if security.get("service_password_encryption"):
            findings.append({
                "severity": "warning",
                "category": "security",
                "device": "management",
                "finding": (
                    "Legacy enable password is configured with "
                    "service password-encryption enabled."
                ),
                "impact": (
                    "The service password-encryption setting uses weak, reversible "
                    "encryption for eligible passwords; it does not provide strong "
                    "password protection."
                ),
                "recommendation": (
                    "Prefer an enable secret and remove the legacy "
                    "enable password where supported."
                )
            })
        else:
            findings.append({
                "severity": "high",
                "category": "security",
                "device": "management",
                "finding": (
                    "Legacy enable password is configured without "
                    "service password-encryption."
                ),
                "impact": (
                    "Without service password-encryption, the legacy enable password "
                    "may remain visible in the saved configuration. Anyone who can "
                    "read or obtain that configuration may be able to recover it."
                ),
                "recommendation": (
                    "Configure an enable secret and remove the legacy "
                    "enable password where supported."
                )
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
