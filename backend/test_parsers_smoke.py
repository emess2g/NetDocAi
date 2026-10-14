from parsers.acl import parse_acls
from parsers.cdp import parse_cdp
from parsers.dhcp import parse_dhcp
from parsers.hostname import parse_hostname
from parsers.interfaces import parse_interfaces
from parsers.nat import parse_nat
from parsers.routing import (
    parse_ospf,
    parse_eigrp,
    parse_static_routes,
    parse_bgp,
)
from parsers.security import parse_security
from parsers.stp import parse_stp
from parsers.vlans import parse_vlans


PARSERS = {
    "hostname": parse_hostname,
    "interfaces": parse_interfaces,
    "vlans": parse_vlans,
    "OSPF": parse_ospf,
    "EIGRP": parse_eigrp,
    "static routes": parse_static_routes,
    "BGP": parse_bgp,
    "DHCP": parse_dhcp,
    "ACLs": parse_acls,
    "NAT": parse_nat,
    "security": parse_security,
    "STP": parse_stp,
    "CDP": parse_cdp,
}


def main():
    print("NetDocAI Parser Smoke Test")
    print("=" * 35)

    failures = []

    for name, parser in PARSERS.items():
        try:
            result = parser("")
            print(f"PASS: {name} handles empty configuration "
                  f"(returns {type(result).__name__})")
        except Exception as error:
            failures.append((name, error))
            print(f"FAIL: {name} raised "
                  f"{type(error).__name__}: {error}")

    print("\n" + "=" * 35)
    print(f"Passed: {len(PARSERS) - len(failures)}/{len(PARSERS)}")
    print(f"Failed: {len(failures)}/{len(PARSERS)}")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
