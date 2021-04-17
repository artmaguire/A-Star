from .NodeOptions import NodeOptions


class Node:
    def __init__(self, node_id=-1, clazz=0, initial_cost=0, lng=0, lat=0, km=0, kmh=2, distance=0, previous=None,
                 geojson=None, node_options=NodeOptions()):
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
        self.cost_minutes = initial_cost + self.previous.cost_minutes if self.previous else 0

        self.cost = self.cost_modifier(initial_cost)
        self.distance_minutes = self.distance_modifier()
        self.total_cost = self.calculate_total_cost()

        self.visited = False

    def get_total_distance(self):
        if not self.previous:
            return self.km

        print(self.previous.node_id)

        return self.km + self.previous.get_total_distance()

    def get_total_cost(self):
        if not self.previous:
            return self.calculate_total_cost()

        return self.calculate_total_cost() + self.previous.calculate_total_cost()

    def calculate_total_cost(self):
        return self.cost + self.distance_minutes  # + self.previous.total_cost if self.previous else 0

    def cost_modifier(self, initial_cost):
        if self.node_options.dijkstra:
            return initial_cost

        cost = initial_cost

        # Start
        if self.cost_minutes < 8:
            if self.clazz < 30 or self.clazz == 43:
                cost /= 3
            else:
                cost *= 3
        # End
        elif self.distance < 8:
            if self.clazz < 30 or self.clazz == 43:
                cost /= 3
            else:
                cost *= 3
        # Middle section
        else:
            if self.clazz < 20 or self.clazz == 43:
                if self.kmh >= 100:
                    cost *= 0.4
                if self.kmh >= 120:
                    cost *= 0.2
                if self.kmh <= 80:
                    cost *= 1
                if self.kmh <= 50:
                    cost *= 2
                if self.kmh < 40:
                    cost *= 100
            else:
                cost *= 5

        return cost

    def distance_modifier(self):
        if self.node_options.dijkstra:
            return 0

        if self.previous is None or self.previous.distance <= 0:
            return 0

        delta = ((self.distance - self.previous.distance) / self.kmh) * 60

        # Start
        if self.cost_minutes < 8:
            if self.clazz < 30 or self.clazz == 43:
                delta /= 3
        # End
        elif self.distance < 8:
            if self.clazz < 30 or self.clazz == 43:
                delta /= 3
        # End
        elif (self.distance / self.node_options.starting_distance) > .5:
            if self.clazz < 20 or self.clazz == 43:
                if self.kmh >= 100:
                    delta *= 0.5
                if self.kmh >= 120:
                    delta *= 0.4
                if self.kmh <= 80:
                    delta *= 1
        # Middle section
        else:
            if self.clazz < 20 or self.clazz == 43:
                if self.kmh >= 100:
                    delta *= 0.5
                if self.kmh >= 120:
                    delta *= 0.4
                if self.kmh <= 80:
                    delta *= 1

        return delta

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
            'cost':             self.cost,
            'total_cost':       self.get_total_cost(),
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
