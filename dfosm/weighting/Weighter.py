from abc import ABCMeta, abstractmethod

from ..classes import Node


class Weighter(metaclass=ABCMeta):
    @abstractmethod
    def cost_modifier(self, node: Node):
        pass

    @abstractmethod
    def distance_modifier(self, node: Node):
        pass
