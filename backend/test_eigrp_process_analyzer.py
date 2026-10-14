
from analyzers.routing_analyzer import analyze_eigrp_processes


def test_valid_multiple_eigrp_processes_have_no_findings():
    processes = [
        {
            "as_number": "100",
            "networks": ["10.0.0.0"],
            "passive_interfaces": [],
        },
        {
            "as_number": "200",
            "networks": ["172.16.0.0"],
            "passive_interfaces": [],
        },
    ]

    assert analyze_eigrp_processes(processes) == []


def test_missing_networks_are_reported_for_correct_process():
    processes = [
        {
            "as_number": "100",
            "networks": ["10.0.0.0"],
            "passive_interfaces": [],
        },
        {
            "as_number": "200",
            "networks": [],
            "passive_interfaces": [],
        },
    ]

    findings = analyze_eigrp_processes(processes)

    assert len(findings) == 1
    assert findings[0]["device"] == "EIGRP AS 200"
    assert "no network statements" in findings[0]["finding"]


def test_empty_eigrp_process_list_has_no_findings():
    assert analyze_eigrp_processes([]) == []
