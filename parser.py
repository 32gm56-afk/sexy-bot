import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime

from config import URL, CHECK_INTERVAL
from telegram import send_telegram
from utils import round_price, format_msg

last_html_table = "<h2>Очікування першої перевірки...</h2>"
state = {}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def build_table(items):
    if not items:
        return "<h2>Немає даних</h2>"

    html = """
    <table border="1" cellpadding="6">
    <tr><th>Назва</th><th>Ціна</th><th>Кількість</th></tr>
    """
    for i in items:
        html += f"<tr><td>{i['name']}</td><td>{i['price']}</td><td>{i['qty']}</td></tr>"
    html += "</table>"
    return html


def parse_page():
    r = requests.get(URL, headers=HEADERS, timeout=20)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")
    result = []

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

            if qty < 1:
                continue

            result.append({
                "name": name,
                "price": price,
                "qty": qty
            })

    return result


def main_loop():
    global last_html_table

    send_telegram("🟢 <b>Бот запущено</b>\nПочинаю перевірку")

    while True:
        print(f"[{datetime.now()}] Перевірка оновлень...")

        try:
            items = parse_page()
            print(f"✅ Парсинг успішний, знайдено {len(items)} предметів")

            last_html_table = build_table(items)

        except Exception as e:
            print("❌ Помилка парсингу:", e)

        time.sleep(CHECK_INTERVAL)
