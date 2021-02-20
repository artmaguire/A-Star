class Node:
    def __init__(self, node_id, cost, lat, lng, distance, previous):
        self.node_id = node_id
        self.cost = cost
        self.lat = lat
        self.lng = lng
        self.distance = distance
        self.previous = previous

    def get_neighbouring_nodes(self):
        print("Hello my name is " + self.node_id)

    def __get_total_cost__(self):
        return self.cost + self.distance

    def __str__(self) -> str:
        return f"[id: {self.node_id}, Cost: {self.cost}, Distance: {self.distance}]"

    def __lt__(self, other):
        return self.__get_total_cost__() < other.__get_total_cost__()
