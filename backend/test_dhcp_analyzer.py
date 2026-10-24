from analyzers.dhcp_analyzer import analyze_dhcp


def test_missing_gateway():
    findings = analyze_dhcp([
        {
            "name": "USERS",
            "network": "192.168.10.0",
            "subnet_mask": "255.255.255.0",
            "default_router": None,
            "dns_servers": ["8.8.8.8"],
        }
    ])

    assert any(
        "no default gateway" in f["finding"].lower()
        for f in findings
    )


def test_gateway_outside_subnet():
    findings = analyze_dhcp([
        {
            "name": "USERS",
            "network": "192.168.10.0",
            "subnet_mask": "255.255.255.0",
            "default_router": "192.168.20.1",
            "dns_servers": ["8.8.8.8"],
        }
    ])

    assert any(
        "outside" in f["finding"].lower()
        for f in findings
    )


def test_missing_dns():
    findings = analyze_dhcp([
        {
            "name": "USERS",
            "network": "192.168.10.0",
            "subnet_mask": "255.255.255.0",
            "default_router": "192.168.10.1",
            "dns_servers": [],
        }
    ])

    assert any(
        "no dns server" in f["finding"].lower()
        for f in findings
    )


if __name__ == "__main__":
    tests = [
        test_missing_gateway,
        test_gateway_outside_subnet,
        test_missing_dns,
    ]

    for test in tests:
        test()
        print(f"PASS: {test.__name__}")

    print(f"\nPASS: {len(tests)}/{len(tests)} DHCP analyzer tests")


def test_gateway_outside_subnet_recommendation_has_no_duplicate_phrase():
    findings = analyze_dhcp([
        {
            "name": "USERS",
            "network": "192.168.10.0",
            "subnet_mask": "255.255.255.0",
            "default_router": "192.168.20.1",
            "dns_servers": ["8.8.8.8"],
        }
    ])

    finding = next(
        item for item in findings
        if "outside" in item["finding"].lower()
    )

    assert "the DHCP pool's the DHCP pool's" not in finding["recommendation"]
    assert "within the DHCP pool's subnet" in finding["recommendation"]

def test_all_default_routers_are_validated_independently():
    findings = analyze_dhcp([{
        "name": "USERS",
        "network": "192.168.10.0",
        "subnet_mask": "255.255.255.0",
        "default_router": "192.168.10.1",
        "default_routers": ["192.168.10.1", "192.168.20.1"],
        "dns_servers": ["8.8.8.8"],
    }])

    gateway_findings = [f for f in findings if "Default gateway" in f["finding"]]
    assert len(gateway_findings) == 1
    assert "192.168.20.1" in gateway_findings[0]["finding"]


def test_multiple_default_routers_do_not_crash_legacy_list_input():
    findings = analyze_dhcp([{
        "name": "USERS",
        "network": "192.168.10.0",
        "subnet_mask": "255.255.255.0",
        "default_router": ["192.168.10.1", "192.168.20.1"],
        "dns_servers": ["8.8.8.8"],
    }])

    assert any("192.168.20.1" in f["finding"] for f in findings)

