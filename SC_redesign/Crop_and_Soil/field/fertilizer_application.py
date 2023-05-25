from typing import Optional

from SC_redesign.Crop_and_Soil.soil.soil import Soil

"""
This module provides a way for Field to apply fertilizer, based on SWAT Theoretical documentation section 6:1.7.
"""


class FertilizerApplication:

    def __init__(self, soil: Optional[Soil] = None, field_size: Optional[float] = None):
        """This method initializes the Soil object that this module will work with, or create one if none provided.

        Parameters
        ----------
        field_size : float, optional
            Used to initialize a Soil object for this module to work with, if a pre-configured SoilData object is not
            provided (ha)

        """
        self.soil = soil or Soil(field_size=field_size)

    def apply_fertilizer(self, phosphorus_applied: float, fertilizer_mass: float, inorganic_nitrogen_fraction: float,
                         ammonium_fraction: float, organic_nitrogen_fraction: float, field_size: float) -> None:
        """
        Applies nutrients to the soil through fertilizer.

        Parameters
        ----------
        phosphorus_applied : float
            Mass of phosphorus applied to the soil (kg)
        fertilizer_mass : float
            Total mass of fertilizer application (kg)
        inorganic_nitrogen_fraction : float
            Fraction of fertilizer mass applied that is inorganic nitrogen (unitless)
        ammonium_fraction : float
            Fraction of inorganic nitrogen mass applied that is ammonium (unitless)
        organic_nitrogen_fraction : float
            Fraction of fertilizer mass applied that is organic nitrogen (unitless)
        field_size : float
            Size of the field (ha)

        References
        ----------
        SWAT Theoretical documentation section 6:1.7

        Notes
        -----
        This method follows the SWAT model for applying nitrogen to the soil via fertilizer, but uses the fertilizer
        phosphorus application method from SurPhos to apply phosphorus.

        """
        self.soil.phosphorus_cycling.fertilizer.add_fertilizer_phosphorus(phosphorus_applied)

        nitrates_applied = (fertilizer_mass * inorganic_nitrogen_fraction * (1 - ammonium_fraction)) / field_size
        ammonium_applied = (fertilizer_mass * inorganic_nitrogen_fraction * ammonium_fraction) / field_size
        organic_nitrogen_applied = (fertilizer_mass * organic_nitrogen_fraction * 0.5) / field_size

        self.soil.data.soil_layers[0].nitrate_content += nitrates_applied
        self.soil.data.soil_layers[0].ammonium_content += ammonium_applied
        self.soil.data.soil_layers[0].fresh_organic_nitrogen_content += organic_nitrogen_applied
        self.soil.data.soil_layers[0].active_organic_nitrogen_content += organic_nitrogen_applied
