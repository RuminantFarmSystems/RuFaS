import pytest
from mock.mock import MagicMock, patch, PropertyMock
from RUFAS.config import Config
from RUFAS.time import Time
from RUFAS.routines.feed_storage.feed_manager import FeedManager
from RUFAS.routines.feed_storage.harvested_crop import HarvestedCrop
from RUFAS.routines.field.crop.crop_management import CropManagement
from RUFAS.routines.field.crop.crop_data import CropData, DEFAULT_CROP_QUALITIES
from RUFAS.routines.field.crop.crop_configurations.alfalfa import AlfalfaSilage
from math import exp
from RUFAS.routines.field.crop.harvest_operations import HarvestOperation
from RUFAS.routines.field.soil.soil_data import SoilData
from RUFAS.output_manager import OutputManager

om = OutputManager()


@pytest.fixture
def mock_time() -> Time:
    config = Config({
        "start_date": "1:1",
        "end_date": "1:10",
        "set_seed": False,
        "random_seed": 42,
    })
    return Time(config)


@pytest.fixture
def mock_feed_manager() -> FeedManager:
    return FeedManager()


@pytest.fixture
def mock_alfalfa_silage_data() -> AlfalfaSilage:
    return AlfalfaSilage()


# ---- Test Static Functions ----
@pytest.mark.parametrize("heatfrac,optimal_index", [
    (0, 1),
    (1, 1),
    (0.5, 1),
    (1.2, 1),
    (0.5, 0),
    (0.5, 100),
    (0.326, 12.2)  # arbitrary
])
def test_determine_potential_harvest_index(heatfrac: float, optimal_index: float):
    """ensure that the potential harvest index is properly calculated"""
    top = 100 * heatfrac
    bottom = (100 * heatfrac) + exp(11.1 - (10 * heatfrac))
    expect = optimal_index * (top / bottom)
    assert CropManagement._determine_potential_harvest_index(heatfrac, optimal_index) == expect


@pytest.mark.parametrize("idx,min_index,deficiency", [
    (1, .5, .5),  # start case
    (0, 0, 0),  # all zeros
    (0, 0.5, 0.5),  # zero harvest index
    (0, 0.5, 0.2),
    (-1, 0.5, 0.5),  # index < 0
    (1, 0, 0.5),  # zero min
    (1, 0.5, 1),  # high deficiency
    (1, 0.5, 0),  # no deficiency
    (1.35, 0.83, 0.29)  # arbitrary
])
def test_adjust_harvest_index(idx: float, min_index: float, deficiency: float):
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


@pytest.mark.parametrize("bmass,harv_ind", [
    (1, 1.2),
    (0, 1.2),  # no biomass
    (1, 2.5),  # increased biomass
    (136.5, 1.22)  # arbitrary
])
def test_determine_biomass_cut_from_whole_plant(bmass: float, harv_ind: float):
    """ensure that yield is correctly calculated by determine_yield_from_total_biomass()"""
    frac = 1 / (1 + harv_ind)
    assert CropManagement.determine_biomass_cut_from_whole_plant(bmass, harv_ind) == bmass * (1 - frac)


# ---- Test Member functions
def test_kill():
    """tests that a crop is properly killed by kill()"""
    crop = CropManagement(crop_data=CropData(yield_residue=5.29, biomass=192.33))
    crop.kill()
    assert not crop.data.is_alive
    assert crop.data.yield_residue == 5.29 + 192.33


def test_dry_down():
    crop = CropManagement(CropData(above_ground_biomass=10.2, dry_down_fraction=0.18))
    crop.dry_down()
    assert pytest.approx(crop.data.above_ground_biomass) == 10.2 * (1 - 0.18)


@pytest.mark.parametrize("heat_sched,heat_frac,harv_day,harv_yr,this_day,this_yr", [
    (False, 1.20, 100, 0, 80, 0),  # scheduled, too early (conflicting heat)
    (False, 1.00, 100, 0, 100, 0),  # scheduled, exactly right (conflicting heat)
    (False, 1.10, 100, 0, 110, 0),  # scheduled, too late (conflicting heat)

    (True, 1.08, 100, 0, 110, 0),  # heat-scheduled, too early (conflicting dates)
    (True, 1.10, 100, 0, 80, 0),  # heat-scheduled, exactly right (conflicting dates)
    (True, 1.20, 100, 0, 80, 0),  # heat-scheduled, passed time (conflicting dates)
])
def test_check_harvest_schedule(heat_sched: bool, heat_frac: float, harv_day: int, harv_yr: int,
                                this_day: int, this_yr: int):
    """ensure that is_harvest_day is correctly set"""
    data = CropData(use_heat_scheduling=heat_sched, next_harvest_day=harv_day, next_harvest_year=harv_yr,
                    harvest_heat_fraction=1.10)
    cm = CropManagement(data)
    with patch.object(CropData, "heat_fraction", new_callable=PropertyMock, return_value=heat_frac):
        cm.check_harvest_schedule(this_day, this_yr)
    scheduled_and_correct = (this_day == harv_day) & (this_yr == harv_yr) & (heat_sched is False)
    heat_scheduled_and_correct = (heat_sched is True) & (heat_frac >= 1.10)
    if scheduled_and_correct or heat_scheduled_and_correct:
        assert data.is_harvest_day is True
    else:
        assert data.is_harvest_day is False


@pytest.mark.parametrize("harvest,heat_frac,water_def", [
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
    (0.85, 0.5, 0.33)  # user-defined, ignore others
])
def test_determine_harvest_index(harvest, heat_frac, water_def):
    """ensure that the harvest index is properly evaluated"""
    data = CropData(user_harvest_index=harvest, optimal_harvest_index=0.95, min_harvest_index=0.5,
                    water_deficiency=water_def)
    crop = CropManagement(data)
    with patch.object(CropData, "heat_fraction", new_callable=PropertyMock, return_value=heat_frac):
        crop.determine_harvest_index()

    if harvest is not None:
        assert data.harvest_index == harvest
    else:
        potential = CropManagement._determine_potential_harvest_index(heat_frac, 0.95)
        assert data.potential_harvest_index == potential
        assert data.harvest_index == CropManagement._adjust_harvest_index(potential, 0.5, water_def)


@pytest.mark.parametrize("harvest_op,field_name,field_size,soil_data,killed", [
    (HarvestOperation.HARVEST_KILL, "test_1", 1.8, SoilData(field_size=1.8), True),
    (HarvestOperation.HARVEST_ONLY, "test_2", 4.5, SoilData(field_size=4.5), False),
    (HarvestOperation.KILL_ONLY, "test_3", 2.2, SoilData(field_size=2.5), True)
])
def test_manage_harvest(mock_time: Time, mock_feed_manager: FeedManager, harvest_op: HarvestOperation, field_name: str,
                        field_size: float, soil_data: SoilData, killed: bool) -> None:
    """ensure that crops are harvested properly, dependent on their operation specs"""
    crop = CropManagement()
    crop.data.yield_residue = 100.0

    with patch.object(crop, "determine_harvest_index") as harvest_index, \
            patch.object(crop, "kill", wraps=crop.kill) as kill, \
            patch.object(crop, "cut_crop") as cut_crop, \
            patch.object(crop, "_store_harvested_crop") as store_crop, \
            patch.object(crop, "_record_yield") as record_yield, \
            patch.object(crop, "_transfer_residue") as transfer_residue:
        crop.manage_harvest(harvest_op, field_name, field_size, mock_time, soil_data, mock_feed_manager)

        harvest_index.assert_called_once()
        # Method specific (one for each op type)
        if harvest_op == HarvestOperation.HARVEST_KILL:
            cut_crop.assert_called_once()
            kill.assert_called_once()
            store_crop.assert_called_once()

        if harvest_op == HarvestOperation.HARVEST_ONLY:
            cut_crop.assert_called_once()
            kill.assert_not_called()
            store_crop.assert_called_once()

        if harvest_op == HarvestOperation.KILL_ONLY:
            cut_crop.assert_not_called()
            kill.assert_called_once()
            store_crop.assert_not_called()

        record_yield.assert_called_once_with(field_name, field_size, mock_time.year, mock_time.day)
        transfer_residue.assert_called_once_with(soil_data, killed)


@pytest.mark.parametrize("efficiency,harvest,override,should_fail", [
    (0, 0, False, False),  # no harvest and not collection
    (0, 0.85, False, False),  # harvest but don't collect
    (0.9, 0, False, False),  # collect from no harvest
    (0.9, 0.85, False, False),  # harvest and collect
    (0, 0, True, False),  # harvest override
    (0.9, 0.85, True, False),  # harvest override
    (-1, 0.85, True, True),
    (0, 1.5, True, False)
])
def test_cut_crop(efficiency: float, harvest: float, override: bool, should_fail: bool):
    """Ensure that the crop cutting routines are properly executed and that errors are raised properly."""
    # setup
    data = CropData(harvest_index=harvest, biomass=100, leaf_area_index=2.3, accumulated_heat_units=1.1,
                    optimal_nitrogen_fraction=0.09, optimal_phosphorus_fraction=0.02,
                    yield_nitrogen_fraction=0.12, yield_phosphorus_fraction=0.0092, above_ground_biomass=75.0)
    if override:
        data.user_harvest_index = harvest
    crop = CropManagement(data)
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
            cut_biomass = data.above_ground_biomass * harvest

        assert data.cut_biomass == cut_biomass
        assert data.biomass == 100 - cut_biomass
        assert data.leaf_area_index == 2.3 * (1 - (cut_biomass / 100))
        assert data.accumulated_heat_units == 1.1 * (1 - (cut_biomass / 100))
        collected_fresh_yield = cut_biomass * efficiency
        collected_dry_matter_yield = collected_fresh_yield * (crop.data.dry_matter_percentage / 100)
        residue = cut_biomass * (1 - efficiency) * (crop.data.dry_matter_percentage / 100)
        crop._recalculate_biomass_distribution.assert_called_once()
        assert data.wet_yield_collected == collected_fresh_yield
        assert data.dry_matter_yield_collected == collected_dry_matter_yield
        assert data.yield_residue == residue

        if override:
            assert data.yield_nitrogen == collected_fresh_yield * 0.09
            assert data.yield_phosphorus == collected_fresh_yield * 0.02
            assert data.residue_nitrogen == residue * 0.09
            assert data.residue_phosphorus == residue * 0.02
        else:
            assert data.yield_nitrogen == collected_dry_matter_yield * 0.12
            assert data.yield_phosphorus == collected_dry_matter_yield * 0.0092
            assert data.residue_nitrogen == residue * 0.12
            assert data.residue_phosphorus == residue * 0.0092


@pytest.mark.parametrize("roots_harvested,cut_biomass,biomass,expected_surface_biomass,expected_root_biomass,"
                         "expected_root_fraction", [
                             (False, 100.0, 100, 50.0, 50.0, 0.5),
                             (False, 150.0, 50.0, 0.0, 50.0, 1.0),
                             (True, 175.0, 25.0, 0.0, 25.0, 1.0)
                         ]
                         )
def test_recalculate_biomass_distribution(roots_harvested: bool, cut_biomass: float, biomass: float,
                                          expected_surface_biomass: float, expected_root_biomass: float,
                                          expected_root_fraction: float) -> None:
    """Tests that biomass is correctly redistributed after a harvest event."""
    crop = CropData(cut_biomass=cut_biomass, biomass=biomass, above_ground_biomass=150, root_biomass=50,
                    root_fraction=0.25)
    crop_management = CropManagement(crop)

    crop_management._recalculate_biomass_distribution(roots_harvested)

    assert crop.above_ground_biomass == expected_surface_biomass
    assert crop.root_biomass == expected_root_biomass
    assert crop.root_fraction == expected_root_fraction


@pytest.mark.parametrize("field_size,wet_yield_collected,expected_fresh_mass", [
    (1.0, 2000.0, 2000.0),
    (2.0, 1500.0, 3000.0),
])
def test_store_harvested_crop(
        mock_time: Time,
        mock_feed_manager: FeedManager,
        mock_alfalfa_silage_data: AlfalfaSilage,
        field_size: float,
        wet_yield_collected: float,
        expected_fresh_mass: float,
) -> None:
    mock_alfalfa_silage_data.wet_yield_collected = wet_yield_collected
    crop_management = CropManagement(crop_data=mock_alfalfa_silage_data)
    expected_harvest_crop = HarvestedCrop(
        category=mock_alfalfa_silage_data.crop_category,
        type=mock_alfalfa_silage_data.crop_type,
        harvest_time=mock_time,
        storage_time=mock_time,
        fresh_mass=expected_fresh_mass,
        dry_matter_percentage=mock_alfalfa_silage_data.dry_matter_percentage,
        dry_matter_digestibility=DEFAULT_CROP_QUALITIES.get("dry_matter_digestibility"),
        crude_protein_percent=DEFAULT_CROP_QUALITIES.get("crude_protein_percent"),
        non_protein_nitrogen=DEFAULT_CROP_QUALITIES.get("non_protein_nitrogen"),
        starch=DEFAULT_CROP_QUALITIES.get("starch"),
        adf=DEFAULT_CROP_QUALITIES.get("adf"),
        ndf=DEFAULT_CROP_QUALITIES.get("ndf"),
        sugar=DEFAULT_CROP_QUALITIES.get("sugar"),
        lignin=mock_alfalfa_silage_data.lignin_dry_matter_percentage,
        ash=DEFAULT_CROP_QUALITIES.get("ash"),
    )

    with patch.object(mock_feed_manager, "receive_crop") as receive_crop:
        crop_management._store_harvested_crop(mock_time, field_size, mock_feed_manager)

        receive_crop.assert_called_once_with(expected_harvest_crop, mock_alfalfa_silage_data.storage_type)


@pytest.mark.parametrize("field_name,field_size,species,year,day,mass,dry_mass,nitrogen,phosphorus", [
    ("field_1", 1.8, "alfalfa", 1993, 200, 100, 90, 12.5, 5),
    ("field_2", 2.33, "corn", 1998, 216, 1500, 1200, 188, 24.5),
    ("field_2", 2.33, "corn", 1999, 218, 1550, 350, 172, 22.3),
    ("field_3", 0.98, "soybeans", 2003, 245, 1200, 800, 199, 89.3)
])
def test_record_yield(field_name: str, field_size: float, species: str, year: int, day: int, mass: float,
                      dry_mass: float, nitrogen: float, phosphorus: float) -> None:
    """Tests that harvest yields are correctly recorded to the OutputManager."""
    crop_manager = CropManagement()

    crop_manager.data.name = "test-crop"
    crop_manager.data.planting_day = 100
    crop_manager.data.planting_year = 1995
    crop_manager.data.species = species
    crop_manager.data.wet_yield_collected = mass
    crop_manager.data.dry_matter_yield_collected = dry_mass
    crop_manager.data.yield_nitrogen = nitrogen
    crop_manager.data.yield_phosphorus = phosphorus

    crop_manager._record_yield(field_name, field_size, year, day)

    expected_info_map = {"suffix": f"field='{field_name}'", "field_size": field_size,
                         "species": f"'{species}'"}
    expected_value = {"crop": crop_manager.data.name, "wet_yield": mass, "dry_yield": dry_mass, "nitrogen": nitrogen,
                      "phosphorus": phosphorus, "planting_date": {"year": 1995, "day": 100},
                      "harvest_date": {"year": year, "day": day}}

    actual = om.variables_pool[f"CropManagement._record_yield.harvest_yield.field='{field_name}'"]
    assert actual['info_maps'].__contains__(expected_info_map)
    assert actual['values'].__contains__(expected_value)


@pytest.mark.parametrize(
    "root_biomass,residue,nitrogen,killed,expected_root_depth,expected_surface_residue,expected_root_residue", [
        (150, 150, 22, True, 100, 0.0, 120.0),
        (100, 150, 22, True, 100, 50, 80.0),
        (100, 150, 22, False, 0, 150, 0)
    ])
def test_transfer_residue(root_biomass: float, residue: float, nitrogen: float, killed: bool,
                          expected_root_depth: float, expected_surface_residue: float,
                          expected_root_residue: float) -> None:
    """Tests that residue and associated nutrients from harvests and not collected are properly transferred to the
        soil."""
    soil_data = SoilData(field_size=1)
    soil_data.soil_layers[0].fresh_organic_nitrogen_content = 0
    crop_data = CropData(yield_residue=residue, residue_nitrogen=nitrogen, dry_matter_percentage=80.0)
    crop_data.root_depth = 100.0
    crop_data.root_biomass = root_biomass
    crop_manage = CropManagement(crop_data)

    crop_manage._transfer_residue(soil_data, killed)

    assert soil_data.plant_surface_residue == expected_surface_residue
    assert soil_data.plant_root_residue == expected_root_residue
    assert soil_data.crop_root_depth == expected_root_depth
    assert soil_data.soil_layers[0].fresh_organic_nitrogen_content == nitrogen
