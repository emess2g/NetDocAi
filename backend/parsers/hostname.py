def parse_hostname(config: str):
    for line in config.splitlines():
        line = line.strip()

        if line.startswith("hostname "):
            return line.split(" ", 1)[1]

    return None