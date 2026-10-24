from core.network_model import build_network_model


def test_builds_interface_and_network_relationships():
    model = build_network_model(
        hostname="R1",
        interfaces=[
            {
                "name": "GigabitEthernet0/1",
                "ip_address": "192.168.10.1",
                "subnet_mask": "255.255.255.0",
                "access_vlan": None,
                "helper_addresses": [],
            }
        ],
    )

    nodes = {node["id"]: node for node in model["nodes"]}
    relationships = model["relationships"]

    assert "device:R1" in nodes
    assert "device:R1/interface:GigabitEthernet0/1" in nodes
    assert "network:192.168.10.0/24" in nodes

    assert any(
        item["type"] == "has_interface"
        for item in relationships
    )
    assert any(
        item["type"] == "configured_in_network"
        and item["target"] == "network:192.168.10.0/24"
        for item in relationships
    )


def test_builds_vlan_membership_and_dhcp_gateway_relationships():
    model = build_network_model(
        hostname="SW1",
        interfaces=[
            {
                "name": "GigabitEthernet0/1",
                "access_vlan": 10,
                "helper_addresses": ["192.168.20.5"],
            }
        ],
        vlans=[{"id": "10", "name": "USERS"}],
        dhcp=[
            {
                "name": "USERS_POOL",
                "network": "192.168.10.0",
                "subnet_mask": "255.255.255.0",
                "default_router": "192.168.10.1",
            }
        ],
    )

    nodes = {node["id"]: node for node in model["nodes"]}
    relationships = model["relationships"]

    assert nodes["vlan:10"]["name"] == "USERS"
    assert "dhcp_pool:USERS_POOL" in nodes

    assert any(
        item["type"] == "access_vlan"
        and item["target"] == "vlan:10"
        for item in relationships
    )
    assert any(
        item["type"] == "configured_dhcp_relay_target"
        and item["target"] == "ipv4_address:192.168.20.5"
        for item in relationships
    )
    assert any(
        item["type"] == "specifies_default_gateway"
        and item["target"] == "ipv4_address:192.168.10.1"
        for item in relationships
    )


def test_invalid_ip_data_does_not_crash_model_builder():
    model = build_network_model(
        hostname="R2",
        interfaces=[
            {
                "name": "GigabitEthernet0/1",
                "ip_address": "not-an-ip",
                "subnet_mask": "255.255.255.0",
                "helper_addresses": ["invalid"],
            }
        ],
    )

    assert model["device_id"] == "device:R2"
    assert not any(
        node["type"] == "ipv4_network"
        for node in model["nodes"]
    )
    assert not any(
        node["type"] == "ipv4_address"
        for node in model["nodes"]
    )


def test_missing_hostname_uses_unknown_device():
    model = build_network_model()

    assert model["device_id"] == "device:Unknown device"
    assert model["nodes"][0]["type"] == "device"


def test_dhcp_gateway_and_interface_share_address_node():
    model = build_network_model(
        hostname="R1",
        interfaces=[
            {
                "name": "GigabitEthernet0/0",
                "ip_address": "192.168.10.1",
                "subnet_mask": "255.255.255.0",
                "helper_addresses": [],
            }
        ],
        dhcp=[
            {
                "name": "USERS",
                "network": "192.168.10.0",
                "subnet_mask": "255.255.255.0",
                "default_router": "192.168.10.1",
            }
        ],
    )

    address_id = "ipv4_address:192.168.10.1"

    matching_nodes = [
        node for node in model["nodes"]
        if node["id"] == address_id
    ]

    assert len(matching_nodes) == 1

    relationships = model["relationships"]

    assert any(
        item["type"] == "has_ip_address"
        and item["target"] == address_id
        for item in relationships
    )

    assert any(
        item["type"] == "specifies_default_gateway"
        and item["target"] == address_id
        for item in relationships
    )


def test_svi_connects_to_its_vlan():
    model = build_network_model(
        hostname="R1",
        interfaces=[{"name": "Vlan10"}],
        vlans=[{"id": "10", "name": "USERS"}],
    )

    assert any(
        relationship["source"] == "device:R1/interface:Vlan10"
        and relationship["type"] == "svi_for_vlan"
        and relationship["target"] == "vlan:10"
        for relationship in model["relationships"]
    )


def test_dhcp_pool_connects_to_dns_server():
    model = build_network_model(
        hostname="R1",
        dhcp=[
            {
                "name": "USERS",
                "dns_servers": ["8.8.8.8", "1.1.1.1"],
            }
        ],
    )

    nodes = {node["id"]: node for node in model["nodes"]}
    relationships = model["relationships"]

    assert "ipv4_address:8.8.8.8" in nodes
    assert "ipv4_address:1.1.1.1" in nodes

    assert sum(
        relationship["type"] == "provides_dns_server"
        and relationship["source"] == "dhcp_pool:USERS"
        for relationship in relationships
    ) == 2


def test_interface_without_explicit_state_has_no_admin_state_claim():
    model = build_network_model(
        hostname="R1",
        interfaces=[
            {
                "name": "GigabitEthernet0/1",
                "status": "up",
                "status_source": None,
            }
        ],
    )

    nodes = {node["id"]: node for node in model["nodes"]}
    interface = nodes["device:R1/interface:GigabitEthernet0/1"]

    assert "status" not in interface
    assert "configured_admin_state" not in interface


def test_explicit_interface_admin_state_preserves_configuration_evidence():
    for status in ("up", "shutdown"):
        model = build_network_model(
            hostname="R1",
            interfaces=[
                {
                    "name": "GigabitEthernet0/1",
                    "status": status,
                    "status_source": "explicit_configuration",
                }
            ],
        )

        nodes = {node["id"]: node for node in model["nodes"]}
        interface = nodes["device:R1/interface:GigabitEthernet0/1"]

        assert interface["configured_admin_state"] == status
        assert interface["configured_admin_state_evidence"] == {
            "basis": "parsed_configuration",
            "field": "shutdown/no shutdown",
        }
        assert "status" not in interface

def test_dhcp_pool_models_every_default_gateway():
    model = build_network_model(
        hostname="R1",
        dhcp=[{
            "name": "USERS",
            "network": "192.168.10.0",
            "subnet_mask": "255.255.255.0",
            "default_router": "192.168.10.1",
            "default_routers": ["192.168.10.1", "192.168.10.254"],
        }],
    )

    relationships = [
        item for item in model["relationships"]
        if item["type"] == "specifies_default_gateway"
        and item["source"] == "dhcp_pool:USERS"
    ]
    assert {item["target"] for item in relationships} == {
        "ipv4_address:192.168.10.1",
        "ipv4_address:192.168.10.254",
    }

