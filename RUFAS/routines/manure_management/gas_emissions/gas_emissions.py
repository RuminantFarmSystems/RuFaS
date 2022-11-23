import math
from dataclasses import dataclass
from typing import Protocol

from RUFAS.routines.manure_management.misc.simple_pen import SimplePen


class GasEmissionConstants:
    """Constants for gas emission calculations."""

    b1 = 1.0  # rate correcting factor, dimensionless
    b2 = 0.01  # rate correcting factor, dimensionless
    lnA = 43.33  # log of Arrhenius parameter, g CH4/kg VS-h
    E = 112700  # apparent activation energy, J/mol
    R = 8.314  # gas constant, J/K-mol

    r_storage_for_manure_with_crust = 75.0
    r_storage_for_manure_without_crust = 19.0
    r_storage_for_solid_manure = 10.0


@dataclass
class HasVolatileSolidsAttributes(Protocol):
    """Protocol for objects that have volatile solids attributes."""

    VSd: float
    VSnd: float


class GasEmissions:

    @classmethod
    def calc_E_CH4_storage_v1(cls, data: HasVolatileSolidsAttributes, tempC=15.0) -> float:
        """Calculates methane emissions from manure storage.

        Notes
            ECH4,man = 	[(( 24 * Vs,d * b1)/1000) * exp[ln(A)) - (E/RT)] + (( 24 * Vs,nd *  b2)/1000) * exp[ln(A) -(
            E/RT)]
            where
                E_CH4_man = emission of CH4 from the storage, kg CH4/day
                VSd and VSnd = degradable and non-degradable VS in the manure, g
                b1 and b2 = rate correcting factors, dimensionless
                A = Arrhenius parameter, g CH4/kg VS-h
                E = apparent activation energy, J/mol
                R = gas constant, J/K-mol
                T = temperature, K

        Parameters
            data: an output object from one of the manure management steps
                that should follow the HasVolatileSolidsAttributes protocol.
            tempC: temperature in Celsius, C.

        Returns
            CH4 emissions from storage, kg CH4/day.

        """
        daily_time_steps = 24
        const = GasEmissionConstants
        b1, b2 = const.b1, const.b2

        lnA, E, R = const.lnA, const.E, const.R
        tempK = cls._convert_temp_C_to_K(tempC)
        exp = math.exp(lnA - (E / (R * tempK)))

        return (daily_time_steps * data.VSd * b1 * exp) + (daily_time_steps * data.VSnd * b2 * exp)

    @staticmethod
    def calc_E_CH4_storage_v2(data: HasVolatileSolidsAttributes, tempC=15.0, Bo=0.2, E_CH4_pot=0.48) -> float:
        """Calculates methane emissions from manure storage.

        Parameters
            data: an output object from one of the manure management steps
                that should follow the CanCalcMethane protocol.
            tempC: temperature, C.
            Bo: achievable emission of CH4 during anaerobic digestion, kg CH4/kg VS.
            E_CH4_pot: potential CH4 yield of the manure, kg CH4/kg VS.

        Returns
            CH4 emissions from storage, kg CH4/day.

        """

        c = 0.024
        VS_tot = data.VSd + data.VSnd
        const = GasEmissionConstants
        b1, b2 = const.b1, const.b2

        lnA, E, R = const.lnA, const.E, const.R
        temp_in_K = GasEmissions._convert_temp_C_to_K(tempC)
        ex = math.exp(lnA - (E / (R * temp_in_K)))

        VS_loss = 3 * Bo
        VSd = (data.VSd * (Bo / E_CH4_pot) - VS_loss) / VS_tot
        VSnd = VS_tot - VSd

        return c * VS_tot * (VSd * b1 + VSnd * b2) * ex

    
    def calc_E_CH4_slurry_storage_v3(Ts,enclosed=False,tempC=15.0,Pvs=0.68, Bo=0.2, E_CH4_pot=0.48,n_eff=0.99,VS_loss_yesterday=0.0) -> float:
        """Calculates methane emissions from manure storage using total solids and manure kg.

        Parameters
            Ts: Total solids in kg
            enclosed: Boolean True if manure storage is enclosed, else False if manure storage is open to air
            tempC: temperature, C.
            Pvs: Fraction (0-1) volatile solids
            Bo: achievable emission of CH4 during anaerobic digestion, kg CH4/kg VS.
            E_CH4_pot: potential CH4 yield of the manure, kg CH4/kg VS.
            n_eff: efficicency of process              TODO: confirm n_eff meaning
            VS_loss_yesterday: VS loss from previous day. 

        Returns
            CH4 emissions from storage, kg CH4/day.
        """

        c = 0.024
        VS_tot = Ts*Pvs
        const = GasEmissionConstants
        b1, b2 = const.b1, const.b2

        lnA, E, R = const.lnA, const.E, const.R
        temp_in_K = GasEmissions._convert_temp_C_to_K(tempC)
        ex = math.exp(lnA - (E / (R * temp_in_K)))

        VSd = (Bo / E_CH4_pot)
        VSnd = 1 - VSd

        if(not enclosed):
            return c * VS_tot * (VSd * b1 + VSnd * b2) * ex
        else:
            return c * VS_tot * (VSd * b1 + VSnd * b2) * ex* (1-n_eff)

    @staticmethod
    def _calc_modified_hours(hours: float) -> float:
        """Calculate modified hours."""

        if hours > 14:
            modified_hours = - math.tanh(hours - 21.5) / 3.5
        elif hours > 4:
            modified_hours = math.tanh(hours - 9.5) / 2.5
        else:
            modified_hours = - math.tanh(hours + 3.5) / 3.5

        return modified_hours

    @classmethod
    def _calc_ambient_temp(cls, hours: float, t_min: float, t_max: float) -> float:
        """Calculates ambient temperature.

        Parameters
            hours: Measured barn temperature, °C within a day, Hours  # TODO: what is this? H = hour of the day from
            1 to 24
            t_min: Minimum barn temperature, °C
            t_max: Maximum barn temperature, °C

        Returns
            Ambient temperature, °C.

        """

        modified_hours = cls._calc_modified_hours(hours)
        t_ambient = modified_hours * (t_max - t_min) / 2 + (t_max + t_min) / 2

        return t_ambient

    @classmethod
    def calc_E_CH4_floor(cls, pen: SimplePen, hours=24, t_min=20.0, t_max=25.0) -> float:
        """Calculates methane floor emissions.

        Parameters
            pen: A SimplePen object.
            hours: Measured barn temperature,°C within a day, Hours  # TODO: what is this? H = hour of the day from 1
            to 24
            t_min: Minimum barn temperature, °C
            t_max: Maximum barn temperature, °C

        Returns
            Methane floor emissions, kg CH4/day.

        """

        t_ambient = cls._calc_ambient_temp(hours, t_min, t_max)
        t = max(-5.0, 0.63 * t_ambient + 6.0)

        return pen.num_animals * max(0.0, 0.13 * t) * pen.barn_area / 1000

    @classmethod
    def calc_E_C02_floor(cls, pen: SimplePen, hours=24, t_min=20.0, t_max=25.0) -> float:
        """Calculates carbon dioxide floor emissions.

        Parameters
            pen: A SimplePen object.
            hours: Measured barn temperature, °C within a day, Hours. # TODO: what is this? H = hour of the day from
            1 to 24
            t_min: Minimum barn temperature, °C.
            t_max: Maximum barn temperature, °C.

        Returns
            Carbon dioxide floor emissions, kg CO2/day.

        """

        t_ambient = cls._calc_ambient_temp(hours, t_min, t_max)
        t = max(-5.0, 0.63 * t_ambient + 6.0)
        return pen.num_animals * max(0.0, 0.0065 + 0.0192 * t) * pen.barn_area / 1000

    @classmethod
    def calc_E_NH3_housing(cls, pen: SimplePen, TAN: float, U: float, tempC: float, p=990.0, pH=7.7) -> float:
        """Calculates ammonia housing emissions.

        Parameters
            pen: A SimplePen object.
            TAN: total ammonia nitrogen in manure, kg N/m^2.
            U: total amount of manure urine in area of exposed surface, kg.
            tempC: temperature in Celsius, °C.
            p: manure density, kg/m^3.
            pH: manure acidity, dimensionless.

        Returns
            Ammonia emissions, kg N/m^2/day.

        """

        c = 86_400  # seconds in a day
        tempK = cls._convert_temp_C_to_K(tempC)
        area = pen.housing_area_for_NH3_emission  # m^2
        r = cls._calc_r_barn(tempC, hsc=260.0)
        M = U / area  # manure urine per area of exposed surface, kg/m^2
        Q = cls._calc_Q(tempK, pH)
        return (TAN * c * p) / (r * M * Q)

    @classmethod
    def calc_E_NH3_storage(cls, TS: float, TAN: float, U: float, tempC: float, area=6.5, p=990.0, pH=7.5) -> float:
        """Calculates NH3 storage emissions.

        Parameters
            TS: total solids or dry matter content, %.
            TAN: total ammonia nitrogen in manure, kg N/m^2.
            U: total amount of manure urine in area of exposed surface, kg.
            tempC: temperature, °C.
            area: surface area for treatment, m^2.
            p: manure density, kg/m^3.
            pH: manure acidity, dimensionless.

        Returns
            NH3 storage emissions, kg N/m^2/day.

        """

        c = 86_400  # seconds in a day
        tempK = cls._convert_temp_C_to_K(tempC)
        r = cls._calc_r_barn(tempC, hsc=cls._calc_hsc_from_dry_matter_content(TS))
        M = U / area  # manure urine per area of exposed surface, kg/m^2
        Q = cls._calc_Q(tempK, pH)
        return (TAN * c * p) / (r * M * Q)
    
    @classmethod
    def calc_E_NH3_storage_v2(cls,barn_area:float,TAN: float,U:float, tempC: float,HSC=260 ) -> float:
        """Calculates NH3 storage emissions.
        Parameters
            pen: Simple pen to use lookup area
            TAN: total ammonia nitrogen in manure, kg N/m^2.
            U: total amount of manure urine in area of exposed surface, kg.
            tempC: temperature, °C.
            area: surface area for treatment, m^2.
        Returns
            NH3 storage emissions, kg N/m^2/day.
        """
        """ Constants
                p: manure density, kg/m^3.
                pH: manure acidity, dimensionless.
                c: seconds in a day
        """
        p=990.0
        pH=7.5
        area = barn_area
        c = 86_400  # seconds in a day
        tempK = cls._convert_temp_C_to_K(tempC)
        r = cls._calc_r_barn(tempC, hsc=HSC)
        M = U / area  # manure per area of exposed surface, kg/m^2
        Q = cls._calc_Q(tempK, pH)
        if(r*M*Q>0):
            return (TAN * c * p) / (r * M * Q)
        else:
            return 0


    @staticmethod
    def _calc_hsc_from_dry_matter_content(TS: float) -> float:
        """Calculates heat storage capacity from dry matter content.

        Parameters
            TS: total solids or dry matter content, %.

        Returns
            Heat storage capacity, J/kg/K.

        """

        if TS <= 5.0:  # liquid
            return 4.1
        elif TS <= 8.0:  # slurry
            return 19.0
        elif TS <= 13.0:  # semi-solid
            return 10.0
        else:  # solid
            return 10.0

    @staticmethod
    def _calc_r_barn(tempC, hsc=260.0) -> float:
        """Calculates barn resistance.

        Parameters
            tempC: temperature in Celsius, °C.
            hsc: housing specific constant, s/m

        Returns
            Barn resistance, s/m.

        """

        return hsc * (1 - 0.027 * (20.0 - tempC))

    @staticmethod
    def _calc_Kh(tempK: float) -> float:
        """Calculates Henry's constant.

        Parameters
            tempK: temperature in Kelvin, K.

        Returns
            Henry's constant, M/atm.

        """

        return 10 ** (1478 / tempK - 1.69)

    @staticmethod
    def _calc_Ka(tempK: float, pH: float) -> float:
        """Calculates acid dissociation constant.

        Parameters
            tempK: temperature in Kelvin, K.
            pH: manure acidity, dimensionless.

        Returns
            Acid dissociation constant, dimensionless.

        """

        return 1 + 10 ** (0.09018 + 2729.9 / tempK - pH)

    @classmethod
    def _calc_Q(cls, tempK: float, pH: float) -> float:
        """Calculates Q. # TODO: What is Q? Q = dimensionless equilibrium coefficient for the NH3 gas in the air for
        a given concentration of TAN in the solution.

        Parameters
            tempK: temperature in Kelvin, K.
            pH: manure acidity, dimensionless.

        Returns
            Q.

        """

        Kh = cls._calc_Kh(tempK)
        Ka = cls._calc_Ka(tempK, pH)
        return Kh * Ka

    @classmethod
    def calc_ruc(cls, tempK: float, cu: float) -> float:
        """Calculates the rate of urea transformation to TAN (RUC) via Eq. (1), kg/m3-h.

        Parameters
            tempK: temperature in Kelvin, K.
            cu: urea concentration in urine, kg/m3.

        Returns
            Rate of urea transformation to TAN (RUC), kg/m3-h.

        """

        # maximum rate of urea conversion, kg N/m3 wet feces-h
        vmax = cls._calc_vmax(tempK)

        # Michaelis-Menten coefficient, kg N/m3 mixture
        Kmc = cls._calc_Kmc(tempK)

        return vmax * cu / (Kmc + cu)

    @staticmethod
    def _calc_vmax(tempK: float) -> float:
        """Calculates the maximum rate of urea conversion (Vmax) via Eq. (2).

        Parameters
            tempK: temperature in Kelvin, K.

        Returns
            Maximum rate of urea conversion (Vmax), kg N/m3 wet feces-h.

        """

        return 3.915 * (10 ** 9) * math.exp(-6463 / tempK)

    @staticmethod
    def _calc_Kmc(tempK: float) -> float:
        """Calculates the Michaelis-Menten coefficient (Kmc).

        Parameters
            tempK: temperature in Kelvin, K.

        Returns
            The Michaelis-Menten coefficient (Kmc), kg N/m3 mixture.

        """

        return 3.371 * (10 ** 8) * math.exp(-5914 / tempK)

    @staticmethod
    def calc_E_N20_manure(TS: float, A_storage=6.5) -> float:
        """Calculates nitrous oxide emissions from slurry storage.

        Notes
            For stacked manure with a greater DM content, an emission factor
                of 0.005 kg N2O-N /(kg N excreted) when a crust does not form,
                no N2O is formed and emitted. This occurs if the manure DM contents
                are less than 8%, manure is loaded daily onto the top surface of the
                storage, or an enclosed tank is used.

        Parameters
            TS: total solids or dry matter content, %.
            A_storage: surface area for treatment, m^2. Default is 6.5 m^2. # TODO: Verify this.

        Returns
            Nitrous oxide emissions from slurry storage, kg N2O-N /day.

        """

        # emission rate of N2O, g N2O/m2-day
        EF_N2O = 0.8 if TS > 8.0 else 0.005

        return (EF_N2O * A_storage) / 1000

    # TODO: Review
    @staticmethod
    def _calc_f(pH: float, Ka: float) -> float:
        """Returns the NH3 fraction of TAN in a manure solution (F).

        Parameters
            pH: surface pH of manure or urine.
            Ka: acid dissociation constant, dimensionless.

        Returns
            NH3 fraction of TAN in a manure solution (F).

        """

        return 1 / (1 + (10 ** (-pH)) / Ka)

    # TODO: Review
    @staticmethod
    def _calc_mass_transfer_coefficient_gaseous(U: float, SC: float) -> float:
        """Calculates the mass transfer coefficient through gaseous layer.

        Parameters
            U: air friction velocity near surface, m/s.
            SC: Schmidt number, dimensionless.

        Returns
            Mass transfer coefficient through gaseous layer. # TODO: What is the unit?

        """

        return 0.001 + 0.0462 * U * (SC ** (-0.67))

    # TODO: Review
    @staticmethod
    def _calc_air_friction_velocity(Va: float) -> float:
        """Calculates the air friction velocity near surface.

        Parameters
            Va: ambient air velocity measured at a standard anemometer height of 10 m.

        Returns
            Air friction velocity near surface, m/s.

        """

        return 0.02 * Va ** 1.5

    # TODO: Review
    @staticmethod
    def _calc_mass_transfer_coefficient_liquid(T: float) -> float:
        """Calculates the mass transfer coefficient through liquid layer.

        Parameters
            T: temperature in Kelvin, K.

        Returns
            Mass transfer coefficient through liquid layer. # TODO: What is the unit?

        """

        return 1.417 * 1E-12 * (T ** 4)

    @staticmethod
    def _calc_resistance_to_mass_transfer(Rs: float, Rc: float) -> float:
        """Calculates the resistance to mass transfer.

        Parameters
            Rs: resistance to mass transfer through the manure, s/m
            Rc: resistance to mass transfer through a storage cover, s/m

        Returns
            Resistance to mass transfer, s/m.

        """

        return Rs + Rc

    # TODO: Review
    @staticmethod
    def _calc_overall_mass_transfer_coefficient(H: float, Kg: float, Kl: float, Rm: float) -> float:
        """Calculates the overall mass transfer coefficient.

        It is equal to the reciprocal of the sum of the three resistances to mass transfer.

        Parameters
            Rm: Resistance to mass transfer. # TODO: What is the unit?
            H:  Henry’s Law constant for ammonia, dimensionless aqueous:gas. # TODO: What is the unit?
            Kg: Mass transfer coefficient through gaseous layer, m/s. # TODO: What is the unit?
            Kl: Mass transfer coefficient through liquid layer. # TODO: What is the unit?

        Returns
            Overall mass transfer coefficient, m/s.

        """

        return 1 / (H / Kg + 1 / Kl + Rm)

    @staticmethod
    def _calc_NH3_flux(K: float, Cm: float, H: float, Ca: float) -> float:
        """Calculates the ammonia flux.

        Returns the NH3 flux, kg/m2-s

        Parameters
            Cm: concentration of NH3 in manure, kg/m3.
            Ca: concentration of NH3 in ambient air, kg/m3.

        Returns
            Ammonia flux, kg/m2-s.

        """

        return 3600 * K * (Cm - H * Ca)

    # TODO: Review
    @staticmethod
    def _calc_NH3_conc_in_manure(F: float, C_tan: float) -> float:
        """Calculates the ammonia concentration in manure.

        Parameters
            F: NH3 fraction of TAN in a manure solution, dimensionless.
            C_tan: concentration of TAN in the manure solution, kg/m^3

        Returns
            Ammonia concentration in manure, kg/m^3.

        """

        return F * C_tan

    @staticmethod
    def _convert_temp_C_to_K(tempC: float) -> float:
        """Converts a temperature from Celsius to Kelvin.

        Parameters
            tempC: temperature in Celsius, C.

        Returns
            Temperature in Kelvin, K.

        """

        return tempC + 273.15

    @staticmethod
    def calc_E_CH4_anaerobic_lagoon(VS: float) -> float:
        """Calculates methane emissions from anaerobic lagoon.

        Parameters
            VS: volatile solids.  # TODO: What is the unit?

        Returns
            Methane emissions from anaerobic lagoon, kg CH4-N /day.

        """

        # TODO: Probably should move the following constants to the GasEmissionsConstants class.
        Bo = 0.24
        MCF = 0.79
        MS = 0.9
        factor = 0.67  # TODO: Use more descriptive variable name
        return VS * Bo * MCF * MS * factor

    @staticmethod
    def calc_direct_E_N2O_anaerobic_lagoon(manure_nitrogen: float) -> float:
        """Calculates direct nitrous oxide emissions from anaerobic lagoon.

        Parameters
            manure_nitrogen: manure nitrogen, kg N /day.

        Returns
            Direct nitrous oxide emissions from anaerobic lagoon, kg N2O-N /day.

        """

        fMMs = 1.0
        emission_factor_N2O_direct = 0.002
        ratio_atomic_mass = 44 / 28  # N2ON to N2O
        return manure_nitrogen * fMMs * emission_factor_N2O_direct * ratio_atomic_mass

    @staticmethod
    def calc_indirect_N2O_anaerobic_lagoon(manure_nitrogen: float) -> float:
        """Calculates indirect nitrous oxide emissions from anaerobic lagoon.

        Parameters
            manure_nitrogen: manure nitrogen, kg N /day.

        Returns
            Indirect nitrous oxide emissions from anaerobic lagoon, kg N2O-N /day.

        """

        fMMs = 1.0
        emission_factor_N2O_indirect = 0.01
        ratio_atomic_mass = 44 / 28  # N2ON to N2O
        fraction_N_volatilization = 0.25
        return manure_nitrogen * fMMs * emission_factor_N2O_indirect * ratio_atomic_mass * fraction_N_volatilization

    @staticmethod
    def calc_CO2_equivalent_of_CH4(CH4: float) -> float:
        """Calculates the CO2 equivalent of CH4.

        Parameters
            CH4: methane. # TODO: What is the unit? kg/day

        Returns
            CO2 equivalent of CH4. # TODO: What is the unit? kg/day

        """

        return CH4 * 30

    @staticmethod
    def calc_CO2_equivalent_of_N20(N2O: float) -> float:
        """Calculates the CO2 equivalent of N2O.

        Parameters
            N2O: nitrous oxide. # TODO: What is the unit? kg/day

        Returns
            CO2 equivalent of N2O. # TODO: What is the unit? kg/day

        """

        return N2O * 310
