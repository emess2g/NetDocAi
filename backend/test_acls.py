from parsers.acl import parse_acls
from analyzers.acl_analyzer import analyze_acls


def test_numbered_extended_acl_2000_range():
    acls = parse_acls(
        "access-list 2000 permit tcp any any eq 80"
    )

    assert len(acls) == 1
    assert acls[0]["type"] == "extended"


def test_named_acl_does_not_capture_interface_commands():
    config = """
ip access-list extended WEB-FILTER
 permit tcp any any eq 80
interface GigabitEthernet0/0
 description Uplink
"""

    acls = parse_acls(config)

    assert len(acls) == 1
    assert len(acls[0]["entries"]) == 1


def test_repeated_named_acl_declaration():
    config = """
ip access-list extended WEB-FILTER
 permit tcp any any eq 80
ip access-list extended WEB-FILTER
 deny ip any any
"""

    acls = parse_acls(config)

    assert len(acls) == 1
    assert len(acls[0]["entries"]) == 2


def test_standard_acl_permit_any_generates_warning():
    acls = parse_acls("access-list 10 permit any")

    findings = analyze_acls(acls)

    assert len(findings) == 1
    assert findings[0]["severity"] == "warning"
    assert findings[0]["category"] == "acl"


def test_extended_acl_permit_ip_any_any_generates_warning():
    acls = parse_acls(
        "ip access-list extended OPEN-ACCESS\n"
        " permit ip any any"
    )

    findings = analyze_acls(acls)

    assert len(findings) == 1
    assert findings[0]["severity"] == "warning"
    assert "permit any-any" in findings[0]["finding"]


def test_deny_any_any_does_not_generate_permit_warning():
    acls = parse_acls(
        "ip access-list extended BLOCK-ALL\n"
        " deny ip any any"
    )

    assert analyze_acls(acls) == []


def test_numbered_standard_acl_1300_range():
    acls = parse_acls("access-list 1300 permit 192.168.1.0 0.0.0.255")

    assert len(acls) == 1
    assert acls[0]["type"] == "standard"


def test_numbered_extended_acl_2699_upper_boundary():
    acls = parse_acls("access-list 2699 permit tcp any any eq 443")

    assert len(acls) == 1
    assert acls[0]["type"] == "extended"


def test_invalid_numbered_acl_number_is_ignored():
    acls = parse_acls("access-list 3000 permit ip any any")

    assert acls == []


def test_invalid_numbered_acl_action_is_ignored():
    acls = parse_acls("access-list 10 maybe any")

    assert acls == []


def test_numbered_acl_action_is_normalized():
    acls = parse_acls("access-list 10 PERMIT any")

    assert len(acls) == 1
    assert acls[0]["entries"][0]["action"] == "permit"
