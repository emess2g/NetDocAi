
from analyzers.routing_analyzer import analyze_ospf_processes


def test_valid_multiple_ospf_processes_have_no_findings():
    processes = [
        {
            "process_id": "1",
            "router_id": "1.1.1.1",
            "networks": [{"network": "10.0.0.0"}],
            "passive_interfaces": [],
        },
        {
            "process_id": "2",
            "router_id": "2.2.2.2",
            "networks": [{"network": "192.168.1.0"}],
            "passive_interfaces": [],
        },
    ]

    assert analyze_ospf_processes(processes) == []


def test_missing_router_id_is_reported_for_correct_process():
    processes = [
        {
            "process_id": "1",
            "router_id": "1.1.1.1",
            "networks": [{"network": "10.0.0.0"}],
            "passive_interfaces": [],
        },
        {
            "process_id": "2",
            "router_id": None,
            "networks": [{"network": "192.168.1.0"}],
            "passive_interfaces": [],
        },
    ]

    findings = analyze_ospf_processes(processes)

    assert len(findings) == 1
    assert findings[0]["device"] == "OSPF process 2"
    assert "router ID" in findings[0]["finding"]


def test_missing_networks_are_reported_for_correct_process():
    processes = [
        {
            "process_id": "1",
            "router_id": "1.1.1.1",
            "networks": [],
            "passive_interfaces": [],
        },
    ]

    findings = analyze_ospf_processes(processes)

    assert len(findings) == 1
    assert findings[0]["device"] == "OSPF process 1"
    assert "network statements" in findings[0]["finding"]
