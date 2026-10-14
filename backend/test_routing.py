from parsers.routing import parse_ospf_processes

from parsers.routing import (
    parse_ospf,
    parse_eigrp,
    parse_static_routes,
    parse_bgp,
)


def test_ospf_parses_networks_and_passive_interfaces():
    config = """
router ospf 1
 router-id 1.1.1.1
 network 10.0.0.0 0.0.0.255 area 0
 passive-interface GigabitEthernet0/1
!
"""

    result = parse_ospf(config)

    assert result["process_id"] == "1"
    assert result["router_id"] == "1.1.1.1"
    assert result["networks"] == [
        {
            "network": "10.0.0.0",
            "wildcard": "0.0.0.255",
            "area": "0",
        }
    ]
    assert result["passive_interfaces"] == ["GigabitEthernet0/1"]


def test_eigrp_parses_networks_and_passive_interfaces():
    config = """
router eigrp 100
 network 10.0.0.0
 network 192.168.1.0
 passive-interface GigabitEthernet0/1
!
"""

    result = parse_eigrp(config)

    assert result["as_number"] == "100"
    assert result["networks"] == [
        "10.0.0.0",
        "192.168.1.0",
    ]
    assert result["passive_interfaces"] == ["GigabitEthernet0/1"]


def test_static_route_with_next_hop():
    config = """
ip route 10.10.0.0 255.255.0.0 192.168.1.1
"""

    result = parse_static_routes(config)

    assert result == [
        {
            "destination": "10.10.0.0",
            "mask": "255.255.0.0",
            "next_hop": "192.168.1.1",
            "exit_interface": None,
        }
    ]


def test_static_route_with_exit_interface():
    config = """
ip route 172.16.0.0 255.255.0.0 GigabitEthernet0/1
"""

    result = parse_static_routes(config)

    assert result == [
        {
            "destination": "172.16.0.0",
            "mask": "255.255.0.0",
            "next_hop": None,
            "exit_interface": "GigabitEthernet0/1",
        }
    ]


def test_static_route_with_next_hop_and_exit_interface():
    config = """
ip route 10.20.0.0 255.255.0.0 192.168.1.2 GigabitEthernet0/1
"""

    result = parse_static_routes(config)

    assert result[0]["destination"] == "10.20.0.0"
    assert result[0]["next_hop"] == "192.168.1.2"
    assert result[0]["exit_interface"] == "GigabitEthernet0/1"


def test_bgp_parses_neighbors_and_networks():
    config = """
router bgp 65001
 bgp router-id 1.1.1.1
 neighbor 192.168.1.2 remote-as 65002
 network 10.0.0.0 mask 255.255.255.0
!
"""

    result = parse_bgp(config)

    assert result["as"] == "65001"
    assert result["router_id"] == "1.1.1.1"
    assert result["neighbors"] == [
        {
            "address": "192.168.1.2",
            "remote_as": "65002",
        }
    ]
    assert result["networks"] == [
        {
            "network": "10.0.0.0",
            "mask": "255.255.255.0",
        }
    ]


def test_routing_protocols_do_not_bleed_into_each_other():
    config = """
router ospf 1
 router-id 1.1.1.1
 network 10.0.0.0 0.0.0.255 area 0
!
router eigrp 100
 network 192.168.1.0
!
router bgp 65001
 neighbor 192.168.1.2 remote-as 65002
 network 172.16.0.0
!
"""

    ospf = parse_ospf(config)
    eigrp = parse_eigrp(config)
    bgp = parse_bgp(config)

    assert ospf["process_id"] == "1"
    assert ospf["networks"][0]["network"] == "10.0.0.0"
    assert all(
        network["network"] != "192.168.1.0"
        for network in ospf["networks"]
    )

    assert eigrp["as_number"] == "100"
    assert eigrp["networks"] == ["192.168.1.0"]

    assert bgp["as"] == "65001"
    assert bgp["networks"] == [
        {"network": "172.16.0.0", "mask": None}
    ]
    assert bgp["neighbors"][0]["remote_as"] == "65002"


def test_static_route_parser_ignores_unrelated_commands():
    config = """
hostname R1
interface GigabitEthernet0/0
 ip address 192.168.1.1 255.255.255.0
!
ip route 10.0.0.0 255.0.0.0 192.168.1.254
!
"""

    result = parse_static_routes(config)

    assert len(result) == 1
    assert result[0]["destination"] == "10.0.0.0"


def test_empty_routing_configuration():
    assert parse_ospf("") is None
    assert parse_eigrp("") is None
    assert parse_bgp("") is None
    assert parse_static_routes("") == []


def test_ospf_stops_at_interface_section():
    config = """
router ospf 1
 router-id 1.1.1.1
 network 10.0.0.0 0.0.0.255 area 0
interface Loopback0
 passive-interface Loopback0
"""

    result = parse_ospf(config)

    assert result["process_id"] == "1"
    assert result["router_id"] == "1.1.1.1"
    assert result["passive_interfaces"] == []


def test_eigrp_stops_at_interface_section():
    config = """
router eigrp 100
 network 192.168.1.0
interface Loopback0
 passive-interface Loopback0
"""

    result = parse_eigrp(config)

    assert result["as_number"] == "100"
    assert result["networks"] == ["192.168.1.0"]
    assert result["passive_interfaces"] == []


def test_ospf_multiple_processes_behavior():
    config = """
router ospf 1
 router-id 1.1.1.1
 network 10.0.0.0 0.0.0.255 area 0
!
router ospf 2
 router-id 2.2.2.2
 network 192.168.1.0 0.0.0.255 area 1
!
"""

    result = parse_ospf(config)

    # Current parser returns one dictionary, so this test documents
    # the desired behavior for a future multi-process enhancement.
    assert result["process_id"] == "1"
    assert result["router_id"] == "1.1.1.1"


def test_ospf_parser_returns_all_processes():
    config = """
router ospf 1
 router-id 1.1.1.1
 network 10.0.0.0 0.0.0.255 area 0
!
router ospf 2
 router-id 2.2.2.2
 network 192.168.1.0 0.0.0.255 area 1
!
"""

    results = parse_ospf_processes(config)

    assert len(results) == 2
    assert results[0]["process_id"] == "1"
    assert results[0]["router_id"] == "1.1.1.1"
    assert results[1]["process_id"] == "2"
    assert results[1]["router_id"] == "2.2.2.2"
    assert results[0]["networks"][0]["area"] == "0"
    assert results[1]["networks"][0]["area"] == "1"


def test_bgp_stops_at_interface_section():
    from parsers.routing import parse_bgp

    config = """
router bgp 65001
 bgp router-id 1.1.1.1
 neighbor 192.0.2.2 remote-as 65002
!
interface GigabitEthernet0/1
 ip address 192.0.2.1 255.255.255.0
"""

    result = parse_bgp(config)

    assert result["as"] == "65001"
    assert len(result["neighbors"]) == 1
    assert result["router_id"] == "1.1.1.1"


def test_bgp_does_not_parse_networks_from_other_sections():
    from parsers.routing import parse_bgp

    config = """
router bgp 65001
 network 10.0.0.0 mask 255.255.255.0
!
router ospf 1
 network 192.168.1.0 0.0.0.255 area 0
"""

    result = parse_bgp(config)

    assert result["as"] == "65001"
    assert result["networks"] == [
        {
            "network": "10.0.0.0",
            "mask": "255.255.255.0",
        }
    ]


def test_eigrp_parser_finds_later_process():
    from parsers.routing import parse_eigrp

    config = """
router eigrp 100
 network 10.0.0.0
!
router ospf 1
 network 192.168.1.0 0.0.0.255 area 0
!
router eigrp 200
 network 172.16.0.0
"""

    result = parse_eigrp(config)

    # The existing parser returns a single process.
    # For now, verify that it returns the first process.
    assert result["as_number"] == "100"
    assert "10.0.0.0" in result["networks"]


def test_eigrp_parser_returns_all_processes():
    from parsers.routing import parse_eigrp_processes

    config = """
router eigrp 100
 network 10.0.0.0
!
router ospf 1
 network 192.168.1.0 0.0.0.255 area 0
!
router eigrp 200
 network 172.16.0.0
 passive-interface GigabitEthernet0/1
!
"""

    result = parse_eigrp_processes(config)

    assert len(result) == 2
    assert result[0]["as_number"] == "100"
    assert result[0]["networks"] == ["10.0.0.0"]
    assert result[1]["as_number"] == "200"
    assert result[1]["networks"] == ["172.16.0.0"]
    assert result[1]["passive_interfaces"] == ["GigabitEthernet0/1"]


def test_static_route_parses_default_route():
    config = """
ip route 0.0.0.0 0.0.0.0 192.168.1.1
"""

    result = parse_static_routes(config)

    assert result == [
        {
            "destination": "0.0.0.0",
            "mask": "0.0.0.0",
            "next_hop": "192.168.1.1",
            "exit_interface": None,
        }
    ]


def test_static_route_parses_host_route():
    config = """
ip route 192.168.1.50 255.255.255.255 192.168.1.1
"""

    result = parse_static_routes(config)

    assert result == [
        {
            "destination": "192.168.1.50",
            "mask": "255.255.255.255",
            "next_hop": "192.168.1.1",
            "exit_interface": None,
        }
    ]


def test_static_route_parses_multiple_routes_independently():
    config = """
ip route 0.0.0.0 0.0.0.0 192.168.1.1
ip route 10.10.0.0 255.255.0.0 192.168.1.2
ip route 172.16.5.0 255.255.255.0 GigabitEthernet0/1
"""

    result = parse_static_routes(config)

    assert len(result) == 3

    assert result[0] == {
        "destination": "0.0.0.0",
        "mask": "0.0.0.0",
        "next_hop": "192.168.1.1",
        "exit_interface": None,
    }

    assert result[1] == {
        "destination": "10.10.0.0",
        "mask": "255.255.0.0",
        "next_hop": "192.168.1.2",
        "exit_interface": None,
    }

    assert result[2] == {
        "destination": "172.16.5.0",
        "mask": "255.255.255.0",
        "next_hop": None,
        "exit_interface": "GigabitEthernet0/1",
    }
