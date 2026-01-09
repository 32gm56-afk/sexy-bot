from config import PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS


def get_proxies():
    if not PROXY_HOST or not PROXY_PORT:
        raise RuntimeError("❌ Proxy ENV variables not set")

    if PROXY_USER and PROXY_PASS:
        proxy = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"
    else:
        proxy = f"http://{PROXY_HOST}:{PROXY_PORT}"

    return {
        "http": proxy,
        "https": proxy
    }
