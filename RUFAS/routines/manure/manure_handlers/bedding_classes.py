from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Dict
from typing import Optional
from typing import Type

from RUFAS.routines.manure.default_enum.default_enum import DefaultEnum
from RUFAS.routines.manure.pen.manure_management_pen import ManureManagementPen


class BeddingType(DefaultEnum):
    """Enumerates the different types of bedding."""

    SAWDUST = 'sawdust'
    MANURE_SOLIDS = 'manure solids'
    SAND = 'sand'
    DEFAULT = SAND


class BaseBedding(ABC):
    """Base class for all bedding types.

    Attributes
        bedding_mass_per_day: Amount of bedding needed for each animal per day, kg/animal/day.
        bedding_density: Density of the bedding, kg/m^3.
        bedding_dry_matter: Dry matter content of the bedding, kg.
        bedding_washed_percent: Percent of the bedding that is washed away, %.
        bedding_type: Type of bedding.

    """

    def __init__(self, bedding_config: BeddingConfig) -> None:
        """Initialize the base bedding class."""

        self.bedding_mass_per_day = bedding_config.bedding_mass_per_day
        self.bedding_density = bedding_config.bedding_density
        self.bedding_dry_matter = bedding_config.bedding_dry_matter
        self.bedding_washed_percent = bedding_config.bedding_washed_percent
        self.bedding_type = bedding_config.bedding_type

    def total_bedding_washed(self, pen: ManureManagementPen) -> float:
        """Return the total amount of bedding that is washed away.

        Parameters
            pen: A ManureManagementPen object.

        Returns:
            Total amount of bedding that is washed away, kg/animal/day.

        """

        return self.bedding_washed_percent * self.total_bedding_mass(pen)

    @abstractmethod
    def total_bedding_mass(self, pen: ManureManagementPen) -> float:
        """Return the total amount of bedding needed for all animals in the given pen.

        Returns
            Total amount of bedding needed for all animals in the given pen, kg/day.

        """

        pass

    def total_bedding_volume(self, pen: ManureManagementPen) -> float:
        """Return the total volume of bedding needed for all animals in the given pen.

        Returns
            Total volume of bedding needed for all animals in the given pen, m^3/day.

        """

        return self.total_bedding_mass(pen) / self.bedding_density


class BaseOrganicBedding(BaseBedding):
    """Base class for all organic bedding types."""

    def total_bedding_mass(self, pen: ManureManagementPen) -> float:
        """Return the total amount of bedding needed for all animals in the given pen.

        Returns
            Total amount of bedding needed for all animals in the given pen, kg/day.

        """
        return pen.num_animals * self.bedding_mass_per_day  # kg/day


class SawdustBedding(BaseOrganicBedding):
    """Class for sawdust bedding."""

    pass


class ManureSolidsBedding(BaseOrganicBedding):
    """Class for manure solids bedding."""

    pass


class SandBedding(BaseBedding):
    """Class for sand bedding.

    Attributes
        All inherited attributes from the parent classes.
        In addition:
        sand_removal_efficiency: Efficiency of removing sand from the bedding, [0.0, 1.0], unitless.

    """

    def __init__(self, bedding_config: BeddingConfig) -> None:
        """Initialize the sand bedding class."""

        super().__init__(bedding_config)
        self.sand_removal_efficiency = bedding_config.sand_removal_efficiency

    def total_bedding_mass(self, pen: ManureManagementPen) -> float:
        """Return the total amount of bedding needed for all animals in the given pen.

        Returns
            Total amount of bedding needed for all animals in the given pen, kg/day.

        """

        bedding_mass = pen.num_animals * self.bedding_mass_per_day  # kg/day
        return bedding_mass * (1 - self.sand_removal_efficiency)


@dataclass
class BeddingConfig:
    """Class for storing the configuration of a bedding.

    Attributes
        bedding_mass_per_day: Amount of bedding needed for each animal per day, kg/animal/day.
        bedding_density: Density of the bedding, kg/m^3.
        bedding_dry_matter: Dry matter content of the bedding, kg.
        bedding_washed_percent: Percent of the bedding that is washed away, %.
        sand_removal_efficiency: Efficiency of removing sand from the bedding, [0.0, 1.0], unitless.

    """

    bedding_mass_per_day: float
    bedding_density: float
    bedding_dry_matter: float
    bedding_washed_percent: float
    bedding_type: BeddingType
    sand_removal_efficiency: float = 0.0


class DefaultBeddingConfigFactory:
    """Class for creating default bedding configurations."""

    SAWDUST_BEDDING_CONFIG = BeddingConfig(
            bedding_mass_per_day=1.97,
            bedding_density=250.0,
            bedding_dry_matter=0.9,
            bedding_washed_percent=1.0,
            bedding_type=BeddingType.SAWDUST,
    )

    MANURE_SOLIDS_BEDDING_CONFIG = BeddingConfig(
            bedding_mass_per_day=1.97,
            bedding_density=250.0,
            bedding_dry_matter=0.9,
            bedding_washed_percent=1.0,
            bedding_type=BeddingType.MANURE_SOLIDS,
    )

    SAND_BEDDING_CONFIG = BeddingConfig(
            bedding_mass_per_day=25.0,
            bedding_density=1500.0,
            bedding_dry_matter=0.9,
            bedding_washed_percent=25.0,
            sand_removal_efficiency=0.5,
            bedding_type=BeddingType.SAND,
    )

    @classmethod
    def get_instance(cls, bedding_type: BeddingType) -> BeddingConfig:
        """Return the default bedding configuration for the given bedding type.

        Parameters
            bedding_type: Type of bedding.

        Returns
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
                     bedding_config: Optional[BeddingConfig] = None) \
            -> BaseBedding:
        """Return the bedding object for the given bedding type name.

        Parameters
            bedding_name: Name of the bedding type.
            bedding_config: Custom configuration of the bedding, if any.

        Returns
            Bedding object for the given bedding type name.

        """

        bedding_class_by_type: Dict[BeddingType, Type[BaseBedding]] = {
            BeddingType.SAWDUST: SawdustBedding,
            BeddingType.MANURE_SOLIDS: ManureSolidsBedding,
            BeddingType.SAND: SandBedding,
        }

        bedding_type = BeddingType.get_type(bedding_type_name)
        bedding_class = bedding_class_by_type[bedding_type]

        if bedding_config:
            bedding_obj = bedding_class(bedding_config)
        else:
            default_bedding_config = DefaultBeddingConfigFactory.get_instance(bedding_type)
            bedding_obj = bedding_class(default_bedding_config)

        return bedding_obj
