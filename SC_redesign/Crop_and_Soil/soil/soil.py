class Soil:
    def __init__(self):
        self.evaporation = 0
        self.transpiration = 0
        self.evapotranspiration_max = 0
        self.available_water = 80
        self.water_capacity = 100

        self.lower_boundaries = [5, 8, 20]
        self.nitrates = [0.5, 1, 5]

        self.evapotranspiration = None
        self.extracted_nitrates = None
        self.total_extracted_nitrates = None
        self.water_factor = None

    def get_total_extracted_nitrates(self) -> None:
        self.total_extracted_nitrates = sum(self.extracted_nitrates)

    def remove_nitrates(self, to_be_removed: list[float]) -> None:
        length_diff = min(len(self.nitrates) - len(to_be_removed), 0)
        extracted_from_all_layers = to_be_removed + ([0] * length_diff)
        self.nitrates = [source - sink for source, sink in zip(self.nitrates, extracted_from_all_layers)]

    def update_soil_water_factor(self):
        self.water_factor = calc_soil_water_factor(self.available_water, self.water_capacity)


    def update_evapotranspiration(self):
        self.evapotranspiration = self.evaporation + self.transpiration


# ---- helper functions ---- TODO: should be moved to soil process classes
def calc_soil_water_factor(available_water: float, water_capacity: float) -> float:  # pseudocode: C.5.D.5
    """
    Description: calculates soil water factor

    Args:
        available_water: the water available in the soil profile (mm)
        water_capacity: the water accessible at field capacity (mm)

    Returns: soil water factor
    """
    return available_water / 0.85 * water_capacity