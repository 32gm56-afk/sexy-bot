from flask import Flask, request
from telegram import send_telegram

app = Flask(__name__)

@app.route("/")
def index():
    return "✅ Sexy-bot Web OK"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json or {}
    msg = data.get("message", {})
    text = msg.get("text", "")

    if text == "/start":
        send_telegram("✅ Бот працює на Render 24/7")
    elif text == "/status":
        send_telegram("📊 Парсер активний (Render)")

    return "ok"
