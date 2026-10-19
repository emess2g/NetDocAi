from parsers.security import parse_security


def test_empty_config_returns_default_security_settings():
    result = parse_security("")

    assert result["ssh"] is False
    assert result["telnet"] is False
    assert result["enable_secret"] is False
    assert result["plaintext_passwords"] is False
    assert result["service_password_encryption"] is False


def test_enable_password_is_detected():
    result = parse_security("enable password mypassword")

    assert result["plaintext_passwords"] is True


def test_service_password_encryption_is_detected():
    result = parse_security("service password-encryption")

    assert result["service_password_encryption"] is True


def test_password_encryption_setting_is_independent_of_command_order():
    first = parse_security(
        "service password-encryption\nenable password 7 0822455D0A16"
    )
    second = parse_security(
        "enable password mypassword\nservice password-encryption"
    )

    assert first["service_password_encryption"] is True
    assert second["service_password_encryption"] is True
    assert first["plaintext_passwords"] is True
    assert second["plaintext_passwords"] is True


def test_ssh_and_telnet_transport_are_detected():
    config = """
line vty 0 4
 transport input telnet ssh
"""
    result = parse_security(config)

    assert result["ssh"] is True
    assert result["telnet"] is True
    assert result["vty_transport"] == [
        {"line": "0 4", "transport": "telnet ssh"}
    ]


def test_ssh_only_transport_does_not_enable_telnet():
    config = """
line vty 0 4
 transport input ssh
"""
    result = parse_security(config)

    assert result["ssh"] is True
    assert result["telnet"] is False


def test_local_users_are_detected():
    result = parse_security(
        "username admin privilege 15 secret 9 example"
    )

    assert result["local_users"] == ["admin"]


def test_domain_and_rsa_settings_are_detected():
    config = """
ip domain-name example.local
crypto key generate rsa modulus 2048
"""
    result = parse_security(config)

    assert result["ssh_domain"] == "example.local"
    assert result["ssh_rsa"] is True
