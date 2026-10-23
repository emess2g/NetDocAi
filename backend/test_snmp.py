from analyzers.snmp_analyzer import analyze_snmp
from parsers.snmp import parse_snmp


CONFIG = """hostname EDGE-R1
snmp-server community read-only RO
snmp-server community write-secret RW 12
snmp-server host 10.20.10.50 version 2c notify-secret
snmp-server group NETOPS v3 priv
snmp-server user monitor NETOPS v3 auth sha auth-secret priv aes 128 privacy-secret
snmp-server enable traps
"""


def test_snmp_parser_redacts_community_strings_and_credentials():
    snmp = parse_snmp(CONFIG)

    assert snmp["enabled"] is True
    assert len(snmp["communities"]) == 2
    assert snmp["communities"][0]["access"] == "RO"
    assert snmp["communities"][0]["has_acl"] is False
    assert snmp["communities"][1]["access"] == "RW"
    assert snmp["communities"][1]["has_acl"] is True
    assert snmp["hosts"] == [{
        "host": "10.20.10.50",
        "version": "2c",
        "evidence": "snmp-server host 10.20.10.50 version 2c <REDACTED>",
    }]
    assert snmp["v3_groups"] == [{"name": "NETOPS", "security_level": "priv"}]
    assert snmp["v3_users"] == [{
        "username": "monitor",
        "group": "NETOPS",
        "auth_enabled": True,
        "privacy_enabled": True,
    }]
    assert snmp["traps_enabled"] is True
    serialized = str(snmp)
    for secret in ("read-only", "write-secret", "notify-secret", "auth-secret", "privacy-secret"):
        assert secret not in serialized

    host_with_optional_flags = parse_snmp(
        "snmp-server host 10.20.10.51 traps version 2c another-secret"
    )
    assert "another-secret" not in str(host_with_optional_flags)
    assert host_with_optional_flags["hosts"][0]["evidence"].endswith("<REDACTED>")


def test_snmp_analyzer_reports_weak_community_and_legacy_version_findings():
    findings = analyze_snmp(parse_snmp(CONFIG))

    assert any(item["severity"] == "warning" and "without an access-class" in item["finding"] for item in findings)
    assert any(item["severity"] == "high" and "read-write" in item["finding"] for item in findings)
    assert any(item["category"] == "security" and "SNMPv2c" in item["finding"] for item in findings)
    assert all("write-secret" not in str(item) for item in findings)


def test_snmp_v3_authpriv_user_does_not_create_a_weak_user_finding():
    snmp = parse_snmp("snmp-server group NETOPS v3 priv\nsnmp-server user monitor NETOPS v3 auth sha secret priv aes 128 secret")
    findings = analyze_snmp(snmp)
    assert not any("SNMPv3 user" in item["finding"] for item in findings)


def test_analyze_config_includes_snmp_data_and_findings():
    from main import analyze_config

    report = analyze_config(CONFIG)
    assert report["snmp"]["enabled"] is True
    assert any("read-write" in item["finding"] for item in report["findings"])
