import pytest
from pytest import approx

from RUFAS.routines.manure.manure_treatments.manure_treatment_configs import (
    DefaultManureTreatmentConfigFactory, ManureTreatmentConfig)
from RUFAS.routines.manure.manure_treatments.manure_treatment_daily_output import \
    ManureTreatmentDailyOutput
from RUFAS.routines.manure.manure_treatments.manure_treatment_types import \
    ManureTreatmentType

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


def test_anaerobic_digestion_and_lagoon_config() -> None:
    # Act
    anaerobic_digestion_and_lagoon_config = DefaultManureTreatmentConfigFactory.ANAEROBIC_DIGESTION_AND_LAGOON_CONFIG

    # Assert
    assert anaerobic_digestion_and_lagoon_config.total_solids_removal_efficiency_for_treatment == approx(0.45)
    assert anaerobic_digestion_and_lagoon_config.volatile_solids_removal_efficiency_for_treatment == approx(0.40)
    assert anaerobic_digestion_and_lagoon_config.nitrogen_removal_efficiency_for_treatment == approx(0.0)
    assert anaerobic_digestion_and_lagoon_config.total_ammoniacal_nitrogen_removal_efficiency_for_treatment == \
           approx(0.1)
    assert anaerobic_digestion_and_lagoon_config.phosphorus_removal_efficiency_for_treatment == approx(0.0)
    assert anaerobic_digestion_and_lagoon_config.potassium_removal_efficiency_for_treatment == approx(0.0)

    assert anaerobic_digestion_and_lagoon_config.storage_time_period == 365
    assert anaerobic_digestion_and_lagoon_config.freeboard_input == approx(0.3048)
    assert anaerobic_digestion_and_lagoon_config.hydraulic_retention_time == 25
    assert anaerobic_digestion_and_lagoon_config.sludge_accumulation_period == 1.0
    assert anaerobic_digestion_and_lagoon_config.sludge_accumulation_volume_fraction == approx(0.03)

    assert anaerobic_digestion_and_lagoon_config.top_cover_volume_fraction == approx(0.2)
    assert anaerobic_digestion_and_lagoon_config.biogas_generation_ratio == approx(0.38)
    assert anaerobic_digestion_and_lagoon_config.methane_generation_ratio == approx(0.65)
    assert anaerobic_digestion_and_lagoon_config.evaporation_fraction == approx(0.02)
    assert anaerobic_digestion_and_lagoon_config.anaerobic_digestion_temperature_set_point == approx(37.5)
    assert anaerobic_digestion_and_lagoon_config.anaerobic_digestion_temperature_celsius == approx(37.5)


@pytest.mark.parametrize(
        "manure_treatment_type, expected_manure_treatment_config",
        [
            (ManureTreatmentType.SLURRY_STORAGE_UNDERFLOOR,
             DefaultManureTreatmentConfigFactory.SLURRY_STORAGE_UNDERFLOOR_CONFIG),
            (ManureTreatmentType.SLURRY_STORAGE_OUTDOOR,
             DefaultManureTreatmentConfigFactory.SLURRY_STORAGE_OUTDOOR_CONFIG),
            (ManureTreatmentType.ANAEROBIC_DIGESTION, DefaultManureTreatmentConfigFactory.ANAEROBIC_DIGESTION_CONFIG),
            (ManureTreatmentType.ANAEROBIC_LAGOON, DefaultManureTreatmentConfigFactory.ANAEROBIC_LAGOON_CONFIG),
            (ManureTreatmentType.ANAEROBIC_DIGESTION_AND_LAGOON,
             DefaultManureTreatmentConfigFactory.ANAEROBIC_DIGESTION_AND_LAGOON_CONFIG),
            (ManureTreatmentType.ANAEROBIC_DIGESTION_AND_LAGOON_WITH_SPLIT,
             DefaultManureTreatmentConfigFactory.ANAEROBIC_DIGESTION_AND_LAGOON_CONFIG),
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
