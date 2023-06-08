from math import exp
from typing import Optional, List, Dict, Tuple
from unittest.mock import MagicMock, PropertyMock, patch, call
import pytest
from SC_redesign.Crop_and_Soil.crop.crop import Crop
from SC_redesign.Crop_and_Soil.crop.crop_data import CropData
from SC_redesign.Crop_and_Soil.crop.species_data_factory import CropSpecies
from SC_redesign.Crop_and_Soil.manager.current_weather import CurrentWeather
from SC_redesign.Crop_and_Soil.manager.events import Event, PlantingEvent, HarvestEvent
from SC_redesign.Crop_and_Soil.soil.soil import Soil
from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData
from SC_redesign.Crop_and_Soil.field.field import Field
from SC_redesign.Crop_and_Soil.field.field_data import FieldData
from SC_redesign.Crop_and_Soil.crop.dormancy import Dormancy
from SC_redesign.Crop_and_Soil.crop_and_soil_constants import LITERS_TO_CUBIC_MILLIMETERS, \
    HECTARES_TO_SQUARE_MILLIMETERS
from RUFAS.classes import Time


@pytest.mark.parametrize("all_events,events_remaining,events_occurring_today", [
    ([PlantingEvent("test_1", 1996, 120, False), PlantingEvent("test_2", 1996, 120, False),
      PlantingEvent("test_3", 1996, 240, False), PlantingEvent("test_4", 1997, 125, False)],
     [PlantingEvent("test_3", 1996, 240, False), PlantingEvent("test_4", 1997, 125, False)],
     [PlantingEvent("test_1", 1996, 120, False), PlantingEvent("test_2", 1996, 120, False)]),
    ([PlantingEvent("crop_1", 1995, 100, True), PlantingEvent("crop_2", 1995, 100, False),
      PlantingEvent("crop_3", 1995, 100)], [],
     [PlantingEvent("crop_1", 1995, 100, True),
      PlantingEvent("crop_2", 1995, 100, False), PlantingEvent("crop_3", 1995, 100)]),
    ([PlantingEvent("not_today_1", 2000, 100, False), PlantingEvent("not_today_2", 2000, 250, True),
      PlantingEvent("not_today_3", 2001, 200, True)],
     [PlantingEvent("not_today_1", 2000, 100, False), PlantingEvent("not_today_2", 2000, 250, True),
      PlantingEvent("not_today_3", 2001, 200, True)], []),
    ([], [], [])
])
def test_check_crop_planting_schedule(all_events: List[PlantingEvent], events_remaining: List[PlantingEvent],
                                      events_occurring_today: List[PlantingEvent]) -> None:
    """
    Tests that the planting schedule is updated correctly and that planting events are executed correctly. This test
    contains four cases: some planting events occur on the current day, all planting events occur on the current day,
    no planting events occur on the current day, and no planting events left.
    """
    field = Field(plantings=all_events)
    field._create_and_update_events = MagicMock(return_value=(events_remaining, events_occurring_today))

    field.plant_crop = MagicMock()
    time = MagicMock(Time)
    expected_create_and_update_events_calls = [call(all_events, time)]
    expected_plant_crop_calls = []
    for event in events_occurring_today:
        expected_plant_crop_calls.append(call(event))

    field.check_crop_planting_schedule(time)

    field._create_and_update_events.assert_has_calls(expected_create_and_update_events_calls)
    field.plant_crop.assert_has_calls(expected_plant_crop_calls)
    assert field.planting_events == events_remaining


@pytest.mark.parametrize("events,year,day,expected_remaining,expected_current", [
    ([Event(1990, 120), Event(1990, 200), Event(1993, 100)], 1990, 120,
     [Event(1990, 200), Event(1993, 100)], [Event(1990, 120)]),
    ([PlantingEvent("corn", 1993, 120, False), PlantingEvent("corn_supplement", 1993, 120, True),
      PlantingEvent("cover_crop", 1993, 245, False)], 1993, 120, [PlantingEvent("cover_crop", 1993, 245, False)],
     [PlantingEvent("corn", 1993, 120, False), PlantingEvent("corn_supplement", 1993, 120, True)]),
    ([HarvestEvent("corn_1", 1999, 240, "default"), HarvestEvent("corn_1", 2000, 240, "default"),
      HarvestEvent("alfalfa_2", 2001, 240, "default")], 1999, 200,
     [HarvestEvent("corn_1", 1999, 240, "default"), HarvestEvent("corn_1", 2000, 240, "default"),
      HarvestEvent("alfalfa_2", 2001, 240, "default")], []),
    ([], 1993, 140, [], [])
])
def test_create_and_update_events(events: List[Event], year: int, day: int, expected_remaining: List[Event],
                                  expected_current: List[Event]) -> None:
    """Tests that list of events are properly checked and have current events correctly removed from them."""
    mocked_time = MagicMock(Time)
    setattr(mocked_time, "calendar_year", year)
    setattr(mocked_time, "day", day)

    actual = Field._create_and_update_events(events, mocked_time)
    assert actual[0] == expected_remaining
    assert actual[1] == expected_current


@pytest.mark.parametrize("daylength,threshold_daylength", [
    (14, 8),
    (17.20948239, 9.19183294),
    (7.293485893, 8.234850920),
])
def test_start_dormancy(daylength: float, threshold_daylength: float) -> None:
    """Tests that each crop's dormancy method is called"""
    # Initialize objects
    crop = Crop()
    field = Field()
    field.field_data.dormancy_threshold_daylength = threshold_daylength
    field.crops = [crop]

    # Mock functions used
    crop.dormancy.enter_dormancy = MagicMock()

    # Run method being tested
    field.assess_dormancy(daylength)

    # Check that subroutines were called correct number of times
    if daylength <= threshold_daylength:
        assert crop.dormancy.enter_dormancy.call_count == 1


@pytest.mark.parametrize("species,specs", [
    ("corn", {}),  # no additional arguments
    ("alfalfa", {"minimum_temperature": -2.1, "id": 123})  # supported species, with alteration
])
def test_make_supported_crop(species: str, specs: dict):
    """ensure that supported crops are properly created."""
    # check that attributes are correct
    crop = Field.make_supported_crop(species, **specs)
    assert crop.data.species == species
    for key, val in specs.items():
        assert getattr(crop.data, key) == val

    if len(specs) > 0:
        assert "altered" in crop.data.name
    else:
        assert "default" in crop.data.name

    # failing cases
    with pytest.raises(Exception):
        Field.make_supported_crop("fake_crop")
    with pytest.raises(Exception):
        Field.make_supported_crop("corn", bad_attr=17.35)


@pytest.mark.parametrize("config", [
    {"species": "grass"},  # custom species, with generic defaults
    {"species": "cottonwood", "is_perennial": True},  # custom species and attribute
    {"minimum_temperature": -10},  # no species name
])
def test_make_custom_crop(config: dict):
    """checks that custom crop attributes are set correctly"""
    crop = Field.make_custom_crop(**config)
    for key, val in config.items():
        assert getattr(crop.data, key) == val


@pytest.mark.parametrize("config", [
    {"species": "corn"},  # supported species
    {"species": "corn", "minimum_temperature": -2.0, "is_perennial": True},  # supported species, with alterations
    {"species": "grass"},  # unsupported species, generic attributes
    {"species": "cottonwood", "is_perennial": True},  # custom species and attributes
    {"minimum_temperature": -2.0},  # generic custom crop, with alterations
])
def test_make_crop_from_config_dict(config: dict):
    supported_crops = set(item.value for item in CropSpecies)
    has_supported_species = "species" in config.keys() and str(config["species"]) in supported_crops
    Field.make_supported_crop = MagicMock()
    Field.make_custom_crop = MagicMock()

    Field.make_crop_from_config_dict(config)

    if has_supported_species:
        Field.make_supported_crop.assert_called_once()
        Field.make_custom_crop.assert_not_called()
    else:
        Field.make_supported_crop.assert_not_called()
        Field.make_custom_crop.assert_called_once()


def test_check_harvest_schedules():
    """ensure that harvest schedules are checked for all crops"""
    field = Field()
    crop1, crop2, crop3 = Crop(), Crop(), Crop()
    crop1.crop_management.check_harvest_schedule = MagicMock()
    crop2.crop_management.check_harvest_schedule = MagicMock()
    crop3.crop_management.check_harvest_schedule = MagicMock()
    field.crops = [crop1, crop2, crop3]
    field.check_harvest_schedules(100, 0)
    crop1.crop_management.check_harvest_schedule.assert_called_once_with(current_day=100, current_year=0)
    crop2.crop_management.check_harvest_schedule.assert_called_once_with(current_day=100, current_year=0)
    crop3.crop_management.check_harvest_schedule.assert_called_once_with(current_day=100, current_year=0)


def test_harvest_scheduled_crops():
    """ensure that crops are harvested when appropriate"""
    field = Field()
    crop1, crop2, crop3 = Crop(CropData(is_harvest_day=True)), Crop(CropData(is_harvest_day=False)), \
        Crop(CropData(is_harvest_day=True))
    crop1.crop_management.manage_harvest = MagicMock()
    crop2.crop_management.manage_harvest = MagicMock()
    crop3.crop_management.manage_harvest = MagicMock()
    field.crops = [crop1, crop2, crop3]
    field.harvest_scheduled_crops()
    crop1.crop_management.manage_harvest.assert_called_once()
    crop2.crop_management.manage_harvest.assert_not_called()
    crop3.crop_management.manage_harvest.assert_called_once()


def test_amend_soil() -> None:
    """Tests that amend_soil() properly calls all the subroutines that add nutrients to the field"""
    field = Field()
    field.soil.phosphorus_cycling.fertilizer.add_fertilizer_phosphorus = MagicMock()
    field.amend_soil()
    field.soil.phosphorus_cycling.fertilizer.add_fertilizer_phosphorus.assert_called_once_with(0)


@pytest.mark.parametrize("field_size,crops_growing,residue,light,mean_temp,min_temp,max_temp,annual_mean_temp,"
                         "transpiration", [
                             (1.5, False, 34.5, 128, 22.5, 18.9, 25.6, 19.22, 5.2),
                             (2.4, True, 40.9, 150, 28, 24.55, 31.2, 17.9, 3.44),
                             (0.8, True, 12.22, 222, 18.7, 13.44, 23.44, 16.4, 1.33)
                         ])
def test_execute_daily_processes(field_size: float, crops_growing: bool, residue: float, light: float, mean_temp: float,
                                 min_temp: float, max_temp: float, annual_mean_temp: float,
                                 transpiration: float) -> None:
    """Tests that all component processes and subroutines are correctly called in Field."""
    with patch("SC_redesign.Crop_and_Soil.crop.crop_data.CropData.in_growing_season", new_callable=PropertyMock,
               return_value=crops_growing):
        field_data = FieldData(field_size=field_size, current_residue=residue)
        incorp = Field(field_data=field_data)
        crop_1 = Crop()
        crop_1.data.max_transpiration = transpiration
        crop_2 = Crop()
        crop_2.data.max_transpiration = transpiration
        incorp.crops = [crop_1, crop_2]
        current_weather = CurrentWeather(incoming_light=light, mean_air_temperature=mean_temp,
                                         min_air_temperature=min_temp, max_air_temperature=max_temp,
                                         annual_mean_air_temperature=annual_mean_temp)

        incorp._determine_total_above_ground_biomass = MagicMock(return_value=89)
        incorp.soil.soil_temp.daily_soil_temperature_update = MagicMock()
        incorp._cycle_water = MagicMock()
        for crop in incorp.crops:
            crop.heat_units.absorb_heat_units = MagicMock()
            crop.root_development = MagicMock()
            crop.nitrogen_incorporation.incorporate_nitrogen = MagicMock()
            crop.phosphorus_incorporation.incorporate_phosphorus = MagicMock()
            crop.growth_constraints.constrain_growth = MagicMock()
            crop.leaf_area_index.grow_canopy = MagicMock()
            crop.biomass_allocation.allocate_biomass = MagicMock()

        incorp._execute_daily_processes(current_weather)

        incorp._determine_total_above_ground_biomass.assert_called_once()
        incorp.soil.soil_temp.daily_soil_temperature_update.assert_called_once_with(light, mean_temp, min_temp,
                                                                                    max_temp, 89 + residue, 0,
                                                                                    annual_mean_temp)
        incorp._cycle_water.assert_called_once_with(current_weather)
        for crop in incorp.crops:
            if crops_growing:
                crop.heat_units.absorb_heat_units.assert_called_once_with(mean_temp, min_temp, max_temp)
                crop.root_development.develop_roots.assert_called_once()
                crop.nitrogen_incorporation.incorporate_nitrogen.assert_called_once_with(incorp.soil.data)
                crop.phosphorus_incorporation.incorporate_phosphorus.assert_called_once_with(incorp.soil.data)
                crop.growth_constraints.constrain_growth.assert_called_once_with(transpiration, mean_temp)
                crop.leaf_area_index.grow_canopy.assert_called_once()
                crop.biomass_allocation.allocate_biomass.assert_called_once_with(light)
            else:
                crop.heat_units.absorb_heat_units.assert_not_called()
                crop.root_development.develop_roots.assert_not_called()
                crop.nitrogen_incorporation.incorporate_nitrogen.assert_not_called()
                crop.phosphorus_incorporation.incorporate_phosphorus.assert_not_called()
                crop.growth_constraints.constrain_growth.assert_not_called()
                crop.leaf_area_index.grow_canopy.assert_not_called()
                crop.biomass_allocation.allocate_biomass.assert_not_called()


@pytest.mark.parametrize("field_size,rainfall,runoff,high_water_table,residue,light,min_temp,max_temp,mean_temp,"
                         "surface_residue,crop_1_proportion,crop_2_proportion,crops_growing", [
                             (1.9, 4.66, 1.22, False, 30.6, 200, 16.5, 20.5, 18.5, 44.5, 0.6, 0.4, True),
                             (2.3, 5.6, 2.1, True, 44.5, 250, 22.33, 25.36, 24.6, 80.4, 0.77, 0.23, False)
                         ])
def test_cycle_water(field_size: float, rainfall: float, runoff: float, high_water_table: bool, residue: float,
                     light: float, min_temp: float, max_temp: float, mean_temp: float, surface_residue: float,
                     crop_1_proportion: float, crop_2_proportion: float, crops_growing: bool) -> None:
    """Tests that cycle_water() correctly executes all water processes on its soil profile and the crops it contains."""
    with patch("SC_redesign.Crop_and_Soil.crop.crop_data.CropData.in_growing_season", new_callable=PropertyMock,
               return_value=crops_growing):
        soil_data = SoilData(field_size=field_size, accumulated_runoff=runoff, water_evaporated=3.5)
        soil_data.plant_surface_residue = surface_residue
        soil = Soil(soil_data)
        crop_data_1 = CropData(field_proportion=crop_1_proportion, max_transpiration=44.1, cumulative_evaporation=105.5,
                               cumulative_transpiration=205.1, cumulative_potential_evapotranspiration=400.19,
                               total_water_uptake=3.5)
        crop_1 = Crop(crop_data_1)
        crop_data_2 = CropData(field_proportion=crop_2_proportion, max_transpiration=39.5, cumulative_evaporation=112.4,
                               cumulative_transpiration=219.2, cumulative_potential_evapotranspiration=480.1,
                               total_water_uptake=3.25)
        crop_2 = Crop(crop_data_2)
        current_weather = CurrentWeather(incoming_light=light, min_air_temperature=min_temp, rainfall=rainfall,
                                         max_air_temperature=max_temp, mean_air_temperature=mean_temp)
        field_data = FieldData(field_size=field_size, current_residue=residue,
                               seasonal_high_water_table=high_water_table)
        incorp = Field(field_data, soil)
        incorp.crops = [crop_1, crop_2]

        incorp.soil.infiltration.infiltrate = MagicMock()
        incorp.soil.percolation.percolate = MagicMock()
        incorp.soil.soil_erosion.erode = MagicMock()
        incorp.soil.phosphorus_cycling.cycle_phosphorus = MagicMock()
        incorp.soil.nitrogen_cycling.cycle_nitrogen = MagicMock()
        incorp.soil.carbon_cycling.cycle_carbon = MagicMock()
        incorp.soil.evaporation.evaporate = MagicMock()

        incorp._determine_watering_amount = MagicMock(return_value=0)
        incorp._handle_water_in_crop_canopies = MagicMock(return_value=2.0)
        incorp._determine_potential_evapotranspiration = MagicMock(return_value=33.5)
        incorp._evaporate_from_crop_canopies = MagicMock(return_value=30.5)
        incorp._determine_total_above_ground_biomass = MagicMock(return_value=40.0)
        incorp._determine_soil_evaporation_and_sublimation_adjusted = MagicMock(return_value=10.5)

        crop_1.water_dynamics.set_maximum_transpiration = MagicMock()
        crop_1.water_dynamics.cycle_water = MagicMock()
        crop_1.water_uptake.uptake_water = MagicMock()
        crop_2.water_dynamics.set_maximum_transpiration = MagicMock()
        crop_2.water_dynamics.cycle_water = MagicMock()
        crop_2.water_uptake.uptake_water = MagicMock()

        incorp._cycle_water(current_weather)

        incorp._determine_watering_amount.assert_called_once_with(rainfall)
        incorp._handle_water_in_crop_canopies.assert_called_once_with(rainfall)
        incorp._determine_potential_evapotranspiration.assert_called_once_with(light, max_temp, min_temp, mean_temp)
        incorp._evaporate_from_crop_canopies.assert_called_once_with(33.5)
        incorp.soil.infiltration.infiltrate.assert_called_once_with(2.0, 1, 33.5)
        incorp.soil.percolation.percolate.assert_called_once_with(high_water_table)
        incorp.soil.soil_erosion.erode.assert_called_once_with(field_size, 0.02, residue)
        incorp.soil.phosphorus_cycling.cycle_phosphorus.assert_called_once_with(2.0, runoff, field_size, mean_temp)
        incorp.soil.nitrogen_cycling.cycle_nitrogen.assert_called_once_with(field_size)
        incorp.soil.carbon_cycling.cycle_carbon.assert_called_once_with(2.0, mean_temp, field_size)
        expected_remaining_demand = 30.5
        crop_1.water_dynamics.set_maximum_transpiration.assert_called_once_with(expected_remaining_demand)
        crop_2.water_dynamics.set_maximum_transpiration.assert_called_once_with(expected_remaining_demand)
        expected_average_transpiration = 44.1 * crop_1_proportion + 39.5 * crop_2_proportion
        incorp._determine_soil_evaporation_and_sublimation_adjusted.assert_called_once_with(
            40.0, surface_residue, 0, expected_remaining_demand, expected_average_transpiration)
        incorp.soil.evaporation.evaporate.assert_called_once_with(10.5)
        expected_actual_evaporation = 33.5 - (expected_remaining_demand - 3.5)
        if crops_growing:
            crop_1.water_uptake.uptake_water.assert_called_once_with(incorp.soil)
            crop_1.water_dynamics.cycle_water.assert_called_once_with(expected_actual_evaporation, 3.5, 33.5)
            crop_2.water_uptake.uptake_water.assert_called_once_with(incorp.soil)
            crop_2.water_dynamics.cycle_water.assert_called_once_with(expected_actual_evaporation, 3.25, 33.5)
        else:
            assert crop_1.data.cumulative_evaporation == 0
            assert crop_1.data.cumulative_transpiration == 0
            assert crop_1.data.cumulative_potential_evapotranspiration == 0
            assert crop_2.data.cumulative_evaporation == 0
            assert crop_2.data.cumulative_transpiration == 0
            assert crop_2.data.cumulative_potential_evapotranspiration == 0


@pytest.mark.parametrize("rainfall,days_into_interval,water_deficit,watering_occurs", [
    (3.4, 3, 1.5, False),  # No watering because water_occurs is False
    (3.1, 5, 2.3, True),  # No watering because rainfall takes care of watering
    (0.2, 5, 3.6, True),  # Watering occurs because water deficit has not been met
    (0.19, 4, 2.8, True)  # No watering occurs because interval has not been met
])
def test_determine_watering_amount(rainfall: float, days_into_interval: int, water_deficit: float,
                                   watering_occurs: float) -> None:
    """Tests that the correct amount of water to be used to water is field is calculated, and that the counters and
        totals are updated correctly."""
    data = FieldData(watering_amount_in_liters=50_000, watering_interval=5,
                     days_into_watering_interval=days_into_interval)
    data.watering_amount_in_mm = 5.0
    data.watering_occurs = watering_occurs
    data.current_water_deficit = water_deficit
    incorp = Field(field_data=data)

    actual = incorp._determine_watering_amount(rainfall)

    if not watering_occurs:
        assert actual == 0.0
        assert incorp.field_data.days_into_watering_interval == days_into_interval
        assert incorp.field_data.annual_irrigation_water_use_total == 0
    elif days_into_interval == incorp.field_data.watering_interval:
        assert actual == max(0.0, water_deficit - rainfall)
        assert incorp.field_data.days_into_watering_interval == 0
        assert incorp.field_data.current_water_deficit == 5.0
        assert incorp.field_data.annual_irrigation_water_use_total == actual
    else:
        assert actual == 0.0
        assert incorp.field_data.days_into_watering_interval == days_into_interval + 1
        assert incorp.field_data.current_water_deficit == max(0.0, water_deficit - rainfall)
        assert incorp.field_data.annual_irrigation_water_use_total == 0


@pytest.mark.parametrize("precipitation,canopy_capacity,first_canopy_amount,second_canopy_amount,expected_return,"
                         "expected_first,expected_second", [
                             (13, 8, 2, 4, 3, 8, 8),  # Fills both pools with some leftover
                             (6, 7, 3, 2, 0, 7, 4),  # Fills one pool, puts some in second, none leftover
                             (14, 5, 7, 1, 12, 5, 5),  # Removes from one pool, fills other, some leftover
                             (3, 6, 8, 9, 8, 6, 6),  # Removes from both pools, lots left over
                             (5, 10, 3, 12, 2, 8, 10)  # Fills one pool as much as possible, removes excess from
                             # another
                         ]
                         )
def test_handle_water_in_crop_canopies(precipitation: float, canopy_capacity: float, first_canopy_amount: float,
                                       second_canopy_amount: float, expected_return: float, expected_first: float,
                                       expected_second: float) -> None:
    """Tests that water is properly added and removed from the crop canopies of field objects."""
    with patch("SC_redesign.Crop_and_Soil.crop.crop_data.CropData.water_canopy_storage_capacity",
               new_callable=PropertyMock, return_value=canopy_capacity):
        crop_data1 = CropData(canopy_water=first_canopy_amount)
        crop1 = Crop(crop_data1)
        crop_data2 = CropData(canopy_water=second_canopy_amount)
        crop2 = Crop(crop_data2)
        field = Field()
        field.crops = [crop1, crop2]

        actual = field._handle_water_in_crop_canopies(precipitation)
        assert actual == expected_return
        assert field.crops[0].data.canopy_water == expected_first
        assert field.crops[1].data.canopy_water == expected_second


@pytest.mark.parametrize("demand,canopy_water_1,canopy_water_2,expected_demand,expected_canopy_water1,"
                         "expected_canopy_water2", [
                             (14.5, 1.8, 2.3, 10.4, 0.0, 0.0),
                             (8.6, 4.7, 4.1, 0.0, 0.0, 0.2),
                             (9.5, 10.8, 5.7, 0.0, 1.3, 5.7)
                         ])
def test_evaporate_from_crop_canopies(demand: float, canopy_water_1: float, canopy_water_2: float,
                                      expected_demand: float, expected_canopy_water1: float,
                                      expected_canopy_water2: float) -> None:
    """Tests that the evapotranspirative demand is correctly reduced by the amounts of water evaporated."""
    data1 = CropData(canopy_water=canopy_water_1)
    crop1 = Crop(data1)
    data2 = CropData(canopy_water=canopy_water_2)
    crop2 = Crop(data2)
    field = Field()
    field.crops = [crop1, crop2]

    actual_demand = field._evaporate_from_crop_canopies(demand)
    assert pytest.approx(actual_demand) == expected_demand
    assert pytest.approx(expected_canopy_water1) == field.crops[0].data.canopy_water
    assert pytest.approx(expected_canopy_water2) == field.crops[1].data.canopy_water


@pytest.mark.parametrize("extraterrestrial_radiation,max_temp,min_temp,avg_temp", [
    (100, 28, 10, 14),
    (568, 20, 14, 18),
    (568, 20, 14, None),
    (80, 14, 0, 8),
    (678.0098, 26.8896, 10.3339, 18.3345),
])
def test_potential_evapotranspiration(extraterrestrial_radiation, max_temp, min_temp, avg_temp):
    with patch("SC_redesign.Crop_and_Soil.field.field.Field._determine_latent_heat_vaporization",
               new_callable=MagicMock, return_value=1.3) as mocked_latent_heat:
        actual = Field._determine_potential_evapotranspiration(extraterrestrial_radiation, max_temp, min_temp, avg_temp)
        if avg_temp is not None:
            expect = (0.0023 * extraterrestrial_radiation * ((max_temp - min_temp) ** (-0.5)) *
                      (avg_temp + 17.8)) / 1.3
        else:
            expect = (0.0023 * extraterrestrial_radiation * ((max_temp - min_temp) ** (-0.5)) *
                      (((max_temp + min_temp) / 2) + 17.8)) / 1.3

        if avg_temp is not None:
            mocked_latent_heat.assert_called_once_with(avg_temp)
        else:
            mocked_latent_heat.assert_called_once_with((max_temp + min_temp) / 2)
        assert actual == expect


@pytest.mark.parametrize("avg_temp", [
    12.86878,
    0,
    (-2.586948),
    20.4486,
])
def test_determine_latent_heat_vaporization(avg_temp):
    observe = Field._determine_latent_heat_vaporization(avg_temp)
    expect = 2.501 - (0.002361 * avg_temp)
    assert expect == observe


@pytest.mark.parametrize("above_ground_biomass,residue,snow_water,potential_evapotrans_adj, transpiration", [
    (800, 40, 0.3, 1.6, 0.9),  # arbitrary
    (1200, 300, 0.433, 2.4, 1.8),  # arbitrary
    (0, 800, 0.03, 0, 3.6),  # after harvest
    (800, 56, 0.84, 0.44, 0.23),  # snowy
    (0, 0, 0.22, 0.69, 0.45),  # empty field
    (400, 150, 0, 0.01, 0),  # dry conditions
    (500, 200, 0, 6.3, 4.5),  # wet conditions
])
def test_determine_soil_evaporation_and_sublimation_adjusted(above_ground_biomass: float, residue: float,
                                                             snow_water: float, potential_evapotrans_adj: float,
                                                             transpiration: float) -> None:
    """Tests that the amount of soil evaporation and sublimation is calculated correctly."""
    with patch("SC_redesign.Crop_and_Soil.field.field.Field._determine_soil_cover_index", new_callable=MagicMock,
               return_value=1.3) as mocked_soil_cover_index:
        actual = Field._determine_soil_evaporation_and_sublimation_adjusted(above_ground_biomass, residue, snow_water,
                                                                            potential_evapotrans_adj, transpiration)
        soil_evaporation = potential_evapotrans_adj * 1.3
        reduced_soil_evaporation = (soil_evaporation * potential_evapotrans_adj) / (soil_evaporation + transpiration)
        expected = min(soil_evaporation, reduced_soil_evaporation)

        mocked_soil_cover_index.assert_called_once_with(above_ground_biomass, residue, snow_water)
        assert actual == expected


@pytest.mark.parametrize("above_ground_biomass,residue,snow_water", [
    (400, 65, 0.3),
    (800, 120, 0),
    (0, 0, 0),
    (1250, 800, 0.4999),
    (990, 200, 0.338),
    (400, 30, 0.51),
])
def test_determine_soil_cover_index(above_ground_biomass: float, residue: float, snow_water: float) -> None:
    """Tests that the soil cover index is correctly calculated."""
    if snow_water > 0.5:
        expect = 0.5
    else:
        expect = exp((-0.00005) * (above_ground_biomass + residue))
    observe = Field._determine_soil_cover_index(above_ground_biomass, residue, snow_water)
    assert expect == observe


@pytest.mark.parametrize("soil_evaporation_adj,snow_water_content", [
    (1.3, 3.2),
    (0, 0),
    (1.3, 0.4),
    (1.8954, 0)
])
def test_determine_maximum_soil_evaporation(soil_evaporation_adj, snow_water_content):
    observe = Field._determine_maximum_soil_evaporation(soil_evaporation_adj, snow_water_content)
    if snow_water_content > soil_evaporation_adj:
        assert 0 == observe
    else:
        assert (soil_evaporation_adj - snow_water_content) == observe


def test_annual_reset() -> None:
    """Tests that all annual reset subroutines are called properly"""
    field = Field()
    field.soil.data.do_annual_reset = MagicMock()
    field.field_data.perform_annual_field_reset = MagicMock()

    field.perform_annual_reset()

    field.soil.data.do_annual_reset.assert_called_once()
    field.field_data.perform_annual_field_reset.assert_called_once()


# TODO: All field methods need to be tested in future PRs.


# --- Test FieldData methods ---
@pytest.mark.parametrize("liters,area", [
    (100, 2.3),
    (356, 4.556),
    (60, 1.8)
])
def test_liters_to_millimeters(liters: float, area: float) -> None:
    """Tests that the conversion from liters for evenly distributed millimeters is performed correctly."""
    actual = FieldData.convert_liters_to_millimeters(liters, area)
    expected = (liters * LITERS_TO_CUBIC_MILLIMETERS) / (area * HECTARES_TO_SQUARE_MILLIMETERS)
    assert actual == expected


@pytest.mark.parametrize("latitude,min_daylength,watering_amount,watering_interval", [
    (45.66, 12.5, 2000, 3),
    (37.445, 9.88, 7500, 7),
    (50.667, 10.334, 0, 5),
    (49.551, 12.65, 3500, 0)
])
def test_field_data_initialization(latitude: float, min_daylength: float, watering_amount: float,
                                   watering_interval: int) -> None:
    """Tests that FieldData objects are initialized correctly."""
    Dormancy.find_dormancy_threshold = MagicMock(return_value=14.5)
    Dormancy.find_threshold_daylength = MagicMock(return_value=10.22)
    FieldData.convert_liters_to_millimeters = MagicMock(return_value=0.8)

    data = FieldData(field_size=3, absolute_latitude=latitude, minimum_daylength=min_daylength,
                     watering_amount_in_liters=watering_amount, watering_interval=watering_interval)

    Dormancy.find_dormancy_threshold.assert_called_once_with(latitude)
    Dormancy.find_threshold_daylength.assert_called_once_with(min_daylength, 14.5)
    assert data.dormancy_threshold == 14.5
    assert data.dormancy_threshold_daylength == 10.22
    if watering_amount is not None and watering_amount != 0.0 and watering_interval is not None and \
            watering_interval != 0:
        FieldData.convert_liters_to_millimeters.assert_called_once_with(watering_amount, 3)
        assert data.watering_amount_in_mm == 0.8
        assert data.current_water_deficit == 0.8
        assert data.watering_occurs
    else:
        FieldData.convert_liters_to_millimeters.assert_not_called()
        assert data.watering_amount_in_mm == 0
        assert data.current_water_deficit == 0
        assert not data.watering_occurs


@pytest.mark.parametrize("watering_amount,interval", [
    (-1300, 13),
    (2000, -3)
])
def test_error_field_data_initialization(watering_amount: float, interval: int) -> None:
    """Tests that errors are correctly raised when FieldData is initialized with invalid values."""
    with pytest.raises(Exception) as e:
        FieldData(watering_amount_in_liters=watering_amount, watering_interval=interval)
    if watering_amount < 0:
        assert f"Expected watering amount to be >= 0, received '{watering_amount}'." == str(e.value)
    elif interval < 0:
        assert f"Expected watering interval to be >= 0, received '{interval}'." == str(e.value)
