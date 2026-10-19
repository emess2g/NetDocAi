
def parse_acls(config: str):
    acls = []
    acl_map = {}
    current_acl = None

    for raw_line in config.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        # Numbered ACL
        if line.startswith("access-list "):
            parts = line.split()

            if len(parts) >= 4:
                acl_number = parts[1]
                action = parts[2].lower()

                try:
                    number = int(acl_number)
                except ValueError:
                    number = -1

                standard_acl = (
                    1 <= number <= 99
                    or 1300 <= number <= 1999
                )
                extended_acl = (
                    100 <= number <= 199
                    or 2000 <= number <= 2699
                )

                if action in {"permit", "deny"} and (
                    standard_acl or extended_acl
                ):
                    if acl_number not in acl_map:
                        acl_type = (
                            "standard" if standard_acl else "extended"
                        )

                        acl = {
                            "number": acl_number,
                            "type": acl_type,
                            "entries": [],
                        }

                        acl_map[acl_number] = acl
                        acls.append(acl)

                    acl_map[acl_number]["entries"].append({
                        "action": action,
                        "source": " ".join(parts[3:]),
                    })

            current_acl = None
            continue

        # Named ACL declaration
        if line.startswith("ip access-list "):
            parts = line.split()

            if len(parts) >= 4:
                acl_type = parts[2].lower()
                acl_name = parts[3]
                key = f"named:{acl_name}"

                if key not in acl_map:
                    current_acl = {
                        "number": acl_name,
                        "type": acl_type,
                        "entries": [],
                    }

                    acl_map[key] = current_acl
                    acls.append(current_acl)
                else:
                    current_acl = acl_map[key]
                    current_acl["type"] = acl_type
            else:
                current_acl = None

            continue

        # Any other top-level command ends named ACL context
        if not raw_line[:1].isspace():
            current_acl = None
            continue

        # Entries inside a named ACL
        if current_acl and (
            line.startswith("permit ")
            or line.startswith("deny ")
        ):
            parts = line.split()

            if len(parts) >= 2:
                current_acl["entries"].append({
                    "action": parts[0].lower(),
                    "rule": " ".join(parts[1:]),
                })

    return acls
