from RUFAS.routines.manure.enums.ManureCoverEnum import ManureCoverEnum


def test_manure_cover_enum() -> None:
    """
    Unit test for the ManureCoverEnum class in file ManureCoverEnum.py.
    """

    # Assert
    assert ManureCoverEnum.COVER.value == "cover"
    assert ManureCoverEnum.CRUST.value == "crust"
    assert ManureCoverEnum.NO_COVER.value == "no cover"
    assert ManureCoverEnum.NOT_APPLICABLE.value == "N/A"

    assert ManureCoverEnum.COVER == ManureCoverEnum("cover")
    assert ManureCoverEnum.CRUST == ManureCoverEnum("crust")
    assert ManureCoverEnum.NO_COVER == ManureCoverEnum("no cover")
    assert ManureCoverEnum.NOT_APPLICABLE == ManureCoverEnum("N/A")
