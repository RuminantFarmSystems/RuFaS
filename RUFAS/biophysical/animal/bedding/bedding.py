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
        Dry matter content in the bedding (unitless).
    bedding_carbon_fraction : float
        Fraction of bedding that is composed of carbon (unitless).
    bedding_phosphorus_content : float
        Quantity of phosphorus in the bedding (kg).
    bedding_type : str
        Type of bedding as a string.

    Methods
    -------
    calc_total_bedding_mass(num_animals: int) -> float
        Calculates total amount of bedding needed.
    calc_total_bedding_volume(num_animals: int) -> float
        Calculates total volume of bedding needed.
    calc_total_bedding_dry_solids(num_animals: int) -> float
        Calculates total dry solids in the bedding.
    calc_total_bedding_water(num_animals: int) -> float
        Calculates total water in the bedding.

    """

    def __init__(
            self,
            name: str,
            bedding_mass_per_day: float,
            bedding_density: float,
            bedding_dry_matter_content: float,
            bedding_carbon_fraction: float,
            bedding_phosphorus_content: float,
            bedding_type: BeddingType,
            sand_removal_efficiency: float,
    ) -> None:
        """Initialize the base bedding class with specific configuration data."""
        self.name = name
        self.bedding_mass_per_day = bedding_mass_per_day
        self.bedding_density = bedding_density
        self.bedding_dry_matter_content = bedding_dry_matter_content
        self.bedding_carbon_fraction = bedding_carbon_fraction
        self.bedding_phosphorus_content = bedding_phosphorus_content
        self.bedding_type = bedding_type
        self.sand_removal_efficiency = (
            sand_removal_efficiency if self.bedding_type == BeddingType.SAND else 0.0
        )

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
        total_bedding_mass = self.bedding_mass_per_day * num_animals
        if self.bedding_type == BeddingType.SAND:
            return total_bedding_mass * (1 - self.sand_removal_efficiency)
        elif self.bedding_type == BeddingType.NONE:
            return 0.0
        else:
            return total_bedding_mass

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
        return (
            self.calculate_total_bedding_mass(num_animals) / self.bedding_density
            if self.bedding_type != BeddingType.NONE
            else 0
        )

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
        return (
            self.calculate_total_bedding_mass(num_animals) * self.bedding_dry_matter_content
            if self.bedding_type != BeddingType.NONE
            else 0
        )

    def calculate_bedding_water(self, num_animals: int) -> float:
        """
        Calculate the total water in the bedding.

        Parameters
        ----------
        num_animals : int
            The number of animals in the pen.

        Returns
        -------
        float
            The total water in the bedding (kg/day).

        """
        return (
            self.calculate_total_bedding_mass(num_animals) * (1 - self.bedding_dry_matter_content)
            if self.bedding_type != BeddingType.NONE
            else 0
        )
