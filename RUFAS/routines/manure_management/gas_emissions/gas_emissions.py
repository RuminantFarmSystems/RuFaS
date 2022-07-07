import math
from dataclasses import dataclass
from typing import Protocol

from RUFAS.routines.manure_management.misc.simple_pen import SimplePen


class GasEmissionConstants:
    b1 = 1.0  # rate correcting factor, dimensionless
    b2 = 0.01  # rate correcting factor, dimensionless
    lnA = 43.33  # log of Arrhenius parameter, g CH4/kg VS-h
    E = 112700  # apparent activation energy, J/mol
    R = 8.314  # gas constant, J/K-mol


@dataclass
class CanCalcMethane(Protocol):
    """
    To calculate methane emission, we need VSd and VSnd from
    manure handlers, separators, or treatments.
    """
    VSd: float
    VSnd: float


class GasEmissions:
    @staticmethod
    def calc_E_CH4_storage(data: CanCalcMethane, temp_in_C=15.0) -> float:
        """TODO: Add brief description

        ECH4,man = 	[(( 24 * Vs,d * b1)/1000) * exp[ln(A)) - (E/RT)] + (( 24 * Vs,nd *  b2)/1000) * exp[ln(A) -(E/RT)]
        where
            E CH4 man = emission of CH4 from the storage, kg CH4/day
            VSd and VSnd = degradable and non-degradable VS in the manure, g
            b1 and b2 = rate correcting factors, dimensionless
            A = Arrhenius parameter, g CH4/kg VS-h
            E = apparent activation energy, J/mol
            R = gas constant, J/K-mol
            T = temperature, K

        Args:
            data: an output object from one of the manure management steps
                that should follow the CanCalcMethane protocol.
            temp_in_C: temperature in Celsius.

        Returns:
            CH4 emissions from storage.

        """
        daily_time_steps = 24
        const = GasEmissionConstants
        b1, b2 = const.b1, const.b2

        lnA, E, R = const.lnA, const.E, const.R
        temp_in_K = GasEmissions.convert_temp_C_to_K(temp_in_C)
        exp = math.exp(lnA - (E / (R * temp_in_K)))

        return (daily_time_steps * data.VSd * b1 * exp) + (daily_time_steps * data.VSnd * b2 * exp)

    @staticmethod
    def calc_E_CH4_storage_2(data: CanCalcMethane, temp_in_C=15.0, Bo=0.2, E_CH4_pot=0.48) -> float:
        """TODO: Describe

        Args:
            data: an output object from one of the manure management steps that should follow the CanCalcMethane protocol.
            temp_in_C: temperature, C.
            Bo:  achievable emission of CH4 during anaerobic digestion, kg CH4/kg VS
            E_CH4_pot: potential CH4 yield of the manure, kg CH4/kg VS

        Returns:
            CH4 emission from storage.

        """
        c = 0.024
        VS_tot = data.VSd + data.VSnd
        const = GasEmissionConstants
        b1, b2 = const.b1, const.b2

        lnA, E, R = const.lnA, const.E, const.R
        temp_in_K = GasEmissions.convert_temp_C_to_K(temp_in_C)
        ex = math.exp(lnA - (E / (R * temp_in_K)))

        VS_loss = 3 * Bo
        VSd = (data.VSd * (Bo / E_CH4_pot) - VS_loss) / VS_tot
        VSnd = VS_tot - VSd

        return c * VS_tot * (VSd * b1 + VSnd * b2) * ex

    @staticmethod
    def calc_modified_hours(hours: float) -> float:
        """TODO: Describe

        Args:
            hours:

        Returns:
            TODO: Describe

        """
        if hours > 14:
            modified_hours = - math.tanh(hours - 21.5) / 3.5
        elif hours > 4:
            modified_hours = math.tanh(hours - 9.5) / 2.5
        else:
            modified_hours = - math.tanh(hours + 3.5) / 3.5

        return modified_hours

    @staticmethod
    def calc_ambient_temp(hours: float, t_min: float, t_max: float) -> float:
        """Calculates ambient temperature.

        Args:
            t_min: Minimum barn temperature, °C
            t_max: Maximum barn temperature, °C
            hours: Measured barn temperature,°C within a day, Hours

        Returns:
            Ambient temperature.

        """
        modified_hours = GasEmissions.calc_modified_hours(hours)
        t_ambient = modified_hours * (t_max - t_min) / 2 + (t_max + t_min) / 2

        return t_ambient

    @staticmethod
    def calc_E_CH4_floor(pen: SimplePen, t_min=20.0, t_max=25.0, hours=24) -> float:
        """Calculates CH4 floor emissions.

        Args:
            pen: Housing type and numbers of aniamls.
            t_min: Minimum barn temperature, °C
            t_max: Maximum barn temperature, °C
            hours: Measured barn temperature,°C within a day, Hours

        Returns:
            CH4 floor emissions.

        """
        t_ambient = GasEmissions.calc_ambient_temp(hours, t_min, t_max)
        t = max(-5.0, 0.63 * t_ambient + 6.0)

        return pen.num_animals * max(0.0, 0.13 * t) * pen.barn_area / 1000

    @staticmethod
    def calc_E_C02_floor(pen: SimplePen, t_min=20.0, t_max=25.0, hours=24) -> float:
        """Calculates CO2 floor emissions.

        Args:
            pen: Housing type and number of animals.
            t_min: Minimum barn temperature, °C.
            t_max: Maximum barn temperature, °C.
            hours: Measured barn temperature, °C within a day, Hours.

        Returns:
            CO2 floor emissions.

        """
        t_ambient = GasEmissions.calc_ambient_temp(hours, t_min, t_max)
        t = max(-5.0, 0.63 * t_ambient + 6.0)
        return pen.num_animals * max(0.0, 0.0065 + 0.0192 * t) * pen.barn_area / 1000

    @staticmethod
    def calc_E_NH3_N(Tan, r, U, temp_in_C, p=990.0, pH=7.7) -> float:
        """Calculates NH3 emissions.

        Args:
            Tan: total ammonia nitrogen in manure, kg N/m^2.
            r: resistance of NH3 transport from the manure surface to the free atmosphere, s/m.
            U: total amount of manure urine in area of exposed surface, kg. 
            temp_in_C: temperature, C.
            p: manure density, kg/m^3.
            pH: manure acidity.

        Returns:
            NH3 emissions.

        """
        c = 86400  # time conversion, seconds/day
        temp_in_K = GasEmissions.convert_temp_C_to_K(temp_in_C)
        area = 6.5  # m^2 TODO: Switch based on housing type
        M = U / area  # manure urine per area of exposed surface, kg/m^2
        Q = GasEmissions.calc_Q(temp_in_K, pH)
        return (Tan * c * p) / (r * M * Q)

    @staticmethod
    def calc_r_barn(temp_in_C) -> float:
        """TODO: Describe

        Args:
            temp_in_C: temperature, C.

        Returns:
            TODO: Describe

        """
        hsc = 260  # housing specific constant, s/m
        return hsc * (1 - 0.027 * (20.0 - temp_in_C))

    @staticmethod
    def get_r_storage_for_manure_with_crust() -> float:
        """TODO: Describe

        Returns:
            TODO: Describe

        """
        return 75

    @staticmethod
    def get_r_storage_for_manure_without_crust() -> float:
        """TODO: Describe

        Returns:
            TODO: Describe

        """
        return 19

    @staticmethod
    def get_r_storage_for_solid_manure() -> float:
        """TODO: Describe

        Returns:
            TODO: Describe

        """
        return 10

    @staticmethod
    def calc_Kh(temp_in_K: float) -> float:
        """TODO: Describe

        Args:
            temp_in_K: temperature, K.

        Returns:
            TODO: Describe

        """
        return 10 ** (1478 / temp_in_K - 1.69)

    @staticmethod
    def calc_Ka(temp_in_K: float, pH: float) -> float:
        """TODO: Describe

        Args:
            temp_in_K: temperature, K.
            pH:

        Returns:
            TODO: Describe

        """
        return 1 + 10 ** (0.09018 + 2729.9 / temp_in_K - pH)

    @staticmethod
    def calc_Q(temp_in_K: float, pH: float) -> float:
        """TODO: Describe

        Args:
            temp_in_K: temperature, K.
            pH:

        Returns:
            TODO: Describe

        """
        kh = GasEmissions.calc_Kh(temp_in_K)
        ka = GasEmissions.calc_Ka(temp_in_K, pH)
        return kh * ka

    @staticmethod
    def calc_ruc(temp_in_K: float, cu: float) -> float:
        """Returns the rate of urea transformation to TAN (RUC) via Eq. (1), kg/m3-h.

        Args:
            temp_in_K: temperature, K.
            cu: urea concentration in urine, kg/m3.

        Returns:
            Rate of urea transformation to TAN (RUC), kg/m3-h.

        """
        # maximum rate of urea conversion, kg N/m3 wet feces-h
        vmax = GasEmissions.calc_vmax(temp_in_K)

        # Michaelis-Menten coefficient, kg N/m3 mixture
        Kmc = GasEmissions.calc_Kmc(temp_in_K)

        return vmax * cu / (Kmc + cu)

    @staticmethod
    def calc_vmax(temp_in_K: float) -> float:
        """Returns the maximum rate of urea conversion (Vmax), kg N/m3 wet feces-h.

        Args:
          temp_in_K - temperature in Kelvin.

        Returns:
            Maximum rate of urea conversion (Vmax), kg N/m3 wet feces-h.

        """
        return 3.915 * (10 ** 9) * math.exp(-6463 / temp_in_K)

    @staticmethod
    def calc_Kmc(temp_in_K: float) -> float:
        """Returns the Michaelis-Menten coefficient (Kmc), kg N/m3 mixture.

        Args:
            temp_in_K: temperature, K.

        Returns:
            The Michaelis-Menten coefficient (Kmc), kg N/m3 mixture.

        """
        return 3.371 * (10 ** 8) * math.exp(-5914 / temp_in_K)

    @staticmethod
    def calc_f(pH: float, Ka: float) -> float:
        """
        Returns the NH3 fraction of TAN in a manure solution (F).

        Args:
            pH : surface pH of manure or urine.
            Ka: the dissociation constant.

        Returns:
            NH3 fraction of TAN in a manure solution (F).

        """
        return 1 / (1 + (10 ** (-pH)) / Ka)

    # @staticmethod
    # def calc_Ka(T):
    #     """
    #     Returns the dissociation constant, Ka
    #
    #     Args:
    #       T - temperature in Kelvin
    #     """
    #     return 10 ** (0.05 - 2788 / T)

    # @staticmethod
    # def calc_henry_constant(T):
    #    H = (T / 0.2138) * 10 ** (1825 / T - 6.123)
    #    return H

    @staticmethod
    def calc_mass_transfer_coefficient_gaseous(U, SC):
        """Returns the mass transfer coefficient through gaseous layer.

        Args:
            U = air friction velocity near surface, m/s
            SC = Schmidt number

        Returns:
            TODO: Describe

        """
        return 0.001 + 0.0462 * U * (SC ** (-0.67))

    @staticmethod
    def calc_air_friction_velocity(Va):
        """Returns the air friction velocity.

        Args:
            Va: ambient air velocity measured at a standard anemometer height of
            10 m

        Returns:
            TODO: Describe

        """
        return 0.02 * Va ** 1.5

    @staticmethod
    def calc_henry_constant(T):
        """Returns the  Henry’s Law constant for ammonia, H.

        Args:
            T - temperature in Kelvin

        Returns:
            TODO: Describe

        """
        hsc = (T / 0.2138) * 10 ** (1825 / T - 6.123)

        return hsc * (1 - 0.027 * (20 - T))

    @staticmethod
    def calc_mass_transfer_coefficient_liquid(T):
        """Returns the mass transfer coefficient through liquid layer.

        Args:
            T - temperature in Kelvin

        Returns:
            TODO: Describe

        """
        return 1.417 * 10 ** (-12) * T ** 4

    @staticmethod
    def calc_resistance_to_mass_transfer(Rs, Rc):
        """Returns the resistance to mass transfer.

        Args:
            Rs = resistance to mass transfer through the manure, s/m
            Rc = resistance to mass transfer through a storage cover, s/m

        Returns:
            TODO: Describe

        """
        return Rs + Rc

    @staticmethod
    def calc_overall_mass_transfer_coefficient(H, Kg, Kl, Rm):
        """
        Returns the overall mass transfer coefficient, the reciprocal of the
        sum of the three resistances to mass transfer.

        Args:
            Rm: resistance to mass transfer
            H:  Henry’s Law constant for ammonia, dimensionless aqueous:gas
            Kg: = mass transfer coefficient through gaseous layer, m/s
            Kl: mass transfer coefficient through liquid layer
        """
        return 1 / (H / Kg + 1 / Kl + Rm)

    @staticmethod
    def calc_ammonia_flux(K, Cm, H, Ca):
        """
        Returns the ammonia flux, kg/m2-s

        Args:
            Cm = concentration of ammonia in manure, kg/m3
            Ca = concentration of ammonia in ambient air, kg/m3
        """
        return 3600 * K * (Cm - H * Ca)

    @staticmethod
    def calc_concentration_of_ammonia_in_manure(F, C_tan):
        """Returns the ammonia concentration in the manure

        Args:
            F = ammonia fraction of TAN in a manure solution
            C_tan = concentration of TAN in the manure solution, kg/m^3
        """
        return F * C_tan

    @staticmethod
    def calc_E_N20_manure(EF_n20, A_storage):
        return (EF_n20 * A_storage) / 1000

    """ EN2O,manure = emission of N2O from slurry storage, kg N2O /day
        EF,N2O,man = emission rate of N2O, 0.8 g N2O /m2 -day
        A_storage = exposed surface area of the manure storage, m2

     Note: For stacked manure with a greater DM content, an emission factor of 0.005 kg N2O-N /(kg Nexcreted)
          when a crust does not form, no N2O is formed and emitted. This occurs if the manure DM contents less than 8%, manure is loaded daily onto the top surface of the
          storage, or an enclosed tank is used.
    
    """

    @staticmethod
    def convert_temp_C_to_K(temp_in_C: float) -> float:
        """Converts a temperature from Celsius to Kelvin.

        Args:
            temp_in_C: temperature, C.

        Returns:
            Temperature, K.

        """
        return temp_in_C + 273.15
