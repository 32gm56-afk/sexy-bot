# parser.py

import time
import json
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

from config import URL, CHECK_INTERVAL
from telegram import send_telegram
from utils import round_price, format_msg


DATA_FILE = "data.json"
STATE_FILE = "state.json"


# -------------------------------
# helpers
# -------------------------------

def log(msg: str):
    """ЛОГ У STDOUT → видно в Render Logs"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)


def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return default
    return default


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# -------------------------------
# parser
# -------------------------------

def parse_page():
    session = requests.Session()

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    # перший "прогрів" (отримати cookies)
    r1 = session.get(URL, headers=headers, timeout=20)
    r1.raise_for_status()

    # другий реальний запит
    r = session.get(URL, headers=headers, timeout=20)
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

            total = int(cols[3].text.strip())
            left = int(cols[4].text.strip())
            qty = total - left

            if qty < 1 or price < 0.01:
                continue

            items[name] = {
                "price_real": price,
                "qty": qty
            }

    return items



# -------------------------------
# MAIN LOOP
# -------------------------------

def main_loop():
    log("🚀 Парсер запущено")

    prev_data = load_json(DATA_FILE, {})
    state = load_json(STATE_FILE, {})

    while True:
        start_ts = time.time()
        log("🔍 Перевірка оновлень...")

        try:
            current = parse_page()
        except Exception as e:
            log(f"❌ Помилка парсингу: {e}")
            time.sleep(CHECK_INTERVAL)
            continue

        for name, item in current.items():
            price_real = item["price_real"]
            qty = item["qty"]

            price_round = round_price(price_real)
            if price_round is None:
                continue

            if name not in state:
                state[name] = {"baseline": price_round}
                continue

            baseline = state[name]["baseline"]
            diff_pct = ((price_round - baseline) / baseline) * 100
            abs_diff = abs(price_round - baseline)

            if abs(diff_pct) >= 30 and abs_diff >= 0.008:
                msg_type = "Підвищення" if diff_pct > 0 else "Падіння"

                send_telegram(
                    format_msg(
                        name,
                        baseline,
                        price_round,
                        qty,
                        msg_type
                    )
                )

                log(f"📨 {name} | {baseline} → {price_round} ({diff_pct:.2f}%)")
                state[name]["baseline"] = price_round

        save_json(DATA_FILE, current)
        save_json(STATE_FILE, state)

        elapsed = time.time() - start_ts
        log(f"✅ Перевірка завершена | items: {len(current)} | {elapsed:.2f}s")

        time.sleep(CHECK_INTERVAL)

