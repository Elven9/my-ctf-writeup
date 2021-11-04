from flask import Flask, request, render_template, Response
from flask_cors import CORS

from RetrOPwn.state_management import *
import Plugin.web.csp as routeCsp

# Create Flask App
app = Flask(__name__)

# Add Plugin
CORS(app)

# Initialize Module
routeCsp.RegisterRoute(app)

# Basic Map Content IO
@app.route("/bm/read/<key>", methods=["GET"])
def get_basic_map_content(key):
    try:
        return Basic_Map_Content[key]
    except:
        res = Response("Key Not Found")
        res.status_code = 404
        return res

@app.route("/bm/write", methods=["POST"])
def write_basic_map_content():
    payload = request.get_json()

    if payload["key"] in Basic_Map_Content.keys():
        Basic_Map_Content[payload["key"]] = payload["value"]
        return "Override"
    else:
        Basic_Map_Content[payload["key"]] = payload["value"]
        return "Create"

# Maybe Add File Download Support

if __name__ == "__main__":
    app.run("127.0.0.1", 9000)

