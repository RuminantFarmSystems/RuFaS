from abc import ABC
from abc import abstractmethod
from enum import Enum
from dataclasses import dataclass
from typing import Dict
from typing import Type


class BeddingType(Enum):
    """
    Enumerate the different types of bedding.

    This class, derived from the `DefaultEnum` base class, provides a set of predefined constants
    that represent different types of bedding such as sawdust, straw, and sand. The default type is sand.

    Attribute
    ----------
    SAWDUST : str
        Represent the 'sawdust' type of bedding.
    CBPB_SAWDUST : str
        Represent the 'CBPB sawdust' type of bedding.
    MANURE_SOLIDS : str
        Represent the 'manure solids' type of bedding.
    STRAW : str
        Represent the 'straw' type of bedding.
    SAND : str
        Represent the 'sand' type of bedding.
    NONE : str
        Represent no bedding.

    """

    SAWDUST = "sawdust"
    CBPB_SAWDUST = "CBPB sawdust"
    MANURE_SOLIDS = "manure solids"
    STRAW = "straw"
    SAND = "sand"
    NONE = "none"


@dataclass
class BeddingConfig:
    bedding_mass_per_day: float
    """Quantity of bedding required per animal per day (:math:`kg/animal/day`)."""

    bedding_density: float
    """Density of the bedding (:math:`kg/m^3`)."""

    bedding_dry_matter_content: float
    """
    Dry matter content in the bedding (unitless).
    Value should be in the range :math:`[0.7 - 1.0]`.
    """

    bedding_cleaned_fraction: float
    """
    Fraction of bedding that is removed from the barn (unitless).
    Value should be in the range :math:`[0.7 - 1.0]`.
    """

    bedding_carbon_fraction: float
    """
    Fraction of bedding that is composed of carbon (unitless).
    Value should be in the range :math:`[0.0 - 1.0]`.
    """

    bedding_phosphorus_content: float
    """Quantity of phosphorus in the bedding (kg)."""

    bedding_type: BeddingType
    """Type of bedding."""

    sand_removal_efficiency: float
    """
    Efficiency of removing sand from the bedding (unitless).
    Value should be in the range :math:`[0.7 - 1.0]`.
    """


class BaseBedding(ABC):
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

    def calc_total_bedding_washed(self, num_animals: int) -> float:
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
        return self.bedding_cleaned_fraction * self.calc_total_bedding_mass(num_animals)

    @abstractmethod
    def calc_total_bedding_mass(self, num_animals: int) -> float:
        """
        Abstract method to calculate the total amount of bedding needed for all animals.

        Parameters
        ----------
        num_animals : int
            The number of animals in the pen.

        Returns
        -------
        float
            The total amount of bedding needed for all animals (kg/day).

        """
        pass

    def calc_total_bedding_volume(self, num_animals: int) -> float:
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
        return self.calc_total_bedding_mass(num_animals) / self.bedding_density

    def calc_total_bedding_dry_solids(self, num_animals: int) -> float:
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
        return self.calc_total_bedding_mass(num_animals) * self.bedding_dry_matter_content


class BaseOrganicBedding(BaseBedding):
    """
    Abstract base class for all organic bedding types.

    This class extends the BaseBedding class and provides a method to calculate the total
    amount of bedding needed for all animals in a pen.

    """

    def calc_total_bedding_mass(self, num_animals: int) -> float:
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
        return num_animals * self.bedding_mass_per_day


class SawdustBedding(BaseOrganicBedding):
    """
    A concrete class representing sawdust bedding.

    All attributes and methods are inherited from BaseOrganicBedding.
    """

    pass


class CBPBSawdustBedding(BaseOrganicBedding):
    """
    A concrete class representing sawdust bedding type for compost bedded pack barns.

    All attributes and methods are inherited from BaseOrganicBedding.
    """

    pass


class ManureSolidsBedding(BaseOrganicBedding):
    """
    A concrete class representing manure solids bedding.

    All attributes and methods are inherited from BaseOrganicBedding.
    """

    pass


class StrawBedding(BaseOrganicBedding):
    """
    A concrete class representing straw bedding.

    All attributes and methods are inherited from BaseOrganicBedding.
    """

    pass


class SandBedding(BaseBedding):
    """
    A concrete class representing sand bedding.

    In addition to the attributes inherited from the parent classes, this class also includes
    sand_removal_efficiency.

    Attributes
    ----------
    sand_removal_efficiency : float
        Efficiency of removing sand from the bedding (unitless). Range: [0.0, 1.0].

    """

    def __init__(self, name: str, bedding_config: BeddingConfig) -> None:
        """
        Initialize the sand bedding class with a specific configuration.

        Parameters
        ----------
        name : str
            Identifier for the sand bedding configuration being used here.
        bedding_config : BeddingConfig
            A BeddingConfig object that specifies config data for sand bedding.

        """
        super().__init__(name, bedding_config)
        self.sand_removal_efficiency = bedding_config.sand_removal_efficiency

    def calc_total_bedding_mass(self, num_animals: int) -> float:
        """
        Calculate the total amount of bedding needed for all animals in the given pen.

        The total mass is adjusted by the efficiency of sand removal.

        Parameters
        ----------
        num_animals : int
            The number of animals in the pen.

        Returns
        -------
        float
            Total amount of bedding needed for all animals in the given pen (kg/day).

        """
        bedding_mass = num_animals * self.bedding_mass_per_day
        return bedding_mass * (1 - self.sand_removal_efficiency)


class NoBedding(BaseBedding):
    """
    A concrete class representing no bedding.

    Notes
    -----
    Because this class represents no bedding, it overrides inherited methods to simply return 0.0, to avoid possible
    division-by-zero errors.

    """

    def calc_total_bedding_washed(self, num_animals: int) -> float:
        return 0.0

    def calc_total_bedding_mass(self, num_animals: int) -> float:
        return 0.0

    def calc_total_bedding_volume(self, num_animals: int) -> float:
        return 0.0

    def calc_total_bedding_dry_solids(self, num_animals: int) -> float:
        return 0.0


class BeddingFactory:
    """
    A factory class for creating bedding objects.

    Notes
    -----
    This class leverages the Factory design pattern to instantiate bedding objects of different types.
    Based on the bedding type and the configuration provided, a new bedding instance will be manufactured.

    """

    @classmethod
    def get_instance(
        cls,
        bedding_name: str,
        bedding_config: BeddingConfig,
    ) -> BaseBedding:
        """
        Create a bedding object of the specified type.

        Parameters
        ----------
        bedding_name : str
            Name of the bedding configuration to be used.
        bedding_config : BeddingConfig
            Configuration of the bedding to be used.

        Returns
        -------
        BaseBedding
            Bedding object of the specified type.

        """
        bedding_class_by_type: Dict[BeddingType, Type[BaseBedding]] = {
            BeddingType.SAWDUST: SawdustBedding,
            BeddingType.CBPB_SAWDUST: CBPBSawdustBedding,
            BeddingType.MANURE_SOLIDS: ManureSolidsBedding,
            BeddingType.STRAW: StrawBedding,
            BeddingType.SAND: SandBedding,
            BeddingType.NONE: NoBedding,
        }

        bedding_class = bedding_class_by_type[bedding_config.bedding_type]

        bedding_obj = bedding_class(bedding_name, bedding_config)

        return bedding_obj
