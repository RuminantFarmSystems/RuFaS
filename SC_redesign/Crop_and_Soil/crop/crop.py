from SC_redesign.Crop_and_Soil.crop.growth_constraints import GrowthConstraints
from SC_redesign.Crop_and_Soil.crop.biomass_allocation import BiomassAllocation
from SC_redesign.Crop_and_Soil.crop.nitrogen_incorporation import NitrogenIncorporation
from SC_redesign.Crop_and_Soil.crop.water_dynamics import WaterDynamics
from SC_redesign.Crop_and_Soil.crop.heat_units import HeatUnits
from SC_redesign.Crop_and_Soil.crop.leaf_area_index import LeafAreaIndex
from SC_redesign.Crop_and_Soil.soil.soil import Soil

# TODO: Should use an ENUM class to represent the supported species??

class Crop(GrowthConstraints, BiomassAllocation, WaterDynamics, NitrogenIncorporation, HeatUnits, LeafAreaIndex):
    def __init__(self):
        GrowthConstraints.__init__(self)
        BiomassAllocation.__init__(self)
        WaterDynamics.__init__(self)
        NitrogenIncorporation.__init__(self)

    def grow_crop(self, layer_nitrates: list[float], layer_depths: list[float], soil_water_factor: float,
                  max_transpiration: float, air_temperature: float,
                  incoming_light: float,
                  evaporation: float, transpiration: float, max_evapotranspiration: float,
                  mean_air_temperature: float, min_air_temperature: float, max_air_temperature: float) -> None:
        """main function for growing the crop on a daily basis

        Args:
            layer_nitrates: nitrates present in each layer of the soil profile (kg/ha)
            layer_depths: the maximum depth of each soil layer
            soil_water_factor: the soil water factor

            max_transpiration: maximum amount of transpiration possible (mm), as determined by soil, on this day
            air_temperature: current air temperature (C)

            incoming_light: incoming light radiation energy (MJ/m)

            evaporation: total evaporation occurring (mm) as determined by soil, on a given day
            transpiration: total transpiration occurring (mm) as determined by soil, on a given day
            max_evapotranspiration: maximum amount of evapotranspiration possible (mm), as determined by soil
                on a given day.

            mean_air_temperature:
            min_air_temperature:
            max_air_temperature:

        Details: grow_crop is a wrapper function for all the Crop growth process sub-routines. It should be called
        every day that the crop is alive and growing in the simulation
        """
        self.absorb_heat_units(mean_air_temperature, min_air_temperature, max_air_temperature)
        #
        # root_development_update_all()
        #
        self.incorporate_nitrogen(layer_nitrates, layer_depths, soil_water_factor)
        #
        # phosphorus_uptake.update_all()
        #
        self.constrain_growth(max_transpiration, air_temperature)
        self.grow_canopy()
        self.allocate_biomass(incoming_light)
        self.cycle_water(evaporation, transpiration, max_evapotranspiration)

# class CropSoilInterface:
#     def __init__(self):
#         self.layer_nitrates = [8.3, 6.4, 12.1]  # arbitrary
#         self.depths = [1, 5, 20]  # arbitrary
#         self.soil_water_factor = 0.5  # arbitrary
#     def get_soil_variables_needed_by_crop(self, soil: Soil):
#         self.layer_nitrates = soil.nitrates
#         self.depths = soil.depths
#         self.soil_water_factor = self.water_factor
