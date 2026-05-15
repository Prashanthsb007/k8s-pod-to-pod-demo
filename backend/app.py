from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow frontend pod to call backend pod

votes = {"Dogs": 0, "Cats": 0}

@app.route("/vote/<option>", methods=["POST"])
def vote(option):
    if option not in votes:
        return jsonify({"error": "Invalid option"}), 400
    votes[option] += 1
    return jsonify({"message": f"Voted for {option}!", "votes": votes})

@app.route("/votes", methods=["GET"])
def get_votes():
    return jsonify(votes)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)