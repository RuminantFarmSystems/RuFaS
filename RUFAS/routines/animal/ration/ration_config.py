from __future__ import annotations


class RationConfig:
    """
    RationConfig provides a structured way to represent the configuration for rations.

    Attributes:

    - price: The price of each feed.
    - n: The length of the price list.
    - NEmaint: Net energy for maintenance requirement (Mcal).
    - NEa: Net energy for activity requirement (Mcal).
    - NEpreg: Net energy requirement for pregnancy (Mcal).
    - NEl: Net energy requirement for lactation (Mcal).
    - NEg: Net energy for growth requirement (Mcal).
    - MP_req: Metabolizable protein requirement for growth (g).
    - C_req: Calcium requirement (g).
    - P_req: Phosphorus requirement (g).
    - TDN: Total digestible nutrient in each feed (% of DM).
    - DE: Digestible energy in each feed (Mcal/kg).
    - EE: Ether extract, crude fat in each feed (% of DM).
    - is_fat: Indicates if the feed is a fat supplement.
    - BW: The average body weight of the pen.
    - calcium: Calcium content of each feed (% of DM).
    - phosphorus: Phosphorus content of each feed (% of DM).
    - NDF: Neutral detergent fiber in each feed (% of DM).
    - type: Feed types (Forage, Concentrate, or Mineral).
    - is_wetforage: Indicates if the feed is wet forage.
    - Kd: Rumen protein degradation rate in each feed (%/h).
    - N_A: Fraction A of protein, degraded immediately in rumen for each feed (% of CP).
    - N_B: Fraction B of protein, potentially degradable protein in rumen for each feed (% of CP).
    - CP: Crude protein in each feed (% of DM).
    - dRUP: RUP degradability in each feed (% of RUP).
    - limit: Limiting upper bounds for each feed (kg).
    - cow_type: Indicates if the cow is lactating.
    - DMIest: Dry matter intake estimation (kg).

    Methods:

    """

    def __init__(self, price_: list[float] | None = None, NEmaint_: float = 0, NEa_: float = 0, NEpreg_: float = 0,
                 NEl_: float = 0, NEg_: float = 0, MP_req_: float = 0, C_req_: float = 0, P_req_: float = 0,
                 TDN_: list[float] | None = None, DE_: list[float] | None = None, EE_: list[float] | None = None,
                 is_fat_: list[bool] | None = None, BW_: float = 0, calcium_: list[float] | None = None,
                 phosphorus_: list[float] | None = None, NDF_: list[float] | None = None,
                 type_: list[str] | None = None, is_wetforage_: list[bool] | None = None,
                 Kd_: list[float] | None = None, N_A_: list[float] | None = None, N_B_: list[float] | None = None,
                 CP_: list[float] | None = None, dRUP_: list[float] | None = None,
                 limit_: list[float] | None = None, cow_type_: bool = False, DMIest_: float | None = None) -> None:
        """
        Initialize the RationConfig class with the provided feed information. If the input
        is a list, it should have a length corresponding to the decision vector.

        Parameters
        ----------
        price_ : list, optional
            The price of each feed.
        NEmaint_ : float, optional
            Net energy for maintenance requirement (Mcal).
        NEa_ : float, optional
            Net energy for activity requirement (Mcal).
        NEpreg_ : float, optional
            Net energy requirement for pregnancy (Mcal).
        NEl_ : float, optional
            Net energy requirement for lactation (Mcal).
        NEg_ : float, optional
            Net energy for growth requirement (Mcal).
        MP_req_ : float, optional
            Metabolizable protein requirement for growth (g).
        C_req_ : float, optional
            Calcium requirement (g).
        P_req_ : float, optional
            Phosphorus requirement (g).
        TDN_ : list, optional
            Total digestible nutrient in each feed (% of DM).
        DE_ : list, optional
            Digestible energy in each feed (Mcal/kg).
        EE_ : list, optional
            Ether extract, crude fat in each feed (% of DM).
        is_fat_ : list of bool, optional
            Indicates if the feed is a fat supplement (yes = True; no = False).
        BW_ : float, optional
            The average body weight of the pen.
        calcium_ : list, optional
            Calcium content of each feed (% of DM).
        phosphorus_ : list, optional
            Phosphorus content of each feed (% of DM).
        NDF_ : list, optional
            Neutral detergent fiber in each feed (% of DM).
        type_ : list, optional
            Feed types (Forage, Concentrate, or Mineral).
        is_wetforage_ : list of bool, optional
            Indicates if the feed is wet forage (yes = True; no = False).
        Kd_ : list, optional
            Rumen protein degradation rate in each feed (%/h).
        N_A_ : list, optional
            Fraction A of protein, degraded immediately in rumen for each feed (% of CP).
        N_B_ : list, optional
            Fraction B of protein, potentially degradable protein, requires time to degrade in rumen for each feed (% of CP).
        CP_ : list, optional
            Crude protein in each feed (% of DM).
        dRUP_ : list, optional
            RUP degradability in each feed (% of RUP).
        limit_ : list, optional
            Limiting upper bounds for each feed (kg).
        cow_type_ : bool, optional
            True if the cow is lactating, False otherwise.
        DMIest_ : float, optional
            Dry matter intake estimation (kg).

        Returns
        -------
        None
        """

        self.price = price_ if price_ is not None else []
        self.n = len(self.price)
        self.NEmaint = NEmaint_
        self.NEa = NEa_
        self.NEpreg = NEpreg_
        self.NEl = NEl_
        self.NEg = NEg_
        self.MP_req = MP_req_
        self.C_req = C_req_
        self.P_req = P_req_
        self.TDN = TDN_ if TDN_ is not None else []
        self.DE = DE_ if DE_ is not None else []
        self.EE = EE_ if EE_ is not None else []
        self.is_fat = is_fat_ if is_fat_ is not None else []
        self.BW = BW_
        self.calcium = calcium_ if calcium_ is not None else []
        self.phosphorus = phosphorus_ if phosphorus_ is not None else []
        self.NDF = NDF_ if NDF_ is not None else []
        self.type = type_ if type_ is not None else []
        self.is_wetforage = is_wetforage_ if is_wetforage_ is not None else []
        self.Kd = Kd_ if Kd_ is not None else []
        self.N_A = N_A_ if N_A_ is not None else []
        self.N_B = N_B_ if N_B_ is not None else []
        self.CP = CP_ if CP_ is not None else []
        self.dRUP = dRUP_ if dRUP_ is not None else []
        self.limit = limit_ if limit_ is not None else []
        self.cow_type = cow_type_
        self.DMIest = DMIest_

