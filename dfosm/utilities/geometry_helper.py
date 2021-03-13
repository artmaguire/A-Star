from math import sin, cos, sqrt, atan2, radians


def get_distance(lat1, lng1, lat2, lng2):
    # approximate radius of earth in km
    R = 6373.0

    source_lat, source_lng = radians(lat1), radians(lng1)
    target_lat, target_lng = radians(lat2), radians(lng2)

    diff_lat = target_lat - source_lat
    diff_lng = target_lng - source_lng

    # Formula for getting distance between (lat, lng): d = acos( sin φ1 ⋅ sin φ2 + cos φ1 ⋅ cos φ2 ⋅ cos Δλ ) ⋅ R
    a = sin(diff_lat / 2) ** 2 + cos(source_lat) * cos(target_lat) * sin(diff_lng / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c

    return distance
