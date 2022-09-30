from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import asdict, dataclass
from enum import auto
from typing import Dict, Optional, Tuple, Type

from RUFAS.routines.manure_management.helpers.enum_helpers import ExtendedEnum
from RUFAS.routines.manure_management.misc.simple_pen import SimplePen


class BeddingType(ExtendedEnum):
    """Enumerates the different types of bedding."""

    SAWDUST = auto()
    MANURE_SOLIDS = auto()
    STRAW = auto()
    SAND = auto()
    DEFAULT = SAND


class BaseBedding(ABC):
    """Base class for all bedding types.

    Attributes
        mass: , kg/animal/day.  # TODO: Describe this better
        density: Density of the bedding, kg/m^3.
        bedding_dry_matter: Dry matter content of the bedding, kg. # TODO: What is the unit of this?
        bedding_washed_percent: Percent of the bedding that is washed away, %.
        bedding_mass_per_day: Amount of bedding needed for each animal per day, kg/animal/day.
        bedding_type: Type of bedding.

    """

    def __init__(self, bedding_config: BeddingConfig) -> None:
        """Initialize the bedding class."""

        self.mass = bedding_config.mass  # kg/animal/day
        self.density = bedding_config.density
        self.bedding_dry_matter = bedding_config.bedding_dry_matter
        self.bedding_washed_percent = bedding_config.bedding_washed_percent
        self.bedding_mass_per_day = bedding_config.bedding_mass_per_day
        self.bedding_type: Optional[BeddingType] = None

    @property
    def bedding_washed(self) -> float:
        """Return the amount of bedding that is washed away.

        Returns:
            Amount of bedding that is washed away, kg/animal/day.

        """

        return self.bedding_washed_percent * self.bedding_mass_per_day

    @abstractmethod
    def total_bedding_mass(self, pen: SimplePen) -> float:
        """Return the total amount of bedding needed for all animals in the given pen.

        Returns
            Total amount of bedding needed for all animals in the given pen, kg/day.

        """

        pass

    def total_bedding_volume(self, pen: SimplePen) -> float:
        """Return the total volume of bedding needed for all animals in the given pen.

        Returns
            Total volume of bedding needed for all animals in the given pen, m^3/day.

        """

        return self.total_bedding_mass(pen) / self.density

    @property
    def volume(self):
        """Return the volume of the bedding.

        Returns
            Volume of the bedding, m^3.

        """

        return self.mass / self.density


class BaseOrganicBedding(BaseBedding):
    """Base class for all organic bedding types."""

    def total_bedding_mass(self, pen: SimplePen) -> float:
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
        sand_removal_efficiency: Efficiency of removing sand from the bedding, [0.0, 1.0], unitless.

    """

    def __init__(self, bedding_config: BeddingConfig) -> None:
        """Initialize the sand bedding class."""

        super().__init__(bedding_config)
        self.sand_removal_efficiency = bedding_config.sand_removal_efficiency

    def total_bedding_mass(self, pen: SimplePen) -> float:
        """Return the total amount of bedding needed for all animals in the given pen.

        Returns
            Total amount of bedding needed for all animals in the given pen, kg/day.

        """

        bedding_mass = pen.num_animals * self.bedding_mass_per_day  # kg/day
        return bedding_mass * (1 - self.sand_removal_efficiency)


@dataclass(frozen=True)
class BeddingConfig:
    """Class for storing the configuration of a bedding.

    Attributes
        mass: , kg/animal/day.  # TODO: Describe this better
        density: Density of the bedding, kg/m^3.
        bedding_dry_matter: Dry matter content of the bedding, kg. # TODO: What is the unit of this?
        bedding_washed_percent: Percent of the bedding that is washed away, %.
        bedding_mass_per_day: Amount of bedding needed for each animal per day, kg/animal/day.
        sand_removal_efficiency: Efficiency of removing sand from the bedding, [0.0, 1.0], unitless.

    """

    mass: float
    density: float
    bedding_dry_matter: float
    bedding_washed_percent: float
    bedding_mass_per_day: float
    sand_removal_efficiency: float = 0.0


class DefaultBeddingConfigFactory:
    """Class for creating default bedding configurations."""

    SAWDUST_BEDDING_CONFIG = BeddingConfig(mass=1.97,
                                           density=250.0,
                                           bedding_dry_matter=0.9,
                                           bedding_washed_percent=1.0,
                                           bedding_mass_per_day=1.97)

    MANURE_SOLIDS_BEDDING_CONFIG = BeddingConfig(mass=1.97,
                                                 density=250.0,
                                                 bedding_dry_matter=0.9,
                                                 bedding_washed_percent=1.0,
                                                 bedding_mass_per_day=1.97)

    SAND_BEDDING_CONFIG = BeddingConfig(mass=25.0,
                                        density=1500.0,
                                        bedding_dry_matter=0.9,
                                        bedding_washed_percent=25.0,
                                        bedding_mass_per_day=1.0,
                                        sand_removal_efficiency=0.5)  # TODO: This is a placeholder value

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
    def get_instance(cls, bedding_name: str, bedding_config: Optional[BeddingConfig] = None) -> BaseBedding:
        """Return the bedding object for the given bedding name.

        Parameters
            bedding_name: Name of the bedding type.
            bedding_config: Custom configuration of the bedding, if any.

        Returns
            Bedding object for the given bedding name.

        """

        bedding_class_by_type: Dict[BeddingType, Type[BaseBedding]] = {
            BeddingType.SAWDUST: SawdustBedding,
            BeddingType.MANURE_SOLIDS: ManureSolidsBedding,
            BeddingType.SAND: SandBedding,
        }

        bedding_type = BeddingType.get_type(bedding_name)
        bedding_class = bedding_class_by_type[bedding_type]

        if bedding_config:
            bedding = bedding_class(bedding_config)
        else:
            default_bedding_config = DefaultBeddingConfigFactory.get_instance(bedding_type)
            bedding = bedding_class(default_bedding_config)

        bedding.bedding_type = bedding_type
        return bedding
