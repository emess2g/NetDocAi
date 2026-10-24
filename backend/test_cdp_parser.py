from parsers.cdp import parse_cdp


def test_cdp_global_enable_and_disable_are_detected():
    assert parse_cdp("cdp run")["enabled"] is True
    assert parse_cdp("no cdp run")["enabled"] is False


def test_last_global_cdp_command_determines_enabled_state():
    assert parse_cdp("no cdp run\ncdp run")["enabled"] is True
    assert parse_cdp("cdp run\nno cdp run")["enabled"] is False


def test_interface_level_cdp_disable_does_not_claim_neighbor_inventory():
    config = """
cdp run
interface GigabitEthernet0/1
 no cdp enable
!
"""
    result = parse_cdp(config)

    assert result["enabled"] is True
    assert result["neighbors"] == []


def test_empty_cdp_configuration_returns_stable_defaults():
    assert parse_cdp("") == {"enabled": False, "neighbors": []}
