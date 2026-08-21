def apply_discount(price, percent_off):
    if percent_off < 0 or percent_off > 100:
        raise ValueError("percent_off must be between 0 and 100")
    if price < 0:
        raise ValueError("price must be non-negative")
    return round(price * (1 - percent_off / 100), 2)


def calculate_tax(price, tax_rate=0.08):
    return round(price * tax_rate, 2)


def total_with_tax(price, tax_rate=0.08):
    return round(price + calculate_tax(price, tax_rate), 2)
