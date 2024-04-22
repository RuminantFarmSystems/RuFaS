from RUFAS.routines.manure.manure_nutrients.nutrient_request import NutrientRequest
from RUFAS.routines.manure.manure_nutrients.nutrient_request_results import NutrientRequestResults
from RUFAS.routines.manure.manure_treatments.manure_types import ManureType
from RUFAS.output_manager import OutputManager


"""Factor for converting dry matter mass of liquid manure to wet mass."""
LIQUID_MANURE_DRY_MASS_TO_WET_MASS = 17.86

"""Factor for converting nitrogen mass to dry matter mass of liquid manure."""
NITROGEN_TO_LIQUID_MANURE_DRY_MASS = 22.4

"""Factor for converting phosphorus mass to dry matter mass of liquid manure."""
PHOSPHORUS_TO_LIQUID_MANURE_DRY_MASS = 56.0

om = OutputManager()


class FieldManureSupplier:
    """
    Supplies manure for field applications.

    Methods
    -------
    request_nutrients(request: NutrientRequest) -> NutrientRequestResults
        Receives a request for manure nutrients and constructs a manure amount to fulfill the request.

    """

    def __init__(self) -> None:
        pass

    def request_nutrients(self, request: NutrientRequest) -> NutrientRequestResults:
        """
        Receives requests for amounts of nutrients to be contained in manure and formulates manure reponses to send out.

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
        selects the smallest mass and uses it to construct the amount of manure that is actually returned.

        """
        type_to_constants_map = {
            ManureType.LIQUID: {
                "mass": LIQUID_MANURE_DRY_MASS_TO_WET_MASS,
                "nitrogen": NITROGEN_TO_LIQUID_MANURE_DRY_MASS,
                "phosphorus": PHOSPHORUS_TO_LIQUID_MANURE_DRY_MASS,
            },
            ManureType.SOLID: {
                "mass": LIQUID_MANURE_DRY_MASS_TO_WET_MASS,
                "nitrogen": NITROGEN_TO_LIQUID_MANURE_DRY_MASS,
                "phosphorus": PHOSPHORUS_TO_LIQUID_MANURE_DRY_MASS,
            },
        }

        constants = type_to_constants_map[request.manure_type]

        nitrogen_projected_mass = request.nitrogen * constants["nitrogen"]
        phosphorus_projected_mass = request.phosphorus * constants["phosphorus"]
        min_dry_mass = min(nitrogen_projected_mass, phosphorus_projected_mass)

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
