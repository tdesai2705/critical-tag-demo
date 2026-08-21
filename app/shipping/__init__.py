def estimate_delivery_days(distance_miles, express=False):
    base_days = max(1, distance_miles // 500)
    return max(1, base_days // 2) if express else base_days


def calculate_shipping_cost(weight_lbs, express=False):
    cost = round(weight_lbs * 0.75, 2)
    return round(cost * 2, 2) if express else cost
