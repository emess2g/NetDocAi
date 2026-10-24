from parsers.hostname import parse_hostname


def test_hostname_is_extracted():
    assert parse_hostname("hostname BRANCH-R1\n") == "BRANCH-R1"


def test_hostname_with_hyphens_and_digits_is_preserved():
    assert parse_hostname("hostname LAG-BR-RTR-01") == "LAG-BR-RTR-01"


def test_missing_hostname_returns_none():
    assert parse_hostname("interface GigabitEthernet0/0\n") is None


def test_first_hostname_declaration_is_returned():
    config = "hostname EDGE-R1\nhostname EDGE-R2"
    assert parse_hostname(config) == "EDGE-R1"
