from typing import Any, Dict, List, Set, Tuple

from RUFAS.general_constants import GeneralConstants
from RUFAS.input_manager import InputManager
from RUFAS.routines.animal.animal_typed_dicts import AnimalBaseInitArgsTypedDict
from RUFAS.routines.animal.life_cycle.animal_events import AnimalEvents
from RUFAS.routines.animal.life_cycle.body_weight_history import BodyWeightHistory
from RUFAS.routines.animal.life_cycle.lactation_curve import LactationCurve
from RUFAS.routines.animal.life_cycle.pen_history import PenHistory
from RUFAS.routines.animal.ration.amino_acid import EssentialAminoAcidRequirements
from RUFAS.rufas_time import RufasTime


class AnimalBase:
    config: Dict[str, Any] = {}
    nutrients = None
    lactation_curve = None

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

    @classmethod
    def setup_lactation_curve_parameters(cls, time: RufasTime) -> None:
        """Initializes the LactationCurve class attribute."""
        cls.lactation_curve = LactationCurve(time)

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
                        args.net_merit: The net merit value that represents the animal's genetic value in US Dollars.
        """
        self.id = args["id"]
        self.breed = args["breed"]
        self.birth_date: str = args["birth_date"]
        self.days_born = args["days_born"]
        self.semen_used = self.config["semen_type"]
        self.culled = False
        self.do_not_breed = False
        self.body_weight_history: List[BodyWeightHistory] = []
        self.events = AnimalEvents()
        self.pen_history: List[PenHistory] = []
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
        self.essential_amino_acid_requirement: EssentialAminoAcidRequirements = EssentialAminoAcidRequirements(
            histidine=0.0,
            isoleucine=0.0,
            leucine=0.0,
            lysine=0.0,
            methionine=0.0,
            phenylalanine=0.0,
            threonine=0.0,
            thryptophan=0.0,
            valine=0.0,
        )
        self.sold_at_day: int | None = None
        self.net_merit: float = args.get("net_merit", 0.0)
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

    def update_pen_history(self, curr_pen: int, curr_day: int, classes_in_pen: Set[str]) -> None:
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
        last_pen = self.pen_history[-1]["pen"] if len(self.pen_history) > 0 else None
        if last_pen is None or last_pen != curr_pen:
            self.pen_history.append(
                PenHistory(start_date=curr_day, end_date=curr_day, pen=curr_pen, classes_in_pen=list(classes_in_pen))
            )
        else:  # last_pen == curr_pen
            self.pen_history[-1]["end_date"] = curr_day
            self.pen_history[-1]["classes_in_pen"] = list(classes_in_pen)

    def update_body_weight_history(self, sim_day: int) -> None:
        """
        Updates the animal's body weight history by appending a
        BodyWeightHistory object to the list.

        Args:
            sim_day: simulation day
        """
        self.body_weight_history.append(
            BodyWeightHistory(simulation_day=sim_day, days_born=self.days_born, body_weight=self.body_weight)
        )
