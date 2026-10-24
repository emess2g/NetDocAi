from parsers.acl import parse_acls


def test_numbered_standard_and_extended_acls_are_classified():
    config = """
access-list 10 permit 192.168.10.0 0.0.0.255
access-list 101 deny tcp any host 192.0.2.10 eq 443
access-list 1300 permit host 198.51.100.5
access-list 2001 deny ip any any
"""
    result = parse_acls(config)

    assert [(acl["number"], acl["type"]) for acl in result] == [
        ("10", "standard"),
        ("101", "extended"),
        ("1300", "standard"),
        ("2001", "extended"),
    ]
    assert result[0]["entries"] == [{
        "action": "permit",
        "source": "192.168.10.0 0.0.0.255",
    }]
    assert result[1]["entries"][0]["action"] == "deny"


def test_numbered_acl_entries_with_same_number_are_grouped_in_order():
    config = """
access-list 10 permit 192.168.1.0 0.0.0.255
access-list 10 deny any
"""
    result = parse_acls(config)

    assert len(result) == 1
    assert [entry["action"] for entry in result[0]["entries"]] == [
        "permit",
        "deny",
    ]


def test_named_acl_collects_indented_permit_and_deny_entries():
    config = """
ip access-list extended WEB-FILTER
 permit tcp any host 192.0.2.10 eq 443
 deny ip any any
!
"""
    result = parse_acls(config)

    assert len(result) == 1
    assert result[0]["number"] == "WEB-FILTER"
    assert result[0]["type"] == "extended"
    assert result[0]["entries"] == [
        {"action": "permit", "rule": "tcp any host 192.0.2.10 eq 443"},
        {"action": "deny", "rule": "ip any any"},
    ]


def test_acl_parser_ignores_invalid_numbered_acl_and_unrelated_commands():
    config = """
access-list 9999 permit any
access-list 10 remark temporary note
hostname EDGE-R1
ip access-list extended EMPTY-ACL
!
"""
    result = parse_acls(config)

    assert result == [{
        "number": "EMPTY-ACL",
        "type": "extended",
        "entries": [],
    }]


def test_named_acl_context_does_not_capture_following_top_level_commands():
    config = """
ip access-list extended EDGE-IN
 permit ip any any
!
hostname EDGE-R1
 permit tcp any any
"""
    result = parse_acls(config)

    assert result == [{
        "number": "EDGE-IN",
        "type": "extended",
        "entries": [{"action": "permit", "rule": "ip any any"}],
    }]
