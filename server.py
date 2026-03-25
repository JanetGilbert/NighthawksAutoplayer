import json
import sys
from flask import Flask, request, jsonify
import llm

sys.stdout.reconfigure(line_buffering=True)

app = Flask(__name__)


@app.route("/decide", methods=["POST"])
def decide():
    data = request.get_json()
    #print(json.dumps(data, indent=2))

    choices = data.get("choices", [])
    if len(choices) == 0:
        print("ERROR: No choices available")
        return jsonify({"result": -1})
    
    if len(choices) == 1:
        print("Single option")
        return jsonify({"result": choices[0], "justification": "Only choice"})
    
    pick, justification = llm.decide(data, choices)
    return jsonify({"result": pick, "justification": justification})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080)
