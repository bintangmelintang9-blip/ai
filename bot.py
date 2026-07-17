import os
from flask import Flask, request, jsonify

api = Flask(__name__)

@api.route("/")
def home():
    return {
        "status": "online",
        "service": "HusnanAI"
    }

@api.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()

    user_id = data.get("user_id", "unknown")
    message = data.get("message", "")

    if not message:
        return jsonify({
            "reply": "Pesan kosong."
        })

    # sementara echo test
    return jsonify({
        "reply": f"Halo, Anda berkata: {message}"
    })

if __name__ == "__main__":

    port = int(os.getenv("PORT", 8080))

    api.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
