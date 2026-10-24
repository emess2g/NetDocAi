from main import analyze_config


def test_configuration_report_summary_matches_findings_and_model():
    config = """
hostname BRANCH-R1
interface GigabitEthernet0/0
 description LAN gateway
 ip address 192.168.10.1 255.255.255.0
 no shutdown
vlan 10
 name USERS
"""

    report = analyze_config(config)

    assert report["hostname"] == "BRANCH-R1"
    assert isinstance(report["interfaces"], list)
    assert isinstance(report["vlans"], list)
    assert isinstance(report["findings"], list)
    assert isinstance(report["health"], dict)
    assert isinstance(report["summary"], dict)
    assert report["summary"]["total_findings"] == len(report["findings"])

    for severity in ("critical", "high", "warning", "info"):
        expected = sum(
            finding.get("severity", "").lower() == severity
            for finding in report["findings"]
        )
        assert report["summary"][severity] == expected

    validation = report["network_model_validation"]
    assert validation["valid"] is (len(validation["errors"]) == 0)
    assert isinstance(report["network_model"]["nodes"], list)
    assert isinstance(report["network_model"]["relationships"], list)


def test_empty_configuration_returns_stable_configuration_report():
    report = analyze_config("")

    assert report["hostname"] is None
    assert report["interfaces"] == []
    assert report["vlans"] == []
    assert isinstance(report["findings"], list)
    assert report["summary"]["total_findings"] == len(report["findings"])
    assert report["network_model_validation"]["valid"] is True


def test_syslog_report_uses_event_risk_not_configuration_health_shape():
    log = (
        "2026-10-24T11:00:02Z router1 %LINK-3-UPDOWN: "
        "Interface GigabitEthernet0/0/0, changed state to down"
    )

    report = analyze_config(log)

    assert report["report_type"] == "syslog"
    assert len(report["syslog_events"]) == 1
    assert isinstance(report["incident_analysis"], dict)
    assert report["health"]["basis"].startswith(
        "Heuristic score from supplied Syslog"
    )
    assert "network_model" not in report
