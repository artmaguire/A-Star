import math

class Node:
    found_route = False

    def __init__(self, node_id, previous_cost, cost, lng, lat, km=0, kmh=2, distance=1, previous=None, geojson=None):
        self.node_id = node_id
        self.cost = previous_cost + cost * (5 / math.log(kmh, math.e))
        self.lng = lng
        self.lat = lat
        self.km = km
        self.kmh = kmh
        self.distance = distance
        self.previous = previous
        self.geojson = geojson
        self.visited = False

    def get_total_distance(self):
        if not self.previous:
            return self.km

        return self.km + self.previous.get_total_distance()

    def get_total_cost(self):
        return math.log(self.cost+1, math.e) + math.log(self.distance_modifier()+1, math.e)

    def distance_modifier(self):
        return (self.distance / 100) * 60

    def __str__(self) -> str:
        return str(self.serialize())

    def __lt__(self, other):
        if not Node.found_route:
            return self.get_total_cost() < other.get_total_cost()

        return self.get_branch_length() < other.get_branch_length()

    def get_previous(self):
        if self.visited is True:
            return None

        self.visited = True
        return self.previous

    def get_branch_length(self):
        if self.visited:
            return 0

        return self.km + self.previous.get_branch_length() if self.previous else 0

    def serialize(self):
        d = {
            'node_id': self.node_id,
            'cost': self.cost,
            'total_cost': self.get_total_cost(),
            'km': self.km,
            'kmh': self.kmh,
            'distance': self.distance,
            'distance_minutes': self.distance_modifier(),
            'geojson': self.geojson
        }
        return d
