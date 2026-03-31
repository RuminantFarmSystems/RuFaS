from typing import Any
from warnings import catch_warnings

from scipy.optimize import minimize

from RUFAS.biophysical.animal.milk.milk_production import MilkProduction
from RUFAS.general_constants import GeneralConstants
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.rufas_time import RufasTime
from RUFAS.units import MeasurementUnits
from RUFAS.util import Utility

"""
Constant that is used to determine whether cows are considered to be milking twice or thrice daily when determining how
to adjust the lactation curve parameters.
"""
MILKING_FREQUENCY_THRESHOLD = 2.5

"""
Constants used to scale the adjustments for Wood's m and n parameters, respectively, before using them to the adjust
parameters.
"""
M_ADJUSTMENT_SCALING_FACTOR = 1e-2
N_ADJUSTMENT_SCALING_FACTOR = 1e-4


"""
If user's input for parity 1, 2, and 3+ fractions of the milking herd are invalid (i.e. do not sum to 1), then the below
defaults will be used. Note that these defaults are ONLY used to adjust the lactation curve parameters, they are not
used at all to determine herd structure. These numbers are from Li et al, 2023.

References
----------
.. [1] Li, M., K. F. Reed, and V. E. Cabrera. "A time series analysis of milk productivity in US dairy states." Journal
of Dairy Science 106.9 (2023): 6232-6248.

"""
PARITY_1_DEFAULT_FRACTION_OF_MILKING_COWS = 0.386
PARITY_2_DEFAULT_FRACTION_OF_MILKING_COWS = 0.281
PARITY_3_DEFAULT_FRACTION_OF_MILKING_COWS = 0.333


"""These constants regulate the range used to fit Wood's l lactation parameter to estimated 305 day milk yields."""
UPPER_BOUND = 20
LOWER_BOUND = -20


"""Defines the accepted error tolerance when checking that fractions of parity 1, 2 and 3+ milking cows sum to 1.0."""
ACCEPTABLE_PARITY_FRACTION_ERROR = 0.01


class LactationCurve:
    """
    Manages Wood's lactation curve parameters l, m, and n as they are used by the rest of the Animal module.

    Attributes
    ----------
    _om : OutputManager
        The OutputManager for this module to use.
    _parity_to_parameter_mapping : dict[int, dict[str, float]]
        Maps the parity (1, 2, and 3+) to the associated sets of l, m and n parameters.
    _parity_to_std_dev_mapping : dict[int, dict[str, float]]
        Maps parities (1, 2, and 3+) to the standard devations of Wood's l, m, and n parameters.

    """

    _om = OutputManager()
    _parity_to_parameter_mapping: dict[int, dict[str, float]] = {}
    _parity_to_std_dev_mapping: dict[int, dict[str, float]] = {}

    @classmethod
    def set_lactation_parameters(cls, time: RufasTime) -> None:
        """
        Calculates Wood's lactation curve parameters, adjusted based on the location, production, and management
        practices of the farm being simulated.

        Parameters
        ----------
        time : RufasTime
            RufasTime instance that manages time in the simulation.

        """
        im = InputManager()

        lactation_inputs: dict[str, Any] = im.get_data("lactation")
        all_year_adjustments: dict[str, dict[str, float]] = lactation_inputs["adjustments"]["year"]
        year_adjustments = cls._get_year_adjustments(all_year_adjustments, time)

        fips_code: int = im.get_data("config.FIPS_county_code")
        all_region_adjustments: dict[str, dict[str, float]] = lactation_inputs["adjustments"]["region"]
        region_mapping: dict[str, str] = lactation_inputs["state_to_region_mapping"]
        region_adjustments = cls._get_region_adjustments(all_region_adjustments, region_mapping, fips_code)

        animal_inputs: dict[str, Any] = im.get_data("animal")
        animal_milking_frequency: float = animal_inputs["animal_config"]["management_decisions"][
            "cow_times_milked_per_day"
        ]
        all_milking_frequency_adjustments: dict[str, dict[str, float]] = lactation_inputs["adjustments"][
            "milking_frequency"
        ]
        milking_frequency_adjustments = cls._get_milking_frequency_adjustments(
            all_milking_frequency_adjustments, animal_milking_frequency
        )

        parity_adjustments: dict[str, dict[str, float]] = lactation_inputs["adjustments"]["parity"]

        base_wood_parameter_l: float = lactation_inputs["parameter_mean_values"]["parameter_l_mean"]
        base_wood_parameter_m: float = lactation_inputs["parameter_mean_values"]["parameter_m_mean"]
        base_wood_parameter_n: float = lactation_inputs["parameter_mean_values"]["parameter_n_mean"]

        for parity, adjustments in parity_adjustments.items():
            cls._parity_to_parameter_mapping[int(parity)] = cls._calculate_adjusted_wood_parameters(
                base_wood_parameter_l,
                base_wood_parameter_m,
                base_wood_parameter_n,
                [adjustments, year_adjustments, region_adjustments, milking_frequency_adjustments],
            )

        cls._parity_to_std_dev_mapping = {
            1: lactation_inputs["parameter_standard_deviations"]["1"],
            2: lactation_inputs["parameter_standard_deviations"]["2"],
            3: lactation_inputs["parameter_standard_deviations"]["3"],
        }

        info_map: dict[str, Any] = {"class": cls.__name__, "function": "__init__"}
        annual_milk_yield: float = animal_inputs["herd_information"]["annual_milk_yield"]
        if annual_milk_yield is not None:
            cls._om.add_log(
                "Projected annual milk yield provided to simulation",
                "Using the annual milk yield input to fit lactation curve parameters.",
                info_map,
            )
            cls._adjust_lactation_curve_to_milk_yield(animal_inputs, lactation_inputs)
        else:
            cls._om.add_log(
                "Annual milk yield not provided to simulation",
                "Lactation curve parameters will not be fit to the target milk production.",
                info_map,
            )

        info_map["units"] = MeasurementUnits.UNITLESS
        for animal_parity, params in cls._parity_to_parameter_mapping.items():
            base_var_name = f"parity_{animal_parity}_lactation_curve_parameter_"
            for param, value in params.items():
                cls._om.add_variable(f"{base_var_name}_{param}", value, info_map)

    @classmethod
    def _get_year_adjustments(
        cls, year_adjustment_values: dict[str, dict[str, float]], time: RufasTime
    ) -> dict[str, float]:
        """Retrieves the appropriate adjustment values based on the end year of the simulation."""
        end_year = time.end_date.year

        info_map = {"class": cls.__name__, "function": cls._get_year_adjustments.__name__}
        if not 2006 <= end_year <= 2016:
            bounded_end_year = min(2016, max(2006, end_year))
            cls._om.add_warning(
                f"Lactation curve adjustments not available for simulation ending in {end_year}",
                f"Using adjustments for {bounded_end_year}.",
                info_map,
            )
            end_year = bounded_end_year

        return year_adjustment_values[str(end_year)]

    @classmethod
    def _get_region_adjustments(
        cls, region_adjustment_values: dict[str, dict[str, float]], region_mapping: dict[str, str], fips_code: int
    ) -> dict[str, float]:
        """Retrieves the appropriate adjustment values for the region being simulated."""
        state_fips_code = int(fips_code / 1000)

        region = region_mapping[str(state_fips_code)]

        return region_adjustment_values[region]

    @classmethod
    def _get_milking_frequency_adjustments(
        cls, milking_frequency_adjustments: dict[str, dict[str, float]], milking_frequency: float
    ) -> dict[str, float]:
        """Retrieves the lactation curve adjustment values for the milking frequency of cows in the simulation."""
        if milking_frequency < MILKING_FREQUENCY_THRESHOLD:
            frequency = "twice_daily"
        else:
            frequency = "thrice_daily"

        return milking_frequency_adjustments[frequency]

    @classmethod
    def _calculate_adjusted_wood_parameters(
        cls, l_param: float, m_param: float, n_param: float, adjustments: list[dict[str, float]]
    ) -> dict[str, float]:
        """
        Computes Wood's Lactation Curve parameters adjusted for different factors.

        Notes
        -----
        Parameter adjustments: [AN.MLK.1], [AN.MLK.2], [AN.MLK.3]

        Parameters
        ----------
        l_param : float
            Base value for Wood's l parameter (unitless).
        m_param : float
            Base value for Wood's m parameter (unitless).
        n_param : float
            Base value for Wood's n parameter (unitless).
        adjustments : list[dict[str, float]]
            List of adjustment sets, where each dictionary in the list represents the adjustments for a single factor
            (region, parity, etc.) and contains the keys "l", "m", and "n".

        Returns
        -------
        dict[str, float]
            Dictionary containing the adjusted Wood l, m, and n parameters.

        """
        l_param += sum([adjustment["l"] for adjustment in adjustments])
        m_param += sum([adjustment["m"] for adjustment in adjustments]) * M_ADJUSTMENT_SCALING_FACTOR
        n_param += sum([adjustment["n"] for adjustment in adjustments]) * N_ADJUSTMENT_SCALING_FACTOR

        return {"l": l_param, "m": m_param, "n": n_param}

    @classmethod
    def get_wood_parameters(cls, parity: int) -> dict[str, float]:
        """
        Adjusts the default lactation curve parameters based on farm-specific attributes.

        Parameters
        ----------
        parity : int
            The number of calves that a cow has had.

        Returns
        -------
        dict[str, float]
            Wood's parameters l, m, and n for the specified parity.

        """
        parity = min(3, parity)

        params = cls._parity_to_parameter_mapping[parity]
        std_deviations = cls._parity_to_std_dev_mapping[parity]
        return {
            "l": Utility.generate_random_number(params["l"], std_deviations["parameter_l_std_dev"]),
            "m": Utility.generate_random_number(params["m"], std_deviations["parameter_m_std_dev"]),
            "n": Utility.generate_random_number(params["n"], std_deviations["parameter_n_std_dev"]),
        }

    @classmethod
    def _adjust_lactation_curve_to_milk_yield(
        cls, animal_inputs: dict[str, Any], lactation_curve_inputs: dict[str, dict[str, Any]]
    ) -> None:
        """
        Adjust the lactation parameters using predicted milk yields for the different parities of cows on the farm.
        """
        num_milking_cows: int = (
            animal_inputs["herd_information"]["cow_num"] * animal_inputs["herd_information"]["milking_cow_fraction"]
        )
        annual_milk_yield: float = animal_inputs["herd_information"]["annual_milk_yield"]
        parity_1_percentage: float = animal_inputs["herd_information"]["parity_fractions"]["1"]
        parity_2_percentage: float = animal_inputs["herd_information"]["parity_fractions"]["2"]
        parity_3_percentage: float = (
            animal_inputs["herd_information"]["parity_fractions"]["3"]
            + animal_inputs["herd_information"]["parity_fractions"]["4"]
            + animal_inputs["herd_information"]["parity_fractions"]["5"]
        )
        parity_2_milk_yield_adjustment: float = lactation_curve_inputs["parity_milk_yield_adjustments"][
            "parity_2_305_day_milk_yield_adjustment"
        ]
        parity_3_milk_yield_adjustment: float = lactation_curve_inputs["parity_milk_yield_adjustments"][
            "parity_3_305_day_milk_yield_adjustment"
        ]

        milk_yield_305_day_by_parity = cls._estimate_305_day_milk_yield_by_parity(
            annual_milk_yield,
            num_milking_cows,
            parity_1_percentage,
            parity_2_percentage,
            parity_3_percentage,
            parity_2_milk_yield_adjustment,
            parity_3_milk_yield_adjustment,
        )

        param_milk_yield_paired_by_parity = [
            (cls._parity_to_parameter_mapping[1], milk_yield_305_day_by_parity["parity_1"]),
            (cls._parity_to_parameter_mapping[2], milk_yield_305_day_by_parity["parity_2"]),
            (cls._parity_to_parameter_mapping[3], milk_yield_305_day_by_parity["parity_3"]),
        ]
        for params, milk_yield in param_milk_yield_paired_by_parity:
            fitted_l_param = cls._fit_wood_l_param_to_milk_yield(params["l"], params["m"], params["n"], milk_yield)
            params["l"] = fitted_l_param

    @classmethod
    def _estimate_305_day_milk_yield_by_parity(
        cls,
        annual_milk_yield: float,
        num_milking_cows: int,
        parity_1_frac: float,
        parity_2_frac: float,
        parity_3_frac: float,
        parity_2_milk_yield_adjustment: float,
        parity_3_milk_yield_adjustment: float,
    ) -> dict[str, float]:
        """
        Calculates the 305-day milk yield for each lactation group based on total farm milk production.

        Notes
        -----
        Herd average 305-day milk yield: [AN.MLK.4]
        Parity specific 305-day milk yield: [AN.MLK.5], [AN.MLK.6], [AN.MLK.7]

        Parameters
        ----------
        annual_milk_yield : float
            Annual milk yield of the farm (kg).
        num_milking_cows : int
            Number of milking cows on the farm.
        parity_1_frac : float
            Fraction of cows on the farm that have a parity of 1.
        parity_2_frac : float
            Fraction of cows on the farm that have a parity of 2.
        parity_3_frac : float
            Fraction of cows on the farm that have a parity of 3 or more.
        parity_2_milk_yield_adjustment : float
            Factor used to adjust for parity 2 cows (unitless).
        parity_3_milk_yield_adjustment : float
            Factor used to adjust for parity 3 cows (unitless).

        Returns
        -------
        dict[str, float]
            Mapping of the parity (1, 2, 3+) to the estimated 305 day milk production of an individual cow of that
            parity (kg).

        """
        milk_yield_305_day_all_cows = annual_milk_yield * (305 / GeneralConstants.YEAR_LENGTH)
        milk_yield_305_day = milk_yield_305_day_all_cows / num_milking_cows

        parity_fractions_sum = sum([parity_1_frac, parity_2_frac, parity_3_frac])
        parity_fractions_difference = abs(1.0 - parity_fractions_sum)
        if parity_fractions_difference > ACCEPTABLE_PARITY_FRACTION_ERROR:
            cls._om.add_error(
                f"Fractions of milking cows that are parity 1, 2 and 3+ sum to {parity_fractions_sum}, not 1.0",
                f"Using {PARITY_1_DEFAULT_FRACTION_OF_MILKING_COWS}, {PARITY_2_DEFAULT_FRACTION_OF_MILKING_COWS} and "
                f"{PARITY_3_DEFAULT_FRACTION_OF_MILKING_COWS} as the fractions of parity 1, 2 and 3+ cows in the "
                "milking herd, respectively",
                {"class": cls.__name__, "function": cls._estimate_305_day_milk_yield_by_parity.__name__},
            )
            parity_1_frac = PARITY_1_DEFAULT_FRACTION_OF_MILKING_COWS
            parity_2_frac = PARITY_2_DEFAULT_FRACTION_OF_MILKING_COWS
            parity_3_frac = PARITY_3_DEFAULT_FRACTION_OF_MILKING_COWS
        elif ACCEPTABLE_PARITY_FRACTION_ERROR >= parity_fractions_difference > 0.0:
            cls._om.add_warning(
                f"Fractions of milking cows that are parity 1, 2 and 3+ sum to {parity_fractions_sum}, not 1.0, but the"
                f" difference is within the accepted tolerance of {ACCEPTABLE_PARITY_FRACTION_ERROR}",
                f"Will use {parity_1_frac}, {parity_2_frac} and {parity_3_frac} as the fractions of parity 1, 2, and 3+"
                " cows in the milking herd, respectively.",
                {"class": cls.__name__, "function": cls._estimate_305_day_milk_yield_by_parity.__name__},
            )

        parity_1_305_day_milk_yield = milk_yield_305_day / (
            parity_1_frac
            + parity_2_frac * parity_2_milk_yield_adjustment
            + parity_3_frac * parity_3_milk_yield_adjustment
        )
        parity_2_305_day_milk_yield = parity_1_305_day_milk_yield * parity_2_milk_yield_adjustment
        parity_3_305_day_milk_yield = parity_1_305_day_milk_yield * parity_3_milk_yield_adjustment

        return {
            "parity_1": parity_1_305_day_milk_yield,
            "parity_2": parity_2_305_day_milk_yield,
            "parity_3": parity_3_305_day_milk_yield,
        }

    @staticmethod
    def _calculate_305_day_milk_yield_error(l_param: float, m_param: float, n_param: float, milk_yield: float) -> float:
        """Calculates absolute difference between an estimated 305 day milk yield and a predetermined one."""
        return abs(MilkProduction.calc_305_day_milk_yield(l_param, m_param, n_param) - milk_yield)

    @classmethod
    def _fit_wood_l_param_to_milk_yield(
        cls, l_param: float, m_param: float, n_param: float, milk_yield: float
    ) -> float:
        """
        Modifies Wood's l parameter to best fit a given 305 day milk yield.

        Notes
        -----
        [AN.MLK.8]

        Parameters
        ----------
        l_param : float
            Wood's l lactation curve parameter.
        m_param : float
            Wood's m lactation curve parameter.
        n_param : float
            Wood's n lactation curve parameter.
        milk_yield : float
            305 day milk yield that Wood's l parameter will be fitted to (kg).

        Returns
        -------
        float
            Wood's l parameter adjusted to best fit the given milk yield.

        """

        bounds = [(max(l_param + LOWER_BOUND, 0.0), l_param + UPPER_BOUND)]

        with catch_warnings(record=True) as caught_warnings:
            minimized_result = minimize(
                cls._calculate_305_day_milk_yield_error, x0=l_param, args=(m_param, n_param, milk_yield), bounds=bounds
            )
            for warning in caught_warnings:
                cls._om.add_warning(
                    f"Captured warning during optimization of type {warning.category.__name__}",
                    f"{warning.message}. Warning generated in {warning.filename}",
                    {
                        "class": cls.__name__,
                        "function": cls._fit_wood_l_param_to_milk_yield.__name__,
                        "full_warning": warning,
                    },
                )
        l_param_best_fit: float = minimized_result.x[0]

        return l_param_best_fit
