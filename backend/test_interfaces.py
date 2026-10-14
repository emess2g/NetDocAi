
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
