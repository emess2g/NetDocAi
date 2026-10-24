import ipaddress


def build_network_model(
    hostname=None,
    interfaces=None,
    vlans=None,
    dhcp=None,
    cdp=None,
):
    """Build a normalized, evidence-based model from parsed configuration."""

    interfaces = interfaces or []
    vlans = vlans or []
    dhcp = dhcp or []
    cdp = cdp or {}

    device_name = hostname or "Unknown device"
    device_id = f"device:{device_name}"

    nodes = []
    relationships = []
    node_ids = set()
    relationship_keys = set()

    def add_node(node_id, node_type, **attributes):
        if node_id not in node_ids:
            nodes.append({
                "id": node_id,
                "type": node_type,
                **attributes,
            })
            node_ids.add(node_id)

    def add_relationship(source, relation, target, evidence):
        key = (source, relation, target)
        if key not in relationship_keys:
            relationships.append({
                "source": source,
                "type": relation,
                "target": target,
                "evidence": evidence,
            })
            relationship_keys.add(key)

    def add_configured_relationship(source, relation, target, field):
        add_relationship(
            source,
            relation,
            target,
            {
                "basis": "parsed_configuration",
                "field": field,
            },
        )

    add_node(device_id, "device", name=device_name)

    # Create nodes for explicitly configured VLANs.
    configured_vlan_ids = set()

    for vlan in vlans:
        vlan_id = str(vlan.get("id", "")).strip()

        try:
            vlan_number = int(vlan_id)
        except (TypeError, ValueError):
            continue

        if not 1 <= vlan_number <= 4094:
            continue

        vlan_id = str(vlan_number)
        configured_vlan_ids.add(vlan_id)

        add_node(
            f"vlan:{vlan_id}",
            "vlan",
            vlan_id=vlan_id,
            name=vlan.get("name"),
            explicitly_configured=True,
        )

    # Add interfaces, their VLAN memberships, IP networks, and relay targets.
    for index, interface in enumerate(interfaces):
        interface_name = str(
            interface.get("name") or f"Unknown interface {index}"
        )
        interface_id = f"{device_id}/interface:{interface_name}"

        interface_attributes = {
            "name": interface_name,
            "mode": interface.get("mode"),
            "ip_address": interface.get("ip_address"),
            "subnet_mask": interface.get("subnet_mask"),
        }

        if interface.get("status_source") == "explicit_configuration":
            interface_attributes["configured_admin_state"] = interface.get(
                "status"
            )
            interface_attributes["configured_admin_state_evidence"] = {
                "basis": "parsed_configuration",
                "field": "shutdown/no shutdown",
            }

        add_node(
            interface_id,
            "interface",
            **interface_attributes,
        )

        add_configured_relationship(
            device_id,
            "has_interface",
            interface_id,
            "interfaces",
        )

        # Represent configured interface IPs as reusable address nodes.
        ip_address = interface.get("ip_address")

        if ip_address:
            try:
                normalized_ip = str(ipaddress.IPv4Address(ip_address))
                address_id = f"ipv4_address:{normalized_ip}"

                add_node(
                    address_id,
                    "ipv4_address",
                    address=normalized_ip,
                )

                add_configured_relationship(
                    interface_id,
                    "has_ip_address",
                    address_id,
                    "ip_address",
                )
            except (ValueError, TypeError):
                pass

        # Preserve VLAN references even when a VLAN definition was not parsed.
        vlan_fields = (
            ("access_vlan", "access_vlan"),
            ("voice_vlan", "voice_vlan"),
            ("native_vlan", "native_vlan"),
        )

        # An SVI named Vlan10 represents the Layer 3 interface
        # associated with VLAN 10.
        if interface_name.lower().startswith("vlan"):
            vlan_suffix = interface_name[4:]

            if vlan_suffix.isdigit():
                vlan_number = int(vlan_suffix)

                if 1 <= vlan_number <= 4094:
                    vlan_id = str(vlan_number)
                    vlan_node_id = f"vlan:{vlan_id}"

                    if vlan_id not in configured_vlan_ids:
                        add_node(
                            vlan_node_id,
                            "vlan",
                            vlan_id=vlan_id,
                            name=None,
                            explicitly_configured=False,
                        )

                    add_configured_relationship(
                        interface_id,
                        "svi_for_vlan",
                        vlan_node_id,
                        "interface.name",
                    )

        for field, relation in vlan_fields:
            value = interface.get(field)
            if value is None:
                continue

            try:
                vlan_number = int(value)
            except (TypeError, ValueError):
                continue

            if not 1 <= vlan_number <= 4094:
                continue

            vlan_id = str(vlan_number)
            vlan_node_id = f"vlan:{vlan_id}"

            if vlan_id not in configured_vlan_ids:
                add_node(
                    vlan_node_id,
                    "vlan",
                    vlan_id=vlan_id,
                    name=None,
                    explicitly_configured=False,
                )

            add_configured_relationship(
                interface_id,
                relation,
                vlan_node_id,
                field,
            )

        # Parse allowed VLAN lists such as "10,20-22".
        allowed_vlans = interface.get("allowed_vlans")

        if isinstance(allowed_vlans, str):
            for part in allowed_vlans.split(","):
                part = part.strip()

                if not part or part.lower() == "all":
                    continue

                try:
                    if "-" in part:
                        start, end = map(int, part.split("-", 1))
                        if start < 1 or end > 4094 or start > end:
                            continue
                        vlan_numbers = range(start, end + 1)
                    else:
                        vlan_numbers = [int(part)]
                except (TypeError, ValueError):
                    continue

                for vlan_number in vlan_numbers:
                    vlan_id = str(vlan_number)
                    vlan_node_id = f"vlan:{vlan_id}"

                    if vlan_id not in configured_vlan_ids:
                        add_node(
                            vlan_node_id,
                            "vlan",
                            vlan_id=vlan_id,
                            name=None,
                            explicitly_configured=False,
                        )

                    add_configured_relationship(
                        interface_id,
                        "carries_vlan",
                        vlan_node_id,
                        "allowed_vlans",
                    )

        # Derive the interface's IP network only when both values are valid.
        ip_address = interface.get("ip_address")
        subnet_mask = interface.get("subnet_mask")

        if ip_address and subnet_mask:
            try:
                ip_interface = ipaddress.IPv4Interface(
                    f"{ip_address}/{subnet_mask}"
                )
                network = ip_interface.network
                network_id = f"network:{network.with_prefixlen}"

                add_node(
                    network_id,
                    "ipv4_network",
                    network=str(network.network_address),
                    prefix_length=network.prefixlen,
                    cidr=network.with_prefixlen,
                )

                add_configured_relationship(
                    interface_id,
                    "configured_in_network",
                    network_id,
                    "ip_address,subnet_mask",
                )
            except (ValueError, TypeError):
                pass

        # A helper address is evidence of a configured relay target,
        # not proof of DHCP reachability or successful address assignment.
        helper_addresses = interface.get("helper_addresses") or []

        if isinstance(helper_addresses, str):
            helper_addresses = [helper_addresses]

        for helper_address in helper_addresses:
            try:
                target_ip = str(ipaddress.IPv4Address(helper_address))
            except (ValueError, TypeError):
                continue

            target_id = f"ipv4_address:{target_ip}"

            add_node(
                target_id,
                "ipv4_address",
                address=target_ip,
            )

            add_configured_relationship(
                interface_id,
                "configured_dhcp_relay_target",
                target_id,
                "helper_addresses",
            )

    # Model DHCP pools and their declared subnets and gateways.
    for index, pool in enumerate(dhcp):
        pool_name = str(pool.get("name") or f"pool-{index}")
        pool_id = f"dhcp_pool:{pool_name}"

        add_node(
            pool_id,
            "dhcp_pool",
            name=pool_name,
        )

        network_address = pool.get("network")
        subnet_mask = pool.get("subnet_mask")

        if network_address and subnet_mask:
            try:
                network = ipaddress.IPv4Network(
                    f"{network_address}/{subnet_mask}",
                    strict=False,
                )
                network_id = f"network:{network.with_prefixlen}"

                add_node(
                    network_id,
                    "ipv4_network",
                    network=str(network.network_address),
                    prefix_length=network.prefixlen,
                    cidr=network.with_prefixlen,
                )

                add_configured_relationship(
                    pool_id,
                    "declares_network",
                    network_id,
                    "network,subnet_mask",
                )
            except (ValueError, TypeError):
                pass

        gateways = pool.get("default_routers")
        if not isinstance(gateways, list) or not gateways:
            gateway = pool.get("default_router")
            gateways = gateway if isinstance(gateway, list) else [gateway] if gateway else []

        # Preserve DNS servers advertised by this DHCP pool.
        dns_servers = pool.get("dns_servers") or []

        if isinstance(dns_servers, str):
            dns_servers = [dns_servers]

        for dns_server in dns_servers:
            try:
                dns_ip = str(ipaddress.IPv4Address(dns_server))
            except (ValueError, TypeError):
                continue

            dns_id = f"ipv4_address:{dns_ip}"

            add_node(
                dns_id,
                "ipv4_address",
                address=dns_ip,
            )

            add_configured_relationship(
                pool_id,
                "provides_dns_server",
                dns_id,
                "dns_servers",
            )

        for gateway in dict.fromkeys(gateways):
            try:
                gateway_ip = str(ipaddress.IPv4Address(gateway))
                gateway_id = f"ipv4_address:{gateway_ip}"

                add_node(
                    gateway_id,
                    "ipv4_address",
                    address=gateway_ip,
                )

                add_configured_relationship(
                    pool_id,
                    "specifies_default_gateway",
                    gateway_id,
                    "default_routers" if len(gateways) > 1 else "default_router",
                )
            except (ValueError, TypeError):
                pass

    # This configuration parser does not establish live CDP neighbor links.
    # Do not invent device-to-device relationships from missing neighbor data.

    return {
        "schema_version": "1.0",
        "device_id": device_id,
        "nodes": nodes,
        "relationships": relationships,
    }
