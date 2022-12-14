from SC_redesign.Crop_and_Soil.crop.crop import Crop
from SC_redesign.Crop_and_Soil.soil.soil import Soil


class Field:
    def __init__(self):
        # soil attributes
        self.soil = None
        """the soil of the field"""
        self.is_amendment_day = False
        """should nutrients be added to the soil today?"""
        self.is_tillage_day = False
        """should the soil be tilled today?"""

        # crop attributes
        self.crops = []  # empty crop list
        """crops currently in the field"""
        self.crop_proportions = []  # empty composition list
        """proportion of the field's area that each crop occupies"""
        self.priorities = []
        """the priorities of each crop for obtaining nutrients from a given soil layer"""
        self.is_planting_day = False
        """is today the day to plant new crops?"""
        self.is_cutting_day = False
        """is today the day to cut crops in the field?"""
        self.harvest_proportion = 1
        """the proportion of cut crop biomass that will be removed from the field"""

    def manage_field(self) -> None:
        """main Field function, runs all field routines based on current attribute configuration
                **All the logic will go in this function**
        """
        pass

    # ---- Soil Management ----
    def setup_soil(self, soil_config) -> None:
        """set up the soil for this field"""
        self.soil = Soil.make_from_config(soil_config)

    def till_soil(self, tillage_config) -> None:
        """till the soil"""
        pass

    def amend_soil(self, amendment_config) -> None:
        """ammend the soil with nutrients"""
        pass

    # ... other Soil management methods

    # ---- Crop Management ----
    def plant_crops(self, crop_config) -> None:
        """plant all crops for the field"""
        # for sp in crop_config.species:
        #     self.add_crop(sp)
        pass

    def add_crop(self, species: str, field_cover: float = 1.0, priority: int = 1) -> None:
        """add a crop to the field"""
        if sum(self.crop_proportions) + field_cover > 1:
            ValueError("Desired proportion of field not available")
        self.crops.append(Crop.plant_species(species))
        self.crop_proportions.append(field_cover)
        self.priorities.append(priority)

    def grow_crops(self) -> None:
        """grow crops in the field. Resources will be transferred from the soil to the crops"""
        # [c.grow_crop(...) for c in self.crops]
        pass

    def cut_crops(self):
        """cut all crops in the field, either removing the cut biomass as harvest
        or leaving it in the field as residue to be incorporated into the soil depending upon 'harvest_percent'
        """
        cuttings = [c.cut() for c in self.crops]
        if self.harvest_proportion > 0:
            # ... remove cut biomass from field
            pass
        else:
            # ... leave cut biomass in field as residue
            pass
        # ... kill crops if not perennial
        pass

    @property
    def _composition_sums_to_one(self) -> bool:
        """ensure that the crop_proportions values sum to 1"""
        return sum(self.crop_proportions) == 1.0
