import ipaddress
import re


def parse_dhcp(config: str):
    """Parse Cisco IOS DHCP pools and global excluded addresses."""
    pools = {}
    excluded_addresses = []
    current_pool = None

    for raw_line in config.splitlines():
        line = raw_line.strip()

        if not line or line.startswith("!"):
            continue

        lower = line.lower()

        # Global DHCP excluded-address command.
        # This command is normally outside DHCP pool configuration.
        excluded_match = re.match(
            r"^ip\s+dhcp\s+excluded-address\s+(.+)$",
            line,
            re.I,
        )
        if excluded_match:
            addresses = excluded_match.group(1).split()

            # Support a single excluded address or an address range.
            if len(addresses) in (1, 2):
                try:
                    parsed = [
                        str(ipaddress.IPv4Address(address))
                        for address in addresses
                    ]
                    excluded_addresses.append(parsed)
                except ipaddress.AddressValueError:
                    # Preserve invalid entries for later diagnostics.
                    excluded_addresses.append(addresses)

            continue

        # Start or re-enter a DHCP pool.
        match = re.match(
            r"^ip\s+dhcp\s+pool\s+(\S+)",
            line,
            re.I,
        )
        if match:
            current_pool = match.group(1)
            pools.setdefault(
                current_pool,
                {
                    "name": current_pool,
                    "network": None,
                    "subnet_mask": None,
                    "default_router": None,
                    "dns_servers": [],
                    "excluded_addresses": [],
                    "gateway_in_subnet": None,
                },
            )
            continue

        # Leave the current configuration context.
        if lower in {"end", "exit"}:
            current_pool = None
            continue

        if not current_pool:
            continue

        pool = pools[current_pool]

        # Support "network" and "net".
        network_match = re.match(
            r"^(?:network|net)\s+"
            r"(\d{1,3}(?:\.\d{1,3}){3})\s+"
            r"(\d{1,3}(?:\.\d{1,3}){3})$",
            line,
            re.I,
        )
        if network_match:
            pool["network"] = network_match.group(1)
            pool["subnet_mask"] = network_match.group(2)
            continue

        # Default gateway.
        router_match = re.match(
            r"^default-router\s+(.+)$",
            line,
            re.I,
        )
        if router_match:
            pool["default_router"] = (
                router_match.group(1).split()[0]
            )
            continue

        # DNS: accumulate multiple lines without duplicates.
        dns_match = re.match(
            r"^dns-server\s+(.+)$",
            line,
            re.I,
        )
        if dns_match:
            for address in dns_match.group(1).split():
                if address not in pool["dns_servers"]:
                    pool["dns_servers"].append(address)

    # Attach global exclusions to each pool without sharing mutable lists.
    for pool in pools.values():
        pool["excluded_addresses"] = [
            item.copy() for item in excluded_addresses
        ]

        network = pool["network"]
        mask = pool["subnet_mask"]
        router = pool["default_router"]

        if not (network and mask and router):
            continue

        try:
            subnet = ipaddress.IPv4Network(
                f"{network}/{mask}",
                strict=False,
            )
            gateway = ipaddress.IPv4Address(router)

            pool["gateway_in_subnet"] = (
                gateway in subnet
                and gateway != subnet.network_address
                and gateway != subnet.broadcast_address
            )
        except ValueError:
            pool["gateway_in_subnet"] = False

    return list(pools.values())


