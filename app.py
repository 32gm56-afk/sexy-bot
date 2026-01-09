import os
import time
import json
import threading
import requests
from datetime import datetime
from flask import Flask
from bs4 import BeautifulSoup

# ================== CONFIG ==================
URL = "https://price.csgetto.love/"
CHECK_INTERVAL = 50

DATA_FILE = "data.json"
STATE_FILE = "state.json"

BOT_TOKEN = os.getenv("8134393467:AAHRcOjVFiy8RTDWSXt3y3u_SDQwYIssK68")
CHAT_ID = os.getenv("-4840038262")

# ---------- PROXY ----------
PROXY_HOST = os.getenv("PROXY_HOST")
PROXY_PORT = os.getenv("PROXY_PORT")
PROXY_USER = os.getenv("PROXY_USER")
PROXY_PASS = os.getenv("PROXY_PASS")

def get_proxies():
    if not all([PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS]):
        print("⚠️ Proxy not configured")
        return None

    proxy = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"
    print("🌍 Proxy enabled")
    return {
        "http": proxy,
        "https": proxy
    }

PROXIES = get_proxies()

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://google.com"
}

# ================== TELEGRAM ==================
def send_telegram(text):
    if not BOT_TOKEN or not CHAT_ID:
        print("⚠️ Telegram not configured")
        return

    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"},
            timeout=10
        )
    except Exception as e:
        print("❌ Telegram error:", e)

# ================== HELPERS ==================
def log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)

def round_price(p):
    if p < 0.009:
        return None
    x = int(round(p * 1000))
    base = (x // 10) * 10
    if x % 10 >= 9:
        base += 10
    return base / 1000

# ================== PARSER ==================
def parse_page():
    r = requests.get(
        URL,
        headers=HEADERS,
        proxies=PROXIES,
        timeout=25
    )
    r.raise_for_status()

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
            except:
                continue

            total = int(cols[3].text)
            left = int(cols[4].text)
            qty = total - left

            if qty < 1 or price < 0.01:
                continue

            items[name] = {"price": price, "qty": qty}

    return items

# ================== MAIN LOOP ==================
last_html = "<h2>Немає даних</h2>"

def main_loop():
    global last_html

    send_telegram("🤖 Бот запущено та почав перевірку цін")

    state = {}
    if os.path.exists(STATE_FILE):
        state = json.load(open(STATE_FILE, "r", encoding="utf-8"))

    while True:
        log("🔍 Перевірка оновлень (start)...")
        try:
            items = parse_page()
            log(f"✅ Перевірка пройшла успішно | items: {len(items)}")

        except Exception as e:
            log(f"❌ Помилка парсингу: {e}")
            time.sleep(CHECK_INTERVAL)
            continue

        changes = []

        for name, item in items.items():
            rp = round_price(item["price"])
            if rp is None:
                continue

            if name not in state:
                state[name] = rp
                continue

            diff = ((rp - state[name]) / state[name]) * 100
            if abs(diff) >= 30 and abs(rp - state[name]) >= 0.008:
                msg = (
                    f"<b>{name}</b>\n"
                    f"Ціна: {state[name]} → {rp}\n"
                    f"Кількість: {item['qty']}\n"
                    f"Зміна: {diff:.2f}%"
                )
                send_telegram(msg)
                state[name] = rp

            changes.append(
                f"<tr><td>{name}</td><td>{item['price']}</td>"
                f"<td>{item['qty']}</td><td>{diff:.2f}%</td></tr>"
            )

        last_html = (
            "<table border=1 cellpadding=6>"
            "<tr><th>Назва</th><th>Ціна</th><th>Кількість</th><th>Δ%</th></tr>"
            + "".join(changes)
            + "</table>"
        )

        json.dump(items, open(DATA_FILE, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
        json.dump(state, open(STATE_FILE, "w", encoding="utf-8"), indent=2, ensure_ascii=False)

        time.sleep(CHECK_INTERVAL)

# ================== WEB ==================
app = Flask(__name__)

@app.route("/")
def index():
    return f"<html><body><h1>Sexy-bot is running</h1>{last_html}</body></html>"

# ================== START ==================
if __name__ == "__main__":
    threading.Thread(target=main_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)

