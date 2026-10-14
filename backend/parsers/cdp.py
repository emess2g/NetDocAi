def parse_cdp(config: str):
    cdp = {
        "enabled": False,
        "neighbors": [],
    }

    lines = config.splitlines()
    current_interface = None

    for line in lines:
        line = line.strip()

        if line == "no cdp run":
            cdp["enabled"] = False

        elif line == "cdp run":
            cdp["enabled"] = True

        elif line.startswith("interface "):
            current_interface = line.split(" ", 1)[1]

        elif current_interface and line == "no cdp enable":
            current_interface = None

    # CDP neighbor data is normally learned dynamically,
    # so configuration alone can only tell us whether CDP
    # is enabled globally or disabled on an interface.

    return cdp
