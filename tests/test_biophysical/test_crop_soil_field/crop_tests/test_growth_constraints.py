from math import exp

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.field.crop.crop_data import CropData
from RUFAS.biophysical.field.crop.growth_constraints import GrowthConstraints

from tests.test_biophysical.test_crop_soil_field.sample_crop_configuration import SAMPLE_CROP_CONFIGURATION


@pytest.fixture
def mock_crop_data() -> CropData:
    return CropData(**SAMPLE_CROP_CONFIGURATION)


# ---- helper function tests ----
@pytest.mark.parametrize(
    ("act", "opt"),
    [
        (0, 0),  # all 1
        (1, 1),  # all 0
        (1, 0),  # both 0
        (0, 1),  # 0 nitrogen
        (-1, 1),  # negative nitrogen
        (1, -1),  # negative optimal
        (90.3, 130.1),  # arbitrary act < opt
        (78.1, 32.55),  # negative act > opt
        (200.3, 200.3),  # arbitrary act = opt
        (190.53, 190.54),  # almost equal
    ],
)
def test_calc_nutrient_stress(act: float, opt: float) -> None:
    """ensure that nitrogen scaling factor is correctly calculated by calc_nitrogen_stress_scaling_factor()."""
    if opt == 0:
        stress = 0
    else:
        phi = max(0.0, (200 * ((act / opt) - 0.5)))
        stress = 1 - (phi / (phi + exp(3.535 - (0.02597 * phi))))

    if stress > 1:
        stress = 1

    assert GrowthConstraints._determine_nutrient_stress(stored=act, optimal=opt) == stress


@pytest.mark.parametrize(
    ("uptake", "trans"),
    [
        (20, 40),  # arbitrary int
        (0, 0),  # zeroes
        (1, 1),  # ones
        (-1, -1),  # negative
        (26.8, 34.1),  # arbitrary floats
        (32.55, 18.2),  # trans < uptake
    ],
)
def test_calc_water_stress(uptake: float, trans: float) -> None:
    """ensure water stress is correctly calculated with calc_water_stress()"""
    if trans == 0:
        w_stress = 0
    else:
        w_stress = 1.0 - (uptake / trans)

    if w_stress < 0:
        w_stress = 0
    elif w_stress > 1:
        w_stress = 1

    assert GrowthConstraints._determine_water_stress(uptake, trans) == w_stress


@pytest.mark.parametrize(
    "air,mini,opt",
    [
        (1, 1, 1),  # all 1 (A)
        (1, 0, 0),  # air 1 (D)
        (0, 1, 0),  # min 1 (A)
        (0, 0, 1),  # opt 1 (A)
        (0, 0, 0),  # all 0 (A)
        (0.5, 0, 1),  # min < air < opt (B)
        (1, 0, 1),  # min < air = opt (B)
        (1.5, 0, 1),  # opt < air < 2*opt - min (C)
        (2, 0, 1),  # opt < air = 2*opt - min (C)
        (3, 0, 1),  # opt < air > 2*opt - min (D)
        (5.6, 12.2, 25.5),  # arbitrary (A)
        (15.8, 12.2, 25.5),  # arbitrary (B)
        (36.7, 12.2, 25.5),  # arbitrary (C)
        (39.9, 12.2, 25.5),  # arbitrary (D)
    ],
)
def test_calc_temperature_stress(air: float, mini: float, opt: float) -> None:
    """ensure temperature stress is correctly calculated with calc_temperature_stress()"""
    top = -0.1054 * ((opt - air) ** 2)
    dbl = (2 * opt) - mini

    expect = None
    if air <= mini:  # A
        expect = 1
    if mini < air <= opt:  # B
        expect = 1 - exp(top / ((air - mini) ** 2))
    if opt < air < dbl:  # C
        expect = 1 - exp(top / ((dbl - air) ** 2))
    if air >= dbl:  # D
        expect = 1

    assert GrowthConstraints._determine_temperature_stress(air_temp=air, min_temp=mini, optimal_temp=opt) == expect


@pytest.mark.parametrize(
    "w_stress,t_stress,n_stress,p_stress",
    [
        (1, 1, 1, 1),  # all 1
        (0.8, 0.7, 0.6, 0.5),  # water limited
        (0.8, 0.82, 0.6, 0.5),  # temperature limited
        (0.8, 0.7, 0.9, 0.5),  # nitrogen limited
        (0.8, 0.7, 0.6, 0.93),  # phosphorus limited
        (0, 0, 0, 0),  # no limits
    ],
)
def test_calc_growth_factor(w_stress: float, t_stress: float, n_stress: float, p_stress: float) -> None:
    limiting_factor = max(w_stress, t_stress, n_stress, p_stress)
    expect = 1 - limiting_factor
    assert (
        GrowthConstraints._determine_growth_factor(
            water_stress=w_stress,
            temperature_stress=t_stress,
            nitrogen_stress=n_stress,
            phosphorus_stress=p_stress,
        )
        == expect
    )


@pytest.mark.parametrize(
    "trans,temp,stressors,returned_stress,expected_stress",
    [
        (0, 0, False, 0.1, 0.0),  # all zero
        (18.8, 10.4, True, 0.3, 0.3),  # trans < uptake; temp < min
        (18.8, 19.7, False, 0.4, 0.0),  # trans < uptake; temp > min
        (18.8, 26.3, True, 0.4, 0.4),  # trans < uptake; temp > opt
        (27.1, 19.7, False, 0.5, 0.0),  # trans > uptake; temp > min
    ],
)
def test_constrain_growth(
    mocker: MockerFixture,
    mock_crop_data: CropData,
    trans: float,
    temp: float,
    stressors: bool,
    returned_stress: float,
    expected_stress: float,
) -> None:
    """integration test: check that the growth factor is properly determined"""
    # initialize with arbitrary crop values
    mock_crop_data.water_uptake = 22.33
    mock_crop_data.nitrogen = 38.7
    mock_crop_data.optimal_nitrogen = 77.1
    mock_crop_data.phosphorus = 12.9
    mock_crop_data.optimal_phosphorus = 31.2
    mock_crop_data.minimum_temperature = 12.8
    mock_crop_data.optimal_temperature = 24.0
    gc = GrowthConstraints(mock_crop_data)
    water_stress = mocker.patch.object(gc, "_determine_water_stress", return_value=returned_stress)
    temp_stress = mocker.patch.object(gc, "_determine_temperature_stress", return_value=returned_stress)
    nutrient_stress = mocker.patch.object(gc, "_determine_nutrient_stress", return_value=returned_stress)
    growth_factor = mocker.patch.object(gc, "_determine_growth_factor", return_value=0.55)

    gc.constrain_growth(trans, temp, stressors, stressors, stressors, stressors)

    if stressors:
        assert water_stress.call_count == 1
        assert temp_stress.call_count == 1
        assert nutrient_stress.call_count == 2
    else:
        assert water_stress.call_count == 0
        assert temp_stress.call_count == 0
        assert nutrient_stress.call_count == 0

    growth_factor.assert_called_once_with(*[expected_stress] * 4)
    assert gc.data.growth_factor == 0.55
