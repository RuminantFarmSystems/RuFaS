from RUFAS.biophysical.animal.data_types.bedding_config import BeddingConfig
from RUFAS.biophysical.animal.data_types.bedding_types import BeddingType


class Bedding:
    """
    Abstract base class for all bedding types.

    This class provides a base for all bedding types. It initializes with a configuration of bedding
    attributes and includes methods for calculating various bedding properties.

    Attributes
    ----------
    name : str
        The name of the bedding.
    bedding_mass_per_day : float
        Quantity of bedding required per animal per day (kg/animal/day).
    bedding_density : float
        Density of the bedding (kg/:math:`m^3`).
    bedding_dry_matter_content : float
        Dry matter content in the bedding (unitless). Value should be in the range [0.7 - 1.0].
    bedding_cleaned_fraction : float
        Fraction of bedding that is removed from the barn (unitless). Value should be in the range [0.7 - 1.0].
    bedding_carbon_fraction : float
        Fraction of bedding that is composed of carbon (unitless). Value should be in the range [0.0 - 1.0].
    bedding_phosphorus_content : float
        Quantity of phosphorus in the bedding (kg).
    bedding_type : str
        Type of bedding as a string.

    Methods
    -------
    calc_total_bedding_washed(num_animals: int) -> float
        Calculates total amount of bedding washed away.
    calc_total_bedding_mass(num_animals: int) -> float
        Calculates total amount of bedding needed.
    calc_total_bedding_volume(num_animals: int) -> float
        Calculates total volume of bedding needed.
    calc_total_bedding_dry_solids(num_animals: int) -> float
        Calculates total dry solids in the bedding.

    """

    def __init__(self, name: str, bedding_config: BeddingConfig) -> None:
        """
        Initialize the base bedding class with specific configuration data.

        Parameters
        ----------
        name : str
            Identifier for the bedding configuration being used here.
        bedding_config : BeddingConfig
            A BeddingConfig object that specifies configuration data specific to the choice of bedding.

        """
        self.name = name
        self.bedding_mass_per_day = bedding_config.bedding_mass_per_day
        self.bedding_density = bedding_config.bedding_density
        self.bedding_dry_matter_content = bedding_config.bedding_dry_matter_content
        self.bedding_cleaned_fraction = bedding_config.bedding_cleaned_fraction
        self.bedding_carbon_fraction = bedding_config.bedding_carbon_fraction
        self.bedding_phosphorus_content = bedding_config.bedding_phosphorus_content
        self.bedding_type = bedding_config.bedding_type
        self.sand_removal_efficiency = bedding_config.sand_removal_efficiency \
            if self.bedding_type == BeddingType.SAND else 0.0

    def calculate_total_bedding_washed(self, num_animals: int) -> float:
        """
        Calculate the total amount of bedding that is washed away.

        Parameters
        ----------
        num_animals : int
            The number of animals in the pen.

        Returns
        -------
        float
            The total amount of bedding that is washed away (kg/animal/day).

        """
        return self.bedding_cleaned_fraction * self.calculate_total_bedding_mass(num_animals) \
            if self.bedding_type != BeddingType.NONE else 0

    def calculate_total_bedding_mass(self, num_animals: int) -> float:
        """
        Calculate the total amount of bedding needed for all animals in the given pen.

        Parameters
        ----------
        num_animals : int
            The number of animals in the pen.

        Returns
        -------
        float
            Total amount of bedding needed for all animals in the given pen (kg/day).

        """
        return num_animals * self.bedding_mass_per_day if self.bedding_type != BeddingType.NONE else 0

    def calculate_total_bedding_volume(self, num_animals: int) -> float:
        """
        Calculate the total volume of bedding needed for all animals.

        Parameters
        ----------
        num_animals : int
            The number of animals in the pen.

        Returns
        -------
        float
            The total volume of bedding needed for all animals (:math:`m^3`/day).

        """
        return self.calculate_total_bedding_mass(num_animals) / self.bedding_density \
            if self.bedding_type != BeddingType.NONE else 0

    def calculate_total_bedding_dry_solids(self, num_animals: int) -> float:
        """
        Calculate the total amount of dry solids in the bedding.

        Parameters
        ----------
        num_animals : int
            The number of animals in the pen.

        Returns
        -------
        float
            The total amount of dry solids in the bedding (kg/day).

        """
        return self.calculate_total_bedding_mass(num_animals) * self.bedding_dry_matter_content \
            if self.bedding_type != BeddingType.NONE else 0

    def calculate_bedding_water(self, num_animals: int) -> float:
        return self.calculate_total_bedding_mass(num_animals) * (1 - self.bedding_dry_matter_content) \
            if self.bedding_type != BeddingType.NONE else 0
