from .NodeOptions import NodeOptions
from ..weighting.CarWeightor import CarWeightor


class Node:
    def __init__(self, node_id=-1, clazz=0, initial_cost=0, lng=0, lat=0, km=0, kmh=2, distance=0, previous=None,
                 geojson=None, node_options=NodeOptions(), weighting=CarWeightor()):
        self.node_id = node_id
        self.clazz = clazz
        self.lng = lng
        self.lat = lat
        self.km = km
        self.kmh = kmh
        self.distance = distance
        self.previous = previous
        self.geojson = geojson
        self.node_options = node_options
        self.initial_cost = initial_cost
        self.cost_minutes = initial_cost + self.previous.cost_minutes if self.previous else 0

        self.cost = weighting.cost_modifier(self)
        self.distance_minutes = weighting.distance_modifier(self)

        self.total_cost = self.calculate_total_cost()

        self.visited = False

    def get_total_distance(self):
        if not self.previous:
            return self.km

        return self.km + self.previous.get_total_distance()

    def get_total_cost(self):
        if not self.previous:
            return self.calculate_total_cost()

        return self.calculate_total_cost() + self.previous.calculate_total_cost()

    def calculate_total_cost(self):
        return self.cost + self.distance_minutes  # + self.previous.total_cost if self.previous else 0

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
            'node_id':          self.node_id,
            'clazz':            self.clazz,
            'initial_cost':     self.initial_cost,
            'cost':             self.cost,
            'total_cost':       self.get_total_cost(),
            'cost_minutes':     self.cost_minutes,
            'km':               self.km,
            'kmh':              self.kmh,
            'distance':         self.distance,
            'distance_minutes': self.distance_minutes,
            'geojson':          self.geojson
        }
        return d

    def __str__(self) -> str:
        d = self.serialize()
        del d['geojson']
        return str(d)

    def __lt__(self, other):
        return self.get_total_cost() < other.get_total_cost()


def __eq__(self, other):
    return self.node_id == other.node_id
