
from analyzers.cross_feature_analyzer import analyze_nat_interface_consistency
from analyzers.cross_feature_analyzer import (
    analyze_dhcp_interface_consistency,
    analyze_nat_interface_consistency
)


def test_matching_dhcp_subnet_has_no_finding():
    dhcp = [{
        "name": "USERS",
        "network": "192.168.10.0",
        "subnet_mask": "255.255.255.0",
    }]
    interfaces = [{
        "name": "Vlan10",
        "ip_address": "192.168.10.1",
        "subnet_mask": "255.255.255.0",
        "mode": "layer3",
    }]

    assert analyze_dhcp_interface_consistency(dhcp, interfaces) == []


def test_mismatched_dhcp_subnet_generates_warning():
    dhcp = [{
        "name": "USERS",
        "network": "192.168.20.0",
        "subnet_mask": "255.255.255.0",
    }]
    interfaces = [{
        "name": "Vlan10",
        "ip_address": "192.168.10.1",
        "subnet_mask": "255.255.255.0",
        "mode": "layer3",
    }]

    findings = analyze_dhcp_interface_consistency(dhcp, interfaces)

    assert len(findings) == 1
    assert findings[0]["severity"] == "warning"
    assert findings[0]["category"] == "cross_feature"
    assert "192.168.20.0/24" in findings[0]["finding"]
    assert findings[0]["evidence"]["dhcp_pool"] == "USERS"


def test_missing_dhcp_network_is_skipped():
    dhcp = [{
        "name": "USERS",
        "network": None,
        "subnet_mask": None,
    }]
    interfaces = [{
        "name": "Vlan10",
        "ip_address": "192.168.10.1",
        "subnet_mask": "255.255.255.0",
    }]

    assert analyze_dhcp_interface_consistency(dhcp, interfaces) == []


def test_missing_interface_addressing_is_skipped():
    dhcp = [{
        "name": "USERS",
        "network": "192.168.20.0",
        "subnet_mask": "255.255.255.0",
    }]
    interfaces = [{
        "name": "GigabitEthernet0/1",
        "ip_address": None,
        "subnet_mask": None,
    }]

    assert analyze_dhcp_interface_consistency(dhcp, interfaces) == []


def test_invalid_interface_address_is_ignored():
    dhcp = [{
        "name": "USERS",
        "network": "192.168.20.0",
        "subnet_mask": "255.255.255.0",
    }]
    interfaces = [{
        "name": "GigabitEthernet0/1",
        "ip_address": "999.168.10.1",
        "subnet_mask": "255.255.255.0",
    }]

    assert analyze_dhcp_interface_consistency(dhcp, interfaces) == []


def test_nat_rule_referencing_missing_interface_generates_warning():
    nat = {
        "inside_interfaces": ["GigabitEthernet0/0"],
        "outside_interfaces": ["GigabitEthernet0/1"],
        "static": [],
        "dynamic": [],
        "overload": [
            {
                "command": (
                    "ip nat inside source list 1 "
                    "interface GigabitEthernet0/2 overload"
                )
            }
        ],
        "pools": [],
    }

    interfaces = [
        {"name": "GigabitEthernet0/0"},
        {"name": "GigabitEthernet0/1"},
    ]

    findings = analyze_nat_interface_consistency(nat, interfaces)

    assert len(findings) == 1
    assert findings[0]["severity"] == "warning"
    assert findings[0]["category"] == "cross_feature"
    assert "GigabitEthernet0/2" in findings[0]["finding"]


def test_interface_cannot_have_both_nat_roles():
    nat = {
        "inside_interfaces": ["GigabitEthernet0/0"],
        "outside_interfaces": ["GigabitEthernet0/0"],
        "static": [],
        "dynamic": [],
        "overload": [],
        "pools": [],
    }

    interfaces = [{"name": "GigabitEthernet0/0"}]

    findings = analyze_nat_interface_consistency(nat, interfaces)

    assert len(findings) == 1
    assert findings[0]["severity"] == "warning"
    assert findings[0]["category"] == "cross_feature"
    assert "GigabitEthernet0/0" in findings[0]["finding"]


def test_nat_overload_referencing_inside_interface_generates_warning():
    nat = {
        "inside_interfaces": ["GigabitEthernet0/0"],
        "outside_interfaces": [],
        "dynamic": [],
        "overload": [{
            "command": (
                "ip nat inside source list 1 "
                "interface GigabitEthernet0/0 overload"
            )
        }],
    }

    interfaces = [{
        "name": "GigabitEthernet0/0",
        "ip_address": "192.168.1.1",
        "subnet_mask": "255.255.255.0",
    }]

    findings = analyze_nat_interface_consistency(nat, interfaces)

    assert any(
        "configured as NAT inside rather than NAT outside" in finding["finding"]
        for finding in findings
    )
