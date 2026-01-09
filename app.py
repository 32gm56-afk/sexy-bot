from flask import Flask
import threading

from parser import main_loop, last_table_html

app = Flask(__name__)


@app.route("/")
def index():
    return f"""
    <html>
    <head>
        <meta charset="utf-8">
        <title>Sexy-bot</title>
        <script>
            async function update() {{
                const r = await fetch('/table');
                document.getElementById('data').innerHTML = await r.text();
            }}
            setInterval(update, 60000);
            window.onload = update;
        </script>
    </head>
    <body>
        <h1>Sexy-bot is running</h1>
        <div id="data">{last_table_html}</div>
    </body>
    </html>
    """


@app.route("/table")
def table():
    return last_table_html


# 🔥 ГАРАНТОВАНИЙ СТАРТ ПАРСЕРА
threading.Thread(target=main_loop, daemon=True).start()
