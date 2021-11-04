# CSP Related Route
from flask import request, Flask
import json

from RetrOPwn.web.csp import CSP_Breaker
from RetrOPwn.state_management import *

# Register URL
def RegisterRoute(app: Flask):
    DEFAULT_CSP_BASE_URL = "/module/csp"

    app.add_url_rule(DEFAULT_CSP_BASE_URL+"/report_csp", view_func=report_csp, methods=["POST"])

def report_csp():
    data = json.loads(request.get_data())

    csp_breaker = CSP_Breaker()
    csp_breaker.extractReport(data)

    Basic_Map_Content["csp-nonce"] = csp_breaker.csp_rule["script-src"][0][7:-1]

    print(Basic_Map_Content["csp-nonce"])

    return "ok"
