from math import exp

import pytest
from mock.mock import MagicMock, PropertyMock, patch
from pytest_mock import MockerFixture

from RUFAS.output_manager import OutputManager
from RUFAS.data_structures.crop_soil_to_feed_storage_connection import (
    HarvestedCrop,
)
from RUFAS.biophysical.field.crop.crop_data import DEFAULT_DRY_MATTER_DIGESTIBILITY, CropData
from RUFAS.biophysical.field.crop.crop_management import CropManagement
from RUFAS.biophysical.field.crop.harvest_operations import HarvestOperation
from RUFAS.biophysical.field.soil.layer_data import LayerData
from RUFAS.biophysical.field.soil.soil_data import SoilData
from RUFAS.rufas_time import RufasTime
from RUFAS.units import MeasurementUnits

from tests.test_biophysical.test_crop_soil_field.sample_crop_configuration import SAMPLE_CROP_CONFIGURATION


@pytest.fixture
def mock_time() -> RufasTime:
    return MagicMock(auto_spec=RufasTime)


@pytest.fixture
def mock_crop_data() -> CropData:
    return CropData(**SAMPLE_CROP_CONFIGURATION)


@pytest.fixture
def crop_manager(mock_crop_data: CropData) -> CropManagement:
    return CropManagement(crop_data=mock_crop_data)


# ---- Test Static Functions ----
@pytest.mark.parametrize(
    "heatfrac,optimal_index",
    [
        (0, 1),
        (1, 1),
        (0.5, 1),
        (1.2, 1),
        (0.5, 0),
        (0.5, 100),
        (0.326, 12.2),  # arbitrary
    ],
)
def test_determine_potential_harvest_index(heatfrac: float, optimal_index: float) -> None:
    """ensure that the potential harvest index is properly calculated"""
    top = 100 * heatfrac
    bottom = (100 * heatfrac) + exp(11.1 - (10 * heatfrac))
    expect = optimal_index * (top / bottom)
    assert CropManagement._determine_potential_harvest_index(heatfrac, optimal_index) == expect


@pytest.mark.parametrize(
    "idx,min_index,deficiency",
    [
        (1, 0.5, 0.5),  # start case
        (0, 0, 0),  # all zeros
        (0, 0.5, 0.5),  # zero harvest index
        (0, 0.5, 0.2),
        (-1, 0.5, 0.5),  # index < 0
        (1, 0, 0.5),  # zero min
        (1, 0.5, 1),  # high deficiency
        (1, 0.5, 0),  # no deficiency
        (1.35, 0.83, 0.29),  # arbitrary
    ],
)
def test_adjust_harvest_index(idx: float, min_index: float, deficiency: float) -> None:
    """ensure that actual harvest index is properly calculated by calc_actual_harvest_index()"""
    if min_index < 0:
        adj_min = 0
    else:
        adj_min = min_index

    if idx < adj_min:
        adj_idx = adj_min
    else:
        adj_idx = idx

    diff = adj_idx - adj_min
    bottom = deficiency + exp(6.13 - 0.883 * deficiency)
    expect = diff * deficiency / bottom + adj_min
    if expect < 0:
        expect = 0
    assert CropManagement._adjust_harvest_index(idx, min_index, deficiency) == expect


@pytest.mark.parametrize(
    "bmass,harv_ind",
    [
        (1, 1.2),
        (0, 1.2),  # no biomass
        (1, 2.5),  # increased biomass
        (136.5, 1.22),  # arbitrary
    ],
)
def test_determine_biomass_cut_from_whole_plant(bmass: float, harv_ind: float) -> None:
    """ensure that yield is correctly calculated by determine_yield_from_total_biomass()"""
    frac = 1 / (1 + harv_ind)
    assert CropManagement.determine_biomass_cut_from_whole_plant(bmass, harv_ind) == bmass * (1 - frac)


# ---- Test Member functions
def test_kill(mock_crop_data: CropData) -> None:
    """Tests that a crop is properly killed."""
    mock_crop_data.biomass = 192.33
    crop = CropManagement(crop_data=mock_crop_data, yield_residue=5.29)

    crop.kill()

    assert not crop.data.is_alive
    assert crop.yield_residue == 5.29 + 192.33


@pytest.mark.parametrize(
    "harvest,heat_frac,water_def",
    [
        (None, 0, 0),  # base case
        (None, 0.5, 0),  # accumulated half heat
        (None, 0.9, 0),  # accumulated 90% heat
        (None, 1.0, 0),  # accumulated all heat
        (None, 1.2, 0),  # accumulated more than PHU
        (None, 0, 0.5),  # increase water deficiency
        (None, 0.5, 0.5),  # increase water deficiency and heat
        (None, 0, 1.0),  # max deficiency, no heat
        (None, 0.5, 1.0),  # max deficiency, some heat
        (None, 1.0, 1.0),  # max deficiency, max heat
        (1.0, None, None),  # user-defined harvest index, others not given
        (0.85, 0.5, 0.33),  # user-defined, ignore others
    ],
)
def test_determine_harvest_index(
    mock_crop_data: CropData, harvest: float | None, heat_frac: float | None, water_def: float | None
) -> None:
    """ensure that the harvest index is properly evaluated"""
    mock_crop_data.user_harvest_index = harvest
    mock_crop_data.water_deficiency = water_def
    mock_crop_data.optimal_harvest_index = 0.95
    mock_crop_data.minimum_harvest_index = 0.5
    crop = CropManagement(mock_crop_data)

    with patch.object(CropData, "heat_fraction", new_callable=PropertyMock, return_value=heat_frac):
        crop.determine_harvest_index()

    if harvest is not None:
        assert crop.harvest_index == harvest
    else:
        potential = CropManagement._determine_potential_harvest_index(heat_frac, 0.95)
        assert crop.potential_harvest_index == potential
        assert crop.harvest_index == CropManagement._adjust_harvest_index(potential, 0.5, water_def)


@pytest.mark.parametrize(
    "harvest_op,field_name,field_size,soil_data,killed,expect_harvest",
    [
        (HarvestOperation.HARVEST_KILL, "test_1", 1.8, SoilData(field_size=1.8), True, True),
        (HarvestOperation.HARVEST_ONLY, "test_2", 4.5, SoilData(field_size=4.5), False, True),
        (HarvestOperation.KILL_ONLY, "test_3", 2.2, SoilData(field_size=2.5), True, False),
    ],
)
def test_manage_harvest(
    mocker: MockerFixture,
    crop_manager: CropManagement,
    mock_time: RufasTime,
    harvest_op: HarvestOperation,
    field_name: str,
    field_size: float,
    soil_data: SoilData,
    killed: bool,
    expect_harvest: bool,
) -> None:
    """ensure that crops are harvested properly, dependent on their operation specs"""
    crop_manager.yield_residue = 100.0

    harvest_index = mocker.patch.object(crop_manager, "determine_harvest_index")
    kill = mocker.patch.object(crop_manager, "kill", wraps=crop_manager.kill)
    cut_crop = mocker.patch.object(crop_manager, "cut_crop")
    get_crop = mocker.patch.object(
        crop_manager,
        "_get_harvested_crop",
        return_value=(
            expected_val := HarvestedCrop(
                config_name="mock_crop",
                field_name="mock_field",
                harvest_time=mock_time.current_date.date(),
                storage_time=mock_time.current_date.date(),
                dry_matter_mass=1234.5,
                dry_matter_percentage=42.0,
                dry_matter_digestibility=DEFAULT_DRY_MATTER_DIGESTIBILITY,
                crude_protein_percent=20.0,
                non_protein_nitrogen=10.0,
                starch=2.0,
                adf=33.0,
                ndf=43.0,
                sugar=6.0,
                lignin=7.0,
                ash=10.0,
            )
        ),
    )
    record_yield = mocker.patch.object(crop_manager, "_record_yield")
    transfer_residue = mocker.patch.object(crop_manager, "_transfer_residue")

    actual = crop_manager.manage_harvest(harvest_op, field_name, field_size, mock_time, soil_data)

    harvest_index.assert_called_once()
    if harvest_op == HarvestOperation.HARVEST_KILL:
        cut_crop.assert_called_once()
        kill.assert_called_once()
        get_crop.assert_called_once()

    if harvest_op == HarvestOperation.HARVEST_ONLY:
        cut_crop.assert_called_once()
        kill.assert_not_called()
        get_crop.assert_called_once()

    if harvest_op == HarvestOperation.KILL_ONLY:
        cut_crop.assert_not_called()
        kill.assert_called_once()
        get_crop.assert_not_called()

    record_yield.assert_called_once_with(
        harvest_op, field_name, field_size, mock_time.current_calendar_year, mock_time.current_julian_day
    )
    transfer_residue.assert_called_once_with(soil_data, killed)

    if expect_harvest:
        assert actual == expected_val
    else:
        assert actual is None


@pytest.mark.parametrize(
    "efficiency,harvest,override,should_fail",
    [
        (0, 0, False, False),  # no harvest and not collection
        (0, 0.85, False, False),  # harvest but don't collect
        (0.9, 0, False, False),  # collect from no harvest
        (0.9, 0.85, False, False),  # harvest and collect
        (0, 0, True, False),  # harvest override
        (0.9, 0.85, True, False),  # harvest override
        (-1, 0.85, True, True),
        (0, 1.5, True, False),
    ],
)
def test_cut_crop(
    mock_crop_data: CropData, efficiency: float, harvest: float, override: bool, should_fail: bool
) -> None:
    """Ensure that the crop cutting routines are properly executed and that errors are raised properly."""
    # setup
    mock_crop_data.biomass = 100
    mock_crop_data.leaf_area_index = 2.3
    mock_crop_data.accumulated_heat_units = 1.1
    mock_crop_data.optimal_nitrogen_fraction = 0.09
    mock_crop_data.optimal_phosphorus_fraction = 0.02
    mock_crop_data.yield_nitrogen_fraction = 0.12
    mock_crop_data.above_ground_biomass = 75.0
    mock_crop_data.yield_phosphorus_fraction = 0.0092
    if override:
        mock_crop_data.user_harvest_index = harvest
    crop = CropManagement(mock_crop_data, harvest_index=harvest)
    crop._recalculate_biomass_distribution = MagicMock()

    # act
    if should_fail:
        try:
            crop.cut_crop(efficiency)
        except ValueError as e:
            assert str(e) == f"Expected collected_fraction to be between 0 and 1 (inclusive), received '{efficiency}'."
        crop._recalculate_biomass_distribution.assert_not_called()
    else:
        crop.cut_crop(efficiency)
        if harvest > 1:
            cut_biomass = CropManagement.determine_biomass_cut_from_whole_plant(100, harvest)
        else:
            cut_biomass = mock_crop_data.above_ground_biomass * harvest

        assert crop.cut_biomass == cut_biomass
        assert mock_crop_data.biomass == 100 - cut_biomass
        assert mock_crop_data.leaf_area_index == 2.3 * (1 - (cut_biomass / 100))
        assert mock_crop_data.accumulated_heat_units == 1.1 * (1 - (cut_biomass / 100))
        collected_fresh_yield = cut_biomass / (crop.data.dry_matter_percentage / 100) * efficiency
        collected_dry_matter_yield = cut_biomass * efficiency
        residue = cut_biomass * (1 - efficiency)
        crop._recalculate_biomass_distribution.assert_called_once()
        assert crop.wet_yield_collected == collected_fresh_yield
        assert crop.dry_matter_yield_collected == collected_dry_matter_yield
        assert crop.yield_residue == residue

        if override:
            assert crop.yield_nitrogen == collected_fresh_yield * 0.09
            assert crop.yield_phosphorus == collected_fresh_yield * 0.02
            assert crop.residue_nitrogen == residue * 0.09
            assert crop.residue_phosphorus == residue * 0.02
        else:
            assert crop.yield_nitrogen == collected_dry_matter_yield * 0.12
            assert crop.yield_phosphorus == collected_dry_matter_yield * 0.0092
            assert crop.residue_nitrogen == residue * 0.12
            assert crop.residue_phosphorus == residue * 0.0092


@pytest.mark.parametrize(
    "roots_harvested,cut_biomass,biomass,expected_surface_biomass,expected_root_biomass,expected_root_fraction",
    [
        (False, 100.0, 100, 50.0, 50.0, 0.5),
        (False, 150.0, 50.0, 0.0, 50.0, 1.0),
        (True, 175.0, 25.0, 0.0, 25.0, 1.0),
    ],
)
def test_recalculate_biomass_distribution(
    mock_crop_data: CropData,
    roots_harvested: bool,
    cut_biomass: float,
    biomass: float,
    expected_surface_biomass: float,
    expected_root_biomass: float,
    expected_root_fraction: float,
) -> None:
    """Tests that biomass is correctly redistributed after a harvest event."""
    mock_crop_data.biomass = biomass
    mock_crop_data.above_ground_biomass = 150.0
    mock_crop_data.root_biomass = 50.0
    mock_crop_data.root_fraction = 0.25
    crop_management = CropManagement(mock_crop_data, cut_biomass=cut_biomass)

    crop_management._recalculate_biomass_distribution(roots_harvested)

    assert mock_crop_data.above_ground_biomass == expected_surface_biomass
    assert mock_crop_data.root_biomass == expected_root_biomass
    assert mock_crop_data.root_fraction == expected_root_fraction


@pytest.mark.parametrize(
    "field_size,dry_yield_collected,expected_dry_mass", [(1.0, 2000.0, 2000.0), (2.0, 1500.0, 3000.0)]
)
def test_store_harvested_crop(
    mock_time: RufasTime,
    mock_crop_data: CropData,
    field_size: float,
    dry_yield_collected: float,
    expected_dry_mass: float,
) -> None:
    crop_management = CropManagement(crop_data=mock_crop_data, dry_matter_yield_collected=dry_yield_collected)
    expected_harvest_crop = HarvestedCrop(
        config_name=mock_crop_data.name,
        field_name="mock_field",
        harvest_time=mock_time.current_date.date(),
        storage_time=mock_time.current_date.date(),
        dry_matter_mass=expected_dry_mass,
        dry_matter_percentage=mock_crop_data.dry_matter_percentage,
        dry_matter_digestibility=DEFAULT_DRY_MATTER_DIGESTIBILITY,
        crude_protein_percent=mock_crop_data.crude_protein_percent_at_harvest,
        non_protein_nitrogen=mock_crop_data.non_protein_nitrogen_at_harvest,
        starch=mock_crop_data.starch_at_harvest,
        adf=mock_crop_data.adf_at_harvest,
        ndf=mock_crop_data.ndf_at_harvest,
        sugar=mock_crop_data.sugar_at_harvest,
        lignin=mock_crop_data.lignin_dry_matter_percentage,
        ash=mock_crop_data.ash_at_harvest,
    )
    expected_harvest_crop.last_time_degraded = expected_harvest_crop.storage_time

    actual = crop_management._get_harvested_crop(mock_time, field_size, "mock_field")

    assert actual.dry_matter_mass == expected_dry_mass
    assert actual.dry_matter_percentage == expected_harvest_crop.dry_matter_percentage
    assert actual.dry_matter_digestibility == expected_harvest_crop.dry_matter_digestibility
    assert actual.crude_protein_percent == expected_harvest_crop.crude_protein_percent
    assert actual.non_protein_nitrogen == expected_harvest_crop.non_protein_nitrogen
    assert actual.starch == expected_harvest_crop.starch
    assert actual.adf == expected_harvest_crop.adf
    assert actual.ndf == expected_harvest_crop.ndf
    assert actual.sugar == expected_harvest_crop.sugar
    assert actual.lignin == expected_harvest_crop.lignin
    assert actual.ash == expected_harvest_crop.ash
    assert actual.last_time_degraded == expected_harvest_crop.last_time_degraded


@pytest.mark.parametrize(
    "harvest_op, field_name,field_size,year,day,mass,dry_mass,nitrogen,phosphorus",
    [
        (HarvestOperation.HARVEST_KILL, "field_1", 1.8, 1993, 200, 100, 90, 12.5, 5),
        (HarvestOperation.HARVEST_ONLY, "field_2", 2.33, 1998, 216, 1500, 1200, 188, 24.5),
        (HarvestOperation.KILL_ONLY, "field_2", 2.33, 1999, 218, 1550, 350, 172, 22.3),
        (HarvestOperation.HARVEST_ONLY, "field_3", 0.98, 2003, 245, 1200, 800, 199, 89.3),
    ],
)
def test_record_yield(
    crop_manager: CropManagement,
    harvest_op: HarvestOperation,
    field_name: str,
    field_size: float,
    year: int,
    day: int,
    mass: float,
    dry_mass: float,
    nitrogen: float,
    phosphorus: float,
    mocker: MockerFixture,
) -> None:
    """Tests that harvest yields are correctly recorded to the OutputManager."""
    crop_manager.data.planting_day = 100
    crop_manager.data.planting_year = 1995
    crop_manager.wet_yield_collected = mass
    crop_manager.dry_matter_yield_collected = dry_mass
    crop_manager.yield_nitrogen = nitrogen
    crop_manager.yield_phosphorus = phosphorus
    crop_manager.residue_nitrogen = 333.3
    crop_manager.residue_phosphorus = 33.3

    expected_units = {
        "crop": MeasurementUnits.UNITLESS,
        "harvest_type": MeasurementUnits.UNITLESS,
        "wet_yield": MeasurementUnits.WET_KILOGRAMS_PER_HECTARE,
        "dry_yield": MeasurementUnits.DRY_KILOGRAMS_PER_HECTARE,
        "nitrogen": MeasurementUnits.KILOGRAMS_PER_HECTARE,
        "phosphorus": MeasurementUnits.KILOGRAMS_PER_HECTARE,
        "yield_residue": MeasurementUnits.DRY_KILOGRAMS_PER_HECTARE,
        "residue_nitrogen": MeasurementUnits.KILOGRAMS_PER_HECTARE,
        "residue_phosphorus": MeasurementUnits.KILOGRAMS_PER_HECTARE,
        "harvest_index": MeasurementUnits.UNITLESS,
        "planting_year": MeasurementUnits.CALENDAR_YEAR,
        "planting_day": MeasurementUnits.ORDINAL_DAY,
        "harvest_year": MeasurementUnits.CALENDAR_YEAR,
        "harvest_day": MeasurementUnits.ORDINAL_DAY,
        "field_size": MeasurementUnits.HECTARE,
        "field_name": MeasurementUnits.UNITLESS,
    }

    expected_info_map = {
        "class": crop_manager.__class__.__name__,
        "function": crop_manager._record_yield.__name__,
        "suffix": f"field='{field_name}'",
        "units": expected_units,
    }
    expected_value = {
        "crop": crop_manager.data.name,
        "harvest_type": harvest_op.value,
        "wet_yield": mass,
        "dry_yield": dry_mass,
        "nitrogen": nitrogen,
        "phosphorus": phosphorus,
        "planting_year": 1995,
        "planting_day": 100,
        "yield_residue": crop_manager.yield_residue,
        "residue_nitrogen": 333.3,
        "residue_phosphorus": 33.3,
        "harvest_index": crop_manager.harvest_index,
        "harvest_year": year,
        "harvest_day": day,
        "field_size": field_size,
        "field_name": field_name,
    }
    add_variable = mocker.patch.object(OutputManager, "add_variable")
    crop_manager._record_yield(harvest_op, field_name, field_size, year, day)

    add_variable.assert_called_once_with(
        "harvest_yield",
        expected_value,
        expected_info_map,
    )


@pytest.mark.parametrize(
    "root_biomass,residue,killed,expected_surface_residue",
    [
        (150, 150, True, 0.0),
        (100, 150, True, 50),
        (100, 150, False, 150),
    ],
)
def test_transfer_residue(
    mock_crop_data: CropData,
    root_biomass: float,
    residue: float,
    killed: bool,
    expected_surface_residue: float,
) -> None:
    """Tests that residue and associated nutrients from harvests and not collected are properly transferred to the
    soil."""
    soil_data = SoilData(field_size=1)
    soil_data.soil_layers[0].fresh_organic_nitrogen_content = 0
    soil_data.soil_layers[0].labile_inorganic_phosphorus_content = 0
    mock_crop_data.root_depth = 100.0
    mock_crop_data.root_biomass = root_biomass
    crop_manage = CropManagement(mock_crop_data, yield_residue=residue, residue_nitrogen=22, residue_phosphorus=23)

    with patch.object(crop_manage, "_distribute_residue_nutrients") as distribute_nutrients:
        crop_manage._transfer_residue(soil_data, killed)
        distribute_nutrients.assert_called_once() if killed else distribute_nutrients.assert_not_called()

    if not killed:
        assert soil_data.soil_layers[0].plant_residue == expected_surface_residue
        assert soil_data.soil_layers[0].fresh_organic_nitrogen_content == 22
        assert soil_data.soil_layers[0].labile_inorganic_phosphorus_content == 23
    assert crop_manage.yield_residue == 0.0
    assert crop_manage.residue_nitrogen == 0.0
    assert crop_manage.residue_phosphorus == 0.0


@pytest.mark.parametrize(
    "root_depth,n,p,expected_n,expected_p",
    [
        (100.0, 40.0, 20.0, [22.0, 12.0, 2.0, 4.0], [11.0, 6.0, 1.0, 2.0]),
        (45.0, 40.0, 20.0, [22.0, 12.0, 2.0, 4.0], [11.0, 6.0, 1.0, 2.0]),
    ],
)
def test_distribute_residue_nutrients(
    mocker: MockerFixture,
    mock_crop_data: CropData,
    root_depth: float,
    n: float,
    p: float,
    expected_n: list[float],
    expected_p: list[float],
) -> None:
    mock_crop_data.root_biomass = 50.0
    mock_crop_data.max_root_depth = root_depth
    crop_manager = CropManagement(mock_crop_data, yield_residue=100.0, residue_nitrogen=n, residue_phosphorus=p)
    mocker.patch.object(crop_manager, "_calculate_root_mass_distribution", side_effect=[0.1, 0.7, 0.8, 1.0])
    field_size = 1.0
    layers = [
        LayerData(top_depth=0.0, bottom_depth=20.0, field_size=field_size),
        LayerData(top_depth=20.0, bottom_depth=50.0, field_size=field_size),
        LayerData(top_depth=50.0, bottom_depth=100.0, field_size=field_size),
    ]
    soil_data = SoilData(field_size=field_size, soil_layers=layers)
    soil_data.set_vectorized_layer_attribute("fresh_organic_nitrogen_content", [0.0] * 3)
    soil_data.set_vectorized_layer_attribute("active_organic_nitrogen_content", [0.0] * 3)
    soil_data.set_vectorized_layer_attribute("labile_inorganic_phosphorus_content", [0.0] * 3)
    soil_data.set_vectorized_layer_attribute("plant_residue", [0.0] * 3)

    expected_pr = [55.0, 30.0, 5.0, 10.0]
    crop_manager._distribute_residue_nutrients(soil_data)

    assert soil_data.soil_layers[0].fresh_organic_nitrogen_content == pytest.approx(expected_n[0])
    assert soil_data.get_vectorized_layer_attribute("fresh_organic_nitrogen_content")[1:3] == pytest.approx(
        expected_n[1:-1]
    )
    assert soil_data.get_vectorized_layer_attribute("labile_inorganic_phosphorus_content") == pytest.approx(
        expected_p[:-1]
    )
    assert soil_data.get_vectorized_layer_attribute("plant_residue") == pytest.approx(expected_pr[:-1])

    assert soil_data.vadose_zone_layer.fresh_organic_nitrogen_content == pytest.approx(expected_n[-1])
    assert soil_data.vadose_zone_layer.labile_inorganic_phosphorus_content == pytest.approx(expected_p[-1])
    assert soil_data.vadose_zone_layer.plant_residue == pytest.approx(expected_pr[-1])


@pytest.mark.parametrize(
    "fraction,mass,n,p,expected_mass,expected_fresh_n,expected_active_n,expected_p",
    [(0.5, 100.0, 20.0, 10.0, 50.0, 10.0, 0.0, 5.0), (0.25, 80.0, 12.0, 4.0, 20.0, 3.0, 0.0, 1.0)],
)
def test_add_residue_to_layer(
    crop_manager: CropManagement,
    fraction: float,
    mass: float,
    n: float,
    p: float,
    expected_mass: float,
    expected_fresh_n: float,
    expected_active_n: float,
    expected_p: float,
) -> None:
    """Tests that _add_residue_to_layer in CropManagement."""
    layer = LayerData(top_depth=20.0, bottom_depth=50.0, field_size=1.0)
    layer.plant_residue = 0.0
    layer.fresh_organic_nitrogen_content = 0.0
    layer.active_organic_nitrogen_content = 0.0
    layer.labile_inorganic_phosphorus_content = 0.0

    crop_manager._add_yield_residue_to_layer(layer, fraction, mass, n, p)

    assert layer.plant_residue == expected_mass
    assert layer.fresh_organic_nitrogen_content == expected_fresh_n
    assert layer.active_organic_nitrogen_content == expected_active_n
    assert layer.labile_inorganic_phosphorus_content == expected_p


@pytest.mark.parametrize(
    "d_a,c,root_depth,depth,expected",
    [
        (145.0, -1.165, 20.0, 20.0, 1.0),
        (145.0, -1.165, 1500.0, 200.0, 0.6008058),
        (145.0, -1.165, 2000.0, 1500.0, 0.9719949),
        (145.0, -1.165, 2000.0, 2050.0, 1.0),
        (116.0, -0.626, 500.0, 0.0, 0.0),
        (116.0, -0.626, 500.0, 10.0, 0.1830823),
        (116.0, -0.626, 1721.0, 150.0, 0.5537369),
        (116.0, -0.626, 1721.0, 2000.0, 1.0),
    ],
)
def test_calculate_root_mass_distribution(
    crop_manager: CropManagement, d_a: float, c: float, root_depth: float, depth: float, expected: float
) -> None:
    """Tests _calculate_root_mass_distribution() in CropManagement."""
    crop_manager.data.root_distribution_param_da = d_a
    crop_manager.data.root_distribution_param_c = c
    crop_manager.data.max_root_depth = root_depth

    actual = crop_manager._calculate_root_mass_distribution(depth)

    assert pytest.approx(actual) == expected


def test_cut_crop_zero_division(mocker: MockerFixture, mock_crop_data: CropData) -> None:
    """Ensure that the crop cutting routines have division error"""
    # setup
    mock_crop_data.biomass = 0
    mock_crop_data.leaf_area_index = 2.3
    mock_crop_data.accumulated_heat_units = 1.1
    mock_crop_data.optimal_nitrogen_fraction = 0.09
    mock_crop_data.optimal_phosphorus_fraction = 0.02
    mock_crop_data.yield_nitrogen_fraction = 0.12
    mock_crop_data.above_ground_biomass = 75.0
    mock_crop_data.yield_phosphorus_fraction = 0.0092

    crop = CropManagement(mock_crop_data, harvest_index=3)
    crop._recalculate_biomass_distribution = MagicMock()
    crop.determine_biomass_cut_from_whole_plant = MagicMock(return_value=0)

    patch_for_add_warning = mocker.patch.object(crop.om, "add_warning")
    crop.cut_crop(0.5)
    crop.determine_biomass_cut_from_whole_plant.assert_called_once()
    info_map = {"class": crop.__class__.__name__, "function": crop.cut_crop.__name__}
    warning_name = "Zero division error in crop management"
    warning_message = (
        "A zero division error occurred in the harvesting process of crop management when calculating "
        "fraction cut."
        "The variable 'biomass' in CropData has an invalid value: '0'. "
    )
    patch_for_add_warning.assert_called_once_with(warning_name, warning_message, info_map)
