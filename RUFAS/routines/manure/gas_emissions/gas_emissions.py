import math

from RUFAS.general_constants import GeneralConstants
from RUFAS.routines.manure.constants.gas_emission_constants import GasEmissionConstants
from RUFAS.routines.manure.constants.manure_constants import ManureConstants


class GasEmissions:
    # TODO: review docstring
    @classmethod
    def calc_methane_emission_for_slurry_storage(cls,
                                                 total_volatile_solids: float,
                                                 temp=GasEmissionConstants.DEFAULT_SLURRY_STORAGE_TEMPERATURE,
                                                 ) -> float:
        """
        Calculates methane emissions from manure storage using total solids.

        # TODO: Add the equation here.

        Parameters
        ----------
        total_volatile_solids : float
            Total volatile solids in manure, kg.
        temp : float
            Temperature in Celsius, C.

        Returns
        -------
        float
            Storage methane emissions, kg CH4/day.

        """
        constants = GasEmissionConstants
        tempK = cls._convert_temp_celsius_to_kelvin(temp)
        arrhenius_exponent = math.exp(constants.lnA - (constants.E / (constants.R * tempK)))

        Vsd = total_volatile_solids * (constants.Bo / constants.POTENTIAL_METHANE_YIELD_OF_MANURE)  # g
        VSnd = total_volatile_solids - Vsd  # g

        VSd_term = 24 * Vsd * constants.b1 * arrhenius_exponent
        VSnd_term = 24 * VSnd * constants.b2 * arrhenius_exponent
        E_CH4_open_air = VSd_term + VSnd_term  # kg CH4/day

        return E_CH4_open_air

    @classmethod
    def _calc_modified_hours(cls, hours: float) -> float:
        """
        Calculate modified hours.

        Parameters
        ----------
        hours : float
            Hours of the day from 1 to 24.

        Returns
        -------
        float
            Modified hours.

        """
        if hours > 14:
            modified_hours = - math.tanh(hours - 21.5) / 3.5
        elif hours > 4:
            modified_hours = math.tanh(hours - 9.5) / 2.5
        else:
            modified_hours = - math.tanh(hours + 3.5) / 3.5

        return modified_hours

    @classmethod
    def _calc_ambient_temp(cls, hours: float, min_temp: float, max_temp: float) -> float:
        """
        Calculate ambient temperature.

        Parameters
        ----------
        hours : float
            Hours of the day from 1 to 24.
        min_temp : float
            Minimum barn temperature, :math:`^{\circ}C`.
        max_temp : float
            Maximum barn temperature, :math:`^{\circ}C`.

        Returns
        -------
        float
            Ambient temperature, :math:`^{\circ}C`.

        """
        modified_hours = cls._calc_modified_hours(hours)
        ambient_temp = modified_hours * (max_temp - min_temp) / 2 + (max_temp + min_temp) / 2
        return ambient_temp

    @classmethod
    def calc_housing_methane_emission(cls, num_animals: int, barn_area: float, barn_temp: float) -> float:
        """
        Calculate methane housing emission.

        Parameters
        ----------
        num_animals : int
            Number of animals in the pen.
        barn_area : float
            Barn area per animal based on housing type, :math:`m^2`.
        barn_temp : float
            Current barn temperature, :math:`^{\circ}C`.

        Returns
        -------
        float
            Methane housing emission, kg CH4/day.

        """
        return num_animals * max(0.0, 0.13 * barn_temp) * barn_area / 1000

    @classmethod
    def calc_housing_carbon_dioxide_emission(cls, num_animals: int, barn_area: float, barn_temp: float) -> float:
        """
        Calculate carbon dioxide housing emission.

        Parameters
        ----------
        num_animals : int
            Number of animals in the pen.
        barn_area : float
            Barn area per animal based on housing type, :math:`m^2`.
        barn_temp : float
            Current barn temperature, :math:`^{\circ}C`.

        Returns
        -------
        float
            Carbon dioxide housing emission, kg CO2/day.

        """
        return num_animals * max(0.0, 0.0065 + 0.0192 * barn_temp) * barn_area / 1000

    @classmethod
    def calc_housing_ammonia_emission(cls,
                                      num_animals: int,
                                      barn_area: float,
                                      urine_total_ammoniacal_nitrogen: float,
                                      urine: float,
                                      temp: float,
                                      pH=GasEmissionConstants.DEFAULT_PH_FOR_HOUSING_AMMONIA,
                                      housing_specific_constant=GasEmissionConstants.DEFAULT_HOUSING_SPECIFIC_CONSTANT_FOR_HOUSING,
                                      ) -> float:
        """
        Calculate ammonia housing emissions for manure handlers.

        Parameters
        ----------
        num_animals : int
            Number of animals in the pen.
        barn_area : float
            Surface area per animal, m^2.
        urine_total_ammoniacal_nitrogen : float
            Total ammoniacal nitrogen in urine per animal, kg N.
        urine : float
            Total urine per animal, kg.
        temp : float
            Current temperature, C.
        pH : float
            pH of the urine.
        housing_specific_constant : float, optional
            Housing specific constant, s/m.
            The default is 260.0.

        """
        total_barn_area = num_animals * barn_area
        TAN = urine_total_ammoniacal_nitrogen / total_barn_area
        p = ManureConstants.MANURE_DENSITY  # kg/m^3
        c = GeneralConstants.SECONDS_PER_DAY  # s/day
        tempK = cls._convert_temp_celsius_to_kelvin(temp)  # K
        r = cls._calc_barn_resistance(temp, housing_specific_constant)
        M = urine / total_barn_area  # manure per area of exposed surface, kg/m^2
        Q = cls._calc_Q(tempK, pH)
        loss = (TAN * c * p) / (r * M * Q)
        total_loss = loss * total_barn_area

        # Add this number to manure TAN, and then pass this new sum to storage ammonia as TAN
        # remaining = (TAN - loss) * total_barn_area

        return max(0.0, total_loss)

    @classmethod
    def calc_storage_ammonia_emission(cls, num_animals: int, manure_total_ammoniacal_nitrogen: float,
                                      manure_volume: float, total_solids: float,
                                      storage_area: float,  # use 1 m^2 for now
                                      temp: float, pH: float) -> float:
        """
        Calculate storage ammonia emissions for manure treatments.

        Parameters
        ----------
        num_animals : int
            Number of animals in the pen.
        manure_total_ammoniacal_nitrogen : float
            Total ammoniacal nitrogen in manure per animal, kg.
        manure_volume : float
            Total manure volume per animal, :math:`m^3`.
        total_solids : float
            Total solids in manure per animal, kg.
        storage_area : float
            Storage area per animal, :math:`m^2`.
        temp : float
            Current temperature, :math:`^{\circ}C`.
        pH : float
            pH of the manure.

        Returns
        -------
        float
            Storage ammonia emission for manure treatments, kg NH3/day.

        """
        TAN = manure_total_ammoniacal_nitrogen
        p = ManureConstants.MANURE_DENSITY  # kg/m^3
        c = GeneralConstants.SECONDS_PER_DAY  # s/day
        tempK = cls._convert_temp_celsius_to_kelvin(temp)  # K

        manure_mass = manure_volume * ManureConstants.MANURE_DENSITY
        housing_specific_constant = cls._calc_housing_specific_constant(manure_mass, total_solids)
        r = cls._calc_barn_resistance(temp, housing_specific_constant)

        M = manure_mass - total_solids
        Q = cls._calc_Q(tempK, pH)
        loss = (TAN * c * p) / (r * M * Q)
        total_loss = loss * storage_area * num_animals

        return max(0.0, total_loss)

    @classmethod
    def _calc_housing_specific_constant(cls, manure_mass: float, total_solids: float) -> float:
        """
        Calculate housing specific constant.

        Parameters
        ----------
        manure_mass : float
            Total manure mass, kg.
        total_solids : float
            Total solids in manure, kg.

        Returns
        -------
        float
            Housing specific constant, s/m.

        """
        # TODO: How to handle this?
        if total_solids == 0.0:
            return 10.0
        dry_matter = manure_mass / total_solids
        if dry_matter >= 13.0:  # solid manure
            housing_specific_constant = 10.0
        elif dry_matter >= 8.0:  # semi-solid manure
            housing_specific_constant = 10.0
        elif dry_matter >= 5.0:  # slurry manure
            housing_specific_constant = 19.0
        else:  # liquid manure
            housing_specific_constant = 4.1
        return housing_specific_constant

    @classmethod
    def _calc_barn_resistance(cls, temp: float,
                              hsc=GasEmissionConstants.DEFAULT_HOUSING_SPECIFIC_CONSTANT_FOR_HOUSING) -> float:
        """
        Calculate barn resistance.

        Parameters
        ----------
        temp : float
            Temperature, :math:`^{\circ}C`.
        hsc : float, optional
            Housing specific constant, s/m.

        Returns
        -------
        float
            Barn resistance, s/m.

        """
        return hsc * (1 - 0.027 * (20.0 - temp))

    @classmethod
    def _calc_Kh(cls, temp: float) -> float:
        """
        Calculate Henry's constant.

        Parameters
        ----------
        temp : float
            Temperature in Kelvin, K.

        Returns
        -------
        float
            Henry's constant, M/atm.


        """
        return 10 ** (1478 / temp - 1.69)

    @classmethod
    def _calc_Ka(cls, temp: float, pH: float) -> float:
        """
        Calculate acid dissociation constant.

        Parameters
        ----------
        temp : float
            Temperature in Kelvin, K.
        pH : float
            Manure acidity, dimensionless.

        Returns
        -------
        float
            Acid dissociation constant, dimensionless.

        """
        return 1 + 10 ** (0.09018 + 2729.9 / temp - pH)

    @classmethod
    def _calc_Q(cls, temp: float, pH: float) -> float:
        """
        Calculate Q, the equilibrium coefficient for ammonia in the air.

        Parameters
        ----------
        temp : float
            Temperature in Kelvin, K.
        pH : float
            Manure acidity, dimensionless.

        Returns
        -------
        float
            Q, the equilibrium coefficient for ammonia in the air, dimensionless.

        """
        Kh = cls._calc_Kh(temp)
        Ka = cls._calc_Ka(temp, pH)
        return Kh * Ka

    @classmethod
    def _convert_temp_celsius_to_kelvin(cls, temp: float) -> float:
        """
        Convert temperature in Celsius to Kelvin.

        Parameters
        ----------
        temp : float
            Temperature in Celsius, :math:`^{\circ}C`.

        Returns
        -------
        float
            Temperature in Kelvin, K.

        """
        return temp + 273.15

    @classmethod
    def calc_methane_volume_via_Chen_equation(cls, manure_total_volatile_solids: float,
                                              hydraulic_retention_time: int) -> float:
        """
        Calculate methane generation volume using the Chen-Hashimoto equation.

        Parameters
        ----------
        manure_total_volatile_solids : float
            Total volatile solids, kg.
        hydraulic_retention_time : int
            Hydraulic retention time, days.

        Returns
        -------
        float
            Methane generation volume, :math:`m^3`.

        """
        return (GasEmissionConstants.METHANE_POTENTIAL_Go *
                (1 - GasEmissionConstants.CHEN_HASHIMOTO_KINETIC_CONSTANT_KCH /
                 (hydraulic_retention_time * GasEmissionConstants.SPECIFIC_GROWTH_RATE +
                  GasEmissionConstants.CHEN_HASHIMOTO_KINETIC_CONSTANT_KCH - 1)) *
                manure_total_volatile_solids * GeneralConstants.GRAMS_TO_KG)

    @classmethod
    def calc_biogas_energy_content(cls, methane_volume: float) -> float:
        """
        Calculate biogas energy content.

        Parameters
        ----------
        methane_volume : float
            Methane generation volume, :math:`m^3`.

        Returns
        -------
        float
            Biogas energy content, MJ.

        """
        return methane_volume * GasEmissionConstants.METHANE_DENSITY * GasEmissionConstants.METHANE_ENERGY_DENSITY

    @classmethod
    def calc_methane_emission_for_anaerobic_lagoon(cls, volatile_solids: float) -> float:
        """
        Calculate methane emissions from anaerobic lagoon.

        Parameters
        ----------
        volatile_solids : float
            Volatile solids, kg.

        Returns
        -------
        float
            Methane emissions from anaerobic lagoon, kg CH4-N/day.

        """
        constants = GasEmissionConstants
        return volatile_solids * constants.Bo * constants.MCF * constants.MS * constants.METHANE_FACTOR

    @classmethod
    def _calc_compost_nitrification_rate(cls,
                                         compost_ammonium_concentration: float,
                                         temperature_factor: float,
                                         compost_moisture_factor: float,
                                         compost_pH_factor: float) -> float:
        """
        Calculate the rate of nitrification in compost.

        The equation used for the calculation is as follows:

        .. math::

            R_{NO_3} = K_{max} \cdot N_{NH_4} \cdot F_{temp} \cdot F_{wfp} \cdot F_{pH}

        where:

            :math:`R_{NO_3}` = compost nitrification rate, :math:`g \, N/m^2 \cdot day`

            :math:`K_{max}` = maximum fraction of ammonium concentration in the compost nitrified, dimensionless

            :math:`N_{NH_4}` = ammonium concentration in the compost, :math:`g \, N/m^3`

            :math:`F_{temp}` = factor for the effect of temperature, dimensionless

            :math:`F_{wfp}` = factor for the effect of compost moisture, dimensionless

            :math:`F_{pH}` = factor for the effect of compost pH, dimensionless

        Parameters
        ----------
        compost_ammonium_concentration : float
            Ammonium concentration in the compost, :math:`g \, N/m^3`.
        temperature_factor : float
            Factor for the effect of temperature, dimensionless.
        compost_moisture_factor : float
            Factor for the effect of compost moisture, dimensionless.
        compost_pH_factor : float
            Factor for the effect of compost pH, dimensionless.

        Returns
        -------
        float
            Compost nitrification rate, :math:`g \, N/m^2 \cdot day`.

        """

        K_max = GasEmissionConstants.MAX_COMPOST_AMMONIUM_CONCENTRATION_FRACTION
        return K_max * compost_ammonium_concentration * temperature_factor * compost_moisture_factor * compost_pH_factor

    @classmethod
    def _calc_nitrification_emission(cls, nitrified_fraction: float, compost_nitrification_rate: float) -> float:
        """
        Calculate the emission of nitrous oxide (:math:`N_2O`) from nitrification in compost.

        The equation used for the calculation is as follows:

        .. math::

            E_{N_{2}O,soil,N} = f_{nitrified \, N} \cdot R_{NO_3} \cdot F_{N,conv}

        where:

            :math:`f_{nitrified \, N}` = fraction of nitrified `N` lost as :math:`N_2O` flux, :math:`g \, N/g \, N_{2}O`

            :math:`R_{NO_3}` = compost nitrification rate, :math:`g \, N/m^2 \cdot day`

            :math:`F_{N,conv}` = nitrification conversion factor, :math:`(kg \, N_{2}O/ha \cdot day) / (g \, N/m^2 \cdot day) = 15.7`

        Parameters
        ----------
        nitrified_fraction : float
            The fraction of nitrified nitrogen that is lost as :math:`N_2O` flux. Should be between 0 and 1.
        compost_nitrification_rate : float
            The rate at which nitrogen is nitrified in the compost, :math:`g \, N/m^2 \cdot day`.

        Returns
        -------
        float
            The estimated emission of :math:`N_2O` from nitrification in compost, :math:`kg \, N_{2}O/ha \cdot day`.

        """

        return nitrified_fraction * compost_nitrification_rate * GasEmissionConstants.NITRIFICATION_CONVERSION_FACTOR

    @classmethod
    def _calc_compost_respiration_factor(cls, compost_carbon_dioxide_flux: float):
        """
        Calculate the factor for the effect of compost respiration on the emission of nitrous oxide (:math:`N_2O`)
        due to denitritication.

        The equation used for the calculation is as follows:

        .. math::

            F_{d, CO_2} = 0.1 \\cdot C_{CO_2}^{1.3}  \\quad (\\text{M.1.B.5})

        where:

            :math:`F_{d, CO_2}` = factor for the effect of compost respiration on the emission of :math:`N_2O` due to
            denitrification, :math:`\mu g \, N/g \, compost \cdot day`

            :math:`C_{CO_2}` = compost carbon dioxide flux, :math:`\mu g \, C/g \, compost`

        Parameters
        ----------
        compost_carbon_dioxide_flux : float
            The flux of carbon dioxide from compost, :math:`\mu g \, C/g \, compost`.

        Returns
        -------
        float
            The factor for the effect of compost respiration on the emission of :math:`N_2O` due to denitrification,
            dimensionless.

        """
        return 0.1 * (compost_carbon_dioxide_flux ** 1.3)

    @classmethod
    def _calc_compost_moisture_factor(cls, pore_space: float, controlling_factor: float) -> float:
        """
        Calculate the factor for the effect of compost moisture on the emission of nitrous oxide (:math:`N_2O`) due to
        denitrification.

        The equation used for the calculation is as follows:

        .. math::

            F_{f,wfps} = 0.45 + \\frac{\\tan^{-1}(0.6 \\pi \\cdot (0.1 w_{wfps} - a))}{\\pi}  \\quad (\\text{M.1.B.6})

        where:

            :math:`F_{f,wfps}` = factor for the effect of compost moisture on the emission of :math:`N_2O` due to
            denitrification, dimensionless

            :math:`w_{wfps}` = water-filled pore space, %

            :math:`a` = compost moisture content controlling factor, dimensionless


        Parameters
        ----------
        pore_space : float
            Water-filled pore space, %.
        controlling_factor : float
            Compost moisture content controlling factor, dimensionless.

        Returns
        -------
        float
            The factor for the effect of compost moisture on the emission of :math:`N_2O` due to denitrification,
            dimensionless.
        """

        return 0.45 + (math.atan(0.6 * math.pi * (0.1 * pore_space - controlling_factor)) / math.pi)

    @classmethod
    def _calc_compost_moisture_content_controlling_factor(cls, interaction_term: float, carbon_dioxide_flux: float):
        """
        Calculate the compost moisture content controlling factor.

        The equation used for the calculation is as follows:

        .. math::

            a = 9.0 - M \\cdot C_{CO_2} \\quad (\\text{M.1.B.7})

        where:
            :math:`a` = compost moisture content controlling factor, dimensionless

            :math:`M` = interaction between compost moisture and compost respiration, dimensionless

            :math:`C_{CO_2}` = compost carbon dioxide flux, :math:`\mu g \, C/g \, compost`

        Parameters
        ----------
        interaction_term : float
            The interaction between compost moisture and compost respiration, dimensionless.
        carbon_dioxide_flux : float
            The flux of carbon dioxide from compost, :math:`\mu g \, C/g \, compost`.

        Returns
        -------
        float
            The compost moisture content controlling factor, dimensionless.
        """

        return 9.0 - interaction_term * carbon_dioxide_flux

    @classmethod
    def _calc_compost_moisture_and_respiration_interaction(cls, gas_diffusivity_coefficient: float) -> float:
        """
        Calculate the interaction between compost moisture and compost respiration.

        The equation used for the calculation is as follows:

        .. math::

            M = 0.145 - 1.25 \\cdot \\min(0.113, D_{fc}) \\quad (\\text{M.1.B.8})

        where:
            :math:`M` = interaction between compost moisture and compost respiration, dimensionless

            :math:`D_{fc}` = gas diffusivity coefficient, dimensionless

        Parameters
        ----------
        gas_diffusivity_coefficient : float
            Gas diffusivity coefficient, dimensionless.

        Returns
        -------
        float
            The interaction between compost moisture and compost respiration, dimensionless.

        Examples
        --------
        >>> GasEmissions._calc_compost_moisture_and_respiration_interaction(0.1)
        0.01999999999999999

        >>> GasEmissions._calc_compost_moisture_and_respiration_interaction(0.2)
        0.0037499999999999756
        """

        return 0.145 - 1.25 * min(0.113, gas_diffusivity_coefficient)
