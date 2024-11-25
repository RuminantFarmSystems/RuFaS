from RUFAS.data_structures.manure_types import ManureType


def test_enum_ManureType() -> None:
    """
    Unit test for ManureType enum in the file manure_types.py.

    This test verifies that each member of the ManureType enum can be instantiated and that the
    enum members are equal to the expected values.

    """
    # Assert
    assert ManureType.LIQUID == ManureType("liquid")
    assert ManureType.SOLID == ManureType("solid")
