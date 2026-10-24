from parsers.dhcp import parse_dhcp


def test_valid_gateway():
    config = """
ip dhcp pool USERS
 network 192.168.10.0 255.255.255.0
 default-router 192.168.10.1
"""

    pools = parse_dhcp(config)

    assert len(pools) == 1
    assert pools[0]["network"] == "192.168.10.0"
    assert pools[0]["default_router"] == "192.168.10.1"
    assert pools[0]["default_routers"] == ["192.168.10.1"]
    assert pools[0]["gateway_in_subnet"] is True


def test_gateway_outside_subnet():
    config = """
ip dhcp pool USERS
 network 192.168.10.0 255.255.255.0
 default-router 192.168.20.1
"""

    pools = parse_dhcp(config)

    assert len(pools) == 1
    assert pools[0]["gateway_in_subnet"] is False


def test_multiple_dns_servers():
    config = """
ip dhcp pool USERS
 network 192.168.10.0 255.255.255.0
 default-router 192.168.10.1
 dns-server 8.8.8.8 1.1.1.1
"""

    pools = parse_dhcp(config)

    assert pools[0]["dns_servers"] == ["8.8.8.8", "1.1.1.1"]


def test_pools_do_not_bleed_into_each_other():
    config = """
ip dhcp pool USERS
 network 192.168.10.0 255.255.255.0
 default-router 192.168.10.1
 exit
ip dhcp pool VOICE
 network 192.168.20.0 255.255.255.0
 default-router 192.168.20.1
"""

    pools = parse_dhcp(config)

    assert len(pools) == 2
    assert pools[0]["name"] == "USERS"
    assert pools[0]["network"] == "192.168.10.0"
    assert pools[1]["name"] == "VOICE"
    assert pools[1]["network"] == "192.168.20.0"
    assert all(p["gateway_in_subnet"] is True for p in pools)


def test_gateway_cannot_be_network_or_broadcast_address():
    config = """
ip dhcp pool USERS
 network 192.168.10.0 255.255.255.0
 default-router 192.168.10.0
"""

    pools = parse_dhcp(config)

    assert pools[0]["gateway_in_subnet"] is False



def test_repeated_dns_commands():
    config = """
ip dhcp pool USERS
 network 192.168.1.0 255.255.255.0
 default-router 192.168.1.1
 dns-server 8.8.8.8
 dns-server 1.1.1.1 8.8.8.8
"""

    pools = parse_dhcp(config)

    assert len(pools) == 1
    assert pools[0]["dns_servers"] == [
        "8.8.8.8",
        "1.1.1.1",
    ]


def test_global_excluded_addresses():
    config = """
ip dhcp excluded-address 192.168.1.1
ip dhcp excluded-address 192.168.1.10 192.168.1.20

ip dhcp pool USERS
 network 192.168.1.0 255.255.255.0
 default-router 192.168.1.1
 dns-server 8.8.8.8
"""

    pools = parse_dhcp(config)

    assert len(pools) == 1
    assert pools[0]["excluded_addresses"] == [
        ["192.168.1.1"],
        ["192.168.1.10", "192.168.1.20"],
    ]


if __name__ == "__main__":
    tests = [
        test_valid_gateway,
        test_gateway_outside_subnet,
        test_multiple_dns_servers,
        test_pools_do_not_bleed_into_each_other,
        test_gateway_cannot_be_network_or_broadcast_address,
        test_repeated_dns_commands,
        test_global_excluded_addresses,
    ]

    for test in tests:
        test()
        print(f"PASS: {test.__name__}")

    print(f"\nPASS: {len(tests)}/{len(tests)} DHCP tests")

def test_multiple_default_routers_are_preserved_and_validated():
    config = """
ip dhcp pool USERS
 network 192.168.10.0 255.255.255.0
 default-router 192.168.10.1 192.168.20.1
"""

    pools = parse_dhcp(config)

    assert pools[0]["default_router"] == "192.168.10.1"
    assert pools[0]["default_routers"] == [
        "192.168.10.1",
        "192.168.20.1",
    ]
    assert pools[0]["gateway_in_subnet"] is False

