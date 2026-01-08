import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime

from config import *
from telegram import send_telegram
from utils import round_price, format_msg


def log(msg):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {msg}\n")


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

            total = int(cols[3].text)
            left = int(cols[4].text)
            qty = total - left

            if qty < 1 or price < 0.010:
                continue

            items[name] = {"price": price, "qty": qty}

    return items


def run():
    state = {}

    while True:
        try:
            current = parse_page()

            for name, item in current.items():
                rp = round_price(item["price"])
                if rp is None:
                    continue

                if name not in state:
                    state[name] = rp
                    continue

                base = state[name]
                diff_pct = ((rp - base) / base) * 100
                diff_abs = rp - base

                if abs(diff_pct) >= 30 and abs(diff_abs) >= 0.008:
                    kind = "Підвищення" if diff_pct > 0 else "Падіння"
                    send_telegram(format_msg(name, base, rp, item["qty"], kind))
                    log(f"{name}: {base} → {rp}")
                    state[name] = rp

        except Exception as e:
            log(f"ERROR: {e}")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    run()
