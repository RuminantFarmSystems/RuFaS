import dataclasses
from typing import Type

import pytest
from mock.mock import PropertyMock
from pytest import approx
from pytest_mock import MockFixture

from RUFAS.routines.manure.constants.manure_constants import ManureConstants
from RUFAS.routines.manure.manure_treatments.base_manure_treatment import BaseManureTreatment
from RUFAS.routines.manure.manure_treatments.manure_treatment_configs import DefaultManureTreatmentConfigFactory
from RUFAS.routines.manure.manure_treatments.manure_treatment_configs import ManureTreatmentConfig
from RUFAS.routines.manure.manure_treatments.manure_treatment_daily_output import ManureTreatmentDailyOutput
from RUFAS.routines.manure.manure_treatments.manure_treatment_factory import ManureTreatmentFactory
from RUFAS.routines.manure.manure_treatments.manure_treatment_types import ManureTreatmentType
from RUFAS.routines.manure.manure_treatments.slurry_storage_outdoor import SlurryStorageOutdoor
from RUFAS.routines.manure.manure_treatments.slurry_storage_underfloor import SlurryStorageUnderfloor
from RUFAS.routines.manure.protocols.liquid_manure_portion_protocol import LiquidManurePortionProtocol


# Test ManureTreatmentDailyOutput
# ===============================


def test_manure_treatment_daily_output() -> None:
    """Tests the ManureTreatmentDailyOutput class."""
    # Act
    manure_treatment_daily_output = ManureTreatmentDailyOutput(
            pen_id=1,
            simulation_day=2,
            liquid_manure_total_ammoniacal_nitrogen=3.0,
            liquid_manure_nitrogen=4.0,
            liquid_manure_total_solids=5.0,
            liquid_manure_total_volatile_solids=6.0,
            liquid_manure_phosphorus=7.0,
            liquid_manure_potassium=8.0,
            final_manure_volume=9.0,
            liquid_manure_daily_volume=10.0,  # Intentionally made different from final_manure_volume

            storage_methane=11.0,
            storage_ammonia=12.0,

            sludge_manure_total_solids=13.0,
            sludge_manure_total_volatile_solids=14.0,
            sludge_manure_nitrogen=15.0,
            sludge_manure_phosphorus=16.0,
            sludge_manure_potassium=17.0,
            sludge_manure_daily_volume=18.0,
            accumulated_sludge_volume=19.0,
            accumulated_final_manure_volume=20.0
    )

    # Assert
    assert manure_treatment_daily_output.pen_id == 1
    assert manure_treatment_daily_output.simulation_day == 2
    assert manure_treatment_daily_output.liquid_manure_total_ammoniacal_nitrogen == approx(3.0)
    assert manure_treatment_daily_output.liquid_manure_nitrogen == approx(4.0)
    assert manure_treatment_daily_output.liquid_manure_total_solids == approx(5.0)
    assert manure_treatment_daily_output.liquid_manure_total_volatile_solids == approx(6.0)
    assert manure_treatment_daily_output.liquid_manure_phosphorus == approx(7.0)
    assert manure_treatment_daily_output.liquid_manure_potassium == approx(8.0)

    # Note: final_manure_volume is the same as liquid_manure_daily_volume
    assert manure_treatment_daily_output.final_manure_volume == approx(9.0)
    assert manure_treatment_daily_output.liquid_manure_daily_volume == approx(9.0)

    assert manure_treatment_daily_output.storage_methane == approx(11.0)
    assert manure_treatment_daily_output.storage_ammonia == approx(12.0)

    assert manure_treatment_daily_output.sludge_manure_total_solids == approx(13.0)
    assert manure_treatment_daily_output.sludge_manure_total_volatile_solids == approx(14.0)
    assert manure_treatment_daily_output.sludge_manure_nitrogen == approx(15.0)
    assert manure_treatment_daily_output.sludge_manure_phosphorus == approx(16.0)
    assert manure_treatment_daily_output.sludge_manure_potassium == approx(17.0)
    assert manure_treatment_daily_output.sludge_manure_daily_volume == approx(18.0)
    assert manure_treatment_daily_output.accumulated_sludge_volume == approx(19.0)
    assert manure_treatment_daily_output.accumulated_final_manure_volume == approx(20.0)


def test_manure_treatment_daily_output_add() -> None:
    # Case 1: Add a ManureTreatmentDailyOutput to a non-ManureTreatmentDailyOutput object.

    # Arrange
    manure_treatment_daily_output = ManureTreatmentDailyOutput()

    # Act and Assert
    with pytest.raises(TypeError) as e:
        sum_object = manure_treatment_daily_output + 1
        # Check error message
        assert "Other must be of type ManureTreatmentDailyOutput" in str(e.value)

    # ------------------------------

    # Case 2: Add two valid ManureTreatmentDailyOutput objects.

    # Arrange
    manure_treatment_daily_output_1 = ManureTreatmentDailyOutput(
            pen_id=1,
            simulation_day=2,
            liquid_manure_total_ammoniacal_nitrogen=3.0,
            liquid_manure_nitrogen=4.0,
            liquid_manure_total_solids=5.0,
            liquid_manure_total_volatile_solids=6.0,
            liquid_manure_phosphorus=7.0,
            liquid_manure_potassium=8.0,
            final_manure_volume=9.0,
            liquid_manure_daily_volume=10.0,
            storage_methane=11.0,
            storage_ammonia=12.0,
            sludge_manure_total_solids=13.0,
            sludge_manure_total_volatile_solids=14.0,
            sludge_manure_nitrogen=15.0,
            sludge_manure_phosphorus=16.0,
            sludge_manure_potassium=17.0,
            sludge_manure_daily_volume=18.0,
            accumulated_sludge_volume=19.0,
            accumulated_final_manure_volume=20.0
    )

    manure_treatment_daily_output_2 = ManureTreatmentDailyOutput(
            pen_id=3,
            simulation_day=4,
            liquid_manure_total_ammoniacal_nitrogen=21.0,
            liquid_manure_nitrogen=22.0,
            liquid_manure_total_solids=23.0,
            liquid_manure_total_volatile_solids=24.0,
            liquid_manure_phosphorus=25.0,
            liquid_manure_potassium=26.0,
            final_manure_volume=27.0,
            liquid_manure_daily_volume=28.0,
            storage_methane=29.0,
            storage_ammonia=30.0,
            sludge_manure_total_solids=31.0,
            sludge_manure_total_volatile_solids=32.0,
            sludge_manure_nitrogen=33.0,
            sludge_manure_phosphorus=34.0,
            sludge_manure_potassium=35.0,
            sludge_manure_daily_volume=36.0,
            accumulated_sludge_volume=37.0,
            accumulated_final_manure_volume=38.0
    )

    # Act
    sum_of_manure_treatment_daily_outputs = manure_treatment_daily_output_1 + manure_treatment_daily_output_2

    # Assert
    assert sum_of_manure_treatment_daily_outputs.pen_id == 4
    assert sum_of_manure_treatment_daily_outputs.simulation_day == 6
    assert sum_of_manure_treatment_daily_outputs.liquid_manure_total_ammoniacal_nitrogen == approx(24.0)
    assert sum_of_manure_treatment_daily_outputs.liquid_manure_nitrogen == approx(26.0)
    assert sum_of_manure_treatment_daily_outputs.liquid_manure_total_solids == approx(28.0)
    assert sum_of_manure_treatment_daily_outputs.liquid_manure_total_volatile_solids == approx(30.0)
    assert sum_of_manure_treatment_daily_outputs.liquid_manure_phosphorus == approx(32.0)
    assert sum_of_manure_treatment_daily_outputs.liquid_manure_potassium == approx(34.0)

    # Note: final_manure_volume is the same as liquid_manure_daily_volume
    assert sum_of_manure_treatment_daily_outputs.final_manure_volume == approx(36.0)
    assert sum_of_manure_treatment_daily_outputs.liquid_manure_daily_volume == approx(36.0)

    assert sum_of_manure_treatment_daily_outputs.storage_methane == approx(40.0)
    assert sum_of_manure_treatment_daily_outputs.storage_ammonia == approx(42.0)
    assert sum_of_manure_treatment_daily_outputs.sludge_manure_total_solids == approx(44.0)
    assert sum_of_manure_treatment_daily_outputs.sludge_manure_total_volatile_solids == approx(46.0)
    assert sum_of_manure_treatment_daily_outputs.sludge_manure_nitrogen == approx(48.0)
    assert sum_of_manure_treatment_daily_outputs.sludge_manure_phosphorus == approx(50.0)
    assert sum_of_manure_treatment_daily_outputs.sludge_manure_potassium == approx(52.0)
    assert sum_of_manure_treatment_daily_outputs.sludge_manure_daily_volume == approx(54.0)
    assert sum_of_manure_treatment_daily_outputs.accumulated_sludge_volume == approx(56.0)
    assert sum_of_manure_treatment_daily_outputs.accumulated_final_manure_volume == approx(58.0)


# Test ManureTreatmentConfig
# ==========================

def test_manure_treatment_config() -> None:
    """Tests ManureTreatmentConfig class."""
    # Act
    manure_treatment_config = ManureTreatmentConfig(
            total_solids_removal_efficiency_for_treatment=0.1,
            volatile_solids_removal_efficiency_for_treatment=0.2,
            nitrogen_removal_efficiency_for_treatment=0.3,
            total_ammoniacal_nitrogen_removal_efficiency_for_treatment=0.4,
            phosphorus_removal_efficiency_for_treatment=0.5,
            potassium_removal_efficiency_for_treatment=0.6,

            hydraulic_retention_time=10,
            sludge_accumulation_period=20,
            sludge_accumulation_volume_fraction=0.15,
            top_cover_volume_fraction=0.25,
            biogas_generation_ratio=0.35,
            methane_generation_ratio=0.45,

            evaporation_fraction=0.55,
            anaerobic_digestion_temperature_set_point=60.0,
            anaerobic_digestion_temperature_celsius=70.0,

            storage_time_period=30,
            freeboard_input=0.65,
    )

    # Assert
    assert manure_treatment_config.total_solids_removal_efficiency_for_treatment == approx(0.1)
    assert manure_treatment_config.volatile_solids_removal_efficiency_for_treatment == approx(0.2)
    assert manure_treatment_config.nitrogen_removal_efficiency_for_treatment == approx(0.3)
    assert manure_treatment_config.total_ammoniacal_nitrogen_removal_efficiency_for_treatment == approx(0.4)
    assert manure_treatment_config.phosphorus_removal_efficiency_for_treatment == approx(0.5)
    assert manure_treatment_config.potassium_removal_efficiency_for_treatment == approx(0.6)

    assert manure_treatment_config.hydraulic_retention_time == 10
    assert manure_treatment_config.sludge_accumulation_period == 20
    assert manure_treatment_config.sludge_accumulation_volume_fraction == approx(0.15)
    assert manure_treatment_config.top_cover_volume_fraction == approx(0.25)
    assert manure_treatment_config.biogas_generation_ratio == approx(0.35)
    assert manure_treatment_config.methane_generation_ratio == approx(0.45)

    assert manure_treatment_config.evaporation_fraction == approx(0.55)
    assert manure_treatment_config.anaerobic_digestion_temperature_set_point == approx(60.0)
    assert manure_treatment_config.anaerobic_digestion_temperature_celsius == approx(70.0)

    assert manure_treatment_config.storage_time_period == 30
    assert manure_treatment_config.freeboard_input == approx(0.65)


# Test DefaultManureTreatmentConfigFactory
# ========================================

def test_slurry_storage_underfloor_default_config() -> None:
    """Tests the default values of the slurry storage underfloor manure treatment config."""
    # Arrange
    slurry_storage_underfloor_config = DefaultManureTreatmentConfigFactory.SLURRY_STORAGE_UNDERFLOOR_CONFIG

    # Assert
    assert slurry_storage_underfloor_config.total_solids_removal_efficiency_for_treatment == approx(0.10)
    assert slurry_storage_underfloor_config.volatile_solids_removal_efficiency_for_treatment == approx(0.20)
    assert slurry_storage_underfloor_config.nitrogen_removal_efficiency_for_treatment == approx(0.10)
    assert slurry_storage_underfloor_config.total_ammoniacal_nitrogen_removal_efficiency_for_treatment == approx(0.45)
    assert slurry_storage_underfloor_config.phosphorus_removal_efficiency_for_treatment == approx(0.05)
    assert slurry_storage_underfloor_config.potassium_removal_efficiency_for_treatment == approx(0.05)
    assert slurry_storage_underfloor_config.storage_time_period == 120


def test_slurry_storage_outdoor_default_config() -> None:
    """Tests the default values of the slurry storage outdoor manure treatment config."""
    # Act
    slurry_storage_outdoor_config = DefaultManureTreatmentConfigFactory.SLURRY_STORAGE_OUTDOOR_CONFIG

    # Assert
    assert slurry_storage_outdoor_config.total_solids_removal_efficiency_for_treatment == approx(0.10)
    assert slurry_storage_outdoor_config.volatile_solids_removal_efficiency_for_treatment == approx(0.20)
    assert slurry_storage_outdoor_config.nitrogen_removal_efficiency_for_treatment == approx(0.10)
    assert slurry_storage_outdoor_config.total_ammoniacal_nitrogen_removal_efficiency_for_treatment == approx(0.45)
    assert slurry_storage_outdoor_config.phosphorus_removal_efficiency_for_treatment == approx(0.05)
    assert slurry_storage_outdoor_config.potassium_removal_efficiency_for_treatment == approx(0.05)
    assert slurry_storage_outdoor_config.storage_time_period == 120
    assert slurry_storage_outdoor_config.freeboard_input == approx(0.3048)


def test_anaerobic_digestion_default_config() -> None:
    """Tests the default values of the anaerobic digestion manure treatment config."""
    # Act
    anaerobic_digestion_config = DefaultManureTreatmentConfigFactory.ANAEROBIC_DIGESTION_CONFIG

    # Assert
    assert anaerobic_digestion_config.total_solids_removal_efficiency_for_treatment == approx(0.45)
    assert anaerobic_digestion_config.volatile_solids_removal_efficiency_for_treatment == approx(0.40)
    assert anaerobic_digestion_config.nitrogen_removal_efficiency_for_treatment == approx(0.0)
    assert anaerobic_digestion_config.total_ammoniacal_nitrogen_removal_efficiency_for_treatment == approx(0.1)
    assert anaerobic_digestion_config.phosphorus_removal_efficiency_for_treatment == approx(0.0)
    assert anaerobic_digestion_config.potassium_removal_efficiency_for_treatment == approx(0.0)

    assert anaerobic_digestion_config.hydraulic_retention_time == 25
    assert anaerobic_digestion_config.sludge_accumulation_period == 1.0
    assert anaerobic_digestion_config.sludge_accumulation_volume_fraction == approx(0.03)
    assert anaerobic_digestion_config.top_cover_volume_fraction == approx(0.2)
    assert anaerobic_digestion_config.biogas_generation_ratio == approx(0.38)
    assert anaerobic_digestion_config.methane_generation_ratio == approx(0.65)

    assert anaerobic_digestion_config.evaporation_fraction == approx(0.02)
    assert anaerobic_digestion_config.anaerobic_digestion_temperature_set_point == approx(37.5)
    assert anaerobic_digestion_config.anaerobic_digestion_temperature_celsius == approx(37.5)


def test_anaerobic_lagoon_default_config() -> None:
    # Act
    anaerobic_lagoon_config = DefaultManureTreatmentConfigFactory.ANAEROBIC_LAGOON_CONFIG

    # Assert
    assert anaerobic_lagoon_config.total_solids_removal_efficiency_for_treatment == approx(0.75)
    assert anaerobic_lagoon_config.volatile_solids_removal_efficiency_for_treatment == approx(0.85)
    assert anaerobic_lagoon_config.nitrogen_removal_efficiency_for_treatment == approx(0.65)
    assert anaerobic_lagoon_config.total_ammoniacal_nitrogen_removal_efficiency_for_treatment == approx(0.7)
    assert anaerobic_lagoon_config.phosphorus_removal_efficiency_for_treatment == approx(0.6)
    assert anaerobic_lagoon_config.potassium_removal_efficiency_for_treatment == approx(0.2)

    assert anaerobic_lagoon_config.hydraulic_retention_time == 365
    assert anaerobic_lagoon_config.sludge_accumulation_period == 10.0
    assert anaerobic_lagoon_config.sludge_accumulation_volume_fraction == approx(0.00251)

    assert anaerobic_lagoon_config.storage_time_period == 365
    assert anaerobic_lagoon_config.freeboard_input == approx(0.3048)


@pytest.mark.parametrize(
        "manure_treatment_type, expected_manure_treatment_config",
        [
            (ManureTreatmentType.SLURRY_STORAGE_UNDERFLOOR,
             DefaultManureTreatmentConfigFactory.SLURRY_STORAGE_UNDERFLOOR_CONFIG),
            (ManureTreatmentType.SLURRY_STORAGE_OUTDOOR,
             DefaultManureTreatmentConfigFactory.SLURRY_STORAGE_OUTDOOR_CONFIG),
            (ManureTreatmentType.ANAEROBIC_DIGESTION, DefaultManureTreatmentConfigFactory.ANAEROBIC_DIGESTION_CONFIG),
            (ManureTreatmentType.ANAEROBIC_LAGOON, DefaultManureTreatmentConfigFactory.ANAEROBIC_LAGOON_CONFIG),
        ])
def test_default_manure_treatment_config_factory_get_instance(manure_treatment_type: ManureTreatmentType,
                                                              expected_manure_treatment_config:
                                                              ManureTreatmentConfig) -> None:
    # Act
    manure_treatment_config = DefaultManureTreatmentConfigFactory.get_instance(manure_treatment_type)

    # Assert
    assert manure_treatment_config == expected_manure_treatment_config


# Test ManureTreatmentType
# ========================

@pytest.mark.parametrize(
        'manure_treatment_type_name, expected_manure_treatment_type',
        [
            ('slurry storage underfloor', ManureTreatmentType.SLURRY_STORAGE_UNDERFLOOR),
            ('slurry storage outdoor', ManureTreatmentType.SLURRY_STORAGE_OUTDOOR),
            ('anaerobic digestion', ManureTreatmentType.ANAEROBIC_DIGESTION),
            ('anaerobic lagoon', ManureTreatmentType.ANAEROBIC_LAGOON),
            ('anaerobic digestion and lagoon', ManureTreatmentType.ANAEROBIC_DIGESTION_AND_LAGOON),
            ('anaerobic digestion and lagoon with split',
             ManureTreatmentType.ANAEROBIC_DIGESTION_AND_LAGOON_WITH_SPLIT),
            ('slurry_storage_underfloor', ManureTreatmentType.SLURRY_STORAGE_UNDERFLOOR),
            ('slurry_storage_outdoor', ManureTreatmentType.SLURRY_STORAGE_OUTDOOR),
            ('anaerobic_digestion', ManureTreatmentType.ANAEROBIC_DIGESTION),
            ('anaerobic_lagoon', ManureTreatmentType.ANAEROBIC_LAGOON),
            ('anaerobic_digestion_and_lagoon', ManureTreatmentType.ANAEROBIC_DIGESTION_AND_LAGOON),
            ('anaerobic_digestion_and_lagoon_with_split',
             ManureTreatmentType.ANAEROBIC_DIGESTION_AND_LAGOON_WITH_SPLIT),
            ('dummy', ManureTreatmentType.SLURRY_STORAGE_UNDERFLOOR)
        ])
def test_manure_treatment_type_get_type(manure_treatment_type_name: str,
                                        expected_manure_treatment_type: ManureTreatmentType) -> None:
    # Assert
    assert ManureTreatmentType.get_type(manure_treatment_type_name) == expected_manure_treatment_type


# Test ManureTreatmentFactory
# ===========================

@pytest.mark.parametrize(
        'manure_treatment_type_name, custom_manure_treatment_config,'
        'expected_manure_treatment_class,expected_manure_treatment_config',
        [
            ('slurry storage underfloor', None, SlurryStorageUnderfloor,
             DefaultManureTreatmentConfigFactory.SLURRY_STORAGE_UNDERFLOOR_CONFIG),
            ('slurry storage underfloor', DefaultManureTreatmentConfigFactory.SLURRY_STORAGE_UNDERFLOOR_CONFIG,
             SlurryStorageUnderfloor, DefaultManureTreatmentConfigFactory.SLURRY_STORAGE_UNDERFLOOR_CONFIG),
            ('slurry storage outdoor', None, SlurryStorageOutdoor,
             DefaultManureTreatmentConfigFactory.SLURRY_STORAGE_OUTDOOR_CONFIG),
            ('slurry storage outdoor', DefaultManureTreatmentConfigFactory.SLURRY_STORAGE_OUTDOOR_CONFIG,
             SlurryStorageOutdoor, DefaultManureTreatmentConfigFactory.SLURRY_STORAGE_OUTDOOR_CONFIG),
        ])
def test_manure_treatment_factory_get_instance(manure_treatment_type_name: str,
                                               custom_manure_treatment_config: ManureTreatmentConfig,
                                               expected_manure_treatment_class: Type[BaseManureTreatment],
                                               expected_manure_treatment_config: ManureTreatmentConfig,
                                               mocker: MockFixture) -> None:
    """Unit test for get_instance() method of ManureTreatmentFactory class."""
    # Arrange
    mock_weather = mocker.MagicMock()
    mock_time = mocker.MagicMock()

    # Act
    manure_treatment = ManureTreatmentFactory.get_instance(manure_treatment_type_name,
                                                           mock_weather,
                                                           mock_time,
                                                           custom_manure_treatment_config)

    # Assert
    assert type(manure_treatment) == expected_manure_treatment_class
    assert manure_treatment.weather == mock_weather
    assert manure_treatment.time == mock_time
    assert manure_treatment.config == expected_manure_treatment_config

    assert manure_treatment._sim_day == -1
    assert manure_treatment._current_pen is None
    assert manure_treatment._manure_handler_daily_output is None
    assert manure_treatment._current_manure_treatment_daily_input is None
    assert manure_treatment._manure_separator is None
    assert manure_treatment._manure_separator_daily_output is None
    assert manure_treatment._accumulated_output == ManureTreatmentDailyOutput()

    assert manure_treatment.manure_separator_daily_output is None


# Test BaseManureTreatment
# ========================

@pytest.mark.parametrize(
        'manure_treatment_type_name',
        [
            'slurry storage underfloor',
            'slurry storage outdoor',
            # 'anaerobic digestion',
            # 'anaerobic lagoon',
            # 'anaerobic digestion and lagoon',
            # 'anaerobic digestion and lagoon with split',
        ])
def test_initialize_private_attributes_during_update(manure_treatment_type_name: str,
                                                     mocker: MockFixture) -> None:
    # Arrange
    manure_treatment = ManureTreatmentFactory.get_instance(
            manure_treatment_type_name=manure_treatment_type_name,
            weather=mocker.MagicMock(),
            time=mocker.MagicMock(),
            custom_manure_treatment_config=None
    )
    sim_day = 10
    current_pen = mocker.MagicMock()
    manure_handler_daily_output = mocker.MagicMock()
    manure_treatment_daily_input = mocker.MagicMock()
    manure_separator = mocker.MagicMock()

    # Act
    manure_treatment._initialize_private_attributes_during_update(
            sim_day=sim_day,
            current_pen=current_pen,
            manure_handler_daily_output=manure_handler_daily_output,
            manure_treatment_daily_input=manure_treatment_daily_input,
            manure_separator=manure_separator
    )

    # Assert
    assert manure_treatment._sim_day == sim_day
    assert manure_treatment._current_pen == current_pen
    assert manure_treatment._manure_handler_daily_output == manure_handler_daily_output
    assert manure_treatment._current_manure_treatment_daily_input == manure_treatment_daily_input
    assert manure_treatment._manure_separator == manure_separator


@pytest.mark.parametrize(
        'manure_treatment_type_name',
        [
            'slurry storage underfloor',
            'slurry storage outdoor',
            # 'anaerobic digestion',
            # 'anaerobic lagoon',
            # 'anaerobic digestion and lagoon',
            # 'anaerobic digestion and lagoon with split',
        ])
def test_initialize_daily_output_during_update(manure_treatment_type_name: str,
                                               mocker: MockFixture) -> None:
    """Unit test for _initialize_daily_output_during_update() method of BaseManureTreatment class."""

    # Arrange
    total_ammoniacal_nitrogen_removal_efficiency_for_treatment = 0.1
    nitrogen_removal_efficiency_for_treatment = 0.2
    phosphorus_removal_efficiency_for_treatment = 0.3
    potassium_removal_efficiency_for_treatment = 0.4
    volatile_solids_removal_efficiency_for_treatment = 0.5
    total_solids_removal_efficiency_for_treatment = 0.6

    custom_manure_treatment_config = ManureTreatmentConfig(
            total_ammoniacal_nitrogen_removal_efficiency_for_treatment=(
                total_ammoniacal_nitrogen_removal_efficiency_for_treatment),
            nitrogen_removal_efficiency_for_treatment=nitrogen_removal_efficiency_for_treatment,
            phosphorus_removal_efficiency_for_treatment=phosphorus_removal_efficiency_for_treatment,
            potassium_removal_efficiency_for_treatment=potassium_removal_efficiency_for_treatment,
            volatile_solids_removal_efficiency_for_treatment=volatile_solids_removal_efficiency_for_treatment,
            total_solids_removal_efficiency_for_treatment=total_solids_removal_efficiency_for_treatment

    )
    manure_treatment = ManureTreatmentFactory.get_instance(
            manure_treatment_type_name=manure_treatment_type_name,
            weather=mocker.MagicMock(),
            time=mocker.MagicMock(),
            custom_manure_treatment_config=custom_manure_treatment_config
    )
    manure_treatment_daily_input: LiquidManurePortionProtocol = mocker.MagicMock()
    manure_treatment_daily_input.simulation_day = simulation_day = 5
    manure_treatment_daily_input.pen_id = pen_id = 6
    manure_treatment_daily_input.liquid_manure_daily_volume = liquid_manure_daily_volume = 100
    manure_treatment_daily_input.liquid_manure_total_solids = liquid_manure_total_solids = 10
    manure_treatment_daily_input.liquid_manure_total_ammoniacal_nitrogen = liquid_manure_total_ammoniacal_nitrogen = 20
    manure_treatment_daily_input.liquid_manure_nitrogen = liquid_manure_nitrogen = 30
    manure_treatment_daily_input.liquid_manure_total_volatile_solids = liquid_manure_total_volatile_solids = 40
    manure_treatment_daily_input.liquid_manure_phosphorus = liquid_manure_phosphorus = 50
    manure_treatment_daily_input.liquid_manure_potassium = liquid_manure_potassium = 60

    expected_manure_treatment_daily_output = ManureTreatmentDailyOutput(
            simulation_day=simulation_day,
            pen_id=pen_id,
            liquid_manure_total_ammoniacal_nitrogen=(liquid_manure_total_ammoniacal_nitrogen *
                                                     (1 - total_ammoniacal_nitrogen_removal_efficiency_for_treatment)),
            liquid_manure_nitrogen=(liquid_manure_nitrogen * (1 - nitrogen_removal_efficiency_for_treatment)),
            liquid_manure_phosphorus=(liquid_manure_phosphorus * (1 - phosphorus_removal_efficiency_for_treatment)),
            liquid_manure_potassium=(liquid_manure_potassium * (1 - potassium_removal_efficiency_for_treatment)),
            liquid_manure_total_volatile_solids=(liquid_manure_total_volatile_solids *
                                                 (1 - volatile_solids_removal_efficiency_for_treatment)),
            liquid_manure_total_solids=(
                    liquid_manure_total_solids * (1 - total_solids_removal_efficiency_for_treatment)),
            final_manure_volume=(liquid_manure_daily_volume -
                                 (liquid_manure_total_solids * total_solids_removal_efficiency_for_treatment) / 1000.0)
    )

    # Act
    actual_daily_output = manure_treatment._initialize_daily_output_during_update(
            manure_treatment_daily_input=manure_treatment_daily_input
    )

    # Assert
    assert actual_daily_output == expected_manure_treatment_daily_output


@pytest.mark.parametrize(
        'manure_treatment_type_name',
        [
            'slurry storage underfloor',
            'slurry storage outdoor',
            # 'anaerobic digestion',
            # 'anaerobic lagoon',
            # 'anaerobic digestion and lagoon',
            # 'anaerobic digestion and lagoon with split',
        ])
def test_get_current_day_temperature_and_rainfall(manure_treatment_type_name: str,
                                                  mocker: MockFixture) -> None:
    """Unit test for _get_current_day_average_temperature_celsius() and _get_current_day_rainfall()."""

    # Arrange
    expected_current_day_average_temperature_celsius = 10
    expected_rainfall = 20
    mock_time = mocker.MagicMock()
    mock_time.year = 10
    mock_time.day = 1
    mock_weather = mocker.MagicMock()
    mock_weather.T_avg = [[0.0] * 10 for _ in range(mock_time.year + 1)]
    mock_weather.T_avg[mock_time.year - 1][mock_time.day - 1] = expected_current_day_average_temperature_celsius
    mock_weather.rainfall = [[0.0] * 10 for _ in range(mock_time.year + 1)]
    mock_weather.rainfall[mock_time.year - 1][mock_time.day - 1] = expected_rainfall

    manure_treatment = ManureTreatmentFactory.get_instance(
            manure_treatment_type_name=manure_treatment_type_name,
            weather=mock_weather,
            time=mock_time,
    )

    # Act
    actual_current_day_average_temperature_celsius = manure_treatment._get_current_day_average_temperature_celsius()
    actual_current_day_rainfall = manure_treatment._get_current_day_rainfall()

    # Assert
    assert actual_current_day_average_temperature_celsius == expected_current_day_average_temperature_celsius
    assert actual_current_day_rainfall == expected_rainfall


@pytest.mark.parametrize(
        'manure_treatment_type_name',
        [
            'slurry storage underfloor',
            'slurry storage outdoor',
            # 'anaerobic digestion',
            # 'anaerobic lagoon',
            # 'anaerobic digestion and lagoon',
            # 'anaerobic digestion and lagoon with split',
        ])
def test_accumulate_daily_output(manure_treatment_type_name: str,
                                 mocker: MockFixture) -> None:
    """Unit test for _accumulate_daily_output()."""

    # Arrange
    manure_treatment = ManureTreatmentFactory.get_instance(
            manure_treatment_type_name=manure_treatment_type_name,
            weather=mocker.MagicMock(),
            time=mocker.MagicMock(),
    )
    manure_treatment_daily_output = ManureTreatmentDailyOutput()
    dummy_value = 10
    for field_name in dataclasses.fields(manure_treatment_daily_output):
        setattr(manure_treatment_daily_output, field_name.name, dummy_value)
    expected_accumulated_output = ManureTreatmentDailyOutput() + manure_treatment_daily_output

    # Assert before
    assert manure_treatment._accumulated_output == ManureTreatmentDailyOutput()

    # Act
    manure_treatment._accumulate_daily_output(manure_treatment_daily_output=manure_treatment_daily_output)

    # Assert after
    assert manure_treatment._accumulated_output == expected_accumulated_output


@pytest.mark.parametrize(
        'manure_treatment_type_name',
        [
            'slurry storage underfloor',
            'slurry storage outdoor',
            # 'anaerobic digestion',
            # 'anaerobic lagoon',
            # 'anaerobic digestion and lagoon',
            # 'anaerobic digestion and lagoon with split',
        ])
def test_daily_update(manure_treatment_type_name: str,
                      mocker: MockFixture) -> None:
    """Unit test for daily_update() in base_manure_treatment.py."""

    # Arrange
    mock_manure_handler_daily_output = mocker.MagicMock()
    mock_manure_treatment_daily_input = mocker.MagicMock()
    mock_pen = mocker.MagicMock()
    simulation_day = 10
    mock_manure_separator = mocker.MagicMock()

    manure_treatment = ManureTreatmentFactory.get_instance(
            manure_treatment_type_name=manure_treatment_type_name,
            weather=mocker.MagicMock(),
            time=mocker.MagicMock(),
    )
    patch_for_initialize_private_attributes_during_update = mocker.patch.object(
            manure_treatment, '_initialize_private_attributes_during_update'
    )
    expected_manure_treatment_daily_output = ManureTreatmentDailyOutput()
    patch_for_daily_update_helper = mocker.patch.object(
            manure_treatment, '_daily_update_helper',
            return_value=expected_manure_treatment_daily_output
    )

    # Act
    actual_manure_treatment_daily_output = manure_treatment.daily_update(
            manure_handler_daily_output=mock_manure_handler_daily_output,
            manure_treatment_daily_input=mock_manure_treatment_daily_input,
            pen=mock_pen,
            sim_day=simulation_day,
            manure_separator=mock_manure_separator,
    )

    # Assert
    patch_for_initialize_private_attributes_during_update.assert_called_once_with(
            simulation_day, mock_pen, mock_manure_handler_daily_output,
            mock_manure_treatment_daily_input, mock_manure_separator
    )
    patch_for_daily_update_helper.assert_called_once()
    assert actual_manure_treatment_daily_output == expected_manure_treatment_daily_output


# Test SlurryStorageUnderfloor and SlurryStorageOutdoor
# =====================================================

@pytest.mark.parametrize(
        'slurry_storage_treatment_type_name',
        [
            'slurry storage underfloor',
            'slurry storage outdoor',
        ]
)
def test_slurry_storage_daily_update_helper(slurry_storage_treatment_type_name: str,
                                            mocker: MockFixture) -> None:
    """Unit test for _daily_update_helper() in both slurry storage treatments."""
    # Arrange
    slurry_storage = ManureTreatmentFactory.get_instance(
            manure_treatment_type_name=slurry_storage_treatment_type_name,
            weather=mocker.MagicMock(),
            time=mocker.MagicMock
    )
    mock_accumulated_output: ManureTreatmentDailyOutput = mocker.MagicMock()
    mock_accumulated_output.liquid_manure_total_solids = liquid_manure_total_solids = 20.0
    mock_accumulated_output.final_manure_volume = final_manure_volume = 30.0
    mock_accumulated_output.liquid_manure_total_ammoniacal_nitrogen = liquid_manure_total_ammoniacal_nitrogen = 40.0
    slurry_storage._accumulated_output = mock_accumulated_output
    patch_for_accumulate_daily_output = mocker.patch.object(
            slurry_storage, '_accumulate_daily_output'
    )

    mock_pen = mocker.MagicMock()
    mock_pen.num_animals = num_animals = 100
    mock_pen.barn_area_from_pen_type = barn_area_from_pen_type = 1000.0
    slurry_storage._current_pen = mock_pen

    initial_manure_treatment_daily_output = ManureTreatmentDailyOutput()
    slurry_storage._current_manure_treatment_daily_input = \
        current_manure_treatment_daily_input = mocker.MagicMock()
    patch_for_initialize_daily_output_during_update = mocker.patch.object(
            slurry_storage, '_initialize_daily_output_during_update',
            return_value=initial_manure_treatment_daily_output
    )

    expected_methane_loss = 10.0
    expected_new_accumulated_liquid_manure_total_solids = 30.0
    patch_for_calc_methane_emission = mocker.patch.object(
            slurry_storage, 'calc_methane_emission',
            return_value=[expected_methane_loss, expected_new_accumulated_liquid_manure_total_solids]
    )

    expected_ammonia_loss = 50.0
    expected_new_accumulated_liquid_manure_total_ammoniacal_nitrogen = 60.0
    patch_for_calc_ammonia_emission = mocker.patch.object(
            slurry_storage, 'calc_ammonia_emission',
            return_value=[expected_ammonia_loss, expected_new_accumulated_liquid_manure_total_ammoniacal_nitrogen]
    )

    # Act
    actual_manure_treatment_daily_output = slurry_storage._daily_update_helper()

    # Assert
    patch_for_initialize_daily_output_during_update.assert_called_once_with(current_manure_treatment_daily_input)
    patch_for_accumulate_daily_output.assert_called_once_with(initial_manure_treatment_daily_output)

    patch_for_calc_methane_emission.assert_called_once_with(liquid_manure_total_solids)
    assert slurry_storage._accumulated_output.liquid_manure_total_solids == \
           expected_new_accumulated_liquid_manure_total_solids
    assert actual_manure_treatment_daily_output.storage_methane == expected_methane_loss

    patch_for_calc_ammonia_emission.assert_called_once_with(
            num_animals=num_animals,
            barn_area=barn_area_from_pen_type,
            accumulated_manure_volume=final_manure_volume,
            accumulated_manure_total_ammoniacal_nitrogen=liquid_manure_total_ammoniacal_nitrogen,
    )
    assert slurry_storage._accumulated_output.liquid_manure_total_ammoniacal_nitrogen == \
           expected_new_accumulated_liquid_manure_total_ammoniacal_nitrogen
    assert actual_manure_treatment_daily_output.storage_ammonia == expected_ammonia_loss


@pytest.mark.parametrize(
        'slurry_storage_treatment_type_name, is_enclosed',
        [
            ('slurry storage underfloor', True),
            ('slurry storage outdoor', False),
        ]
)
def test_slurry_storage_calc_methane_emission(slurry_storage_treatment_type_name: str,
                                              is_enclosed: bool,
                                              mocker: MockFixture) -> None:
    """Unit test for calc_methane_emission() in both slurry storage treatments."""
    # Arrange
    slurry_storage = ManureTreatmentFactory.get_instance(
            manure_treatment_type_name=slurry_storage_treatment_type_name,
            weather=mocker.MagicMock(),
            time=mocker.MagicMock(),
    )
    accumulated_liquid_manure_total_solids = 10.0
    temperature_celsius = 20.0
    patch_for_get_current_day_average_temperature_celsius = mocker.patch.object(
            slurry_storage, '_get_current_day_average_temperature_celsius',
            return_value=temperature_celsius
    )
    expected_methane_loss = 2.0
    patch_for_calc_methane_emission_for_slurry_storage = mocker.patch(
            'RUFAS.routines.manure.manure_treatments.slurry_storage_underfloor.'
            'GasEmissions.calc_methane_emission_for_slurry_storage',
            return_value=expected_methane_loss
    )
    expected_new_accumulated_liquid_manure_total_solids = max(
            accumulated_liquid_manure_total_solids - expected_methane_loss, 0.0)

    # Act
    actual_methane_loss, actual_new_accumulated_liquid_manure_total_solids = \
        slurry_storage.calc_methane_emission(
                accumulated_liquid_manure_total_solids=accumulated_liquid_manure_total_solids
        )

    # Assert
    patch_for_get_current_day_average_temperature_celsius.assert_called_once()
    patch_for_calc_methane_emission_for_slurry_storage.assert_called_once_with(
            manure_total_solids=accumulated_liquid_manure_total_solids,
            is_enclosed=is_enclosed,
            temperature_celsius=temperature_celsius,
    )
    assert actual_methane_loss == expected_methane_loss
    assert actual_new_accumulated_liquid_manure_total_solids == expected_new_accumulated_liquid_manure_total_solids


@pytest.mark.parametrize(
        'slurry_storage_treatment_type_name',
        [
            'slurry storage underfloor',
            'slurry storage outdoor',
        ]
)
def test_slurry_storage_calc_ammonia_emission(slurry_storage_treatment_type_name: str,
                                              mocker: MockFixture) -> None:
    """Unit test for calc_ammonia_emission() in both slurry storage treatments."""
    # Arrange
    slurry_storage = ManureTreatmentFactory.get_instance(
            manure_treatment_type_name=slurry_storage_treatment_type_name,
            weather=mocker.MagicMock(),
            time=mocker.MagicMock(),
    )

    num_animals = 100
    barn_area = 1000.0
    accumulated_manure_volume = 200.0
    accumulated_manure_total_ammoniacal_nitrogen = 20.0
    temperature_celsius = 20.0
    patch_for_get_current_day_average_temperature_celsius = mocker.patch.object(
            slurry_storage, '_get_current_day_average_temperature_celsius',
            return_value=temperature_celsius
    )
    expected_ammonia_loss = 2.0
    patch_for_calc_ammonia_emission_for_slurry_storage = mocker.patch(
            'RUFAS.routines.manure.manure_treatments.slurry_storage_underfloor.'
            'GasEmissions.calc_ammonia_emission',
            return_value=expected_ammonia_loss
    )
    expected_new_accumulated_manure_total_ammoniacal_nitrogen = max(
            accumulated_manure_total_ammoniacal_nitrogen - expected_ammonia_loss, 0.0)

    # Act
    actual_ammonia_loss, actual_new_accumulated_manure_total_ammoniacal_nitrogen = \
        slurry_storage.calc_ammonia_emission(
                num_animals=num_animals,
                barn_area=barn_area,
                accumulated_manure_volume=accumulated_manure_volume,
                accumulated_manure_total_ammoniacal_nitrogen=accumulated_manure_total_ammoniacal_nitrogen
        )

    # Assert
    patch_for_get_current_day_average_temperature_celsius.assert_called_once()
    patch_for_calc_ammonia_emission_for_slurry_storage.assert_called_once_with(
            num_animals=num_animals,
            barn_area=barn_area,
            manure_urine_total_ammoniacal_nitrogen=accumulated_manure_total_ammoniacal_nitrogen / num_animals,
            manure_urine=accumulated_manure_volume * ManureConstants.MANURE_DENSITY / num_animals,
            temperature_celsius=temperature_celsius
    )
    assert actual_ammonia_loss == expected_ammonia_loss
    assert actual_new_accumulated_manure_total_ammoniacal_nitrogen == \
           expected_new_accumulated_manure_total_ammoniacal_nitrogen


# Test SlurryStorageUnderfloor specific methods
# ==========================================

def test_slurry_storage_underfloor_init(mocker: MockFixture) -> None:
    """Unit test for __init__() in slurry_storage_underfloor.py."""
    # Arrange
    mock_weather = mocker.MagicMock()
    mock_time = mocker.MagicMock()
    mock_manure_treatment_config = mocker.MagicMock()
    mock_manure_treatment_config.storage_time_period = storage_time_period = 120

    def mock_base_manure_treatment(self, weather, time, manure_treatment_config: ManureTreatmentConfig) -> None:
        self.weather = weather
        self.time = time
        self.config = manure_treatment_config

    mocker.patch(
            'RUFAS.routines.manure.manure_treatments.base_manure_treatment.BaseManureTreatment.__init__',
            new=mock_base_manure_treatment
    )

    # Act
    slurry_storage_underfloor = SlurryStorageUnderfloor(
            weather=mock_weather,
            time=mock_time,
            manure_treatment_config=mock_manure_treatment_config
    )

    # Assert
    assert slurry_storage_underfloor.storage_time_period == storage_time_period


# Test SlurryStorageOutdoor specific methods
# ==========================================

def test_slurry_storage_outdoor_init(mocker: MockFixture) -> None:
    """Unit test for __init__() in slurry_storage_underfloor.py."""
    # Arrange
    mock_weather = mocker.MagicMock()
    mock_time = mocker.MagicMock()
    mock_manure_treatment_config = mocker.MagicMock()
    mock_manure_treatment_config.storage_time_period = storage_time_period = 120
    mock_manure_treatment_config.freeboard_input = freeboard_input = 130.0

    def mock_base_manure_treatment(self, weather, time, manure_treatment_config: ManureTreatmentConfig) -> None:
        self.weather = weather
        self.time = time
        self.config = manure_treatment_config

    mocker.patch(
            'RUFAS.routines.manure.manure_treatments.base_manure_treatment.BaseManureTreatment.__init__',
            new=mock_base_manure_treatment
    )

    # Act
    slurry_storage_outdoor = SlurryStorageOutdoor(
            weather=mock_weather,
            time=mock_time,
            manure_treatment_config=mock_manure_treatment_config
    )

    # Assert
    assert slurry_storage_outdoor.storage_time_period == storage_time_period
    assert slurry_storage_outdoor.freeboard_input == freeboard_input


def test_wastewater_volume(mocker: MockFixture) -> None:
    """Unit test for _wastewater_volume() in slurry_storage_outdoor.py."""
    # Case 1: There is a current manure treatment daily input
    # Arrange
    slurry_storage_outdoor = SlurryStorageOutdoor(
            weather=mocker.MagicMock(),
            time=mocker.MagicMock(),
            manure_treatment_config=mocker.MagicMock()
    )
    mock_manure_treatment_daily_input = mocker.MagicMock()
    mock_manure_treatment_daily_input.liquid_manure_daily_volume = expected_liquid_manure_daily_volume = 100.0
    slurry_storage_outdoor._current_manure_treatment_daily_input = mock_manure_treatment_daily_input

    # Act
    actual_wastewater_volume = slurry_storage_outdoor.wastewater_volume

    # Assert
    assert actual_wastewater_volume == expected_liquid_manure_daily_volume

    # ----------------------------------------

    # Case 2: There is no current manure treatment daily input
    # Arrange
    slurry_storage_outdoor = SlurryStorageOutdoor(
            weather=mocker.MagicMock(),
            time=mocker.MagicMock(),
            manure_treatment_config=mocker.MagicMock()
    )
    slurry_storage_outdoor._current_manure_treatment_daily_input = None

    # Act
    actual_wastewater_volume = slurry_storage_outdoor.wastewater_volume

    # Assert
    assert actual_wastewater_volume == 0.0


def test_treatment_volume(mocker: MockFixture) -> None:
    """Unit test for _treatment_volume() in slurry_storage_outdoor.py."""
    # Arrange
    slurry_storage_outdoor = SlurryStorageOutdoor(
            weather=mocker.MagicMock(),
            time=mocker.MagicMock(),
            manure_treatment_config=mocker.MagicMock()
    )
    wastewater_volume = 100.0
    patch_for_wastewater_volume = mocker.patch(
            'RUFAS.routines.manure.manure_treatments.slurry_storage_outdoor.SlurryStorageOutdoor.wastewater_volume',
            new_callable=PropertyMock,
            return_value=wastewater_volume)
    slurry_storage_outdoor.storage_time_period = storage_time_period = 120

    # Act
    actual_treatment_volume = slurry_storage_outdoor.treatment_volume

    # Assert
    assert actual_treatment_volume == wastewater_volume * storage_time_period
    patch_for_wastewater_volume.assert_called_once()


def test_total_pit_volume(mocker: MockFixture) -> None:
    """Unit test for _total_pit_volume() in slurry_storage_outdoor.py."""
    # Case 1: There is a current manure treatment daily input
    # Arrange
    slurry_storage_outdoor = SlurryStorageOutdoor(
            weather=mocker.MagicMock(),
            time=mocker.MagicMock(),
            manure_treatment_config=mocker.MagicMock()
    )
    mock_manure_treatment_daily_input = mocker.MagicMock()
    slurry_storage_outdoor._current_manure_treatment_daily_input = mock_manure_treatment_daily_input
    treatment_volume = 100.0
    patch_for_treatment_volume = mocker.patch(
            'RUFAS.routines.manure.manure_treatments.slurry_storage_outdoor.SlurryStorageOutdoor.treatment_volume',
            new_callable=PropertyMock,
            return_value=treatment_volume)
    freeboard_volume = 200.0
    patch_for_freeboard_volume = mocker.patch(
            'RUFAS.routines.manure.manure_treatments.slurry_storage_outdoor.SlurryStorageOutdoor.freeboard_volume',
            new_callable=PropertyMock,
            return_value=freeboard_volume)
    precipitation_volume = 300.0
    patch_for_precipitation_volume = mocker.patch(
            'RUFAS.routines.manure.manure_treatments.slurry_storage_outdoor.SlurryStorageOutdoor.precipitation_volume',
            new_callable=PropertyMock,
            return_value=precipitation_volume)
    expected_total_pit_volume = treatment_volume + freeboard_volume + precipitation_volume

    # Act
    actual_total_pit_volume = slurry_storage_outdoor.total_pit_volume

    # Assert
    assert actual_total_pit_volume == expected_total_pit_volume
    patch_for_treatment_volume.assert_called_once()
    patch_for_freeboard_volume.assert_called_once()
    patch_for_precipitation_volume.assert_called_once()

    # ----------------------------------------

    # Case 2: There is no current manure treatment daily input
    # Arrange
    slurry_storage_outdoor = SlurryStorageOutdoor(
            weather=mocker.MagicMock(),
            time=mocker.MagicMock(),
            manure_treatment_config=mocker.MagicMock()
    )
    slurry_storage_outdoor._current_manure_treatment_daily_input = None

    # Act
    actual_total_pit_volume = slurry_storage_outdoor.total_pit_volume

    # Assert
    assert actual_total_pit_volume == 0.0


def test_pit_depth(mocker: MockFixture) -> None:
    """Unit test for _pit_depth() in slurry_storage_outdoor.py."""
    # Arrange
    slurry_storage_outdoor = SlurryStorageOutdoor(
            weather=mocker.MagicMock(),
            time=mocker.MagicMock(),
            manure_treatment_config=mocker.MagicMock()
    )
    expected_pit_depth = 3.657

    # Act
    actual_pit_depth = slurry_storage_outdoor.pit_depth

    # Assert
    assert actual_pit_depth == expected_pit_depth


def test_pit_slope(mocker: MockFixture) -> None:
    """Unit test for _pit_slope() in slurry_storage_outdoor.py."""
    # Arrange
    slurry_storage_outdoor = SlurryStorageOutdoor(
            weather=mocker.MagicMock(),
            time=mocker.MagicMock(),
            manure_treatment_config=mocker.MagicMock()
    )
    expected_pit_slope = 2.0

    # Act
    actual_pit_slope = slurry_storage_outdoor.pit_slope

    # Assert
    assert actual_pit_slope == expected_pit_slope


def test_calc_abc(mocker: MockFixture) -> None:
    """Unit test for _calc_abc() in slurry_storage_outdoor.py."""
    # Arrange
    slurry_storage_outdoor = SlurryStorageOutdoor(
            weather=mocker.MagicMock(),
            time=mocker.MagicMock(),
            manure_treatment_config=mocker.MagicMock()
    )
    pit_depth = 3.0
    patch_for_pit_depth = mocker.patch(
            'RUFAS.routines.manure.manure_treatments.slurry_storage_outdoor.SlurryStorageOutdoor.pit_depth',
            new_callable=PropertyMock,
            return_value=pit_depth)
    pit_slope = 2.0
    patch_for_pit_slope = mocker.patch(
            'RUFAS.routines.manure.manure_treatments.slurry_storage_outdoor.SlurryStorageOutdoor.pit_slope',
            new_callable=PropertyMock,
            return_value=pit_slope)
    treatment_volume = 100.0
    patch_for_treatment_volume = mocker.patch(
            'RUFAS.routines.manure.manure_treatments.slurry_storage_outdoor.SlurryStorageOutdoor.treatment_volume',
            new_callable=PropertyMock,
            return_value=treatment_volume)
    expected_a = 3 * pit_depth
    expected_b = -4 * pit_slope * (pit_depth ** 2)
    expected_c = 4 * (pit_slope ** 2) * (pit_depth ** 3) / 3 - treatment_volume

    # Act
    actual_a, actual_b, actual_c = slurry_storage_outdoor._calc_abc()

    # Assert
    assert actual_a == expected_a
    assert actual_b == expected_b
    assert actual_c == expected_c
    assert patch_for_pit_depth.call_count == 3
    assert patch_for_pit_slope.call_count == 2
    assert patch_for_treatment_volume.call_count == 1


def test_pit_width(mocker: MockFixture) -> None:
    """Unit test for pit_width() in slurry_storage_outdoor.py."""
    # Case 1: There is a current manure treatment daily input
    # Arrange
    slurry_storage_outdoor = SlurryStorageOutdoor(
            weather=mocker.MagicMock(),
            time=mocker.MagicMock(),
            manure_treatment_config=mocker.MagicMock()
    )
    mock_manure_treatment_daily_input = mocker.MagicMock()
    slurry_storage_outdoor._current_manure_treatment_daily_input = mock_manure_treatment_daily_input
    a, b, c = 2.0, 10.0, 4.0
    patch_for_calc_abc = mocker.patch(
            'RUFAS.routines.manure.manure_treatments.slurry_storage_outdoor.SlurryStorageOutdoor._calc_abc',
            return_value=(a, b, c))
    expected_pit_width = (-b + (b ** 2 - 4 * a * c) ** 0.5) / (2 * a)

    # Act
    actual_pit_width = slurry_storage_outdoor.pit_width

    # Assert
    assert actual_pit_width == expected_pit_width
    patch_for_calc_abc.assert_called_once()

    # ----------------------------------------

    # Case 2: There is no current manure treatment daily input
    # Arrange
    slurry_storage_outdoor = SlurryStorageOutdoor(
            weather=mocker.MagicMock(),
            time=mocker.MagicMock(),
            manure_treatment_config=mocker.MagicMock()
    )
    slurry_storage_outdoor._current_manure_treatment_daily_input = None

    # Act
    actual_pit_width = slurry_storage_outdoor.pit_width

    # Assert
    assert actual_pit_width == 0.0


def test_pit_length(mocker: MockFixture) -> None:
    """Unit test for pit_length() in slurry_storage_outdoor.py."""
    # Arrange
    slurry_storage_outdoor = SlurryStorageOutdoor(
            weather=mocker.MagicMock(),
            time=mocker.MagicMock(),
            manure_treatment_config=mocker.MagicMock()
    )
    pit_width = 10.0
    patch_for_pit_width = mocker.patch(
            'RUFAS.routines.manure.manure_treatments.slurry_storage_outdoor.SlurryStorageOutdoor.pit_width',
            new_callable=PropertyMock,
            return_value=pit_width)
    expected_pit_length = pit_width * 3

    # Act
    actual_pit_length = slurry_storage_outdoor.pit_length

    # Assert
    assert actual_pit_length == expected_pit_length


def test_pit_surface_area(mocker: MockFixture) -> None:
    """Unit test for pit_surface_area() in slurry_storage_outdoor.py."""
    # Arrange
    slurry_storage_outdoor = SlurryStorageOutdoor(
            weather=mocker.MagicMock(),
            time=mocker.MagicMock(),
            manure_treatment_config=mocker.MagicMock()
    )
    pit_width = 10.0
    patch_for_pit_width = mocker.patch(
            'RUFAS.routines.manure.manure_treatments.slurry_storage_outdoor.SlurryStorageOutdoor.pit_width',
            new_callable=PropertyMock,
            return_value=pit_width)
    pit_length = 30.0
    patch_for_pit_length = mocker.patch(
            'RUFAS.routines.manure.manure_treatments.slurry_storage_outdoor.SlurryStorageOutdoor.pit_length',
            new_callable=PropertyMock,
            return_value=pit_length)
    expected_pit_surface_area = pit_width * pit_length

    # Act
    actual_pit_surface_area = slurry_storage_outdoor.pit_surface_area

    # Assert
    assert actual_pit_surface_area == expected_pit_surface_area
    patch_for_pit_width.assert_called_once()
    patch_for_pit_length.assert_called_once()


def test_pit_volume(mocker: MockFixture) -> None:
    """Unit test for pit_volume() in slurry_storage_outdoor.py."""
    # Arrange
    slurry_storage_outdoor = SlurryStorageOutdoor(
            weather=mocker.MagicMock(),
            time=mocker.MagicMock(),
            manure_treatment_config=mocker.MagicMock()
    )
    pit_length = 30.0
    patch_for_pit_length = mocker.patch(
            'RUFAS.routines.manure.manure_treatments.slurry_storage_outdoor.SlurryStorageOutdoor.pit_length',
            new_callable=PropertyMock,
            return_value=pit_length)
    pit_width = 10.0
    patch_for_pit_width = mocker.patch(
            'RUFAS.routines.manure.manure_treatments.slurry_storage_outdoor.SlurryStorageOutdoor.pit_width',
            new_callable=PropertyMock,
            return_value=pit_width)
    pit_depth = 2.0
    patch_for_pit_depth = mocker.patch(
            'RUFAS.routines.manure.manure_treatments.slurry_storage_outdoor.SlurryStorageOutdoor.pit_depth',
            new_callable=PropertyMock,
            return_value=pit_depth)
    pit_slope = 0.1
    patch_for_pit_slope = mocker.patch(
            'RUFAS.routines.manure.manure_treatments.slurry_storage_outdoor.SlurryStorageOutdoor.pit_slope',
            new_callable=PropertyMock,
            return_value=pit_slope)
    expected_pit_volume = (pit_length * pit_width * pit_depth
                           - (pit_slope * (pit_depth ** 2)) * (pit_length + pit_width)
                           + (4 * pit_slope * (pit_depth ** 3) / 3))

    # Act
    actual_pit_volume = slurry_storage_outdoor.pit_volume

    # Assert
    assert actual_pit_volume == expected_pit_volume
    assert patch_for_pit_length.call_count == 2
    assert patch_for_pit_width.call_count == 2
    assert patch_for_pit_depth.call_count == 3
    assert patch_for_pit_slope.call_count == 2


def test_precipitation_volume(mocker: MockFixture) -> None:
    """Unit test for precipitation_volume() in slurry_storage_outdoor.py."""
    # Arrange
    slurry_storage_outdoor = SlurryStorageOutdoor(
            weather=mocker.MagicMock(),
            time=mocker.MagicMock(),
            manure_treatment_config=mocker.MagicMock()
    )
    rainfall = 10.0
    patch_for_get_current_day_rainfall = mocker.patch(
            'RUFAS.routines.manure.manure_treatments.slurry_storage_outdoor.SlurryStorageOutdoor'
            '._get_current_day_rainfall',
            return_value=rainfall)
    pit_surface_area = 300.0
    patch_for_pit_surface_area = mocker.patch(
            'RUFAS.routines.manure.manure_treatments.slurry_storage_outdoor.SlurryStorageOutdoor.pit_surface_area',
            new_callable=PropertyMock,
            return_value=pit_surface_area)
    expected_precipitation_volume = rainfall * pit_surface_area

    # Act
    actual_precipitation_volume = slurry_storage_outdoor.precipitation_volume

    # Assert
    assert actual_precipitation_volume == expected_precipitation_volume
    patch_for_get_current_day_rainfall.assert_called_once()
    patch_for_pit_surface_area.assert_called_once()


def test_freeboard_volume(mocker: MockFixture) -> None:
    """Unit test for freeboard_volume() in slurry_storage_outdoor.py."""
    # Arrange
    slurry_storage_outdoor = SlurryStorageOutdoor(
            weather=mocker.MagicMock(),
            time=mocker.MagicMock(),
            manure_treatment_config=mocker.MagicMock()
    )
    slurry_storage_outdoor.freeboard_input = freeboard_input = 10.0
    pit_surface_area = 300.0
    patch_for_pit_surface_area = mocker.patch(
            'RUFAS.routines.manure.manure_treatments.slurry_storage_outdoor.SlurryStorageOutdoor.pit_surface_area',
            new_callable=PropertyMock,
            return_value=pit_surface_area)
    expected_freeboard_volume = freeboard_input * pit_surface_area

    # Act
    actual_freeboard_volume = slurry_storage_outdoor.freeboard_volume

    # Assert
    assert actual_freeboard_volume == expected_freeboard_volume
    patch_for_pit_surface_area.assert_called_once()
