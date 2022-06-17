import math
from dataclasses import dataclass, asdict
from typing import Protocol
from gas_emissions_constants import GasEmissionConstants as Constants


@dataclass
class CanCalcMethane(Protocol):
    """
    List of
    """
    VSd: float
    VSnd: float


class GasEmissions:
    @staticmethod
    def calc_methane(data: CanCalcMethane, temp=15.0) -> float:
        """
        ECH4,man = 	[(( 24 * Vs,d * b1)/1000) * exp[ln(A)) - (E/RT)] + (( 24 * Vs,nd *  b2)/1000) * exp[ln(A) -(E/RT)]

        E CH4 man = emission of CH4 from the storage, kg CH4/day
        Vs,d and Vs, nd = degradable and non-degradable VS in the manure, g
        b1 and b2 = rate correcting factors, dimensionless
        A = Arrhenius parameter, g CH4/kg VS-h
        E = apparent activation energy, J/mol
        R = gas constant, J/K-mol
        T = temperature, K
        VS = volatile solids

        Constants

        b1	           = 1
        b2	           = 0.0.1
        ln(A)          = 43.33
        E	           = 112700
        R	           = 8.314
        Temp (manure) °K   = T + 273.15
        T                  = 0 to 25 degree C
        B0                 = 0.2
        ECH4,pot           = 0.48
        VS                 = input value from the manure

        """
        daily_time_steps = 24
        b1 = 1.0
        b2 = 0.01
        lnA = 43.33
        E = 112700
        R = 8.314
        T = temp + 273.15
        ex = math.exp(lnA - (E / (R * T)))

        # Equation: (( 24 * Vs,d * b1)) * exp[ln(A)) - (E/RT)] + (( 24 * Vs,nd *  b2)) * exp[ln(A) -(E/RT)]
        return (daily_time_steps * data.VSd * b1 * ex) + (daily_time_steps * data.VSnd * b2 * ex)

        # Simplified: return daily_time_steps * ex * (output.VSd * b1 + output.VSnd * b2)

    @staticmethod
    def calc_methane2(data: CanCalcMethane, temp=15.0, Bo=0.2, E_CH4_pot=0.48) -> float:
        c = 0.024
        VS_tot = data.VSd + data.VSnd
        b1 = 1.0
        b2 = 0.01
        lnA = 43.33
        E = 112700
        R = 8.314
        T = temp + 273.15
        ex = math.exp(lnA - (E / (R * T)))
        VS_loss = 3 * Bo
        VSd = (data.VSd * (Bo / E_CH4_pot) - VS_loss) / VS_tot
        VSnd = VS_tot - VSd

        print(f'raw data: {data}')
        print(f'new VSd: {VSd}')
        print(f'new VSnd: {VSnd}')

        return c * VS_tot * (VSd * b1 + VSnd * b2) * ex


@dataclass
class FakeOutput:
    VSd = 3546.6
    VSnd = 4163.4

    def __str__(self):
        return f'{self.VSd}, {self.VSnd}'


if __name__ == '__main__':
    print(f'method1: {GasEmissions.calc_methane(FakeOutput())}')
    print()
    print(f'method2: {GasEmissions.calc_methane2(FakeOutput())}')
