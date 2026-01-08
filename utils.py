# utils.py

def round_price(price: float):
    """
    Округлення ціни для Telegram і логіки:
    - ігнорує < 0.009
    - округлення до кроку 0.01 / 0.010
    - логіка повністю як у твоєму оригінальному скрипті
    """
    if price < 0.009:
        return None

    # переводимо в "тисячні"
    price_x1000 = int(round(price * 1000))
    last_digit = price_x1000 % 10

    # база без останньої цифри
    base = (price_x1000 // 10) * 10

    # якщо ...8 або ...9 → округляємо вгору
    if last_digit >= 9:
        base += 10

    return base / 1000.0


def format_msg(
    name: str,
    old_price: float,
    new_price: float,
    qty: int,
    msg_type: str
) -> str:
    """
    Формат Telegram повідомлення
    """
    return (
        f"<code>{name}</code>\n"
        f"{msg_type} ціни: {old_price} → {new_price}\n"
        f"Кількість: {qty}"
    )
