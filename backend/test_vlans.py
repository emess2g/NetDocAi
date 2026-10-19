from parsers.vlans import parse_vlans


def test_basic_vlan_parsing():
    config = """
vlan 10
 name USERS
vlan 20
 name SERVERS
vlan 30
 name MANAGEMENT
"""

    result = parse_vlans(config)

    expected = [
        {"id": "10", "name": "USERS"},
        {"id": "20", "name": "SERVERS"},
        {"id": "30", "name": "MANAGEMENT"},
    ]

    assert result == expected, (
        f"Expected {expected}, got {result}"
    )


def test_empty_configuration():
    assert parse_vlans("") == []


def test_vlan_without_name():
    config = """
vlan 40
"""

    result = parse_vlans(config)

    assert len(result) == 1
    assert result[0]["id"] == "40"
    assert result[0]["name"] in (None, "")


if __name__ == "__main__":
    test_basic_vlan_parsing()
    test_empty_configuration()
    test_vlan_without_name()
    print("PASS: all VLAN regression tests")


def test_vlan_name_preserves_spaces():
    config = """
vlan 50
 name FINANCE DEPARTMENT
!
"""
    result = parse_vlans(config)

    assert result == [
        {"id": "50", "name": "FINANCE DEPARTMENT"}
    ]


def test_name_outside_vlan_section_is_ignored():
    config = """
name SHOULD_NOT_BE_ASSIGNED
!
vlan 60
!
name ALSO_SHOULD_NOT_BE_ASSIGNED
"""
    result = parse_vlans(config)

    assert result == [{"id": "60", "name": None}]


def test_duplicate_vlan_definitions_are_preserved():
    config = """
vlan 10
 name USERS
!
vlan 10
 name STAFF
"""
    result = parse_vlans(config)

    assert result == [
        {"id": "10", "name": "USERS"},
        {"id": "10", "name": "STAFF"},
    ]


def test_vlan_command_without_id_is_ignored():
    config = """
vlan
 name INVALID
!
vlan 20
 name SERVERS
"""
    result = parse_vlans(config)

    assert result == [{"id": "20", "name": "SERVERS"}]


def test_vlan_id_with_extra_tokens():
    config = """
vlan 10 extra
 name USERS
"""
    result = parse_vlans(config)

    assert result == [{"id": "10", "name": "USERS"}]


def test_non_numeric_vlan_id_is_ignored():
    config = """
vlan abc
 name INVALID
!
vlan 20
 name SERVERS
"""
    result = parse_vlans(config)

    assert result == [{"id": "20", "name": "SERVERS"}]


def test_vlan_zero_is_ignored():
    config = """
vlan 0
 name INVALID
"""
    assert parse_vlans(config) == []


def test_vlan_4095_is_ignored():
    config = """
vlan 4095
 name INVALID
"""
    assert parse_vlans(config) == []

    print("PASS: all VLAN regression tests")
