from .BikeWeighter import BikeWeighter
from .CarWeighter import CarWeighter
from .HGVWeighter import HGVWeighter
from .WalkWeighter import WalkWeighter
from ..utilities.constants import Flags


class WeighterFactory:
    @staticmethod
    def create_weighter(flag: Flags):
        if flag == Flags.CAR.value:
            weightor = CarWeighter()
        elif flag == Flags.BIKE.value:
            weightor = BikeWeighter()
        elif flag == Flags.FOOT.value:
            weightor = WalkWeighter()
        elif flag == Flags.HGV.value:
            weightor = HGVWeighter()
        else:
            weightor = CarWeighter()

        return weightor
