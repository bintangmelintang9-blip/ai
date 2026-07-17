import os
import random
from flask import Flask, request, jsonify
from google import genai

api = Flask(__name__)

# =========================
# GEMINI
# =========================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise Exception("GEMINI_API_KEY belum diisi!")

client = genai.Client(
    api_key=GEMINI_API_KEY
)

# =========================
# DATA OWNER
# =========================

OWNER_NAME = "Muhammad Sulaiman"
WEBSITE = "https://sites.google.com/view/husnanweb"
INSTAGRAM = "https://www.instagram.com/husnan.eth"

# =========================
# JOKES GILA
# =========================

JOKES = [
    "🤣 Tadi saya ngobrol sama kulkas. Orangnya dingin banget.",
    "😂 Saya mau jadi awan, biar kalau hilang dibilang cuacanya mendung.",
    "😆 Ayam saya belajar matematika, sekarang dia bisa menghitung telurnya sendiri.",
    "🤣 Tadi saya balapan sama bayangan sendiri. Seri, karena dia selalu mengikuti saya.",
    "😂 Saya buka dompet, dompetnya malah minta bantuan finansial.",
    "😆 Kalau semut bisa sekolah, mungkin sekarang sudah jadi semutjana.",
    "🤣 Tadi saya tanya jam berapa ke jam dinding. Dia diam, mungkin sedang malu.",
]

# =========================
# SYSTEM PROMPT
# =========================

SYSTEM_PROMPT = f"""
Kamu adalah KocakAi.

Informasi penting:
- Owner: {OWNER_NAME}
- Website: {WEBSITE}
- Instagram: {INSTAGRAM}

Karakter:
- Selalu menggunakan bahasa Indonesia.
- Ramah, santai, dan membantu.
- Jawaban singkat dan jelas.
- Jangan terlalu panjang kecuali diminta.
- Sesekali berikan lelucon gila atau absurd yang lucu.
- Jangan memberi lelucon di setiap jawaban.
- Jika ditanya siapa owner atau pembuatmu, jawab {OWNER_NAME}.
- Jika ditanya website atau media sosial, berikan informasi resmi.
- Jangan mengaku sebagai Gemini atau Google AI.
"""

# =========================
# HOME
# =========================

@api.route("/")
def home():
    return {
        "status": "online",
        "bot": "KocakAi",
        "owner": OWNER_NAME
    }

# =========================
# CHAT
# =========================

@api.route("/chat", methods=["POST"])
def chat():

    try:

        data = request.get_json()

        user_message = data.get("message", "").strip()

        if not user_message:
            return jsonify({
                "reply": "Pesan kosong.\n\n🤖 Created by Sulaiman"
            })

        prompt = f"""
{SYSTEM_PROMPT}

Pesan pengguna:
{user_message}
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        answer = response.text.strip()

        # 20% peluang menambahkan lelucon
        if random.randint(1, 100) <= 20:
            answer += "\n\n" + random.choice(JOKES)

        msg = user_message.lower()

        owner_keywords = [
            "owner",
            "pemilik",
            "creator",
            "developer",
            "siapa pembuatmu",
            "siapa yang membuatmu"
        ]

        website_keywords = [
            "website",
            "web",
            "situs"
        ]

        instagram_keywords = [
            "instagram",
            "ig",
            "sosial media"
        ]

        if any(x in msg for x in owner_keywords):
            answer += f"""

👨‍💻 Owner:
{OWNER_NAME}
"""

        if any(x in msg for x in website_keywords):
            answer += f"""

🌐 Website:
{WEBSITE}
"""

        if any(x in msg for x in instagram_keywords):
            answer += f"""

📸 Instagram:
{INSTAGRAM}
"""

        answer += "\n\n🤖 Created by Sulaiman"

        return jsonify({
            "reply": answer
        })

    except Exception as e:

        print("ERROR:", e)

        return jsonify({
            "reply":
            f"Terjadi kesalahan AI: {str(e)}\n\n🤖 Created by Sulaiman"
        })

# =========================
# START
# =========================

if __name__ == "__main__":

    port = int(os.getenv("PORT", 8080))

    print("✅ KocakAi Online")
    print(f"👨‍💻 Owner: {OWNER_NAME}")

    api.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
