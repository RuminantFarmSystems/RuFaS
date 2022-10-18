from dataclasses import dataclass
from dataclasses import field


@dataclass
class ManureHandlerDailyOutput:
    """Daily output of a manure handler.

    Attributes:
        simulation_day: Number of days into the simulation.
        pen_id: ID of the pen that this output is associated with.
        urea: Urea concentration in manure, g/L.
        TAN_s: Total ammonia nitrogen concentration, g/L.
        N_manure: Amount of nitrogen in manure, kg.
        TSd: Total amount of solids, kg.
        VSd: Amount of degradable volatile solids, kg.
        VSnd: Amount of non-degradable volatile solids, kg.
        VS_total: Total amount of volatile solids, kg.
        WIP_frac: Fraction of water extractable inorganic phosphorus, dimensionless.
        WOP_frac: Fraction of water extractable organic phosphorus, dimensionless.
        p_excrt_manure: Amount of phosphorus excreted in manure, kg.
        K_manure: Amount of potassium in manure, kg.
        raw_manure: Amount of raw manure, kg.
        cleaning_water: Volume of cleaning water used in main barn, L.
        total_bedding_mass: Total amount of bedding needed for all the animals in pen, kg.
        total_water_volume_in_milking_center: Total volume of water used for
            lactating cows in the milking center, L.
        total_daily_mass: Total amount of manure, bedding, and water combined, kg.

    """
    simulation_day: int = -1
    pen_id: int = -1
    urea: float = 0.0
    TAN_s: float = 0.0
    N_manure: float = 0.0
    TSd: float = 0.0
    VSd: float = 0.0
    VSnd: float = 0.0
    VS_total: float = field(init=False)
    WIP_frac: float = 0.0
    WOP_frac: float = 0.0
    p_excrt_manure: float = 0.0
    K_manure: float = 0.0

    raw_manure: float = 0.0
    cleaning_water: float = 0.0
    total_bedding_mass: float = 0.0
    total_water_volume_in_milking_center: float = 0.0
    total_daily_mass: float = field(init=False)

    def __post_init__(self) -> None:
        """Calculate total volatile solids and total daily mass after initialization."""

        self.VS_total = self.VSd + self.VSnd

        self.total_daily_mass = sum([
            self.raw_manure,
            self.cleaning_water,
            self.total_bedding_mass,
            self.total_water_volume_in_milking_center,
        ])
