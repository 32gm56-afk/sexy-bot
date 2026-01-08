from parser import main_loop
import threading
from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "Sexy-bot is running"

# ⬇️ старт парсера
threading.Thread(target=main_loop, daemon=True).start()
