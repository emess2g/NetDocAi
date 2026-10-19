
from core.summary import calculate_summary
from core.health import calculate_health_score


def test_empty_summary_has_zero_findings():
    result = calculate_summary([])

    assert result["total_findings"] == 0
    assert result["critical"] == 0
    assert result["high"] == 0
    assert result["warning"] == 0
    assert result["info"] == 0


def test_summary_counts_findings_by_severity():
    findings = [
        {"severity": "critical"},
        {"severity": "high"},
        {"severity": "high"},
        {"severity": "warning"},
        {"severity": "info"},
    ]

    result = calculate_summary(findings)

    assert result["total_findings"] == 5
    assert result["critical"] == 1
    assert result["high"] == 2
    assert result["warning"] == 1
    assert result["info"] == 1


def test_summary_counts_severity_case_insensitively():
    findings = [
        {"severity": "CRITICAL"},
        {"severity": "High"},
        {"severity": "Warning"},
    ]

    result = calculate_summary(findings)

    assert result["critical"] == 1
    assert result["high"] == 1
    assert result["warning"] == 1


def test_summary_total_includes_unknown_severities():
    findings = [
        {"severity": "unexpected"},
        {"category": "routing"},
    ]

    result = calculate_summary(findings)

    assert result["total_findings"] == 2
    assert result["critical"] == 0
    assert result["high"] == 0
    assert result["warning"] == 0
    assert result["info"] == 0


def test_summary_counts_interface_and_vlan_metrics():
    result = calculate_summary(
        [],
        interfaces=[
            {"name": "GigabitEthernet0/1", "status": "up"},
            {"name": "GigabitEthernet0/2", "status": "shutdown"},
        ],
        vlans=[
            {"id": "10", "name": "USERS"},
            {"id": "20", "name": "SERVERS"},
        ],
    )

    assert result["metrics"]["interfaces"] == 2
    assert result["metrics"]["active_interfaces"] == 1
    assert result["metrics"]["shutdown_interfaces"] == 1
    assert result["metrics"]["vlans"] == 2


def test_health_and_summary_agree_on_recognized_findings():
    findings = [
        {"severity": "critical"},
        {"severity": "high"},
        {"severity": "warning"},
        {"severity": "info"},
    ]

    summary = calculate_summary(findings)
    health = calculate_health_score(findings)

    assert summary["total_findings"] == 4
    assert (
        summary["critical"]
        + summary["high"]
        + summary["warning"]
        + summary["info"]
        == summary["total_findings"]
    )
    assert health["score"] == 50
    assert health["status"] == "Needs attention"
