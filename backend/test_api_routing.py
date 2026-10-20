from main import app
from fastapi.testclient import TestClient


client = TestClient(app)


def test_analyze_returns_routing_data_and_findings():
    config = """
hostname R1

router ospf 1
 router-id 1.1.1.1
 network 10.0.0.0 0.0.0.255 area 0
!

router eigrp 100
 network 192.168.1.0
!

ip route 172.16.0.0 255.255.0.0 192.168.1.1

router bgp 65001
 neighbor 192.168.1.2 remote-as 65002
 network 10.10.0.0
!
"""

    response = client.post("/analyze", json={"config": config})

    assert response.status_code == 200

    data = response.json()

    assert data["ospf"]["process_id"] == "1"
    assert data["eigrp"]["as_number"] == "100"
    assert len(data["static_routes"]) == 1
    assert data["static_routes"][0]["destination"] == "172.16.0.0"
    assert data["bgp"]["as"] == "65001"

    assert data["bgp"]["neighbors"][0] == {
        "address": "192.168.1.2",
        "remote_as": "65002",
    }

    routing_findings = [
        finding
        for finding in data["findings"]
        if finding.get("category") == "routing"
    ]

    assert any(
        finding["device"] == "BGP"
        and "router ID" in finding["finding"]
        for finding in routing_findings
    )


def test_analyze_empty_config_returns_routing_sections():
    response = client.post("/analyze", json={"config": ""})

    assert response.status_code == 422
    assert "detail" in response.json()



def test_analyze_returns_multiple_ospf_processes():
    config = """
hostname R1
router ospf 1
 router-id 1.1.1.1
 network 10.0.0.0 0.0.0.255 area 0
router ospf 2
"""

    response = client.post("/analyze", json={"config": config})

    assert response.status_code == 200

    data = response.json()

    assert len(data["ospf_processes"]) == 2
    assert data["ospf_processes"][0]["process_id"] == "1"
    assert data["ospf_processes"][1]["process_id"] == "2"

    ospf_findings = [
        finding
        for finding in data["findings"]
        if "OSPF process 2" in str(finding)
    ]

    assert ospf_findings, "Expected a finding for OSPF process 2"


def test_analyze_returns_multiple_eigrp_processes():
    config = """
hostname R1
router eigrp 100
 network 10.0.0.0
!
router eigrp 200
!
"""

    response = client.post("/analyze", json={"config": config})

    assert response.status_code == 200

    data = response.json()

    assert len(data["eigrp_processes"]) == 2
    assert data["eigrp_processes"][0]["as_number"] == "100"
    assert data["eigrp_processes"][1]["as_number"] == "200"

    eigrp_findings = [
        finding
        for finding in data["findings"]
        if finding.get("device") == "EIGRP AS 200"
    ]

    assert eigrp_findings, "Expected a finding for EIGRP AS 200"


def test_analyze_static_route_validation_end_to_end():
    config = """
hostname R1

router ospf 1
 router-id 1.1.1.1
 network 10.0.0.0 0.0.0.255 area 0
!

ip route 10.1.2.3 255.255.255.0 192.168.1.1
ip route 172.16.0.0 255.0.255.0 192.168.1.2
ip route 192.168.1.0 255.255.255.0 999.1.1.1

router bgp 65001
 neighbor 192.168.1.2 remote-as 65002
!
"""

    response = client.post("/analyze", json={"config": config})

    assert response.status_code == 200

    data = response.json()
    routes = data["static_routes"]

    assert len(routes) == 3
    assert routes[0]["destination"] == "10.1.2.3"
    assert routes[1]["mask"] == "255.0.255.0"
    assert routes[2]["next_hop"] == "999.1.1.1"

    routing_findings = [
        finding
        for finding in data["findings"]
        if finding.get("category") == "routing"
    ]

    static_findings = [
        finding
        for finding in routing_findings
        if finding.get("device") == "Static route"
    ]

    messages = [
        finding["finding"].lower()
        for finding in static_findings
    ]

    assert any("network address" in message for message in messages), (
        f"Missing destination alignment finding: {messages}"
    )

    assert any("mask" in message for message in messages), (
        f"Missing subnet mask finding: {messages}"
    )

    assert any("next-hop" in message for message in messages), (
        f"Missing next-hop finding: {messages}"
    )

    assert any(
        finding.get("device") == "BGP"
        for finding in routing_findings
    )

    assert all(
        finding.get("device") == "Static route"
        for finding in static_findings
    )



def test_routing_findings_remain_separated_by_protocol():
    config = """
hostname R1

router ospf 1
!

router eigrp 100
!

ip route 10.1.2.3 255.255.255.0 999.1.1.1

router bgp 65001
!
"""

    response = client.post("/analyze", json={"config": config})

    assert response.status_code == 200

    data = response.json()

    routing_findings = [
        finding
        for finding in data["findings"]
        if finding.get("category") == "routing"
    ]

    # Each finding must have a device label.
    assert all(
        finding.get("device")
        for finding in routing_findings
    ), f"Found an unlabeled routing finding: {routing_findings}"

    # Each protocol should retain its own findings.
    assert any(
        finding.get("device") == "OSPF"
        or str(finding.get("device", "")).startswith("OSPF process")
        for finding in routing_findings
    ), f"Missing OSPF finding: {routing_findings}"

    assert any(
        finding.get("device") == "EIGRP"
        or str(finding.get("device", "")).startswith("EIGRP AS")
        for finding in routing_findings
    ), f"Missing EIGRP finding: {routing_findings}"

    assert any(
        finding.get("device") == "BGP"
        for finding in routing_findings
    ), f"Missing BGP finding: {routing_findings}"

    assert any(
        finding.get("device") == "Static route"
        and "next-hop" in finding.get("finding", "").lower()
        for finding in routing_findings
    ), f"Missing static-route next-hop finding: {routing_findings}"

    # A static-route finding must not be mislabeled as another protocol.
    static_findings = [
        finding
        for finding in routing_findings
        if "static route" in finding.get("device", "").lower()
    ]

    assert static_findings
    assert all(
        finding.get("device") == "Static route"
        for finding in static_findings
    )



def test_analyze_returns_network_model():
    config = """
hostname R1
!
interface GigabitEthernet0/0
 description LAN gateway
 ip address 192.168.10.1 255.255.255.0
 no shutdown
!
"""

    response = client.post("/analyze", json={"config": config})

    assert response.status_code == 200

    data = response.json()

    assert "network_model" in data
    network_model = data["network_model"]

    assert isinstance(network_model, dict)
    assert "nodes" in network_model
    assert "relationships" in network_model

    assert any(
        node.get("id") == "device:R1"
        for node in network_model["nodes"]
    )

    interface_id = "device:R1/interface:GigabitEthernet0/0"

    interface_node = next(
        (
            node
            for node in network_model["nodes"]
            if node.get("id") == interface_id
            and node.get("type") == "interface"
        ),
        None,
    )

    assert interface_node is not None
    assert interface_node["ip_address"] == "192.168.10.1"
    assert interface_node["configured_admin_state"] == "up"
    assert interface_node["configured_admin_state_evidence"]["basis"] == (
        "parsed_configuration"
    )
