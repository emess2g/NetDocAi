
def analyze_acls(acls):
    findings = []

    for acl in acls:
        acl_number = acl.get("number")

        for entry in acl.get("entries", []):
            action = entry.get("action")

            # -----------------------------
            # Standard ACL
            # -----------------------------
            source = entry.get("source")

            if action == "permit" and source == "any":
                findings.append({
                    "severity": "warning",
                    "category": "acl",
                    "device": f"ACL {acl_number}",
                    "finding": "ACL permits traffic from any source.",
                    "recommendation": (
                        "Restrict the source to only the networks "
                        "or hosts that require access."
                    )
                })

            # -----------------------------
            # Extended ACL
            # -----------------------------
            rule = entry.get("rule", "").strip()

            if action == "permit" and rule == "ip any any":
                findings.append({
                    "severity": "warning",
                    "category": "acl",
                    "device": f"ACL {acl_number}",
                    "finding": "ACL contains a permit any-any rule.",
                    "recommendation": (
                        "Restrict the rule to only the required "
                        "source and destination traffic."
                    )
                })

    return findings


