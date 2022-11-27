from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Dict
from typing import Optional
from typing import Type

from RUFAS.routines.manure.default_enum.default_enum import DefaultEnum


class BeddingType(DefaultEnum):
    """Enumerates the different types of bedding."""
    SAWDUST = 'sawdust'
    MANURE_SOLIDS = 'manure solids'
    SAND = 'sand'
    DEFAULT = SAND


class BaseBedding(ABC):
    """Base class for all bedding types.

    Attributes:
        bedding_mass_per_day: Amount of bedding needed for each animal per day, kg/animal/day.
        bedding_density: Density of the bedding, kg/m^3.
        bedding_dry_matter_content: Dry matter mass of the bedding, [0.7 - 1.0].
        bedding_cleaned_frac: Fraction of bedding removed from the barn [0.7 - 1.0].
        bedding_type: Type of bedding.

    """

    def __init__(self, bedding_config: BeddingConfig) -> None:
        """Initialize the base bedding class.

        Args:
            bedding_config: A BeddingConfig object that specifies config data specific to the choice
                of bedding.

        """
        self.bedding_mass_per_day = bedding_config.bedding_mass_per_day
        self.bedding_density = bedding_config.bedding_density
        self.bedding_dry_matter_content = bedding_config.bedding_dry_matter_content
        self.bedding_cleaned_frac = bedding_config.bedding_cleaned_frac
        self.bedding_type = bedding_config.bedding_type

    def total_bedding_washed(self, num_animals: int) -> float:
        """Return the total amount of bedding that is washed away.

        Args:
            num_animals: Number of animals in the pen.

        Returns:
            Total amount of bedding that is washed away, kg/animal/day.

        """
        return self.bedding_cleaned_frac * self.total_bedding_mass(num_animals)

    @abstractmethod
    def total_bedding_mass(self, num_animals: int) -> float:
        """Return the total amount of bedding needed for all animals in the given pen.

        Args:
            num_animals: Number of animals in the pen.

        Returns:
            Total amount of bedding needed for all animals in the given pen, kg/day.

        """
        pass

    def total_bedding_volume(self, num_animals: int) -> float:
        """Return the total volume of bedding needed for all animals in the given pen.

        Args:
            num_animals: Number of animals in the pen.

        Returns:
            Total volume of bedding needed for all animals in the given pen, m^3/day.

        """
        return self.total_bedding_mass(num_animals) / self.bedding_density

    def total_bedding_dry_solids(self, num_animals: int) -> float:
        """Return the total amount of dry solids in the bedding.

        Args:
            num_animals: Number of animals in the pen.

        Returns:
            Total amount of dry solids in the bedding, kg/day.

        """
        return self.total_bedding_mass(num_animals) / self.bedding_dry_matter_content


class BaseOrganicBedding(BaseBedding):
    """Base class for all organic bedding types."""

    def total_bedding_mass(self, num_animals: int) -> float:
        """Returns the total amount of bedding needed for all animals in the given pen.

        Args:
            num_animals: Number of animals in the pen.

        Returns:
            Total amount of bedding needed for all animals in the given pen, kg/day.

        """
        return num_animals * self.bedding_mass_per_day  # kg/day


class SawdustBedding(BaseOrganicBedding):
    """Class for sawdust bedding.

    Attributes:
        Inherited from BaseOrganicBedding.

    """
    pass


class ManureSolidsBedding(BaseOrganicBedding):
    """Class for manure solids bedding.

    Attributes:
        Inherited from BaseOrganicBedding.

    """
    pass


class SandBedding(BaseBedding):
    """Class for sand bedding.

    Attributes:
        All inherited attributes from the parent classes.
        In addition:
        sand_removal_efficiency: Efficiency of removing sand from the bedding, [0.0, 1.0], unitless.

    """

    def __init__(self, bedding_config: BeddingConfig) -> None:
        """Initialize the sand bedding class.

        Args:
            bedding_config: A BeddingConfig object that specifies config data for sand bedding.

        """
        super().__init__(bedding_config)
        self.sand_removal_efficiency = bedding_config.sand_removal_efficiency

    def total_bedding_mass(self, num_animals: int) -> float:
        """Returns the total amount of bedding needed for all animals in the given pen.

        Args:
            num_animals: Number of animals in the pen.

        Returns:
            Total amount of bedding needed for all animals in the given pen, kg/day.

        """
        bedding_mass = num_animals * self.bedding_mass_per_day
        return bedding_mass * (1 - self.sand_removal_efficiency)


@dataclass
class BeddingConfig:
    """Class for storing the configuration of a bedding.

    Attributes:
        bedding_mass_per_day: Amount of bedding needed for each animal per day, kg/animal/day.
        bedding_density: Density of the bedding, kg/m^3.
        bedding_dry_matter_content: Dry matter content of the bedding, [0.7, 1.0], dimensionless.
        bedding_cleaned_frac: Percent of the bedding that is washed away, [0.7, 1.0], dimensionless.
        sand_removal_efficiency: Efficiency of removing sand from the bedding, [0.7, 1.0], dimensionless.

    """
    bedding_mass_per_day: float
    bedding_density: float
    bedding_dry_matter_content: float
    bedding_cleaned_frac: float
    bedding_type: BeddingType
    sand_removal_efficiency: float = 0.0


class DefaultBeddingConfigFactory:
    """Class for creating default bedding configurations."""

    SAWDUST_BEDDING_CONFIG = BeddingConfig(
            bedding_mass_per_day=1.97,
            bedding_density=250.0,
            bedding_dry_matter_content=0.9,
            bedding_cleaned_frac=1.0,
            bedding_type=BeddingType.SAWDUST,
    )

    MANURE_SOLIDS_BEDDING_CONFIG = BeddingConfig(
            bedding_mass_per_day=2.50,
            bedding_density=400.0,
            bedding_dry_matter_content=0.9,
            bedding_cleaned_frac=1.0,
            bedding_type=BeddingType.MANURE_SOLIDS,
    )

    SAND_BEDDING_CONFIG = BeddingConfig(
            bedding_mass_per_day=25.0,
            bedding_density=1500.0,
            bedding_dry_matter_content=0.9,
            bedding_cleaned_frac=1.0,
            bedding_type=BeddingType.SAND,
            sand_removal_efficiency=1.0,
    )

    @classmethod
    def get_instance(cls, bedding_type: BeddingType) -> BeddingConfig:
        """Return the default bedding configuration for the given bedding type.

        Args:
            bedding_type: Type of bedding.

        Returns:
            Default bedding configuration for the given bedding type.

        """

        bedding_config_by_type = {
            BeddingType.SAWDUST: cls.SAWDUST_BEDDING_CONFIG,
            BeddingType.MANURE_SOLIDS: cls.MANURE_SOLIDS_BEDDING_CONFIG,
            BeddingType.SAND: cls.SAND_BEDDING_CONFIG
        }
        return bedding_config_by_type[bedding_type]


class BeddingFactory:
    """Class for creating bedding objects."""

    @classmethod
    def get_instance(cls,
                     bedding_type_name: str,
                     custom_bedding_config: Optional[BeddingConfig] = None) \
            -> BaseBedding:
        """Return the bedding object for the given bedding type name.

        Args:
            bedding_type_name: Name of the bedding type.
            custom_bedding_config: Custom configuration of the bedding, if any.

        Returns:
            Bedding object for the given bedding type name.

        """

        bedding_class_by_type: Dict[BeddingType, Type[BaseBedding]] = {
            BeddingType.SAWDUST: SawdustBedding,
            BeddingType.MANURE_SOLIDS: ManureSolidsBedding,
            BeddingType.SAND: SandBedding,
        }

        bedding_type = BeddingType.get_type(bedding_type_name)
        bedding_class = bedding_class_by_type[bedding_type]

        if custom_bedding_config:
            bedding_obj = bedding_class(custom_bedding_config)
        else:
            default_bedding_config = DefaultBeddingConfigFactory.get_instance(bedding_type)
            bedding_obj = bedding_class(default_bedding_config)

        return bedding_obj
