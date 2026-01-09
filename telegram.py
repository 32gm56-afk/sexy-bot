import requests
from config import BOT_TOKEN, CHAT_ID


def send_telegram(text: str):
    if not BOT_TOKEN or not CHAT_ID:
        print("⚠️ Telegram ENV not set", flush=True)
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }

    try:
        requests.post(url, json=payload, timeout=15)
    except Exception as e:
        print("❌ Telegram error:", e, flush=True)
