
from parsers.nat import parse_nat
from analyzers.nat_analyzer import analyze_nat

def test_nat_inside_and_outside_interfaces():
    config = """
interface GigabitEthernet0/0
 ip nat inside
!
interface GigabitEthernet0/1
 ip nat outside
!
"""

    result = parse_nat(config)

    assert result["inside_interfaces"] == ["GigabitEthernet0/0"]
    assert result["outside_interfaces"] == ["GigabitEthernet0/1"]


def test_nat_pool_is_parsed():
    config = """
ip nat pool PUBLIC_POOL 203.0.113.10 203.0.113.20 netmask 255.255.255.0
"""

    result = parse_nat(config)

    assert result["pools"] == [
        {
            "name": "PUBLIC_POOL",
            "start": "203.0.113.10",
            "end": "203.0.113.20",
            "netmask": "255.255.255.0",
        }
    ]


def test_nat_interface_context_does_not_leak():
    config = """
interface GigabitEthernet0/0
 ip nat inside
!
ip nat pool PUBLIC_POOL 203.0.113.10 203.0.113.20 netmask 255.255.255.0
"""

    result = parse_nat(config)

    assert result["inside_interfaces"] == ["GigabitEthernet0/0"]
    assert len(result["pools"]) == 1
    assert result["outside_interfaces"] == []


def test_nat_overload_rule_is_parsed():
    config = """
ip nat inside source list 1 interface GigabitEthernet0/1 overload
"""

    result = parse_nat(config)

    assert len(result["overload"]) == 1
    assert result["overload"][0]["command"] == (
        "ip nat inside source list 1 interface GigabitEthernet0/1 overload"
    )


def test_nat_duplicate_interface_roles_are_not_duplicated():
    config = """
interface GigabitEthernet0/0
 ip nat inside
 ip nat inside
!
"""

    result = parse_nat(config)

    assert result["inside_interfaces"] == ["GigabitEthernet0/0"]


def test_dynamic_nat_extracts_referenced_pool_name():
    config = """
ip nat inside source list 1 pool PUBLIC_POOL
"""

    result = parse_nat(config)

    assert len(result["dynamic"]) == 1
    assert result["dynamic"][0]["pool_name"] == "PUBLIC_POOL"
    assert result["dynamic"][0]["command"] == (
        "ip nat inside source list 1 pool PUBLIC_POOL"
    )


def test_dynamic_nat_extracts_interface_name():
    config = """
ip nat inside source list 1 interface GigabitEthernet0/1 overload
"""

    result = parse_nat(config)

    assert len(result["overload"]) == 1
    assert result["overload"][0]["command"].endswith(
        "interface GigabitEthernet0/1 overload"
    )


def test_nat_rule_referencing_missing_pool_generates_warning():
    nat = {
        "inside_interfaces": ["GigabitEthernet0/0"],
        "outside_interfaces": ["GigabitEthernet0/1"],
        "static": [],
        "dynamic": [{
            "command": "ip nat inside source list 1 pool MISSING_POOL",
            "pool_name": "MISSING_POOL",
        }],
        "overload": [],
        "pools": [{
            "name": "PUBLIC_POOL",
            "start": "203.0.113.10",
            "end": "203.0.113.20",
            "netmask": "255.255.255.0",
        }],
    }

    findings = analyze_nat(nat)

    assert any(
        "MISSING_POOL" in finding["finding"]
        and "not found" in finding["finding"]
        for finding in findings
    )


def test_nat_rule_referencing_existing_pool_has_no_missing_pool_warning():
    nat = {
        "inside_interfaces": ["GigabitEthernet0/0"],
        "outside_interfaces": ["GigabitEthernet0/1"],
        "static": [],
        "dynamic": [{
            "command": "ip nat inside source list 1 pool PUBLIC_POOL",
            "pool_name": "PUBLIC_POOL",
        }],
        "overload": [],
        "pools": [{
            "name": "PUBLIC_POOL",
            "start": "203.0.113.10",
            "end": "203.0.113.20",
            "netmask": "255.255.255.0",
        }],
    }

    findings = analyze_nat(nat)

    assert not any(
        "not found in the configuration" in finding["finding"]
        for finding in findings
    )


def test_interface_based_dynamic_nat_does_not_require_pool():
    nat = {
        "inside_interfaces": ["GigabitEthernet0/0"],
        "outside_interfaces": ["GigabitEthernet0/1"],
        "static": [],
        "dynamic": [{
            "command": "ip nat inside source list 1 interface GigabitEthernet0/1",
            "interface_name": "GigabitEthernet0/1",
        }],
        "overload": [],
        "pools": [],
    }

    findings = analyze_nat(nat)

    assert not any(
        "references pool" in finding["finding"]
        for finding in findings
    )


def test_static_nat_rule_is_parsed():
    config = """
ip nat inside source static 192.168.10.10 203.0.113.10
"""

    result = parse_nat(config)

    assert result["static"] == [{
        "command": "ip nat inside source static 192.168.10.10 203.0.113.10"
    }]
    assert result["dynamic"] == []
    assert result["overload"] == []


def test_unrelated_commands_do_not_create_nat_rules():
    config = """
ip nat outside source list 1 pool PUBLIC_POOL
ip nat translation timeout 300
"""

    result = parse_nat(config)

    assert result["static"] == []
    assert result["dynamic"] == []
    assert result["overload"] == []
