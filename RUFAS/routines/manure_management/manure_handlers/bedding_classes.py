from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import auto
from typing import Dict, Optional, Tuple, Type

from RUFAS.routines.manure_management.helpers.enum_helpers import ExtendedEnum
from RUFAS.routines.manure_management.misc.simple_pen import SimplePen


# TODO: Add straw bedding
class BeddingEnum(ExtendedEnum):
    SAWDUST = auto()
    MANURE_SOLIDS = auto()

    SAND = auto()
    DEFAULT = SAND


class BaseBedding:
    def __init__(self, mass: float,
                 density: float,
                 bedding_dry_matter=0.0,
                 bedding_washed_percent=0.0,
                 bedding_mass_per_day=0.0,
                 sand_removal_efficiency=0.0):
        self.mass = mass  # kg/animal/day
        self.density = density  # kg/m^3
        self.bedding_dry_matter = bedding_dry_matter
        self.bedding_washed_percent = bedding_washed_percent
        self.bedding_mass_per_day = bedding_mass_per_day  # kg/animal/day
        self.sand_removal_efficiency = sand_removal_efficiency
        self.bedding_enum = None

    @property
    def bedding_washed(self) -> float:
        return self.bedding_washed_percent * self.bedding_mass_per_day

    def total_bedding_mass(self, pen: SimplePen) -> float:
        bedding_mass = pen.num_animals * self.bedding_mass_per_day  # kg/day
        return bedding_mass * (1 - self.sand_removal_efficiency)

    def total_bedding_volume(self, pen: SimplePen) -> float:
        return self.total_bedding_mass(pen) / self.density  # m^3/day

    @property
    def volume(self):
        """A calculated attribute for volume.

        Returns
            Volume of bedding. Units: m^3/day

        """

        return self.mass / self.density

    def __add__(self, other: BaseBedding) -> BaseBedding:
        if not isinstance(other, BaseBedding):
            raise TypeError('Added two incompatible types.')
        new_mass = self.mass + other.mass
        new_volume = self.volume + other.volume
        new_density = new_mass / new_volume
        return BaseBedding(new_mass, new_density)

    def __str__(self):
        return f'{self.__class__.__name__}: ' \
               f'mass = {self.mass}, ' \
               f'density = {self.density}, ' \
               f'volume = {self.volume}'


# 3 subtypes: they have different mass usage per animal per day
# recycled manure fibers (solids) DEFAULT
# sawdust
# straw

class OrganicBedding(BaseBedding):

    def __add__(self, other: BaseBedding) -> BaseBedding:
        b = super().__add__(other)
        return OrganicBedding(b.mass, b.density)


class SawdustBedding(OrganicBedding):
    pass


class ManureSolidsBedding(OrganicBedding):
    pass


class SandBedding(BaseBedding):

    def __add__(self, other: BaseBedding) -> BaseBedding:
        b = super().__add__(other)
        return SandBedding(b.mass, b.density)


@dataclass(frozen=True)
class BeddingConfig:
    mass: float
    density: float
    bedding_dry_matter: float
    bedding_washed_percent: float
    bedding_mass_per_day: float
    sand_removal_efficiency: float = 0.0


class BeddingFactory:
    @classmethod
    def get_instance(cls, bedding_type: str, bedding_config: Optional[BeddingConfig] = None) -> BaseBedding:
        enum_to_init_data: Dict[BeddingEnum, Tuple[Type[BaseBedding], BeddingConfig]] = {
            BeddingEnum.SAWDUST: (SawdustBedding, BeddingConfig(mass=1.97,
                                                                density=250.0,
                                                                bedding_dry_matter=0.9,
                                                                bedding_washed_percent=1.0,
                                                                bedding_mass_per_day=1.97)),
            BeddingEnum.MANURE_SOLIDS: (ManureSolidsBedding, BeddingConfig(mass=1.97,
                                                                           density=250.0,
                                                                           bedding_dry_matter=0.9,
                                                                           bedding_washed_percent=1.0,
                                                                           bedding_mass_per_day=4.0)),
            BeddingEnum.SAND: (SandBedding, BeddingConfig(mass=25.0,
                                                          density=1500.0,
                                                          bedding_dry_matter=0.9,
                                                          bedding_washed_percent=1.0,
                                                          bedding_mass_per_day=25.0,
                                                          sand_removal_efficiency=1.0))
        }

        bedding_enum = BeddingEnum.get_enum(bedding_type)
        bedding_class = enum_to_init_data[bedding_enum][0]

        if bedding_config:
            bedding = bedding_class(**asdict(bedding_config))
        else:
            init_data = enum_to_init_data[bedding_enum][1]
            bedding = bedding_class(**asdict(init_data))

        bedding.bedding_enum = bedding_enum
        return bedding

