from typing import Optional
from SC_redesign.Crop_and_Soil.crop.crop_data import CropData

"""
This module is based on the crop-related aspects of SWAT 6.1 'General Management'.

The CropManagement class is a component class of the Crop composite and serves as the foundation for
planting (6:1.1), Cutting/Harvesting (6:1.2, 6:1.5), Grazing (6:1.3), Crop death (6:1.4, 6:1.5), and
end of growing season (6:1.5)
"""

# TODO: This class will likely need to be reconciled with yields.py

class CropManagement():
    def __int__(self, crop_data: Optional[CropData] = None):
        self.data = crop_data or CropData()

    # TODO: implement cut() and kill() methods - GitHub Issue #248
    #   the old versions are pasted in the comment blocks below.
    #   these method (or a similar harvest method) will eventually need to call
    #   obtain_yields()
    def cut(self, fraction: float, allow_below_ground: bool = True,
            death_threshold: float = 0.0) -> float:
        """

        Args:
            fraction: the fraction of above-ground biomass to be cut
            allow_below_ground: should fraction > 1 be allowed to remove from below-ground biomass?
            death_threshold: the biomass threshold below which the plant will die (kg/ha)

        Returns: The total biomass removed from the plant (kg/ha)

        Details: if fraction is greater than 1 and the roots are allowed to be cut, then all of the above ground
            biomass is removed and any remainder is removed from below ground. Otherwise, only the above ground
            portion gets cut.

            The output of this function is the biomass removed, which should be redirected depending on the use case
            (i.e., converted to residue, removed as economic yield, consumed by grazer, etc.)

        """
        exceeds_available = fraction > 1.0

        if exceeds_available and allow_below_ground:  # cut into entire plant
            below_frac = fraction - 1.0
            self.data.above_ground_biomass = 0.0
            self.data.root_biomass -= max(self.data.root_biomass, below_frac*self.data.root_biomass)

        else:  # don't cut more than available above ground
            self.data.above_ground_biomass -= max(self.data.above_ground_biomass,
                                                  fraction*self.data.above_ground_biomass)

        # update biomass features
        og_biomass = self.data.biomass  # original for comparison
        self.data.biomass = self.data.above_ground_biomass + self.data.root_biomass

        # kill the crop if too much biomass is removed
        if self.data.biomass > death_threshold:
            self.kill()

        return og_biomass - self.data.biomass

    def kill(self) -> None:
        """kill the plant, preventing it from growing"""
        self.data.is_alive = False

    def harvest(self):
        """harvests the crop's cut yield biomass"""
        pass
