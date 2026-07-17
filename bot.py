import os
from flask import Flask, request, jsonify
from google import genai

api = Flask(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(
    api_key=GEMINI_API_KEY
)

SYSTEM_PROMPT = """
Kamu adalah KocakAi.

Aturan:
- Selalu menjawab dalam bahasa Indonesia.
- Ramah, membantu, dan santai.
- Boleh menyisipkan humor ringan jika sesuai.
- Jawaban harus jelas dan mudah dipahami.
- Jangan mengaku sebagai Gemini atau Google AI.
"""

@api.route("/")
def home():
    return {
        "status": "online",
        "service": "KocakAi",
        "creator": "Sulaiman"
    }

@api.route("/chat", methods=["POST"])
def chat():

    try:

        data = request.get_json()

        message = data.get("message", "")

        if not message:
            return jsonify({
                "reply": "Pesan kosong.\n\n🤖 Created by Sulaiman"
            })

        prompt = f"""
{SYSTEM_PROMPT}

Pesan pengguna:
{message}
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        answer = response.text.strip()

        answer += "\n\n🤖 Created by Sulaiman"

        return jsonify({
            "reply": answer
        })

    except Exception as e:

        print("ERROR:", e)

        return jsonify({
            "reply": f"Error AI: {str(e)}\n\n🤖 Created by Sulaiman"
        })

if __name__ == "__main__":

    port = int(os.getenv("PORT", 8080))

    print("✅ KocakAi Online")
    print("👨‍💻 Created by Sulaiman")

    api.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
