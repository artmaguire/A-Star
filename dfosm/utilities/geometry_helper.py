from math import sin, cos, sqrt, atan2, radians


def get_distance(lng, lat, target):
    # approximate radius of earth in km
    R = 6378.0

    source_lng, source_lat = radians(lng), radians(lat)
    target_lat, target_lng = radians(target.lng), radians(target.lat)

    diff_lat = target_lat - source_lng
    diff_lng = target_lng - source_lat

    # Formula for getting distance between (lat, lng): d = acos( sin φ1 ⋅ sin φ2 + cos φ1 ⋅ cos φ2 ⋅ cos Δλ ) ⋅ R
    a = sin(diff_lat / 2) ** 2 + cos(source_lng) * cos(target_lat) * sin(diff_lng / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c

    return distance
