
def constrain(value, min_value, max_value):
    if value < min_value: return min_value
    if value > max_value: return max_value
    return value