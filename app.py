from flask import Flask
import threading
import parser

app = Flask(__name__)


@app.route("/")
def index():
    return f"""
    <html>
    <head><meta charset="utf-8"></head>
    <body>
        <h2>Sexy-bot is running</h2>
        {parser.last_table_html}
    </body>
    </html>
    """


def start_parser():
    t = threading.Thread(target=parser.main_loop)
    t.daemon = True
    t.start()


# 🔥 СТАРТ ОДРАЗУ ПРИ ЗАПУСКУ
start_parser()
