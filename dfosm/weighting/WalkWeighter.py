from .Weighter import Weighter
from ..classes import Node


class WalkWeighter(Weighter):
    def cost_modifier(self, node: Node):
        if node.node_options.dijkstra:
            return node.initial_cost

        cost = node.initial_cost

        if node.cost_minutes < 1:
            return cost / 10

        # Start
        if node.cost_minutes < 8:
            if node.clazz < 30 or node.clazz == 43:
                cost /= 3
            else:
                cost *= 5
        # End
        elif node.distance < 8:
            if node.clazz < 30 or node.clazz == 43:
                cost /= 3
            else:
                cost *= 3
        # Middle End
        elif (node.distance / node.node_options.starting_distance) > .5:
            if node.clazz < 30 or node.clazz == 43:
                if node.kmh >= 100:
                    cost *= 0.1
                elif node.kmh >= 80:
                    cost *= 0.2
                elif node.kmh >= 50:
                    cost *= 0.3
                else:
                    cost *= 1
        # Middle Start
        else:
            if node.clazz <= 22 or node.clazz == 43:
                if node.kmh >= 100:
                    cost *= 0.1
                elif node.kmh >= 80:
                    cost *= 0.2
                elif node.kmh >= 50:
                    cost *= 0.3
                else:
                    cost *= 100
            else:
                cost *= 5

        # if cost == 0.014238:
        #     print(node.node_id)
        #     pass

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
        # if node.cost_minutes < 8:
        #     if node.clazz < 30 or node.clazz == 43:
        #         delta /= 3
        # End
        elif node.distance < 8:
            if node.clazz < 30 or node.clazz == 43:
                delta /= 3
            else:
                delta *= 6
        # Middle End
        elif (node.distance / node.node_options.starting_distance) > .5:
            if node.clazz < 30 or node.clazz == 43:
                if node.kmh >= 100:
                    delta *= 0.05
                elif node.kmh >= 80:
                    delta *= 0.08
                elif node.kmh >= 50:
                    delta *= 0.13
                else:
                    delta *= 1
        # Middle Start
        else:
            if node.clazz <= 22 or node.clazz == 43:
                if node.kmh >= 100:
                    delta *= 0.05
                elif node.kmh >= 80:
                    delta *= 0.08
                elif node.kmh >= 50:
                    delta *= 0.13
                else:
                    delta *= 100
            else:
                delta *= 5

        return delta
