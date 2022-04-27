from RUFAS.routines.manure_management.manure_handlers.bedding.base_bedding import BaseBedding
from RUFAS.routines.manure_management.manure_handlers.bedding.bedding_enum import BeddingEnum
from RUFAS.routines.manure_management.manure_handlers.bedding.organic_bedding import OrganicBedding
from RUFAS.routines.manure_management.manure_handlers.bedding.sand_bedding import SandBedding


class BeddingFactory:
    @classmethod
    def get_instance(cls, bedding_type: str) -> BaseBedding:
        bedding_enum = BeddingEnum.get_enum(bedding_type)
        return cls.get_instance_from_enum(bedding_enum)

    @classmethod
    def get_instance_from_enum(cls, bedding_enum: BeddingEnum) -> BaseBedding:
        enum_to_class = {
            bedding_enum.ORGANIC: OrganicBedding(arg_mass=1.97),
            bedding_enum.SAND: SandBedding(arg_mass=25)
        }
        return enum_to_class[bedding_enum]
