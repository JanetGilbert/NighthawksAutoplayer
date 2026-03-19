import json
import random
from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/decide", methods=["POST"])
def decide():
    data = request.get_json()
    print(json.dumps(data, indent=2))

    choices = data.get("choices", [])
    if len(choices) == 0:
        print("ERROR: No choices available")
        return jsonify({"status": "error", "message": "no choices"})

    pick = random.randrange(len(choices))
    print("pick:"+str(pick))
    return jsonify({"result": pick})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080)
