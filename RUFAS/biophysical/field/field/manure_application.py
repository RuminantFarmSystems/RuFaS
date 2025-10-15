from typing import Dict, Optional

from RUFAS.general_constants import GeneralConstants
from RUFAS.biophysical.field.field.fertilizer_application import FertilizerApplication
from RUFAS.biophysical.field.soil.soil_data import SoilData

FRESH_FRACTION_OF_ORGANIC_NITROGEN = 0.9286
"""This fraction was used in the evaluation of RuFaS Soil Nitrogen cycling, and was validated empirically."""

SOIL_INFILTRATION = 0.6
"""Surphos assumes infiltration of 60% of nutrients from manure with less than 15% dry matter"""


class ManureApplication:
    """
    This class contains all necessary methods for adding new applications for manure phosphorus to a field, based on the
    SurPhos model.

    Parameters
    ----------
    soil_data : SoilData, optional
        The SoilData object used by this module to track manure phosphorus activity, creates new one if one is not
        provided.
    field_size : float, optional
        Used to initialize a SoilData object for this module to work with, if a pre-configured SoilData object is
        not provided (ha).

    Attributes
    ----------
    data : SoilData
        Reference to the SoilData object that is being tracked

    Methods
    -------
    apply_grazing_manure(dry_matter_mass: float, dry_matter_fraction: float, total_phosphorus_mass: float,
                             inorganic_nitrogen_fraction: float, ammonium_fraction: float,
                             organic_nitrogen_fraction: float, field_size: float) -> None
        This method takes a new application of machine-applied manure phosphorus and adds it to the existing pool to
        be tracked.
    apply_machine_manure(dry_matter_mass: float, dry_matter_fraction: float,
                             total_phosphorus_mass: float, field_coverage: float, application_depth: float,
                             surface_remainder_fraction: float, field_size: float,
                             inorganic_nitrogen_fraction: float, ammonium_fraction: float,
                             organic_nitrogen_fraction: float,
                             water_extractable_inorganic_phosphorus_fraction: float = None,
                             source_animal: str = None) -> None
        This method takes a new application of machine-applied manure phosphorus and adds it to the existing pool to
        be tracked.
    """

    def __init__(self, soil_data: Optional[SoilData] = None, field_size: Optional[float] = None) -> None:
        self.data = soil_data or SoilData(field_size=field_size)

    def apply_grazing_manure(
        self,
        dry_matter_mass: float,
        dry_matter_fraction: float,
        total_phosphorus_mass: float,
        inorganic_nitrogen_fraction: float,
        ammonium_fraction: float,
        organic_nitrogen_fraction: float,
        field_size: float,
    ) -> None:
        """This method takes a new application of machine-applied manure phosphorus and adds it to the existing pool to
            be tracked.

        Parameters
        ----------
        dry_matter_mass : float
            Dry weight equivalent of this application (kg).
        dry_matter_fraction : float
            Fraction of this manure application that is dry matter, in the range (0.0, 1.0] (unitless).
        total_phosphorus_mass : float
            Total mass of phosphorus in this application of manure (kg).
        inorganic_nitrogen_fraction : float
            Fraction of dry manure mass that is inorganic nitrogen (unitless).
        ammonium_fraction : float
            Fraction of inorganic nitrogen that is ammonium (unitless).
        organic_nitrogen_fraction : float
            Fraction of dry manure mass that is organic nitrogen (unitless).
        field_size : float
            Size of the field (ha).

        Notes
        -----
        The hardcoded values that determine the distribution of phosphorus between the water extractable
        inorganic/organic and stable inorganic/organic pools are listed in the SurPhos theoretical documentation page 7,
        in the paragraph immediately following the head "Simulation of Grazing Manure Transforms".

        """
        self.data.grazing_manure.water_extractable_inorganic_phosphorus += total_phosphorus_mass * 0.50
        self.data.grazing_manure.water_extractable_organic_phosphorus += total_phosphorus_mass * 0.05
        self.data.grazing_manure.stable_inorganic_phosphorus += total_phosphorus_mass * 0.1125
        self.data.grazing_manure.stable_organic_phosphorus += total_phosphorus_mass * 0.3375

        application_field_coverage = self._determine_grazing_manure_field_coverage(field_size, dry_matter_mass)
        new_vals = self._determine_weighted_manure_attributes(
            self.data.grazing_manure.manure_dry_mass,
            self.data.grazing_manure.manure_moisture_factor,
            self.data.grazing_manure.manure_field_coverage,
            dry_matter_mass,
            dry_matter_fraction,
            application_field_coverage,
        )
        self.data.grazing_manure.manure_dry_mass = new_vals.get("new_dry_matter_mass", 0.0)
        self.data.grazing_manure.manure_moisture_factor = new_vals.get("new_moisture_factor", 0.0)
        self.data.grazing_manure.manure_field_coverage = new_vals.get("new_field_coverage", 0.0)
        self.data.grazing_manure.manure_applied_mass = dry_matter_mass

        self._add_nitrogen_to_soil_layer(
            0,
            dry_matter_mass,
            inorganic_nitrogen_fraction,
            ammonium_fraction,
            organic_nitrogen_fraction,
            field_size,
        )

    def apply_machine_manure(
        self,
        dry_matter_mass: float,
        dry_matter_fraction: float,
        total_phosphorus_mass: float,
        field_coverage: float,
        application_depth: float,
        surface_remainder_fraction: float,
        field_size: float,
        inorganic_nitrogen_fraction: float,
        ammonium_fraction: float,
        organic_nitrogen_fraction: float,
        water_extractable_inorganic_phosphorus_fraction: float | None = None,
        source_animal: str | None = None,
    ) -> None:
        """This method takes a new application of machine-applied manure phosphorus and adds it to the existing pool to
            be tracked.

        Parameters
        ----------
        dry_matter_mass : float
            Dry weight equivalent of this application (kg).
        dry_matter_fraction : float
            Fraction of this manure application that is dry matter, in the range (0.0, 1.0] (unitless).
        total_phosphorus_mass : float
            Total mass of phosphorus in this application of manure (kg).
        field_coverage : float
            Fraction of the field this manure is applied to (unitless).
        application_depth : float
            Depth at which fertilizer is injected into the soil (mm).
        surface_remainder_fraction : float
            Fraction of fertilizer applied that remains on the soil surface after application (unitless).
        field_size : float
            Size of the field (ha).
        inorganic_nitrogen_fraction : float
            Fraction of dry manure mass that is inorganic nitrogen (unitless).
        ammonium_fraction : float
            Fraction of inorganic nitrogen that is ammonium (unitless).
        organic_nitrogen_fraction : float
            Fraction of dry manure mass that is organic nitrogen (unitless).
        water_extractable_inorganic_phosphorus_fraction : float, default=None
            Fraction of total phosphorus in this application of manure that is water extractable inorganic phosphorus,
            in the range [0.0, 1.0] (unitless).
        source_animal : str, default=None
            Type of animal that produced this manure (options are "CATTLE", "SWINE", or "POULTRY") (unitless).

        Raises
        ------
        ValueError
            If the water extractable inorganic phosphorus fraction is not inside the range [0.0, 0.95].

        Notes
        -----
        When manure is applied that contains 15% or less solid matter, the slurry immediately infiltrates the soil. The
        SurPhos theoretical documentation states that "the model assumes slurry liquid immediately infiltrates into soil
        and adds 60% of all manure P to corresponding soil P pools".

        """
        if water_extractable_inorganic_phosphorus_fraction is not None:
            if not 0.0 <= water_extractable_inorganic_phosphorus_fraction <= 0.95:
                raise ValueError(
                    f"Water extractable inorganic phosphorus fraction must be in the range [0.0, 0.95], "
                    f"received '{water_extractable_inorganic_phosphorus_fraction}'."
                )
        else:
            water_extractable_inorganic_phosphorus_fraction = (
                self._determine_water_extractable_inorganic_phosphorus_fraction_by_animal(source_animal)
            )

        surface_dry_matter_mass = dry_matter_mass * surface_remainder_fraction

        is_liquid_manure = dry_matter_fraction <= 0.15

        if is_liquid_manure:
            surface_retention = 1.0 - SOIL_INFILTRATION
        else:
            surface_retention = 1.0

        water_extractable_organic_phosphorus_fraction = 0.05
        stable_phosphorus_fraction = 1.0 - (
            water_extractable_organic_phosphorus_fraction + water_extractable_inorganic_phosphorus_fraction
        )
        stable_inorganic_phosphorus_fraction = 0.25 * stable_phosphorus_fraction
        stable_organic_phosphorus_fraction = 0.75 * stable_phosphorus_fraction

        self.data.machine_manure.water_extractable_inorganic_phosphorus += (
            total_phosphorus_mass
            * water_extractable_inorganic_phosphorus_fraction
            * surface_retention
            * surface_remainder_fraction
        )
        self.data.machine_manure.water_extractable_organic_phosphorus += (
            total_phosphorus_mass
            * water_extractable_organic_phosphorus_fraction
            * surface_retention
            * surface_remainder_fraction
        )
        self.data.machine_manure.stable_inorganic_phosphorus += (
            total_phosphorus_mass
            * stable_inorganic_phosphorus_fraction
            * surface_retention
            * surface_remainder_fraction
        )
        self.data.machine_manure.stable_organic_phosphorus += (
            total_phosphorus_mass * stable_organic_phosphorus_fraction * surface_retention * surface_remainder_fraction
        )

        if is_liquid_manure:
            mass_to_add_to_labile_P = (
                total_phosphorus_mass * water_extractable_inorganic_phosphorus_fraction * SOIL_INFILTRATION
            )
            mass_to_add_to_labile_P += (
                total_phosphorus_mass * water_extractable_organic_phosphorus_fraction * SOIL_INFILTRATION * 0.95
            )
            mass_to_add_to_labile_P += (
                total_phosphorus_mass * stable_organic_phosphorus_fraction * SOIL_INFILTRATION * 0.95
            )
            mass_to_add_to_labile_P *= surface_remainder_fraction

            self.data.soil_layers[0].add_to_labile_phosphorus(mass_to_add_to_labile_P, field_size)

            mass_to_add_to_active_P = (
                total_phosphorus_mass
                * stable_inorganic_phosphorus_fraction
                * SOIL_INFILTRATION
                * surface_remainder_fraction
            )
            self.data.soil_layers[0].add_to_active_phosphorus(mass_to_add_to_active_P, field_size)
            adjusted_field_coverage = field_coverage * 0.5
            adjusted_dry_matter_mass = surface_dry_matter_mass * 0.8
        else:
            adjusted_field_coverage = field_coverage
            adjusted_dry_matter_mass = surface_dry_matter_mass

        new_vals = self._determine_weighted_manure_attributes(
            self.data.machine_manure.manure_dry_mass,
            self.data.machine_manure.manure_moisture_factor,
            self.data.machine_manure.manure_field_coverage,
            adjusted_dry_matter_mass,
            dry_matter_fraction,
            adjusted_field_coverage,
        )

        self.data.machine_manure.manure_dry_mass = new_vals.get("new_dry_matter_mass", 0.0)
        self.data.machine_manure.manure_moisture_factor = new_vals.get("new_moisture_factor", 0.0)
        self.data.machine_manure.manure_field_coverage = new_vals.get("new_field_coverage", 0.0)

        if is_liquid_manure:
            top_layer_mass = surface_retention * surface_dry_matter_mass
        else:
            top_layer_mass = surface_dry_matter_mass

        self._add_nitrogen_to_soil_layer(
            0,
            top_layer_mass,
            inorganic_nitrogen_fraction,
            ammonium_fraction,
            organic_nitrogen_fraction,
            field_size,
        )

        if is_liquid_manure:
            second_layer_mass = SOIL_INFILTRATION * surface_dry_matter_mass
            self._add_nitrogen_to_soil_layer(
                1,
                second_layer_mass,
                inorganic_nitrogen_fraction,
                ammonium_fraction,
                organic_nitrogen_fraction,
                field_size,
            )

        self.data.machine_manure.manure_applied_mass = dry_matter_mass

        is_not_subsurface_application = application_depth == 0.0 and surface_remainder_fraction == 1.0
        if is_not_subsurface_application:
            return

        subsurface_fraction = 1.0 - surface_remainder_fraction
        self._apply_subsurface_manure(
            total_phosphorus_mass,
            water_extractable_inorganic_phosphorus_fraction,
            water_extractable_organic_phosphorus_fraction,
            stable_inorganic_phosphorus_fraction,
            stable_organic_phosphorus_fraction,
            dry_matter_mass,
            inorganic_nitrogen_fraction,
            ammonium_fraction,
            organic_nitrogen_fraction,
            application_depth,
            subsurface_fraction,
            field_size,
        )

    def _add_nitrogen_to_soil_layer(
        self,
        layer_index: int,
        dry_matter_mass: float,
        inorganic_nitrogen_fraction: float,
        ammonium_fraction: float,
        organic_nitrogen_fraction: float,
        field_size: float,
    ) -> None:
        """
        Adds nitrogen into the top of the soil profile when manure is applied to the field.

        Parameters
        ----------
        layer_index : int
            Index of the soil layer to be added to (unitless).
        dry_matter_mass : float
            Dry weight equivalent of this application (kg).
        inorganic_nitrogen_fraction : float
            Fraction of dry manure mass that is inorganic nitrogen (unitless).
        ammonium_fraction : float
            Fraction of inorganic nitrogen that is ammonium (unitless).
        organic_nitrogen_fraction : float
            Fraction of dry manure mass that is organic nitrogen (unitless).
        field_size : float
            Size of the field (ha).

        References
        ----------
        SWAT Theoretical documentation section 6:1.7
        pseudocode_field_management [FM.4.D.1]

        Notes
        -----
        This method allows nitrogen to be added to any soil layer in the profile by specifying the index of that layer.
        The top soil layer will always be at index 0.

        Instead of partitioning organic nitrogen between the fresh and active pools, it is partitioned between the
        stable and active pools. Refer to the pseudocode for this.

        """
        nitrates_added = (dry_matter_mass * inorganic_nitrogen_fraction * (1 - ammonium_fraction)) / field_size
        ammonium_added = (dry_matter_mass * inorganic_nitrogen_fraction * ammonium_fraction) / field_size
        fresh_organic_nitrogen_added = (
            dry_matter_mass * organic_nitrogen_fraction * FRESH_FRACTION_OF_ORGANIC_NITROGEN
        ) / field_size
        stable_organic_nitrogen_added = (
            dry_matter_mass * organic_nitrogen_fraction * (1.0 - FRESH_FRACTION_OF_ORGANIC_NITROGEN)
        ) / field_size

        self.data.soil_layers[layer_index].nitrate_content += nitrates_added
        self.data.soil_layers[layer_index].ammonium_content += ammonium_added
        self.data.soil_layers[layer_index].stable_organic_nitrogen_content += stable_organic_nitrogen_added
        self.data.soil_layers[layer_index].fresh_organic_nitrogen_content += fresh_organic_nitrogen_added

    def _apply_subsurface_manure(
        self,
        total_phosphorus_mass: float,
        water_extractable_inorganic_phosphorus_fraction: float,
        water_extractable_organic_phosphorus_fraction: float,
        stable_inorganic_phosphorus_fraction: float,
        stable_organic_phosphorus_fraction: float,
        dry_matter_mass: float,
        inorganic_nitrogen_fraction: float,
        ammonium_fraction: float,
        organic_nitrogen_fraction: float,
        application_depth: float,
        subsurface_fraction: float,
        field_size: float,
    ) -> None:
        """
        Applies subsurface nutrients to the soil profile.

        Parameters
        ----------
        total_phosphorus_mass : float
            Total mass of phosphorus in this application of manure (kg).
        water_extractable_inorganic_phosphorus_fraction : float
            Fraction of total phosphorus in this application of manure that is water extractable inorganic phosphorus,
            in the range [0.0, 1.0] (unitless).
        water_extractable_organic_phosphorus_fraction : float
            Fraction of total phosphorus in this application of manure that is water extractable organic phosphorus, in
            the range [0.0, 1.0] (unitless).
        stable_inorganic_phosphorus_fraction : float
            Fraction of total phosphorus in this application of manure that is stable inorganic phosphorus, in the range
            [0.0, 1.0] (unitless).
        stable_organic_phosphorus_fraction : float
            Fraction of total phosphorus in this application of manure that is stable organic phosphorus, in the range
            [0.0, 1.0] (unitless).
        dry_matter_mass : float
            Dry weight equivalent of the manure application (kg).
        inorganic_nitrogen_fraction : float
            Fraction of dry manure mass that is inorganic nitrogen (unitless).
        ammonium_fraction : float
            Fraction of inorganic nitrogen that is ammonium (unitless).
        organic_nitrogen_fraction : float
            Fraction of dry manure mass that is organic nitrogen (unitless).
        application_depth : float
            Depth at which fertilizer is injected into the soil (mm).
        subsurface_fraction : float
            Fraction of total manure application that is applied below the soil surface (unitless).
        field_size : float
            Size of the field (ha).

        Notes
        -----
        Only 95% of water extractable organic and stable organic phosphorus are put into their corresponding pools
        because that is how SurPhos transfers organic phosphorus, as an approximation for organic phosphorus loss. This
        practice will be changed when issue #444 is addressed.

        """
        bottom_depths = self.data.get_vectorized_layer_attribute("bottom_depth")
        depth_factors = FertilizerApplication.generate_depth_factors(application_depth, bottom_depths)
        water_extractable_inorganic_phosphorus = total_phosphorus_mass * water_extractable_inorganic_phosphorus_fraction
        water_extractable_organic_phosphorus = (
            total_phosphorus_mass * water_extractable_organic_phosphorus_fraction * 0.95
        )
        stable_inorganic_phosphorus = total_phosphorus_mass * stable_inorganic_phosphorus_fraction
        stable_organic_phosphorus = total_phosphorus_mass * stable_organic_phosphorus_fraction * 0.95
        labile_phosphorus_addition = (
            water_extractable_inorganic_phosphorus + water_extractable_organic_phosphorus + stable_organic_phosphorus
        ) * subsurface_fraction
        active_phosphorus_addition = stable_inorganic_phosphorus * subsurface_fraction
        for index, depth_factor in enumerate(depth_factors):
            labile_phosphorus_added_to_layer = labile_phosphorus_addition * depth_factor
            active_phosphorus_added_to_layer = active_phosphorus_addition * depth_factor
            self.data.soil_layers[index].add_to_labile_phosphorus(labile_phosphorus_added_to_layer, field_size)
            self.data.soil_layers[index].add_to_active_phosphorus(active_phosphorus_added_to_layer, field_size)

            dry_matter_added_to_layer = dry_matter_mass * subsurface_fraction * depth_factor
            self._add_nitrogen_to_soil_layer(
                index,
                dry_matter_added_to_layer,
                inorganic_nitrogen_fraction,
                ammonium_fraction,
                organic_nitrogen_fraction,
                field_size,
            )

    # --- Static Methods ---
    @staticmethod
    def _determine_grazing_manure_field_coverage(field_size: float, total_manure_applied: float) -> float:
        """Calculates the fraction of the field covered by manure that was applied by grazers.

        Parameters
        ----------
        field_size : float
            Size of the field (ha)
        total_manure_applied : float
            Total mass of the manure application (kg)

        Returns
        -------
        float
            The fraction of the field covered by manure (unitless)

        Notes
        -----
        This method is only used for calculating the field coverage for manure applied by grazers. It is based on the
        relationship specified in the SurPhos theoretical documentation which states that the ratio is 250 grams of
        manure to 659 square centimeters of field coverage (James et al., 2007).

        References
        ----------
        James E., Kleinman P., Veith T., Stedman R., Sharpley A. (2007) Phosphorus contributions from
            pastured dairy cattle to streams of the Cannonsville Watershed, New York. Journal of Soil
            and Water Conservation 62:40-47.

        """
        manure_applied_in_grams = total_manure_applied * GeneralConstants.KG_TO_GRAMS
        field_coverage_in_square_cm = manure_applied_in_grams * (659 / 250)
        field_coverage_in_ha = field_coverage_in_square_cm * GeneralConstants.SQUARE_CENTIMETERS_TO_HECTARES
        field_coverage_fraction = min(1.0, field_coverage_in_ha / field_size)
        return field_coverage_fraction

    @staticmethod
    def _determine_moisture_factor(dry_matter_fraction: float) -> float:
        """This method determines the moisture factor of a new manure application based on how much manure was applied
            and how much water was in the application.

        Parameters
        ----------
        dry_matter_fraction : float
            Fraction of this manure application that is dry matter, in the range (0.0, 1.0] (unitless)

        Returns
        -------
        float
            The moisture factor of this application of manure (unitless)

        Raises
        ------
        ValueError
            If the dry matter content is not inside the range (0.0, 1.0]

        Notes
        -----
        This equation is not listed in the SurPhos theoretical documentation, but is present in both the SurPhos Python
        and Fortran code (see manure.f and manure.py, lines 30, 31 and 41, 42 respectively). This equation is a way of
        determining the moisture factor based on the amount of dry matter mass in the manure application that produces
        more accurate results.

        """
        if not 0.0 < dry_matter_fraction <= 1.0:
            raise ValueError(f"Dry matter content must be in the range (0.0, 1.0], received: '{dry_matter_fraction}'.")
        return min(0.9, (1 - dry_matter_fraction))

    @staticmethod
    def _determine_weighted_manure_attributes(
        old_total_dry_mass: float,
        old_moisture_factor: float,
        old_field_coverage: float,
        application_dry_mass: float,
        application_dry_fraction: float,
        application_field_coverage: float,
    ) -> Dict:
        """Recalculates the manure pool attributes that use a weighted average to find their new values.

        Parameters
        ----------
        old_total_dry_mass : float
            Dry weight equivalent of the manure that was already on the field (kg)
        old_moisture_factor : float
            Moisture factor of the manure that was already on the field, between [0, 0.9] (unitless)
        old_field_coverage : float
            The fraction of the area of the field that was already covered by old manure, between [0, 1] (unitless)
        application_dry_mass : float
            Dry weight equivalent of manure application (kg)
        application_dry_fraction : float
            Fraction of this manure application that is dry matter, in the range (0.0, 1.0] (unitless)
        application_field_coverage : float
            Fraction of the field covered by the manure application (unitless)

        Returns
        -------
        new_dry_matter_mass : float
            The new dry weight equivalent of manure on the field (kg)
        new_moisture_factor : float
            The new moisture factor of the manure on the field, in the range [0, 0.9] (unitless)
        new_field_coverage : float
            The new fraction of field area that is covered by manure, in the range [0, 1] (unitless)

        Notes
        -----
        To keep a more accurate state of the manure and grazing phosphorus pools, the field coverage and moisture
        variables are recalculated to be a weighted average of the new and preexisting field coverage and moisture
        variables, weighted by mass.

        """
        new_dry_matter_mass = old_total_dry_mass + application_dry_mass

        if new_dry_matter_mass > 0:
            application_moisture_factor = ManureApplication._determine_moisture_factor(application_dry_fraction)
            new_moisture_factor = (
                old_moisture_factor * old_total_dry_mass + application_moisture_factor * application_dry_mass
            ) / new_dry_matter_mass
            new_field_coverage = (
                old_field_coverage * old_total_dry_mass + application_field_coverage * application_dry_mass
            ) / new_dry_matter_mass
            return {
                "new_dry_matter_mass": new_dry_matter_mass,
                "new_moisture_factor": new_moisture_factor,
                "new_field_coverage": new_field_coverage,
            }

        else:
            return {
                "new_dry_matter_mass": 0,
                "new_moisture_factor": 0,
                "new_field_coverage": 0,
            }

    @staticmethod
    def _determine_water_extractable_inorganic_phosphorus_fraction_by_animal(
        animal_type: str | None,
    ) -> float:
        """

        Parameters
        ----------
        animal_type : str
            Type of animal that produced the manure (can be either "CATTLE", "SWINE", or "POULTRY")

        Returns
        -------
        float
            Fraction of manure that is water-extractable inorganic phosphorus (unitless)

        Raises
        ------
        ValueError
            If the animal type passed does not match any of the supported types.

        Notes
        -----
        These are reasonable defaults provided Pete Vadas.

        """
        if animal_type == "CATTLE":
            return 0.50
        elif animal_type == "SWINE":
            return 0.35
        elif animal_type == "POULTRY":
            return 0.20
        else:
            raise ValueError(f'Expected "CATTLE", "SWINE", or "POULTRY", received \'{animal_type}\'.')
