from RUFAS.data_structures.manure_to_crop_soil_connection import NutrientRequest, NutrientRequestResults
from RUFAS.data_structures.manure_types import ManureType

"""
The Field Manure Supplier uses ratios of dry mass to wet mass, Nitrogen to dry mass, and Phosphorus to dry mass to
project total amounts of manure applied. These ratios were derived from the ManureDB
(http://manuredb.umn.edu/?a=Dairy&y=2024&y=2023&y=2022&y=2021&y=2020) for the year of 2023. The liquid ratios were
calculated using the data collected for manure designated as "Slurry" and "Liquid", and the solid ratios for manure
designated as "Solid".
"""


"""Factor for converting dry matter mass of liquid manure to wet mass."""
LIQUID_MANURE_DRY_MASS_TO_WET_MASS = 21.739

"""Factor for converting nitrogen mass to dry matter mass of liquid manure."""
NITROGEN_TO_LIQUID_MANURE_DRY_MASS = 20.909

"""Factor for converting phosphorus mass to dry matter mass of liquid manure."""
PHOSPHORUS_TO_LIQUID_MANURE_DRY_MASS = 51.111


"""Factor for converting dry matter mass of solid manure to wet mass."""
SOLID_MANURE_DRY_MASS_TO_WET_MASS = 2.469

"""Factor for converting nitrogen mass to dry matter mass of solid manure."""
NITROGEN_TO_SOLID_MANURE_DRY_MASS = 67.516

"""Factor for converting phosphorus mass to dry matter mass of solid manure."""
PHOSPHORUS_TO_SOLID_MANURE_DRY_MASS = 135.033

"""Maps the currently supported manure types to the constants associated with them."""
TYPE_TO_CONSTANTS_MAP = {
    ManureType.LIQUID: {
        "mass": LIQUID_MANURE_DRY_MASS_TO_WET_MASS,
        "nitrogen": NITROGEN_TO_LIQUID_MANURE_DRY_MASS,
        "phosphorus": PHOSPHORUS_TO_LIQUID_MANURE_DRY_MASS,
    },
    ManureType.SOLID: {
        "mass": SOLID_MANURE_DRY_MASS_TO_WET_MASS,
        "nitrogen": NITROGEN_TO_SOLID_MANURE_DRY_MASS,
        "phosphorus": PHOSPHORUS_TO_SOLID_MANURE_DRY_MASS,
    },
}


class FieldManureSupplier:
    """
    Supplies manure for field applications.

    Methods
    -------
    request_nutrients(request: NutrientRequest) -> NutrientRequestResults
        Receives a request for manure nutrients and constructs a manure amount to fulfill the request.

    """

    @staticmethod
    def request_nutrients(request: NutrientRequest) -> NutrientRequestResults:
        """
        Formulates a manure supply response based on a nutrient request.

        Parameters
        ----------
        request : NutrientRequest
            Request for manure containing masses of N, P and the desired manure type (liquid or solid).

        Returns
        -------
        NutrientRequestResults
            Response containing manure mass, nutrient mass, and other nutrient details in response to the request.

        Notes
        -----
        This method calculates the total mass of manure that would be applied for each of the requested nutrients, then
        selects the smallest mass and uses it to construct the amount of manure that is actually returned. If one of the
        requested nutrient masses is 0, that nutrient is not considered when formulating the manure result.

        """
        constants = TYPE_TO_CONSTANTS_MAP[request.manure_type]

        nitrogen_projected_mass = request.nitrogen * constants["nitrogen"]
        phosphorus_projected_mass = request.phosphorus * constants["phosphorus"]

        if nitrogen_projected_mass != 0.0 and phosphorus_projected_mass != 0.0:
            min_dry_mass = min(nitrogen_projected_mass, phosphorus_projected_mass)
        elif nitrogen_projected_mass == 0.0:
            min_dry_mass = phosphorus_projected_mass
        else:
            min_dry_mass = nitrogen_projected_mass

        nitrogen_mass = min_dry_mass / constants["nitrogen"]
        phosphorus_mass = min_dry_mass / constants["phosphorus"]
        wet_mass = min_dry_mass * constants["mass"]
        dry_matter_fraction = 1 / constants["mass"]

        return NutrientRequestResults(
            nitrogen=nitrogen_mass,
            phosphorus=phosphorus_mass,
            dry_matter=min_dry_mass,
            total_manure_mass=wet_mass,
            dry_matter_fraction=dry_matter_fraction,
        )
