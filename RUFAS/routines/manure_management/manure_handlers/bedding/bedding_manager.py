from __future__ import annotations

from dataclasses import dataclass
from typing import NamedTuple

from RUFAS.routines.manure_management.manure_handlers.bedding.base_bedding import BaseBedding
from RUFAS.routines.manure_management.manure_handlers.bedding.bedding_enum import BeddingEnum
from RUFAS.routines.manure_management.manure_handlers.bedding.bedding_factory import BeddingFactory


class BeddingManager:
    def __init__(self, bedding_type: str):
        self.bedding_enum = BeddingEnum.get_enum(bedding_type)
        self.bedding = BeddingFactory.get_instance(bedding_type)
        self.bedding_added: float = 0.0
        self.bedding_dry_matter: float = 0.0
        self.bedding_washed_percent: float = 0.0
        self.bedding_mass_per_day: float = 0.0

    @property
    def bedding_washed(self) -> float:
        return self.bedding_washed_percent * self.bedding_added

    @classmethod
    def get_instance(cls, bedding_type: str) -> BeddingManager:
        BeddingParams = NamedTuple('BeddingParams',
                                   [('bedding_added', float),
                                    ('bedding_dry_matter', float),
                                    ('bedding_washed_percent', float),
                                    ('bedding_mass_per_day', float)])
        enum_to_params = {
            BeddingEnum.ORGANIC: BeddingParams(1.97, 0.9, 1.0, 1.97),
            BeddingEnum.SAND: BeddingParams(25, 0.9, 1.0, 22.23)
        }

        mngr = cls(bedding_type)
        params = enum_to_params[mngr.bedding_enum]
        for name, value in params._asdict().items():
            setattr(mngr, name, value)

        return mngr
