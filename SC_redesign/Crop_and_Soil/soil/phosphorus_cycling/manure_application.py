from typing import Optional

from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData

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

    def apply_machine_manure(self, dry_matter_mass: float, dry_matter_content: float,
                             total_phosphorus_mass: float, field_coverage: float,
                             water_extractable_inorganic_phosphorus_fraction: float = None,
                             source_animal: str = None) -> None:
        """This method takes a new application of machine-applied manure phosphorus and adds it to the existing pool to
            be tracked.

        Parameters
        ----------
        dry_matter_mass : float
            Dry weight equivalent of this application (kg)
        dry_matter_content : float
            Fraction of this manure application that is dry matter, in the range (0.0, 1.0] (unitless)
        total_phosphorus_mass : float
            Total mass of phosphorus in this application of manure (kg)
        field_coverage : float
            Fraction of the field this manure is applied to (unitless)
        water_extractable_inorganic_phosphorus_fraction : float, default=None
            Fraction of total phosphorus in this application of manure that is water extractable inorganic phosphorus,
            in the range [0.0, 1.0] (unitless)
        source_animal : str, default=None
            Type of animal that produced this manure (options are "CATTLE", "SWINE", or "POULTRY") (unitless)

        Raises
        ------
        ValueError
            If the water extractable inorganic phosphorus fraction is not inside the range [0.0, 1.0]
        ValueError
            If the dry matter content is not inside the range (0.0, 1.0]

        Notes
        -----
        This method adds new manure phosphorus to a pool of phosphorus that contains values from other manure
        applications. To keep a more accurate state of this pool, the field coverage and moisture variables are
        recalculated to be a weighted average of the new and preexisting field coverage and moisture variables, weighted
        by mass.

        """
        # TODO: implement an option for applying manure phosphorus at subsurface levels, after talking with Pete about
        #  how this should be done with more than two soil layers.

        if water_extractable_inorganic_phosphorus_fraction is not None:
            if not 0.0 <= water_extractable_inorganic_phosphorus_fraction <= 1.0:
                raise ValueError(f"Water extractable inorganic phosphorus fraction must be in the range [0.0, 1.0], "
                                 f"received '{water_extractable_inorganic_phosphorus_fraction}'.")
        else:
            water_extractable_inorganic_phosphorus_fraction = \
                self._determine_water_extractable_inorganic_phosphorus_fraction_by_animal(source_animal)
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

        if not 0.0 < dry_matter_content <= 1.0:
            raise ValueError(f"Dry matter content must be in the range (0.0, 1.0], received: '{dry_matter_content}'.")
        new_total_mass = self.data.machine_manure_dry_mass + dry_matter_mass
        application_moisture_factor = (1 - dry_matter_content) * dry_matter_mass
        new_moisture_factor = (self.data.machine_manure_moisture_factor * self.data.machine_manure_dry_mass +
                               application_moisture_factor) / new_total_mass
        new_field_coverage = (self.data.machine_manure_field_coverage * self.data.machine_manure_dry_mass +
                              field_coverage * dry_matter_mass) / new_total_mass
        self.data.machine_manure_dry_mass = new_total_mass
        self.data.machine_manure_moisture_factor = new_moisture_factor
        self.data.machine_manure_field_coverage = new_field_coverage

    def apply_grazing_manure(self, dry_matter_mass: float, dry_matter_content: float,
                             total_phosphorus_mass: float) -> None:
        """

        Parameters
        ----------
        dry_matter_mass : float
            Dry weight equivalent of this application (kg)
        dry_matter_content : float
            Fraction of this manure application that is dry matter, in the range (0.0, 1.0] (unitless)
        total_phosphorus_mass : float
            Total mass of phosphorus in this application of manure (kg)



        """
        self.data.grazing_water_extractable_inorganic_phosphorus += total_phosphorus_mass * 0.50
        self.data.grazing_water_extractable_organic_phosphorus += total_phosphorus_mass * 0.05
        self.data.grazing_stable_inorganic_phosphorus += total_phosphorus_mass * 0.1125
        self.data.grazing_stable_organic_phosphorus += total_phosphorus_mass * 33.75

        if not 0.0 < dry_matter_content <= 1.0:
            raise ValueError(f"Dry matter content must be in the range (0.0, 1.0], received: '{dry_matter_content}'.")
        new_total_mass = self.data.grazing_manure_dry_mass + dry_matter_mass
        application_moisture_factor = (1 - dry_matter_content) * dry_matter_mass



    # --- Static Methods ---
    @staticmethod
    def _determine_water_extractable_inorganic_phosphorus_fraction_by_animal(source_animal: str = None) -> float:
        """This method returns what the water extractable inorganic phosphorus fraction of total manure phosphorus mass
            should be based on the type of animal that produced the manure.

        Parameters
        ----------
        source_animal : str, default=None
            Type of animal that produced this manure (options are "CATTLE", "SWINE", or "POULTRY") (unitless)

        Returns
        -------
        float
             Fraction of water extractable inorganic phosphorus in a manure application, when that manure is produced by
             a certain type of animal.

        Raises
        ------
        ValueError
            If source animal of the manure application is not None, 'CATTLE', 'SWINE', or 'POULTRY'

        """
        if source_animal is None:
            return 0.45
        elif source_animal == "CATTLE":
            return 0.50
        elif source_animal == "SWINE":
            return 0.35
        elif source_animal == "POULTRY":
            return 0.20
        else:
            raise ValueError(f"Expected manure source animal to be 'CATTLE', 'SWINE', 'POULTRY', or None, "
                             f"received: '{source_animal}'.")

    @staticmethod
    def _determine_field_coverage(field_size: float, total_manure_applied: float) -> float:
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
        manure to 659 cubic centimeters of field_coverage (James et al., 2007).

        References
        ----------
        James E., Kleinman P., Veith T., Stedman R., Sharpley A. (2007) Phosphorus contributions from
            pastured dairy cattle to streams of the Cannonsville Watershed, New York. Journal of Soil
            and Water Conservation 62:40-47.

        """
        