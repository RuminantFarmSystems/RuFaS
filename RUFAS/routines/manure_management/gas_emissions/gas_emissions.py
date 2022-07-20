import math
from dataclasses import dataclass
from typing import Protocol

from RUFAS.routines.manure_management.misc.simple_pen import SimplePen


class GasEmissionConstants:
    """
    Stores a list of constants useful for evaluating gas emission equations.
    """

    b1 = 1.0  # rate correcting factor, dimensionless
    b2 = 0.01  # rate correcting factor, dimensionless
    lnA = 43.33  # log of Arrhenius parameter, g CH4/kg VS-h
    E = 112700  # apparent activation energy, J/mol
    R = 8.314  # gas constant, J/K-mol

    r_storage_for_manure_with_crust = 75
    r_storage_for_manure_without_crust = 19
    r_storage_for_solid_manure = 10


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
    def calc_E_CH4_storage_v1(data: CanCalcMethane, temp_in_C=15.0) -> float:
        """
        TODO: Describe

        Notes
        -----
        ECH4,man = 	[(( 24 * Vs,d * b1)/1000) * exp[ln(A)) - (E/RT)] + (( 24 * Vs,nd *  b2)/1000) * exp[ln(A) -(E/RT)]
        where
            E_CH4_man = emission of CH4 from the storage, kg CH4/day
            VSd and VSnd = degradable and non-degradable VS in the manure, g
            b1 and b2 = rate correcting factors, dimensionless
            A = Arrhenius parameter, g CH4/kg VS-h
            E = apparent activation energy, J/mol
            R = gas constant, J/K-mol
            T = temperature, K

        Parameters
        ----------
        data: an output object from one of the manure management steps
            that should follow the CanCalcMethane protocol.
        temp_in_C: temperature, C.

        Returns
        -------
        CH4 emissions from storage, kg CH4/day.

        """
        daily_time_steps = 24
        const = GasEmissionConstants
        b1, b2 = const.b1, const.b2

        lnA, E, R = const.lnA, const.E, const.R
        temp_in_K = GasEmissions.convert_temp_C_to_K(temp_in_C)
        exp = math.exp(lnA - (E / (R * temp_in_K)))

        return (daily_time_steps * data.VSd * b1 * exp) + (daily_time_steps * data.VSnd * b2 * exp)

    @staticmethod
    def calc_E_CH4_storage_v2(data: CanCalcMethane, temp_in_C=15.0, Bo=0.2, E_CH4_pot=0.48) -> float:
        """
        TODO: Describe

        Parameters
        ----------
        data: an output object from one of the manure management steps
            that should follow the CanCalcMethane protocol.
        temp_in_C: temperature, C.
        Bo:  achievable emission of CH4 during anaerobic digestion, kg CH4/kg VS.
        E_CH4_pot: potential CH4 yield of the manure, kg CH4/kg VS.

        Returns
        -------
        CH4 emission from storage, kg CH4/day.

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
        """
        TODO: Describe

        Parameters
        ----------
        hours:

        Returns
        -------
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
        """
        Calculates ambient temperature.

        Parameters
        ----------
        t_min: Minimum barn temperature, °C
        t_max: Maximum barn temperature, °C
        hours: Measured barn temperature, °C within a day, Hours

        Returns
        -------
        Ambient temperature, °C.

        """

        modified_hours = GasEmissions.calc_modified_hours(hours)
        t_ambient = modified_hours * (t_max - t_min) / 2 + (t_max + t_min) / 2

        return t_ambient

    @staticmethod
    def calc_E_CH4_floor(pen: SimplePen, t_min=20.0, t_max=25.0, hours=24) -> float:
        """
        Calculates CH4 floor emissions.

        Parameters
        ----------
        pen: Housing type and numbers of animals.
        t_min: Minimum barn temperature, °C
        t_max: Maximum barn temperature, °C
        hours: Measured barn temperature,°C within a day, Hours

        Returns
        -------
        CH4 floor emissions, kg CH4/day.

        """

        t_ambient = GasEmissions.calc_ambient_temp(hours, t_min, t_max)
        t = max(-5.0, 0.63 * t_ambient + 6.0)

        return pen.num_animals * max(0.0, 0.13 * t) * pen.barn_area / 1000

    @staticmethod
    def calc_E_C02_floor(pen: SimplePen, t_min=20.0, t_max=25.0, hours=24) -> float:
        """
        Calculates CO2 floor emissions.

        Parameters
        ----------
        pen: Housing type and number of animals.
        t_min: Minimum barn temperature, °C.
        t_max: Maximum barn temperature, °C.
        hours: Measured barn temperature, °C within a day, Hours.

        Returns
        -------
        CO2 floor emissions, kg CO2/day.

        """

        t_ambient = GasEmissions.calc_ambient_temp(hours, t_min, t_max)
        t = max(-5.0, 0.63 * t_ambient + 6.0)
        return pen.num_animals * max(0.0, 0.0065 + 0.0192 * t) * pen.barn_area / 1000

    @staticmethod
    def calc_E_NH3_N(TAN: float, r: float, U: float, tempC: float, p=990.0, pH=7.7) -> float:
        """
        Calculates NH3 emissions.

        Parameters
        ----------
        TAN: total ammonia nitrogen in manure, kg N/m^2.
        r: resistance of NH3 transport from the manure surface to the free atmosphere, s/m.
        U: total amount of manure urine in area of exposed surface, kg.
        tempC: temperature, °C.
        p: manure density, kg/m^3.
        pH: manure acidity.

        Returns
        -------
        NH3 emissions, kg N/m^2/day.

        """

        c = 86400  # time conversion, seconds/day
        tempK = GasEmissions.convert_temp_C_to_K(tempC)
        area = 6.5  # m^2 TODO: Switch based on housing type
        M = U / area  # manure urine per area of exposed surface, kg/m^2
        Q = GasEmissions.calc_Q(tempK, pH)
        return (TAN * c * p) / (r * M * Q)

    @staticmethod
    def calc_r_barn(tempC) -> float:
        """
        TODO: Describe

        Parameters
        ----------
        tempC: temperature, °C.

        Returns
        -------
        TODO: Describe

        """

        hsc = 260  # housing specific constant, s/m
        return hsc * (1 - 0.027 * (20.0 - tempC))

    @staticmethod
    def calc_Kh(tempK: float) -> float:
        """
        TODO: Describe

        Parameters
        ----------
        tempK: temperature, K.

        Returns
        -------
        TODO: Describe

        """

        return 10 ** (1478 / tempK - 1.69)

    @staticmethod
    def calc_Ka(tempK: float, pH: float) -> float:
        """
        TODO: Describe

        Parameters
        ----------
        tempK: temperature, K.
        pH:

        Returns
        -------
        TODO: Describe

        """

        return 1 + 10 ** (0.09018 + 2729.9 / tempK - pH)

    @staticmethod
    def calc_Q(tempK: float, pH: float) -> float:
        """
        TODO: Describe

        Parameters
        ----------
        tempK: temperature, K.
        pH:

        Returns
        -------
        TODO: Describe

        """

        Kh = GasEmissions.calc_Kh(tempK)
        Ka = GasEmissions.calc_Ka(tempK, pH)
        return Kh * Ka

    @staticmethod
    def calc_ruc(tempK: float, cu: float) -> float:
        """
        Returns the rate of urea transformation to TAN (RUC) via Eq. (1), kg/m3-h.

        Parameters
        ----------
        tempK: temperature, K.
        cu: urea concentration in urine, kg/m3.

        Returns
        -------
        Rate of urea transformation to TAN (RUC), kg/m3-h.

        """

        # maximum rate of urea conversion, kg N/m3 wet feces-h
        vmax = GasEmissions.calc_vmax(tempK)

        # Michaelis-Menten coefficient, kg N/m3 mixture
        Kmc = GasEmissions.calc_Kmc(tempK)

        return vmax * cu / (Kmc + cu)

    @staticmethod
    def calc_vmax(tempK: float) -> float:
        """
        Returns the maximum rate of urea conversion (Vmax), kg N/m3 wet feces-h.

        Parameters
        ----------
        temp_in_K - temperature in Kelvin.

        Returns
        -------
        Maximum rate of urea conversion (Vmax), kg N/m3 wet feces-h.

        """

        return 3.915 * (10 ** 9) * math.exp(-6463 / tempK)

    @staticmethod
    def calc_Kmc(tempK: float) -> float:
        """
        Returns the Michaelis-Menten coefficient (Kmc), kg N/m3 mixture.

        Parameters
        ----------
        tempK: temperature, K.

        Returns
        -------
        The Michaelis-Menten coefficient (Kmc), kg N/m3 mixture.

        """

        return 3.371 * (10 ** 8) * math.exp(-5914 / tempK)

    # TODO: Review
    @staticmethod
    def calc_E_N20_manure(pen: SimplePen) -> float:
        """
        TODO: Describe

        Notes
        -----
        For stacked manure with a greater DM content, an emission factor
            of 0.005 kg N2O-N /(kg N excreted) when a crust does not form,
            no N2O is formed and emitted. This occurs if the manure DM contents
            are less than 8%, manure is loaded daily onto the top surface of the
            storage, or an enclosed tank is used.
        EN2O,manure = emission of N2O from slurry storage, kg N2O /day

        Parameters
        ----------
        pen: A SimplePen object to get the barn area from

        Returns
        -------

        """
        # emission rate of N2O, g N2O/m2-day
        EF_N2O = 0.8

        A_storage = pen.barn_area

        return (EF_N2O * A_storage) / 1000

    # TODO: Review
    @staticmethod
    def calc_f(pH: float, Ka: float) -> float:
        """
        Returns the NH3 fraction of TAN in a manure solution (F).

        Parameters
        ----------
        pH : surface pH of manure or urine.
        Ka: the dissociation constant.

        Returns
        -------
        NH3 fraction of TAN in a manure solution (F).

        """

        return 1 / (1 + (10 ** (-pH)) / Ka)

    # TODO: Review
    @staticmethod
    def calc_mass_transfer_coefficient_gaseous(U: float, SC: float) -> float:
        """
        Returns the mass transfer coefficient through gaseous layer.

        Parameters
        ----------
        U: air friction velocity near surface, m/s.
        SC: Schmidt number.

        Returns
        -------
        Mass transfer coefficient through gaseous layer.

        """

        return 0.001 + 0.0462 * U * (SC ** (-0.67))

    # TODO: Review
    @staticmethod
    def calc_air_friction_velocity(Va: float) -> float:
        """
        Returns the air friction velocity.

        Parameters
        ----------
        Va: ambient air velocity measured at a standard anemometer height of 10 m

        Returns
        -------
        Air friction velocity

        """

        return 0.02 * Va ** 1.5

    # TODO: Review
    @staticmethod
    def calc_mass_transfer_coefficient_liquid(T: float) -> float:
        """
        Returns the mass transfer coefficient through liquid layer.

        Parameters
        ----------
        T: temperature, K.

        Returns
        -------
        Mass transfer coefficient through liquid layer.

        """

        return 1.417 * 10 ** (-12) * T ** 4

    # TODO: Review
    @staticmethod
    def calc_resistance_to_mass_transfer(Rs: float, Rc: float) -> float:
        """
        Returns the resistance to mass transfer.

        Parameters
        ----------
        Rs = resistance to mass transfer through the manure, s/m
        Rc = resistance to mass transfer through a storage cover, s/m

        Returns
        -------
        resistance to mass transfer.

        """

        return Rs + Rc

    # TODO: Review
    @staticmethod
    def calc_overall_mass_transfer_coefficient(H: float, Kg: float, Kl: float, Rm: float) -> float:
        """
        Returns the overall mass transfer coefficient, the reciprocal of the
        sum of the three resistances to mass transfer.

        Parameters
        ----------
        Rm: resistance to mass transfer
        H:  Henry’s Law constant for ammonia, dimensionless aqueous:gas
        Kg: = mass transfer coefficient through gaseous layer, m/s
        Kl: mass transfer coefficient through liquid layer

        Returns
        -------


        """

        return 1 / (H / Kg + 1 / Kl + Rm)

    # TODO: Review
    @staticmethod
    def calc_NH3_flux(K: float, Cm: float, H: float, Ca: float) -> float:
        """
        Returns the NH3 flux, kg/m2-s

        Parameters
        ----------
        Cm = concentration of NH3 in manure, kg/m3
        Ca = concentration of NH3 in ambient air, kg/m3

        Returns
        -------

        """

        return 3600 * K * (Cm - H * Ca)

    # TODO: Review
    @staticmethod
    def calc_conc_of_NH3_in_manure(F, C_tan):
        """
        Returns the NH3 concentration in the manure

        Parameters
        ----------
        F: NH3 fraction of TAN in a manure solution
        C_tan: concentration of TAN in the manure solution, kg/m^3

        Returns
        -------

        """

        return F * C_tan

    @staticmethod
    def convert_temp_C_to_K(temp_in_C: float) -> float:
        """
        Converts a temperature from Celsius to Kelvin.

        Parameters
        ----------
        temp_in_C: temperature, C.

        Returns
        -------
        Temperature, K.

        """

        return temp_in_C + 273.15
