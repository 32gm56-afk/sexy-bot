import requests
import time
import json
import os
from bs4 import BeautifulSoup
from datetime import datetime

from config import *
from telegram import send_telegram

last_html_table = "<h2>Немає даних...</h2>"

# ---------------- LOG ----------------

def log_change(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {msg}\n")

# ---------------- ROUND PRICE ----------------

def round_price(p):
    if p < 0.009:
        return None
    p1000 = int(round(p * 1000))
    base = (p1000 // 10) * 10
    if p1000 % 10 >= 9:
        base += 10
    return base / 1000.0

# ---------------- PARSE PAGE ----------------

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
            except:
                continue

            total = int(cols[3].text.strip())
            left = int(cols[4].text.strip())
            qty = total - left

            if qty < 1 or price < 0.010:
                continue

            items[name] = {
                "price_real": price,
                "qty": qty
            }

    return items

# ---------------- STATE ----------------

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

# ---------------- MAIN LOOP ----------------

def check_loop():
    global last_html_table

    prev_data = {}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            prev_data = json.load(f)

    state = load_state()

    while True:
        try:
            current = parse_page()
        except Exception as e:
            log_change(f"Parse error: {e}")
            time.sleep(CHECK_INTERVAL)
            continue

        # ---- TELEGRAM LOGIC ----
        for name, item in current.items():
            price_real = item["price_real"]
            qty = item["qty"]

            rounded = round_price(price_real)
            if rounded is None:
                continue

            if name not in state:
                state[name] = {"baseline": rounded}
                continue

            baseline = state[name]["baseline"]
            change_percent = ((rounded - baseline) / baseline) * 100
            diff_abs = rounded - baseline

            if abs(change_percent) >= 30 and abs(diff_abs) >= 0.008:
                kind = "Підвищення" if change_percent > 0 else "Падіння"
                msg = (
                    f"<code>{name}</code>\n"
                    f"{kind} ціни: {baseline} → {rounded}\n"
                    f"Кількість: {qty}"
                )
                send_telegram(msg)
                log_change(f"{name}: {baseline} → {rounded} ({change_percent:.2f}%)")
                state[name]["baseline"] = rounded

        # ---- BUILD WEB TABLE ----
        rows = []
        for name, item in current.items():
            price = item["price_real"]
            qty = item["qty"]
            old = prev_data.get(name, {}).get("price_real")
            diff = ""
            if old:
                diff = f"{((price - old) / old * 100):.2f}"
            rows.append((name, price, qty, diff))

        rows.sort(key=lambda x: abs(float(x[3])) if x[3] else 0, reverse=True)

        html = """
        <h2>Зміни цін</h2>
        <table border="1" cellspacing="0" cellpadding="6">
            <tr>
                <th>Назва</th>
                <th>Ціна</th>
                <th>Кількість</th>
                <th>Зміна (%)</th>
            </tr>
        """
        for r in rows:
            html += f"""
            <tr>
                <td>{r[0]}</td>
                <td>{r[1]}</td>
                <td>{r[2]}</td>
                <td>{r[3]}</td>
            </tr>
            """
        html += "</table>"

        last_html_table = html

        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(current, f, indent=2, ensure_ascii=False)

        save_state(state)
        prev_data = current

        time.sleep(CHECK_INTERVAL)
