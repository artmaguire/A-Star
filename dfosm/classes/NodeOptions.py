from dataclasses import dataclass


@dataclass
class NodeOptions:
    dijkstra: bool = False
    starting_distance: float = 0
