import json
from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/decide", methods=["POST"])
def decide():
    data = request.get_json()
    print(json.dumps(data, indent=2))
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080)
