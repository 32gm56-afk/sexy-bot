def round_price(p):
    if p < 0.009:
        return None
    v = int(p * 1000)
    base = (v // 10) * 10
    if v % 10 >= 9:
        base += 10
    return base / 1000.0


def format_msg(name, old_p, new_p, qty, kind):
    return (
        f"<code>{name}</code>\n"
        f"{kind} ціни: {old_p} → {new_p}\n"
        f"Кількість: {qty}"
    )
