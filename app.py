from flask import Flask
import threading
from parser import main_loop, last_html_table

app = Flask(__name__)


@app.route("/")
def index():
    return f"""
    <html>
    <head><meta charset="utf-8"></head>
    <body>
        <h2>Sexy-bot is running</h2>
        {last_html_table}
    </body>
    </html>
    """


if __name__ == "__main__":
    t = threading.Thread(target=main_loop)
    t.daemon = True
    t.start()

    app.run(host="0.0.0.0", port=10000)
