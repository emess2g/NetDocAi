from parsers.stp import parse_stp


def test_stp_global_mode_and_vlan_priority_are_parsed():
    config = """
spanning-tree mode rapid-pvst
spanning-tree vlan 10 priority 4096
"""
    result = parse_stp(config)

    assert result["mode"] == "rapid-pvst"
    assert result["priority"] == "4096"


def test_stp_interface_protections_are_associated_with_their_interfaces():
    config = """
interface GigabitEthernet1/0/1
 spanning-tree portfast
 spanning-tree bpduguard enable
 spanning-tree guard root
!
interface GigabitEthernet1/0/2
 spanning-tree bpdufilter enable
 spanning-tree guard loop
!
"""
    result = parse_stp(config)

    assert result["portfast_interfaces"] == ["GigabitEthernet1/0/1"]
    assert result["bpdu_guard_interfaces"] == ["GigabitEthernet1/0/1"]
    assert result["root_guard_interfaces"] == ["GigabitEthernet1/0/1"]
    assert result["bpdu_filter_interfaces"] == ["GigabitEthernet1/0/2"]
    assert result["loop_guard_interfaces"] == ["GigabitEthernet1/0/2"]


def test_empty_stp_configuration_returns_stable_defaults():
    result = parse_stp("")

    assert result == {
        "mode": None,
        "priority": None,
        "portfast_interfaces": [],
        "bpdu_guard_interfaces": [],
        "bpdu_filter_interfaces": [],
        "root_guard_interfaces": [],
        "loop_guard_interfaces": [],
    }
