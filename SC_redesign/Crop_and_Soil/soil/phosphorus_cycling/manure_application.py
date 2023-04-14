from typing import Optional, Dict

from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData
from SC_redesign.Crop_and_Soil.crop_and_soil_constants import KILOGRAMS_TO_GRAMS, SQUARE_CENTIMETERS_TO_HECTARES

"""
This module contains all necessary methods for adding new applications for manure phosphorus to a field, based on the
SurPhos model.
"""


class ManureApplication:

    def __init__(self, soil_data: Optional[SoilData] = None):
        """This method initializes the SoilData object that this module will work with, or create one if none provided.

        Parameters
        ----------
        soil_data : SoilData, optional
            The SoilData object used by this module to track manure phosphorus activity, creates new one if one is not
            provided.

        """
        self.data = soil_data or SoilData()

    def apply_grazing_manure(self, dry_matter_mass: float, dry_matter_fraction: float,
                             total_phosphorus_mass: float, field_size: float) -> None:
        """This method takes a new application of machine-applied manure phosphorus and adds it to the existing pool to
            be tracked.

        Parameters
        ----------
        dry_matter_mass : float
            Dry weight equivalent of this application (kg)
        dry_matter_fraction : float
            Fraction of this manure application that is dry matter, in the range (0.0, 1.0] (unitless)
        total_phosphorus_mass : float
            Total mass of phosphorus in this application of manure (kg)
        field_size : float
            Size of the field (ha)

        Notes
        -----
        The hardcoded values that determine the distribution of phosphorus between the water extractable
        inorganic/organic and stable inorganic/organic pools are listed in the SurPhos theoretical documentation page 7,
        in the paragraph immediately following the head "Simulation of Grazing Manure Transforms".

        """
        self.data.grazing_water_extractable_inorganic_phosphorus += total_phosphorus_mass * 0.50
        self.data.grazing_water_extractable_organic_phosphorus += total_phosphorus_mass * 0.05
        self.data.grazing_stable_inorganic_phosphorus += total_phosphorus_mass * 0.1125
        self.data.grazing_stable_organic_phosphorus += total_phosphorus_mass * 0.3375

        application_field_coverage = self._determine_grazing_manure_field_coverage(field_size, dry_matter_mass)
        new_vals = self._determine_weighted_manure_attributes(self.data.grazing_manure_dry_mass,
                                                              self.data.grazing_manure_moisture_factor,
                                                              self.data.grazing_manure_field_coverage, dry_matter_mass,
                                                              dry_matter_fraction, application_field_coverage)
        self.data.grazing_manure_dry_mass = new_vals.get("new_dry_matter_mass")
        self.data.grazing_manure_moisture_factor = new_vals.get("new_moisture_factor")
        self.data.grazing_manure_field_coverage = new_vals.get("new_field_coverage")
        self.data.grazing_manure_applied_mass = dry_matter_mass

    def apply_machine_manure(self, dry_matter_mass: float, dry_matter_fraction: float,
                             total_phosphorus_mass: float, field_coverage: float, field_size: float,
                             water_extractable_inorganic_phosphorus_fraction: float = None,
                             source_animal: str = None) -> None:
        """This method takes a new application of machine-applied manure phosphorus and adds it to the existing pool to
            be tracked.

        Parameters
        ----------
        dry_matter_mass : float
            Dry weight equivalent of this application (kg)
        dry_matter_fraction : float
            Fraction of this manure application that is dry matter, in the range (0.0, 1.0] (unitless)
        total_phosphorus_mass : float
            Total mass of phosphorus in this application of manure (kg)
        field_coverage : float
            Fraction of the field this manure is applied to (unitless)
        field_size : float
            Size of the field (ha)
        water_extractable_inorganic_phosphorus_fraction : float, default=None
            Fraction of total phosphorus in this application of manure that is water extractable inorganic phosphorus,
            in the range [0.0, 1.0] (unitless)
        source_animal : str, default=None
            Type of animal that produced this manure (options are "CATTLE", "SWINE", or "POULTRY") (unitless)

        Raises
        ------
        ValueError
            If the water extractable inorganic phosphorus fraction is not inside the range [0.0, 0.95]

        """
        if water_extractable_inorganic_phosphorus_fraction is not None:
            if not 0.0 <= water_extractable_inorganic_phosphorus_fraction <= 0.95:
                raise ValueError(f"Water extractable inorganic phosphorus fraction must be in the range [0.0, 0.95], "
                                 f"received '{water_extractable_inorganic_phosphorus_fraction}'.")
        else:
            water_extractable_inorganic_phosphorus_fraction = \
                self._determine_water_extractable_inorganic_phosphorus_fraction_by_animal(source_animal)

        if dry_matter_fraction <= 0.15:
            self._apply_liquid_machine_manure(dry_matter_mass, dry_matter_fraction, total_phosphorus_mass,
                                              field_coverage, field_size,
                                              water_extractable_inorganic_phosphorus_fraction)
        else:
            self._apply_solid_machine_manure(dry_matter_mass, dry_matter_fraction, total_phosphorus_mass,
                                             field_coverage, water_extractable_inorganic_phosphorus_fraction)
        self.data.machine_manure_applied_mass = dry_matter_mass

    def _apply_solid_machine_manure(self, dry_matter_mass: float, dry_matter_fraction: float,
                                    total_phosphorus_mass: float, field_coverage: float,
                                    water_extractable_inorganic_phosphorus_fraction: float) -> None:
        """This method applies manure to the field surface when the dry matter content of the application is greater
            than 15%.

        Parameters
        ----------
        dry_matter_mass : float
            Dry weight equivalent of this application (kg)
        dry_matter_fraction : float
            Fraction of this manure application that is dry matter, in the range (0.0, 1.0] (unitless)
        total_phosphorus_mass : float
            Total mass of phosphorus in this application of manure (kg)
        field_coverage : float
            Fraction of the field this manure is applied to (unitless)
        water_extractable_inorganic_phosphorus_fraction : float
            Fraction of total phosphorus in this application of manure that is water extractable inorganic phosphorus,
            in the range [0.0, 1.0] (unitless)

        """
        water_extractable_organic_phosphorus_fraction = 0.05
        stable_phosphorus_fraction = 1.0 - (water_extractable_organic_phosphorus_fraction +
                                            water_extractable_inorganic_phosphorus_fraction)
        stable_inorganic_phosphorus_fraction = 0.25 * stable_phosphorus_fraction
        stable_organic_phosphorus_fraction = 0.75 * stable_phosphorus_fraction
        self.data.machine_water_extractable_inorganic_phosphorus += (total_phosphorus_mass *
                                                                     water_extractable_inorganic_phosphorus_fraction)
        self.data.machine_water_extractable_organic_phosphorus += (total_phosphorus_mass *
                                                                   water_extractable_organic_phosphorus_fraction)
        self.data.machine_stable_inorganic_phosphorus += (total_phosphorus_mass * stable_inorganic_phosphorus_fraction)
        self.data.machine_stable_organic_phosphorus += (total_phosphorus_mass * stable_organic_phosphorus_fraction)

        new_vals = self._determine_weighted_manure_attributes(self.data.machine_manure_dry_mass,
                                                              self.data.machine_manure_moisture_factor,
                                                              self.data.machine_manure_field_coverage, dry_matter_mass,
                                                              dry_matter_fraction, field_coverage)
        self.data.machine_manure_dry_mass = new_vals.get("new_dry_matter_mass")
        self.data.machine_manure_moisture_factor = new_vals.get("new_moisture_factor")
        self.data.machine_manure_field_coverage = new_vals.get("new_field_coverage")

    def _apply_liquid_machine_manure(self, dry_matter_mass: float, dry_matter_fraction: float,
                                     total_phosphorus_mass: float, field_coverage: float, field_size: float,
                                     water_extractable_inorganic_phosphorus_fraction: float) -> None:
        """This method applies manure with 15% solid content or less to a field.

        Parameters
        ----------
        dry_matter_mass : float
            Dry weight equivalent of this application (kg)
        dry_matter_fraction : float
            Fraction of this manure application that is dry matter, in the range (0.0, 1.0] (unitless)
        total_phosphorus_mass : float
            Total mass of phosphorus in this application of manure (kg)
        field_coverage : float
            Fraction of the field this manure is applied to (unitless)
        field_size : float
            Size of the field (ha)
        water_extractable_inorganic_phosphorus_fraction : float
            Fraction of total phosphorus in this application of manure that is water extractable inorganic phosphorus,
            in the range [0.0, 1.0] (unitless)

        Notes
        -----
        When manure is applied that contains 15% or less solid matter, the slurry immediately infiltrates the soil. The
        SurPhos theoretical documentation states that "the model assumes slurry liquid immediately infiltrates into soil
        and adds 60% of all manure P to corresponding soil P pools", but is handled differently in the actual SurPhos
        implementation. Currently, RuFaS uses the same equations as the SurPhos code.

        """
        wet_rate = self._determine_wet_rate_factor(dry_matter_mass, dry_matter_fraction, field_coverage, field_size)
        soil_infiltration = self._determine_infiltration_factor(wet_rate)
        surface_retention = (1.0 - soil_infiltration)
        water_extractable_organic_phosphorus_fraction = 0.05
        stable_phosphorus_fraction = 1.0 - (water_extractable_organic_phosphorus_fraction +
                                            water_extractable_inorganic_phosphorus_fraction)
        stable_inorganic_phosphorus_fraction = 0.25 * stable_phosphorus_fraction
        stable_organic_phosphorus_fraction = 0.75 * stable_phosphorus_fraction

        self.data.machine_water_extractable_inorganic_phosphorus += total_phosphorus_mass * \
            water_extractable_inorganic_phosphorus_fraction * surface_retention
        self.data.machine_water_extractable_organic_phosphorus += total_phosphorus_mass * \
            water_extractable_organic_phosphorus_fraction * surface_retention
        self.data.machine_stable_inorganic_phosphorus += total_phosphorus_mass * \
            stable_inorganic_phosphorus_fraction * surface_retention
        self.data.machine_stable_organic_phosphorus += total_phosphorus_mass * \
            stable_organic_phosphorus_fraction * surface_retention

        # TODO: remove or explain why 0.95 is preset of stable organic phosphorus and water extractable inorganic
        #  phosphorus after getting explanation from Pete
        mass_to_add_to_labile_P = total_phosphorus_mass * water_extractable_inorganic_phosphorus_fraction * \
            soil_infiltration
        mass_to_add_to_labile_P += total_phosphorus_mass * water_extractable_organic_phosphorus_fraction * \
            soil_infiltration * 0.95
        mass_to_add_to_labile_P += total_phosphorus_mass * stable_organic_phosphorus_fraction * soil_infiltration * 0.95
        self.data.soil_layers[0].add_to_labile_phosphorus(mass_to_add_to_labile_P, field_size)

        mass_to_add_to_active_P = total_phosphorus_mass * stable_inorganic_phosphorus_fraction * soil_infiltration
        self.data.soil_layers[0].add_to_active_phosphorus(mass_to_add_to_active_P, field_size)

        adjusted_field_coverage = field_coverage * 0.5
        adjusted_dry_matter_mass = dry_matter_mass * 0.8
        new_vals = self._determine_weighted_manure_attributes(self.data.machine_manure_dry_mass,
                                                              self.data.machine_manure_moisture_factor,
                                                              self.data.machine_manure_field_coverage,
                                                              adjusted_dry_matter_mass, dry_matter_fraction,
                                                              adjusted_field_coverage)
        self.data.machine_manure_dry_mass = new_vals.get("new_dry_matter_mass")
        self.data.machine_manure_moisture_factor = new_vals.get("new_moisture_factor")
        self.data.machine_manure_field_coverage = new_vals.get("new_field_coverage")

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
        manure_applied_in_grams = total_manure_applied * KILOGRAMS_TO_GRAMS
        field_coverage_in_square_cm = manure_applied_in_grams * (659 / 250)
        field_coverage_in_ha = field_coverage_in_square_cm * SQUARE_CENTIMETERS_TO_HECTARES
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
        and Fortran code (see manure.f and manure.py, lines 30, 31 and 41, 42 respectively).

        """
        # TODO: clarify where this equation comes from / how it works after finding out from Pete
        if not 0.0 < dry_matter_fraction <= 1.0:
            raise ValueError(f"Dry matter content must be in the range (0.0, 1.0], received: '{dry_matter_fraction}'.")
        return min(0.9, (1 - dry_matter_fraction))

    @staticmethod
    def _determine_weighted_manure_attributes(old_total_dry_mass: float, old_moisture_factor: float,
                                              old_field_coverage: float, application_dry_mass: float,
                                              application_dry_fraction: float, application_field_coverage: float) \
            -> Dict:
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
        application_moisture_factor = ManureApplication._determine_moisture_factor(application_dry_fraction)
        new_moisture_factor = (old_moisture_factor * old_total_dry_mass + application_moisture_factor *
                               application_dry_mass) / new_dry_matter_mass
        new_field_coverage = (old_field_coverage * old_total_dry_mass +
                              application_field_coverage * application_dry_mass) / new_dry_matter_mass
        return {"new_dry_matter_mass": new_dry_matter_mass, "new_moisture_factor": new_moisture_factor,
                "new_field_coverage": new_field_coverage}

    @staticmethod
    def _determine_wet_rate_factor(dry_matter_mass: float, dry_matter_fraction: float, field_coverage: float,
                                   field_size: float) -> float:
        """This method calculates the wet rate factor, which is used to calculate how much liquid manure infiltrates the
            soil.

        Parameters
        ----------
        dry_matter_mass : float
            Dry weight equivalent of this application (kg)
        dry_matter_fraction : float
            Fraction of this manure application that is dry matter, in the range (0.0, 1.0] (unitless)
        field_coverage : float
            Fraction of the field this manure is applied to (unitless)
        field_size : float
            Size of the field (ha)

        Returns
        -------
        float
            The wet rate of this manure application.

        Notes
        -----
        This equation is not present in the SurPhos theoretical documentation, but can be found on line 32 of the
        manure.f file of the SurPhos Fortran code.

        """
        # TODO: add note about and/or reference to origin of this equation after talking with Pete about it
        return dry_matter_mass / dry_matter_fraction / (field_size * field_coverage)

    @staticmethod
    def _determine_infiltration_factor(wet_rate: float) -> float:
        """Calculates the rate at which manure slurry infiltrates the soil.

        Parameters
        ----------
        wet_rate : float
            Factor accounting for how liquid an application of manure is and the area it was applied to (kg / ha)

        Returns
        -------
        The fraction of machine-applied manure slurry that immediately infiltrates soil after application (unitless).

        Notes
        -----
        This function will only be used to determine the amount of phosphorus that infiltrates the soil after an
        application of manure that has 15% or less solid matter content. It is not present in the SurPhos documentation,
        but can be found on line 33 of the manure.f file of the SurPhos Fortran code.

        """
        # TODO: add note about and/or reference to origin of this equation after talking with Pete about it
        retention_rate = min(0.9, 0.000002 * wet_rate + 0.267)
        return 1.0 - retention_rate
