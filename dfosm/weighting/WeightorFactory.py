from .BikeWeightor import BikeWeightor
from .CarWeightor import CarWeightor
from .WalkWeightor import WalkWeightor
from ..utilities.constants import Flags


class WeightorFactory:
    @staticmethod
    def create_weightor(flag: Flags):
        if flag == Flags.CAR.value:
            weightor = CarWeightor()
        elif flag == Flags.BIKE.value:
            weightor = BikeWeightor()
        elif flag == Flags.FOOT.value:
            weightor = WalkWeightor()
        else:
            weightor = CarWeightor()

        return weightor
