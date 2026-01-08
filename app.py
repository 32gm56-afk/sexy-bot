import threading
from flask import Flask
from parser import check_loop

app = Flask(__name__)

def start_parser():
    t = threading.Thread(target=check_loop, daemon=True)
    t.start()

start_parser()

@app.route("/")
def index():
    return "✅ Sexy-bot running (price notifier only)"
