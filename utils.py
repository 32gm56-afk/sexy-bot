import os


def round_price(p):
    if p < 0.009:
        return None

    p1000 = int(round(p * 1000))
    last = p1000 % 10
    base = (p1000 // 10) * 10

    if last >= 9:
        base += 10

    return base / 1000.0


def format_msg(name, old_price, new_price, qty, change_type):
    return (
        f"<code>{name}</code>\n"
        f"{change_type} ціни: {old_price} → {new_price}\n"
        f"Кількість: {qty}"
    )


def get_proxies():
    """
    Підтягує proxy з ENV (Render → Environment Variables)
    Якщо proxy не заданий — повертає None
    """

    host = os.getenv("PROXY_HOST")
    port = os.getenv("PROXY_PORT")
    user = os.getenv("PROXY_USER")
    pwd = os.getenv("PROXY_PASS")

    if not host or not port:
        return None

    if user and pwd:
        proxy = f"http://{user}:{pwd}@{host}:{port}"
    else:
        proxy = f"http://{host}:{port}"

    return {
        "http": proxy,
        "https": proxy
    }
