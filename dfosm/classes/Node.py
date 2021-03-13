import math


class Node:
    found_route = False

    def __init__(self, node_id, previous_cost, initial_cost, lng, lat, km=0, kmh=2, distance=0, previous=None, geojson=None):
        self.node_id = node_id
        self.lng = lng
        self.lat = lat
        self.km = km
        self.kmh = kmh
        self.distance = distance
        self.previous = previous
        self.geojson = geojson
        self.cost_minutes = initial_cost + self.previous.cost_minutes if self.previous else 0

        self.cost = self.cost_modifier(initial_cost)
        self.distance_minutes = self.distance_modifier()
        self.total_cost = self.calculate_total_cost()

        self.visited = False

    def get_total_distance(self):
        if not self.previous:
            return self.km

        return self.km + self.previous.get_total_distance()

    def calculate_total_cost(self):
        # if self.cost < -self.distance_modifier():
        #     print(round(self.cost, 6), round(self.km, 6), self.kmh, round(self.distance, 6),
        #           round(self.previous.distance, 6) if self.previous else 0, round(self.distance_modifier(), 6),
        #           self.lat, self.lng, self.previous.lat, self.previous.lng,
        #           sep='  -  ')
        return self.cost + self.distance_minutes + self.previous.total_cost if self.previous else 0

    def cost_modifier(self, initial_cost):
        cost = initial_cost

        if self.distance > 5 and self.cost_minutes > 2:
            # cost *= 90 / self.kmh
            if self.kmh >= 100:
                cost *= 0.2
            if self.kmh >= 120:
                cost *= 0.05
            if self.kmh <= 80:
                cost *= 1
            if self.kmh <= 50:
                cost *= 2
            if self.kmh < 40:
                cost *= 100

        if self.distance < 1 and self.kmh > 10:
            cost /= 2

        return cost

    def distance_modifier(self):
        if self.previous is None or self.previous.distance <= 0:
            return 0

        delta = ((self.distance - self.previous.distance) / self.kmh) * 60

        if self.distance > 5 and self.cost_minutes > 2:
            # Lessen the punishment / reward on fast roads to avoid getting stuck on a long bend / ring road
            if self.kmh >= 100:
                delta *= 0.25
            if self.kmh >= 120:
                delta *= 0.2
            if self.kmh <= 80:
                delta *= 1

        if self.cost_minutes < 5:
            delta *= 0.5

        return delta

    def __str__(self) -> str:
        return str(self.serialize())

    def __lt__(self, other):
        if not Node.found_route:
            return self.total_cost < other.total_cost

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
            'total_cost': self.total_cost,
            'km': self.km,
            'kmh': self.kmh,
            'distance': self.distance,
            'distance_minutes': self.distance_minutes,
            'geojson': self.geojson
        }
        return d
