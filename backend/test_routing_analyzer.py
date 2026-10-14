
from analyzers.routing_analyzer import analyze_routing


def test_missing_ospf_router_id():
    ospf = {
        "router_id": None,
        "networks": [{"network": "10.0.0.0"}],
    }

    findings = analyze_routing(ospf, None, [], None)

    assert any(
        f["device"] == "OSPF"
        and "router ID" in f["finding"]
        for f in findings
    )


def test_missing_ospf_networks():
    ospf = {
        "router_id": "1.1.1.1",
        "networks": [],
    }

    findings = analyze_routing(ospf, None, [], None)

    assert any(
        f["device"] == "OSPF"
        and "network statements" in f["finding"]
        for f in findings
    )


def test_missing_eigrp_networks():
    eigrp = {
        "as_number": "100",
        "networks": [],
    }

    findings = analyze_routing(None, eigrp, [], None)

    assert any(
        f["device"] == "EIGRP"
        and "network statements" in f["finding"]
        for f in findings
    )


def test_static_route_without_next_hop_or_interface():
    routes = [
        {
            "destination": "10.0.0.0",
            "mask": "255.0.0.0",
            "next_hop": None,
            "exit_interface": None,
        }
    ]

    findings = analyze_routing(None, None, routes, None)

    assert any(
        f["device"] == "Static route"
        and "no next-hop or exit interface" in f["finding"]
        for f in findings
    )


def test_static_route_with_next_hop_has_no_warning():
    routes = [
        {
            "destination": "10.0.0.0",
            "mask": "255.0.0.0",
            "next_hop": "192.168.1.1",
            "exit_interface": None,
        }
    ]

    findings = analyze_routing(None, None, routes, None)

    assert not any(f["device"] == "Static route" for f in findings)


def test_static_route_with_exit_interface_has_no_warning():
    routes = [
        {
            "destination": "10.0.0.0",
            "mask": "255.0.0.0",
            "next_hop": None,
            "exit_interface": "GigabitEthernet0/1",
        }
    ]

    findings = analyze_routing(None, None, routes, None)

    assert not any(f["device"] == "Static route" for f in findings)


def test_missing_bgp_router_id():
    bgp = {
        "router_id": None,
        "neighbors": [{"address": "192.168.1.2", "remote_as": "65002"}],
    }

    findings = analyze_routing(None, None, [], bgp)

    assert any(
        f["device"] == "BGP"
        and "router ID" in f["finding"]
        for f in findings
    )


def test_missing_bgp_neighbors():
    bgp = {
        "router_id": "1.1.1.1",
        "neighbors": [],
    }

    findings = analyze_routing(None, None, [], bgp)

    assert any(
        f["device"] == "BGP"
        and "no neighbors" in f["finding"]
        for f in findings
    )


def test_valid_routing_configuration_has_no_findings():
    ospf = {
        "router_id": "1.1.1.1",
        "networks": [{"network": "10.0.0.0"}],
    }
    eigrp = {
        "as_number": "100",
        "networks": ["192.168.1.0"],
    }
    routes = [
        {
            "destination": "172.16.0.0",
            "mask": "255.255.0.0",
            "next_hop": "192.168.1.1",
            "exit_interface": None,
        }
    ]
    bgp = {
        "router_id": "2.2.2.2",
        "neighbors": [{"address": "192.168.1.2", "remote_as": "65002"}],
    }

    findings = analyze_routing(ospf, eigrp, routes, bgp)

    assert findings == []


def test_all_findings_have_required_fields():
    ospf = {"router_id": None, "networks": []}
    eigrp = {"networks": []}
    routes = [
        {
            "destination": "10.0.0.0",
            "mask": "255.0.0.0",
            "next_hop": None,
            "exit_interface": None,
        }
    ]
    bgp = {"router_id": None, "neighbors": []}

    findings = analyze_routing(ospf, eigrp, routes, bgp)

    assert len(findings) == 6

    for finding in findings:
        assert finding["severity"] == "warning"
        assert finding["category"] == "routing"
        assert finding["device"]
        assert finding["finding"]
        assert finding["recommendation"]


def test_static_route_with_invalid_destination_is_flagged():
    routes = [
        {
            "destination": "999.0.0.0",
            "mask": "255.0.0.0",
            "next_hop": "192.168.1.1",
            "exit_interface": None,
        }
    ]

    findings = analyze_routing(None, None, routes, None)

    assert any(
        f["device"] == "Static route"
        and "destination" in f["finding"].lower()
        for f in findings
    )


def test_static_route_with_noncontiguous_mask_is_flagged():
    routes = [
        {
            "destination": "10.0.0.0",
            "mask": "255.0.255.0",
            "next_hop": "192.168.1.1",
            "exit_interface": None,
        }
    ]

    findings = analyze_routing(None, None, routes, None)

    assert any(
        f["device"] == "Static route"
        and "mask" in f["finding"].lower()
        for f in findings
    )


def test_static_route_with_invalid_next_hop_is_flagged():
    routes = [
        {
            "destination": "10.0.0.0",
            "mask": "255.0.0.0",
            "next_hop": "999.1.1.1",
            "exit_interface": None,
        }
    ]

    findings = analyze_routing(None, None, routes, None)

    assert any(
        f["device"] == "Static route"
        and "next-hop" in f["finding"].lower()
        for f in findings
    )


def test_static_route_with_misaligned_destination_is_flagged():
    routes = [
        {
            "destination": "10.1.2.3",
            "mask": "255.255.255.0",
            "next_hop": "192.168.1.1",
            "exit_interface": None,
        }
    ]

    findings = analyze_routing(None, None, routes, None)

    assert any(
        f["device"] == "Static route"
        and "network address" in f["finding"].lower()
        for f in findings
    )

