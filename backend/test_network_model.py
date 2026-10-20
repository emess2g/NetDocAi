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
