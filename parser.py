import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime

from config import URL, CHECK_INTERVAL
from utils import get_proxies
from telegram import send_telegram

last_table_html = "<p>Очікування першої перевірки...</p>"


def log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)


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
        timeout=40
    )

    r.raise_for_status()
    return r.text


def main_loop():
    global last_table_html

    log("🚀 Парсер ЗАПУЩЕНИЙ")
    send_telegram("🚀 Sexy-bot запущений та почав перевірку")

    while True:
        try:
            log("🔍 Перевірка оновлень...")

            html = parse_page()
            soup = BeautifulSoup(html, "html.parser")

            rows = soup.find_all("tr")[1:]
            items = []

            for row in rows:
                cols = row.find_all("td")
                if len(cols) < 5:
                    continue

                name = cols[0].text.strip()
                price = cols[1].text.strip()
                qty = cols[3].text.strip()

                items.append((name, price, qty))

            last_table_html = "<table border='1'><tr><th>Назва</th><th>Ціна</th><th>К-сть</th></tr>"
            for n, p, q in items[:100]:
                last_table_html += f"<tr><td>{n}</td><td>{p}</td><td>{q}</td></tr>"
            last_table_html += "</table>"

            log(f"✅ Перевірка успішна ({len(items)} предметів)")

        except Exception as e:
            log(f"❌ Помилка парсингу: {e}")

        time.sleep(CHECK_INTERVAL)
