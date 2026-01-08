import threading
from flask import Flask
from parser import check_loop, last_html_table

app = Flask(__name__)

def start_parser():
    t = threading.Thread(target=check_loop, daemon=True)
    t.start()

start_parser()

@app.route("/")
def index():
    return f"""
    <html>
    <head>
        <meta charset="utf-8">
        <title>Sexy Bot – Price Monitor</title>
        <script>
            async function update() {{
                const r = await fetch('/table');
                document.getElementById('table').innerHTML = await r.text();
            }}
            setInterval(update, 60000);
            window.onload = update;
        </script>
    </head>
    <body>
        <div id="table">{last_html_table}</div>
    </body>
    </html>
    """

@app.route("/table")
def table():
    return last_html_table
