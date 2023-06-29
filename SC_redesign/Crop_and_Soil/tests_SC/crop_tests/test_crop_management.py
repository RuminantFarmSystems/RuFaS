import pytest
from mock.mock import MagicMock
from SC_redesign.Crop_and_Soil.crop.crop_management import CropManagement
from SC_redesign.Crop_and_Soil.crop.crop_data import CropData
from math import exp
from SC_redesign.Crop_and_Soil.crop.harvest_operations import HarvestOperation
from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData
from RUFAS.output_manager import OutputManager

om = OutputManager()


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
    data = CropData(use_heat_scheduling=heat_sched, heat_fraction=heat_frac, next_harvest_day=harv_day,
                    next_harvest_year=harv_yr, harvest_heat_fraction=1.10)
    cm = CropManagement(data)
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
    data = CropData(user_harvest_index=harvest, heat_fraction=heat_frac, optimal_harvest_index=0.95,
                    min_harvest_index=0.5, water_deficiency=water_def)
    crop = CropManagement(data)
    crop.determine_harvest_index()

    if harvest is not None:
        assert data.harvest_index == harvest
    else:
        potential = CropManagement._determine_potential_harvest_index(heat_frac, 0.95)
        assert data.potential_harvest_index == potential
        assert data.harvest_index == CropManagement._adjust_harvest_index(potential, 0.5, water_def)


@pytest.mark.parametrize("harvest_op,field_name,field_size,year,day,soil_data", [
    (HarvestOperation.HARVEST, "test_1", 1.8, 1995, 200, SoilData(field_size=1.3)),
    (HarvestOperation.HARVEST_NOKILL, "test_2", 4.5, 2010, 150, SoilData(field_size=2.4))
])
def test_manage_harvest(harvest_op: HarvestOperation, field_name: str, field_size: float, year: int, day: int,
                        soil_data: SoilData) -> None:
    """ensure that crops are harvested properly, dependent on their operation specs"""
    # Setup
    crop = CropManagement()
    crop.determine_harvest_index = MagicMock()
    crop.kill = MagicMock()
    crop.cut_crop = MagicMock()
    crop._record_yield = MagicMock()
    crop._transfer_residue = MagicMock()

    # Act
    crop.manage_harvest(harvest_op, field_name, field_size, year, day, soil_data)

    # Assertions
    crop.determine_harvest_index.assert_called_once()
    # Method specific (one for each op type)
    if harvest_op == HarvestOperation.HARVEST:
        crop.cut_crop.assert_called_once()
        crop.kill.assert_called_once()

    if harvest_op == HarvestOperation.HARVEST_NOKILL:
        crop.cut_crop.assert_called_once()
        crop.kill.assert_not_called()

    crop._record_yield.assert_called_once_with(field_name, field_size, year, day)
    crop._transfer_residue.assert_called_once_with(soil_data)


@pytest.mark.parametrize("efficiency,harvest,override", [
    (0, 0, False),  # no harvest and not collection
    (0, 0.85, False),  # harvest but don't collect
    (0.9, 0, False),  # collect from no harvest
    (0.9, 0.85, False),  # harvest and collect
    (0, 0, True),  # harvest override
    (0.9, 0.85, True), # harvest override
    (-1, 0.85, True),
    (0, 1.5, True)
])
def test_cut_crop(efficiency: float, harvest: float, override: bool):
    """ensure that the crop cutting routines are properly executed"""
    # setup
    data = CropData(harvest_index=harvest, biomass=100, leaf_area_index=2.3, accumulated_heat_units=1.1,
                    optimal_nitrogen_fraction=0.09, optimal_phosphorus_fraction=0.02,
                    yield_nitrogen_fraction=0.12, yield_phosphorus_fraction=0.0092, above_ground_biomass=0.37)
    if override:
        data.user_harvest_index = harvest
    crop = CropManagement(data)

    # act
    try:
        crop.cut_crop(efficiency)
    except ValueError as e:
        assert not 0 <= efficiency <= 1.0
        assert str(e) == f"Expected collected_fraction to be between 0 and 1 (inclusive), received '{efficiency}'."
        return


    # expect/assert
    if harvest > 1:
        cut_biomass = CropManagement.determine_biomass_cut_from_whole_plant(100, harvest)
    else:
        cut_biomass = data.above_ground_biomass * harvest

    assert data.cut_biomass == cut_biomass
    assert data.biomass == 100 - cut_biomass
    assert data.leaf_area_index == 2.3 * (1 - (cut_biomass / 100))
    assert data.accumulated_heat_units == 1.1 * (1 - (cut_biomass / 100))
    collected = cut_biomass * efficiency
    residue = cut_biomass * (1 - efficiency)
    assert data.yield_collected == collected
    assert data.yield_residue == residue

    if override:
        assert data.yield_nitrogen == collected * 0.09
        assert data.yield_phosphorus == collected * 0.02
        assert data.residue_nitrogen == residue * 0.09
        assert data.residue_phosphorus == residue * 0.02
    else:
        assert data.yield_nitrogen == collected * 0.12
        assert data.yield_phosphorus == collected * 0.0092
        assert data.residue_nitrogen == residue * 0.12
        assert data.residue_phosphorus == residue * 0.0092


@pytest.mark.parametrize("field_name,field_size,species,year,day,mass,nitrogen,phosphorus", [
    ("field_1", 1.8, "alfalfa", 1993, 200, 100, 12.5, 5),
    ("field_2", 2.33, "corn", 1998, 216, 1500, 188, 24.5),
    ("field_2", 2.33, "corn", 1999, 218, 1550, 172, 22.3),
    ("field_3", 0.98, "soybeans", 2003, 245, 1200, 199, 89.3)
])
def test_record_yield(field_name: str, field_size: float, species: str, year: int, day: int, mass: float,
                      nitrogen: float, phosphorus: float) -> None:
    """Tests that harvest yields are correctly recorded to the OutputManager."""
    crop_manager = CropManagement()

    crop_manager.data.species = species
    crop_manager.data.yield_collected = mass
    crop_manager.data.yield_nitrogen = nitrogen
    crop_manager.data.yield_phosphorus = phosphorus

    crop_manager._record_yield(field_name, field_size, year, day)

    expected_info_map = {"prefix": f"field_name:'{field_name}'", "field_size": field_size, "species": f"'{species}'",
                         "date": {"year": year, "day": day}}
    expected_value = {"yield": mass, "nitrogen": nitrogen, "phosphorus": phosphorus}

    actual = om.variables_pool[f"field_name:'{field_name}'.harvest_yield"]
    assert actual['info_maps'].__contains__(expected_info_map)
    assert actual['values'].__contains__(expected_value)


@pytest.mark.parametrize("residue,nitrogen", [
    (100, 22),
    (0, 0),
    (200.23, 45.66)
])
def test_transfer_residue(residue: float, nitrogen: float) -> None:
    """Tests that residue and associated nutrients from harvests and not collected are properly transferred to the
        soil."""
    soil_data = SoilData(field_size=1)
    soil_data.plant_surface_residue = 0
    soil_data.soil_layers[0].fresh_organic_nitrogen_content = 0
    crop_data = CropData(yield_residue=residue, yield_nitrogen=nitrogen)
    crop_manage = CropManagement(crop_data)

    crop_manage._transfer_residue(soil_data)

    assert soil_data.plant_surface_residue == residue
    assert soil_data.soil_layers[0].fresh_organic_nitrogen_content == nitrogen
