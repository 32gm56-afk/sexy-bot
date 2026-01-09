import os

URL = "https://price.csgetto.love/"
CHECK_INTERVAL = 50  # секунд

# Telegram
BOT_TOKEN = os.getenv("8134393467:AAHRcOjVFiy8RTDWSXt3y3u_SDQwYIssK68")
CHAT_ID = os.getenv("-4840038262")

# Proxy (ПІДТЯГУЮТЬСЯ АВТОМАТИЧНО з Render ENV)
PROXY_HOST = os.getenv("PROXY_HOST")
PROXY_PORT = os.getenv("PROXY_PORT")
PROXY_USER = os.getenv("PROXY_USER")
PROXY_PASS = os.getenv("PROXY_PASS")
