import math
from dataclasses import dataclass, asdict
from typing import Protocol

from RUFAS.routines.manure_management.misc.simple_pen import SimplePen
from .gas_emissions_constants import GasEmissionConstants as Constants


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

    @staticmethod
    def calc_nh3_volatilization_n(Tan, c, p, r, m, q):
        return (Tan * c * p) / (r * m * q)

    @staticmethod
    def calc_kh(T):
        return 10 ** (1478 / (T + 273) - 1.69)

    @staticmethod
    def calc_ka(T):
        return 10 ** (1478 / (T + 273) - 1.69)

    @staticmethod
    def calc_methane_floor(pen: SimplePen, t_min=20.0, t_max=25.0, hours=24):
        """
        Calculates the ECH4_floor.
        Inputs:
          t_min:
          t_max:
          hours:
          barn_area: area of the barn floor covered with manure, m2
        """
        if hours > 14:
            modified_hours = - math.tanh(hours - 21.5) / 3.5
        elif hours > 4:
            modified_hours = math.tanh(hours - 9.5) / 2.5
        else:
            modified_hours = - math.tanh(hours + 3.5) / 3.5
        t_ambient = modified_hours * (t_max - t_min) / 2 + (t_max + t_min) / 2
        t = max(-5.0, 0.63 * t_ambient + 6.0)

        if 'Cow' in pen.classes_in_pen:
            if pen.housing_type == 'tie stall':
                barn_area = 1.2
            elif pen.housing_type == 'bedded pack':
                barn_area = 5.0
            else:  # default is free stall
                barn_area = 3.5
        else:
            if pen.housing_type == 'tie stall':
                barn_area = 1.0
            elif pen.housing_type == 'bedded pack':
                barn_area = 3.0
            else:  # default is free stall
                barn_area = 2.5

        return pen.num_animals * (max(0.0, 0.13 * t) * barn_area / 1000)

    @staticmethod
    def calculate_EC02_floor(T, Area_barn):
        """
        Calculates the EC02_floor.
        Inputs:
          T: ambient barn temperature, C
          Area_barn: area of the barn flooor covered with manure, m2
        """
        return max(0.0, (0.0065 + 0.0192 * T)) * Area_barn

    @staticmethod
    def calculate_N2O_storage(A_storage, N2O_man=0.8, ):
        """
        Calculates the nitrous oxide emissions from stored manure.
        :param A_storage: Surface area of the manure storage, m2
        :param N2O_man: Daily emission rate of N2O, 0.8 g N2O m-2 day-1
        :return: Emission of N2O from manure storage, kg N2O day-1
        """
        return (N2O_man * A_storage) / 1000


@dataclass
class FakeOutput:
    VSd = 3546.6
    VSnd = 4163.4

    def __str__(self):
        return f'{self.VSd}, {self.VSnd}'
