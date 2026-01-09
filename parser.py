import time
import json
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

from config import URL, CHECK_INTERVAL
from telegram import send_telegram
from utils import round_price, format_msg, get_proxies

DATA_FILE = "data.json"
STATE_FILE = "state.json"

last_table_html = "<h2>Очікування першої перевірки...</h2>"


def log(msg: str):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)


def load_json(path):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


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

            items[name] = {
                "price_real": price,
                "qty": qty
            }

    return items


def build_table(items):
    if not items:
        return "<h2>Дані відсутні</h2>"

    html = """
    <h2>Поточні дані</h2>
    <table border="1" cellpadding="6">
    <tr>
        <th>Назва</th>
        <th>Ціна</th>
        <th>Кількість</th>
    </tr>
    """
    for name, i in items.items():
        html += f"""
        <tr>
            <td>{name}</td>
            <td>{i['price_real']}</td>
            <td>{i['qty']}</td>
        </tr>
        """
    html += "</table>"
    return html


def main_loop():
    global last_table_html

    log("🚀 Парсер запущений")
    send_telegram("🚀 Sexy-bot запущений та почав перевірку")

    prev_data = load_json(DATA_FILE)
    state = load_json(STATE_FILE)

    while True:
        log("🔍 Перевірка оновлень (start)...")

        try:
            current = parse_page()
            log(f"✅ Перевірка пройшла успішно, знайдено {len(current)} предметів")
        except Exception as e:
            log(f"❌ Помилка парсингу: {e}")
            time.sleep(CHECK_INTERVAL)
            continue

        last_table_html = build_table(current)
        save_json(DATA_FILE, current)
        save_json(STATE_FILE, state)

        time.sleep(CHECK_INTERVAL)
