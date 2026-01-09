def round_price(p):
    if p < 0.009:
        return None

    p1000 = int(round(p * 1000))
    last = p1000 % 10
    base = (p1000 // 10) * 10

    if last >= 9:
        base += 10

    return base / 1000


def format_msg(name, old_p, new_p, qty, typ):
    return (
        f"<code>{name}</code>\n"
        f"{typ}: {old_p} → {new_p}\n"
        f"Кількість: {qty}"
    )
