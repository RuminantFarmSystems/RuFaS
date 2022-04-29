from RUFAS.routines.manure_management.manure_handlers.bedding.base_bedding import BaseBedding


class SandBedding(BaseBedding):
    def __init__(self, arg_mass: float = 0, arg_density: float = 1500):
        super().__init__(arg_mass, arg_density)

    def __add__(self, other: BaseBedding) -> BaseBedding:
        b = super().__add__(other)
        return SandBedding(b.mass, b.density)
