from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Dict
from typing import Optional
from typing import Type

from RUFAS.routines.manure.default_enum.default_enum import DefaultEnum


class BeddingType(DefaultEnum):
    """
    Enumerate the different types of bedding.

    This class, derived from the `DefaultEnum` base class, provides a set of predefined constants
    that represent different types of bedding such as sawdust, straw, and sand. The default type is sand.

    Attributes
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
    DEFAULT : str
        The default type of bedding is 'sand' if none is specified.

    """

    SAWDUST = "sawdust"
    CBPB_SAWDUST = "CBPB sawdust"
    MANURE_SOLIDS = "manure solids"
    STRAW = "straw"
    SAND = "sand"
    NONE = "none"
    DEFAULT = SAND


class BaseBedding(ABC):
    """
    Abstract base class for all bedding types.

    This class provides a base for all bedding types. It initializes with a configuration of bedding
    attributes and includes methods for calculating various bedding properties.

    Attributes
    ----------
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

    def __init__(self, bedding_config: BeddingConfig) -> None:
        """
        Initialize the base bedding class with specific configuration data.

        Parameters
        ----------
        bedding_config : BeddingConfig
            A BeddingConfig object that specifies configuration data specific to the choice of bedding.

        """
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
        return (
            self.calc_total_bedding_mass(num_animals) / self.bedding_dry_matter_content
        )


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

    def __init__(self, bedding_config: BeddingConfig) -> None:
        """
        Initialize the sand bedding class with a specific configuration.

        Parameters
        ----------
        bedding_config : BeddingConfig
            A BeddingConfig object that specifies config data for sand bedding.

        """
        super().__init__(bedding_config)
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


class DefaultBeddingConfigFactory:
    """
    Factory class for creating default bedding configurations.

    This class contains predefined configurations for different types of beddings. It offers a method to retrieve
    these predefined configurations based on the bedding type.

    """

    # Predefined configuration for Sawdust Bedding
    SAWDUST_BEDDING_CONFIG = BeddingConfig(
        bedding_mass_per_day=1.97,
        bedding_density=250.0,
        bedding_dry_matter_content=0.9,
        bedding_cleaned_fraction=1.0,
        bedding_carbon_fraction=0.0,
        bedding_phosphorus_content=0.0,
        bedding_type=BeddingType.SAWDUST,
        sand_removal_efficiency=0.0,
    )

    # Predefined configuration for CBPB Sawdust Bedding
    CBPB_SAWDUST_BEDDING_CONFIG = BeddingConfig(
        bedding_mass_per_day=12,
        bedding_density=350.0,
        bedding_dry_matter_content=0.9,
        bedding_cleaned_fraction=1.0,
        bedding_carbon_fraction=0.35,
        bedding_phosphorus_content=0.0,
        bedding_type=BeddingType.CBPB_SAWDUST,
        sand_removal_efficiency=0.0,
    )

    # Predefined configuration for Manure Solids Bedding
    MANURE_SOLIDS_BEDDING_CONFIG = BeddingConfig(
        bedding_mass_per_day=2.50,
        bedding_density=400.0,
        bedding_dry_matter_content=0.9,
        bedding_cleaned_fraction=1.0,
        bedding_carbon_fraction=0.0,
        bedding_phosphorus_content=0.0,
        bedding_type=BeddingType.MANURE_SOLIDS,
        sand_removal_efficiency=0.0,
    )

    # Predefined configuration for Straw Bedding
    STRAW_BEDDING_CONFIG = BeddingConfig(
        bedding_mass_per_day=1.97,
        bedding_density=100.0,
        bedding_dry_matter_content=0.9,
        bedding_cleaned_fraction=1.0,
        bedding_carbon_fraction=0.35,
        bedding_phosphorus_content=0.0,
        bedding_type=BeddingType.STRAW,
        sand_removal_efficiency=0.0,
    )

    # Predefined configuration for Sand Bedding
    SAND_BEDDING_CONFIG = BeddingConfig(
        bedding_mass_per_day=25.0,
        bedding_density=1500.0,
        bedding_dry_matter_content=0.9,
        bedding_cleaned_fraction=1.0,
        bedding_carbon_fraction=0.0,
        bedding_phosphorus_content=0.0,
        bedding_type=BeddingType.SAND,
        sand_removal_efficiency=1.0,
    )

    # Predefined configuration for no bedding
    NONE_BEDDING_CONFIG = BeddingConfig(
        bedding_mass_per_day=0.0,
        bedding_density=0.0,
        bedding_dry_matter_content=0.0,
        bedding_cleaned_fraction=0.0,
        bedding_carbon_fraction=0.0,
        bedding_phosphorus_content=0.0,
        bedding_type=BeddingType.NONE,
        sand_removal_efficiency=0.0,
    )

    @classmethod
    def get_instance(cls, bedding_type: BeddingType) -> BeddingConfig:
        """
        Fetch the default bedding configuration for the given bedding type.

        Parameters
        ----------
        bedding_type : BeddingType
            Type of the bedding.

        Returns
        -------
        BeddingConfig
            Default bedding configuration for the given bedding type.

        Raises
        ------
        ValueError
            If the given bedding type is invalid.

        """
        bedding_config_by_type = {
            BeddingType.SAWDUST: cls.SAWDUST_BEDDING_CONFIG,
            BeddingType.CBPB_SAWDUST: cls.CBPB_SAWDUST_BEDDING_CONFIG,
            BeddingType.MANURE_SOLIDS: cls.MANURE_SOLIDS_BEDDING_CONFIG,
            BeddingType.STRAW: cls.STRAW_BEDDING_CONFIG,
            BeddingType.SAND: cls.SAND_BEDDING_CONFIG,
            BeddingType.NONE: cls.NONE_BEDDING_CONFIG,
        }

        if bedding_type not in bedding_config_by_type:
            raise ValueError(
                f"Bedding type {bedding_type} is not recognized. "
                f"It may be a new bedding type that has not been added "
                f"to the 'get_instance' method."
            )

        return bedding_config_by_type[bedding_type]


class BeddingFactory:
    """
    A factory class for creating bedding objects.

    This class leverages the Factory design pattern to instantiate bedding objects of different types.
    Based on the bedding type provided, it either uses the default configuration or a custom configuration,
    if provided.

    """

    @classmethod
    def get_instance(
        cls,
        bedding_type_name: str,
        custom_bedding_config: Optional[BeddingConfig] = None,
    ) -> BaseBedding:
        """
        Create a bedding object of the specified type.

        If a custom bedding configuration is provided, it is used to create the bedding object. Otherwise,
        the default configuration for the bedding type is used.

        Parameters
        ----------
        bedding_type_name : str
            Name of the bedding type.
        custom_bedding_config : Optional[BeddingConfig], default is None
            Custom configuration of the bedding, if any.

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

        bedding_type = BeddingType.get_type(bedding_type_name)
        bedding_class = bedding_class_by_type[bedding_type]

        if custom_bedding_config:
            bedding_obj = bedding_class(custom_bedding_config)
        else:
            default_bedding_config = DefaultBeddingConfigFactory.get_instance(
                bedding_type
            )
            bedding_obj = bedding_class(default_bedding_config)

        return bedding_obj
