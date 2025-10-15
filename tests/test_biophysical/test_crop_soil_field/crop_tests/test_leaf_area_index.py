from math import exp, log, sqrt
from unittest.mock import PropertyMock, patch

import pytest
from pytest_mock import MockerFixture

from RUFAS.output_manager import OutputManager
from RUFAS.biophysical.field.crop.crop_data import CropData
from RUFAS.biophysical.field.crop.leaf_area_index import LeafAreaIndex

from tests.test_biophysical.test_crop_soil_field.sample_crop_configuration import SAMPLE_CROP_CONFIGURATION


@pytest.fixture
def mock_crop_data() -> CropData:
    return CropData(**SAMPLE_CROP_CONFIGURATION)


@pytest.mark.parametrize(
    "heatfrac,s1,s2",
    [
        (0.5, 1, 1),  # starting point
        (0.0, 1, 1),  # no heatfrac
        (1.0, 1, 1),  # full heatfrac
        (0.5, 0.33, 1),  # reduced s1
        (0.5, 1, 0.33),  # reduced s2
        (0.5, 0.33, 0.33),  # reduced s1 and s2
        (0.239, 1.2, -2.33),  # arbitrary
        (-1, 1, 1),
    ],
)
def test_determine_optimal_leaf_area_fraction(heatfrac: float, s1: float, s2: float) -> None:
    """ensure that optimal leaf area fraction is properly calculated by calc_optimal_leaf_area_fraction()"""
    x = heatfrac + exp(s1 - s2 * heatfrac)
    if heatfrac / x < 0:
        expect = 0
    else:
        expect = heatfrac / x
    assert LeafAreaIndex._determine_optimal_leaf_area_fraction(heatfrac, s1, s2) == expect


@pytest.mark.parametrize(
    "heatfrac,areafrac",
    [
        (0.5, 0.5),  # heatfrac = areafrac
        (0.3, 0.5),  # heatfrac < areafrac
        (0.4, 0.2),  # heatfrac > areafrac
        (1, 0.5),  # heatfrac = 1
        (1.3, 0.5),  # heatfrac > 1
        (0.5, 1 - 1e-9),  # areafrac approx 1
        (0.5, 1e-9),  # areafrac approx 0
        (1e-9, 0.5),  # heatfrac approx 0
        (-2, -1),  # both negative
        (-1, -2),  # both negative
        (0.439, 0.611),  # arbitrary
    ],
)
def test_calc_shape_log(heatfrac: float, areafrac: float) -> None:
    """ensure that log terms are calculated correctly"""
    observe = LeafAreaIndex._calc_shape_log(heatfrac, areafrac)
    x = (heatfrac / areafrac) - heatfrac
    assert log(x) == observe


@pytest.mark.parametrize(
    "heatfrac,areafrac",
    [
        (0, 1),  # heatfrac = 0 -- math domain
        (0, 0.5),  # heatfrac = 0 -- math domain
        (1, 0),  # areafrac = 0 -- division by zero
        (0.5, 0),  # areafrac = 0 -- division by zero
        (0.5, 1),  # areafrac = 1 -- math domain
        (-1, 0.5),  # negative heatfrac -- math domain
        (0.5, -1),  # negative areafrac -- math domain
    ],
)
def test_error_calc_shape_log(heatfrac: float, areafrac: float) -> None:
    """ensure that the errors are thrown for inappropriate input to calc_shape_log()"""
    with pytest.raises(Exception):
        LeafAreaIndex._calc_shape_log(heatfrac, areafrac)


@pytest.mark.parametrize(
    "heatfrac1,heatfrac2,areafrac1,areafrac2",
    [
        (0.3, 0.6, 0.2, 0.4),  # start
        (0.6, 0.3, 0.2, 0.4),  # heatfrac1 > heatfrac2
        (0.3, 0.6, 0.4, 0.2),  # areafrac1 > areafrac2
        (0.3, 0.6, 0.2, 0.2),  # areafrac1 = areafrac2
        (1, 0.6, 0.2, 0.4),  # heatfrac1 = 1
        (0.3, 1, 0.2, 0.4),  # heatfrac2 = 1
        (1.3, 0.6, 0.2, 0.4),  # heatfrac1 > 1
        (1, 1 - 1e-9, 0.2, 0.4),  # heatfrac1 approx heatfrac2
        (0.135, 0.842, 0.09, 0.321),  # arbitrary
    ],
)
def test_determine_lai_shapes(heatfrac1: float, heatfrac2: float, areafrac1: float, areafrac2: float) -> None:
    x = LeafAreaIndex._calc_shape_log(heatfrac1, areafrac1)
    y = LeafAreaIndex._calc_shape_log(heatfrac2, areafrac2)
    s2 = (x - y) / (heatfrac2 - heatfrac1)
    s1 = x + s2 * heatfrac1
    assert LeafAreaIndex._determine_lai_shapes(heatfrac1, heatfrac2, areafrac1, areafrac2) == [s1, s2]


@pytest.mark.parametrize(
    "heatfrac1,heatfrac2,areafrac1,areafrac2",
    [
        # shape log errors
        (0, 0.3, 0.2, 0.4),  # heatfrac1 = 0 -- math domain
        (0.5, 0, 0.2, 0.4),  # heatfrac2 = 0 -- math domain
        (0.5, 0.3, 0, 0.4),  # areafrac1 = 0 -- division by zero
        (0.5, 0.3, 0.2, 0),  # areafrac2 = 0 -- division by zero
        (0.5, 0.3, 1, 0.4),  # areafrac1 = 0 -- math domain
        (0.5, 0.3, 0.2, 1),  # areafrac2 = 0 -- math domain
        (-1, 0.3, 0.2, 0.4),  # heatfrac1 < 0 -- math domain
        (0.5, -1, 0.2, 0.4),  # heatfrac2 < 0 -- math domain
        (0.5, 0.3, -1, 0.4),  # areafrac1 < 0 -- math domain
        (0.5, 0.3, 0.2, -1),  # areafrac2 < 0 -- math domain
        (0.3, 0.3, 0.2, 0.4),  # heatfrac1 = heatfrac2 -- division by zero
    ],
)
def test_error_determine_lai_shape(
    heatfrac1: float, heatfrac2: float, areafrac1: float, areafrac2: float, mocker: MockerFixture
) -> None:
    """check that invalid input to test_error_calc_shape_parameters throws errors"""
    om = OutputManager()
    mock_add = mocker.patch.object(om, "add_error")
    with pytest.raises(ValueError):
        LeafAreaIndex._determine_lai_shapes(heatfrac1, heatfrac2, areafrac1, areafrac2)
    mock_add.assert_called_once()


@pytest.mark.parametrize(
    "heatfrac,senheatfrac,optareafrac",
    [
        (0.6, 0.5, 0.9),
        (0.1, 0.05, 0.7),
        (0.4, 0.3, 0.01),
        (1, 0.8, 0.8),  # heatfrac = 1
    ],
)
def test_determine_senescent_leaf_area_index(heatfrac: float, senheatfrac: float, optareafrac: float) -> None:
    """
    heatfrac is fr_PHU
    senheatfrac is fr_PHU,sen
    optareafrac is LAI_mx
    """
    top = 1 - heatfrac
    bottom = 1 - senheatfrac
    expect = optareafrac * (top / bottom)
    assert LeafAreaIndex._determine_senescent_leaf_area_index(heatfrac, senheatfrac, optareafrac) == expect


@pytest.mark.parametrize("heatfrac,senheatfrac,optareafrac", [(1.1, 1, 0.9), (1.1, 1.9, 0.9)])
def test_error_determine_senescent_leaf_area_index(heatfrac: float, senheatfrac: float, optareafrac: float) -> None:
    with pytest.raises(Exception) as e:
        LeafAreaIndex._determine_senescent_leaf_area_index(heatfrac, senheatfrac, optareafrac)
    assert "Senescent heat fraction must be less than 1" in str(e.value)


@pytest.mark.parametrize(
    "frac,prev_frac,max_lai,prev_lai",
    [
        (1, 1 / 3, 3, 1),  # start (prevfrac = prev_lai/max_lai)
        (1, 1 / 3, 3, 2.5),  # increased prev_lai, same prev_frac
        (0.5, 1 / 3, 3, 1),  # reduced frac
        (0, 1 / 3, 3, 1),  # frac = 0
        (1, 1 / 3, 3, 3),  # prev_lai = lai
        (1, 1, 3, 3),  # prev_lai = lai, pref_frac = current frac
        (1.2, 0.657, 3, 2.5),  # arbitrary
    ],
)
def test_determine_max_leaf_area_change(frac: float, prev_frac: float, max_lai: float, prev_lai: float) -> None:
    scaled_diff = (frac - prev_frac) * max_lai
    expo = 1 - exp(5 * (prev_lai - max_lai))
    assert LeafAreaIndex._determine_max_leaf_area_change(frac, prev_frac, max_lai, prev_lai) == scaled_diff * expo


@pytest.mark.parametrize("max_can_height, opt_leaf_area_frac", [(0, 0), (1, 1), (1.3, 0.4), (2.4, 0.9)])
def test_determine_canopy_height(max_can_height: float, opt_leaf_area_frac: float) -> None:
    sqrt_opt = sqrt(opt_leaf_area_frac)
    product = max_can_height * sqrt_opt
    expect = min(max_can_height, product)
    assert expect == LeafAreaIndex.determine_canopy_height(max_can_height, opt_leaf_area_frac)


@pytest.mark.parametrize(
    "max_can_height, opt_leaf_area_frac",
    [
        (-0.1, 0),  # Negative max canopy height
        (1, 1.5),  # Optimal leaf frac > 1
        (1, -0.3),  # Optimal leaf frac negative
        (-0.5, 1.3),  # Negative max canopy height and optimal leaf height > 1
    ],
)
def test_error_determine_canopy_height(max_can_height: float, opt_leaf_area_frac: float) -> None:
    with pytest.raises(ValueError):
        LeafAreaIndex.determine_canopy_height(max_can_height, opt_leaf_area_frac)


@pytest.mark.parametrize(
    "heatfrac, previous_leaf_area_index, previous_optimal_leaf_area_fraction",
    [
        (0, 0.1, 0.01),
        (0.2, 0.1, 0.01),
        (0.95, 0.1, 0.01),
        (1.2, 0.1, 0.01),
        (-1, 0.1, 0.01),
        (0.2, None, 0.01),
        (0.2, 0.1, None),
    ],
)
def test_grow_canopy(
    mock_crop_data: CropData,
    heatfrac: float,
    previous_leaf_area_index: int,
    previous_optimal_leaf_area_fraction: int,
) -> None:
    """Integration test for leaf area processes via grow_canopy()."""
    # observe
    mock_crop_data.leaf_area_index = 0.7
    mock_crop_data.max_canopy_height = 2.5
    mock_crop_data.growth_factor = 0.95
    mock_crop_data.max_leaf_area_index = 3.0
    mock_crop_data.senescent_heat_fraction = 0.9
    mock_crop_data.first_heat_fraction_point = 0.2
    mock_crop_data.second_heat_fraction_point = 0.33
    mock_crop_data.first_leaf_fraction_point = 0.05
    mock_crop_data.second_leaf_fraction_point = 0.95
    mock_crop_data.is_perennial = False
    lai = LeafAreaIndex(
        mock_crop_data,
        previous_leaf_area_index=previous_leaf_area_index,
        previous_optimal_leaf_area_fraction=previous_optimal_leaf_area_fraction,
    )

    with patch.object(CropData, "heat_fraction", new_callable=PropertyMock, return_value=heatfrac):
        lai.grow_canopy()
        # expect
        shapes = LeafAreaIndex._determine_lai_shapes(0.2, 0.33, 0.05, 0.95)
        assert lai.lai_shapes == shapes
        optimal_lai = LeafAreaIndex._determine_optimal_leaf_area_fraction(heatfrac, shapes[0], shapes[1])
        assert lai.optimal_leaf_area_fraction == optimal_lai
        assert lai.canopy_height == LeafAreaIndex.determine_canopy_height(
            mock_crop_data.max_canopy_height, lai.optimal_leaf_area_fraction
        )
        if heatfrac <= 0.9:  # normal growth
            assert mock_crop_data.is_in_senescence is False
            if previous_leaf_area_index is None and previous_optimal_leaf_area_fraction is None:
                max_change = LeafAreaIndex._determine_max_leaf_area_change(optimal_lai, 0, 3.0, 0)
            elif previous_leaf_area_index is None:
                max_change = LeafAreaIndex._determine_max_leaf_area_change(optimal_lai, 0.01, 3.0, 0)
            elif previous_optimal_leaf_area_fraction is None:
                max_change = LeafAreaIndex._determine_max_leaf_area_change(optimal_lai, 0, 3.0, 0.1)
            else:
                max_change = LeafAreaIndex._determine_max_leaf_area_change(optimal_lai, 0.01, 3.0, 0.1)
            assert lai.optimal_leaf_area_change == max_change
            added = max_change * sqrt(0.95)
            if max_change < added:  # when heatfrac = 0, no growth occurs
                added = max_change
            assert lai.leaf_area_added == added
            if previous_leaf_area_index is None:
                assert mock_crop_data.leaf_area_index == added
            else:
                assert mock_crop_data.leaf_area_index == 0.1 + added
            assert lai.previous_leaf_area_index == mock_crop_data.leaf_area_index
            assert lai.previous_optimal_leaf_area_fraction == optimal_lai
        else:  # senescence
            assert mock_crop_data.is_in_senescence is True
            assert mock_crop_data.leaf_area_index == LeafAreaIndex._determine_senescent_leaf_area_index(
                heatfrac, 0.9, mock_crop_data.max_leaf_area_index
            )
