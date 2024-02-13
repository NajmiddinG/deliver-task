from math import sin, cos, radians, degrees, acos, ceil
from .models import Order


def get_distance(lat_a, long_a, lat_b, long_b):
    """
    Calculate distance between two location.
    """
    lat_a, long_a, lat_b, long_b = radians(lat_a), radians(long_a), radians(lat_b), radians(long_b)

    long_diff = long_a - long_b
    distance = (sin(lat_a) * sin(lat_b) +
                cos(lat_a) * cos(lat_b) * cos(long_diff))
    distance_in_km = abs(int(degrees(acos(distance)) * 111.133))
    return distance_in_km


def estimate_time(distance, order_count):
    """
    Calculate estimate_date.
    """
    total_count = order_count
    for order in Order.objects.filter(delivered=False, food_on_the_way=False):
        total_count += order.count
    ready_time = ceil(total_count/4)*5
    driver_time = distance*3
    return ready_time + driver_time


def change_estimates(order):
    """
    Update newer estimate_date's after deleting Order item
    """
    minutes = max(0, ceil(order.count/4)*5)
    created_date = order.date
    orders = Order.objects.filter(delivered=False, food_on_the_way=False, date__gte=created_date)
    for order in orders:
        order.estimate_date = max(1, order.estimate_date - minutes)
        order.save()
