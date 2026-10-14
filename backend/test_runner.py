import json
import urllib.error
import urllib.request

API_URL = "http://127.0.0.1:8000/analyze"

config = """
hostname SW1

spanning-tree mode rapid-pvst
spanning-tree vlan 1 priority 4096

interface GigabitEthernet0/1
 description User Access Port
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
 spanning-tree bpduguard enable

interface GigabitEthernet0/23
 spanning-tree guard loop
 spanning-tree bpdufilter enable

interface GigabitEthernet0/24
 description Uplink
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30
 switchport trunk native vlan 99
 spanning-tree guard root

vlan 10
 name USERS

vlan 20
 name SERVERS

router ospf 1
 router-id 1.1.1.1
 network 192.168.1.0 0.0.0.255 area 0
 passive-interface GigabitEthernet0/1
"""


def main():
    print("===================================")
    print("       NetDocAI Test Runner")
    print("===================================")

    request = urllib.request.Request(
        API_URL,
        data=json.dumps({"config": config}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            data = json.load(response)

    except urllib.error.HTTPError as error:
        print(f"FAIL: API returned HTTP {error.code}")
        print(error.read().decode("utf-8", errors="replace"))
        raise SystemExit(1)

    except (urllib.error.URLError, TimeoutError) as error:
        print(f"FAIL: Could not reach the API: {error}")
        print("Check that FastAPI is running at", API_URL)
        raise SystemExit(1)

    checks = [
        ("Hostname is SW1", data.get("hostname") == "SW1"),
        ("Two VLANs were parsed", len(data.get("vlans", [])) == 2),
        (
            "Access interface was parsed",
            any(
                item.get("name") == "GigabitEthernet0/1"
                and item.get("mode") == "access"
                and item.get("access_vlan") == "10"
                for item in data.get("interfaces", [])
            ),
        ),
        (
            "Trunk interface was parsed",
            any(
                item.get("name") == "GigabitEthernet0/24"
                and item.get("mode") == "trunk"
                and item.get("native_vlan") == "99"
                for item in data.get("interfaces", [])
            ),
        ),
        ("Summary is present", isinstance(data.get("summary"), dict)),
        ("Findings is a list", isinstance(data.get("findings"), list)),
    ]

    print()
    for description, passed in checks:
        print(f'{"PASS" if passed else "FAIL"}: {description}')

    failures = sum(not passed for _, passed in checks)
    print(f"\nResult: {len(checks) - failures}/{len(checks)} checks passed")

    if failures:
        print("\nReturned data for debugging:")
        print(json.dumps(data, indent=2))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
