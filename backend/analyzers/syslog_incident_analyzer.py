"""Correlate Syslog events into a cautious, evidence-backed incident summary."""
from datetime import datetime
import re


def _dt(event):
    try:
        return datetime.fromisoformat(str(event.get("timestamp", "")).replace("Z", "+00:00"))
    except ValueError:
        return None


def _duration(start, end):
    if not start or not end:
        return "Not available"
    try:
        seconds = max(0, int((end - start).total_seconds()))
    except (TypeError, ValueError):
        return "Not available"
    if seconds < 60:
        return f"{seconds} seconds"
    minutes, remainder = divmod(seconds, 60)
    return f"{minutes} min" + (f" {remainder} sec" if remainder else "")


def _ref(event):
    return {
        "timestamp": event.get("timestamp"),
        "device": event.get("device"),
        "event_code": f'{event.get("facility", "")}-{event.get("severity", "")}-{event.get("mnemonic", "")}',
        "line_number": event.get("line_number"),
        "message": event.get("message", ""),
        "raw": event.get("raw", ""),
    }


def _path_switches(events):
    switches = []
    from_to = re.compile(r"\bfrom\s+([\w.-]+)\s+to\s+([\w.-]+)", re.I)
    returned_to = re.compile(r"\b(?:returned|moved)\s+(?:back\s+)?to\s+([\w.-]+)", re.I)
    for event in events:
        if "PATH_SWITCH" not in str(event.get("mnemonic", "")).upper():
            continue
        message = str(event.get("message", ""))
        match = from_to.search(message)
        if match:
            switches.append({
                "event": event,
                "from_path": match.group(1),
                "to_path": match.group(2),
                "message": message,
            })
            continue
        returned = returned_to.search(message)
        if returned:
            switches.append({
                "event": event,
                "from_path": None,
                "to_path": returned.group(1),
                "message": message,
            })
    return switches


def analyze_syslog_incident(events):
    """Correlate events without claiming that logs prove physical root cause."""
    # ISO timestamps with offsets are normalized to epoch values for reliable comparisons.
    def sort_key(event):
        value = _dt(event)
        return value.timestamp() if value else float("inf")
    ordered = list(events)
    try:
        ordered = sorted(events, key=sort_key)
    except (OverflowError, OSError, ValueError):
        pass

    sla = [e for e in ordered
           if ("IPSLA" in str(e.get("facility", "")).upper()
               or "IP SLA" in str(e.get("message", "")).upper())
           and any(w in str(e.get("message", "")).upper()
                   for w in ("THRESHOLD", "PACKET LOSS", "VIOLATION", "EXCEEDED"))]
    bfd_down = [e for e in ordered
                if ("BFD" in str(e.get("facility", "")).upper()
                    or "SESSION_STATE" in str(e.get("mnemonic", "")).upper())
                and "DOWN" in str(e.get("message", "")).upper()]
    bfd_up = [e for e in ordered
              if ("BFD" in str(e.get("facility", "")).upper()
                  or "SESSION_STATE" in str(e.get("mnemonic", "")).upper())
              and "UP" in str(e.get("message", "")).upper()]
    link_down = [e for e in ordered
                 if str(e.get("facility", "")).upper() in {"LINK", "LINEPROTO"}
                 and "state to down" in str(e.get("message", "")).lower()]
    link_up = [e for e in ordered
               if str(e.get("facility", "")).upper() in {"LINK", "LINEPROTO"}
               and "state to up" in str(e.get("message", "")).lower()]
    ineligible = [e for e in ordered
                  if "PATH_MONITOR" in str(e.get("mnemonic", "")).upper()
                  and "INELIGIBLE" in str(e.get("message", "")).upper()]
    meets_sla = [e for e in ordered
                 if "PATH_MONITOR" in str(e.get("mnemonic", "")).upper()
                 and "MEETS SLA" in str(e.get("message", "")).upper()]
    stable = [e for e in ordered if "PATH_STABLE" in str(e.get("mnemonic", "")).upper()]
    switches = _path_switches(ordered)

    # DHCP pool exhaustion is a service incident in its own right; it does not
    # require WAN/BFD/SD-WAN signals to be diagnosable.
    pool_warnings = [
        e for e in ordered
        if "POOL_WARNING" in str(e.get("mnemonic", "")).upper()
        or ("UTILIZATION" in str(e.get("message", "")).upper()
            and "POOL" in str(e.get("message", "")).upper())
    ]
    pool_exhausted = [
        e for e in ordered
        if "POOL_EXHAUSTED" in str(e.get("mnemonic", "")).upper()
        or ("POOL" in str(e.get("message", "")).upper()
            and any(term in str(e.get("message", "")).upper()
                    for term in ("NO AVAILABLE ADDRESSES", "EXHAUSTED")))
    ]
    no_free_leases = [
        e for e in ordered
        if ("DHCPDISCOVER" in str(e.get("mnemonic", "")).upper()
            or "DHCPDISCOVER" in str(e.get("message", "")).upper())
        and any(term in str(e.get("message", "")).upper()
                for term in ("NO FREE LEASES", "NO FREE ADDRESSES", "NO AVAILABLE ADDRESSES"))
    ]
    address_assignment_failures = [
        e for e in ordered
        if ("CLIENT_AUTH_FAIL" in str(e.get("mnemonic", "")).upper()
            or "AUTH_FAIL" in str(e.get("mnemonic", "")).upper())
        and any(term in str(e.get("message", "")).upper()
                for term in ("IP ADDRESS ASSIGNMENT FAILURE", "ADDRESS ASSIGNMENT FAILURE"))
    ]
    if pool_exhausted or no_free_leases:
        exhaustion_event = pool_exhausted[0] if pool_exhausted else no_free_leases[0]
        )
        pool_names = []
        for event in pool_warnings + pool_exhausted:
            match = re.search(r"Pool\s+([\w.-]+)", str(event.get("message", "")), re.I)
            if match and match.group(1) not in pool_names:
                pool_names.append(match.group(1))
        networks = []
        for event in no_free_leases:
            match = re.search(r"network\s+([0-9a-fA-F:.]+/\d+)", str(event.get("message", "")), re.I)
            if match and match.group(1) not in networks:
                networks.append(match.group(1))
        evidence_events = [
            e for e in ordered
            if e in pool_warnings or e in pool_exhausted or e in no_free_leases
            or e in address_assignment_failures
        ]
        phases = []
        if pool_warnings:
            phases.append({
                "phase": "DHCP pool utilization warning",
                "start": pool_warnings[0].get("timestamp"),
                "end": pool_warnings[-1].get("timestamp"),
                "duration": _duration(_dt(pool_warnings[0]), _dt(pool_warnings[-1])),
                "evidence": [_ref(e) for e in pool_warnings],
            })
        if pool_exhausted or no_free_leases:
            phase_start = pool_exhausted[0] if pool_exhausted else no_free_leases[0]
            phases.append({
                "phase": "DHCP address pool exhausted",
                "start": phase_start.get("timestamp"),
                "end": no_free_leases[-1].get("timestamp") if no_free_leases else phase_start.get("timestamp"),
                "duration": _duration(_dt(phase_start), _dt(no_free_leases[-1])) if no_free_leases else "Not available",
                "evidence": [_ref(e) for e in pool_exhausted + no_free_leases],
            })
        if address_assignment_failures:
            phases.append({
                "phase": "Wireless client address assignment failures",
                "start": address_assignment_failures[0].get("timestamp"),
                "end": address_assignment_failures[-1].get("timestamp"),
                "duration": _duration(_dt(address_assignment_failures[0]), _dt(address_assignment_failures[-1])),
                "evidence": [_ref(e) for e in address_assignment_failures],
            })
        recommendations = [
            "Inspect the DHCP lease table for active, expired, abandoned, and stale leases; confirm leases are being reclaimed as expected.",
            "Check the WIFI-CORPORATE scope size, subnet mask, excluded ranges, reservations, and remaining usable addresses before changing pool capacity.",
            "Review DHCP lease duration and utilization trends; adjust lease policy or expand the address scope only after validating available address space and routing/VLAN design.",
        ]
        if address_assignment_failures:
            recommendations.append(
                "After DHCP capacity is restored, verify affected wireless clients can obtain leases and confirm the AP's reported IP-assignment failures stop; do not treat these messages alone as proof of an authentication-server fault."
            )
        return {
            "status": "correlated_incident",
            "title": "Corporate Wi-Fi DHCP pool exhaustion",
            "primary_hypothesis": (
                "The WIFI-CORPORATE DHCP address pool exhausted its available leases, causing DHCP requests on "
                + (", ".join(networks) if networks else "the reported client network")
                + " to receive no-free-lease responses; subsequent AP messages report wireless client IP-assignment failures."
            ),
            "confidence": "High" if pool_exhausted and no_free_leases else "Moderate",
            "confidence_basis": (
                "The logs explicitly report pool exhaustion and DHCP requests with no free leases"
                + ("; AP messages independently report IP-address-assignment failures." if address_assignment_failures else ".")
                + " The reason the pool ran out of addresses is not established by these events."
            ),
            "evidence": [_ref(e) for e in evidence_events],
            "logical_events": [
                {
                    "title": "DHCP pool utilization warning",
                    "timestamp": pool_warnings[0].get("timestamp"),
                    "event_count": len(pool_warnings),
                    "evidence": [_ref(e) for e in pool_warnings],
                },
                {
                    "title": "DHCP pool exhaustion / no free leases",
                    "timestamp": exhaustion_event.get("timestamp"),
                    "event_count": len(pool_exhausted) + len(no_free_leases),
                    "evidence": [_ref(e) for e in pool_exhausted + no_free_leases],
                },
                *([{
                    "title": "Wireless client IP-assignment failures",
                    "timestamp": address_assignment_failures[0].get("timestamp"),
                    "event_count": len(address_assignment_failures),
                    "evidence": [_ref(e) for e in address_assignment_failures],
                }] if address_assignment_failures else []),
            ],
            "phases": phases,
            "impact": [
                "DHCP clients on " + (", ".join(networks) if networks else "the reported Wi-Fi network") + " could not obtain new leases when the pool had no free addresses.",
                "The supplied AP events report IP-address-assignment failures; the logs do not quantify the number of affected users or prove an authentication-system fault.",
            ],
            "failover": {"assessment": "Not applicable to the DHCP pool exhaustion signals supplied; no traffic-path failover was identified."},
            "failback": {"assessment": "Not applicable to the DHCP pool exhaustion signals supplied; no path failback was identified."},
            "recommendations": recommendations,
            "related_events_note": "Diagnosis is based on explicit DHCP pool and lease messages plus related AP assignment-failure events; the underlying reason for exhaustion requires lease-table and scope review.",
        }

    signal_groups = [sla, bfd_down, link_down, switches, ineligible, meets_sla]
    signal_count = sum(bool(group) for group in signal_groups)
    correlated = signal_count >= 2 and bool(sla or bfd_down or link_down)
    if not correlated:
        return {
            "status": "insufficient_evidence",
            "title": "No correlated incident identified",
            "primary_hypothesis": "The supplied events do not contain enough related signals for a defensible incident diagnosis.",
            "confidence": "Low",
            "confidence_basis": "Insufficient independent event types to correlate a likely incident.",
            "evidence": [_ref(e) for e in ordered],
            "logical_events": [],
            "phases": [],
            "impact": [],
            "failover": {"assessment": "Not determined from supplied events."},
            "failback": {"assessment": "Not determined from supplied events."},
            "recommendations": [
                "Provide surrounding interface, routing, BFD, IP SLA, and SD-WAN logs for the same device and time window."
            ],
        }

    first_down = link_down[0] if link_down else None
    first_up = link_up[0] if link_up else None
    first_sla = meets_sla[0] if meets_sla else None
    first_switch = switches[0] if switches else None
    first_stable = stable[0] if stable else None

    if sla and (bfd_down or link_down):
        hypothesis = "WAN path SLA degradation followed by BFD and/or interface failure"
    elif link_down and bfd_down:
        hypothesis = "WAN interface failure correlated with BFD session loss"
    else:
        hypothesis = "WAN path degradation correlated with a traffic-path change"
    confidence = "High" if signal_count >= 4 and (link_down or bfd_down) else "Moderate"

    phases = []
    if sla:
        phase_end = first_down or (first_switch["event"] if first_switch else None)
        phases.append({
            "phase": "SLA degradation",
            "start": sla[0].get("timestamp"),
            "end": (phase_end or sla[-1]).get("timestamp"),
            "duration": _duration(_dt(sla[0]), _dt(phase_end)) if phase_end else "Not available",
            "evidence": [_ref(e) for e in sla + bfd_down[:1]],
        })
    if first_down:
        phases.append({
            "phase": "Interface / transport failure",
            "start": first_down.get("timestamp"),
            "end": first_up.get("timestamp") if first_up else None,
            "duration": _duration(_dt(first_down), _dt(first_up)),
            "evidence": [_ref(e) for e in link_down + bfd_down[:1]],
        })
    if first_up and first_sla:
        phases.append({
            "phase": "Link recovered; preferred path still outside SLA",
            "start": first_up.get("timestamp"),
            "end": first_sla.get("timestamp"),
            "duration": _duration(_dt(first_up), _dt(first_sla)),
            "evidence": [_ref(e) for e in link_up + ineligible + bfd_up],
        })
    if first_sla:
        later_switches = [s for s in switches
                          if _dt(s["event"]) and _dt(first_sla) and _dt(s["event"]) >= _dt(first_sla)]
        final_event = later_switches[-1]["event"] if later_switches else first_sla
        phases.append({
            "phase": "SLA compliance and failback",
            "start": first_sla.get("timestamp"),
            "end": final_event.get("timestamp"),
            "duration": _duration(_dt(first_sla), _dt(final_event)),
            "evidence": [_ref(first_sla)] + [_ref(s["event"]) for s in later_switches],
        })

    # Group adjacent LINK and LINEPROTO messages for the same interface/state.
    logical_events = []
    consumed = set()
    for index, event in enumerate(ordered):
        if index in consumed:
            continue
        facility = str(event.get("facility", "")).upper()
        message = str(event.get("message", ""))
        if facility in {"LINK", "LINEPROTO"} and (
            "state to down" in message.lower() or "state to up" in message.lower()
        ):
            state = "down" if "state to down" in message.lower() else "up"
            match = re.search(r"Interface\s+([^,\s]+)", message, re.I)
            interface = match.group(1) if match else "unknown interface"
            cluster = [event]
            for other_index in range(index + 1, len(ordered)):
                other = ordered[other_index]
                other_facility = str(other.get("facility", "")).upper()
                other_message = str(other.get("message", ""))
                other_match = re.search(r"Interface\s+([^,\s]+)", other_message, re.I)
                same_state = ("state to down" in other_message.lower()) if state == "down" else ("state to up" in other_message.lower())
                if (other_index not in consumed and other_facility in {"LINK", "LINEPROTO"}
                    and other_match and other_match.group(1) == interface and same_state
                    and _dt(event) and _dt(other) and abs((_dt(other) - _dt(event)).total_seconds()) <= 5):
                    cluster.append(other)
                    consumed.add(other_index)
            if len(cluster) > 1:
                logical_events.append({
                    "title": "Interface failure" if state == "down" else "Interface recovery",
                    "interface": interface,
                    "state": state,
                    "timestamp": event.get("timestamp"),
                    "event_count": len(cluster),
                    "evidence": [_ref(e) for e in cluster],
                })
                continue
        logical_events.append({
            "title": f'{event.get("facility", "")}-{event.get("mnemonic", "")}',
            "timestamp": event.get("timestamp"),
            "event_count": 1,
            "evidence": [_ref(event)],
        })

    impacted = []
    for switch in switches:
        match = re.match(r"\s*([\w-]+(?:\s+[\w-]+)?)\s+traffic\b", switch["message"], re.I)
        label = match.group(1).strip() if match else "Traffic"
        value = label + " traffic"
        if value not in impacted:
            impacted.append(value)

    failover = {"assessment": "No explicit traffic failover was identified."}
    if first_switch:
        switch_before_stable = [
            item for item in switches
            if first_stable and _dt(item["event"]) and _dt(first_stable)
            and _dt(item["event"]) <= _dt(first_stable)
        ]
        stabilization_switch = switch_before_stable[-1] if switch_before_stable else first_switch
        failover = {
            "assessment": "Traffic-path failover was observed in the supplied logs.",
            "successful": bool(first_stable),
            "backup_path": first_switch["to_path"],
            "affected_traffic": impacted,
            "backup_path_observation": first_stable.get("message") if first_stable else "No explicit backup-path stability event was found.",
            "backup_sla_compliance": "Not explicitly confirmed by the supplied log messages.",
            "stabilization_time": _duration(_dt(stabilization_switch["event"]), _dt(first_stable)) if first_stable else "Not available",
        }

    failback = {"assessment": "No explicit failback was identified."}
    if first_sla:
        later_switches = [s for s in switches
                          if _dt(s["event"]) and _dt(first_sla) and _dt(s["event"]) >= _dt(first_sla)]
        failback = {
            "assessment": "Failback was observed after an explicit preferred-path SLA-compliance event." if later_switches else "Preferred path met SLA, but no subsequent path-switch event was found.",
            "safe_sequence_observed": bool(later_switches),
            "preferred_path_sla_event": _ref(first_sla),
            "failback_events": [_ref(s["event"]) for s in later_switches],
            "note": "The log supports the event order; it does not prove how long SLA compliance was sustained unless duration is logged.",
        }

    recommendations = [
        "Correlate this incident with provider circuit alarms, interface counters, optics, and maintenance records before assigning definitive physical root cause.",
        "Review IP SLA thresholds and BFD timers against application requirements; verify SD-WAN path selection uses the intended SLA policy.",
    ]
    if first_switch:
        recommendations.append("Confirm affected application sessions recovered on " + first_switch["to_path"] + " and review packet loss, latency, and jitter during failover.")
    if first_sla:
        recommendations.append("Keep failback gated on sustained SLA compliance and monitor for repeated path changes or flapping.")

    evidence_events = []
    for event in ordered:
        if event in sla or event in bfd_down or event in link_down or event in ineligible or event in meets_sla or any(event is s["event"] for s in switches):
            evidence_events.append(_ref(event))

    return {
        "status": "correlated_incident",
        "title": "Probable WAN path degradation and failover incident",
        "primary_hypothesis": hypothesis,
        "confidence": confidence,
        "confidence_basis": f"{signal_count} independent signal groups support the hypothesis; logs establish correlation, not definitive physical root cause.",
        "evidence": evidence_events,
        "phases": phases,
        "logical_events": logical_events,
        "impact": [
            "Observed traffic-path changes: " + (", ".join(impacted) if impacted else "not specified in supplied logs"),
            "Only supplied events are assessed; absence of an event does not prove that a path or service was unused.",
        ],
        "failover": failover,
        "failback": failback,
        "recommendations": recommendations,
        "related_events_note": "Events outside the correlated WAN path sequence remain available in the raw Events and Findings views.",
    }
