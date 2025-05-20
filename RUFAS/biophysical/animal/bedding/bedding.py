from typing import Optional

from RUFAS.biophysical.animal.data_types.bedding_types import BeddingType


class Bedding:
    """
    Abstract base class for all bedding types.

    This class provides a base for all bedding types. It initializes with a configuration of bedding
    attributes and includes methods for calculating various bedding properties. While bedding mass
    and nutrients are added to individual manure streams, which may represent only a fraction of the
    total manure excreted by a pen, the mass of bedding applied per animal is based on the total
    number of animals housed in the pen from which the manure stream originated.

    Attributes
    ----------
    name : str
        Unique identifier to reference this bedding configuration.
    bedding_mass_per_day : float
        The daily mass of fresh bedding added to the housing area per animal per day on a wet weight
        basis (kg/animal/day). Bedding mass is applied based on the total number of animals in the pen,
        and is not based on the stream proportion of the manure stream the bedding is assigned to.
    bedding_density : float
        The density of the bedding on a wet weight basis (kg/:math:`m^3`).
    bedding_dry_matter_content : float
        The fraction (0.XX) of dry matter in the bedding (unitless).
    bedding_carbon_fraction : float
        The bedding carbon content as a fraction (0.XX) of total mass, on a wet weight basis (unitless).
    bedding_phosphorus_content : float
        The bedding phosphorus content as a fraction (0.XX) of total mass, on a wet weight basis (unitless).
    bedding_type : str
        The type of bedding material as a string.

    Methods
    -------
    calc_total_bedding_mass(num_animals: int) -> float
        Calculates total mass of bedding used.
    calc_total_bedding_volume(num_animals: int) -> float
        Calculates total volume of bedding used.
    calc_total_bedding_dry_solids(num_animals: int) -> float
        Calculates the mass of total dry solids in the bedding used.
    calc_total_bedding_water(num_animals: int) -> float
        Calculates the mass of water in the bedding used.

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
        sand_removal_efficiency: Optional[float] = None,
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
            sand_removal_efficiency
            if (self.bedding_type == BeddingType.SAND and sand_removal_efficiency is not None)
            else 0.0
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
            Total amount of bedding to be added to the ManureStream instance (kg/day).

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
            The total volume to be added to the ManureStream instance (:math:`m^3`/day).

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
            The total amount of dry solids to be added to the ManureStream instance (kg/day).

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
            The total water to be added to the ManureStream instance (kg/day).

        """
        return (
            self.calculate_total_bedding_mass(num_animals) * (1 - self.bedding_dry_matter_content)
            if self.bedding_type != BeddingType.NONE
            else 0
        )
