import math
from enum import Enum
from typing import Any, Dict
from RUFAS.data_structures.feed_storage_to_animal_connection import Feed
from RUFAS.general_constants import GeneralConstants


"""RuFaS IDs for supported calf feeds."""
WHOLE_MILK_ID = 202
MILK_REPLACER_ID = 203
STARTER_ID = 216


class CalfMilkType(Enum):
    """Calf milk types."""

    WHOLE = "whole"
    REPLACER = "replacer"


class CalfRationManager:
    """
    Calf ration formulation is distinct from other animal types, and managed separately.
    Note that the ration formulated is a fixed ration; requirements used only for reporting

    """

    milk_type: CalfMilkType

    @classmethod
    def set_milk_type(cls, milk_type: CalfMilkType) -> None:
        """
        Set the milk type for the calf.

        Parameters
        ----------
        milk_type : CalfMilkType
            The type of milk being fed to the calf.

        """
        cls.milk_type = milk_type

    @classmethod
    def _get_ration(cls) -> Dict[str, float | str]:
        """
        Harcoded calf ration.

        Returns
        -------
        Dict[str, float | str]
            Dictionary of formulated ration.

        """
        return {"202": 1, "216": 2, "status": "Optimal", "objective": 4.5}

    @classmethod
    def optimize(cls) -> Dict[str, float | str]:
        """ "
        Returns "optimized" calf ration.

        Notes
        -----
        Use of calf nutrient requirements not implemented, hardcoded ration is returned.

        Returns
        -------
        Dictionary of formulated ration.

        """
        return cls._get_ration()

    @classmethod
    def calc_requirements(
        cls,
        calf,
        feed: Dict[str, float],
        temp: float,
        animal_intake: Dict[str, int | float],
    ) -> Dict[str, Dict[str, Any]]:
        """
        Calculate dietary intake and nutrient requirements for the calf.

        Parameters
        ----------
        calf : Calf
            Calf object
        feed : Dict[str, float]
            Instance of Feed class defined in feed.py.
        temp : float
            Average temperature of the simulation day, C.
        animal_intake : Dict
            Dictionary of calculated intake values.

        Returns
        -------
        Dict[str,  Dict[str, Any]]
            Dictionary of requirement values and methods.

        """

        whole_milk_intake = animal_intake["whole_milk_intake"]
        milk_replacer_intake = animal_intake["milk_replacer_intake"]
        starter_intake = animal_intake["starter_intake"]
        dm_intake = animal_intake["dm_intake"]
        me_intake = animal_intake["me_intake"]
        cp_intake = animal_intake["cp_intake"]
        adp_intake = animal_intake["adp_intake"]
        milk_me_proportion = animal_intake["milk_me_proportion"]
        starter_me_proportion = animal_intake["starter_me_proportion"]
        milk_proportion = animal_intake["milk_proportion"]
        starter_proportion = animal_intake["starter_proportion"]

        # nutrient composition of feeds from the feed library
        whole_milk_id = 202
        milk_replacer_id = 203
        starter_id = 216
        calf_feeds = feed.calf_feeds

        whole_milk_cp = calf_feeds[whole_milk_id]["CP"]
        de_key = "DE_Base" if "DE_Base" in calf_feeds[whole_milk_id].keys() else "DE"
        whole_milk_de = calf_feeds[whole_milk_id][de_key]
        milk_replacer_de = calf_feeds[milk_replacer_id][de_key]
        starter_de = calf_feeds[starter_id][de_key]

        # [A.1B.C.1]
        whole_milk_me = 0.96 * whole_milk_de

        milk_replacer_cp = calf_feeds[milk_replacer_id]["CP"]

        # [A.1B.C.1]
        milk_replacer_me = 0.96 * milk_replacer_de

        starter_cp = calf_feeds[starter_id]["CP"]

        starter_ee = calf_feeds[starter_id]["EE"]
        # [A.1B.C.2]
        starter_me = (1.01 * starter_de - 0.45) + 0.0046 * (starter_ee - 3)

        # [A.1B.C.5]
        milk_me_proportion = (whole_milk_intake * whole_milk_me + milk_replacer_intake * milk_replacer_me) / me_intake
        # [A.1B.C.6]
        starter_me_proportion = starter_intake * starter_me / me_intake

        # [A.1B.E.2]
        milk_cp_intake = 0.01 * (whole_milk_cp * whole_milk_intake + milk_replacer_cp * milk_replacer_intake)
        starter_cp_intake = 0.01 * starter_cp * starter_intake

        # [A.1B.D.2]
        milk_proportion = (whole_milk_intake + milk_replacer_intake) / dm_intake
        # [A.1B.D.3]
        starter_proportion = starter_intake / dm_intake

        # maintainance requirements
        # [A.1B.F.1]
        t_factor = 0
        if calf.days_born <= 60:
            if temp < -30:
                t_factor = 1.34
            elif temp < 15:
                t_factor = -0.0272 * temp + 0.4751
        else:
            if temp < -30:
                t_factor = 1.07
            elif temp <= 5:
                t_factor = -0.0271 * temp + 0.2002

        # [A.1B.F.2]
        ne_maint = 0.086 * calf.body_weight**0.75 * (1 + t_factor)
        # [A.1B.F.3]
        me_maint = ne_maint / (0.86 * milk_proportion + 0.75 * starter_proportion)

        # [A.1B.G.1]
        bio_val = 0.8 * milk_cp_intake / cp_intake + 0.7 * starter_cp_intake / cp_intake

        # [A.1B.G.2]
        endo_urine_N = 0.0002 * calf.body_weight**0.75 * 1000
        # [A.1B.G.3]
        meta_fecal_N = (0.0019 * (whole_milk_intake + milk_replacer_intake) + 0.0033 * starter_intake) * 1000

        # [A.1B.G.4]
        adp_maint = 6.25 * (1 / bio_val * (endo_urine_N + meta_fecal_N) - meta_fecal_N)

        # growth requirements
        # [A.1B.H.1]
        me_gain = me_intake - me_maint
        # [A.1B.H.2]
        ne_gain = me_gain * (0.69 * milk_me_proportion + 0.57 * starter_me_proportion)

        # [A.1B.H.3]
        energy_allow_gain = 0
        if ne_gain >= 0:
            energy_allow_gain = math.exp(0.833 * math.log((1.19 * ne_gain) / (0.69 * calf.body_weight**0.355)))

        # [A.1B.H.4]
        adp_allow_gain = (adp_intake - adp_maint) * bio_val / 0.188 * 0.001
        # [A.1B.H.5]
        live_weight_change = min(energy_allow_gain, adp_allow_gain)

        nutrient_requirements = {
            "ne_maint": {"op": "=", "val": ne_maint},
            "me_maint": {"op": "=", "val": me_maint},
            "bio_val": {"op": "=", "val": bio_val},
            "endo_urine_N": {"op": "=", "val": endo_urine_N},
            "meta_fecal_N": {"op": "=", "val": meta_fecal_N},
            "adp_maint": {"op": "=", "val": adp_maint},
            "me_gain": {"op": "=", "val": me_gain},
            "ne_gain": {"op": "=", "val": ne_gain},
            "energy_allow_gain": {"op": "=", "val": energy_allow_gain},
            "adp_allow_gain": {"op": "=", "val": adp_allow_gain},
            "live_weight_change": {"op": "=", "val": live_weight_change},
        }

        return nutrient_requirements

    @classmethod
    def calc_intake(
        cls, birth_weight: float, body_weight: float, wean_day: int, wean_length: int, available_feeds: list[Feed]
    ) -> dict[str, float]:
        """
        Calculates the amounts of whole milk, milk replacer, and starter that a calf consumes.

        Parameters
        ----------
        birth_weight : float
            Birth weight of the calf (kg).
        body_weight : float
            Body weight of the calf (kg).
        wean_day : int
            Number of days after birth that calf is fully weaned from milk (or replacer).
        wean_length : int
            Wean length of the calf (days).
        available_feeds : list[Feed]
            List of feeds available to the calf.

        Returns
        -------
        dict[str, float]
            Amounts of feed taken in by calf and nutritive content of the intake.

        References
        ----------
        Animal Scientific Documentation [A.1B]

        """

        whole_milk = next(feed for feed in available_feeds if feed.rufas_id == WHOLE_MILK_ID)
        milk_replacer = next(feed for feed in available_feeds if feed.rufas_id == MILK_REPLACER_ID)
        starter = next(feed for feed in available_feeds if feed.rufas_id == STARTER_ID)

        whole_milk_metabolizable_energy = 0.96 * whole_milk.DE
        milk_replacer_metabolizable_energy = 0.96 * milk_replacer.DE
        starter_metabolizable_energy = (1.01 * starter.DE - 0.45) + 0.0046 * (starter.DE - 3)

        wean_start = wean_day - wean_length - 1
        milk_reduct = round(0.5 * wean_length)
        wean_fraction = 1 - milk_reduct / (wean_length + 1)

        if cls.milk_type == CalfMilkType.WHOLE:
            whole_milk_intake = 0.1 * birth_weight * whole_milk.DM * GeneralConstants.PERCENTAGE_TO_FRACTION
            milk_replacer_intake = 0.0
            milk_intake_wean = whole_milk_intake * wean_fraction
        else:
            whole_milk_intake = 0.0
            milk_replacer_intake = 0.1 * birth_weight * milk_replacer.DM * GeneralConstants.PERCENTAGE_TO_FRACTION
            milk_intake_wean = milk_replacer_intake * wean_fraction

        if body_weight <= 50.0:
            starter_intake = 0.01
        elif 50.0 < body_weight <= 69.365:
            starter_intake = -0.24783 + 0.0049567 * body_weight
        else:
            starter_intake = -6.2263 + 0.091145 * body_weight

        dry_matter_intake = whole_milk_intake + milk_replacer_intake + starter_intake

        milk_me_intake = (
            whole_milk_metabolizable_energy * whole_milk_intake
            + milk_replacer_metabolizable_energy * milk_replacer_intake
        )
        starter_me_intake = starter_metabolizable_energy * starter_intake
        me_intake = milk_me_intake + starter_me_intake

        milk_me_proportion = milk_me_intake / me_intake
        starter_me_proportion = starter_me_intake / me_intake

        milk_cp_intake = GeneralConstants.PERCENTAGE_TO_FRACTION * (
            whole_milk.CP * whole_milk_intake + milk_replacer.CP * milk_replacer_intake
        )
        starter_cp_intake = GeneralConstants.PERCENTAGE_TO_FRACTION * starter.CP * starter_intake
        total_cp_intake = milk_cp_intake + starter_cp_intake

        adp_intake = (0.93 * milk_cp_intake / total_cp_intake + 0.75 * starter_cp_intake / total_cp_intake) * 1000

        milk_proportion = (whole_milk_intake + milk_replacer_intake) / dry_matter_intake
        starter_proportion = starter_intake / dry_matter_intake

        animal_intake = {
            "whole_milk_intake": whole_milk_intake,
            "milk_replacer_intake": milk_replacer_intake,
            "starter_intake": starter_intake,
            "wean_start": wean_start,
            "milk_reduction": milk_reduct,
            "milk_intake_wean": milk_intake_wean,
            "dry_matter_intake": dry_matter_intake,
            "me_intake": me_intake,
            "cp_intake": total_cp_intake,
            "adp_intake": adp_intake,
            "milk_me_proportion": milk_me_proportion,
            "starter_me_proportion": starter_me_proportion,
            "milk_proportion": milk_proportion,
            "starter_proportion": starter_proportion,
        }

        return animal_intake
