from analyzers.syslog_analyzer import analyze_syslog_events
from parsers.syslog import looks_like_syslog, parse_syslog


SAMPLE = """2026-10-23T08:58:12Z CAI-RTR-01 %LINK-3-UPDOWN: Interface GigabitEthernet0/0/2, changed state to down
2026-10-23T08:58:12Z CAI-RTR-01 %LINEPROTO-5-UPDOWN: Line protocol on Interface GigabitEthernet0/0/2, changed state to down
2026-10-23T09:12:04Z CAI-RTR-01 %SEC-6-IPACCESSLOGP: list BRANCH-INTERNET-POLICY denied tcp 10.20.30.45(52411) -> 10.20.10.25(443), 1 packet
2026-10-23T09:12:07Z CAI-RTR-01 %SEC-6-IPACCESSLOGP: list BRANCH-INTERNET-POLICY denied tcp 10.20.30.51(52488) -> 10.20.10.25(443), 1 packet
2026-10-23T09:18:31Z CAI-RTR-01 %SYS-3-CPUHOG: Task is running for 2412 msec, process = IP Input
2026-10-23T09:22:45Z CAI-RTR-01 %IPFLOW-6-CACHEOVERFLOW: NetFlow cache entries exceeded configured maximum
2026-10-23T09:31:02Z CAI-RTR-01 %QOS-3-INVALID_QOS: Output drops increasing on GigabitEthernet0/0/1
2026-10-23T09:44:19Z CAI-SW-01 %LINK-3-UPDOWN: Interface GigabitEthernet1/0/13, changed state to up
2026-10-23T09:44:22Z CAI-SW-01 %LINEPROTO-5-UPDOWN: Line protocol on Interface GigabitEthernet1/0/13, changed state to up
2026-10-23T09:47:51Z CAI-AP-03 %CAPWAP-3-DROP: Control path to WLC 10.20.10.20 experienced packet loss
2026-10-23T09:52:08Z CAI-AP-03 %DOT11-4-RADIO_OVERLOAD: Radio 0 client count 118 exceeds recommended threshold
2026-10-23T09:58:33Z CAI-SW-01 %PORT_SECURITY-2-PSECURE_VIOLATION: Security violation on GigabitEthernet1/0/13 caused by MAC address 00:1b:44:11:3a:b7
2026-10-23T10:04:11Z CAI-RTR-01 %SEC-6-IPACCESSLOGP: list BRANCH-INTERNET-POLICY denied udp 10.20.40.88(5353) -> 10.20.10.10(53), 1 packet
2026-10-23T10:11:47Z CAI-RTR-01 %SYS-3-CPUHOG: Task is running for 3104 msec, process = IP Input
2026-10-23T10:18:22Z CAI-RTR-01 %QOS-3-INVALID_QOS: Output drops increasing on GigabitEthernet0/0/1
"""


def test_parse_cisco_syslog_events_and_preserve_source_details():
    events = parse_syslog(SAMPLE)
    assert len(events) == 15
    assert events[0]["device"] == "CAI-RTR-01"
    assert events[0]["facility"] == "LINK"
    assert events[0]["severity"] == 3
    assert events[0]["mnemonic"] == "UPDOWN"
    assert events[0]["line_number"] == 1
    assert "GigabitEthernet0/0/2" in events[0]["message"]


def test_syslog_detection_does_not_match_plain_configuration():
    assert looks_like_syslog(SAMPLE)
    assert not looks_like_syslog("hostname CAI-RTR-01\ninterface GigabitEthernet0/0/1")


def test_syslog_analyzer_classifies_sampled_events_and_keeps_evidence():
    findings = analyze_syslog_events(parse_syslog(SAMPLE))
    assert len(findings) == 15
    assert findings[0]["severity"] == "high"
    assert findings[0]["category"] == "availability"
    assert findings[2]["category"] == "security"
    assert findings[4]["severity"] == "high"
    assert findings[5]["category"] == "performance"
    assert findings[6]["category"] == "performance"
    assert findings[9]["category"] == "wireless"
    assert findings[10]["severity"] == "high"
    assert findings[11]["severity"] == "high"
    assert findings[12]["category"] == "security"
    assert findings[13]["severity"] == "high"
    assert findings[14]["category"] == "performance"
    assert findings[0]["timestamp"] == "2026-10-23T08:58:12Z"
    assert findings[0]["device"] == "CAI-RTR-01"
    assert findings[0]["evidence"][0].startswith("2026-10-23T08:58:12Z")


def test_analyze_config_returns_syslog_report_without_running_config_parsers():
    from main import analyze_config

    report = analyze_config(SAMPLE)
    assert report["report_type"] == "syslog"
    assert report["hostname"] == "Syslog Analysis"
    assert len(report["syslog_events"]) == 15
    assert len(report["findings"]) == 15
    assert report["summary"]["devices"] == 3
    assert report["health"]["score"] is not None
    assert 0 <= report["health"]["score"] <= 100
    assert "event risk" in report["health"]["status"].lower()
    assert "not live network health" in report["health"]["basis"]
    assert report["health"]["score_start"] == 100
    assert report["health"]["total_deduction"] == sum(
        item["deduction"] for item in report["health"]["risk_breakdown"]
    )
    assert report["health"]["score"] == max(0, 100 - report["health"]["total_deduction"])
    assert "formula" in report["health"]


def test_syslog_report_summary_counts_match_findings():
    from main import analyze_config

    report = analyze_config(SAMPLE)
    findings = report["findings"]
    summary = report["summary"]

    assert summary["total_findings"] == len(findings) == 15
    assert summary["critical"] == sum(item["severity"] == "critical" for item in findings)
    assert summary["high"] == sum(item["severity"] == "high" for item in findings)
    assert summary["warning"] == sum(item["severity"] == "warning" for item in findings)
    assert summary["info"] == sum(item["severity"] == "info" for item in findings)
    assert all(item.get("finding") for item in findings)
    assert all(item.get("device") and item.get("timestamp") and item.get("event_code") for item in findings)


def test_syslog_report_does_not_claim_configuration_inventory():
    from main import analyze_config

    report = analyze_config(SAMPLE)

    assert report["report_type"] == "syslog"
    assert report["interfaces"] == []
    assert report["vlans"] == []
    assert report["ospf"] is None
    assert report["eigrp"] is None
    assert report["static_routes"] == []



def _event(facility, severity, mnemonic, message):
    return {
        "timestamp": "2026-10-23T10:30:00Z",
        "device": "TEST-RTR-01",
        "facility": facility,
        "severity": severity,
        "mnemonic": mnemonic,
        "message": message,
        "raw": f"2026-10-23T10:30:00Z TEST-RTR-01 %{facility}-{severity}-{mnemonic}: {message}",
        "line_number": 1,
    }


def test_bgp_route_refresh_is_informational_not_automatically_high():
    finding = analyze_syslog_events([
        _event("BGP", 3, "NOTIFICATION", "Route refresh received from neighbor 192.0.2.2")
    ])[0]

    assert finding["severity"] == "info"
    assert finding["category"] == "routing"
    assert "peer remains established" in finding["recommendation"]


def test_route_map_change_has_change_validation_guidance():
    finding = analyze_syslog_events([
        _event("ROUTEMAP", 6, "MODIFY", "Route-map EDGE-POLICY modified")
    ])[0]

    assert finding["severity"] == "info"
    assert finding["category"] == "configuration_change"
    assert "authorized" in finding["recommendation"]


def test_ip_sla_threshold_event_has_targeted_guidance():
    finding = analyze_syslog_events([
        _event("IPSLA", 4, "THRESHOLD", "IP SLA operation 12 threshold exceeded")
    ])[0]

    assert finding["severity"] == "warning"
    assert finding["category"] == "performance"
    assert "latency/loss" in finding["recommendation"]


def test_ipsec_tunnel_down_has_availability_guidance():
    finding = analyze_syslog_events([
        _event("CRYPTO", 3, "TUNNEL_DOWN", "IPsec tunnel to 192.0.2.8 is down")
    ])[0]

    assert finding["severity"] == "high"
    assert finding["category"] == "availability"
    assert "security associations" in finding["recommendation"]


def test_mpls_lsp_degraded_has_routing_guidance():
    finding = analyze_syslog_events([
        _event("MPLS", 3, "LSP_DEGRADED", "MPLS LSP to PE2 degraded")
    ])[0]

    assert finding["severity"] == "high"
    assert finding["category"] == "routing"
    assert "label distribution" in finding["recommendation"]


def test_tcp_timeout_has_connectivity_guidance():
    finding = analyze_syslog_events([
        _event("TCP", 4, "CONNECTION_TIMEOUT", "TCP connection timeout to 192.0.2.20")
    ])[0]

    assert finding["severity"] == "warning"
    assert finding["category"] == "connectivity"
    assert "port availability" in finding["recommendation"]


def test_configuration_change_event_has_audit_guidance():
    finding = analyze_syslog_events([
        _event("SYS", 5, "CONFIG_I", "Configured from console by admin")
    ])[0]

    assert finding["severity"] == "info"
    assert finding["category"] == "configuration_change"
    assert "change record" in finding["recommendation"]


SDWAN_SAMPLE = """2026-10-23T10:04:02Z LAG-BR-RTR-01 %IPSLA-3-ALERT: Probe 100 packet loss threshold exceeded
2026-10-23T10:04:06Z LAG-BR-RTR-01 %SDWAN-6-PATH_SWITCH: Realtime traffic moved from mpls-fra to inet-ams due to SLA violation
2026-10-23T10:04:09Z LAG-BR-RTR-01 %BFD-5-SESSION_STATE: BFD session on GigabitEthernet0/0/0 changed to DOWN
2026-10-23T10:06:00Z LAG-BR-RTR-01 %LINK-3-UPDOWN: Interface GigabitEthernet0/0/0, changed state to down
2026-10-23T10:06:01Z LAG-BR-RTR-01 %LINEPROTO-5-UPDOWN: Line protocol on Interface GigabitEthernet0/0/0, changed state to down
2026-10-23T10:06:02Z LAG-BR-RTR-01 %ROUTING-6-PATH_CHANGE: ERP route 10.10.10.0/24 switched from 10.255.0.1 to 172.31.100.2
2026-10-23T10:06:02Z LAG-BR-RTR-01 %SDWAN-6-PATH_SWITCH: Business-critical traffic moved from mpls-fra to inet-ams due to link down
2026-10-23T10:06:38Z LAG-BR-RTR-01 %SDWAN-6-PATH_STABLE: inet-ams path stable; ERP latency 82 ms, loss 0.3%
2026-10-23T10:18:00Z LAG-BR-RTR-01 %LINK-3-UPDOWN: Interface GigabitEthernet0/0/0, changed state to up
2026-10-23T10:18:01Z LAG-BR-RTR-01 %LINEPROTO-5-UPDOWN: Line protocol on Interface GigabitEthernet0/0/0, changed state to up
2026-10-23T10:18:02Z LAG-BR-RTR-01 %BFD-5-SESSION_STATE: BFD session on GigabitEthernet0/0/0 changed to UP
2026-10-23T10:18:03Z LAG-BR-RTR-01 %SDWAN-6-PATH_MONITOR: mpls-fra remains ineligible; latency 118 ms, loss 1.8%
2026-10-23T10:26:00Z LAG-BR-RTR-01 %SDWAN-6-PATH_MONITOR: mpls-fra meets SLA; latency 41 ms, jitter 5 ms, loss 0.03%
2026-10-23T10:26:20Z LAG-BR-RTR-01 %SDWAN-6-PATH_SWITCH: New business-critical sessions returned to mpls-fra
2026-10-23T10:27:00Z LAG-BR-RTR-01 %SDWAN-6-FAILOVER_COMPLETE: Traffic returned to preferred path mpls-fra
"""


def test_sdwan_bfd_incident_produces_event_risk_score_and_actionable_findings():
    from main import analyze_config

    report = analyze_config(SDWAN_SAMPLE)
    assert len(report["syslog_events"]) == 15
    assert report["health"]["score"] is not None
    assert 0 <= report["health"]["score"] <= 100
    assert report["health"]["status"] in {
        "Low event risk", "Moderate event risk", "Elevated event risk", "High event risk"
    }
    assert "not live network health" in report["health"]["basis"]
    assert report["summary"]["total_findings"] == 15

    findings = report["findings"]
    bfd_down = next(f for f in findings if "SESSION_STATE" in f["event_code"] and "DOWN" in f["impact"])
    bfd_up = next(f for f in findings if "SESSION_STATE" in f["event_code"] and "UP" in f["impact"])
    ineligible = next(f for f in findings if "PATH_MONITOR" in f["event_code"] and "ineligible" in f["impact"])
    failover = next(f for f in findings if "FAILOVER_COMPLETE" in f["event_code"])

    assert bfd_down["severity"] == "high"
    assert bfd_up["severity"] == "info"
    assert ineligible["severity"] == "warning"
    assert failover["severity"] == "info"



def test_sdwan_sample_builds_evidence_backed_incident_diagnosis():
    from main import analyze_config

    report = analyze_config(SDWAN_SAMPLE)
    diagnosis = report["incident_analysis"]

    assert diagnosis["status"] == "correlated_incident"
    assert "SLA degradation" in diagnosis["primary_hypothesis"]
    assert diagnosis["confidence"] in {"Moderate", "High"}
    assert diagnosis["evidence"]
    assert any(phase["phase"] == "Link recovered; preferred path still outside SLA" for phase in diagnosis["phases"])
    assert diagnosis["failover"]["backup_path"] == "inet-ams"
    assert diagnosis["failover"]["successful"] is True
    assert diagnosis["failover"]["backup_sla_compliance"] == "Not explicitly confirmed by the supplied log messages."
    assert diagnosis["failback"]["safe_sequence_observed"] is True
    assert len(diagnosis["logical_events"]) < len(report["syslog_events"])
    assert any(item["title"] == "Interface failure" and item["event_count"] == 2 for item in diagnosis["logical_events"])
    assert any(item["title"] == "Interface recovery" and item["event_count"] == 2 for item in diagnosis["logical_events"])


def test_incident_analyzer_does_not_invent_root_cause_without_correlated_signals():
    from analyzers.syslog_incident_analyzer import analyze_syslog_incident

    events = parse_syslog("2026-10-23T10:30:00Z TEST-RTR-01 %SYS-6-CONFIG_I: Configured from console by admin")
    diagnosis = analyze_syslog_incident(events)

    assert diagnosis["status"] == "insufficient_evidence"
    assert diagnosis["confidence"] == "Low"
    assert "not contain enough related signals" in diagnosis["primary_hypothesis"]
