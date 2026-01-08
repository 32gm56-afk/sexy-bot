import requests
import json
import time
import os
from bs4 import BeautifulSoup
from datetime import datetime
from time import perf_counter

from config import URL, CHECK_INTERVAL
from telegram import send_telegram
from utils import round_price, format_msg

DATA_FILE = "data.json"
STATE_FILE = "state.json"

# ---------------------------
# logging (Render Logs)
# ---------------------------
def log(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)

# ---------------------------
# json helpers
# ---------------------------
def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default
    return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ---------------------------
# parsing
# ---------------------------
def parse_page():
    r = requests.get(
        URL,
        timeout=20,
        headers={"User-Agent": "Mozilla/5.0"}
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
                total = int(cols[3].text.strip())
                left = int(cols[4].text.strip())
            except Exception:
                continue

            qty = total - left
            if qty < 1:
                continue
            if price < 0.010:
                continue

            items[name] = {
                "price_real": price,
                "qty": qty
            }

    return items

# ---------------------------
# main loop
# ---------------------------
def parser_loop(shared_state: dict):
    log("🚀 Парсер запущено")

    prev_data = load_json(DATA_FILE, {})
    state = load_json(STATE_FILE, {})

    while True:
        start_time = perf_counter()
        log("🔍 Початок перевірки...")

        try:
            current = parse_page()
            duration = perf_counter() - start_time

            log(
                f"✅ Перевірка успішна | items: {len(current)} | "
                f"time: {duration:.2f}s"
            )

        except Exception as e:
            log(f"❌ Помилка перевірки: {e}")
            time.sleep(CHECK_INTERVAL)
            continue

        # --- price logic ---
        for name, item in current.items():
            price_real = item["price_real"]
            qty = item["qty"]

            price_rounded = round_price(price_real)
            if price_rounded is None:
                continue

            if name not in state:
                state[name] = {"baseline": price_rounded}
                continue

            baseline = state[name]["baseline"]
            diff = price_rounded - baseline
            diff_percent = (diff / baseline) * 100 if baseline > 0 else 0

            if abs(diff_percent) >= 30 and abs(diff) >= 0.008:
                msg_type = "📈 Підвищення" if diff > 0 else "📉 Падіння"

                msg = format_msg(
                    name=name,
                    old_price=baseline,
                    new_price=price_rounded,
                    qty=qty,
                    msg_type=msg_type
                )

                send_telegram(msg)
                log(f"{msg_type}: {name} {baseline} → {price_rounded}")

                state[name]["baseline"] = price_rounded

        save_json(DATA_FILE, current)
        save_json(STATE_FILE, state)

        shared_state["last_data"] = current
        shared_state["last_check"] = datetime.now().strftime("%H:%M:%S")

        time.sleep(CHECK_INTERVAL)
