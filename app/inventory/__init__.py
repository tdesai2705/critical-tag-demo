def is_in_stock(quantity):
    return quantity > 0


def reserve_stock(quantity, requested):
    if requested > quantity:
        raise ValueError("Cannot reserve more than available stock")
    return quantity - requested


def low_stock_warning(quantity, threshold=5):
    return 0 < quantity <= threshold
