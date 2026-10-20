from copy import deepcopy

from core.network_model import build_network_model
from core.network_model_validation import validate_network_model


def valid_model():
    return build_network_model(
        hostname="R1",
        interfaces=[
            {
                "name": "GigabitEthernet0/0",
                "ip_address": "192.168.10.1",
                "subnet_mask": "255.255.255.0",
                "status": "up",
                "status_source": "explicit_configuration",
            }
        ],
        vlans=[{"id": "10", "name": "USERS"}],
        dhcp=[
            {
                "name": "USERS",
                "network": "192.168.10.0",
                "subnet_mask": "255.255.255.0",
                "default_router": "192.168.10.1",
                "dns_servers": ["8.8.8.8"],
            }
        ],
    )


def test_valid_network_model_has_no_validation_errors():
    assert validate_network_model(valid_model()) == []


def test_detects_duplicate_node_ids():
    model = valid_model()
    model["nodes"].append(deepcopy(model["nodes"][0]))

    errors = validate_network_model(model)

    assert any("Duplicate node ID" in error for error in errors)


def test_detects_relationship_with_missing_target():
    model = valid_model()
    model["relationships"].append({
        "source": model["device_id"],
        "type": "has_interface",
        "target": "device:R1/interface:Missing",
        "evidence": {"basis": "test"},
    })

    errors = validate_network_model(model)

    assert any(
        "Relationship target" in error and "does not exist" in error
        for error in errors
    )


def test_detects_incompatible_relationship_node_types():
    model = valid_model()
    model["relationships"].append({
        "source": model["device_id"],
        "type": "has_interface",
        "target": "ipv4_address:192.168.10.1",
        "evidence": {"basis": "test"},
    })

    errors = validate_network_model(model)

    assert any(
        "requires target type 'interface'" in error
        for error in errors
    )


def test_detects_unknown_relationship_type():
    model = valid_model()
    model["relationships"].append({
        "source": model["device_id"],
        "type": "invented_relationship",
        "target": model["device_id"],
        "evidence": {"basis": "test"},
    })

    errors = validate_network_model(model)

    assert any("Unknown relationship type" in error for error in errors)


def test_detects_duplicate_relationships():
    model = valid_model()
    model["relationships"].append(
        deepcopy(model["relationships"][0])
    )

    errors = validate_network_model(model)

    assert any("Duplicate relationship" in error for error in errors)


def test_rejects_non_dictionary_model():
    assert validate_network_model(None) == [
        "Model must be a dictionary."
    ]


def test_detects_invalid_device_reference():
    model = valid_model()
    model["device_id"] = "device:MISSING"

    errors = validate_network_model(model)

    assert any(
        "does not reference an existing node" in error
        for error in errors
    )


def test_rejects_unhashable_node_type_without_crashing():
    model = valid_model()
    model["nodes"][0]["type"] = ["device"]

    errors = validate_network_model(model)

    assert any("has invalid type" in error for error in errors)


def test_rejects_unsupported_schema_version():
    model = valid_model()
    model["schema_version"] = "2.0"

    errors = validate_network_model(model)

    assert any("Unsupported or missing schema version" in error for error in errors)


def test_rejects_relationship_with_missing_evidence():
    model = valid_model()
    del model["relationships"][0]["evidence"]

    errors = validate_network_model(model)

    assert any("evidence" in error.lower() for error in errors)


def test_rejects_relationship_with_non_dictionary_evidence():
    model = valid_model()
    model["relationships"][0]["evidence"] = "parsed_configuration"

    errors = validate_network_model(model)

    assert any("evidence" in error.lower() for error in errors)


def test_rejects_relationship_with_empty_evidence():
    model = valid_model()
    model["relationships"][0]["evidence"] = {}

    errors = validate_network_model(model)

    assert any("evidence" in error.lower() for error in errors)