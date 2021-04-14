from dataclasses import dataclass

from ..weighting import Weightor


@dataclass
class NodeOptions:
    dijkstra: bool = False
    starting_distance: float = 0
    weightor: Weightor = None
