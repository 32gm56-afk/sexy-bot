def round_price(p):
    if p < 0.009:
        return None
    x = int(round(p * 1000))
    last = x % 10
    base = (x // 10) * 10
    if last >= 9:
        base += 10
    return base / 1000


def format_msg(name, old_p, new_p, qty, kind):
    return (
        f"<code>{name}</code>\n"
        f"{kind}: {old_p} → {new_p}\n"
        f"Кількість: {qty}"
    )
