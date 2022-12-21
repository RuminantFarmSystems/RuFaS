import pytest

from RUFAS.routines.manure.default_enum.default_enum import DefaultEnum


class DummyDefaultEnumWithDefault(DefaultEnum):
    SUCCESS = 1
    FAILED = 2
    DEFAULT = SUCCESS


class DummyDefaultEnumNoDefault(DefaultEnum):
    SUCCESS = 1
    FAILED = 2


@pytest.mark.parametrize(
        "enum_type, expected_default",
        [(DummyDefaultEnumWithDefault, DummyDefaultEnumWithDefault.SUCCESS),
         (DummyDefaultEnumNoDefault, DummyDefaultEnumNoDefault.SUCCESS),
         ])
def test_get_default_type(enum_type: DefaultEnum, expected_default: DefaultEnum) -> None:
    """Unit test for function get_default_type() in file default_enum.py"""

    assert enum_type.get_default_type() is expected_default


@pytest.mark.parametrize(
        "enum_type, lookup_member, expected_type",
        [(DummyDefaultEnumWithDefault, 'success', DummyDefaultEnumWithDefault.SUCCESS),
         (DummyDefaultEnumWithDefault, 'failed', DummyDefaultEnumWithDefault.FAILED),
         (DummyDefaultEnumWithDefault, 'dummy', DummyDefaultEnumWithDefault.DEFAULT),
         (DummyDefaultEnumNoDefault, 'success', DummyDefaultEnumNoDefault.SUCCESS),
         (DummyDefaultEnumNoDefault, 'failed', DummyDefaultEnumNoDefault.FAILED),
         (DummyDefaultEnumNoDefault, 'dummy', DummyDefaultEnumNoDefault.SUCCESS),
         ])
def test_get_type(enum_type: DefaultEnum, lookup_member: str, expected_type: DefaultEnum) -> None:
    """Unit test for function get_type() in file default_enum.py"""

    assert enum_type.get_type(lookup_member) is expected_type


class DummyDefaultEnumWithNoMembers(DefaultEnum):
    pass


def test_get_type_no_members() -> None:
    """Unit test for function get_type() in file default_enum.py"""

    with pytest.raises(IndexError):
        DummyDefaultEnumWithNoMembers.get_type('dummy')
