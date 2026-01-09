import time
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

from config import URL, CHECK_INTERVAL
from telegram import send_telegram
from utils import round_price, format_msg

DATA_FILE = "data.json"
STATE_FILE = "state.json"

last_html_table = "<p>Очікування першої перевірки...</p>"
first_run = True


def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def parse_page():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "en-US,en;q=0.9"
    }

    r = requests.get(URL, headers=headers, timeout=20)
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
                total = int(cols[3].text)
                left = int(cols[4].text)
            except:
                continue

            qty = total - left
            if qty < 1 or price < 0.01:
                continue

            items[name] = {
                "price": price,
                "qty": qty
            }

    return items


def build_table(items):
    if not items:
        return "<p>Даних не знайдено</p>"

    html = """
    <table border="1" cellpadding="6">
    <tr>
        <th>Назва</th>
        <th>Ціна</th>
        <th>Кількість</th>
    </tr>
    """

    for name, d in items.items():
        html += f"""
        <tr>
            <td>{name}</td>
            <td>{d['price']}</td>
            <td>{d['qty']}</td>
        </tr>
        """

    html += "</table>"
    return html


def main_loop():
    global last_html_table, first_run

    print("🚀 Парсер запущений")
    send_telegram("🚀 Бот запущено. Починаю першу перевірку...")

    state = load_json(STATE_FILE)
    prev = load_json(DATA_FILE)

    while True:
        print(f"[{datetime.now()}] 🔍 Перевірка оновлень...")

        try:
            current = parse_page()
            last_html_table = build_table(current)

            save_json(DATA_FILE, current)
            save_json(STATE_FILE, state)

            if first_run:
                send_telegram("✅ Перша перевірка успішна, дані отримано")
                first_run = False

            print("✅ Перевірка успішна")

        except Exception as e:
            print("❌ Помилка парсингу:", e)

        time.sleep(CHECK_INTERVAL)
