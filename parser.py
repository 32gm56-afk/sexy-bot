import requests
import time
import json
import os
from bs4 import BeautifulSoup
from datetime import datetime

from config import *
from telegram import send_telegram

# для веб-таблиці
last_html_table = "<h2>Немає даних...</h2>"


# ---------------- HELPERS ----------------

def round_price(p):
    if p < 0.009:
        return None
    v = int(round(p * 1000))
    base = (v // 10) * 10
    if v % 10 >= 9:
        base += 10
    return base / 1000.0


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


# ---------------- PARSER ----------------

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


# ---------------- MAIN LOOP ----------------

def main_loop():
    global last_html_table

    prev_data = load_json(DATA_FILE)
    state = load_json(STATE_FILE)

    # 🔥 ПЕРША ПЕРЕВІРКА — ОДРАЗУ ПРИ СТАРТІ
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Перевірка оновлень (start)...")

    try:
        current = parse_page()
    except Exception as e:
        print(f"[ERROR] Parse error: {e}")
        current = {}

    # ініціалізація baseline
    for name, item in current.items():
        rounded = round_price(item["price_real"])
        if rounded is not None:
            state.setdefault(name, {"baseline": rounded})

    save_json(DATA_FILE, current)
    save_json(STATE_FILE, state)
    prev_data = current

    # 🔁 ОСНОВНИЙ ЦИКЛ
    while True:
        time.sleep(CHECK_INTERVAL)

        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Перевірка оновлень...")

        try:
            current = parse_page()
        except Exception as e:
            print(f"[ERROR] Parse error: {e}")
            continue

        # ---------- TELEGRAM ----------
        for name, item in current.items():
            price_real = item["price_real"]
            qty = item["qty"]

            rounded = round_price(price_real)
            if rounded is None:
                continue

            baseline = state.get(name, {}).get("baseline")
            if baseline is None:
                state[name] = {"baseline": rounded}
                continue

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
                state[name]["baseline"] = rounded

        # ---------- WEB TABLE ----------
        rows = []
        for name, item in current.items():
            price = item["price_real"]
            qty = item["qty"]
            old = prev_data.get(name, {}).get("price_real")
            diff = f"{((price - old) / old * 100):.2f}" if old else ""
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

        save_json(DATA_FILE, current)
        save_json(STATE_FILE, state)
        prev_data = current
