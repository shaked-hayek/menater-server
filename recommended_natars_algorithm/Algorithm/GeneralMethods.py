import math


def calculate_distance(point_a, point_b):

    km = haversine(lon1=point_a[0], lat1=point_a[1] , lon2=point_b[0], lat2=point_b[1])
    return km


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    # Radius of earth in kilometers is 6371
    km = 6371 * c
    return km

