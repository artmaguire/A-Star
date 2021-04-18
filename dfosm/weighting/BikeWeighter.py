from .Weighter import Weighter
from ..classes import Node


class BikeWeighter(Weighter):
    def cost_modifier(self, node: Node):
        if node.node_options.dijkstra:
            return node.initial_cost

        cost = node.initial_cost

        if node.cost_minutes < 1:
            return cost / 10

        # Start
        if node.cost_minutes < 3:
            if node.clazz < 30 or node.clazz == 43:
                cost /= 1
            else:
                cost *= 1
        # End
        elif node.distance < 8:
            if node.clazz < 30 or node.clazz == 43:
                cost /= 0.7
            else:
                cost *= 1
        # Middle End
        elif (node.distance / node.node_options.starting_distance) > .5:
            if node.clazz < 30 or node.clazz == 43:
                cost *= 1
        # Middle Start
        else:
            if node.clazz <= 22 or node.clazz == 43:
                cost *= 0.7
            else:
                cost *= 1

        return cost

    def distance_modifier(self, node: Node):
        if node.node_options.dijkstra:
            return 0

        if node.previous is None or node.previous.distance <= 0:
            return 0

        delta = ((node.distance - node.previous.distance) / node.kmh) * 60

        if node.cost_minutes < 1:
            return 0

        # Start
        if node.cost_minutes < 3:
            if node.clazz < 30 or node.clazz == 43:
                delta /= 1
        # End
        elif node.distance < 8:
            if node.clazz < 30 or node.clazz == 43:
                delta *= 2
            else:
                delta *= 2
        # Middle End
        elif (node.distance / node.node_options.starting_distance) > .5:
            if node.clazz < 30 or node.clazz == 43:
                delta *= 1.2
        # Middle Start
        else:
            if node.clazz <= 22 or node.clazz == 43:
                delta *= 1.2
            else:
                delta *= 1

        return delta
