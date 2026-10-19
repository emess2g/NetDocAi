from analyzers.security_analyzer import analyze_security
from parsers.security import parse_security


def password_findings(config):
    security = parse_security(config)
    findings = analyze_security(security)
    return [
        finding
        for finding in findings
        if "enable password" in finding["finding"].lower()
    ]


def test_legacy_password_without_encryption_is_high_severity():
    findings = password_findings("enable password mypassword")

    assert len(findings) == 1
    assert findings[0]["severity"] == "high"
    assert "without service password-encryption" in findings[0]["finding"]


def test_legacy_password_with_type7_encryption_is_warning():
    findings = password_findings(
        "enable password 7 0822455D0A16\nservice password-encryption"
    )

    assert len(findings) == 1
    assert findings[0]["severity"] == "warning"
    assert "reversible" in findings[0]["impact"]


def test_no_legacy_password_produces_no_password_finding():
    findings = password_findings("")

    assert findings == []


def test_enable_secret_does_not_trigger_legacy_password_finding():
    findings = password_findings("enable secret 9 examplehash")

    assert findings == []


def test_telnet_finding_only_includes_vty_lines_permitting_telnet():
    config = """
line vty 0 4
 transport input ssh
line vty 5 15
 transport input telnet
"""

    findings = analyze_security(parse_security(config))

    telnet_findings = [
        finding
        for finding in findings
        if finding["finding"] == "Telnet access is enabled."
    ]

    assert len(telnet_findings) == 1
    assert telnet_findings[0]["evidence"] == [
        {"line": "5 15", "transport": "telnet"}
    ]
