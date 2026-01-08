from flask import Flask
import threading

from parser import main_loop

app = Flask(__name__)


def start_background():
    t = threading.Thread(target=main_loop, daemon=True)
    t.start()


# стартуємо парсер одразу при запуску сервісу
start_background()


@app.route("/")
def index():
    return "Sexy-bot is running"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
