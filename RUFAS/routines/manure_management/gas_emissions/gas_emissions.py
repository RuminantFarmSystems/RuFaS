from dataclasses import dataclass
from typing import Protocol


@dataclass
class CanCalcMethane(Protocol):
    Vsd: float
    VSnd: float


class GasEmissions:
    @staticmethod
    def calc_methane(output: CanCalcMethane):
        print(output.Vsd, output.VSnd)


class FakeOutput1:
    def __init__(self):
        self.Vsd = 2.0
        self.VSnd = 3.0


@dataclass
class FakeOutput2:
    Vsd: float = 5.0
    VSnd: float = 6.0
    extra1: float = 10.0


if __name__ == '__main__':
    GasEmissions.calc_methane(FakeOutput1())
    GasEmissions.calc_methane(FakeOutput2())

