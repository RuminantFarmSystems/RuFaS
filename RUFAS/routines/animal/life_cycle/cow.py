from __future__ import annotations

import collections
import math
from random import random
from typing import Dict, Any

import numpy as np

from RUFAS.output_manager import OutputManager
from RUFAS.routines.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.routines.animal.life_cycle import animal_constants as const
from RUFAS.general_constants import GeneralConstants
from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase
from RUFAS.routines.animal.life_cycle.heiferIII import HeiferIII
from RUFAS.routines.animal.life_cycle.repro_protocol_enums import (
    CowReproProtocolEnum,
    ReproStateEnum,
)
from RUFAS.routines.animal.life_cycle.repro_state_manager import ReproStateManager
from RUFAS.routines.animal.manure.dry_cow_manure_excretion import (
    manure_calculations as dry_manure_calculations,
)
from RUFAS.routines.animal.manure.lactating_cow_manure_excretion import (
    manure_calculations as lactating_manure_calculations,
)
from RUFAS.routines.animal.ration.animal_requirements import AnimalRequirements
from RUFAS.routines.animal.types.preg_check_config import PregCheckConfig
from RUFAS.routines.animal.life_cycle.lactation_curve import LactationCurve

om = OutputManager()


class MilkProductionHistory:
    def __init__(self, sim_day: int, days_in_milk: int, milk_prod: float, days_born: int) -> None:
        self.simulation_day: int = sim_day
        self.days_in_milk: int = days_in_milk
        self.milk_production: float = milk_prod
        self.days_born: int = days_born


class Cow(HeiferIII):
    stats = collections.defaultdict(int)

    def __init__(self, args: dict[str, Any]):
        """
        Initialize a cow from a heifer.

        Parameters
        ----------
        args : dict[str, Any]
            args.id: id of the animal
            args.breed: breed of the animal
            args.birth_date: the date of the simulation when the calf was born
            args.daysBorn: age of the animal
            args.repro_sub_protocol: string indicating the sub-type of the reproduction protocol being used. Can be
                "5dCG2P", "5dCGP", "2P", "CP" or "N/A".
            args.tai_method_h: timed-AI protocols used for
                reproduction programs, three of them: 5dCG2P,
                5dCGP, and user-defined
            args.synch_ed_method_h: synch ed protocols used for
                reproduction programs, two of them: 2P and CP
            args.repro_program: reproduction program used in cow,
                    three of them: ED, TAI, and ED-TAI programs
            args.presynch_method: presynch protocols used for presynch
                programs, four of them: Presynch, Double OvSynch, G6G,
                and user_defined
            args.tai_method_c: timed-AI protocols used for reproduction
                programs, five of them: OvSynch 56, OvSynch 48, CoSynch 72,
                5d CoSynch, and user-defined
            args.resynch_method: resynch protocols used for resynch
                programs, three of them: TAIafterPD, TAIbeforePD,
                and PGFatPD
            (optional: include the following to assign cow information)
            args.birth_weight: the birth weight of the animal
            args.body_weight: current body weight of the animal
            args.wean_weight: the wean weight of the animal
            args.mature_body_weight: the mature body weight of the animal
            args.events: events of the animal
            args.estrus_count : number of estrus during ED program
            args.estrus_day: the age when the heifer is estrus in ED program
            args.tai_program_start_day_h: start day for heifers in TAI program
            args.synch_ed_program_start_day_h: start day for heifers in synch_ED program
            args.synch_ed_estrus_day: the age when the heifer is estrus in synch_ED program
            args.synch_ed_stop_day: the age the the synch protocol stop for this round
            args.conception_rate: conception rate associated with repro programs and protocols
            args.ai_day: the age of animal for scheduled AI
            args.abortion_day: the age of the animal when abortion happens
            args.days_in_preg: days science pregnancy
            args.gestation_length: the projected gestation
            args.p_gest_for_calf
            args.days_in_milk: cow's current day in milk
            args.parity: parity of the cow
            args.calving_interval: cow's most recent calving interval
            args.lactation_curve: lactation curve model choice

        Notes
        -----
        When a cow is initialized, it is checked to see whether it is already pregnant. If it is, it is immediately
        entered in the `PREGNANT` repro state.

        """
        super().__init__(args)

        # current hard-coded values necessary for nutrient requirement
        # calculations
        self.BCS = 3.5  # body condition score
        self.CP_milk = AnimalModuleConstants.MILK_CRUDE_PROTEIN
        self.lactose_milk = AnimalModuleConstants.MILK_LACTOSE
        self.mPrt = 0.0

        self.DVD = 0  # daily vertical distance, km
        self.DHD = 0  # daily horizontal distance, km
        self.CI = 0  # calving interval, days
        self.CI_history = []
        self.BW_at_calving = 0  # weight of cow when she gives birth
        self.calf_birth_weight = args["calf_birth_weight"]  # calf birth weight
        self.daily_growth = 0  # change in body weight, kg
        self.calves = 0
        self.calving_to_preg_time = 0
        self.milking = False
        self.days_in_milk = 0
        self.estimated_daily_milk_produced = 0.0
        # Milk production as estimated from the lactation curve, kg/day.
        self.milk_fat_kg = 0.0
        # Milk fat content estimate, kg/day.
        self.milk_protein_kg = 0.0
        # Milk protein content estimate, kg/day.
        self.milk_production_reduction = 0.0
        self.latest_milk_production_305days = 0.0
        self.single_acc_milk_prod = 0.0
        self.future_cull_date = 0
        self.future_death_date = 0
        self.cull_reason = None
        self.repro_program = args["repro_program"]
        self.first_ai = False
        self.fat_percent = 0.0

        # TAI params
        self.presynch_method = args["presynch_method"]
        self.tai_method_c = args["tai_method_c"]
        self.presynch_program_start_day = 0
        self.tai_program_start_day_c = 0
        self.resynch_method = args["resynch_method"]

        self._num_conception_rate_decreases: int = 0
        self._repro_state_manager: ReproStateManager = ReproStateManager()
        if self.is_pregnant:
            self._repro_state_manager.enter(ReproStateEnum.PREGNANT)

        self.wood_l = 0
        self.wood_m = 0
        self.wood_n = 0

        self.lactation_curve = "wood"
        self.milk_production_history = []
        self.breed_index = 0
        self.parity_index = 0
        self.set_breed_index()

        # grouping nutrition requirement values
        # Required net energy density (Mcal/kg of DM)
        self.DNED_req = 0
        # Required Metabolizing Protein Density (g/kg of DM)
        self.DMPD_req = 0

        if "days_in_milk" in args:
            self.days_in_milk = args["days_in_milk"]
            self.milking = self.days_in_milk != 0
            self.calves = args["parity"]
            self.CI = args["calving_interval"]
            self.set_parity_index()
            self.set_lactation_curve_params()

    def get_cow_values(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "breed": self.breed,
            "birth_date": self.birth_date,
            "days_born": self.days_born,
            "birth_weight": self.birth_weight,
            "body_weight": self.body_weight,
            "wean_weight": self.wean_weight,
            "events": str(self.events),
            "repro_program": self.repro_program,
            "repro_sub_protocol": self.repro_sub_protocol,
            "mature_body_weight": self.mature_body_weight,
            "estrus_count": self.estrus_count,
            "estrus_day": self.estrus_day,
            "tai_program_start_day_h": self.tai_program_start_day_h,
            "synch_ed_program_start_day_h": self.synch_ed_program_start_day_h,
            "synch_ed_estrus_day": self.synch_ed_estrus_day,
            "synch_ed_stop_day": self.synch_ed_stop_day,
            "conception_rate": self.conception_rate,
            "ai_day": self.ai_day,
            "abortion_day": self.abortion_day,
            "days_in_preg": self.days_in_preg,
            "gestation_length": self.gestation_length,
            "p_gest_for_calf": self.p_gest_for_calf,
            "calf_birth_weight": self.calf_birth_weight,
            "presynch_method": self.presynch_method,
            "tai_method_c": self.tai_method_c,
            "resynch_method": self.resynch_method,
            "days_in_milk": self.days_in_milk,
            "parity": self.calves,
            "calving_interval": self.CI,
        }

    def get_replacement_values(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "breed": self.breed,
            "birth_date": self.birth_date,
            "days_born": self.days_born,
            "birth_weight": self.birth_weight,
            "body_weight": self.body_weight,
            "wean_weight": self.wean_weight,
            "events": str(self.events),
            "repro_program": self.repro_program,
            "repro_sub_protocol": self.repro_sub_protocol,
            "mature_body_weight": self.mature_body_weight,
            "estrus_count": self.estrus_count,
            "estrus_day": self.estrus_day,
            "tai_program_start_day_h": self.tai_program_start_day_h,
            "synch_ed_program_start_day_h": self.synch_ed_program_start_day_h,
            "synch_ed_estrus_day": self.synch_ed_estrus_day,
            "synch_ed_stop_day": self.synch_ed_stop_day,
            "conception_rate": self.conception_rate,
            "ai_day": self.ai_day,
            "abortion_day": self.abortion_day,
            "days_in_preg": self.days_in_preg,
            "gestation_length": self.gestation_length,
            "p_gest_for_calf": self.p_gest_for_calf,
            "calf_birth_weight": self.calf_birth_weight,
            "presynch_method": self.presynch_method,
            "tai_method_c": self.tai_method_c,
            "resynch_method": self.resynch_method,
        }

    @property
    def is_lactating(self) -> bool:
        """
        Check if the cow is lactating.

        Returns
        -------
        bool
            True if the cow is lactating, False otherwise.

        """

        return self.milking

    @property
    def is_dry(self) -> bool:
        """
        Check if the cow is in the dry state.

        Returns
        -------
        bool
            True if the cow is in the dry state, False otherwise.

        """

        return not self.is_lactating

    def set_breed_index(self) -> None:
        """Sets the cow's breed index for use in the lactation curve parameter calculation"""
        if self.breed == "HO":
            self.breed_index = 0
        if self.breed == "JE":
            self.breed_index = 1

    def set_parity_index(self) -> None:
        """Sets the cow's parity index for use in the lactation curve parameter calculation"""
        self.parity_index = 2 if self.calves - 1 > 2 else self.calves - 1

    def set_lactation_curve_params(self) -> None:
        """
        Sets cow's lactation curve parameters based on cow's lactation curve attribute.
        Currently only set up for wood model.
        """
        if self.lactation_curve == "wood":

            parity_key = self.parity_index
            # this is a temporary fix for the negative parity_index issue
            #'parity_key' should not be needed if self.parity_index is always an int between 0 and 2
            if parity_key < 0:
                parity_key = 0

            lactation_curve = LactationCurve()
            lactation_parameters = lactation_curve.set_lactation_curve_parameters()
            self.wood_l = self.determine_param_value(
                lactation_parameters[parity_key][0],
                AnimalBase.config["wood_l_std"][self.breed_index][self.parity_index],
            )
            self.wood_m = self.determine_param_value(
                lactation_parameters[parity_key][1],
                AnimalBase.config["wood_m_std"][self.breed_index][self.parity_index],
            )
            self.wood_n = self.determine_param_value(
                lactation_parameters[parity_key][2],
                AnimalBase.config["wood_n_std"][self.breed_index][self.parity_index],
            )

    def calculate_daily_milk_produced(self) -> float:
        """Returns a float calculation of the milk produced based on a cow's lactation curve parameters"""
        if self.lactation_curve == "wood":
            return (
                self.wood_l * math.pow(self.days_in_milk, self.wood_m) * math.exp((0 - self.wood_n) * self.days_in_milk)
            )
        if self.lactation_curve == "milkbot":
            return (
                AnimalBase.config["a"]
                * (1 - math.exp((AnimalBase.config["c"] - self.days_in_milk) / AnimalBase.config["b"]) / 2)
                * math.exp((0 - AnimalBase.config["d"]) * self.days_in_milk)
            )
        return 0.0

    def update_milk_production_history(self, sim_day: int) -> None:
        """
        Updates the animal's milk production history by appending a
        MilkProductionHistory object to the list.

        If milk production history has already been updated for the day,
        the most recent entry is deleted before appending the latest values.
        Once a cow reaches 305 days in milk, latest_milk_production_305days is updated.

        Parameter
        ---------
        sim_day : int
            Day of simulation.

        """
        if len(self.milk_production_history) > 0 and self.milk_production_history[-1].simulation_day == sim_day:
            del self.milk_production_history[-1]

        self.milk_production_history.append(
            MilkProductionHistory(
                sim_day,
                self.days_in_milk,
                self.estimated_daily_milk_produced,
                self.days_born,
            )
        )

        if self.days_in_milk == 305 and len(self.milk_production_history) > 305:
            milk_history = [day.milk_production for day in self.milk_production_history[-305:]]
            self.latest_milk_production_305days = np.sum(milk_history)

    @staticmethod
    def determine_param_value(mean: float, std: float) -> float:
        """
        Determine parameter value distribution for lactation curve model
        parameters.
        Args:
            mean: mean of the parameter value for l, m, n in wood's model
            std: standard deviation of the parameter value for l, m, n in
                wood's model
        Returns: a random value draw from distribution of parameters
        """
        return np.random.normal(mean, std)

    def milking_update(self, sim_day: int, calving_interval: int | float) -> None:
        """
        Updates milking status for lactating cows, using breed and parity
        to estimate daily milk production from specific lactation curves
        (following Wood's curve model).

        Parameters
        -------
        sim_day : int
            The current simulation day.
        calving_interval : int | float
            calving_interval is an int (user input calving interval) if the
            value of animal_config["use_input_calving_interval"] exists
            and is True; otherwise, it is a float (average herd calving
            interval). See logic in _set_avg_CI in lifecycle.py.

        Notes
        ------
        - The targeted lactation curve is set at the beginning of each lactation,
        and the variance can be added after adjusted by the nutrition submodel.
        - Currently, the variables for fat percent, FCM,
        body weight during lactation, and dry matter intake
        are coded here with equations containing hard-coded parameters
        just to validate the simulation model. They indicate places for future adjustment
        in regards to ration formulation and economics calculation.

        References
        ------
        [1] [A.1A.C.33]-[A.1A.C.34]
        [2] M. Li, G.J.M. Rosa, K.F. Reed, V.E. Cabrera,
        Investigating the effect of temporal, geographic, and management
        factors on US Holstein lactation curve parameters,
        Journal of Dairy Science, Volume 105, Issue 9, 2022,
        Pages 7525-7538, ISSN 0022-0302.
        """
        if self.days_in_preg == AnimalBase.config["days_in_preg_when_dry"]:
            self.milking = False
            self.events.add_event(self.days_born, sim_day, const.DRY)
            self.days_in_milk = 0
            self.estimated_daily_milk_produced = 0.0
            self.latest_milk_production_305days = 0.0
            self.fat_percent = 0.0
            self.milk_fat_kg = 0.0
            self.milk_protein_kg = 0.0
            self.lactose_milk = 0.0
            self.CP_milk = 0.0
            self.mPrt = 0.0

        if self.milking:
            self.days_in_milk += 1
        else:
            self.days_in_milk = 0

        estimated_daily_milk_produced = self.calculate_daily_milk_produced()

        if estimated_daily_milk_produced > 0.0:
            daily_milk_variation = self.determine_param_value(
                AnimalModuleConstants.DAILY_MILK_VARIATION_MEAN,
                AnimalModuleConstants.DAILY_MILK_VARIATION_STD_DEV,
            )
            estimated_daily_milk_produced += daily_milk_variation
            estimated_daily_milk_produced += self.milk_production_reduction

        if self.milking:
            self.estimated_daily_milk_produced = max(0.0, estimated_daily_milk_produced)
            self.lactose_milk = AnimalModuleConstants.MILK_LACTOSE
            self.CP_milk = AnimalModuleConstants.MILK_CRUDE_PROTEIN
            self.mPrt = self.get_user_defined_milk_protein_percent()
        else:
            self.estimated_daily_milk_produced = 0.0
            self.lactose_milk = 0.0
            self.CP_milk = 0.0
            self.mPrt = 0.0
        self.single_acc_milk_prod += estimated_daily_milk_produced

        # calculate fat percent in milk and fat corrected milk production
        if self.milking:
            self.fat_percent = self.get_user_defined_milk_fat_percent()
            # daily_fat_correct_milk_production = (
            #     0.4 * estimated_daily_milk_produced + 0.15 * self.fat_percent * estimated_daily_milk_produced
            # )
            self.milk_fat_kg = (self.fat_percent / 100) * self.estimated_daily_milk_produced
            self.milk_protein_kg = (self.mPrt / 100) * self.estimated_daily_milk_produced
        else:
            self.fat_percent = 0.0
            self.milk_fat_kg = 0.0
            self.milk_protein_kg = 0.0

        self.daily_growth = self.get_bw_change(calving_interval)

        self.body_weight += self.daily_growth

    def get_user_defined_milk_fat_percent(self) -> float:
        """
        Return the user-defined milk fat percent for the cow.

        Returns
        -------
        float
            The user-defined milk fat percent for the cow.
        """

        return AnimalBase.config["milk_fat_percent"]

    def get_user_defined_milk_protein_percent(self) -> float:
        """
        Return the user-defined milk protein percent for the cow.

        Returns
        -------
        float
            The user-defined milk protein percent for the cow.
        """

        return AnimalBase.config["milk_protein_percent"]

    def calc_manure_excretion(
        self,
        methane_model: str,
        methane_mitigation_method: str,
        methane_mitigation_additive_amount: float,
        ME_intake: float,
        nutrient_amount: Dict[str, float],
        nutrient_conc: Dict[str, float],
    ) -> None:
        """
        Calculates and sets the manure excretion components.
        Parameters
        ----------
        methane_model : str
            Methane model used for methane emission calculations, including Boadi, IPCC.
        methane_mitigation_method: str
            Methane mitigation method used.
        methane_mitigation_additive_amount: float
            Amount of methane mitigation additive per kg dry matter intake (DMI) (mg/kg).
        ME_intake : float
            Metabolizable energy intake per kg DMI (Mcal/kg).
        nutrient_amount : Dict[str, float]
            Amounts of nutrients in pen ration, calculated per animal, see Notes section for units.
        nutrient_conc : Dict[str, float]
            Concentrations of nutrients in pen ration, calculated per animal, percentages.

        Notes
        -----
        nutrient_amount_units = {
            "dm": "kg/animal",
            "CP": "percent of DM",
            "ADF": "percent of DM",
            "NDF": "percent of DM",
            "lignin": "percent of DM",
            "ash": "percent of DM",
            "phosphorus": "percent of DM",
            "potassium": "percent of DM",
            "N": "percent of DM",
            }
        """
        p_urine, p_feces_excrt = self.calc_base_manure()

        if self.milking:
            self.p_excrt, self.manure_excretion = lactating_manure_calculations(
                self.body_weight,
                self.days_in_milk,
                self.mPrt,
                self.estimated_daily_milk_produced,
                p_feces_excrt,
                p_urine,
                methane_model,
                methane_mitigation_method,
                methane_mitigation_additive_amount,
                self.fat_percent,
                ME_intake,
                nutrient_amount=nutrient_amount,
                nutrient_conc=nutrient_conc,
            )
        else:
            self.p_excrt, self.manure_excretion = dry_manure_calculations(
                self.body_weight,
                self.estimated_daily_milk_produced,
                p_feces_excrt,
                p_urine,
                methane_model,
                ME_intake,
                nutrient_amount=nutrient_amount,
                nutrient_conc=nutrient_conc,
            )

    def set_nutrient_rqmts(self, animal_grouping_scenario, nutrient_conc: dict = {}) -> None:
        """
        Calculates this Cow's nutrient requirements.

        """
        if nutrient_conc and nutrient_conc["dm"] != 0.0:
            NDF_conc = nutrient_conc["NDF"] / 100
            TDN_conc = nutrient_conc["TDN"] / 100
        else:
            NDF_conc = 0.3
            TDN_conc = 0.7
        req = AnimalRequirements()
        animal_requirements = req.calc_rqmts(
            body_weight=self.body_weight,
            mature_body_weight=self.mature_body_weight,
            day_of_pregnancy=self.days_in_preg,
            animal_type=animal_grouping_scenario.get_animal_type(self),
            parity=self.calves,
            calving_interval=self.CI,
            milk_true_protein=self.mPrt,
            milk_fat=self.fat_percent,
            milk_lactose=self.lactose_milk,
            milk_production=self.estimated_daily_milk_produced,
            days_in_milk=self.days_in_milk,
            lactating=self.milking,
            NDF_conc=NDF_conc,
            TDN_conc=TDN_conc,
        )

        self.NEmaint_requirement = animal_requirements["NEmaint_requirement"]
        self.NEg_requirement = animal_requirements["NEg_requirement"]
        self.NEpreg_requirement = animal_requirements["NEpreg_requirement"]
        self.NEl_requirement = animal_requirements["NEl_requirement"]
        self.MP_requirement = animal_requirements["MP_requirement"]
        self.Ca_requirement = animal_requirements["Ca_requirement"]
        self.P_requirement = animal_requirements["P_requirement"]
        self.DMIest_requirement = animal_requirements["DMIest_requirement"]
        self.DNED_requirement = (
            animal_requirements["NEmaint_requirement"] + animal_requirements["NEl_requirement"]
        ) / self.DMIest_requirement
        self.DMDP_requirement = (animal_requirements["MP_requirement"]) / self.DMIest_requirement

    def phosphorus_rqmts(self, DMI: float) -> None:
        """
        Calculates and sets the animal's phosphorus requirement.

        Parameters
        ----------
        DMI : float
            Dry Matter Intake (kg).
        """
        # amount of P required for endogenous losses (g) (A.1EF.E.1)
        self.p_maint_feces = 0.001 * DMI * GeneralConstants.KG_TO_GRAMS

        # absorbed P retained for growth (g) (A.1EF.E.3)
        if self.body_weight < self.mature_body_weight:
            self.p_growth = (
                (0.0012 + 0.004635 * (self.mature_body_weight**0.22) * (self.body_weight ** (-0.22)))
                * self.daily_growth
                / 0.96
                * GeneralConstants.KG_TO_GRAMS
            )
        else:
            self.p_growth = 0

        # amount pf P required for urine production (g) (A.1EF.E.2)
        p_urine = 0.000002 * self.body_weight * GeneralConstants.KG_TO_GRAMS

        # absorbed P retained for fetal growth (g) (A.1EF.E.4)
        if self.days_in_preg >= 190:
            exp_1 = (0.05527 - 0.000075 * self.days_in_preg) * self.days_in_preg
            exp_2 = (0.05527 - 0.000075 * (self.days_in_preg - 1)) * (self.days_in_preg - 1)
            self.p_gest = (0.00002743 * math.exp(exp_1) - 0.00002743 * math.exp(exp_2)) * GeneralConstants.KG_TO_GRAMS
            self.p_gest_for_calf += self.p_gest
        else:
            self.p_gest = 0

        # amount of P in milk per animal (g) (A.1E.E.5)
        if self.milking:
            p_milk = 0.0009 * self.estimated_daily_milk_produced * GeneralConstants.KG_TO_GRAMS
        else:
            p_milk = 0

        # absorbed P required by the animal (g) (A.1EF.E.6)
        p_absorb = p_urine + self.p_maint_feces + self.p_growth + self.p_gest + p_milk

        # requirement of P from the ration (g) (A.1EF.E.7)
        if self.milking:
            self.p_req = p_absorb / (1.86696 - 5.01238 * self.p_conc_ration + 5.12286 * self.p_conc_ration**2)
        else:
            self.p_req = p_absorb / 0.664

    def calc_daily_walking_dist(self, vertical_dist_to_parlor: float, horizontal_dist_to_parlor: float) -> None:
        """
        Calculates and sets the animal's daily vertical and horizontal
        walking distance (DVD and DHD).

        Parameters
        ----------
        vertical_dist_to_parlor : float
            Vertical distance to milking parlor (km).
        horizontal_dist_to_parlor : float
            Horizontal distance to milking parlor, km.

        """
        # multiplied by 2 for return trip
        self.DVD = 2 * vertical_dist_to_parlor * AnimalBase.config["cow_times_milked_per_day"]
        self.DHD = 2 * horizontal_dist_to_parlor * AnimalBase.config["cow_times_milked_per_day"]

    def get_bw_change(self, CI: int | float) -> float:  # noqa
        """
        Calculates the body weight change for a cow.

        Parameters
        ----------
        calving_interval : int | float
            The calving interval used in the body weight
                change calculation, can be from config or average value.

        Returns
        -------
            The daily body weight change for a cow.

        References
        ----------
        Life cycle pseudocode @[A.1A.C.56/57/58]

        """
        # on the calving day
        if self.days_in_preg == self.gestation_length:
            conceptus_growth = -self.conceptus_weight
            self.conceptus_weight = 0
            self.tissue_changed = 0
        # conceptus weight change during pregnancy
        elif self.days_in_preg > 50:
            conceptus_total_weight = (0.0148 * self.gestation_length - 2.408) * self.calf_birth_weight
            conceptus_param = conceptus_total_weight ** (1 / 3) / (self.gestation_length - 50)
            conceptus_growth = 3 * conceptus_param**3 * (self.days_in_preg - 50) ** 2
            self.conceptus_weight += conceptus_growth
        else:
            conceptus_growth = 0

        # growth for 1st and 2nd lactation cows
        if self.calves == 1:
            if self.days_in_preg < 1:  # before pregnancy
                target_adg_cow = (0.92 - 0.82) * 0.96 * self.mature_body_weight / CI
            else:  # after pregnancy
                target_adg_cow = (0.92 * self.mature_body_weight - self.body_weight) / (
                    self.gestation_length - self.days_in_preg + 1
                )
        elif self.calves == 2:
            if self.days_in_preg < 1:  # before pregnancy
                target_adg_cow = (1 - 0.92) * 0.96 * self.mature_body_weight / CI
            else:  # after pregnancy
                target_adg_cow = (self.mature_body_weight - self.body_weight) / (
                    self.gestation_length - self.days_in_preg + 1
                )
        else:  # parity > 2
            target_adg_cow = 0

        if not self.days_in_milk == 0:
            if self.calves == 1:
                bodyweight_tissue = -20 / 65 * math.exp(1 - self.days_in_milk / 65) + 20 / (
                    65**2
                ) * self.days_in_milk * math.exp(1 - self.days_in_milk / 65)
                if self.days_in_preg == AnimalBase.config["days_in_preg_when_dry"] - 1:
                    self.tissue_changed = 20 * self.days_in_milk / 65 * math.exp(1 - self.days_in_milk / 65)
            else:  # parity > 1
                bodyweight_tissue = -40 / 70 * math.exp(1 - self.days_in_milk / 70) + 40 / (
                    70**2
                ) * self.days_in_milk * math.exp(1 - self.days_in_milk / 70)
                if self.days_in_preg == AnimalBase.config["days_in_preg_when_dry"] - 1:
                    self.tissue_changed = 40 * self.days_in_milk / 70 * math.exp(1 - self.days_in_milk / 70)
        else:  # dry period
            bodyweight_tissue = self.tissue_changed / (
                self.gestation_length - AnimalBase.config["days_in_preg_when_dry"]
            )

        return target_adg_cow + conceptus_growth + bodyweight_tissue

    def update(self, sim_day: int, calving_interval: int | float) -> bool:  # noqa
        """Update cow status from the moment of calving, parity+1,
        milking start, pregnancy stop, and estrus restart.

        Parameters
        ----------
        sim_day : int
            The simulation day.
        calving_interval : int | float
            The size of the calving interval in days, can be average current calving interval instead of input value.

        Returns
        -------
        bool
            new_born status which is True if a calf is born.

        Raises
        ------
        ValueError
            If reproduction program not in list of current reproduction programs.

        """

        new_born = False
        self.days_born += 1

        if self.days_in_preg > 0 and self.days_in_preg == self.gestation_length:
            self._repro_state_manager.reset()
            self.calves += 1
            self.milking = True
            self.days_in_milk = 0
            self.days_in_preg = 0
            self.gestation_length = 0
            if self.calves >= 2:
                last_time_given_birth = self.events.get_most_recent_date(const.NEW_BIRTH)
                self.CI = self.days_born - last_time_given_birth
                self.CI_history.append(self.CI)
            self.BW_at_calving = self.body_weight
            self.events.add_event(self.days_born, sim_day, const.NEW_BIRTH)
            self.log_event(self.days_born, sim_day, f"{const.NUM_CALVES_BORN_NOTE}: {self.calves}")
            self.health_cull_update()
            self.death_update()
            new_born = True
            self.set_parity_index()
            self.set_lactation_curve_params()

            if self.repro_program != self.get_user_defined_repro_protocol():
                self._set_repro_program(sim_day, self.get_user_defined_repro_protocol())
                self._repro_state_manager.reset()

            # restarting estrus
            if self.repro_program in [
                CowReproProtocolEnum.ED.value,
                CowReproProtocolEnum.ED_TAI.value,
            ]:
                self._simulate_estrus(
                    self.days_born,
                    sim_day,
                    f"{const.ESTRUS_AFTER_CALVING_NOTE}: {const.ESTRUS_DAY_SCHEDULED_NOTE}",
                    self.get_avg_estrus_cycle_return(),
                    self.get_std_estrus_cycle_return(),
                )

        # if self.milking:
        self.milking_update(sim_day, calving_interval)

        self.update_body_weight_history(sim_day)
        self.update_milk_production_history(sim_day)

        if not self.do_not_breed:
            if self.repro_program not in [
                CowReproProtocolEnum.ED.value,
                CowReproProtocolEnum.TAI.value,
                CowReproProtocolEnum.ED_TAI.value,
            ]:
                raise ValueError(f"Invalid cow repro program: {self.repro_program}")

            if self.repro_program != self.get_user_defined_repro_protocol():
                self._set_repro_program(sim_day, self.get_user_defined_repro_protocol())
                self.log_event(
                    self.days_born,
                    sim_day,
                    f"Pre-existing days in milk: {self.days_in_milk}",
                )
                self.log_event(
                    self.days_born,
                    sim_day,
                    f"Pre-existing days in preg: {self.days_in_preg}",
                )
                self.log_event(self.days_born, sim_day, f"Pre-existing AI day: {self.ai_day}")
                self.log_event(
                    self.days_born,
                    sim_day,
                    f"Pre-existing estrus day: {self.estrus_day}",
                )
                if not self.is_pregnant:
                    self._repro_state_manager.enter(ReproStateEnum.ENTER_HERD_FROM_INIT)
                    self._log_repro_states(sim_day)

            if self.repro_program == CowReproProtocolEnum.ED_TAI.value:
                self.execute_ed_tai_protocol(sim_day)

            if self.repro_program == CowReproProtocolEnum.ED.value or self._repro_state_manager.is_in_any(
                {
                    ReproStateEnum.WAITING_FULL_ED_CYCLE,
                    ReproStateEnum.WAITING_SHORT_ED_CYCLE,
                    ReproStateEnum.WAITING_FULL_ED_CYCLE_BEFORE_OVSYNCH,
                }
            ):
                self.execute_ed_protocol(sim_day)

            if self.repro_program == CowReproProtocolEnum.TAI.value or self._repro_state_manager.is_in_any(
                {
                    ReproStateEnum.IN_PRESYNCH,
                    ReproStateEnum.HAS_DONE_PRESYNCH,
                    ReproStateEnum.IN_OVSYNCH,
                }
            ):
                self.execute_tai_protocol(sim_day)

            if self.days_born == self.ai_day:
                self._calculate_conception_rate_on_ai_day()
                self._repro_state_manager.enter(ReproStateEnum.AFTER_AI)
                self._log_repro_states(sim_day)
                self._perform_ai(sim_day)

            self.preg_update(sim_day)

        self._check_do_not_breed_flag(sim_day)

        self.cull_update(sim_day)

        return new_born

    def _calculate_conception_rate_on_ai_day(self) -> None:
        if self.should_decrease_conception_rate_in_rebreeding():
            self.conception_rate -= self._num_conception_rate_decreases * self.get_conception_rate_decrease()

        if self.should_decrease_conception_rate_by_parity():
            self.conception_rate = self._decrease_conception_rate_by_parity(self.calves, self.conception_rate)

        self.conception_rate = max(0.0, self.conception_rate)

    def _log_repro_states(self, sim_day: int) -> None:
        self.log_event(
            self.days_born,
            sim_day,
            f"Current repro state(s): {self._repro_state_manager}",
        )

    def execute_ed_protocol(self, sim_day: int) -> None:
        """
        Execute the estrus detection protocol. This method is used in the ED and ED-TAI protocols.

        Notes
        -----
        When the number of days in milk is less than the voluntary waiting period, the cow is in the fresh state.
        After the voluntary waiting period, depending on the current state of the cow, different actions are taken.

        Parameters
        ----------
        sim_day : int
            The current simulation day.
        """

        if 1 <= self.days_in_milk <= self.get_voluntary_waiting_period():
            self._repeat_estrus_simulation_before_vwp(sim_day)

        elif self.days_in_milk > self.get_voluntary_waiting_period():
            # For cows entering the herd but no estrus day has been set
            if (
                self._repro_state_manager.is_in(ReproStateEnum.ENTER_HERD_FROM_INIT)
                and self.days_born > self.estrus_day
            ):
                self._simulate_estrus(
                    self.days_born,
                    sim_day,
                    const.ESTRUS_DAY_SCHEDULED_NOTE,
                    self.get_avg_estrus_cycle(),
                    self.get_std_estrus_cycle(),
                )

            if self._repro_state_manager.is_in_any({ReproStateEnum.FRESH, ReproStateEnum.ENTER_HERD_FROM_INIT}):
                self._repro_state_manager.enter(ReproStateEnum.WAITING_FULL_ED_CYCLE)
                self._log_repro_states(sim_day)

            if self.days_born == self.estrus_day:
                # Used in PGFatPD resynch program
                if self._repro_state_manager.is_in(ReproStateEnum.WAITING_SHORT_ED_CYCLE):
                    self._repro_state_manager.exit(ReproStateEnum.WAITING_SHORT_ED_CYCLE)
                    self._handle_estrus_detection(
                        sim_day,
                        on_estrus_detected=self._setup_ai_day_after_estrus_detected,
                        on_estrus_not_detected=lambda _: self._repro_state_manager.enter(ReproStateEnum.IN_OVSYNCH),
                    )
                    if self._repro_state_manager.is_in(ReproStateEnum.IN_OVSYNCH):
                        self._log_repro_states(sim_day)

                elif self._repro_state_manager.is_in(ReproStateEnum.WAITING_FULL_ED_CYCLE):
                    self._repro_state_manager.exit(ReproStateEnum.WAITING_FULL_ED_CYCLE)
                    self._handle_estrus_detection(
                        sim_day,
                        on_estrus_detected=self._setup_ai_day_after_estrus_detected,
                        on_estrus_not_detected=self._simulate_full_estrus_cycle,
                    )

                # Used in the initial ED portion of the ED-TAI protocol
                elif self._repro_state_manager.is_in(ReproStateEnum.WAITING_FULL_ED_CYCLE_BEFORE_OVSYNCH):
                    self._repro_state_manager.exit(ReproStateEnum.WAITING_FULL_ED_CYCLE_BEFORE_OVSYNCH)
                    self._handle_estrus_detection(
                        sim_day,
                        on_estrus_detected=self._setup_ai_day_after_estrus_detected,
                        on_estrus_not_detected=self._simulate_full_estrus_cycle_before_ovsynch,
                    )

    def _repeat_estrus_simulation_before_vwp(self, sim_day: int) -> None:
        """
        Repeat the estrus simulation before the voluntary waiting period.

        Parameters
        ----------
        sim_day : int
            The current simulation day.
        """

        if self._repro_state_manager.is_in_empty_state() or self._repro_state_manager.is_in(
            ReproStateEnum.ENTER_HERD_FROM_INIT
        ):
            self._repro_state_manager.enter(ReproStateEnum.FRESH)
            self._log_repro_states(sim_day)
        if self.days_born == self.estrus_day:
            self.log_event(
                self.days_born,
                sim_day,
                const.ESTRUS_BEFORE_VOLUNTARY_WAITING_PERIOD_NOTE,
            )
            self._simulate_estrus(
                self.days_born,
                sim_day,
                const.ESTRUS_DAY_SCHEDULED_NOTE,
                self.get_avg_estrus_cycle(),
                self.get_std_estrus_cycle(),
            )
        elif self.days_born > self.estrus_day:
            self._simulate_estrus(
                self.days_born,
                sim_day,
                const.ESTRUS_DAY_SCHEDULED_NOTE,
                self.get_avg_estrus_cycle(),
                self.get_std_estrus_cycle(),
            )

    def _setup_ai_day_after_estrus_detected(self, sim_day: int) -> None:
        """
        Handle the estrus detected event.

        Parameters
        ----------
        sim_day : int
            The current simulation day.
        """

        if self._repro_state_manager.is_in(ReproStateEnum.IN_OVSYNCH):
            self._exit_ovsynch_program_early_when_first_preg_check_passed_or_estrus_detected(sim_day)

        self._repro_state_manager.enter(ReproStateEnum.ESTRUS_DETECTED)
        self._log_repro_states(sim_day)
        self.conception_rate = self.get_estrus_conception_rate()
        self.ai_day = self.days_born + 1
        self.log_event(
            self.days_born,
            sim_day,
            f"{const.AI_DAY_SCHEDULED_NOTE} on day {self.ai_day}",
        )

    def get_general_estrus_detection_rate(self) -> float:
        """
        Get the estrus detection rate for cows.

        Returns
        -------
        float
            The estrus detection rate for cows.
        """

        return AnimalBase.config["cows"]["estrus_detection_rate"]

    def get_estrus_conception_rate(self) -> float:
        """
        Get the estrus conception rate for cows.

        Returns
        -------
        float
            The estrus conception rate.
        """

        return AnimalBase.config["cows"]["ED_conception_rate"]

    def _simulate_full_estrus_cycle(self, sim_day: int) -> None:
        """
        Handle the estrus not detected event.

        Parameters
        ----------
        sim_day : int
            The current simulation day.
        """

        self._repro_state_manager.enter(ReproStateEnum.WAITING_FULL_ED_CYCLE, keep_existing=True)
        self._log_repro_states(sim_day)
        self._simulate_estrus(
            self.days_born,
            sim_day,
            const.ESTRUS_DAY_SCHEDULED_NOTE,
            self.get_avg_estrus_cycle(),
            self.get_std_estrus_cycle(),
        )

    def _simulate_full_estrus_cycle_before_ovsynch(self, sim_day: int) -> None:
        """
        Simulate another estrus cycle before the OvSynch program in the ED-TAI protocol.

        Notes
        -----
        This method is called when the estrus is not detected on an estrus day during the period
        between the voluntary waiting period and the start of the OvSynch program. It will schedule
        the next estrus day and if this day is beyond the OvSynch program start day, the estrus
        detection process will be canceled and the cow will enter the OvSynch program.

        Parameters
        ----------
        sim_day : int
            The current simulation day.
        """

        self._repro_state_manager.enter(ReproStateEnum.WAITING_FULL_ED_CYCLE_BEFORE_OVSYNCH)
        self._log_repro_states(sim_day)
        self._simulate_estrus(
            self.days_born,
            sim_day,
            const.ESTRUS_DAY_SCHEDULED_NOTE,
            self.get_avg_estrus_cycle(),
            self.get_std_estrus_cycle(),
        )

    def _execute_hormone_delivery_schedule(self, sim_day: int, schedule: dict[int, dict]) -> None:
        """
        Execute a hormone delivery schedule for cows.

        Notes
        -----
        This method overrides the similar method in the HeiferII class. In addition to the actions performed by the
        version in the HeiferII class, this method can also perform the following actions:
        - set the presynch end day
        - set the TAI start day
        - set the TAI end day

        Parameters
        ----------
        sim_day : int
            The current day of the entire simulation.
        schedule : dict[int, dict]
            A dictionary of days and actions to perform on those days.
        """

        super()._execute_hormone_delivery_schedule(sim_day, schedule)

        actions = schedule.get(self.days_born)
        if actions is not None:
            if actions.get("set_presynch_end", False):
                self.log_event(
                    self.days_born,
                    sim_day,
                    f"{const.PRESYNCH_PERIOD_END}: {self.get_presynch_program()}",
                )
                self._repro_state_manager.exit(ReproStateEnum.IN_PRESYNCH)
                self._repro_state_manager.enter(ReproStateEnum.HAS_DONE_PRESYNCH)
                del actions["set_presynch_end"]

            if actions.get("set_ovsynch_end", False):
                self.log_event(
                    self.days_born,
                    sim_day,
                    f"{const.OVSYNCH_PERIOD_END_NOTE}: {self.get_ovsynch_program()}",
                )
                self._repro_state_manager.exit(ReproStateEnum.IN_OVSYNCH)
                del actions["set_ovsynch_end"]

            if not actions:
                del schedule[self.days_born]

    def execute_tai_protocol(self, sim_day: int) -> None:
        """
        Execute the TAI protocol by setting up and executing hormone delivery schedules for
        the presynch and ovsynch programs.

        Parameters
        ----------
        sim_day : int
            The current simulation day.
        """

        if self.get_presynch_program() == CowReproProtocolEnum.NONE.value:
            if 1 <= self.days_in_milk < self.get_ovsynch_program_start_day():
                self._enter_fresh_state_if_in_empty_state(sim_day)
            elif self.days_in_milk >= self.get_ovsynch_program_start_day():
                self._setup_ovsynch_on_ovsynch_start_day_if_valid(sim_day)
            if self._hormone_schedule:
                self._execute_hormone_delivery_schedule(sim_day, self._hormone_schedule)
            return

        if 1 <= self.days_in_milk < self.get_presynch_program_start_day():
            self._enter_fresh_state_if_in_empty_state(sim_day)
        elif self.days_in_milk >= self.get_presynch_program_start_day():
            self._setup_presynch_on_presynch_start_day_if_valid(sim_day)
            if self._hormone_schedule:
                self._execute_hormone_delivery_schedule(sim_day, self._hormone_schedule)
            self._setup_ovsynch_on_ovsynch_start_day_if_valid(sim_day)
        if self._hormone_schedule:
            self._execute_hormone_delivery_schedule(sim_day, self._hormone_schedule)

    def _setup_presynch_on_presynch_start_day_if_valid(self, sim_day: int) -> None:
        """
        Set up a presynch program on the presynch start day if it does not exist.

        Parameters
        ----------
        sim_day : int
            The current simulation day.
        """

        if self._should_set_up_hormone_delivery_for_presynch():
            self._set_up_hormone_schedule("cows", self.get_presynch_program(), self.days_born)
            self.log_event(
                self.days_born,
                sim_day,
                f"{const.PRESYNCH_PERIOD_START}: {self.get_presynch_program()}",
            )

    def _enter_fresh_state_if_in_empty_state(self, sim_day: int) -> None:
        """
        Enter the fresh state if the cow is in no repro state initially.

        Parameters
        ----------
        sim_day : int
            The current simulation day.
        """

        if self._repro_state_manager.is_in_empty_state() or self._repro_state_manager.is_in(
            ReproStateEnum.ENTER_HERD_FROM_INIT
        ):
            self._repro_state_manager.enter(ReproStateEnum.FRESH)
            self._log_repro_states(sim_day)

    def _setup_ovsynch_on_ovsynch_start_day_if_valid(self, sim_day: int) -> None:
        """
        Set up an OvSynch program on the OvSynch start day if it does not exist.

        Parameters
        ----------
        sim_day : int
            The current simulation day.
        """

        if self._should_set_up_hormone_delivery_for_ovsynch():
            self._set_up_hormone_schedule("cows", self.get_ovsynch_program(), self.days_born)
            self._TAI_conception_rate = self.get_ovsynch_program_conception_rate()
            self.log_event(
                self.days_born,
                sim_day,
                f"{const.OVSYNCH_PERIOD_START_NOTE}: {self.get_ovsynch_program()}",
            )

    def _should_set_up_hormone_delivery_for_presynch(self) -> bool:
        """
        Check if the cow should set up hormone delivery for a presynch program.

        Returns
        -------
        bool
            True if the cow should set up hormone delivery for a presynch program, False otherwise.
        """

        if self.repro_program != CowReproProtocolEnum.TAI.value:
            return False

        if self.get_presynch_program() not in [
            CowReproProtocolEnum.Presynch_PreSynch.value,
            CowReproProtocolEnum.Presynch_DoubleOvSynch.value,
            CowReproProtocolEnum.Presynch_G6G.value,
        ]:
            return False

        if self._hormone_schedule:
            return False

        if self.days_in_milk == self.get_presynch_program_start_day() and self._repro_state_manager.is_in_any(
            {ReproStateEnum.FRESH, ReproStateEnum.ENTER_HERD_FROM_INIT}
        ):
            self._repro_state_manager.enter(ReproStateEnum.IN_PRESYNCH)
            self._log_repro_states(self.days_born)
            return True

        if self.days_in_milk > self.get_presynch_program_start_day() and self._repro_state_manager.is_in(
            ReproStateEnum.ENTER_HERD_FROM_INIT
        ):
            self._repro_state_manager.enter(ReproStateEnum.IN_PRESYNCH)
            self._log_repro_states(self.days_born)
            return True

        return self._repro_state_manager.is_in(ReproStateEnum.IN_PRESYNCH)

    def _should_set_up_hormone_delivery_for_ovsynch(self) -> bool:
        """
        Check if the cow should set up hormone delivery for timed artificial insemination.

        Notes
        -----
        If the number of days in milk is equal to the OvSynch program start day and the cow is in
        the fresh state or has just gone through a presynch program, then the cow should be scheduled
        for an OvSynch program.

        If the OvSynch program start day happens before the last day of the presynch program, then
        the start day of the OvSynch program will be adjusted to be the last day of the presynch program.
        In other words, if both presynch and OvSynch programs are scheduled, then their schedules
        cannot be overlapped.

        Returns
        -------
        bool
            True if the cow should set up a hormone delivery schedule for an OvSynch program, False otherwise.
        """

        if self._hormone_schedule:
            return False

        if self.get_ovsynch_program() not in [
            CowReproProtocolEnum.TAI_OvSynch_48.value,
            CowReproProtocolEnum.TAI_OvSynch_56.value,
            CowReproProtocolEnum.TAI_CoSynch_72.value,
            CowReproProtocolEnum.TAI_5d_CoSynch.value,
        ]:
            return False

        if self._repro_state_manager.is_in(ReproStateEnum.IN_PRESYNCH):
            return False

        if self.days_in_milk == self.get_ovsynch_program_start_day():
            if self._repro_state_manager.is_in_empty_state() or self._repro_state_manager.is_in_any(
                {
                    ReproStateEnum.ENTER_HERD_FROM_INIT,
                    ReproStateEnum.FRESH,
                    ReproStateEnum.HAS_DONE_PRESYNCH,
                }
            ):
                self._repro_state_manager.enter(ReproStateEnum.IN_OVSYNCH)
                self._log_repro_states(self.days_born)
                return True

        if self.days_in_milk > self.get_ovsynch_program_start_day():
            if self._repro_state_manager.is_in_any(
                {ReproStateEnum.HAS_DONE_PRESYNCH, ReproStateEnum.ENTER_HERD_FROM_INIT}
            ):
                self._repro_state_manager.enter(ReproStateEnum.IN_OVSYNCH)
                self._log_repro_states(self.days_born)
                return True

        return self._repro_state_manager.is_in(ReproStateEnum.IN_OVSYNCH)

    def _increment_ai_counts(self) -> None:
        """
        Increment the performed AI counts across all cows.
        """

        self.stats["num_ai_performed"] += 1

    def _increment_successful_conceptions(self) -> None:
        """
        Increment the successful conception counts across all heifers.
        """

        self.stats["num_successful_conceptions"] += 1

    def execute_ed_tai_protocol(self, sim_day: int) -> None:
        """
        Execute the ED-TAI protocol by checking the days in milk and taking the appropriate actions.

        Notes
        -----
        The following actions are taken:
        - If the days in milk is between 1 and the program start day, no actions will be taken.

        - If the days in milk is between the program start day and the TAI program start day, the cow
        will be monitored for estrus daily during this period.

        - If the days in milk is greater than or equal to the TAI program start day, the cow will be
        scheduled for a TAI program if estrus has not been detected before the TAI start day.

        Parameters
        ----------
        sim_day : int
            The current simulation day.
        """

        if 1 <= self.days_in_milk <= self.get_voluntary_waiting_period():
            self._repeat_estrus_simulation_before_vwp(sim_day)

        elif self.get_voluntary_waiting_period() < self.days_in_milk < self.get_ovsynch_program_start_day():
            if (
                self._repro_state_manager.is_in(ReproStateEnum.ENTER_HERD_FROM_INIT)
                and self.days_born > self.estrus_day
            ):
                self._simulate_estrus(
                    self.days_born,
                    sim_day,
                    const.ESTRUS_DAY_SCHEDULED_NOTE,
                    self.get_avg_estrus_cycle(),
                    self.get_std_estrus_cycle(),
                )

            if self._repro_state_manager.is_in_any({ReproStateEnum.FRESH, ReproStateEnum.ENTER_HERD_FROM_INIT}):
                self._repro_state_manager.enter(ReproStateEnum.WAITING_FULL_ED_CYCLE_BEFORE_OVSYNCH)
                self._log_repro_states(sim_day)

        elif self.days_in_milk >= self.get_ovsynch_program_start_day():
            self._handle_estrus_not_detected_before_ovsynch_start_day(sim_day)

    def _handle_estrus_not_detected_before_ovsynch_start_day(self, sim_day: int) -> None:
        """
        Redirect the cow to enter an OvSynch program when estrus has not been detected between the
        voluntary waiting period and the OvSynch program start day.

        Parameters
        ----------
        sim_day : int
            The current simulation day.
        """

        if self._repro_state_manager.is_in(ReproStateEnum.ENTER_HERD_FROM_INIT):
            self._repro_state_manager.enter(ReproStateEnum.IN_OVSYNCH)
            self._log_repro_states(sim_day)

        elif self._repro_state_manager.is_in(ReproStateEnum.WAITING_FULL_ED_CYCLE_BEFORE_OVSYNCH):
            self.log_event(
                self.days_born,
                sim_day,
                const.ESTRUS_NOT_DETECTED_BETWEEN_VWP_AND_OVSYNCH_START_DAY_NOTE,
            )
            self.log_event(self.days_born, sim_day, const.CANCEL_ESTRUS_DETECTION_NOTE)
            self._repro_state_manager.enter(ReproStateEnum.IN_OVSYNCH)
            self._log_repro_states(sim_day)

        elif self._repro_state_manager.is_in(ReproStateEnum.FRESH):  # When no ED is instituted
            self.log_event(
                self.days_born,
                sim_day,
                const.NO_ED_INSTITUTED_BEFORE_OVSYNCH_IN_ED_TAI_NOTE,
            )
            self._repro_state_manager.enter(ReproStateEnum.IN_OVSYNCH)
            self._log_repro_states(sim_day)

    def _decrease_conception_rate_by_parity(self, calves: int, conception_rate: float) -> float:
        """
        Adjust conception rate based on the parity of the cow.

        Parameters
        ----------
        calves : int
            The number of calves the cow has had.
        conception_rate : float
            The conception rate to adjust.

        Returns
        -------
        float
            The adjusted conception rate.
        """

        if calves <= 1:
            return conception_rate
        elif calves == 2:
            return conception_rate - 0.05
        else:
            return conception_rate - 0.1

    def _handle_successful_conception(self, sim_day: int) -> None:
        """
        Set the gestation length, calf birth weight, and calving to pregnancy time and
        schedule a TAI program in advance if the resynch protocol is TAIbeforePD.

        Notes
        -----
        When a successful conception occurs, the following variables are set:
        - days_in_preg: Initialized to 1.
        - gestation_length: Calculated using the '_calculate_gestation_length' method.
        - calf_birth_weight: Calculated using the '_calculate_calf_birth_weight' method.
        - calving_to_preg_time: Calculated as the difference between the current simulation day and the
            most recent birth event.
        - If the resynch protocol is TAIbeforePD, an OvSynch program will be scheduled in advance.

        Parameters
        ----------
        sim_day : int
            The current simulation day.
        """

        self.log_event(
            self.days_born,
            sim_day,
            f"{const.SUCCESSFUL_CONCEPTION}, " f"with conception rate at {self.conception_rate}",
        )
        self.log_event(self.days_born, sim_day, const.COW_PREG)
        self.days_in_preg = 1
        self._repro_state_manager.enter(ReproStateEnum.PREGNANT)
        self._log_repro_states(sim_day)
        self.gestation_length = self._calculate_gestation_length()
        self.calf_birth_weight = self._calculate_calf_birth_weight(self.breed)
        if self.calves > 0:
            last_time_given_birth = self.events.get_most_recent_date(const.NEW_BIRTH)
            self.calving_to_preg_time = self.days_born - last_time_given_birth

        if self.repro_program in [
            CowReproProtocolEnum.TAI.value,
            CowReproProtocolEnum.ED_TAI.value,
        ]:
            if self.get_resynch_program() == CowReproProtocolEnum.Resynch_TAIbeforePD.value:
                self._schedule_ovsynch_program_in_advance(sim_day)
                self._repro_state_manager.enter(ReproStateEnum.IN_OVSYNCH, keep_existing=True)
                self._log_repro_states(sim_day)

    def _handle_failed_conception(self, sim_day: int) -> None:
        """
        Manage different scenarios that the cow's repro states can be in when a failed conception occurs.

        Notes
        -----
        If the repro program is ED or ED-TAI, after a failed conception, the cow will be
        scheduled for a full estrus cycle.
        If the repro program is TAI and the resynch protocol is TAIbeforePD, the cow will be
        scheduled for an OvSynch program in advance.
        If the repro program is ED-TAI and the resynch protocol is TAIAfterPD, the cow will also
        be scheduled for an OvSynch program in advance, while monitoring for estrus at the same time.

        Parameters
        ----------
        sim_day : int
            The current simulation day.
        """

        self.log_event(
            self.days_born,
            sim_day,
            f"{const.FAILED_CONCEPTION}, " f"with conception rate at {self.conception_rate}",
        )
        self.log_event(self.days_born, sim_day, const.COW_NOT_PREG)

        if self.repro_program in [
            CowReproProtocolEnum.ED.value,
            CowReproProtocolEnum.ED_TAI.value,
        ]:
            self._repro_state_manager.enter(ReproStateEnum.WAITING_FULL_ED_CYCLE)
            self._log_repro_states(sim_day)
            self._simulate_estrus(
                self.days_born,
                sim_day,
                const.ESTRUS_DAY_SCHEDULED_NOTE,
                self.get_avg_estrus_cycle(),
                self.get_std_estrus_cycle(),
            )

        if self.repro_program in [
            CowReproProtocolEnum.TAI.value,
            CowReproProtocolEnum.ED_TAI.value,
        ]:
            if self.get_resynch_program() == CowReproProtocolEnum.Resynch_TAIbeforePD.value:
                self._schedule_ovsynch_program_in_advance(sim_day)

                if self.repro_program == CowReproProtocolEnum.ED_TAI.value:
                    # We want to keep the ED protocol running at the same time as the OvSynch program.
                    self._repro_state_manager.enter(ReproStateEnum.IN_OVSYNCH, keep_existing=True)
                    self._log_repro_states(sim_day)
                elif self.repro_program == CowReproProtocolEnum.TAI.value:
                    self._repro_state_manager.enter(ReproStateEnum.IN_OVSYNCH)
                    self._log_repro_states(sim_day)

    def preg_update(self, sim_day: int) -> None:
        """
        Perform a pregnancy check if the current day is a designated pregnancy check day.

        Notes
        -----
        The method uses a list of dictionaries, each representing a specific pregnancy check configuration.
        The method iterates through each configuration, checking if the current simulation day
        matches a scheduled pregnancy check day. If so, it calls the '_handle_preg_check' method
        with the specific configuration and the current simulation day.

        Parameters
        ----------
        sim_day : int
            The current day of the simulation.
        """

        if self.days_in_preg > 0:
            self.days_in_preg += 1

        preg_check_configs: list[PregCheckConfig] = [
            {
                "day": self.get_first_preg_check_day(),
                "loss_rate": self.get_first_preg_check_loss_rate(),
                "on_preg_loss": const.PREG_LOSS_BEFORE_1,
                "on_preg": const.PREG_CHECK_1_PREG,
                "on_not_preg": const.PREG_CHECK_1_NOT_PREG,
            },
            {
                "day": self.get_second_preg_check_day(),
                "loss_rate": self.get_second_preg_check_loss_rate(),
                "on_preg_loss": const.PREG_LOSS_BTWN_1_AND_2,
                "on_preg": const.PREG_CHECK_2_PREG,
            },
            {
                "day": self.get_third_preg_check_day(),
                "loss_rate": self.get_third_preg_check_loss_rate(),
                "on_preg_loss": const.PREG_LOSS_BTWN_2_AND_3,
                "on_preg": const.PREG_CHECK_3_PREG,
            },
        ]

        for preg_check_config in preg_check_configs:
            if self.days_born == self.ai_day + preg_check_config["day"]:
                self._handle_preg_check(preg_check_config, sim_day)

    def _check_do_not_breed_flag(self, sim_day: int) -> None:
        """
        Check if the cow should still be in the breeding stage and mark her as do-not-breed if necessary.

        Notes
        -----
        If the cow still cannot get pregnant after the do-not-breed time has passed, she will be
        marked as do-not-breed.

        Important caveat: If even a cow is already pregnant, we cannot mark her as do-not-breed
        yet because she may still lose the pregnancy.

        Parameters
        ----------
        sim_day : int
            The current day of the simulation.
        """

        if not self.is_pregnant and self.days_in_milk > self.get_do_not_breed_time():
            if not self.do_not_breed:
                self.log_event(
                    self.days_born,
                    sim_day,
                    f"{const.DO_NOT_BREED}, days in milk: {self.days_in_milk}, not pregnant",
                )
                self.do_not_breed = True

    def _handle_preg_check(self, preg_check_config: PregCheckConfig, sim_day: int) -> None:
        """
        Handle a pregnancy check by logging the event and terminating the pregnancy if necessary.

        Notes
        -----
        If the cow is not pregnant at the start of the method or loses the pregnancy after,
        she will essentially go through the steps as specified in the open() method.

        When the TAIbeforePD resynch protocol is used, the TAI program instituted prior to the
        first pregnancy check will be discontinued if the cow remains pregnant.

        Parameters
        ----------
        preg_check_config : dict[str, str | int | float]
            A dictionary of pregnancy check configuration values.
        sim_day : int
            The current day of the entire simulation.
        """

        self.preg_diagnoses += 1
        if self.is_pregnant:
            if self._compare_randomized_rate_less_than(preg_check_config["loss_rate"]):
                self._repro_state_manager.exit(ReproStateEnum.PREGNANT)
                self._terminate_pregnancy(preg_check_config["on_preg_loss"], sim_day)
            else:
                self.log_event(self.days_born, sim_day, preg_check_config["on_preg"])
                if self._repro_state_manager.is_in(ReproStateEnum.IN_OVSYNCH):
                    self._exit_ovsynch_program_early_when_first_preg_check_passed_or_estrus_detected(sim_day)
        elif "on_not_preg" in preg_check_config:  # Due to failed conception
            self.log_event(self.days_born, sim_day, preg_check_config["on_not_preg"])
            self.abortion_day = self.days_born
            self.open(sim_day)

    def open(self, sim_day: int) -> None:
        """
        Manage and set up the different states an open cow can be in during rebreeding depending on
        the current repro protocol and the resynch program.

        Notes
        -----
        If the current protocol is ED, this method will simulate another full estrus cycle.
        In the TAI and ED-TAI protocols, if the resynch method is TAIafterPD, the cow will
        go through an OvSynch program next. If the resynch method is TAIbeforePD, the cow will
        essentially go through an OvSynch program also but with some extra considerations for her
        current state in the estrus detection process. If the resynch method is PGFatPD,
        the cow will get a PGF injection, then go through a short estrus cycle, and may need to go
        through an OvSynch program next.

        Parameters
        ----------
        sim_day : int
            The current day of the entire simulation.
        """

        self._num_conception_rate_decreases += 1

        if self.repro_program == CowReproProtocolEnum.ED.value:
            if self.days_born > self.estrus_day:  # No estrus day scheduled yet
                self._repro_state_manager.enter(ReproStateEnum.WAITING_FULL_ED_CYCLE)
                self._log_repro_states(sim_day)
                self.log_event(self.days_born, sim_day, f"days in milk: {self.days_in_milk}")
                self._simulate_estrus(
                    self.days_born,
                    sim_day,
                    const.ESTRUS_DAY_SCHEDULED_NOTE,
                    self.get_avg_estrus_cycle(),
                    self.get_std_estrus_cycle(),
                )
            return

        # For both TAI and ED-TAI protocols
        if self.get_resynch_program() == CowReproProtocolEnum.Resynch_TAIafterPD.value:
            self._repro_state_manager.enter(ReproStateEnum.IN_OVSYNCH)
            self._log_repro_states(sim_day)

        elif self.get_resynch_program() == CowReproProtocolEnum.Resynch_TAIbeforePD.value:
            self._handle_open_cow_in_tai_before_pd_resynch(sim_day)

        elif self.get_resynch_program() == CowReproProtocolEnum.Resynch_PGFatPD.value:
            self._handle_open_cow_in_pgf_at_pd_resynch(sim_day)

    def _handle_open_cow_in_pgf_at_pd_resynch(self, sim_day: int) -> None:
        """
        Perform a PGF injection for an open cow in the PGFatPD resynch protocol and simulate a short estrus cycle.

        Notes
        -----
        For simplicity, an open cow in the PGFatPD resynch protocol will get a PGF injection if any of
        the three pregnancy checks fails, without distinguishing between the first and the other two
        pregnancy checks. How the short estrus cycle following the PGF injection is handled is specified
        in the execute_ed_protocol() method. Basically, if estrus is detected, an AI will be performed
        on the next day. If estrus is not detected, a TAI program will be initiated.

        Parameters
        ----------
        sim_day : int
            The current day of the simulation.
        """

        single_pgf_injection_schedule = {self.days_born: {"deliver_hormones": ["PGF"]}}
        self._execute_hormone_delivery_schedule(sim_day, single_pgf_injection_schedule)
        self._repro_state_manager.enter(ReproStateEnum.WAITING_SHORT_ED_CYCLE)
        self._log_repro_states(sim_day)
        self._simulate_estrus(
            self.days_born,
            sim_day,
            const.SIMULATE_ESTRUS_AFTER_PGF_NOTE,
            self.get_avg_estrus_cycle_after_pgf(),
            self.get_std_estrus_cycle_after_pgf(),
            max_cycle_length=const.MAX_ESTRUS_CYCLE_LENGTH_PGF_AT_PREG_CHECK,
        )

    def _handle_open_cow_in_tai_before_pd_resynch(self, sim_day: int) -> None:
        """
        Redirect an open cow in the TAIbeforePD resynch protocol to an OvSynch program after the second or third
        pregnancy check failed and stop any pre-existing estrus detection.

        Notes
        -----
        When the user selects the TAIbeforePD resynch protocol, an OvSynch program will have already been initiated
        prior to the first pregnancy check regardless of the outcome of conception result after performing an AI.
        If the first pregnancy check fails, that OvSynch program set up in advance will be continued.
        On the other hand, if the second or third pregnancy check fails, there was no OvSynch program
        set up in advance, so this method will redirect the cow into an OvSynch program.

        After an AI, a cow in the TAIbeforePD resynch protocol will also be waiting for estrus
        to occur. This method will stop such estrus monitoring if it is still ongoing
        because the cow has already reached the first pregnancy check day.

        Parameters
        ----------
        sim_day : int
            The current day of the simulation.
        """

        if self._repro_state_manager.is_in_empty_state():
            self._repro_state_manager.enter(ReproStateEnum.IN_OVSYNCH)
            self._log_repro_states(sim_day)

        if self._repro_state_manager.is_in(ReproStateEnum.WAITING_FULL_ED_CYCLE):
            self._repro_state_manager.exit(ReproStateEnum.WAITING_FULL_ED_CYCLE)
            self.log_event(self.days_born, sim_day, const.CANCEL_ESTRUS_DETECTION_NOTE)

    def _schedule_ovsynch_program_in_advance(
        self,
        sim_day: int,
        days_before_first_preg_check: int = const.DAYS_BEFORE_FIRST_PREG_CHECK_TO_START_TAI,
    ) -> None:
        """
        Schedule an OvSynch program in advance for the TAIbeforePD resynch protocol after performing an AI.

        Parameters
        ----------
        sim_day : int
            The current day of the entire simulation.
        days_before_first_preg_check : int, optional, default=const.DAYS_BEFORE_FIRST_PREG_CHECK_TO_START_TAI
            The number of days before the first pregnancy check to schedule the OvSynch program.
        """

        hormone_schedule_start_day = self.days_born + self.get_first_preg_check_day() - days_before_first_preg_check
        self._set_up_hormone_schedule("cows", self.get_ovsynch_program(), hormone_schedule_start_day)
        self._TAI_conception_rate = self.get_ovsynch_program_conception_rate()
        self.log_event(
            self.days_born,
            sim_day,
            f"{const.SETTING_UP_OVSYNCH_PROGRAM_IN_ADVANCE_NOTE}: {self.get_ovsynch_program()}",
        )

    def _exit_ovsynch_program_early_when_first_preg_check_passed_or_estrus_detected(self, sim_day: int) -> None:
        """
        Exit the scheduled OvSynch program early in TAIbeforePD resynch protocol when
        the first pregnancy check is successful or estrus has been detected.

        Notes
        -----
        When the user selects the TAIbeforePD resynch protocol, an OvSynch program will be initiated prior to the first
        pregnancy check regardless of the outcome of conception result after performing an AI.
        If the first pregnancy check is successful or estrus has been detected before the first pregnancy check,
        the ongoing OvSynch program should be discontinued.

        Parameters
        ----------
        sim_day : int
            The current day of the simulation.
        """

        self._repro_state_manager.exit(ReproStateEnum.IN_OVSYNCH)
        self._hormone_schedule = {}
        self.log_event(
            self.days_born,
            sim_day,
            f"{const.DISCONTINUE_OVSYNCH_PROGRAM_IN_TAI_BEFORE_PD_NOTE}:" f" {self.get_ovsynch_program()}",
        )

    def _set_repro_program(self, sim_day: int, repro_program: str) -> None:
        """
        Set the reproduction program for the cow if her current program does not match the user-defined program.

        Notes
        -----
        When a cow entering the herd through initialization, her reproduction program may not match the user-defined
        program. This method can be used to correct that.

        Parameters
        ----------
        sim_day : int
            The current day of the entire simulation.
        repro_program : str
            The reproduction program to set for the cow.
        """

        if repro_program not in [
            CowReproProtocolEnum.ED.value,
            CowReproProtocolEnum.TAI.value,
            CowReproProtocolEnum.ED_TAI.value,
        ]:
            raise ValueError(f"Invalid repro program: {repro_program}")

        if self.repro_program == repro_program:
            return

        self.log_event(
            self.days_born,
            sim_day,
            f"{const.SETTING_REPRO_PROGRAM_NOTE} from {self.repro_program} " f"to {repro_program}",
        )
        self.repro_program = repro_program

    def get_first_preg_check_day(self) -> int:
        """
        Get the first pregnancy check day (days).

        Returns
        -------
        int
            The first pregnancy check day (days).
        """

        return AnimalBase.config["preg_check_day_1"]

    def get_second_preg_check_day(self) -> int:
        """
        Get the second pregnancy check day (days).

        Returns
        -------
        int
            The second pregnancy check day (days).
        """

        return AnimalBase.config["preg_check_day_2"]

    def get_third_preg_check_day(self) -> int:
        """
        Get the third pregnancy check day (days).

        Returns
        -------
        int
            The third pregnancy check day (days).
        """

        return AnimalBase.config["preg_check_day_3"]

    def get_first_preg_check_loss_rate(self) -> float:
        """
        Get the first pregnancy check loss rate ([0, 1]).

        Returns
        -------
        float
            The first pregnancy check loss rate ([0, 1]).
        """

        return AnimalBase.config["preg_loss_rate_1"]

    def get_second_preg_check_loss_rate(self) -> float:
        """
        Get the second pregnancy check loss rate ([0, 1]).

        Returns
        -------
        float
            The second pregnancy check loss rate ([0, 1]).
        """

        return AnimalBase.config["preg_loss_rate_2"]

    def get_third_preg_check_loss_rate(self) -> float:
        """
        Get the third pregnancy check loss rate ([0, 1]).

        Returns
        -------
        float
            The third pregnancy check loss rate ([0, 1]).
        """

        return AnimalBase.config["preg_loss_rate_3"]

    def get_do_not_breed_time(self) -> int:
        """
        Get the breeding period for cows before reproductive programs stop if they fail to get pregnant (days).

        Returns
        -------
        int
            The breeding period for cows before reproductive programs stop if they fail to get pregnant (days).
        """

        return AnimalBase.config["do_not_breed_time"]

    def get_avg_estrus_cycle(self) -> int:
        """
        Get the literature value for the average estrus cycle length for cows (days).

        Returns
        -------
        float
            The average estrus cycle length for cows (days).
        """

        return AnimalBase.config["avg_estrus_cycle_cow"]

    def get_std_estrus_cycle(self) -> float:
        """
        Get the literature value for the standard deviation of the estrus cycle length for cows (days).

        Returns
        -------
        float
            The standard deviation of the estrus cycle length for cows (days).
        """

        return AnimalBase.config["std_estrus_cycle_cow"]

    def get_avg_estrus_cycle_return(self) -> int:
        """
        Get the literature value for the average return estrus cycle length for cows (days).

        Returns
        -------
        float
            The average return estrus cycle length for cows (days).
        """

        return AnimalBase.config["avg_estrus_cycle_return"]

    def get_std_estrus_cycle_return(self) -> float:
        """
        Get the literature value for the standard deviation of the return estrus cycle length for cows (days).

        Returns
        -------
        float
            The standard deviation of the return estrus cycle length for cows (days).
        """

        return AnimalBase.config["std_estrus_cycle_return"]

    def get_voluntary_waiting_period(self) -> int:
        """
        Get the voluntary waiting period for cows, used only in the ED and ED-TAI protocols.

        Notes
        -----
        When the cow's days in milk has reached this day, monitoring for estrus will begin.

        Returns
        -------
        int
            The voluntary waiting period for cows, used only in the ED and ED-TAI protocols.
        """

        return AnimalBase.config["voluntary_waiting_period"]

    def get_presynch_program_start_day(self) -> int:
        """
        Get the presynch program start day for cows, used in the TAI protocol.

        Notes
        -----
        In TAI protocol, whether there is a presynch program or not, the cow will be scheduled for an
        OvSynch program and get the first GnRH injection on this day. This means if there is a presynch
        program, the start day for the OvSynch program must be after the last hormone injection of the
        presynch program.

        Returns
        -------
        int
            The presynch program start day for cows, used in the TAI protocol.
        """

        return AnimalBase.config["cows"]["presynch_program_start_day"]

    def get_ovsynch_program_start_day(self) -> int:
        """
        Get the OvSynch program start day for cows used in the TAI and ED-TAI protocol.

        Notes
        -----
        In TAI protocol, whether there is a presynch program or not, the cow will be scheduled for an
        OvSynch program and get the first GnRH injection on this day. This means if there is a presynch
        program, the start day for the OvSynch program must be after the last hormone injection of the
        presynch program.

        In ED-TAI protocol, when estrus has not been detected from the voluntary waiting period to
        this OvSynch program start day, the cow will be scheduled for an OvSynch program and get the
        first GnRH injection on this day.

        Returns
        -------
        int
            The OvSynch program start day for cows used in the TAI and ED-TAI protocol.
        """

        return AnimalBase.config["cows"]["ovsynch_program_start_day"]

    def get_conception_rate_decrease(self) -> float:
        """
        Get the conception rate decrease for cows used during rebreeding ([0, 1]).

        Notes
        -----
        When the user chooses to decrease conception rate during rebreeding, the conception rate
        is decreased by a multiplier of this value depending on the number of times the cow has
        been rebred.

        Returns
        -------
        float
            The conception rate decrease for cows used during rebreeding ([0, 1]).
        """

        return AnimalBase.config["conception_rate_decrease"]

    def get_user_defined_repro_protocol(self) -> str:
        """
        Get the user-defined reproduction protocol for cows. The available options are: ED, TAI, ED-TAI.

        Returns
        -------
        str
            The user-defined reproduction protocol for cows. The available options are: ED, TAI, ED-TAI.
        """

        return AnimalBase.config["cow_repro_method"]

    def get_ovsynch_program(self) -> str:
        """
        Get the OvSynch program for cows, used in either TAI or ED-TAI protocols.

        Notes
        -----
        This OvSynch program is used whenever the cow needs to go through a TAI program that is
        part of the TAI or ED-TAI protocols.

        Returns
        -------
        str
            The OvSynch program for cows used in either TAI or ED-TAI protocols.
            The available options are: OvSynch 48, OvSynch 56, CoSynch 72, 5d CoSynch, N/A.
        """

        return AnimalBase.config["cows"]["ovsynch_program"]

    def get_presynch_program(self) -> str:
        """
        Get the presynch program for cows used in the TA protocol.

        Notes
        -----
        Currently, the presynch protocol is not supported in the ED-TAI protocol yet.

        Returns
        -------
        str
            The presynch program for cows, used in the TA protocol.
            The available options are: Presynch, DoubleOvSynch, G6G, N/A.
        """

        return AnimalBase.config["cows"]["presynch_program"]

    def get_resynch_program(self) -> str:
        """
        Get the resynch program for cows used in the TAI and ED-TAI protocols.

        Returns
        -------
        str
            The resynch program for cows, used in the TAI and ED-TAI protocols.
            The available options are: TAIBeforePD, TAIAfterPD, PGFatPD, N/A.
        """

        return AnimalBase.config["cows"]["resynch_program"]

    def get_ovsynch_program_conception_rate(self) -> float:
        """
        Get the conception rate for OvSynch programs used in the TAI and ED-TAI protocols.

        Notes
        -----
        This conception rate is used whenever the cow needs to go through an OvSynch program that is
        part of the TAI and ED-TAI protocols.

        Returns
        -------
        float
            The conception rate for OvSynch programs used in the TAI and ED-TAI protocols.
        """

        return AnimalBase.config["cows"]["ovsynch_program_conception_rate"]

    def should_decrease_conception_rate_in_rebreeding(self) -> bool:
        """
        Get the user choice of whether to decrease conception rate during rebreeding.

        Returns
        -------
        bool
            True if the user wants to decrease conception rate during rebreeding, False otherwise.
        """

        return AnimalBase.config["decrease_conception_rate_in_rebreeding"]

    def should_decrease_conception_rate_by_parity(self) -> bool:
        """
        Get the user choice of whether to decrease conception rate based on the cow's parity.

        Returns
        -------
        bool
            True if the user wants to decrease conception rate based on the cow's parity, False otherwise.
        """

        return AnimalBase.config["decrease_conception_rate_by_parity"]

    # Cull methods
    def cull_update(self, sim_day: int) -> None:
        """
        Update culling time and cull reasons for cow to leave the herd.

        The reasons for culling are reproduction failure, low production, and health issues.
        """
        if self.do_not_breed and self.estimated_daily_milk_produced < AnimalBase.config["cull_milk_production"]:
            self.culled = True
            self.events.add_event(self.days_born, sim_day, const.LOW_PROD_CULL)
            self.cull_reason = const.LOW_PROD_CULL
        if self.days_born == self.future_cull_date:
            self.culled = True
            self.events.add_event(self.days_born, sim_day, self.cull_reason)
        if self.days_born == self.future_death_date:
            self.culled = True
            self.events.add_event(self.days_born, sim_day, const.DEATH_CULL)
            self.cull_reason = const.DEATH_CULL

    def death_update(self) -> None:
        if self.calves >= 4:
            death_rate = AnimalBase.config["parity_death_prob"][3]
        else:
            death_rate = AnimalBase.config["parity_death_prob"][self.calves - 1]
        death_rand = random()
        if death_rand <= death_rate:
            death_upper_limit = death_lower_limit = death_time_upper_limit = death_time_lower_limit = 0
            death_date_random = random()
            for i in range(len(AnimalBase.config["death_day_prob"]) - 1):
                if (
                    AnimalBase.config["death_day_prob"][i]
                    <= death_date_random
                    < AnimalBase.config["death_day_prob"][i + 1]
                ):
                    death_lower_limit = AnimalBase.config["death_day_prob"][i]
                    death_upper_limit = AnimalBase.config["death_day_prob"][i + 1]
                    death_time_lower_limit = AnimalBase.config["death_day_prob"][i]
                    death_time_upper_limit = AnimalBase.config["death_day_prob"][i + 1]
            n = (death_time_upper_limit - death_time_lower_limit) / (death_upper_limit - death_lower_limit)
            self.future_death_date = round(
                death_time_lower_limit + n * (death_date_random - death_lower_limit) + self.days_born
            )

    def health_cull_update(self) -> None:
        """
        Update cows culled for health problem, first cull or not in this parity
        will be determined with parity specific culling rate, then a cull reason
        will be determined by random draw. Then a cull day will be identified by
        reverse a distribution for cases of this reason.
        """
        # inv_cull_rate = 0
        if self.calves >= 4:
            inv_cull_rate = AnimalBase.config["parity_cull_prob"][3]
        else:
            inv_cull_rate = AnimalBase.config["parity_cull_prob"][self.calves - 1]
        cull_rand = random()
        if cull_rand <= inv_cull_rate:
            cull_reason_rand = random()
            cull_prob = 0
            if cull_reason_rand <= (cull_prob := cull_prob + AnimalBase.config["feet_leg_cull"]["probability"]):
                cull_reason_cull_prob = AnimalBase.config["feet_leg_cull"]["cull_day_prob"]
                self.cull_reason = const.LAMENESS_CULL

            elif cull_reason_rand <= (cull_prob := cull_prob + AnimalBase.config["injury_cull"]["probability"]):
                cull_reason_cull_prob = AnimalBase.config["injury_cull"]["cull_day_prob"]
                self.cull_reason = const.INJURY_CULL

            elif cull_reason_rand <= (cull_prob := cull_prob + AnimalBase.config["mastitis_cull"]["probability"]):
                cull_reason_cull_prob = AnimalBase.config["mastitis_cull"]["cull_day_prob"]
                self.cull_reason = const.MASTITIS_CULL

            elif cull_reason_rand <= (cull_prob := cull_prob + AnimalBase.config["disease_cull"]["probability"]):
                cull_reason_cull_prob = AnimalBase.config["disease_cull"]["cull_day_prob"]
                self.cull_reason = const.DISEASE_CULL

            elif cull_reason_rand <= (cull_prob + AnimalBase.config["udder_cull"]["probability"]):
                cull_reason_cull_prob = AnimalBase.config["udder_cull"]["cull_day_prob"]
                self.cull_reason = const.UDDER_CULL

            else:
                cull_reason_cull_prob = AnimalBase.config["unknown_cull"]["cull_day_prob"]
                self.cull_reason = const.UNKNOWN_CULL

            cull_time_rand = random()
            cull_reason_upper_limit = cull_reason_lower_limit = cull_time_upper_limit = cull_time_lower_limit = 0
            for i in range(len(cull_reason_cull_prob) - 1):
                if cull_reason_cull_prob[i] <= cull_time_rand < cull_reason_cull_prob[i + 1]:
                    cull_reason_lower_limit = cull_reason_cull_prob[i]
                    cull_reason_upper_limit = cull_reason_cull_prob[i + 1]
                    cull_time_lower_limit = AnimalBase.config["cull_day_count"][i]
                    cull_time_upper_limit = AnimalBase.config["cull_day_count"][i + 1]
            x = (cull_time_upper_limit - cull_time_lower_limit) / (cull_reason_upper_limit - cull_reason_lower_limit)
            self.future_cull_date = round(
                cull_time_lower_limit + x * (cull_time_rand - cull_reason_lower_limit) + self.days_born
            )
