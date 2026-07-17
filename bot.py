import os
from flask import Flask, request, jsonify
from google import genai

api = Flask(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(
    api_key=GEMINI_API_KEY
)

@api.route("/")
def home():
    return {
        "status": "online",
        "service": "HusnanAI"
    }

@api.route("/chat", methods=["POST"])
def chat():

    try:

        data = request.get_json()

        message = data.get("message", "")

        if not message:
            return jsonify({
                "reply": "Pesan kosong."
            })

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=message
        )

        return jsonify({
            "reply": response.text
        })

    except Exception as e:

        print("ERROR:", e)

        return jsonify({
            "reply": f"Error AI: {str(e)}"
        })

if __name__ == "__main__":

    port = int(os.getenv("PORT", 8080))

    api.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
