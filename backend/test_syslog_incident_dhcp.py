from analyzers.syslog_analyzer import analyze_syslog_events
from analyzers.syslog_incident_analyzer import analyze_syslog_incident
from parsers.syslog import parse_syslog


DHCP_SAMPLE = """2026-10-23T13:00:11Z CAI-DHCP-01 %DHCPD-4-POOL_WARNING: Pool WIFI-CORPORATE utilization reached 85%
2026-10-23T13:10:22Z CAI-DHCP-01 %DHCPD-4-POOL_WARNING: Pool WIFI-CORPORATE utilization reached 92%
2026-10-23T13:45:31Z CAI-DHCP-01 %DHCPD-3-POOL_EXHAUSTED: Pool WIFI-CORPORATE has no available addresses
2026-10-23T13:45:35Z CAI-DHCP-01 %DHCPD-4-DHCPDISCOVER: DHCPDISCOVER from 00:1b:44:11:3a:b7 via Vlan40: network 10.20.40.0/24: no free leases
2026-10-23T13:46:02Z CAI-DHCP-01 %DHCPD-4-DHCPDISCOVER: DHCPDISCOVER from 00:1b:44:22:4b:c1 via Vlan40: network 10.20.40.0/24: no free leases
2026-10-23T13:52:08Z CAI-AP-03 %DOT11-4-CLIENT_AUTH_FAIL: Client authentication failed due to IP address assignment failure
2026-10-23T13:55:18Z CAI-AP-03 %DOT11-4-CLIENT_AUTH_FAIL: Client authentication failed due to IP address assignment failure
"""


def test_dhcp_pool_exhaustion_produces_correlated_incident_and_timeline():
    events = parse_syslog(DHCP_SAMPLE)
    diagnosis = analyze_syslog_incident(events)

    assert diagnosis["status"] == "correlated_incident"
    assert diagnosis["title"] == "DHCP pool exhaustion with client address-assignment failures"
    assert diagnosis["confidence"] == "High"
    assert "10.20.40.0/24" in diagnosis["primary_hypothesis"]
    assert len(diagnosis["evidence"]) == 7
    assert any(phase["phase"] == "DHCP pool utilization warning" for phase in diagnosis["phases"])
    assert any(phase["phase"] == "DHCP address pool exhausted" for phase in diagnosis["phases"])
    assert any(phase["phase"] == "Wireless client address assignment failures" for phase in diagnosis["phases"])
    assert any("lease table" in item.lower() for item in diagnosis["recommendations"])
    assert any("authentication-server fault" in item.lower() for item in diagnosis["recommendations"])
    assert "not established" in diagnosis["confidence_basis"].lower()
    assert diagnosis["alternative_hypotheses"]
    assert diagnosis["why_alternatives_less_likely"]
    assert diagnosis["verification_steps"]


def test_dhcp_events_receive_specific_findings_and_recommendations():
    findings = analyze_syslog_events(parse_syslog(DHCP_SAMPLE))

    assert len(findings) == 7
    exhausted = next(item for item in findings if "POOL_EXHAUSTED" in item["event_code"])
    discover = next(item for item in findings if "DHCPDISCOVER" in item["event_code"])
    ap_failure = next(item for item in findings if "CLIENT_AUTH_FAIL" in item["event_code"])

    assert exhausted["severity"] == "high"
    assert exhausted["category"] == "dhcp"
    assert "lease" in exhausted["recommendation"].lower()
    assert discover["severity"] == "high"
    assert discover["category"] == "dhcp"
    assert ap_failure["category"] == "wireless"
    assert "does not establish" in ap_failure["recommendation"].lower()
