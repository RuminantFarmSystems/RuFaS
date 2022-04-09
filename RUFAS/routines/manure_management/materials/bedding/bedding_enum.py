from __future__ import annotations

from enum import auto

from RUFAS.routines.manure_management.helpers.enum_helpers import ExtendedEnum


class BeddingEnum(ExtendedEnum):
    ORGANIC = auto()
    SAND = auto()

    DEFAULT = ORGANIC


if __name__ == '__main__':
    for b in BeddingEnum:
        print(b.name, b.value)
    print(BeddingEnum.get_enum('organic'))
    print(BeddingEnum.get_enum('sand'))
    print(BeddingEnum.get_enum('dummy'))
