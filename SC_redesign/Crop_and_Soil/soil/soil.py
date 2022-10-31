class Soil:
    def __init__(self):
        self.evaporation = 0
        self.transpiration = 0
        self.evapotranspiration_max = 0
        self.evapotranspiration = None

        self.lower_boundaries = [5, 8, 20]
        self.nitrates = [0.5, 1, 5]

    def update_evapotranspiration(self):
        self.evapotranspiration = self.evaporation + self.transpiration
