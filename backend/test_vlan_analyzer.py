
from analyzers.vlan_analyzer import analyze_vlans


def test_vlan_1_generates_warning():
    findings = analyze_vlans([{"id": "1", "name": "DEFAULT"}])

    assert any(
        f["severity"] == "warning"
        and "VLAN 1" in f["finding"]
        for f in findings
    )


def test_undefined_access_vlan_generates_high_finding():
    interfaces = [
        {"name": "GigabitEthernet0/1", "access_vlan": 99}
    ]

    findings = analyze_vlans([], interfaces)

    assert any(
        f["severity"] == "high"
        and "Access VLAN 99" in f["finding"]
        for f in findings
    )


def test_undefined_voice_vlan_generates_high_finding():
    interfaces = [
        {"name": "GigabitEthernet0/1", "voice_vlan": 30}
    ]

    findings = analyze_vlans([], interfaces)

    assert any(
        f["severity"] == "high"
        and "Voice VLAN 30" in f["finding"]
        for f in findings
    )


def test_undefined_trunk_vlan_generates_warning():
    interfaces = [
        {"name": "GigabitEthernet0/1", "allowed_vlans": "10,20"}
    ]

    findings = analyze_vlans([], interfaces)

    warnings = [
        f for f in findings
        if "not defined" in f["finding"]
    ]

    assert len(warnings) == 2


def test_duplicate_undefined_trunk_vlan_generates_one_warning():
    interfaces = [
        {"name": "GigabitEthernet0/1", "allowed_vlans": "10,10,10-12"}
    ]

    findings = analyze_vlans([], interfaces)

    warnings = [
        f for f in findings
        if "not defined" in f["finding"]
    ]

    assert len(warnings) == 3


def test_invalid_trunk_vlan_range_generates_warning():
    interfaces = [
        {"name": "GigabitEthernet0/1", "allowed_vlans": "10-5000"}
    ]

    findings = analyze_vlans([], interfaces)

    assert any(
        f["severity"] == "warning"
        and "10-5000" in f["finding"]
        for f in findings
    )


def test_reversed_trunk_vlan_range_generates_warning():
    interfaces = [
        {"name": "GigabitEthernet0/1", "allowed_vlans": "20-10"}
    ]

    findings = analyze_vlans([], interfaces)

    assert any(
        f["severity"] == "warning"
        and "20-10" in f["finding"]
        for f in findings
    )


def test_defined_trunk_vlans_do_not_generate_missing_vlan_findings():
    vlans = [
        {"id": "10", "name": "USERS"},
        {"id": "11", "name": "SERVERS"},
        {"id": "12", "name": "VOICE"},
    ]
    interfaces = [
        {"name": "GigabitEthernet0/1", "allowed_vlans": "10-12"}
    ]

    findings = analyze_vlans(vlans, interfaces)

    assert not any("not defined" in f["finding"] for f in findings)


def test_trunk_allowed_vlans_all_does_not_generate_invalid_vlan_finding():
    interfaces = [
        {"name": "GigabitEthernet0/1", "allowed_vlans": "all"}
    ]

    findings = analyze_vlans([], interfaces)

    assert not any(
        "Could not interpret trunk VLAN entry" in finding["finding"]
        for finding in findings
    )


def test_trunk_allowed_vlans_none_does_not_generate_invalid_vlan_finding():
    interfaces = [
        {"name": "GigabitEthernet0/1", "allowed_vlans": "none"}
    ]

    findings = analyze_vlans([], interfaces)

    assert not any(
        "Could not interpret trunk VLAN entry" in finding["finding"]
        for finding in findings
    )


def test_except_allowed_vlan_list_does_not_report_excluded_ids_as_undefined():
    interfaces = [
        {
            "name": "GigabitEthernet0/1",
            "allowed_vlans": "except 5,7",
        }
    ]

    findings = analyze_vlans(
        vlans=[{"id": "10", "name": "USERS"}],
        interfaces=interfaces,
    )

    assert not any(
        "Could not interpret trunk VLAN" in finding["finding"]
        or "Trunk allows VLAN" in finding["finding"]
        for finding in findings
    )


def test_malformed_vlan_entries_are_ignored():
    vlans = [
        None,
        "invalid VLAN",
        {"id": "10", "name": "USERS"},
    ]

    interfaces = [
        None,
        "invalid interface",
        {"name": "GigabitEthernet0/1", "access_vlan": 20},
    ]

    findings = analyze_vlans(vlans, interfaces)

    assert any(
        "Access VLAN 20" in finding["finding"]
        for finding in findings
    )


def test_malformed_interface_entries_are_ignored():
    vlans = [{"id": "10", "name": "USERS"}]

    interfaces = [
        None,
        "invalid interface",
        {"name": "GigabitEthernet0/1", "access_vlan": 10},
    ]

    findings = analyze_vlans(vlans, interfaces)

    assert not any(
        "Access VLAN 10" in finding["finding"]
        for finding in findings
    )

