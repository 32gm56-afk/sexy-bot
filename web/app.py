import threading
import time
import requests
from flask import Flask, request
from bs4 import BeautifulSoup
from datetime import datetime

from config import (
    URL,
    CHECK_INTERVAL,
)
from telegram import send_telegram
from utils import round_price, format_msg

app = Flask(__name__)

# ----------- PARSER LOGIC -----------

state = {}

def log(msg):
    with open("changes.log", "a", encoding="utf-8") as f:
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

            if qty < 1 o
