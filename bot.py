import os
import sqlite3
import time
import threading
from flask import Flask, request, jsonify

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from google import genai

# ==========================
# CONFIG
# ==========================

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

# ==========================
# DATABASE
# ==========================

db = sqlite3.connect("husnanai.db", check_same_thread=False)
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY,
    username TEXT,
    total_messages INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS memory(
    user_id INTEGER,
    role TEXT,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS media(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    media_type TEXT,
    file_id TEXT,
    caption TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

db.commit()

# ==========================
# SYSTEM PROMPT
# ==========================

SYSTEM = """
Kamu adalah HusnanAi V5.

Owner:
X: @husnan97
Telegram: @Qomaroen
Instagram: @husnan.eth

Karakter:
- Ramah
- Santai
- Lucu
- Ahli Crypto
- Ahli Telegram Bot
- Ahli Python

Jawab menggunakan bahasa Indonesia.
"""

# ==========================
# MEMORY
# ==========================

def save_memory(user_id, role, content):
    cursor.execute(
        "INSERT INTO memory(user_id, role, content) VALUES (?, ?, ?)",
        (user_id, role, content)
    )
    db.commit()

def get_memory(user_id, limit=10):
    cursor.execute("""
        SELECT role, content
        FROM memory
        WHERE user_id=?
        ORDER BY rowid DESC
        LIMIT ?
    """, (user_id, limit))

    rows = cursor.fetchall()

    history = ""

    for role, content in reversed(rows):
        history += f"{role}: {content}\n"

    return history

def save_media(user_id, media_type, file_id, caption=""):
    cursor.execute("""
        INSERT INTO media(user_id, media_type, file_id, caption)
        VALUES (?, ?, ?, ?)
    """, (user_id, media_type, file_id, caption))
    db.commit()

# ==========================
# COMMANDS
# ==========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    cursor.execute("""
    INSERT OR REPLACE INTO users(id, username)
    VALUES(?, ?)
    """, (user.id, user.username))

    db.commit()

    await update.message.reply_text(
        f"👋 Halo {user.first_name}\n\n"
        "Saya HusnanAi V5.\n"
        "Ketik apa saja untuk mulai ngobrol."
    )

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 HusnanAi V5\n\nPowered by Google Gemini"
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(total_messages) FROM users")
    total_messages = cursor.fetchone()[0] or 0

    await update.message.reply_text(
        f"📊 Statistik\n\n👥 Users: {total_users}\n💬 Messages: {total_messages}"
    )

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):

    uid = update.effective_user.id

    cursor.execute(
        "DELETE FROM memory WHERE user_id=?",
        (uid,)
    )

    db.commit()

    await update.message.reply_text(
        "🧠 Memori berhasil dihapus."
    )

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        """
🤖 HusnanAi V5

/start
/about
/stats
/reset
/menu

Kirim:
📷 Foto
🎥 Video
🎤 Voice
📁 File
📍 Lokasi

💬 Chat AI Gemini
🧠 Memory SQLite
"""
    )

# ==========================
# MEDIA
# ==========================

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    photo = update.message.photo[-1]

    save_media(
        update.effective_user.id,
        "photo",
        photo.file_id,
        update.message.caption or ""
    )

    await update.message.reply_text(
        "📷 Foto berhasil disimpan."
    )

async def video_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    video = update.message.video

    save_media(
        update.effective_user.id,
        "video",
        video.file_id,
        update.message.caption or ""
    )

    await update.message.reply_text(
        "🎥 Video berhasil disimpan."
    )

async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    voice = update.message.voice

    save_media(
        update.effective_user.id,
        "voice",
        voice.file_id,
        ""
    )

    await update.message.reply_text(
        "🎤 Voice berhasil disimpan."
    )

async def document_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    doc = update.message.document

    save_media(
        update.effective_user.id,
        "document",
        doc.file_id,
        doc.file_name
    )

    await update.message.reply_text(
        f"📁 File diterima: {doc.file_name}"
    )

async def location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    lat = update.message.location.latitude
    lon = update.message.location.longitude

    save_memory(
        update.effective_user.id,
        "location",
        f"{lat},{lon}"
    )

    await update.message.reply_text(
        f"📍 Lokasi diterima\nhttps://maps.google.com/?q={lat},{lon}"
    )

# ==========================
# CHAT AI
# ==========================

user_cooldown = {}

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):

    uid = update.effective_user.id
    text = update.message.text

    now = time.time()

    if uid in user_cooldown:
        if now - user_cooldown[uid] < 1:
            return

    user_cooldown[uid] = now

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.TYPING
    )

    save_memory(uid, "user", text)

    history = get_memory(uid)

    prompt = f"""
{SYSTEM}

Riwayat:
{history}

User: {text}
"""

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        answer = response.text

        save_memory(uid, "assistant", answer)

        cursor.execute("""
        UPDATE users
        SET total_messages = total_messages + 1
        WHERE id=?
        """, (uid,))
        db.commit()

        if len(answer) > 4096:
            for i in range(0, len(answer), 4000):
                await update.message.reply_text(answer[i:i+4000])
        else:
            await update.message.reply_text(answer)

    except Exception as e:
        await update.message.reply_text(
            f"❌ Error: {str(e)}"
        )

# ==========================
# ERROR
# ==========================

async def error_handler(update, context):
    print("ERROR:", context.error)

# ==========================
# APP
# ==========================

# ==========================
# WHATSAPP API
# ==========================

api = Flask(__name__)

@api.route("/chat", methods=["POST"])
def wa_chat():
    data = request.json or {}

    uid = str(data.get("user_id"))
    text = data.get("message", "")

    save_memory(uid, "user", text)
    history = get_memory(uid)

    prompt = f"""
{SYSTEM}

Riwayat:
{history}

User: {text}
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        answer = response.text

    except Exception as e:
        answer = f"Error AI: {str(e)}"

    save_memory(uid, "assistant", answer)

    return jsonify({
        "reply": answer
    })


def run_api():
    api.run(
        host="0.0.0.0",
        port=5000,
        threaded=True
    )


threading.Thread(
    target=run_api,
    daemon=True
).start()

print("✅ HusnanAi V5 Online")


# ==========================
# TELEGRAM OPTIONAL
# ==========================

if BOT_TOKEN:

    tg_app = Application.builder() \
        .token(BOT_TOKEN) \
        .build()

    tg_app.add_handler(CommandHandler("start", start))
    tg_app.add_handler(CommandHandler("about", about))
    tg_app.add_handler(CommandHandler("stats", stats))
    tg_app.add_handler(CommandHandler("reset", reset))
    tg_app.add_handler(CommandHandler("menu", menu))

    tg_app.add_handler(
        MessageHandler(
            filters.PHOTO,
            photo_handler
        )
    )

    tg_app.add_handler(
        MessageHandler(
            filters.VIDEO,
            video_handler
        )
    )

    tg_app.add_handler(
        MessageHandler(
            filters.VOICE,
            voice_handler
        )
    )

    tg_app.add_handler(
        MessageHandler(
            filters.Document.ALL,
            document_handler
        )
    )

    tg_app.add_handler(
        MessageHandler(
            filters.LOCATION,
            location_handler
        )
    )

    tg_app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            chat
        )
    )

    tg_app.run_polling()

else:

    print("⚠️ BOT_TOKEN tidak diisi")
    print("⚠️ Telegram dinonaktifkan")

    while True:
        time.sleep(60)
