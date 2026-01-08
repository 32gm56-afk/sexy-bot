# app.py

import threading
from flask import Flask
from parser import main_loop

app = Flask(__name__)

@app.route("/")
def index():
    return "Sexy-bot is running"


threading.Thread(target=main_loop, daemon=True).start()
