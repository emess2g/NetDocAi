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
    assert report["health"]["score"] is None
    assert report["health"]["status"] == "Event review required"
