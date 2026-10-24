from analyzers.syslog_incident_analyzer import analyze_syslog_incident
from parsers.syslog import parse_syslog


WAN_SAMPLE = """2026-10-23T11:00:02Z LAG-BR-RTR-01 %LINK-3-UPDOWN: Interface GigabitEthernet0/0/0, changed state to down
2026-10-23T11:00:03Z LAG-BR-RTR-01 %SDWAN-6-PATH_SWITCH: Traffic moved from mpls-fra to inet-ams
2026-10-23T11:05:18Z LAG-BR-RTR-01 %LINK-3-UPDOWN: Interface GigabitEthernet0/0/0, changed state to up
2026-10-23T11:05:19Z LAG-BR-RTR-01 %LINEPROTO-5-UPDOWN: Line protocol on Interface GigabitEthernet0/0/0, changed state to up
2026-10-23T11:05:20Z LAG-BR-RTR-01 %SDWAN-6-PATH_SWITCH: Traffic returned to mpls-fra
2026-10-23T11:05:35Z LAG-BR-RTR-01 %IPSLA-3-ALERT: Probe 100 packet loss threshold exceeded
2026-10-23T11:05:44Z LAG-BR-RTR-01 %SDWAN-6-PATH_MONITOR: mpls-fra latency 132 ms, jitter 38 ms, loss 3.6%
2026-10-23T11:06:02Z LAG-BR-RTR-01 %SDWAN-6-PATH_SWITCH: Traffic moved from mpls-fra to inet-ams due to SLA violation
"""


def test_wan_diagnosis_uses_only_observed_signals_and_orders_timeline():
    diagnosis = analyze_syslog_incident(parse_syslog(WAN_SAMPLE))

    assert diagnosis["status"] == "correlated_incident"
    assert diagnosis["confidence"] == "High"
    assert "premature failback" in diagnosis["primary_hypothesis"].lower()
    assert "mpls-fra" in diagnosis["primary_hypothesis"].lower()
    assert "second" in diagnosis["primary_hypothesis"].lower()
    assert "BFD" not in diagnosis["primary_hypothesis"]
    assert "BFD" not in " ".join(diagnosis["recommendations"])

    phases = diagnosis["phases"]
    starts = [phase["start"] for phase in phases]
    assert starts == sorted(starts)
    assert [phase["phase"] for phase in phases] == [
        "MPLS interface failure and initial failover",
        "Premature failback before SLA recovery was established",
        "SLA violation and second failover",
    ]
    initial_phase, failback_phase, second_failover_phase = phases
    assert initial_phase["start"] == "2026-10-23T11:00:02Z"
    assert initial_phase["end"] == "2026-10-23T11:05:18Z"
    assert initial_phase["duration"] == "5 min 16 sec"
    assert failback_phase["start"] == "2026-10-23T11:05:18Z"
    assert failback_phase["end"] == "2026-10-23T11:05:35Z"
    assert failback_phase["duration"] == "17 seconds"
    assert second_failover_phase["start"] == "2026-10-23T11:05:35Z"
    assert second_failover_phase["end"] == "2026-10-23T11:06:02Z"
    assert second_failover_phase["duration"] == "27 seconds"
    for phase in phases:
        assert phase["start"] <= phase["end"]


def test_wan_diagnosis_detects_return_followed_by_renewed_failover():
    diagnosis = analyze_syslog_incident(parse_syslog(WAN_SAMPLE))

    failback = diagnosis["failback"]
    assert "returned to mpls-fra" in failback["assessment"].lower()
    assert "premature failback" in failback["assessment"].lower()
    assert failback["repeated_path_change_observed"] is True
    assert failback["safe_sequence_observed"] is False
    assert failback["observed_return"]["timestamp"] == "2026-10-23T11:05:20Z"
    assert len(failback["subsequent_path_changes"]) == 1
    assert failback["classification"] == "premature_failback"
    assert any("hold-down" in recommendation.lower() for recommendation in diagnosis["recommendations"])


def test_wan_impact_label_does_not_duplicate_traffic_word():
    diagnosis = analyze_syslog_incident(parse_syslog(WAN_SAMPLE))

    assert "Traffic traffic" not in " ".join(diagnosis["impact"])
