from limit import is_within_bounds, get_golf_limit


def allowlist_check(payload, allowlist):
    # Check against allowlist.
    print(f"Starting Allowlist Check with {payload} and {allowlist}")
    if set(payload) == set(allowlist) or set(payload) <= set(allowlist):
        return payload
    print(f"Failed Allowlist Check: {set(payload)} != {set(allowlist)}")
    return "Failed Allowlist Check, payload-allowlist=" + str(
        set(payload) - set(allowlist)
    )


def detect_remove_hacks(payload):
    # This effectively destroyes all web attack vectors.
    print(f"Received Payload with length:{len(payload)}")

    if not is_within_bounds(payload):
        return f"Payload is too long for current length limit of {get_golf_limit()} at {len(payload)} characters. Try locally."

    allowlist = [
        "c",
        "{",
        "}",
        "d",
        "6",
        "l",
        "(",
        "b",
        "o",
        "r",
        ")",
        '"',
        "1",
        "4",
        "+",
        "h",
        "u",
        "-",
        "*",
        "e",
        "|",
        "'",
    ]
    payload = allowlist_check(payload, allowlist)
    print(f"Allowlist Checked Payload -> {payload}")

    return payload
