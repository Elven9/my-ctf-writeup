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


@server.route("/")
@server.route("/<path>")
def index(path=""):
    # Show app.py source code on homepage, even if not requested.
    if path == "":
        path = "app.py"

    # Make this request hackproof, ensuring that only app.py is displayed.
    elif not os.path.exists(path) or "/" in path or ".." in path:
        path = "app.py"

    # User requested app.py, show that.
    with open(path, "r") as f:
        return render_template("index.html", code=f.read())


@server.route("/secure_translate/", methods=["GET", "POST"])
def render_secure_translate():
    payload = request.args.get("payload", "secure_translate.html")
    print(f"Payload Parsed: {payload}")
    resp = render_template_string(
        """{% extends "secure_translate.html" %}{% block content %}<p>"""
        + str(detect_remove_hacks(payload))
        + """</p><a href="/">Take Me Home</a>{% endblock %}"""
    )
    return Response(response=resp, status=200)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 30069))
    server.run(host="0.0.0.0", port=port, debug=False)