import pytest
from pytest import approx
from pytest_mock import MockerFixture

from RUFAS.time import Time
from RUFAS.weather import Weather
from RUFAS.general_constants import GeneralConstants
from RUFAS.routines.manure.beddings.bedding_classes import BaseBedding
from RUFAS.routines.manure.manure_handlers.manure_handler_classes import (
    AlleyScraper,
    Tillage,
    Harrowing,
)
from RUFAS.routines.manure.manure_handlers.manure_handler_classes import (
    BaseManureHandler,
)
from RUFAS.routines.manure.manure_handlers.manure_handler_classes import FlushSystem
from RUFAS.routines.manure.manure_handlers.manure_handler_classes import ManualScraping
from RUFAS.routines.manure.manure_handlers.manure_handler_classes import (
    ManureHandlerConfig,
)
from RUFAS.routines.manure.manure_handlers.manure_handler_classes import (
    ManureHandlerFactory,
)
from RUFAS.routines.manure.manure_handlers.manure_handler_classes import (
    ManureHandlerType,
)
from RUFAS.routines.manure.manure_handlers.manure_handler_daily_output import (
    ManureHandlerDailyOutput,
)
from RUFAS.routines.manure.manure_handlers.milking_parlor import MilkingParlor
from RUFAS.routines.manure.pen_manure.manure_manager_pen import ManureManagerPen
from RUFAS.routines.manure.pen_manure.pen_manure import PenManure


# Test ManureHandlerDailyOutput
# ============================


@pytest.mark.parametrize(
    "input_values, expected_values",
    [
        # Default values
        (
            {},
            {
                "pen_id": -1,
                "simulation_day": -1,
                "manure_urea": 0.0,
                "liquid_manure_total_ammoniacal_nitrogen": 0.0,
                "liquid_manure_nitrogen": 0.0,
                "liquid_manure_total_solids": 0.0,
                "liquid_manure_total_degradable_volatile_solids": 0.0,
                "liquid_manure_total_non_degradable_volatile_solids": 0.0,
                "liquid_manure_total_volatile_solids": 0.0,
                "liquid_manure_phosphorus": 0.0,
                "housing_methane": 0.0,
                "housing_carbon_dioxide": 0.0,
                "housing_ammonia": 0.0,
                "manure_volume": 0.0,
                "cleaning_water_volume": 0.0,
                "total_bedding_volume": 0.0,
                "total_bedding_mass": 0.0,
                "total_water_volume_in_milking_parlor": 0.0,
                "liquid_manure_daily_volume": 0.0,
                "tempC": 0.0,
            },
        ),
        # Assign a value to each attribute in the initializer
        (
            {
                "pen_id": 1,
                "simulation_day": 1,
                "manure_urea": 1.0,
                "liquid_manure_total_ammoniacal_nitrogen": 2.0,
                "liquid_manure_nitrogen": 3.0,
                "liquid_manure_total_solids": 4.0,
                "liquid_manure_total_degradable_volatile_solids": 5.0,
                "liquid_manure_total_non_degradable_volatile_solids": 6.0,
                "liquid_manure_phosphorus": 7.0,
                "liquid_manure_potassium": 8.0,
                "housing_methane": 9.0,
                "housing_carbon_dioxide": 10.0,
                "housing_ammonia": 11.0,
                "manure_volume": 14.0,
                "cleaning_water_volume": 15.0,
                "total_bedding_volume": 16.0,
                "total_bedding_mass": 17.0,
                "total_water_volume_in_milking_parlor": 18.0,
                "tempC": 19.0,
            },
            {
                "pen_id": 1,
                "simulation_day": 1,
                "manure_urea": approx(1.0),
                "liquid_manure_total_ammoniacal_nitrogen": approx(2.0),
                "liquid_manure_nitrogen": approx(3.0),
                "liquid_manure_total_solids": approx(4.0),
                "liquid_manure_total_degradable_volatile_solids": approx(5.0),
                "liquid_manure_total_non_degradable_volatile_solids": approx(6.0),
                "liquid_manure_total_volatile_solids": approx(5.0 + 6.0),
                "liquid_manure_phosphorus": approx(7.0),
                "liquid_manure_potassium": approx(8.0),
                "housing_methane": approx(9.0),
                "housing_carbon_dioxide": approx(10.0),
                "housing_ammonia": approx(11.0),
                "manure_volume": approx(14.0),
                "cleaning_water_volume": approx(0.015),
                "total_bedding_volume": approx(16.0),
                "total_bedding_mass": approx(17.0),
                "total_water_volume_in_milking_parlor": approx(0.018),
                "total_daily_manure_volume": approx(30.033),
                "liquid_manure_daily_volume": approx(30.033),
                "tempC": approx(19.0),
            },
        ),
    ],
)
def test_manure_handler_daily_output(input_values, expected_values) -> None:
    """Unit test for __init__() of class ManureHandlerDailyOutput in file manure_handler_daily_output.py"""

    # Act
    manure_handler_daily_output = ManureHandlerDailyOutput(**input_values)

    # Assert
    for attribute, expected_value in expected_values.items():
        assert (
            getattr(manure_handler_daily_output, attribute) == expected_value
        ), f"Attribute {attribute} is not equal to {expected_value}."


def test_manure_handler_config() -> None:
    """Unit test for class ManureHandlerConfig in file manure_handler_classes.py."""
    # Arrange
    manure_handler_type = ManureHandlerType.FLUSH_SYSTEM
    cleaning_water_use_rate = 20.0
    minutes_per_cleaning = 10
    cleanings_per_day = 3
    daily_tillage_frequency = 1
    cleaning_water_recycle_fraction = 0.1

    # Act
    manure_handler_config = ManureHandlerConfig(
        manure_handler_type=manure_handler_type,
        cleaning_water_use_rate=cleaning_water_use_rate,
        minutes_per_cleaning=minutes_per_cleaning,
        cleanings_per_day=cleanings_per_day,
        daily_tillage_frequency=daily_tillage_frequency,
        cleaning_water_recycle_fraction=cleaning_water_recycle_fraction,
    )

    # Assert
    assert manure_handler_config.manure_handler_type == ManureHandlerType.FLUSH_SYSTEM
    assert manure_handler_config.cleaning_water_use_rate == approx(cleaning_water_use_rate)
    assert manure_handler_config.minutes_per_cleaning == minutes_per_cleaning
    assert manure_handler_config.cleanings_per_day == cleanings_per_day
    assert manure_handler_config.daily_tillage_frequency == daily_tillage_frequency
    assert manure_handler_config.cleaning_water_recycle_fraction == approx(cleaning_water_recycle_fraction)


# Test ManureHandlerType
# ======================


def test_manure_handler_type_enum() -> None:
    """Unit test for enum ManureHandlerType"""

    # Assert
    assert ManureHandlerType("flush system") is ManureHandlerType.FLUSH_SYSTEM
    assert ManureHandlerType("manual scraping") is ManureHandlerType.MANUAL_SCRAPING
    assert ManureHandlerType("alley scraper") is ManureHandlerType.ALLEY_SCRAPER
    assert ManureHandlerType("tillage") is ManureHandlerType.TILLAGE
    assert ManureHandlerType("harrowing") is ManureHandlerType.HARROWING


# Test ManureHandlerFactory
# =========================


@pytest.mark.parametrize(
    "manure_handler_type_name,manure_handler_type,expected_manure_handler_class",
    [
        ("flush system", ManureHandlerType.FLUSH_SYSTEM, FlushSystem),
        ("alley scraper", ManureHandlerType.ALLEY_SCRAPER, AlleyScraper),
        ("manual_scraping", ManureHandlerType.MANUAL_SCRAPING, ManualScraping),
        ("tillage", ManureHandlerType.TILLAGE, Tillage),
        ("harrowing", ManureHandlerType.HARROWING, Harrowing),
    ],
)
def test_manure_handler_factory_get_manure_handler(
    manure_handler_type_name: str,
    manure_handler_type: ManureHandlerType,
    expected_manure_handler_class: BaseManureHandler,
    mocker: MockerFixture,
) -> None:
    """Unit test for get_instance() of class ManureHandlerFactory"""
    # Arrange
    weather = mocker.MagicMock()
    time = mocker.MagicMock()
    milking_parlor = mocker.MagicMock()
    patch_for_milking_parlor_init = mocker.patch(
        "RUFAS.routines.manure.manure_handlers.manure_handler_classes.MilkingParlor",
        return_value=milking_parlor,
    )
    manure_handler_config = ManureHandlerConfig(
        manure_handler_type=manure_handler_type,
        cleaning_water_use_rate=20.0,
        minutes_per_cleaning=10,
        cleanings_per_day=3,
        daily_tillage_frequency=0,
        cleaning_water_recycle_fraction=0.80,
    )

    # Act
    manure_handler = ManureHandlerFactory.get_manure_handler(
        weather=weather,
        time=time,
        configuration_name=manure_handler_type_name,
        manure_handler_config=manure_handler_config,
    )

    # Assert
    assert type(manure_handler) is expected_manure_handler_class
    assert manure_handler.config == manure_handler_config
    patch_for_milking_parlor_init.assert_called_once()
    assert manure_handler.milking_parlor == milking_parlor
    assert manure_handler.weather == weather
    assert manure_handler.time == time


# Test BaseManureHandler
# ======================


def test_calc_cleaning_water_volume_in_main_barn(mocker: MockerFixture) -> None:
    """Unit test for calc_cleaning_water_volume_in_main_barn() in file manure_handler_classes.py"""
    # Arrange
    num_animals = 100
    cleaning_water_use_rate = 20.0
    cleaning_water_recycle_fraction = 0.75
    expected_cleaning_water_volume_in_main_barn = (
        num_animals * cleaning_water_use_rate * (1 - cleaning_water_recycle_fraction)
    )
    mock_manure_handler_config = mocker.MagicMock(auto_spec=ManureHandlerConfig)
    mock_manure_handler_config.cleaning_water_use_rate = cleaning_water_use_rate
    mock_manure_handler_config.cleaning_water_recycle_fraction = cleaning_water_recycle_fraction
    mock_manure_handler = BaseManureHandler(
        weather=mocker.MagicMock(),
        time=mocker.MagicMock(),
        manure_handler_config=mock_manure_handler_config,
        name="test",
    )

    # Act
    cleaning_water_volume_in_main_barn = mock_manure_handler.calc_cleaning_water_volume_in_main_barn(
        num_animals=num_animals
    )

    # Assert
    assert cleaning_water_volume_in_main_barn == expected_cleaning_water_volume_in_main_barn


def test_get_current_day_avg_temperature_celsius(mocker: MockerFixture) -> None:
    # Arrange
    expected_current_day_avg_tempC = 42.0
    mock_time = mocker.MagicMock(auto_spec=Time)
    mock_time.year = 10
    mock_time.day = 1
    mock_current_day_conditions = mocker.MagicMock()
    setattr(
        mock_current_day_conditions,
        "mean_air_temperature",
        expected_current_day_avg_tempC,
    )
    mock_weather = mocker.MagicMock(auto_spec=Weather)
    mock_weather.get_current_day_conditions.return_value = mock_current_day_conditions

    mock_manure_handler = BaseManureHandler(
        weather=mock_weather,
        time=mock_time,
        manure_handler_config=mocker.MagicMock(auto_spec=ManureHandlerConfig),
        name="test",
    )

    # Act
    current_day_avg_tempC = mock_manure_handler._get_current_day_average_temperature_in_celsius()

    # Assert
    assert current_day_avg_tempC == expected_current_day_avg_tempC


def test_manure_handler_daily_update(mocker: MockerFixture) -> None:
    """
    Unit test for daily_update() of class BaseManureHandler in file manure_handler_classes.py

    This test verifies that output from a manure handler is properly calculated and gathered.

    """

    # Arrange
    mock_manure = mocker.MagicMock(autospec=PenManure)
    mock_manure.manure_total_ammoniacal_nitrogen = TAN = 19.0
    mock_manure.urea = urea = 20.0
    mock_manure.manure_mass = 22.0
    mock_manure.urine = urine = 22.0
    mock_manure.nitrogen = N = 23.0
    mock_manure.total_solids = TS = 24.0
    mock_manure.degradable_volatile_solids = VSd = 25.0
    mock_manure.non_degradable_volatile_solids = VSnd = 26.0
    mock_manure.phosphorus = P = 27.0
    mock_manure.potassium = K = 28.0
    mock_manure.manure_volume = manure_volume = 29.0

    mock_pen = mocker.MagicMock(autospec=ManureManagerPen)
    mock_pen.id = pen_id = 1
    mock_pen.num_animals = num_animals = 100
    mock_pen.num_lactating_cows = 100
    mock_pen.exposed_manure_surface_area_from_pen_type = exposed_manure_surface_area_from_pen_type = 101.0
    mock_pen.manure = mock_manure
    mock_pen.pen_type = "freestall"

    mock_bedding = mocker.MagicMock(autospec=BaseBedding)
    mock_bedding.calc_total_bedding_volume.return_value = total_bedding_volume = 30.0
    mock_bedding.calc_total_bedding_mass.return_value = total_bedding_mass = 31.0

    sim_day = 10
    housing_ammonia_emission = 1.0
    patch_for_calc_housing_ammonia_emission = mocker.patch(
        "RUFAS.routines.manure.manure_handlers.manure_handler_classes.GasEmissionsCalculator.housing_ammonia_emission",
        return_value=housing_ammonia_emission,
    )
    housing_methane_emission = 2.0
    patch_for_calc_housing_methane_emission = mocker.patch(
        "RUFAS.routines.manure.manure_handlers.manure_handler_classes.GasEmissionsCalculator.housing_methane_emission",
        return_value=housing_methane_emission,
    )
    housing_carbon_dioxide_emission = 3.0
    patch_for_calc_housing_carbon_dioxide_emission = mocker.patch(
        "RUFAS.routines.manure.manure_handlers.manure_handler_classes."
        "GasEmissionsCalculator.housing_carbon_dioxide_emission",
        return_value=housing_carbon_dioxide_emission,
    )

    mock_manure_handler = BaseManureHandler(
        weather=mocker.MagicMock(),
        time=mocker.MagicMock(),
        manure_handler_config=mocker.MagicMock(auto_spec=ManureHandlerConfig),
        name="test",
    )
    mock_manure_handler.milking_parlor = mock_milking_parlor = mocker.MagicMock(autospec=MilkingParlor)
    mock_milking_parlor.calc_total_water_volume_used_in_milking_parlor.return_value = (
        total_water_volume_in_milking_parlor
    ) = 31.0
    cleaning_water_volume_in_main_barn = 32.0
    mocker.patch.object(
        mock_manure_handler,
        "calc_cleaning_water_volume_in_main_barn",
        return_value=cleaning_water_volume_in_main_barn,
    )
    current_day_avg_tempC = 42.0
    patch_for_get_current_day_avg_tempC = mocker.patch.object(
        mock_manure_handler,
        "_get_current_day_average_temperature_in_celsius",
        return_value=current_day_avg_tempC,
    )

    # Act
    manure_handler_daily_output = mock_manure_handler.daily_update(pen=mock_pen, bedding=mock_bedding, sim_day=sim_day)

    # Assert
    patch_for_calc_housing_ammonia_emission.assert_called_once_with(
        num_animals=num_animals,
        barn_area=exposed_manure_surface_area_from_pen_type,
        urine_total_ammoniacal_nitrogen=TAN,
        urine=urine,
        temp=current_day_avg_tempC,
    )
    patch_for_calc_housing_methane_emission.assert_called_once_with(
        barn_area=exposed_manure_surface_area_from_pen_type,
        barn_temp=current_day_avg_tempC,
    )
    patch_for_calc_housing_carbon_dioxide_emission.assert_called_once_with(
        barn_area=exposed_manure_surface_area_from_pen_type,
        barn_temp=current_day_avg_tempC,
    )
    assert manure_handler_daily_output.simulation_day == sim_day
    assert manure_handler_daily_output.pen_id == pen_id
    assert manure_handler_daily_output.manure_urea == approx(urea)
    assert manure_handler_daily_output.liquid_manure_total_ammoniacal_nitrogen == (
        approx(max(0.0, TAN - housing_ammonia_emission))
    )
    assert manure_handler_daily_output.liquid_manure_nitrogen == N
    assert manure_handler_daily_output.liquid_manure_total_solids == approx(TS)
    assert manure_handler_daily_output.liquid_manure_total_degradable_volatile_solids == approx(VSd)
    assert manure_handler_daily_output.liquid_manure_total_non_degradable_volatile_solids == approx(VSnd)
    assert manure_handler_daily_output.liquid_manure_phosphorus == approx(P)
    assert manure_handler_daily_output.liquid_manure_potassium == approx(K)
    assert manure_handler_daily_output.housing_methane == approx(housing_methane_emission)
    assert manure_handler_daily_output.housing_carbon_dioxide == approx(housing_carbon_dioxide_emission)
    assert manure_handler_daily_output.housing_ammonia == approx(housing_ammonia_emission)
    assert manure_handler_daily_output.manure_volume == approx(manure_volume)
    assert manure_handler_daily_output.cleaning_water_volume == approx(
        cleaning_water_volume_in_main_barn * GeneralConstants.LITERS_TO_CUBIC_METERS
    )
    assert manure_handler_daily_output.total_bedding_volume == approx(total_bedding_volume)
    assert manure_handler_daily_output.total_bedding_mass == approx(total_bedding_mass)
    assert manure_handler_daily_output.total_water_volume_in_milking_parlor == approx(
        total_water_volume_in_milking_parlor * GeneralConstants.LITERS_TO_CUBIC_METERS
    )
    assert manure_handler_daily_output.tempC == approx(current_day_avg_tempC)
    assert patch_for_get_current_day_avg_tempC.call_count == 4

    # --- Test pen type that does not require GHG emissions estimations. ---
    mock_pen.pen_type = "compost bedded pack barn"

    manure_handler_daily_output = mock_manure_handler.daily_update(pen=mock_pen, bedding=mock_bedding, sim_day=sim_day)

    assert patch_for_calc_housing_ammonia_emission.call_count == 1
    assert patch_for_calc_housing_methane_emission.call_count == 1
    assert patch_for_calc_housing_carbon_dioxide_emission.call_count == 1
    assert manure_handler_daily_output.simulation_day == sim_day
    assert manure_handler_daily_output.pen_id == pen_id
    assert manure_handler_daily_output.manure_urea == approx(urea)
    assert manure_handler_daily_output.liquid_manure_total_ammoniacal_nitrogen == approx(max(0.0, TAN))
    assert manure_handler_daily_output.liquid_manure_nitrogen == approx(N)
    assert manure_handler_daily_output.liquid_manure_total_solids == approx(TS)
    assert manure_handler_daily_output.liquid_manure_total_degradable_volatile_solids == approx(VSd)
    assert manure_handler_daily_output.liquid_manure_total_non_degradable_volatile_solids == approx(VSnd)
    assert manure_handler_daily_output.liquid_manure_phosphorus == approx(P)
    assert manure_handler_daily_output.liquid_manure_potassium == approx(K)
    assert manure_handler_daily_output.housing_methane == approx(0.0)
    assert manure_handler_daily_output.housing_carbon_dioxide == approx(0.0)
    assert manure_handler_daily_output.housing_ammonia == approx(0.0)
    assert manure_handler_daily_output.manure_volume == approx(manure_volume)
    assert manure_handler_daily_output.cleaning_water_volume == approx(
        cleaning_water_volume_in_main_barn * GeneralConstants.LITERS_TO_CUBIC_METERS
    )
    assert manure_handler_daily_output.total_bedding_volume == approx(total_bedding_volume)
    assert manure_handler_daily_output.total_bedding_mass == approx(total_bedding_mass)
    assert manure_handler_daily_output.total_water_volume_in_milking_parlor == approx(
        total_water_volume_in_milking_parlor * GeneralConstants.LITERS_TO_CUBIC_METERS
    )
    assert manure_handler_daily_output.tempC == approx(current_day_avg_tempC)
    assert patch_for_get_current_day_avg_tempC.call_count == 5


def test_manure_handler_daily_update_zero_animals(mocker: MockerFixture) -> None:
    """
    Unit test for daily_update() of class BaseManureHandler in file manure_handler_classes.py

    This test verifies that the daily update returns a default ManureHandlerDailyOutput object
    if there are no animals in the pen.
    """
    mock_manure = mocker.MagicMock(autospec=PenManure)
    mock_pen = mocker.MagicMock(autospec=ManureManagerPen)
    mock_pen.num_animals = 0
    mock_pen.manure = mock_manure

    mock_bedding = mocker.MagicMock(autospec=BaseBedding)

    mock_manure_handler = BaseManureHandler(
        weather=mocker.MagicMock(),
        time=mocker.MagicMock(),
        manure_handler_config=mocker.MagicMock(auto_spec=ManureHandlerConfig),
        name="test",
    )

    manure_handler_daily_output = mock_manure_handler.daily_update(pen=mock_pen, bedding=mock_bedding, sim_day=-1)

    assert manure_handler_daily_output.simulation_day == -1
    assert manure_handler_daily_output.pen_id == -1
    assert manure_handler_daily_output.manure_urea == approx(0.0)
    assert manure_handler_daily_output.liquid_manure_total_ammoniacal_nitrogen == (approx(0.0))
    assert manure_handler_daily_output.liquid_manure_nitrogen == approx(0.0)
    assert manure_handler_daily_output.liquid_manure_total_solids == approx(0.0)
    assert manure_handler_daily_output.liquid_manure_total_degradable_volatile_solids == approx(0.0)
    assert manure_handler_daily_output.liquid_manure_total_non_degradable_volatile_solids == approx(0.0)
    assert manure_handler_daily_output.liquid_manure_phosphorus == approx(0.0)
    assert manure_handler_daily_output.liquid_manure_potassium == approx(0.0)
    assert manure_handler_daily_output.housing_methane == approx(0.0)
    assert manure_handler_daily_output.housing_carbon_dioxide == approx(0.0)
    assert manure_handler_daily_output.housing_ammonia == approx(0.0)
    assert manure_handler_daily_output.manure_volume == approx(0.0)
    assert manure_handler_daily_output.cleaning_water_volume == approx(0.0)
    assert manure_handler_daily_output.total_bedding_volume == approx(0.0)
    assert manure_handler_daily_output.total_bedding_mass == approx(0.0)
    assert manure_handler_daily_output.total_water_volume_in_milking_parlor == approx(0.0)
    assert manure_handler_daily_output.tempC == approx(0.0)
