
from analyzers.cross_feature_analyzer import analyze_nat_interface_consistency
from analyzers.cross_feature_analyzer import (
    analyze_dhcp_interface_consistency,
    analyze_nat_interface_consistency,
    analyze_dhcp_gateway_interface_consistency,
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


def test_dhcp_gateway_mismatch_with_interface_generates_warning():
    dhcp = {
        "pools": [
            {
                "name": "USERS",
                "network": "192.168.10.0",
                "subnet_mask": "255.255.255.0",
                "default_router": ["192.168.10.254"],
            }
        ]
    }

    interfaces = [
        {
            "name": "GigabitEthernet0/0",
            "ip_address": "192.168.10.1",
            "subnet_mask": "255.255.255.0",
        }
    ]

    findings = analyze_dhcp_gateway_interface_consistency(
        dhcp,
        interfaces,
    )

    assert any(
        "DHCP gateway 192.168.10.254" in finding["finding"]
        for finding in findings
    )


def test_matching_dhcp_gateway_interface_has_no_finding():
    dhcp = {
        "pools": [{
            "name": "USERS",
            "network": "192.168.10.0",
            "subnet_mask": "255.255.255.0",
            "default_router": ["192.168.10.1"],
        }]
    }
    interfaces = [{
        "name": "Vlan10",
        "ip_address": "192.168.10.1",
        "subnet_mask": "255.255.255.0",
    }]

    findings = analyze_dhcp_gateway_interface_consistency(
        dhcp, interfaces
    )

    assert findings == []


def test_invalid_dhcp_gateway_is_ignored():
    dhcp = {
        "pools": [{
            "name": "USERS",
            "network": "192.168.10.0",
            "subnet_mask": "255.255.255.0",
            "default_router": ["999.168.10.1"],
        }]
    }
    interfaces = [{
        "name": "Vlan10",
        "ip_address": "192.168.10.1",
        "subnet_mask": "255.255.255.0",
    }]

    findings = analyze_dhcp_gateway_interface_consistency(
        dhcp, interfaces
    )

    assert findings == []


def test_multiple_dhcp_gateways_are_checked_independently():
    dhcp = {
        "pools": [{
            "name": "USERS",
            "network": "192.168.10.0",
            "subnet_mask": "255.255.255.0",
            "default_router": [
                "192.168.10.1",
                "192.168.10.254",
            ],
        }]
    }
    interfaces = [{
        "name": "Vlan10",
        "ip_address": "192.168.10.1",
        "subnet_mask": "255.255.255.0",
    }]

    findings = analyze_dhcp_gateway_interface_consistency(
        dhcp, interfaces
    )

    assert len(findings) == 1
    assert findings[0]["evidence"]["dhcp_gateway"] == "192.168.10.254"
    assert findings[0]["evidence"]["dhcp_pool"] == "USERS"
    assert findings[0]["evidence"]["dhcp_subnet"] == "192.168.10.0/24"


def test_dhcp_gateway_on_different_subnet_is_not_compared():
    dhcp = {
        "pools": [{
            "name": "USERS",
            "network": "192.168.20.0",
            "subnet_mask": "255.255.255.0",
            "default_router": ["192.168.20.1"],
        }]
    }
    interfaces = [{
        "name": "Vlan10",
        "ip_address": "192.168.10.1",
        "subnet_mask": "255.255.255.0",
    }]

    findings = analyze_dhcp_gateway_interface_consistency(
        dhcp, interfaces
    )

    assert findings == []


def test_external_dhcp_gateway_is_reported_as_warning_not_error():
    dhcp = {
        "pools": [{
            "name": "USERS",
            "network": "192.168.10.0",
            "subnet_mask": "255.255.255.0",
            "default_router": ["192.168.10.254"],
        }]
    }
    interfaces = [{
        "name": "Vlan10",
        "ip_address": "192.168.10.1",
        "subnet_mask": "255.255.255.0",
    }]

    findings = analyze_dhcp_gateway_interface_consistency(
        dhcp, interfaces
    )

    assert len(findings) == 1
    assert findings[0]["severity"] == "warning"
    assert "192.168.10.254" in findings[0]["finding"]
    assert "separate router or Layer 3 device" in (
        findings[0]["recommendation"]
    )


def test_dhcp_interface_consistency_ignores_malformed_entries():
    dhcp = {
        "pools": [
            None,
            "invalid pool",
            {
                "name": "USERS",
                "network": "192.168.20.0",
                "subnet_mask": "255.255.255.0",
            },
        ]
    }
    interfaces = [
        None,
        "invalid interface",
        {
            "name": "Vlan10",
            "ip_address": "192.168.10.1",
            "subnet_mask": "255.255.255.0",
        },
    ]

    findings = analyze_dhcp_interface_consistency(dhcp, interfaces)

    assert len(findings) == 1
    assert findings[0]["evidence"]["dhcp_pool"] == "USERS"


def test_nat_interface_consistency_ignores_malformed_lists():
    nat = {
        "inside_interfaces": "GigabitEthernet0/0",
        "outside_interfaces": None,
        "dynamic": None,
        "overload": "not a list",
    }

    findings = analyze_nat_interface_consistency(
        nat,
        [{"name": "GigabitEthernet0/0"}],
    )

    assert findings == []
