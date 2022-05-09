from typing import Type

from pytest import approx, fixture

from RUFAS.routines.manure_management.treatments.constants import TreatmentConstants


@fixture
def constants() -> Type[TreatmentConstants]:
    return TreatmentConstants


# TODO: Use proper names for the constants

def test_constant_Bo_value(constants) -> None:
    assert constants.Bo == approx(0.24)


def test_constant_MCF_methane_conversion_factor_value(constants) -> None:
    assert constants.MCF == approx(0.01)


def test_constant_MS_value(constants) -> None:
    assert constants.MS == approx(0.9)


def test_constant_m3_value(constants) -> None:
    assert constants.m3 == approx(0.662)


def test_constant_TS_loss_perc_value(constants) -> None:
    assert constants.TS_loss_perc == approx(0.02)


def test_constant_VS_loss_perc_value(constants) -> None:
    assert constants.VS_loss_perc == approx(0.85)


def test_constant_density_value(constants) -> None:
    assert constants.density == approx(994.0)
