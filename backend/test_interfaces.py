
from parsers.interfaces import (
    parse_interfaces,
    expand_interface_range,
)


def test_interface_range_expansion():
    cases = {
        "Gi0/1-4": [
            "GigabitEthernet0/1",
            "GigabitEthernet0/2",
            "GigabitEthernet0/3",
            "GigabitEthernet0/4",
        ],
        "Gi1/0/1-4": [
            "GigabitEthernet1/0/1",
            "GigabitEthernet1/0/2",
            "GigabitEthernet1/0/3",
            "GigabitEthernet1/0/4",
        ],
        "Gi1/0/1 - Gi1/0/4": [
            "GigabitEthernet1/0/1",
            "GigabitEthernet1/0/2",
            "GigabitEthernet1/0/3",
            "GigabitEthernet1/0/4",
        ],
        "Fa0/3-4": [
            "FastEthernet0/3",
            "FastEthernet0/4",
        ],
        "Gi0/1,Gi0/3": [
            "GigabitEthernet0/1",
            "GigabitEthernet0/3",
        ],
    }

    for expression, expected in cases.items():
        actual = expand_interface_range(expression)
        assert actual == expected, (
            f"{expression}: expected {expected}, got {actual}"
        )


def test_interface_range_commands_apply_to_each_port():
    config = """
interface range GigabitEthernet1/0/1-4
 description Test access ports
 switchport mode access
 switchport access vlan 10
 shutdown
"""

    interfaces = parse_interfaces(config)

    assert len(interfaces) == 4

    for interface in interfaces:
        assert interface["description"] == "Test access ports"
        assert interface["mode"] == "access"
        assert interface["access_vlan"] == "10"
        assert interface["status"] == "shutdown"


def test_subinterface_parsing():
    config = """
interface GigabitEthernet0/0.10
 encapsulation dot1Q 10
 ip address 192.168.70.1 255.255.255.0
"""

    interfaces = parse_interfaces(config)

    assert len(interfaces) == 1
    assert interfaces[0]["name"] == "GigabitEthernet0/0.10"
    assert interfaces[0]["encapsulation_vlan"] == 10
    assert interfaces[0]["ip_address"] == "192.168.70.1"
    assert interfaces[0]["subnet_mask"] == "255.255.255.0"


if __name__ == "__main__":
    test_interface_range_expansion()
    test_interface_range_commands_apply_to_each_port()
    test_subinterface_parsing()
    print("PASS: all interface regression tests")


def test_invalid_ip_address_does_not_overwrite_valid_address():
    config = """
interface GigabitEthernet0/0
 ip address 192.168.1.1 255.255.255.0
 ip address 999.168.1.1 255.255.255.0
"""

    interfaces = parse_interfaces(config)

    assert len(interfaces) == 1
    assert interfaces[0]["ip_address"] == "192.168.1.1"
    assert interfaces[0]["subnet_mask"] == "255.255.255.0"


def test_noncontiguous_subnet_mask_is_rejected():
    config = """
interface GigabitEthernet0/0
 ip address 192.168.1.1 255.0.255.0
"""

    interfaces = parse_interfaces(config)

    assert interfaces[0]["ip_address"] is None
    assert interfaces[0]["subnet_mask"] is None


def test_commands_outside_interface_section_are_ignored():
    config = """
description OUTSIDE_INTERFACE
ip address 192.168.1.1 255.255.255.0
!
interface GigabitEthernet0/1
 description Valid interface
"""

    interfaces = parse_interfaces(config)

    assert len(interfaces) == 1
    assert interfaces[0]["description"] == "Valid interface"
    assert interfaces[0]["ip_address"] is None


def test_repeated_interface_declaration_updates_existing_record():
    config = """
interface GigabitEthernet0/1
 description First description
 shutdown
!
interface Gi0/1
 description Updated description
 no shutdown
"""

    interfaces = parse_interfaces(config)

    assert len(interfaces) == 1
    assert interfaces[0]["name"] == "GigabitEthernet0/1"
    assert interfaces[0]["description"] == "Updated description"
    assert interfaces[0]["status"] == "up"


def test_reversed_interface_range_does_not_expand():
    result = expand_interface_range("Gi0/4-1")

    assert result == ["GigabitEthernet0/4"]


def test_interface_range_at_expansion_limit():
    result = expand_interface_range("Gi0/1-257")

    assert len(result) == 257
    assert result[0] == "GigabitEthernet0/1"
    assert result[-1] == "GigabitEthernet0/257"


def test_interface_range_above_expansion_limit():
    result = expand_interface_range("Gi0/1-258")

    # The parser should not expand a range beyond its configured limit.
    assert result == ["GigabitEthernet0/1"]


def test_duplicate_interfaces_in_range_are_deduplicated():
    result = expand_interface_range("Gi0/1,Gi0/2,Gi0/1")

    assert result == [
        "GigabitEthernet0/1",
        "GigabitEthernet0/2",
    ]


def test_invalid_subnet_mask_does_not_overwrite_valid_addressing():
    config = """
interface GigabitEthernet0/0
 ip address 192.168.1.1 255.255.255.0
 ip address 192.168.1.2 255.0.255.0
"""

    interfaces = parse_interfaces(config)

    assert interfaces[0]["ip_address"] == "192.168.1.1"
    assert interfaces[0]["subnet_mask"] == "255.255.255.0"


def test_invalid_ip_octet_is_rejected():
    config = """
interface GigabitEthernet0/0
 ip address 192.168.1.256 255.255.255.0
"""

    interfaces = parse_interfaces(config)

    assert interfaces[0]["ip_address"] is None
    assert interfaces[0]["subnet_mask"] is None



def test_trunk_allowed_vlans_all_is_preserved():
    config = """
interface GigabitEthernet0/1
 switchport mode trunk
 switchport trunk allowed vlan all
"""

    interfaces = parse_interfaces(config)

    assert interfaces[0]["allowed_vlans"] == "all"


def test_trunk_allowed_vlans_none_is_preserved():
    config = """
interface GigabitEthernet0/1
 switchport mode trunk
 switchport trunk allowed vlan none
"""

    interfaces = parse_interfaces(config)

    assert interfaces[0]["allowed_vlans"] == "none"


def test_trunk_allowed_vlan_incremental_add_computes_effective_list():
    config = """
interface GigabitEthernet0/1
 switchport mode trunk
 switchport trunk allowed vlan 10,20
 switchport trunk allowed vlan add 30
"""

    interfaces = parse_interfaces(config)

    assert interfaces[0]["allowed_vlans"] == "10,20,30"



def test_trunk_allowed_vlan_add_updates_existing_list():
    config = """
interface GigabitEthernet0/1
 switchport mode trunk
 switchport trunk allowed vlan 10,20
 switchport trunk allowed vlan add 30
"""

    interfaces = parse_interfaces(config)

    assert interfaces[0]["allowed_vlans"] == "10,20,30"


def test_trunk_allowed_vlan_remove_updates_existing_list():
    config = """
interface GigabitEthernet0/1
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30
 switchport trunk allowed vlan remove 20
"""

    interfaces = parse_interfaces(config)

    assert interfaces[0]["allowed_vlans"] == "10,30"


def test_trunk_allowed_vlan_except_excludes_vlan_ids():
    config = """
interface GigabitEthernet0/1
 switchport mode trunk
 switchport trunk allowed vlan except 5,7
"""

    interfaces = parse_interfaces(config)

    assert interfaces[0]["allowed_vlans"] == "except 5,7"


def test_abbreviated_trunk_allowed_vlan_add_updates_list():
    config = """
interface Gi0/1
 sw mo tr
 sw tr allow vlan 10,20
 sw tr allow vlan add 30
"""

    interfaces = parse_interfaces(config)

    assert interfaces[0]["allowed_vlans"] == "10,20,30"


def test_invalid_encapsulation_vlan_does_not_crash_parser():
    config = """
interface GigabitEthernet0/0.10
 encapsulation dot1q abc
"""

    interfaces = parse_interfaces(config)

    assert len(interfaces) == 1
    assert interfaces[0]["encapsulation_vlan"] is None


def test_encapsulation_vlan_out_of_range_is_rejected():
    config = """
interface GigabitEthernet0/0.10
 encapsulation dot1q 4095
"""

    interfaces = parse_interfaces(config)

    assert interfaces[0]["encapsulation_vlan"] is None


def test_encapsulation_vlan_with_native_keyword():
    config = """
interface GigabitEthernet0/0.10
 encapsulation dot1q 10 native
"""

    interfaces = parse_interfaces(config)

    assert interfaces[0]["encapsulation_vlan"] == 10


def test_encapsulation_vlan_zero_is_rejected():
    config = """
interface GigabitEthernet0/0.10
 encapsulation dot1q 0
"""

    interfaces = parse_interfaces(config)

    assert interfaces[0]["encapsulation_vlan"] is None
