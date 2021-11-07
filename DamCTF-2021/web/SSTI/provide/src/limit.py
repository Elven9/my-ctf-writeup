import time

from rctf import golf

def get_golf_limit() -> int:
    rctf_host = "https://damctf.xyz/"
    challenge_id = "super-secure-translation-implementation"
    ctf_start = 1636156800
    limit_function = lambda x: (x * 2) + 147

    limit = golf.calculate_limit(rctf_host, challenge_id, ctf_start, limit_function)
    return limit


def is_within_bounds(payload: str) -> bool:

    return len(payload) <= get_golf_limit()