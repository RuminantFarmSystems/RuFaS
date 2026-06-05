from math import exp, log
from unittest.mock import MagicMock, PropertyMock, patch

import pytest
from pytest_mock import MockerFixture

from RUFAS.output_manager import OutputManager
from RUFAS.biophysical.field.crop.crop_data import CropData
from RUFAS.biophysical.field.crop.nitrogen_uptake import NitrogenUptake
from RUFAS.biophysical.field.soil.soil_data import SoilData

from tests.test_biophysical.test_crop_soil_field.sample_crop_configuration import SAMPLE_CROP_CONFIGURATION


@pytest.fixture
def mock_crop_data() -> CropData:
    return CropData(**SAMPLE_CROP_CONFIGURATION)


# --- static function tests ----
@pytest.mark.parametrize(
    "halfheat,heatfrac,emerge,half,near,mature,should_fail",
    [
        (0.5, 1.0, 0.8, 0.6, 0.3, 0.2, False),  # start
        (0.99, 1.0, 0.8, 0.6, 0.3, 0.2, False),  # half_heat close to mature heat
        (0.01, 1.0, 0.8, 0.6, 0.3, 0.2, False),  # small half_heat
        (0.5, 1.0, 0.8, 0.6, 0.20001, 0.2, False),  # near very close to mature
        (0.286, 0.54, 0.522, 0.4, 0.1, 0.08, False),  # arbitrary
        # Above tests are copied from old subroutine tests
        (0.8, 1, 0.9, 0.6, 0.3, 0.25, False),
        (0.8, 0.81, 0.9, 0.6, 0.3, 0.25, False),  # small difference in heat units
        (
            0.8,
            1,
            0.9,
            0.6,
            0.25000001,
            0.25,
            False,
        ),  # small difference in nfrac_near and nfrac_3
        (0.633, 0.691, 0.530, 0.101, 0.057, 0.013, False),  # arbitrary
        (0.5, 0.5, 0.530, 0.101, 0.057, 0.013, True),
    ],
)
def test_determine_nitrogen_shape_parameters(
    halfheat: float,
    heatfrac: float,
    emerge: float,
    half: float,
    near: float,
    mature: float,
    should_fail: bool,
    mocker: MockerFixture,
) -> None:
    """check that the shape parameters are correctly calculated by determine_nshapes() and that errors were raised
    correctly"""
    om = OutputManager()
    mock_add = mocker.patch.object(om, "add_error")
    if should_fail:
        try:
            NitrogenUptake.determine_nutrient_shape_parameters(halfheat, heatfrac, emerge, half, mature)
        except ValueError as e:
            assert str(e) == "half_mature_heat_fraction must not equal mature_heat_fraction"
            mock_add.assert_called_once()
    else:
        expected_near = mature + 0.00001
        observe = NitrogenUptake.determine_nutrient_shape_parameters(halfheat, heatfrac, emerge, half, mature)
        expect_2 = (
            NitrogenUptake._determine_shape_log(halfheat, half, mature, emerge)
            - NitrogenUptake._determine_shape_log(heatfrac, expected_near, mature, emerge)
        ) / (heatfrac - halfheat)
        expect_1 = NitrogenUptake._determine_shape_log(halfheat, half, mature, emerge) + (expect_2 * halfheat)
        assert observe == [expect_1, expect_2]


@pytest.mark.parametrize(
    "heatfrac,current,mature,emergence",
    [
        (1, 0.5, 0.25, 0.75),  # max_evapotranspiration heatfrac
        (0.8, 0.5, 0.25, 1),  # max_evapotranspiration mature nfrac
        (0.32, 0.5, 0.25, 0.75),  # arbitrary
    ],
)
def test_determine_shape_log(heatfrac: float, current: float, mature: float, emergence: float) -> None:
    """check that determine_shape_log() calculates correct output"""
    observe = NitrogenUptake._determine_shape_log(heatfrac, current, mature, emergence)
    bottom = 1 - ((current - mature) / (emergence - mature))
    inside = (heatfrac / bottom) - heatfrac
    expect = log(inside)
    assert observe == expect


@pytest.mark.parametrize(
    "heatfrac,current,mature,emergence",
    [
        (0, 0.5, 0.25, 0.75),  # no heatfrac
        (0.8, 0, 0.25, 0.75),  # mature nfrac = 0
        (0.8, 0.76, 0.25, 0.75),  # nfrac > emergence
        (0.8, 0.75, 0.25, 0.75),  # nfrac = emergence
        (0.8, 0.5, 0.25, 0.24),  # emergence < mature
        (0.8, 1.2, 0.25, 0.25),  # out of bounds
        (0.8, 1.2, -0.25, 0.25),  # out of bounds
        (0.6, 0.3, 0.31, 0.8),  # log(-y): nfrac < mature
        (0.6, 0.3, 0.3, 0.8),  # nfrac = mature
        (0.8, 0.3, 0.31, 0.8),  # log(-y)
        (1, 0.3, 0.31, 0.8),  # log(-y)
        # (1, 0.3, 0.29, 0.8),  # no error
    ],
)
def test_error_determine_shape_log(
    heatfrac: float, current: float, mature: float, emergence: float, mocker: MockerFixture
) -> None:
    """check that determine_shape_log() throws errors when appropriate"""
    om = OutputManager()
    mock_add = mocker.patch.object(om, "add_error")
    with pytest.raises(Exception):
        NitrogenUptake._determine_shape_log(heatfrac, current, mature, emergence)
    mock_add.assert_called_once()


@pytest.mark.parametrize(
    "heatfrac,emerge,mature,shape1,shape2",
    [
        (0.2, 0.8, 0.5, 0.1, 0.5),  # shape1 < shape2
        (0.2, 0.8, 0.5, 0.5, 0.1),  # shape1 > shape2
        (0.2, 0.8, 0.5, -0.5, 0.1),  # negative shape 1
        (0.2, 0.8, 0.5, 0.5, -0.1),  # negative shape 2
        (0.2, 0.8, 0.5, -0.5, -0.1),  # both negative
        (0.789, 0.587, 0.501, 0.138, 0.920),  # arbitrary
    ],
)
def test_determine_optimal_nitrogen_fraction(
    heatfrac: float, emerge: float, mature: float, shape1: float, shape2: float
) -> None:
    """Ensure that nitrogen fraction is correctly calculated by determine_optimal_nitrogen_fraction()."""
    observe = NitrogenUptake.determine_optimal_nutrient_fraction(heatfrac, emerge, mature, shape1, shape2)
    expect = (emerge - mature) * (1 - (heatfrac / (heatfrac + exp(shape1 - shape2 * heatfrac)))) + mature
    assert observe == expect


@pytest.mark.parametrize(
    "nitrates,expect",
    [
        (0, 1),  # A
        (13.2, 1),  # arbitrary A
        (100, 1),  # A edge
        (100.1, 1.5 - 5e-3 * 100.1),  # B
        (200, 1.5 - 5e-3 * 200),  # B
        (300, 1.5 - 5e-3 * 300),  # B
        (300.1, 0),  # C
        (450, 0),  # C
    ],
)
def test_determine_nitrate_factor(nitrates: float, expect: float) -> None:
    assert NitrogenUptake._determine_nitrate_factor(nitrates) == expect


@pytest.mark.parametrize(
    "heatfrac,expect",
    [
        (-1.0, 0.0),  # piece A
        (0.00, 0.0),
        (0.05, 0.0),
        (0.15, 0.0),
        (0.22, 6.67 * 0.22 - 1),  # piece B
        (0.30, 6.67 * 0.30 - 1),
        (0.43, 1.0),  # piece C
        (0.55, 1.0),
        (0.67, 3.75 - 5 * 0.67),  # piece D
        (0.75, 3.75 - 5 * 0.75),
        (0.76, 0.0),  # piece E
        (1.39, 0.0),
    ],
)
def test_determine_fixation_stage_factor(heatfrac: float, expect: float) -> None:
    assert NitrogenUptake._determine_fixation_stage_factor(heatfrac) == expect


@pytest.mark.parametrize(
    "demand,stage,water,nitrate,expect",
    [
        (0, 1, 1, 1, 0),  # no demand
        (1, 1, 1, 1, 1),  # all 1
        (1, 1, 0.2, 0.5, 0.2),  # water min
        (1, 1, 0.6, 0.5, 0.5),  # nitrate min
        (1, 0.5, 0.6, 0.5, 0.5 * 0.5),  # reduced stage
        (0.3, 0.5, 0.6, 0.5, 0.3 * 0.5 * 0.5),  # reduced demand
    ],
)
def test_determine_fixed_nitrogen(demand: float, stage: float, water: float, nitrate: float, expect: float) -> None:
    """check that nitrogen values are calculated as expected with determine_fixed_nitrogen()"""
    assert NitrogenUptake._determine_fixed_nitrogen(demand, stage, water, nitrate) == expect


@pytest.mark.parametrize(
    "demand,stage,water,nitrate",
    [
        (1, -1, 1, 1),  # neg stage
        (1, 1, -1, 1),  # neg water
        (1, 1, 1, -1),  # neg nitrate
        (1, 1.2, 1, 1),  # stage > 1
        (1, 1, 2, 1),  # water > 1
        (1, 1, 1, 100),  # nitrate > 1
    ],
)
def test_error_determine_fixed_nitrogen(
    demand: float, stage: float, water: float, nitrate: float, mocker: MockerFixture
) -> None:
    om = OutputManager()
    mock_add = mocker.patch.object(om, "add_error")
    with pytest.raises(ValueError):
        NitrogenUptake._determine_fixed_nitrogen(demand, stage, water, nitrate)
    mock_add.assert_called_once()


@pytest.mark.parametrize(
    "prev,new,fix",
    [
        (1, 1, 1),  # all 1
        (1, 1, 0),  # no fixation
        (1, 0, 1),  # no new nitrogen
        (0, 1, 1),  # no previous nitrogen
        (0, 0, 0),  # all 0
        (50.39, 10.55, 3.05),  # arbitrary
    ],
)
def test_determine_stored_nitrogen(prev: float, new: float, fix: float) -> None:
    """test the stored nitrogen is properly calculated by determine_stored_nitrogen()"""
    observe = NitrogenUptake.determine_stored_nutrient(new, prev, fix)
    assert observe == prev + new + fix


@pytest.mark.parametrize(
    "fixer,nitrates,water",
    [
        (True, 100, 0.5),  # fixer with nitrates
        (True, 0, 0.5),  # fixer without nitrates
        (False, 100, 0.5),  # non-fixer with nitrates
        (False, 0, 0.5),  # non-fixer without nitrates
    ],
)
def test_try_fixation(
    fixer: bool, nitrates: float, water: float, mocker: MockerFixture, mock_crop_data: CropData
) -> None:
    """check that try_fixation calls its sub-functions if fixation occurs"""
    patch_update_fixation_attributes = mocker.patch(
        "RUFAS.biophysical.field.crop.nitrogen_uptake.NitrogenUptake.update_fixation_attributes"
    )
    patch_fix_nitrogen = mocker.patch("RUFAS.biophysical.field.crop.nitrogen_uptake.NitrogenUptake.fix_nitrogen")
    mock_crop_data.is_nitrogen_fixer = fixer
    incorp = NitrogenUptake(mock_crop_data)
    incorp.try_fixation(nitrates, water)
    if fixer:
        patch_update_fixation_attributes.assert_called_once()
        patch_fix_nitrogen.assert_called_once()
    else:
        patch_update_fixation_attributes.assert_not_called()
        patch_fix_nitrogen.assert_not_called()
        assert incorp.fixed_nitrogen == 0


def test_update_fixation_attributes(mocker: MockerFixture, mock_crop_data: CropData) -> None:
    """Check that update_nitrate_attributes calls both its sub-functions."""
    patch_determine_nitrate_factor = mocker.patch(
        "RUFAS.biophysical.field.crop.nitrogen_uptake.NitrogenUptake._determine_nitrate_factor"
    )
    patch_determine_determine_fixation_stage_factor = mocker.patch(
        "RUFAS.biophysical.field.crop.nitrogen_uptake.NitrogenUptake._determine_fixation_stage_factor"
    )
    incorp = NitrogenUptake(mock_crop_data)

    incorp.update_fixation_attributes(100)

    patch_determine_nitrate_factor.assert_called_once()
    patch_determine_determine_fixation_stage_factor.assert_called_once()


@pytest.mark.parametrize(
    "uptake,demand,water,fixfact,nitrate",
    [
        (0, 10, 0.5, 0.25, 0.3),  # unmet demand, water > nitrate > fix
        (10, 10, 0.5, 0.25, 0.3),  # no unmet demand, water > nitrate > fix
        (5, 10, 0.2, 0.25, 0.3),  # unmet demand, water < fix < nitrate
        (5, 10, 0.2, 0.25, 0.22),  # unmet demand, water < nitrate < fix
        (73.4, 112.5, 0.83, 0.11, 0.44),  # arbitrary
    ],
)
def test_fix_nitrogen(
    uptake: float, demand: float, water: float, fixfact: float, nitrate: float, mock_crop_data: CropData
) -> None:
    """check that fixed nitrogen is properly calculated by fix_nitrogen()"""
    incorp = NitrogenUptake(
        mock_crop_data,
        potential_nutrient_uptake=demand,
        total_nutrient_uptake=uptake,
        fixation_stage_factor=fixfact,
        nitrate_factor=nitrate,
    )
    incorp.fix_nitrogen(water)
    if (demand - uptake) > 0:
        assert incorp.fixed_nitrogen == NitrogenUptake._determine_fixed_nitrogen(
            demand - uptake, fixfact, water, nitrate
        )
    else:
        assert incorp.fixed_nitrogen == 0


@pytest.mark.parametrize(
    "nitrates,depths,water_factor,gate",
    [
        ([0.5, 0.3, 0.2], [1, 2, 5], 0.692, True),
        ([0.5, 0.3, 0.2], [1, 2, 5], 0.692, False),
    ],
)
def test_incorporate_nitrogen(
    mock_crop_data: CropData, nitrates: list[float], depths: list[float], water_factor: float, gate: bool
) -> None:
    """Tests that nitrogen uptake and fixation is performed correctly."""
    # initialize object
    mock_crop_data.half_mature_heat_fraction = 0.54
    mock_crop_data.mature_heat_fraction = 0.99
    mock_crop_data.biomass = 122.8
    mock_crop_data.biomass_growth_max = 999
    mock_crop_data.emergence_nitrogen_fraction = 0.71
    mock_crop_data.half_mature_nitrogen_fraction = 0.68
    mock_crop_data.mature_nitrogen_fraction = 0.60
    with (
        patch(
            "RUFAS.biophysical.field.soil.soil_data.SoilData.soil_water_factor",
            new_callable=PropertyMock,
            return_value=water_factor,
        ),
        patch.object(CropData, "heat_fraction", new_callable=PropertyMock, return_value=0.38),
    ):
        soil = SoilData(field_size=1.3)
        del soil.soil_layers[3]  # delete 4th layer
        top_depths = [0] + depths[:2]
        soil.set_vectorized_layer_attribute("top_depth", top_depths)
        soil.set_vectorized_layer_attribute("bottom_depth", depths)
        soil.set_vectorized_layer_attribute("nitrate", nitrates)
        incorp = NitrogenUptake(mock_crop_data, previous_nutrient=0)

        # mock intermediate functions
        incorp.shift_nutrient_time = MagicMock(return_value=None)
        incorp.determine_nutrient_shape_parameters = MagicMock(return_value=[1.2, 0.8])
        incorp.determine_optimal_nutrient_fraction = MagicMock(return_value=0.75)
        if gate:
            incorp.determine_optimal_nutrient = MagicMock(return_value=-268)
        else:
            incorp.determine_optimal_nutrient = MagicMock(return_value=268)
        incorp.determine_potential_nutrient_uptake = MagicMock(return_value=123.1)
        incorp.uptake_nitrogen = MagicMock(return_value=None)
        incorp.access_layers = MagicMock(return_value=[5, 10, 15.3])
        incorp.try_fixation = MagicMock(return_value=None)
        NitrogenUptake.determine_stored_nutrient = MagicMock(return_value=99.3)

        # run method
        incorp.uptake(soil)

        # assertions
        incorp.shift_nutrient_time.assert_called_once()
        incorp.determine_nutrient_shape_parameters.assert_called_once_with(0.54, 0.99, 0.71, 0.68, 0.60)
        assert incorp.nutrient_shapes == [1.2, 0.8]
        incorp.determine_optimal_nutrient_fraction.assert_called_once_with(0.38, 0.71, 0.60, 1.2, 0.8)
        assert mock_crop_data.optimal_nitrogen_fraction == 0.75
        if gate:
            incorp.determine_optimal_nutrient.assert_called_once_with(0.75, 122.8)
            assert mock_crop_data.optimal_nitrogen == -268
            incorp.determine_potential_nutrient_uptake.assert_not_called()
            assert incorp.potential_nutrient_uptake == 0
        else:
            assert mock_crop_data.optimal_nitrogen == 268
            incorp.determine_potential_nutrient_uptake.assert_called_once_with(268, 0, 0.60, 999)
            assert incorp.potential_nutrient_uptake == 123.1
        incorp.try_fixation.assert_called_once_with(5 + 10 + 15.3, water_factor)
        NitrogenUptake.determine_stored_nutrient.assert_called_once()  # should called_once_with() w/attr mocked
        assert mock_crop_data.nitrogen == 99.3


def test_uptake(mocker: MockerFixture, mock_crop_data: CropData) -> None:
    """Check that uptake() correctly called functions and variables were updated as expected."""
    uptake = NitrogenUptake(mock_crop_data)
    soil = SoilData(field_size=10)
    mock_main_uptake = mocker.patch.object(uptake, "uptake_main_process")
    mock_determine_stored = mocker.patch.object(uptake, "determine_stored_nutrient", return_value=1)
    mock_try_fixation = mocker.patch.object(uptake, "try_fixation")
    uptake.uptake(soil)
    mock_main_uptake.assert_called_once()
    mock_determine_stored.assert_called_once()
    mock_try_fixation.assert_called_once()
    assert mock_crop_data.nitrogen == 1
