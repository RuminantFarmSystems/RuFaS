from __future__ import annotations

from typing import List

import numpy as np


class RationConfig:
    """
    RationConfig provides a structured way to represent the collection of animal requirements and feed supply
    information for the ration formulation process.

    Attributes
    ----------
    price_list : list
        The price of each feed.
    NEmaint_requirement : float
        Net energy for maintenance requirement (Mcal).
    NEa_requirement : float
        Net energy for activity requirement (Mcal).
    NEpreg_requirement : float
        Net energy requirement for pregnancy (Mcal).
    NEl_requirement : float
        Net energy requirement for lactation (Mcal).
    NEg_requirement : float
        Net energy for growth requirement (Mcal).
    MP_requirement : float
        Metabolizable protein requirement for growth (g).
    C_requirement : float
        Calcium requirement (g).
    P_requirement : float
        Phosphorus requirement (g).
    P_requirement_process : float
        Phosphorus requirement (g).
    TDN_list : list
        Total digestible nutrient in each feed (% of DM).
    DE_list : list
        Digestible energy in each feed (Mcal/kg).
    EE_list : list
        Ether extract, crude fat in each feed (% of DM).
    is_fat_list : list of bool
        Indicates if the feed is a fat supplement (yes = True; no = False).
    BW_list : float
        The average body weight of the pen.
    calcium_list : list
        Calcium content of each feed (% of DM).
    phosphorus_list : list
        Phosphorus content of each feed (% of DM).
    NDF_list : list
        Neutral detergent fiber in each feed (% of DM).
    feed_type_list : list
        Feed types (Forage, Concentrate, or Mineral).
    is_wetforage_list : list of bool
        Indicates if the feed is wet forage (yes = True; no = False).
    Kd_list : list
        Rumen protein degradation rate in each feed (%/h).
    N_A_list : list
        Fraction A of protein, degraded immediately in rumen for each feed (% of CP).
    N_B_list : list
        Fraction B of protein, potentially degradable protein, requires time to degrade
        in rumen for each feed (% of CP).
    CP_list : list
        Crude protein in each feed (% of DM).
    dRUP_list : list
        RUP degradability in each feed (% of RUP).
    feed_limit_list : list
        Limiting upper bounds for each feed (kg).
    lactating : bool
        True if the cow is lactating, False otherwise.
    DMIest_requirement : float
        Dry matter intake estimation (kg).
    MEact_list : list
        Actual metabolizable energy for each feed (Mcal/kg)
    NEgact_list : list
        Actual net energy for growth for each feed (Mcal/kg)
    NEm_act_list : list
        Actual net energy for maintenance for each feed (Mcal/kg)
    is_forage_list : list
        Boolean if feed item is forage or not
    MPbact_list : list
        Metabolizable bacterial protein production for each feed (g)
    RUP_diet_list : list
        Rumen undegradable protein for each feed (% of DM)
    dP_list : list
        P digestibility for each feed (proportion of P)
    TDNact_list : list
        Actual dietary total digestible nutrient for each feed (kg)
    dCa_list : list
        Calcium digesibility of feed (proportion of Ca)
    Methods
    -------
    None.

    """

    def __init__(
        self,
        price__list: list[float] = [],
        NEmaint__requirement: float = 0,
        NEa__requirement: float = 0,
        NEpreg__requirement: float = 0,
        NEl__requirement: float = 0,
        NEg__requirement: float = 0,
        MP__requirement: float = 0,
        C__requirement: float = 0,
        P__requirement: float = 0,
        P__process__requirement: float = 0,
        TDN__list: list[float] = [],
        DE__list: list[float] = [],
        EE__list: list[float] = [],
        is_fat__list: list[bool] = [],
        BW_: float = 0,
        calcium__list: list[float] = [],
        phosphorus__list: list[float] = [],
        NDF__list: list[float] = [],
        feed_type__list: list[str] = [],
        is_wetforage__list: list[bool] = [],
        Kd__list: list[float] = [],
        N_A__list: list[float] = [],
        N_B__list: list[float] = [],
        CP__list: list[float] = [],
        dRUP__list: list[float] = [],
        feed_minimum__list: list[float] = [],
        feed_limit__list: list[float] = [],
        lactating_: bool = False,
        DMIest__requirement: float = 0.0,
    ) -> None:
        """
        Initialize the RationConfig class with the provided feed information. If the input
        is a list, it should have a length corresponding to the decision vector.

        Parameters
        ----------
        price__list : list, default []
            The price of each feed.
        NEmaint__requirement : float, default 0
            Net energy for maintenance requirement (Mcal).
        NEa__requirement : float, default 0
            Net energy for activity requirement (Mcal).
        NEpreg__requirement : float, default 0
            Net energy requirement for pregnancy (Mcal).
        NEl__requirement : float, default 0
            Net energy requirement for lactation (Mcal).
        NEg__requirement : float, default 0
            Net energy for growth requirement (Mcal).
        MP__requirement : float, default 0
            Metabolizable protein requirement for growth (g).
        C__requirement : float, default 0
            Calcium requirement (g).
        P__requirement : float, default 0
            Phosphorus requirement (g) as calculated by NRC or NASEM.
        P__process__requirement : float, default 0
            Phosphorus requirement (g) as calculated by process-based P methods.
        TDN__list : list, default []
            Total digestible nutrient in each feed (% of DM).
        DE__list : list, default []
            Digestible energy in each feed (Mcal/kg).
        EE__list : list, default []
            Ether extract, crude fat in each feed (% of DM).
        is_fat__list : list of bool, default []
            Indicates if the feed is a fat supplement (yes = True; no = False).
        BW_ : float, default 0
            The average body weight of the pen.
        calcium__list : list, default []
            Calcium content of each feed (% of DM).
        phosphorus__list : list, default []
            Phosphorus content of each feed (% of DM).
        NDF__list : list, default []
            Neutral detergent fiber in each feed (% of DM).
        feed_type__list : list, optional
            Feed types (Forage, Concentrate, or Mineral).
        is_wetforage__list : list of bool, default []
            Indicates if the feed is wet forage (yes = True; no = False).
        Kd__list : list, default []
            Rumen protein degradation rate in each feed (%/h).
        N_A__list : list, default []
            Fraction A of protein, degraded immediately in rumen for each feed (% of CP).
        N_B__list : list, default []
            Fraction B of protein, potentially degradable protein, requires time to degrade
            in rumen for each feed (% of CP).
        CP__list : list, default []
            Crude protein in each feed (% of DM).
        dRUP__list : list, default []
            RUP degradability in each feed (% of RUP).
        feed_limit__list : list, default []
            Limiting upper bounds for each feed (kg).
        feed_minimum_list : list, default []
            Limiting lower bounds for each feed (kg).
        lactating_ : bool, default False
            True if the cow is lactating, False otherwise.
        DMIest__requirement : float, default []
            Dry matter intake estimation (kg).

        Returns
        -------
        None
        """

        self.price_list = price__list
        self.NEmaint_requirement = NEmaint__requirement
        self.NEa_requirement = NEa__requirement
        self.NEpreg_requirement = NEpreg__requirement
        self.NEl_requirement = NEl__requirement
        self.NEg_requirement = NEg__requirement
        self.MP_requirement = MP__requirement
        self.C_requirement = C__requirement
        self.P_requirement = P__requirement
        self.P_requirement_process = P__process__requirement
        self.TDN_list = TDN__list
        self.DE_list = DE__list
        self.EE_list = EE__list
        self.is_fat_list = is_fat__list
        self.BW = BW_
        self.calcium_list = calcium__list
        self.phosphorus_list = phosphorus__list
        self.NDF_list = NDF__list
        self.feed_type_list = feed_type__list
        self.is_wetforage_list = is_wetforage__list
        self.Kd_list = Kd__list
        self.N_A_list = N_A__list
        self.N_B_list = N_B__list
        self.CP_list = CP__list
        self.dRUP_list = dRUP__list
        self.feed_minimum_list = feed_minimum__list
        self.feed_limit_list = feed_limit__list
        self.lactating = lactating_
        self.DMIest_requirement = DMIest__requirement

    Discount: float = 0
    TDNact_diet: float = 0

    TDNact_list: List[float] | np.ndarray = []
    DEact_list: List[float] | np.ndarray = []
    MEact_list: List[float] = []

    NEm_act_list: List[float] | np.ndarray = []
    NElact_list: List[float] | np.ndarray = []
    NEgact_list: List[float] = []
    is_forage_list: List[float] | np.ndarray = []

    dP_list: List[float] = []
    dCa_list: List[float] = []
    is_conc_list: List[int] = []

    RDP_list: List[float] | np.ndarray = []
    RUP_list: List[float] | np.ndarray = []
    MPbact: float = 0
    RUP_diet: float = 0
    RDP_diet: float = 0
    MP_supply: float = 0
