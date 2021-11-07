from flask import Flask, render_template, render_template_string, Response, request
import os

from check import detect_remove_hacks
from filters import *

server = Flask(__name__)

# Add filters to the jinja environment to add string
# manipulation capabilities
server.jinja_env.filters["u"] = uppercase
server.jinja_env.filters["l"] = lowercase
server.jinja_env.filters["b64d"] = b64d
server.jinja_env.filters["order"] = order
server.jinja_env.filters["ch"] = character
server.jinja_env.filters["e"] = e

@server.route("/", methods=["GET", "POST"])
def render_secure_translate():
    payload = request.args.get("payload", "inputPa")
    print(f"Payload Parsed: {payload}")
    resp = render_template_string(str(detect_remove_hacks(payload)))
    return Response(response=resp, status=200)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 30069))
    server.run(host="0.0.0.0", port=port, debug=False)