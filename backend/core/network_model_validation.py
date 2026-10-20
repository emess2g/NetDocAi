"""Validation utilities for NetDocAi's normalized network model."""

VALID_NODE_TYPES = {
    "device",
    "interface",
    "vlan",
    "ipv4_address",
    "ipv4_network",
    "dhcp_pool",
}

RELATIONSHIP_TYPES = {
    "has_interface": ("device", "interface"),
    "has_ip_address": ("interface", "ipv4_address"),
    "configured_in_network": ("interface", "ipv4_network"),
    "access_vlan": ("interface", "vlan"),
    "voice_vlan": ("interface", "vlan"),
    "native_vlan": ("interface", "vlan"),
    "carries_vlan": ("interface", "vlan"),
    "svi_for_vlan": ("interface", "vlan"),
    "configured_dhcp_relay_target": ("interface", "ipv4_address"),
    "declares_network": ("dhcp_pool", "ipv4_network"),
    "provides_dns_server": ("dhcp_pool", "ipv4_address"),
    "specifies_default_gateway": ("dhcp_pool", "ipv4_address"),
}


def validate_network_model(model):
    """Return validation errors without modifying the supplied model."""

    errors = []

    if not isinstance(model, dict):
        return ["Model must be a dictionary."]

    schema_version = model.get("schema_version")
    if schema_version != "1.0":
        errors.append("Unsupported or missing schema version: {!r}. Expected {!r}.".format(schema_version, "1.0"))

    nodes = model.get("nodes")
    relationships = model.get("relationships")

    if not isinstance(nodes, list):
        errors.append("'nodes' must be a list.")
        nodes = []

    if not isinstance(relationships, list):
        errors.append("'relationships' must be a list.")
        relationships = []

    node_types = {}
    node_ids = set()

    for index, node in enumerate(nodes):
        if not isinstance(node, dict):
            errors.append(f"Node at index {index} must be a dictionary.")
            continue

        node_id = node.get("id")
        node_type = node.get("type")

        if not isinstance(node_id, str) or not node_id.strip():
            errors.append(f"Node at index {index} has an invalid ID.")
            continue

        if node_id in node_ids:
            errors.append(f"Duplicate node ID: {node_id}")
        else:
            node_ids.add(node_id)
            node_types[node_id] = node_type

        if (
            not isinstance(node_type, str)
            or node_type not in VALID_NODE_TYPES
        ):
            errors.append(
                f"Node '{node_id}' has invalid type: {node_type!r}."
            )

    device_id = model.get("device_id")

    if not isinstance(device_id, str) or not device_id.strip():
        errors.append("'device_id' must be a non-empty string.")
    elif device_id not in node_ids:
        errors.append(
            f"Device ID '{device_id}' does not reference an existing node."
        )
    elif node_types.get(device_id) != "device":
        errors.append(
            f"Device ID '{device_id}' must reference a device node."
        )

    relationship_keys = set()

    for index, relationship in enumerate(relationships):
        if not isinstance(relationship, dict):
            errors.append(
                f"Relationship at index {index} must be a dictionary."
            )
            continue

        source = relationship.get("source")
        relation_type = relationship.get("type")
        target = relationship.get("target")

        if not isinstance(source, str) or not source.strip():
            errors.append(
                f"Relationship at index {index} has an invalid source."
            )
            continue

        if not isinstance(target, str) or not target.strip():
            errors.append(
                f"Relationship at index {index} has an invalid target."
            )
            continue

        if not isinstance(relation_type, str) or not relation_type.strip():
            errors.append(
                f"Relationship at index {index} has an invalid type."
            )
            continue

        key = (source, relation_type, target)

        if key in relationship_keys:
            errors.append(
                f"Duplicate relationship: {source} "
                f"-[{relation_type}]-> {target}"
            )
        else:
            relationship_keys.add(key)

        if source not in node_ids:
            errors.append(
                f"Relationship source '{source}' does not exist."
            )

        if target not in node_ids:
            errors.append(
                f"Relationship target '{target}' does not exist."
            )

        expected_types = RELATIONSHIP_TYPES.get(relation_type)

        if expected_types is None:
            errors.append(
                f"Unknown relationship type: {relation_type!r}."
            )
            continue

        source_type = node_types.get(source)
        target_type = node_types.get(target)

        if source in node_ids and source_type != expected_types[0]:
            errors.append(
                f"Relationship '{relation_type}' requires source type "
                f"'{expected_types[0]}', got '{source_type}'."
            )

        if target in node_ids and target_type != expected_types[1]:
            errors.append(
                f"Relationship '{relation_type}' requires target type "
                f"'{expected_types[1]}', got '{target_type}'."
            )

    return errors
