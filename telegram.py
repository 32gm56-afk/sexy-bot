import requests
from config import BOT_TOKEN, CHAT_ID

def send_telegram(text: str):
    if not BOT_TOKEN or not CHAT_ID:
        return

    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={
                "chat_id": CHAT_ID,
                "text": text,
                "parse_mode": "HTML"
            },
            timeout=5
        )
    except Exception as e:
        print("Telegram error:", e)
