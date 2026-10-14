
def parse_acls(config: str):
    acls = []
    acl_map = {}
    current_acl = None

    for raw_line in config.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        # --------------------------------------------------
        # Numbered ACL
        # Example:
        # access-list 10 permit 192.168.1.0 0.0.0.255
        # access-list 10 deny any
        # --------------------------------------------------
        if line.startswith("access-list "):
            parts = line.split()

            if len(parts) >= 4:
                acl_number = parts[1]
                action = parts[2]

                # Create the ACL only once
                if acl_number not in acl_map:
                    acl = {
                        "number": acl_number,
                        "type": "standard",
                        "entries": [],
                    }

                    acl_map[acl_number] = acl
                    acls.append(acl)
                else:
                    acl = acl_map[acl_number]

                # Numbered ACLs 1-99 are standard,
                # 100-199 are extended.
                try:
                    number = int(acl_number)

                    if 100 <= number <= 199:
                        acl["type"] = "extended"
                    else:
                        acl["type"] = "standard"

                except ValueError:
                    acl["type"] = "standard"

                # Add entry to existing ACL
                acl["entries"].append({
                    "action": action,
                    "source": " ".join(parts[3:]),
                })

            continue

        # --------------------------------------------------
        # Named ACL
        # Example:
        # ip access-list extended WEB-FILTER
        # --------------------------------------------------
        if line.startswith("ip access-list "):
            parts = line.split()

            if len(parts) >= 4:
                acl_type = parts[2]
                acl_name = parts[3]

                current_acl = {
                    "number": acl_name,
                    "type": acl_type,
                    "entries": [],
                }

                acls.append(current_acl)

            continue

        # --------------------------------------------------
        # Named ACL entries
        # Example:
        # permit tcp 192.168.10.0 0.0.0.255 any eq 80
        # deny ip any any
        # --------------------------------------------------
        if current_acl and (
            line.startswith("permit ")
            or line.startswith("deny ")
        ):
            parts = line.split()

            if len(parts) >= 2:
                current_acl["entries"].append({
                    "action": parts[0],
                    "rule": " ".join(parts[1:]),
                })

    return acls
