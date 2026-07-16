import os
from flask import Flask

api = Flask(__name__)

@api.route("/")
def home():
    return {"status": "online"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    api.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
