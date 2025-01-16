from math import exp, log
from unittest.mock import MagicMock, PropertyMock, patch

import pytest
from pytest_mock import MockerFixture

from RUFAS.output_manager import OutputManager
from RUFAS.routines.field.crop.crop_data import CropData
from RUFAS.routines.field.crop.nitrogen_incorporation import NitrogenIncorporation
from RUFAS.routines.field.soil.soil_data import SoilData


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
    assert NitrogenIncorporation._determine_nitrate_factor(nitrates) == expect


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
    assert NitrogenIncorporation._determine_fixation_stage_factor(heatfrac) == expect


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
    assert NitrogenIncorporation._determine_fixed_nitrogen(demand, stage, water, nitrate) == expect


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
        NitrogenIncorporation._determine_fixed_nitrogen(demand, stage, water, nitrate)
    mock_add.assert_called_once()


@pytest.mark.parametrize(
    "old,new",
    [
        (None, 1),  # no start
        (0, 1),  # start = 0
        (1, 2),  # start = 0
        (2, 1),  # start > new
        (133.26, 149.4),  # arbitrary
    ],
)
def test_shift_nitrogen_time(old: float, new: float) -> None:
    data = CropData(nitrogen=new)
    incorp = NitrogenIncorporation(data, previous_nitrogen=old)
    incorp.shift_nitrogen_time()
    assert incorp.previous_nitrogen == new


@pytest.mark.parametrize(
    "fixer,nitrates,water",
    [
        (True, 100, 0.5),  # fixer with nitrates
        (True, 0, 0.5),  # fixer without nitrates
        (False, 100, 0.5),  # non-fixer with nitrates
        (False, 0, 0.5),  # non-fixer without nitrates
    ],
)
def test_try_fixation(fixer: bool, nitrates: float, water: float, mocker: MockerFixture) -> None:
    """check that try_fixation calls its sub-functions if fixation occurs"""
    patch_update_fixation_attributes = mocker.patch(
        "RUFAS.routines.field.crop.nitrogen_incorporation.NitrogenIncorporation.update_fixation_attributes"
    )
    patch_fix_nitrogen = mocker.patch(
        "RUFAS.routines.field.crop.nitrogen_incorporation.NitrogenIncorporation.fix_nitrogen"
    )
    data = CropData(is_nitrogen_fixer=fixer)
    incorp = NitrogenIncorporation(data)
    incorp.try_fixation(nitrates, water)
    if fixer:
        patch_update_fixation_attributes.assert_called_once()
        patch_fix_nitrogen.assert_called_once()
    else:
        patch_update_fixation_attributes.assert_not_called()
        patch_fix_nitrogen.assert_not_called()
        assert incorp.fixed_nitrogen == 0


def test_update_fixation_attributes(mocker: MockerFixture) -> None:
    """ "check that update_nitrate_attributes calls both its sub-functions"""
    patch_determine_nitrate_factor = mocker.patch(
        "RUFAS.routines.field.crop.nitrogen_incorporation.NitrogenIncorporation._determine_nitrate_factor"
    )
    patch_determine_determine_fixation_stage_factor = mocker.patch(
        "RUFAS.routines.field.crop.nitrogen_incorporation.NitrogenIncorporation._determine_fixation_stage_factor"
    )
    incorp = NitrogenIncorporation()
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
def test_fix_nitrogen(uptake: float, demand: float, water: float, fixfact: float, nitrate: float) -> None:
    """check that fixed nitrogen is properly calculated by fix_nitrogen()"""
    data = CropData()
    incorp = NitrogenIncorporation(
        data,
        potential_nitrogen_uptake=demand,
        total_nitrogen_uptake=uptake,
        fixation_stage_factor=fixfact,
        nitrate_factor=nitrate,
    )
    incorp.fix_nitrogen(water)
    if (demand - uptake) > 0:
        assert incorp.fixed_nitrogen == NitrogenIncorporation._determine_fixed_nitrogen(
            demand - uptake, fixfact, water, nitrate
        )
    else:
        assert incorp.fixed_nitrogen == 0


@pytest.mark.parametrize("depths,nitrates", [([0.5, 1, 10, 20], [0.5, 0.8, 5, 10])])
def test_uptake_nitrogen(depths: list[float], nitrates: list[float]) -> None:
    # initialize crop and run method
    data = CropData(root_depth=35.0)
    incorp = NitrogenIncorporation(data, potential_nitrogen_uptake=17.5, nitrogen_distro_param=0.32)

    # Mock functions
    incorp.find_deepest_accessible_soil_layer = MagicMock(return_value=None)
    incorp.access_layers = MagicMock(return_value=[1, 2, 3])
    incorp.determine_layer_nutrient_uptake_potential = MagicMock(return_value=[3.25, 6.33, 7.10])
    incorp.determine_layer_nutrient_demands = MagicMock(return_value=[12, 15, 17])
    incorp.determine_layer_nutrient_uptake = MagicMock(return_value=[8.9, 9.9, 13.12])
    incorp.determine_layer_extracted_resource = MagicMock(return_value=[5.0, 4.0, 2.0])
    incorp.extend_nutrient_uptakes_to_full_profile = MagicMock()
    incorp.extract_nutrient_from_soil_layers = MagicMock()
    incorp.tally_total_nutrient_uptake = MagicMock()

    # run function
    incorp.uptake_nitrogen(nitrates, depths)

    # check assertions
    incorp.find_deepest_accessible_soil_layer.assert_called_once_with(depths)
    incorp.determine_layer_nutrient_uptake_potential.assert_called_once_with([1, 2, 3], 17.5, 35.0, 0.32)
    assert incorp.layer_nitrogen_potentials == [3.25, 6.33, 7.10]
    incorp.determine_layer_nutrient_demands.assert_called_once_with([3.25, 6.33, 7.10], [1, 2, 3])
    assert incorp.unmet_nitrogen_demands == [12, 15, 17]
    incorp.determine_layer_nutrient_uptake.assert_called_once_with([12, 15, 17], [3.25, 6.33, 7.10], [1, 2, 3])
    assert incorp.nitrogen_requests == [8.9, 9.9, 13.12]
    incorp.determine_layer_extracted_resource.assert_called_once_with([8.9, 9.9, 13.12], [1, 2, 3])
    assert incorp.actual_nitrogen_uptakes == [5.0, 4.0, 2.0]
    incorp.extend_nutrient_uptakes_to_full_profile.assert_called_once()
    incorp.extract_nutrient_from_soil_layers.assert_called_once()
    incorp.tally_total_nutrient_uptake.assert_called_once()


@pytest.mark.parametrize(
    "nitrates,depths,water_factor,gate",
    [
        ([0.5, 0.3, 0.2], [1, 2, 5], 0.692, True),
        ([0.5, 0.3, 0.2], [1, 2, 5], 0.692, False),
    ],
)
def test_incorporate_nitrogen(nitrates: list[float], depths: list[float], water_factor: float, gate: bool) -> None:
    """Tests that nitrogen uptake and fixation is performed correctly."""
    # initialize object
    data = CropData(
        half_mature_heat_fraction=0.54,
        mature_heat_fraction=0.99,
        biomass=122.8,
        biomass_growth_max=999,
        emergence_nitrogen_fraction=0.71,
        half_mature_nitrogen_fraction=0.68,
        mature_nitrogen_fraction=0.60,
    )
    with (
        patch(
            "RUFAS.routines.field.soil.soil_data.SoilData.soil_water_factor",
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
        incorp = NitrogenIncorporation(
            data,
            previous_nitrogen=0,
        )
        # mock intermediate functions
        incorp.shift_nitrogen_time = MagicMock(return_value=None)
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
        NitrogenIncorporation.determine_stored_nutrient = MagicMock(return_value=99.3)

        # run method
        incorp.incorporate_nitrogen(soil)

        # assertions
        incorp.shift_nitrogen_time.assert_called_once()
        incorp.determine_nutrient_shape_parameters.assert_called_once_with(0.54, 0.99, 0.71, 0.68, 0.60)
        assert incorp.nitrogen_shapes == [1.2, 0.8]
        incorp.determine_optimal_nutrient_fraction.assert_called_once_with(0.38, 0.71, 0.60, 1.2, 0.8)
        assert data.optimal_nitrogen_fraction == 0.75
        if gate:
            incorp.determine_optimal_nutrient.assert_called_once_with(0.75, 122.8)
            assert data.optimal_nitrogen == -268
            incorp.determine_potential_nutrient_uptake.assert_not_called()
            assert incorp.potential_nitrogen_uptake == 0
        else:
            assert data.optimal_nitrogen == 268
            incorp.determine_potential_nutrient_uptake.assert_called_once_with(268, 0, 0.60, 999)
            assert incorp.potential_nitrogen_uptake == 123.1
        incorp.try_fixation.assert_called_once_with(5 + 10 + 15.3, water_factor)
        NitrogenIncorporation.determine_stored_nutrient.assert_called_once()  # should called_once_with() w/attr mocked
        assert data.nitrogen == 99.3
