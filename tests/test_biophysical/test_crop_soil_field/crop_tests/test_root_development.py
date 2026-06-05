from unittest.mock import PropertyMock

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.field.crop.crop_data import CropData
from RUFAS.biophysical.field.crop.root_development import RootDevelopment
from RUFAS.rufas_time import RufasTime

from tests.test_biophysical.test_crop_soil_field.sample_crop_configuration import SAMPLE_CROP_CONFIGURATION


@pytest.fixture
def mock_crop_data() -> CropData:
    return CropData(**SAMPLE_CROP_CONFIGURATION)


# ---- Test Static Functions ----
@pytest.mark.parametrize(
    "heatfrac,expect",
    [
        (-1, 0.4),
        (0, 0.4),
        (0.5, 0.4 - (0.2 * 0.5)),
        (1, 0.4 - (0.2 * 1)),
        (1.2, 0.4 - (0.2 * 1.2)),
        (2, 0),
        (2.1, 0),
    ],
)
def test_determine_root_fraction(heatfrac: float, expect: float) -> None:
    """Check that root fraction is properly calculated by determine_root_fraction()."""
    assert RootDevelopment._determine_root_fraction(heatfrac) == expect


@pytest.mark.parametrize(
    "maxd,heatfrac",
    [
        (1, 0.5),
        (1, 0.3),
        (1, 0),
        (1, 1),
        (1, 1.2),
        (0, 0.5),
        (100, 0.5),
    ],
)
def test_determine_root_depth(maxd: int, heatfrac: float) -> None:
    """Check that root depths are properly calculated by determine_root_depths()."""
    if heatfrac > 0.4:
        expect = maxd
    else:
        expect = 2.5 * heatfrac * maxd
    assert RootDevelopment._determine_root_depth(maxd, heatfrac) == expect


# ---- Test Class Methods ----


@pytest.mark.parametrize(
    "maxd, expected_root_depth, heatfrac, is_perennial, is_planting_year",
    [
        (1, 1.0, 0.5, True, True),
        (1, 0.75, 0.3, True, True),
        (1, 0.0, 0, True, True),
        (1, 1.0, 1, True, True),
        (1, 1.0, 1.2, True, True),
        (0, 0.0, 0.5, True, True),
        (100, 100.0, 0.5, True, True),
        (1, 1.0, 0.5, False, True),
        (0.75, 0.5625, 0.3, False, True),
        (0.0, 0.0, 0, False, True),
        (1, 1.0, 1, False, True),
        (1, 1.0, 1.2, False, True),
        (0, 0.0, 0.5, False, True),
        (100, 100.0, 0.5, False, True),
        (1, 1.0, 0.5, True, False),
        (1, 1.0, 0.3, True, False),
        (1, 1.0, 0, True, False),
        (1, 1.0, 1, True, False),
        (1, 1.0, 1.2, True, False),
        (0, 0.0, 0.5, True, False),
        (100, 100.0, 0.5, True, False),
        (1, 1.0, 0.5, False, False),
        (0.75, 0.5625, 0.3, False, False),
        (0.0, 0.0, 0, False, False),
        (1, 1.0, 1, False, False),
        (1, 1.0, 1.2, False, False),
        (0, 0.0, 0.5, False, False),
        (100, 100.0, 0.5, False, False),
    ],
)
def test_develop_roots(
    mock_crop_data: CropData,
    maxd: int,
    expected_root_depth: float,
    heatfrac: float,
    is_perennial: bool,
    is_planting_year: bool,
    mocker: MockerFixture,
) -> None:
    """Integration test for main root development function develop_roots()."""
    mock_crop_data.planting_year = 2018
    mock_crop_data.max_root_depth = maxd
    mock_crop_data.is_perennial = is_perennial
    mocker.patch.object(CropData, "heat_fraction", new_callable=PropertyMock, return_value=heatfrac)

    mocker.patch("RUFAS.rufas_time.RufasTime.__init__", return_value=None)
    mock_time = RufasTime()
    current_calendar_year = 2018 if is_planting_year else 2020
    mocker.patch.object(
        RufasTime, "current_calendar_year", new_callable=PropertyMock, return_value=current_calendar_year
    )
    rd = RootDevelopment(mock_crop_data)

    rd.develop_roots(mock_time)

    assert mock_crop_data.root_fraction == RootDevelopment._determine_root_fraction(heatfrac)
    assert mock_crop_data.root_depth == expected_root_depth
