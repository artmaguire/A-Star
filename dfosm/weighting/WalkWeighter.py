from .Weighter import Weighter
from ..classes import Node


class WalkWeighter(Weighter):
    def cost_modifier(self, node: Node):
        return node.initial_cost

    def distance_modifier(self, node: Node):
        if node.node_options.dijkstra:
            return 0

        if node.previous is None or node.previous.distance <= 0:
            return 0

        delta = ((node.distance - node.previous.distance) / node.kmh) * 60

        if node.cost_minutes < 1:
            return 0

        # Start
        if node.cost_minutes < 8:
            delta /= 1.4
        # End
        elif node.distance < 8:
            delta *= 1.4
        else:
            delta *= 1.2

        return delta
