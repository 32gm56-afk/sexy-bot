import threading
import time
import requests
from flask import Flask, request
from bs4 import BeautifulSoup
from datetime import datetime

from config import URL, CHECK_INTERVAL
from telegram import send_telegram
from utils import round_price, format_msg

app = Flask(__name__)

# ---------------- PARSER STATE ----------------

state = {}

def log(msg: str):
    with open("changes.log", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {msg}\n")

# ---------------- PARSER LOGIC ----------------

def parse_page():
    r = requests.get(URL, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")
    items = {}

    for table in soup.find_all("table"):
        for row in table.find_all("tr")[1:]:
            cols = row.find_all("td")
            if len(cols) < 5:
                continue

            name = cols[0].text.strip()

            try:
                price = float(cols[1].text.strip())
            except ValueError:
                continue

            try:
                total = int(cols[3].text.strip())
                left = int(cols[4].text.strip())
            except ValueError:
                continue

            qty = total - left
            if qty < 1:
                continue

            if price < 0.010:
                continue

            items[name] = {
                "price": price,
                "qty": qty
            }

    return items


def parser_loop():
    while True:
        try:
            current = parse_page()

            for name, item in current.items():
                rounded_price = round_price(item["price"])
                if rounded_price is None:
                    continue

                if name not in state:
                    state[name] = rounded_price
                    continue

                base_price = state[name]
                diff_percent = ((rounded_price - base_price) / base_price) * 100
                diff_abs = rounded_price - base_price

                if abs(diff_percent) >= 30 and abs(diff_abs) >= 0.008:
                    kind = "Підвищення" if diff_percent > 0 else "Падіння"
                    send_telegram(
                        format_msg(
                            name,
                            base_price,
                            rounded_price,
                            item["qty"],
                            kind
                        )
                    )
                    log(f"{name}: {base_price} → {rounded_price} ({diff_percent:.2f}%)")
                    state[name] = rounded_price

        except Exception as e:
            log(f"ERROR: {e}")

        time.sleep(CHECK_INTERVAL)

# ---------------- START BACKGROUND THREAD ----------------

def start_parser():
    t = threading.Thread(target=parser_loop, daemon=True)
    t.start()

start_parser()

# ---------------- FLASK ROUTES ----------------

@app.route("/")
def index():
    return "✅ Sexy-bot працює (parser + webhook, Render Free)"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json or {}
    message = data.get("message", {})
    text = message.get("text", "")

    if text == "/start":
        send_telegram("✅ Бот працює 24/7 (Render Free)")
    elif text == "/status":
        send_telegram("📊 Парсер активний")

    return "ok"
