from RUFAS.routines.animal.animal_typed_dicts import AnimalBaseInitArgsTypedDict
from RUFAS.routines.animal.life_cycle.animal_events import AnimalEvents
from RUFAS.routines.animal.life_cycle.body_weight_history import BodyWeightHistory
from RUFAS.routines.animal.life_cycle.pen_history import PenHistory
from RUFAS.input_manager import InputManager
import numpy as np
from scipy.integrate import quad


im = InputManager()
from RUFAS.general_constants import GeneralConstants
from typing import Tuple


class AnimalBase:
    config = {}
    nutrients = None
    lactation_parameters = {}

    @staticmethod
    def set_nutrient_list(nutrients):
        AnimalBase.nutrients = nutrients

    @staticmethod
    def set_config(config):
        im = InputManager()
        AnimalBase.config = config
        AnimalBase.config["nutrient_standard"] = im.get_data("config.nutrient_standard")
        AnimalBase.config["breed"] = im.get_data("animal.herd_information.breed")
        AnimalBase.config["ration"] = im.get_data("animal.ration")

    @staticmethod
    def get_t_values(start=1, end=305, step=1):
        return np.arange(start, end, step)

    @staticmethod
    def get_y_values_wood_curve(t, parameter_a, parameter_b, parameter_c):
        return parameter_a * np.power(t, parameter_b) * np.exp(-1 * parameter_c * t)

    @staticmethod
    def calc_integral_wood_curve(parameter_a, parameter_b, parameter_c):
        result, _ = quad(AnimalBase.get_y_values_wood_curve, 1, 305, args=(parameter_a, parameter_b, parameter_c))
        return result

    @staticmethod
    def get_wood_parameters(
        lactation_group=None, year=None, month=None, region=None, milking_frequency=None, MY_305d=None
    ):
        parameter_a = 19.9
        parameter_b = 24.7 * 1e-2
        parameter_c = 33.76 * 1e-4
        t = AnimalBase.get_t_values()

        adjustment_dict = im.get_data("lactation.adjustment_dict")

        farm_specific = {}
        farm_specific["parity"] = lactation_group
        farm_specific["year"] = year
        farm_specific["month"] = month
        farm_specific["region"] = region
        farm_specific["milking_frequency"] = milking_frequency

        for category in ["parity", "year", "month", "region", "milking_frequency"]:
            if farm_specific[category]:
                print(category)
                adjustment_applied = False
                x = 0
                while x < len(adjustment_dict[category]) and (not adjustment_applied):
                    if adjustment_dict[category][x][category] == farm_specific[category]:
                        parameter_a += adjustment_dict[category][x]["adjustments"][0]
                        parameter_b += adjustment_dict[category][x]["adjustments"][1] * 1e-2
                        parameter_c += adjustment_dict[category][x]["adjustments"][2] * 1e-4
                        adjustment_applied = True

                        print(adjustment_dict[category][x][category])
                        print(farm_specific[category])

                    x = x + 1

        # for category in [lactation_group, year, month, region, milking_frequency]:
        #     if category:
        #         parameter_a += adjustment_dict[category][0]
        #         parameter_b += adjustment_dict[category][1] * 1e-2
        #         parameter_c += adjustment_dict[category][2] * 1e-4

        if MY_305d == None:
            MY_305d = AnimalBase.calc_integral_wood_curve(parameter_a, parameter_b, parameter_c)
            # y = AnimalBase.get_y_values_wood_curve(t, parameter_a, parameter_b, parameter_c)
            return parameter_a, parameter_b, parameter_c, MY_305d

        else:
            min_diff = float("inf")
            parameter_a_best_estimate = 0
            MY_305d_best_estimate = 0

            for parameter_a_error in np.arange(-10, 10, 0.01):
                parameter_a_vary = parameter_a + parameter_a_error
                MY_305d_vary = AnimalBase.calc_integral_wood_curve(parameter_a_vary, parameter_b, parameter_c)
                if abs(MY_305d_vary - MY_305d) < min_diff:
                    min_diff = abs(MY_305d_vary - MY_305d)
                    parameter_a_best_estimate = parameter_a_vary
                    MY_305d_best_estimate = MY_305d_vary
            return parameter_a_best_estimate, parameter_b, parameter_c, MY_305d_best_estimate

    @staticmethod
    def set_lactation_curve_parameters():
        region_dict = im.get_data("lactation.fips_region")

        year = im.get_data("config.end_date")[:4]
        if int(year) > 2016:
            year = "2016"

        FIPS_code = im.get_data("config.FIPS_county_code")
        FIPS_state_code = None
        if FIPS_code != None:
            FIPS_state_code = int(FIPS_code / 1000)
        region = None
        if FIPS_state_code != None:
            for code_region in region_dict:
                if code_region["code"] == FIPS_state_code:
                    region = code_region["region"]
                    print(str(FIPS_state_code))
                    print(region)
                    print(code_region["code"])
                    print(code_region["region"])

        annual_MY_lbs = im.get_data("animal.herd_information.annual_milk_yield_lbs")  # int or None
        parity_percentages = im.get_data("animal.herd_information.parity_percentages")  # list of 3 floats
        num_milking_cows = im.get_data("animal.herd_information.cow_num") * (305 / 365)

        milking_freq = im.get_data("animal.animal_config.management_decisions.cow_times_milked_per_day")
        if milking_freq >= 2.5:
            milking_freq = "3x/d"
        else:
            milking_freq = "2x/d"

        # calculate lactation group yield

        # Assuming Y = 1632 and Z = 2196 based on the given assumptions
        P2_MY305_adj = im.get_data("lactation.parity_milk_adjustments.MY305_P2_adjustment")
        P3_MY305_adj = im.get_data("lactation.parity_milk_adjustments.MY305_P3_adjustment")

        if annual_MY_lbs != None:
            total_avg_305 = annual_MY_lbs * 305 / (365 * num_milking_cows * 2.205)

            # Extracting percentage distribution for each lactation group
            # percent_P1 = parity_percentages[0] * 100
            percent_P2 = parity_percentages[1] * 100
            percent_P3 = parity_percentages[2] * 100

            # Solving for P1-305 using the provided equation
            P1_305 = total_avg_305 - percent_P2 * P2_MY305_adj / 100 - percent_P3 * P3_MY305_adj / 100

            # Calculating 305-day milk yield for each lactation group
            P2_305 = P1_305 + P2_MY305_adj
            P3_305 = P1_305 + P3_MY305_adj

        else:
            P1_305 = None
            P2_305 = None
            P3_305 = None

        # calculate parameters for each lactation group
        AnimalBase.lactation_parameters[1] = AnimalBase.get_wood_parameters(
            lactation_group="1", year=year, region=region, milking_frequency=milking_freq, MY_305d=P1_305
        )
        AnimalBase.lactation_parameters[2] = AnimalBase.get_wood_parameters(
            lactation_group="2", year=year, region=region, milking_frequency=milking_freq, MY_305d=P2_305
        )
        AnimalBase.lactation_parameters[3] = AnimalBase.get_wood_parameters(
            lactation_group="3", year=year, region=region, milking_frequency=milking_freq, MY_305d=P3_305
        )
        """ print("Params 1: " + str(AnimalBase.lactation_parameters[1]))
        print("Params 2: " + str(AnimalBase.lactation_parameters[2]))
        print("Params 3: " + str(AnimalBase.lactation_parameters[3]))"""

        # assign final values to dictionary
        # AnimalBase.lactation_parameters = None

    def __init__(self, args: AnimalBaseInitArgsTypedDict):
        """
        Initializes common parameters for all animals
        Args:
            args.breed: breed of the cow
            args.birth_date: the date of the simulation when the calf was born
            args.days_born: age of the animal
            arg.semen_used: semen used in the dam for the calf
            (optional: include the following to assign animal information)
                        args.birth_weight: the birth weight of the animal
                        args.body_weight: current body weight of the animal
                        args.wean_weight: the wean weight of the animal
                        args.mature_body_weight: the mature body weight of the animal
                        args.events: events of the animal
        """
        self.id = args["id"]
        self.breed = args["breed"]
        self.birth_date = args["birth_date"]
        self.days_born = args["days_born"]
        self.semen_used = self.config["semen_type"]
        self.culled = False
        self.do_not_breed = False
        self.body_weight_history = []
        self.events = AnimalEvents()
        self.pen_history = []
        self.daily_growth = 0.0
        self.nutrient_rqmts = {}
        self.set_default_nutrient_rqmts()
        self.dry_matter_intake = 0.0
        self.manure_excretion = {}
        self.ration_formulation = {"objective": 0.00}
        self.DMIest = 0.0
        self.DBW = 0.0
        self.p_animal = 0.0
        self.p_intake = 0.0
        self.p_conc_ration = 0.0
        self.p_excrt = 0.0
        self.birth_weight = 0.0
        self.body_weight = 0.0
        self.mature_body_weight = 0.0
        self.p_req = 0.0
        self.dP_reserves = 0.0
        self.p_excess = 0.0
        self.p_gest = 0.0
        self.p_growth = 0.0
        self.p_maint_feces = 0.0
        self.conceptus_weight = 0.0
        self.calf_birth_weight = 0.0
        self.tissue_changed = 0.0
        self.sold_at_day: int | None = None
        if "body_weight_history" in args:
            self.body_weight_history = args["body_weight_history"]
            self.pen_history = args["pen_history"]
        if "conceptus_weight" in args:
            self.conceptus_weight = args["conceptus_weight"]
        if "calf_birth_weight" in args:
            self.calf_birth_weight = args["calf_birth_weight"]

    def set_default_nutrient_rqmts(self):
        """
        Sets the default nutrient requirement values to be 0.
        """
        for key in self.nutrients:
            self.nutrient_rqmts[key] = {"op": "", "val": 0}

    def set_ration(self, ration, DMI):
        """
        Sets this animal's ration formulation.

        Args:
            ration: dictionary representing the calculated ration
            DMI: the dry matter intake from @ration
        """
        self.ration_formulation = ration
        self.dry_matter_intake = DMI

    def set_p_intake(self, p_intake: float, p_conc_ration: float) -> None:
        """
        Sets this animal's phosphorus intake.

        Parameters
        ----------
        p_intake : float
            The phosphorus intake (kilograms).
        p_conc_ration : float
            The concentration of P in the ration (% DM).
        """
        self.p_intake = p_intake * GeneralConstants.KG_TO_GRAMS
        self.p_conc_ration = p_conc_ration

    def daily_p_update(self) -> None:
        """
        Calculates this animal's daily phosphorus update.
        """
        # Amount of P in diet greater than animal requirements (A.1G.A.1)
        self.p_excess = max(self.p_intake - self.p_req, 0)

        # change in body P reserves (g), must be <= 0 (A.1G.A.2)
        dP_reserves_prev = self.dP_reserves

        if self.p_intake < self.p_req:
            self.dP_reserves = self.p_intake - self.p_req + self.dP_reserves
        elif self.p_intake >= self.p_req and self.dP_reserves < 0:
            self.dP_reserves = 0.7 * self.p_excess + self.dP_reserves
        else:
            self.dP_reserves = 0

        # amount of P in the animal (A.1G.A.3)
        self.p_animal = self.p_animal + self.p_gest + self.p_growth + (self.dP_reserves - dP_reserves_prev)

    def calc_base_manure(self) -> Tuple[float, float]:
        """
        Calculates the values needed for animal class manure calculations.

        Returns
        -------
        Tuple[float, float]
            p_urine: amount of P required for urine production (g)
            p_feces_excrt: amount of P excreted by an animal (g)
        """

        # amount of P required for urine production (g) (A.1G.B.1)
        p_urine = 0.000002 * self.body_weight * GeneralConstants.KG_TO_GRAMS

        # excess P in the diet (g) (A.1G.A.1)
        self.p_excess = max(self.p_intake - self.p_req, 0)

        # amount of P excreted by an animal (g) (A.1G.B.2)
        if self.dP_reserves == 0 and self.p_intake >= self.p_req:
            p_feces_excrt = self.p_intake - self.p_req + self.p_maint_feces
        elif self.dP_reserves < 0 and self.p_intake >= self.p_req and self.p_excess >= (-1) * self.dP_reserves / 0.7:
            p_feces_excrt = self.p_intake - self.p_req + self.p_maint_feces + self.dP_reserves / 0.7
        else:
            p_feces_excrt = self.p_maint_feces

        return p_urine, p_feces_excrt

    def set_p_purchased(self) -> None:
        """
        Sets this animal's phosphorus value as a purchased animal.
        """
        # (A.1G.C.1) from P tracking
        self.p_animal = 0.0072 * self.body_weight * GeneralConstants.KG_TO_GRAMS

    def update_pen_history(self, curr_pen, curr_day, classes_in_pen):
        """
        Updates the animal's pen history by either appending to the existing
        history if the animal is in a different pen than it was the last time
        this method is called or modifying the last element in the pen_history
        list to reflect the current simulation day.

        Args:
            curr_pen: the pen that the animal is currently in
            curr_day: the current simulation day
            classes_in_pen: the classes in the animal's current pen
        """
        last_pen = self.pen_history[-1].pen if len(self.pen_history) > 0 else None
        if last_pen is None or last_pen != curr_pen:
            self.pen_history.append(PenHistory(curr_day, curr_day, curr_pen, list(classes_in_pen)))
        else:  # last_pen == curr_pen
            self.pen_history[-1].end_date = curr_day
            self.pen_history[-1].classes_in_pen = list(classes_in_pen)

    def update_body_weight_history(self, sim_day):
        """
        Updates the animal's body weight history by appending a
        BodyWeightHistory object to the list.

        Args:
            sim_day: simulation day
        """
        self.body_weight_history.append(BodyWeightHistory(sim_day, self.days_born, self.body_weight))
