from RUFAS.routines.manure_management.manure_handlers.bedding.base_bedding import BaseBedding


# 3 subtypes: they have different mass usage per animal per day
# recycled manure fibers (solids) DEFAULT
# sawdust
# straw

class OrganicBedding(BaseBedding):
    def __init__(self, arg_mass: float = 0, arg_density: float = 250):
        super().__init__(arg_mass, arg_density)

    def __add__(self, other: BaseBedding) -> BaseBedding:
        b = super().__add__(other)
        return OrganicBedding(b.mass, b.density)
