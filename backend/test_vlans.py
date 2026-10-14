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
