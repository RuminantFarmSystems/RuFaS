from SC_redesign.Crop_and_Soil.crop.growth_constraints import GrowthConstraints
from SC_redesign.Crop_and_Soil.crop.biomass_allocation import BiomassAllocation
from SC_redesign.Crop_and_Soil.crop.nitrogen_incorporation import NitrogenIncorporation
from SC_redesign.Crop_and_Soil.crop.water_dynamics import WaterDynamics


class Crop(GrowthConstraints, BiomassAllocation, WaterDynamics, NitrogenIncorporation):
    def __init__(self):
        super().__init__()



    # def grow(self):
    #     heat_units.update_all()
    #
    #     root_developement_update_all()
    #
    #     nitrogen_uptake.update_all()
    #
    #     phosphorus_uptake.update_all()
    #
    #     # growth_constraints.update_all()
    #     self.constrain_growth()
    #
    #     leaf_area_index.update_all()
    #
    #     # biomass.allocate_biomass()
    #     self.allocate_biomass(light)
    #     self.cycle_water()

