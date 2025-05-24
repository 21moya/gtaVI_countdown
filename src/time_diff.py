from datetime import datetime

def calculate_time_diff():
    gta_reales = datetime(2026, 5, 26)
    now = datetime.now()

    diff = gta_reales - now
    days = diff.days
    hours = diff.seconds // 3600
    minutes = (diff.seconds % 3600) // 60

    str_diff = f"{days}d, {hours}h, {minutes}m"
    return str_diff