from unittest.mock import PropertyMock, patch

import pytest

from RUFAS.routines.field.crop.crop_data import CropData
from RUFAS.routines.field.crop.root_development import RootDevelopment

from tests.soil_crop_tests.sample_crop_configuration import SAMPLE_CROP_CONFIGURATION


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
    "maxd, expected_root_depth, heatfrac, is_perennial",
    [
        (1, 1.0, 0.5, True),
        (1, 1.0, 0.3, True),
        (1, 1.0, 0, True),
        (1, 1.0, 1, True),
        (1, 1.0, 1.2, True),
        (0, 0.0, 0.5, True),
        (100, 100.0, 0.5, True),
        (1, 1.0, 0.5, False),
        (0.75, 0.5625, 0.3, False),
        (0.0, 0.0, 0, False),
        (1, 1.0, 1, False),
        (1, 1.0, 1.2, False),
        (0, 0.0, 0.5, False),
        (100, 100.0, 0.5, False),
    ],
)
def test_develop_roots(
    mock_crop_data: CropData, maxd: int, expected_root_depth: float, heatfrac: float, is_perennial: bool
) -> None:
    """Integration test for main root development function develop_roots()."""
    with patch.object(CropData, "heat_fraction", new_callable=PropertyMock, return_value=heatfrac):
        mock_crop_data.max_root_depth = maxd
        mock_crop_data.is_perennial = is_perennial
        rd = RootDevelopment(mock_crop_data)

        rd.develop_roots()

        assert mock_crop_data.root_fraction == RootDevelopment._determine_root_fraction(heatfrac)
        assert mock_crop_data.root_depth == expected_root_depth
