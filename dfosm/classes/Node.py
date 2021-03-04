class Node:
    def __init__(self, node_id, previous_cost, cost, lng, lat, km=0, kmh=1, distance=1, previous=None, geojson=None):
        self.node_id = node_id
        self.cost = previous_cost + (cost * 120 / float(kmh))
        self.lng = lng
        self.lat = lat
        self.km = km
        self.kmh = kmh
        self.distance = distance
        self.previous = previous
        self.geojson = geojson

    def get_total_distance(self):
        if not self.previous:
            return self.km

        return self.km + self.previous.get_total_distance()

    def __get_total_cost__(self):
        return self.cost + (self.distance / 50) * 60

    def __str__(self) -> str:
        return f"[id: {self.node_id}, \tCost: {round(self.cost, 2)}m, \tDistance: {round(self.distance, 2)}km]"

    def __lt__(self, other):
        return self.__get_total_cost__() < other.__get_total_cost__()
