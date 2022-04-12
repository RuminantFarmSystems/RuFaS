from RUFAS.routines.manure_management.manure_handlers.bedding.base_bedding import BaseBedding


class OrganicBedding(BaseBedding):
    def __init__(self, arg_mass: float = 0, arg_density: float = 250):
        super().__init__(arg_mass, arg_density)

    def __add__(self, other: BaseBedding) -> BaseBedding:
        b = super().__add__(other)
        return OrganicBedding(b.mass, b.density)


if __name__ == '__main__':
    o = OrganicBedding(arg_mass=500)
    print(o)

    m = OrganicBedding(arg_mass=1000)
    print(m)

    o += m
    print(o)
