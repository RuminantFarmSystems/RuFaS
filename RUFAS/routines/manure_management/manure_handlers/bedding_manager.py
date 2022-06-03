from __future__ import annotations

from typing import Dict, NamedTuple

from RUFAS.routines.manure_management.misc.simple_pen import SimplePen
from RUFAS.routines.manure_management.manure_handlers.bedding_classes \
    import BaseBedding, BeddingEnum, OrganicBedding, SandBedding


class BeddingManager:
    def __init__(self, bedding_type: str):
        self.bedding_enum = BeddingEnum.get_enum(bedding_type)
        self.bedding = self.get_bedding()
        self.bedding_dry_matter: float = 0.0
        self.bedding_washed_percent: float = 0.0
        self.bedding_mass_per_day: float = 0.0  # kg/animal/day

    @property
    def bedding_washed(self) -> float:
        return self.bedding_washed_percent * self.bedding_mass_per_day

    def get_bedding(self) -> BaseBedding:
        enum_to_class: Dict[BeddingEnum, BaseBedding] = {
            BeddingEnum.SAWDUST: OrganicBedding(),
            BeddingEnum.SAND: SandBedding()
        }
        return enum_to_class[self.bedding_enum]

    @classmethod
    def get_instance(cls, bedding_type: str) -> BeddingManager:
        BeddingParams = NamedTuple('BeddingParams',
                                   [('bedding_dry_matter', float),
                                    ('bedding_washed_percent', float),
                                    ('bedding_mass_per_day', float)])
        enum_to_params = {
            BeddingEnum.SAWDUST: BeddingParams(0.9, 1.0, 1.97),
            BeddingEnum.MANURE_SOLIDS: BeddingParams(0.9, 1.0, 4.0),
            BeddingEnum.SAND: BeddingParams(0.9, 1.0, 25.0)
        }

        manager = cls(bedding_type)
        params = enum_to_params[manager.bedding_enum]
        for name, value in params._asdict().items():
            setattr(manager, name, value)

        return manager

    def total_bedding_mass(self, pen: SimplePen) -> float:
        return pen.num_animals * self.bedding_mass_per_day  # kg/day

    def total_bedding_volume(self, pen: SimplePen) -> float:
        return self.total_bedding_mass(pen) / self.bedding.density  # m^3/day
