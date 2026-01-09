import threading
import time
from flask import Flask
from datetime import datetime

from parser import main_loop
from telegram import send_telegram

app = Flask(__name__)

# ====== HTML ======
@app.route("/")
def index():
    return """
    <h1>Sexy-bot is running</h1>
    <p>Очікування першої перевірки...</p>
    """

# ====== BACKGROUND THREAD ======
def start_background():
    print(f"[{datetime.now()}] 🚀 Бот запущено")
    try:
        send_telegram("🚀 Бот запущено та почав перевірку цін")
    except Exception as e:
        print("Telegram error:", e)

    main_loop()

# 🚨 ВАЖЛИВО:
# запускається ОДИН раз при старті gunicorn worker
thread = threading.Thread(target=start_background, daemon=True)
thread.start()

# Render/Gunicorn імпортує app, запуск тут НЕ ПОТРІБЕН
