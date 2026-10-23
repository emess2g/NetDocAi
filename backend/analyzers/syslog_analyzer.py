"""Turn Cisco Syslog events into actionable, UI-ready findings."""

SEVERITY_NAMES = {
    0: "critical",
    1: "critical",
    2: "critical",
    3: "high",
    4: "warning",
    5: "info",
    6: "info",
    7: "info",
}


def _classify(event: dict) -> tuple[str, str, str, str]:
    facility = event["facility"].upper()
    mnemonic = event["mnemonic"].upper()
    message = event["message"]
    message_upper = message.upper()
    combined = f"{facility}-{mnemonic}".upper()
    default = SEVERITY_NAMES.get(event["severity"], "info")

    # Operational BFD and SD-WAN signals need domain-specific severity.
    if facility == "BFD" or mnemonic == "SESSION_STATE":
        if "DOWN" in message_upper:
            return "high", "availability", "A BFD session went down.", (
                "Check the BFD peer and underlying interface, then correlate routing-neighbor "
                "state and packet loss to determine whether traffic was affected."
            )
        if "UP" in message_upper:
            return "info", "availability", "A BFD session came up.", (
                "Confirm the session remains stable and verify routing has converged on the expected path."
            )

    if facility in {"SDWAN", "SD-WAN"} or "SDWAN" in combined:
        if "PATH_MONITOR" in mnemonic and "INELIGIBLE" in message_upper:
            return "warning", "performance", "An SD-WAN path remains ineligible under its SLA.", (
                "Check latency, jitter, and packet loss against the configured SLA; verify the preferred "
                "path returns only after sustained compliance."
            )
        if "PATH_SWITCH" in mnemonic and any(phrase in message_upper for phrase in ("SLA VIOLATION", "LINK DOWN", "FAILURE")):
            return "warning", "availability", "SD-WAN traffic failed over to an alternate path.", (
                "Verify the alternate path is carrying affected traffic, inspect the failed path and SLA "
                "measurements, and confirm failback occurs only after the preferred path is stable."
            )
        if any(token in mnemonic for token in ("PATH_STABLE", "FAILOVER_COMPLETE")) or (
            "PATH_MONITOR" in mnemonic and "MEETS SLA" in message_upper
        ) or ("PATH_SWITCH" in mnemonic and any(phrase in message_upper for phrase in ("RETURNED TO", "MOVED BACK", "PREFERRED PATH"))):
            return "info", "availability", "SD-WAN path recovery or stability was reported.", (
                "Confirm latency, jitter, and loss remain within SLA and check for repeated path changes "
                "before considering the incident fully resolved."
            )

    # A route-refresh notification is a normal BGP capability/update exchange
    # in many environments; do not label it high severity solely from code 3.
    if "ROUTE REFRESH RECEIVED" in message_upper:
        return "info", "routing", "BGP route refresh received.", (
            "Usually informational. Confirm the BGP peer remains established and "
            "check for repeated notifications or adjacent session resets."
        )

    if mnemonic in {"LINK", "LINEPROTO", "UPDOWN"} or combined.startswith(("LINK-", "LINEPROTO-")):
        if re_state(message, "down"):
            return "high", "availability", "Interface or line protocol went down.", (
                "Check cabling, optics, peer status, interface errors, and recent changes."
            )
        if re_state(message, "up"):
            return "info", "availability", "Interface or line protocol came up.", (
                "Confirm the interface remains stable and check for repeated flapping."
            )

    if mnemonic == "IPACCESSLOGP" or "IPACCESSLOG" in mnemonic:
        return "warning", "security", "An access-control list denied traffic.", (
            "Review the ACL rule, source/destination, protocol, and counters to confirm "
            "the traffic was expected and the policy is correct."
        )
    if mnemonic == "CPUHOG":
        return "high", "performance", "A process is consuming CPU for longer than expected.", (
            "Check CPU utilization and process history; investigate traffic spikes or "
            "control-plane load before changing the configuration."
        )
    if mnemonic == "CACHEOVERFLOW":
        return "warning", "performance", "The NetFlow cache exceeded its configured maximum.", (
            "Inspect flow volume and cache/export settings; verify whether monitoring data "
            "is being dropped or delayed."
        )
    if mnemonic == "INVALID_QOS" or ("OUTPUT" in message_upper and "DROP" in message_upper):
        return "warning", "performance", "Output drops are increasing on an interface.", (
            "Check interface utilization, queue drops, QoS policy counters, and egress link capacity."
        )
    if mnemonic == "DROP" and "CAPWAP" in facility:
        return "warning", "wireless", "The access point reports packet loss on its CAPWAP control path.", (
            "Check AP-to-WLC reachability, latency, packet loss, routing, and firewall rules."
        )
    if mnemonic == "RADIO_OVERLOAD":
        return "high", "wireless", "A wireless radio exceeds its recommended client count.", (
            "Review airtime utilization and client distribution; consider load balancing or "
            "additional access-point capacity."
        )
    if mnemonic == "PSECURE_VIOLATION":
        return "high", "security", "Port security detected an unauthorized or unexpected MAC address.", (
            "Verify the endpoint and switchport assignment, inspect port-security mode and counters, "
            "and follow the site's response process before clearing the violation."
        )

    # Recognize common operational events by their message as well as event code,
    # since Cisco platforms do not use identical mnemonics for every subsystem.
    if "ROUTEMAP" in facility or "ROUTE-MAP" in message_upper or "ROUTE MAP" in message_upper:
        return "info", "configuration_change", "A route-map configuration change was reported.", (
            "Confirm the change was authorized, compare the route-map with the approved baseline, "
            "and check whether affected routes or policies changed."
        )
    if ("IP SLA" in message_upper or "IPSLA" in facility) and any(
        word in message_upper for word in ("THRESHOLD", "VIOLATION", "EXCEEDED")
    ):
        return "warning", "performance", "An IP SLA operation crossed its configured threshold.", (
            "Inspect the SLA operation, target reachability, measured latency/loss, and threshold "
            "settings; correlate with interface and path events at the same time."
        )
    if any(word in message_upper for word in ("IPSEC", "IPSEC", "IPSEC TUNNEL", "IPSEC")) and (
        "TUNNEL" in message_upper and any(word in message_upper for word in ("DOWN", "FAIL", "FAILED"))
    ):
        return "high", "availability", "An IPsec tunnel is down or failing.", (
            "Check peer reachability, IKE/IPsec security associations, authentication and proposal "
            "mismatches, and recent WAN or firewall changes."
        )
    if ("MPLS" in message_upper or "LSP" in message_upper) and any(
        word in message_upper for word in ("DEGRADED", "DOWN", "FAIL", "FAILED")
    ):
        return "high", "routing", "An MPLS label-switched path may be degraded or unavailable.", (
            "Check LSP status, label distribution, next-hop reachability, and provider/core link "
            "health; identify services using the affected path."
        )
    if "TCP" in message_upper and any(
        word in message_upper for word in ("TIMEOUT", "TIMED OUT", "CONNECTION FAILED")
    ):
        return "warning", "connectivity", "A TCP connection timed out or failed.", (
            "Identify the source, destination, and service; test reachability and port availability, "
            "then correlate firewall, routing, and server logs for the same time window."
        )
    if mnemonic == "CONFIG_I" or "CONFIG_I" in combined or "CONFIGURATION CHANGE" in message_upper:
        return "info", "configuration_change", "A configuration change was recorded.", (
            "Verify the change against the approved change record and review the command/audit log "
            "for the responsible session and any unexpected follow-on events."
        )

    return default, "operations", f"Syslog event {facility}-{mnemonic}.", (
        "Review the event message, device state, and nearby events; use the event code and timestamp "
        "to correlate with interface, routing, and service logs before taking action."
    )


def re_state(message: str, state: str) -> bool:
    return f"state to {state}".lower() in message.lower()


def analyze_syslog_events(events: list[dict]) -> list[dict]:
    findings = []
    for event in events:
        severity, category, title, recommendation = _classify(event)
        findings.append({
            "severity": severity,
            "category": category,
            "device": event["device"],
            "timestamp": event["timestamp"],
            "event_code": f'{event["facility"]}-{event["severity"]}-{event["mnemonic"]}',
            "syslog_severity": event["severity"],
            "finding": title,
            "impact": event["message"],
            "evidence": [event["raw"]],
            "recommendation": recommendation,
            "line_number": event["line_number"],
        })
    return findings
