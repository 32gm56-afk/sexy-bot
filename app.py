import os
import threading
import time
import requests
from flask import Flask
from bs4 import BeautifulSoup
from datetime import datetime

# =========================
# CONFIG (ENV)
# =========================
URL = "https://price.csgetto.love/"
CHECK_INTERVAL = 50

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

PROXY_HOST = os.getenv("PROXY_HOST")
PROXY_PORT = os.getenv("PROXY_PORT")
PROXY_USER = os.getenv("PROXY_USER")
PROXY_PASS = os.getenv("PROXY_PASS")

# =========================
# GLOBAL STATE
# =========================
app = Flask(__name__)
last_html_table = "<p>Очікування першої перевірки...</p>"
first_run_done = False


# =========================
# TELEGRAM
# =========================
def send_telegram(text: str):
    if not BOT_TOKEN or not CHAT_ID:
        print("⚠️ Telegram ENV not set")
        return

    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={
                "chat_id": CHAT_ID,
                "text": text,
                "parse_mode": "HTML"
            },
            timeout=10
        )
    except Exception as e:
        print("❌ Telegram error:", e)


# =========================
# PROXY
# =========================
def get_proxies():
    if not PROXY_HOST:
        print("⚠️ Proxy disabled")
        return None

    proxy_url = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"
    print("🌍 Proxy enabled")

    return {
        "http": proxy_url,
        "https": proxy_url
    }


# =========================
# PARSER
# =========================
def parse_page():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/123.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://google.com",
        "Connection": "keep-alive"
    }

    proxies = get_proxies()

    r = requests.get(
        URL,
        headers=headers,
        proxies=proxies,
        timeout=30
    )

    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")
    items = []

    for table in soup.find_all("table"):
        for row in table.find_all("tr")[1:]:
            cols = row.find_all("td")
            if len(cols) < 5:
                continue

            try:
                name = cols[0].text.strip()
                price = float(cols[1].text.strip())
                total = int(cols[3].text.strip())
                left = int(cols[4].text.strip())
                qty = total - left
            except:
                continue

            if qty < 1 or price < 0.01:
                continue

            items.append({
                "name": name,
                "price": price,
                "qty": qty
            })

    return items


# =========================
# HTML TABLE
# =========================
def build_table(items):
    if not items:
        return "<p>Немає даних</p>"

    html = """
    <table border="1" cellpadding="6">
        <tr>
            <th>Назва</th>
            <th>Ціна</th>
            <th>Кількість</th>
        </tr>
    """

    for i in items:
        html += f"""
        <tr>
            <td>{i['name']}</td>
            <td>{i['price']}</td>
            <td>{i['qty']}</td>
        </tr>
        """

    html += "</table>"
    return html


# =========================
# MAIN LOOP
# =========================
def checker_loop():
    global last_html_table, first_run_done

    send_telegram("🚀 Бот запущено. Починаю першу перевірку...")
    print("🚀 Бот запущено")

    while True:
        try:
            print(f"[{datetime.now()}] 🔍 Перевірка оновлень (start)")
            items = parse_page()

            last_html_table = build_table(items)

            print(f"[{datetime.now()}] ✅ Перевірка успішна, items: {len(items)}")

            if not first_run_done:
                send_telegram(f"✅ Перша перевірка успішна. Знайдено {len(items)} предметів.")
                first_run_done = True

        except Exception as e:
            print(f"[{datetime.now()}] ❌ Помилка парсингу: {e}")

        time.sleep(CHECK_INTERVAL)


# =========================
# FLASK
# =========================
@app.route("/")
def index():
    return f"""
    <html>
    <head>
        <meta charset="utf-8">
        <title>Sexy-bot</title>
    </head>
    <body>
        <h2>Sexy-bot is running</h2>
        {last_html_table}
    </body>
    </html>
    """


# =========================
# START
# =========================
threading.Thread(target=checker_loop, daemon=True).start()
