from dataclasses import dataclass

from ..weighting import Weighter


@dataclass
class NodeOptions:
    dijkstra: bool = False
    starting_distance: float = 0
    weighter: Weighter = None
