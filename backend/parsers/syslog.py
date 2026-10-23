"""Parse timestamped Cisco Syslog messages into structured events."""
import re

SYSLOG_LINE = re.compile(
    r"^(?P<timestamp>\S+)\s+"
    r"(?P<device>\S+)\s+"
    r"%(?P<facility>[A-Z0-9_-]+)-(?P<severity>[0-7])-"
    r"(?P<mnemonic>[A-Z0-9_-]+):\s*"
    r"(?P<message>.*)$"
)


def parse_syslog(config: str) -> list[dict]:
    """Return recognized Syslog lines; unrelated lines are ignored."""
    events = []
    for line_number, raw_line in enumerate(config.splitlines(), start=1):
        line = raw_line.strip()
        match = SYSLOG_LINE.match(line)
        if not match:
            continue
        event = match.groupdict()
        event["severity"] = int(event["severity"])
        event["line_number"] = line_number
        event["raw"] = line
        events.append(event)
    return events


def looks_like_syslog(text: str) -> bool:
    """Require at least one valid Cisco Syslog message to avoid false positives."""
    return bool(parse_syslog(text))
