from typing import Dict

from RUFAS.general_constants import GeneralConstants
from RUFAS.output_manager import OutputManager
from RUFAS.routines.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.routines.animal.life_cycle import animal_constants as const
from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase
from RUFAS.routines.animal.life_cycle.calf import Calf
from RUFAS.routines.animal.manure.growing_heifer_manure_excretion import manure_calculations
from RUFAS.routines.animal.ration.animal_requirements import AnimalRequirements

om = OutputManager()


class HeiferI(Calf):
    def __init__(self, args):
        """
        initialize the 1st heifer group from calf information

        Parameters
        ----------
        args.id: id of the animal
        args.breed: breed of the animal
        args.birth_date: the date of the simulation when the calf was born
        args.daysBorn: age of the animal
        (optional: include the following to assign animal information)
        args.birth_weight: the birth weight of the animal
        args.body_weight: current body weight of the animal
        args.wean_weight: the wean weight of the animal
        args.mature_body_weight: the mature body weight of the animal
        args.events: events of the animal
        """
        super().__init__(args)

    def get_heiferI_values(self):
        """
        Get current information from the heiferI
        """
        return self.get_calf_values()

    def set_nutrient_rqmts(
        self,
        temperature: float,
        animal_grouping_scenario,
        nutrient_conc: Dict[str, float] = {},
        metabolizable_energy: float = 15.625,
        previous_DMI: float = 10.0,
    ) -> None:
        """
        Calculates this heiferI's nutrient requirements.
        """
        if metabolizable_energy == 0.0:
            metabolizable_energy = 15.625
        if previous_DMI == 0.0:
            previous_DMI = 10.0
        if nutrient_conc and nutrient_conc["dm"] != 0.0:
            NDF_conc = nutrient_conc["NDF"] / 100
            TDN_conc = nutrient_conc["TDN"] / 100
            net_energy_diet_concentration = (metabolizable_energy * 0.64) / previous_DMI
        else:
            NDF_conc = 0.3
            TDN_conc = 0.7
            net_energy_diet_concentration = 1.0
        req = AnimalRequirements()
        animal_requirements = req.calc_rqmts(
            body_weight=self.body_weight,
            mature_body_weight=self.mature_body_weight,
            day_of_pregnancy=None,
            animal_type=animal_grouping_scenario.get_animal_type(self),
            body_condition_score_5=3,
            previous_temperature=temperature,
            average_daily_gain_heifer=self.daily_growth,
            NDF_conc=NDF_conc,
            TDN_conc=TDN_conc,
            net_energy_diet_concentration=net_energy_diet_concentration,
            days_born=self.days_born,
        )

        self.NEmaint_requirement = animal_requirements["NEmaint_requirement"]
        self.NEg_requirement = animal_requirements["NEg_requirement"]
        self.NEpreg_requirement = animal_requirements["NEpreg_requirement"]
        self.NEl_requirement = animal_requirements["NEl_requirement"]
        self.MP_requirement = animal_requirements["MP_requirement"]
        self.Ca_requirement = animal_requirements["Ca_requirement"]
        self.P_requirement = animal_requirements["P_requirement"]
        self.DMIest_requirement = animal_requirements["DMIest_requirement"]
        self.essential_amino_acid_requirement = animal_requirements["essential_amino_acid_requirement"]

    def calc_manure_excretion(
        self, methane_model: str, nutrient_amount: Dict[str, float], nutrient_conc: Dict[str, float]
    ) -> None:
        """
        Calculates and sets the manure excretion components.

        Parameters
        ----------
        methane_model : str
            Methane model used for methane emission calculations, including Boadi, IPCC.
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
        self.p_excrt, self.manure_excretion = manure_calculations(
            self.body_weight,
            p_feces_excrt,
            p_urine,
            methane_model,
            nutrient_amount=nutrient_amount,
            nutrient_conc=nutrient_conc,
        )

    def phosphorus_rqmts(self, DMI: float) -> None:
        """
        Calculates and sets the animal's phosphorus requirement.

        Parameters
        ----------
        DMI : float
            Dry Matter Intake (kg).
        """
        # amount of P required for endogenous losses (g) (A.1A-D.E.1)
        self.p_maint_feces = 0.0008 * DMI * GeneralConstants.KG_TO_GRAMS

        # amount of P required for urine production (g) (A.1A-F.E.2)
        p_urine = 0.000002 * self.body_weight * GeneralConstants.KG_TO_GRAMS

        # absorbed P retained for growth (g) (A.1A-F.E.3)
        self.p_growth = (
            (0.0012 + 0.004635 * (self.mature_body_weight**0.22) * (self.body_weight ** (-0.22)))
            * self.daily_growth
            / 0.96
            * GeneralConstants.KG_TO_GRAMS
        )

        # absorbed P required by the animal (g) (A.1A-F.E.6)
        p_absorb = p_urine + self.p_maint_feces + self.p_growth

        # requirement of P from the ration (g) (A.1B-D.E.7)
        self.p_req = p_absorb / 0.664

    def get_non_preg_bw_change(self) -> float:
        """
        Calculates the body weight change for a heifer that is not pregnant.
        If the days_born of the animal is equal to 400,
        the difference is set to 1 (otherwise results in a division by 0 error).

        Notes
        -----
        Calculation is [A.1A.C.6] in pseudocode, itself from  Fox et al. 1999 and NRC 2001.
        However, for animals over 55% of their mature body weight, the equation results in a negative return.
        Therefore when the result is negative, the minimum BW change constant is returned instead.

        Returns
        -------
        float
            The daily body weight change for a heifer that is not pregnant.
        """
        divisor = abs(AnimalBase.config["target_heifer_preg_day"] - self.days_born)
        if divisor == 0:
            divisor = 1
        return max(
            (0.55 * 0.96 * self.mature_body_weight - 0.96 * self.body_weight) / divisor,
            AnimalModuleConstants.MINIMUM_HEIFER_DAILY_GROWTH_RATE,
        )

    def update(self, sim_day: int) -> bool:
        """
        Controls heifer's grow with average daily gain based on non-preg ADG based on NRC.
        Here is the place to change growth rate with heifer feeding methods later
        when we have heifer nutrition from the ration formulation module.
        Once reach the breeding start day,
        this heifer would be move to next stage, the heiferII stage.

        Parameters
        ----------
        sim_day : int
            Day of simulation.

        Returns
        -------
        bool
            True if should be moved to second stage of heifer -- breeding stage starts.
        """

        self.update_body_weight_history(sim_day)
        second_stage = False

        self.daily_growth = self.get_non_preg_bw_change()

        self.body_weight += self.daily_growth

        self.days_born += 1
        if self.days_born == AnimalBase.config["breeding_start_day_h"]:
            second_stage = True
            self.events.add_event(self.days_born, sim_day, const.BREEDING_START)
            self.days_born -= 1  # will increment in next stage again

        return second_stage
