from typing import Optional

from RUFAS.biophysical.field.soil.soil import Soil


class FertilizerApplication:
    """
    This module provides a way for Field to apply fertilizer, based on SWAT Theoretical documentation section (6:1.7)
    This class can be initialized with a Soil object or create one if none is provided

    Parameters
    ----------
    soil : Soil, default=None
        Soil object to which fertilizer should be applied.
    field_size : float, default=None
        Size of the field. Used to initialize a Soil object for this module to work with, if a pre-configured
        SoilData object is not provided (ha)

    Attributes
    ----------
    soil: Soil
        Reference to the Soil object to be fertilized.

    Methods
    -------
    apply_fertilizer(phosphorus_applied: float, fertilizer_mass: float, inorganic_nitrogen_fraction: float,
                    ammonium_fraction: float, organic_nitrogen_fraction: float, application_depth: float,
                    surface_remainder_fraction: float, field_size: float) -> None
        Applies nutrients to the soil through fertilizer.
    generate_depth_factors(application_depth: float, soil_layer_bottom_depths: list[float]) -> list[float]
        Generates a list of fractions that partitions sub-surface nutrients between the different soil layers.
    """

    def __init__(self, soil: Optional[Soil] = None, field_size: Optional[float] = None):
        self.soil = soil or Soil(field_size=field_size)

    def apply_fertilizer(
        self,
        phosphorus_applied: float,
        nitrogen_applied: float,
        ammonium_fraction: float,
        application_depth: float,
        surface_remainder_fraction: float,
        field_size: float,
    ) -> None:
        """
        Applies nutrients to the soil through fertilizer.

        Parameters
        ----------
        phosphorus_applied : float
            Mass of phosphorus applied to the soil (kg).
        nitrogen_applied : float
            Mass of nitrogen applied to the soil (kg).
        ammonium_fraction : float
            Fraction of inorganic nitrogen mass applied that is ammonium (unitless).
        application_depth : float
            Depth at which fertilizer is injected into the soil (mm).
        surface_remainder_fraction : float
            Fraction of fertilizer applied that remains on the soil surface after application (unitless).
        field_size : float
            Size of the field (ha).

        References
        ----------
        SWAT Theoretical documentation section 6:1.7.

        Notes
        -----
        This method follows the SWAT model for applying nitrogen to the soil via fertilizer, but uses the fertilizer
        phosphorus application method from SurPhos to apply phosphorus.

        """
        self.soil.phosphorus_cycling.fertilizer.add_fertilizer_phosphorus(
            phosphorus_applied * surface_remainder_fraction
        )

        nitrates_applied = (nitrogen_applied * (1.0 - ammonium_fraction)) / field_size
        ammonium_applied = (nitrogen_applied * ammonium_fraction) / field_size

        self.soil.data.soil_layers[0].nitrate_content += nitrates_applied * surface_remainder_fraction
        self.soil.data.soil_layers[0].ammonium_content += ammonium_applied * surface_remainder_fraction

        non_injection_application = application_depth == 0.0 and surface_remainder_fraction == 1.0
        if non_injection_application:
            return

        subsurface_fraction = 1.0 - surface_remainder_fraction
        phosphorus_area_density = phosphorus_applied / field_size
        self._apply_subsurface_fertilizer(
            phosphorus_area_density,
            nitrates_applied,
            ammonium_applied,
            application_depth,
            subsurface_fraction,
        )

    def _apply_subsurface_fertilizer(
        self,
        phosphorus: float,
        nitrates: float,
        ammonium: float,
        application_depth: float,
        subsurface_fraction: float,
    ) -> None:
        """
        Applies subsurface nutrients to the soil profile.

        Parameters
        ----------
        phosphorus : float
            Amount of phosphorus applied in this application of fertilizer (kg / ha).
        nitrates : float
            Amount of nitrates applied in this application of fertilizer (kg / ha).
        ammonium : float
            Amount of ammonium applied in this application of fertilizer (kg / ha).
        application_depth : float
            Bottom depth of this fertilizer application (mm).
        subsurface_fraction : float
            Fraction of total fertilizer application that is applied below the soil surface (unitless).

        Notes
        -----
        This implementation applies all nutrients from the fertilizer application to subsurface soil layers in the same
        manner. In previous implementations of RuFaS, only phosphorus was added to layers below the surface when
        injection applications occurred.

        """
        bottom_depths = self.soil.data.get_vectorized_layer_attribute("bottom_depth")
        depth_factors = self.generate_depth_factors(application_depth, bottom_depths)
        for index, depth_factor in enumerate(depth_factors):
            self.soil.data.soil_layers[index].labile_inorganic_phosphorus_content += (
                phosphorus * depth_factor * subsurface_fraction
            )
            self.soil.data.soil_layers[index].nitrate_content += nitrates * depth_factor * subsurface_fraction
            self.soil.data.soil_layers[index].ammonium_content += ammonium * depth_factor * subsurface_fraction

    @staticmethod
    def generate_depth_factors(application_depth: float, soil_layer_bottom_depths: list[float]) -> list[float]:
        """
        Generates a list of fractions that partitions sub-surface nutrients between the different soil layers.

        Parameters
        ----------
        application_depth : float
            Bottom depth of nutrient application (mm).
        soil_layer_bottom_depths : list[float]
            List of bottom depths of soil layers in the soil profile (mm).

        Returns
        -------
        list[float]
            List of fractions that determine the distribution of nutrients between different soil layers when subsurface
            nutrients are applied (unitless).

        References
        ----------
        pseudocode_field_management [FM.3.B.3 - 5]

        Notes
        -----
        This method of distributing nutrients between soil layers originates with Pete Vadas' SurPhos model. Its purpose
        is to proportionally distribute nutrients to layers within the soil profile.

        """
        depth_factors_sum = 0.0
        depth_factors = []
        for depth in soil_layer_bottom_depths:
            if depth < application_depth:
                depth_factor = depth / application_depth
                depth_factors_sum += depth_factor
                depth_factors.append(depth_factor)
            else:
                depth_factor = 1.0 - depth_factors_sum
                depth_factors.append(depth_factor)
                break
        return depth_factors
