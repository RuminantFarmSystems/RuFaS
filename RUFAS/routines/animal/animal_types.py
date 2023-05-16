from enum import Enum


class AnimalType(Enum):
    """The different types/subtypes of animals on a farm."""

    CALF = 'Calf'
    HEIFER_I = 'HeiferI'
    HEIFER_II = 'HeiferII'
    HEIFER_III = 'HeiferIII'
    DRY_COW = 'DryCow'
    LAC_COW = 'LacCow'


if __name__ == '__main__':
    # print all member names
    t = AnimalType.CALF
    print(f'AnimalType.CALF: {t}')
