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
