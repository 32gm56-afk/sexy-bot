from flask import Flask
import threading
import time
from datetime import datetime

from parser import check_loop
from config import CHECK_INTERVAL

app = Flask(__name__)


def background_loop():
    """
    Фоновий цикл для Render.
    Лише лог + виклик основного парсера.
    """
    while True:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Перевірка оновлень...")
        time.sleep(CHECK_INTERVAL)


def start_parser():
    """
    Запускаємо основний парсер в окремому потоці.
    """
    t = threading.Thread(target=check_loop, daemon=True)
    t.start()

    # окремий логер для Render Logs
    log_thread = threading.Thread(target=background_loop, daemon=True)
    log_thread.start()


# стартуємо фонові потоки ОДИН раз
start_parser()


@app.route("/")
def index():
    return "Sexy-bot is running"


if __name__ == "__main__":
    # локальний запуск (на Render не використовується)
    app.run(host="0.0.0.0", port=10000)
