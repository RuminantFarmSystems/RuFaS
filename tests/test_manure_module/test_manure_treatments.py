import dataclasses
from typing import Type
from typing import Union

import pytest
from mock.mock import PropertyMock, call
from pytest import approx
from pytest_mock import MockFixture

from RUFAS.general_constants import GeneralConstants
from RUFAS.routines.manure.constants_and_units.manure_constants import ManureConstants
from RUFAS.routines.manure.gas_emissions.calculator import GasEmissionsCalculator
from RUFAS.routines.manure.manure_treatments.anaerobic_digestion import (
    AnaerobicDigestion,
)
from RUFAS.routines.manure.manure_treatments.anaerobic_digestion_and_lagoon import (
    AnaerobicDigestionAndLagoon,
)
from RUFAS.routines.manure.manure_treatments.anaerobic_lagoon import AnaerobicLagoon
from RUFAS.routines.manure.manure_treatments.base_manure_treatment import (
    BaseManureTreatment,
)
from RUFAS.routines.manure.manure_treatments.compost_bedded_pack_barn import (
    CompostBeddedPackBarn,
)
from RUFAS.routines.manure.manure_treatments.manure_treatment_configs import (
    DefaultManureTreatmentConfigFactory,
)
from RUFAS.routines.manure.manure_treatments.manure_treatment_configs import (
    ManureTreatmentConfig,
)
from RUFAS.routines.manure.manure_treatments.manure_treatment_daily_output import (
    ManureTreatmentDailyOutput,
)
from RUFAS.routines.manure.manure_treatments.manure_treatment_factory import (
    ManureTreatmentFactory,
)
from RUFAS.routines.manure.manure_treatments.manure_treatment_types import (
    ManureTreatmentType,
)
from RUFAS.routines.manure.manure_treatments.slurry_storage_outdoor import (
    SlurryStorageOutdoor,
)
from RUFAS.routines.manure.manure_treatments.slurry_storage_underfloor import (
    SlurryStorageUnderfloor,
)
from RUFAS.routines.manure.protocols.liquid_manure_portion_protocol import (
    LiquidManurePortionProtocol,
)


# Test ManureTreatmentDailyOutput
# ===============================


def test_manure_treatment_daily_output() -> None:
    """
    Unit test for the __init__() method in manure_treatment_daily_output.py
    """

    # Arrange
    expected_values = {
        "pen_id": 1,
        "simulation_day": 2,
        "liquid_manure_total_ammoniacal_nitrogen": 3.0,
        "liquid_manure_nitrogen": 4.0,
        "liquid_manure_total_solids": 5.0,
        "liquid_manure_total_volatile_solids": 6.0,
        "liquid_manure_phosphorus": 7.0,
        "liquid_manure_potassium": 8.0,
        "daily_final_manure_volume": 9.0,
        "storage_methane": 11.0,
        "storage_ammonia": 12.0,
        "storage_nitrous_oxide": 13.0,
        "sludge_manure_total_solids": 14.0,
        "sludge_manure_total_volatile_solids": 15.0,
        "sludge_manure_nitrogen": 16.0,
        "sludge_manure_phosphorus": 17.0,
        "sludge_manure_potassium": 18.0,
        "sludge_manure_daily_volume": 19.0,
        "solid_manure_total_solids": 20.0,
        "solid_manure_total_volatile_solids": 21.0,
        "solid_manure_nitrogen": 22.0,
        "solid_manure_inorganic_nitrogen": 23.0,
        "solid_manure_organic_nitrogen": 24.0,
        "solid_manure_inorganic_nitrogen_ammonium": 25.0,
        "solid_manure_phosphorus": 26.0,
        "solid_manure_water_extractable_inorganic_phosphorus": 27.0,
        "solid_manure_water_extractable_organic_phosphorus": 28.0,
        "solid_manure_non_water_extractable_inorganic_phosphorus": 29.0,
        "solid_manure_non_water_extractable_organic_phosphorus": 30.0,
        "solid_manure_potassium": 31.0,
        "solid_manure_daily_mass": 32.0,
        "biogas": 33.0,
        "biogas_energy_content": 34.0,
        "methane_generation_volume": 35.0,
        "heating_input_energy": 36.0,
        "evaporated_water": 37.0,
        "minimum_digester_volume": 38.0,
        "top_cover_volume": 39.0
    }

    # Act
    manure_treatment_daily_output = ManureTreatmentDailyOutput(**expected_values)

    # Assert
    for key, value in expected_values.items():
        assert getattr(manure_treatment_daily_output, key) == approx(value), key

    assert manure_treatment_daily_output.liquid_manure_daily_volume == \
           approx(expected_values["daily_final_manure_volume"])


def test_manure_treatment_daily_output_add() -> None:
    """
    Unit test for the __add__() method in manure_treatment_daily_output.py
    """

    # Case 1: Add a ManureTreatmentDailyOutput to a non-ManureTreatmentDailyOutput object.

    # Arrange
    manure_treatment_daily_output = ManureTreatmentDailyOutput()

    # Act and Assert
    with pytest.raises(TypeError) as e:
        manure_treatment_daily_output + 1
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
        daily_final_manure_volume=9.0,
        liquid_manure_daily_volume=10.0,
        storage_methane=11.0,
        storage_ammonia=12.0,
        storage_nitrous_oxide=13.0,
        sludge_manure_total_solids=14.0,
        sludge_manure_total_volatile_solids=15.0,
        sludge_manure_nitrogen=16.0,
        sludge_manure_phosphorus=17.0,
        sludge_manure_potassium=18.0,
        sludge_manure_daily_volume=19.0,
        solid_manure_total_solids=20.0,
        solid_manure_total_volatile_solids=21.0,
        solid_manure_nitrogen=22.0,
        solid_manure_inorganic_nitrogen=23.0,
        solid_manure_organic_nitrogen=24.0,
        solid_manure_inorganic_nitrogen_ammonium=25.0,
        solid_manure_phosphorus=26.0,
        solid_manure_water_extractable_inorganic_phosphorus=27.0,
        solid_manure_water_extractable_organic_phosphorus=28.0,
        solid_manure_non_water_extractable_inorganic_phosphorus=29.0,
        solid_manure_non_water_extractable_organic_phosphorus=30.0,
        solid_manure_potassium=31.0,
        solid_manure_daily_mass=32.0,
        biogas=33.0,
        biogas_energy_content=34.0,
        methane_generation_volume=35.0,
        heating_input_energy=36.0,
        evaporated_water=37.0,
        minimum_digester_volume=38.0,
        top_cover_volume=39.0,
    )

    manure_treatment_daily_output_2 = ManureTreatmentDailyOutput(
        pen_id=3,
        simulation_day=4,
        liquid_manure_total_ammoniacal_nitrogen=100.0,
        liquid_manure_nitrogen=101.0,
        liquid_manure_total_solids=102.0,
        liquid_manure_total_volatile_solids=103.0,
        liquid_manure_phosphorus=104.0,
        liquid_manure_potassium=105.0,
        daily_final_manure_volume=106.0,
        liquid_manure_daily_volume=107.0,
        storage_methane=108.0,
        storage_ammonia=109.0,
        storage_nitrous_oxide=110.0,
        sludge_manure_total_solids=111.0,
        sludge_manure_total_volatile_solids=112.0,
        sludge_manure_nitrogen=113.0,
        sludge_manure_phosphorus=114.0,
        sludge_manure_potassium=115.0,
        sludge_manure_daily_volume=116.0,
        solid_manure_total_solids=117.0,
        solid_manure_total_volatile_solids=118.0,
        solid_manure_nitrogen=119.0,
        solid_manure_inorganic_nitrogen=120.0,
        solid_manure_organic_nitrogen=121.0,
        solid_manure_inorganic_nitrogen_ammonium=122.0,
        solid_manure_phosphorus=123.0,
        solid_manure_water_extractable_inorganic_phosphorus=124.0,
        solid_manure_water_extractable_organic_phosphorus=125.0,
        solid_manure_non_water_extractable_inorganic_phosphorus=126.0,
        solid_manure_non_water_extractable_organic_phosphorus=127.0,
        solid_manure_potassium=128.0,
        solid_manure_daily_mass=129.0,
        biogas=130.0,
        biogas_energy_content=131.0,
        methane_generation_volume=132.0,
        heating_input_energy=133.0,
        evaporated_water=134.0,
        minimum_digester_volume=135.0,
        top_cover_volume=136.0,
    )

    # Act
    sum_of_manure_treatment_daily_outputs = manure_treatment_daily_output_1 + manure_treatment_daily_output_2

    # Assert
    assert sum_of_manure_treatment_daily_outputs == ManureTreatmentDailyOutput(
        pen_id=4,
        simulation_day=6,
        liquid_manure_total_ammoniacal_nitrogen=103.0,
        liquid_manure_nitrogen=105.0,
        liquid_manure_total_solids=107.0,
        liquid_manure_total_volatile_solids=109.0,
        liquid_manure_phosphorus=111.0,
        liquid_manure_potassium=113.0,
        liquid_manure_daily_volume=117.0,
        daily_final_manure_volume=115.0,
        storage_methane=119.0,
        storage_ammonia=121.0,
        storage_nitrous_oxide=123.0,
        sludge_manure_total_solids=125.0,
        sludge_manure_total_volatile_solids=127.0,
        sludge_manure_nitrogen=129.0,
        sludge_manure_phosphorus=131.0,
        sludge_manure_potassium=133.0,
        sludge_manure_daily_volume=135.0,
        solid_manure_total_solids=137.0,
        solid_manure_daily_mass=161.0,
        solid_manure_total_volatile_solids=139.0,
        solid_manure_nitrogen=141.0,
        solid_manure_inorganic_nitrogen=143.0,
        solid_manure_organic_nitrogen=145.0,
        solid_manure_inorganic_nitrogen_ammonium=147.0,
        solid_manure_phosphorus=149.0,
        solid_manure_water_extractable_inorganic_phosphorus=151.0,
        solid_manure_water_extractable_organic_phosphorus=153.0,
        solid_manure_non_water_extractable_inorganic_phosphorus=155.0,
        solid_manure_non_water_extractable_organic_phosphorus=157.0,
        solid_manure_potassium=159.0,
        biogas=163.0,
        biogas_energy_content=165.0,
        methane_generation_volume=167.0,
        heating_input_energy=169.0,
        evaporated_water=171.0,
        minimum_digester_volume=173.0,
        top_cover_volume=175.0,
    )


def test_set_daily_final_manure_volume() -> None:
    """Unit test for set_daily_final_manure_volume() method in manure_treatment_daily_output.py"""

    # Arrange
    manure_treatment_daily_output = ManureTreatmentDailyOutput(
        daily_final_manure_volume=1.0,
    )
    expected_daily_final_manure_volume = 2.0

    # Assert before
    assert manure_treatment_daily_output.daily_final_manure_volume == approx(1.0)
    assert manure_treatment_daily_output.liquid_manure_daily_volume == approx(1.0)

    # Act
    manure_treatment_daily_output.set_daily_final_manure_volume(
        expected_daily_final_manure_volume
    )

    # Assert after
    assert manure_treatment_daily_output.daily_final_manure_volume == approx(
        expected_daily_final_manure_volume
    )
    assert manure_treatment_daily_output.liquid_manure_daily_volume == approx(
        expected_daily_final_manure_volume
    )


def test_manure_treatment_daily_output_clone() -> None:
    """Unit test for clone() method in manure_treatment_daily_output.py"""
    # Arrange
    manure_treatment_daily_output = ManureTreatmentDailyOutput(
        pen_id=1,
        simulation_day=2,
        liquid_manure_total_ammoniacal_nitrogen=3.0,
        liquid_manure_nitrogen=4.0,
        liquid_manure_total_solids=5.0,
        liquid_manure_total_volatile_solids=6.0,
        liquid_manure_phosphorus=7.0,
        liquid_manure_potassium=8.0,
        daily_final_manure_volume=9.0,
        liquid_manure_daily_volume=10.0,
        storage_methane=11.0,
        storage_ammonia=12.0,
        storage_nitrous_oxide=13.0,
        sludge_manure_total_solids=14.0,
        sludge_manure_total_volatile_solids=15.0,
        sludge_manure_nitrogen=16.0,
        sludge_manure_phosphorus=17.0,
        sludge_manure_potassium=18.0,
        sludge_manure_daily_volume=19.0,
        solid_manure_total_solids=20.0,
        solid_manure_total_volatile_solids=21.0,
        solid_manure_nitrogen=22.0,
        solid_manure_inorganic_nitrogen=23.0,
        solid_manure_organic_nitrogen=24.0,
        solid_manure_inorganic_nitrogen_ammonium=25.0,
        solid_manure_phosphorus=26.0,
        solid_manure_water_extractable_inorganic_phosphorus=27.0,
        solid_manure_water_extractable_organic_phosphorus=28.0,
        solid_manure_non_water_extractable_inorganic_phosphorus=29.0,
        solid_manure_non_water_extractable_organic_phosphorus=30.0,
        solid_manure_potassium=31.0,
        solid_manure_daily_mass=32.0,
        biogas=33.0,
        biogas_energy_content=34.0,
        methane_generation_volume=35.0,
        heating_input_energy=36.0,
        evaporated_water=37.0,
        minimum_digester_volume=38.0,
        top_cover_volume=39.0,
    )

    # Act
    manure_treatment_daily_output_clone = manure_treatment_daily_output.clone()

    # Assert
    assert manure_treatment_daily_output_clone == manure_treatment_daily_output
    assert manure_treatment_daily_output_clone is not manure_treatment_daily_output


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
    assert (
            manure_treatment_config.total_solids_removal_efficiency_for_treatment
            == approx(0.1)
    )
    assert (
            manure_treatment_config.volatile_solids_removal_efficiency_for_treatment
            == approx(0.2)
    )
    assert manure_treatment_config.nitrogen_removal_efficiency_for_treatment == approx(
        0.3
    )
    assert (
            manure_treatment_config.total_ammoniacal_nitrogen_removal_efficiency_for_treatment
            == approx(0.4)
    )
    assert (
            manure_treatment_config.phosphorus_removal_efficiency_for_treatment
            == approx(0.5)
    )
    assert manure_treatment_config.potassium_removal_efficiency_for_treatment == approx(
        0.6
    )

    assert manure_treatment_config.hydraulic_retention_time == 10
    assert manure_treatment_config.sludge_accumulation_period == 20
    assert manure_treatment_config.sludge_accumulation_volume_fraction == approx(0.15)
    assert manure_treatment_config.top_cover_volume_fraction == approx(0.25)
    assert manure_treatment_config.biogas_generation_ratio == approx(0.35)
    assert manure_treatment_config.methane_generation_ratio == approx(0.45)

    assert manure_treatment_config.evaporation_fraction == approx(0.55)
    assert manure_treatment_config.anaerobic_digestion_temperature_set_point == approx(
        60.0
    )
    assert manure_treatment_config.anaerobic_digestion_temperature_celsius == approx(
        70.0
    )

    assert manure_treatment_config.storage_time_period == 30
    assert manure_treatment_config.freeboard_input == approx(0.65)


# Test DefaultManureTreatmentConfigFactory
# ========================================


def test_slurry_storage_underfloor_default_config() -> None:
    """Tests the default values of the slurry storage underfloor manure treatment config."""
    # Arrange
    slurry_storage_underfloor_config = (
        DefaultManureTreatmentConfigFactory.SLURRY_STORAGE_UNDERFLOOR_CONFIG
    )

    # Assert
    assert (
            slurry_storage_underfloor_config.total_solids_removal_efficiency_for_treatment
            == approx(0.10)
    )
    assert (
            slurry_storage_underfloor_config.volatile_solids_removal_efficiency_for_treatment
            == approx(0.20)
    )
    assert (
            slurry_storage_underfloor_config.nitrogen_removal_efficiency_for_treatment
            == approx(0.10)
    )
    assert (
            slurry_storage_underfloor_config.total_ammoniacal_nitrogen_removal_efficiency_for_treatment
            == approx(0.45)
    )
    assert (
            slurry_storage_underfloor_config.phosphorus_removal_efficiency_for_treatment
            == approx(0.05)
    )
    assert (
            slurry_storage_underfloor_config.potassium_removal_efficiency_for_treatment
            == approx(0.05)
    )
    assert slurry_storage_underfloor_config.storage_time_period == 120


def test_slurry_storage_outdoor_default_config() -> None:
    """Tests the default values of the slurry storage outdoor manure treatment config."""
    # Act
    slurry_storage_outdoor_config = (
        DefaultManureTreatmentConfigFactory.SLURRY_STORAGE_OUTDOOR_CONFIG
    )

    # Assert
    assert (
            slurry_storage_outdoor_config.total_solids_removal_efficiency_for_treatment
            == approx(0.10)
    )
    assert (
            slurry_storage_outdoor_config.volatile_solids_removal_efficiency_for_treatment
            == approx(0.20)
    )
    assert (
            slurry_storage_outdoor_config.nitrogen_removal_efficiency_for_treatment
            == approx(0.10)
    )
    assert (
            slurry_storage_outdoor_config.total_ammoniacal_nitrogen_removal_efficiency_for_treatment
            == approx(0.45)
    )
    assert (
            slurry_storage_outdoor_config.phosphorus_removal_efficiency_for_treatment
            == approx(0.05)
    )
    assert (
            slurry_storage_outdoor_config.potassium_removal_efficiency_for_treatment
            == approx(0.05)
    )
    assert slurry_storage_outdoor_config.storage_time_period == 120
    assert slurry_storage_outdoor_config.freeboard_input == approx(0.3048)


def test_anaerobic_digestion_default_config() -> None:
    """Tests the default values of the anaerobic digestion manure treatment config."""
    # Act
    anaerobic_digestion_config = (
        DefaultManureTreatmentConfigFactory.ANAEROBIC_DIGESTION_CONFIG
    )

    # Assert
    assert (
            anaerobic_digestion_config.total_solids_removal_efficiency_for_treatment
            == approx(0.45)
    )
    assert (
            anaerobic_digestion_config.volatile_solids_removal_efficiency_for_treatment
            == approx(0.40)
    )
    assert (
            anaerobic_digestion_config.nitrogen_removal_efficiency_for_treatment
            == approx(0.0)
    )
    assert (
            anaerobic_digestion_config.total_ammoniacal_nitrogen_removal_efficiency_for_treatment
            == approx(0.1)
    )
    assert (
            anaerobic_digestion_config.phosphorus_removal_efficiency_for_treatment
            == approx(0.0)
    )
    assert (
            anaerobic_digestion_config.potassium_removal_efficiency_for_treatment
            == approx(0.0)
    )

    assert anaerobic_digestion_config.hydraulic_retention_time == 25
    assert anaerobic_digestion_config.sludge_accumulation_period == 1.0
    assert anaerobic_digestion_config.sludge_accumulation_volume_fraction == approx(
        0.03
    )
    assert anaerobic_digestion_config.top_cover_volume_fraction == approx(0.2)
    assert anaerobic_digestion_config.biogas_generation_ratio == approx(0.38)
    assert anaerobic_digestion_config.methane_generation_ratio == approx(0.65)

    assert anaerobic_digestion_config.evaporation_fraction == approx(0.02)
    assert (
            anaerobic_digestion_config.anaerobic_digestion_temperature_set_point
            == approx(37.5)
    )
    assert anaerobic_digestion_config.anaerobic_digestion_temperature_celsius == approx(
        37.5
    )


def test_anaerobic_lagoon_default_config() -> None:
    # Act
    anaerobic_lagoon_config = (
        DefaultManureTreatmentConfigFactory.ANAEROBIC_LAGOON_CONFIG
    )

    # Assert
    assert (
            anaerobic_lagoon_config.total_solids_removal_efficiency_for_treatment
            == approx(0.75)
    )
    assert (
            anaerobic_lagoon_config.volatile_solids_removal_efficiency_for_treatment
            == approx(0.85)
    )
    assert anaerobic_lagoon_config.nitrogen_removal_efficiency_for_treatment == approx(
        0.65
    )
    assert (
            anaerobic_lagoon_config.total_ammoniacal_nitrogen_removal_efficiency_for_treatment
            == approx(0.7)
    )
    assert (
            anaerobic_lagoon_config.phosphorus_removal_efficiency_for_treatment
            == approx(0.6)
    )
    assert anaerobic_lagoon_config.potassium_removal_efficiency_for_treatment == approx(
        0.2
    )

    assert anaerobic_lagoon_config.hydraulic_retention_time == 365
    assert anaerobic_lagoon_config.sludge_accumulation_period == 10.0
    assert anaerobic_lagoon_config.sludge_accumulation_volume_fraction == approx(
        0.00251
    )

    assert anaerobic_lagoon_config.storage_time_period == 365
    assert anaerobic_lagoon_config.freeboard_input == approx(0.3048)


@pytest.mark.parametrize(
    "manure_treatment_type, expected_manure_treatment_config",
    [
        (
                ManureTreatmentType.SLURRY_STORAGE_UNDERFLOOR,
                DefaultManureTreatmentConfigFactory.SLURRY_STORAGE_UNDERFLOOR_CONFIG,
        ),
        (
                ManureTreatmentType.SLURRY_STORAGE_OUTDOOR,
                DefaultManureTreatmentConfigFactory.SLURRY_STORAGE_OUTDOOR_CONFIG,
        ),
        (
                ManureTreatmentType.ANAEROBIC_DIGESTION,
                DefaultManureTreatmentConfigFactory.ANAEROBIC_DIGESTION_CONFIG,
        ),
        (
                ManureTreatmentType.ANAEROBIC_LAGOON,
                DefaultManureTreatmentConfigFactory.ANAEROBIC_LAGOON_CONFIG,
        ),
        (
                ManureTreatmentType.ANAEROBIC_DIGESTION_AND_LAGOON,
                (
                        DefaultManureTreatmentConfigFactory.ANAEROBIC_DIGESTION_CONFIG,
                        DefaultManureTreatmentConfigFactory.ANAEROBIC_LAGOON_CONFIG,
                ),
        ),
        (
                ManureTreatmentType.ANAEROBIC_DIGESTION_AND_LAGOON_WITH_SPLIT,
                (
                        DefaultManureTreatmentConfigFactory.ANAEROBIC_DIGESTION_CONFIG,
                        DefaultManureTreatmentConfigFactory.ANAEROBIC_LAGOON_CONFIG,
                ),
        ),
    ],
)
def test_default_manure_treatment_config_factory_get_instance(
        manure_treatment_type: ManureTreatmentType,
        expected_manure_treatment_config: ManureTreatmentConfig,
) -> None:
    # Act
    manure_treatment_config = DefaultManureTreatmentConfigFactory.get_instance(
        manure_treatment_type
    )

    # Assert
    assert manure_treatment_config == expected_manure_treatment_config


# Test ManureTreatmentType
# ========================


@pytest.mark.parametrize(
    "manure_treatment_type_name, expected_manure_treatment_type",
    [
        ("slurry storage underfloor", ManureTreatmentType.SLURRY_STORAGE_UNDERFLOOR),
        ("slurry storage outdoor", ManureTreatmentType.SLURRY_STORAGE_OUTDOOR),
        ("anaerobic digestion", ManureTreatmentType.ANAEROBIC_DIGESTION),
        ("anaerobic lagoon", ManureTreatmentType.ANAEROBIC_LAGOON),
        (
                "anaerobic digestion and lagoon",
                ManureTreatmentType.ANAEROBIC_DIGESTION_AND_LAGOON,
        ),
        (
                "anaerobic digestion and lagoon with split",
                ManureTreatmentType.ANAEROBIC_DIGESTION_AND_LAGOON_WITH_SPLIT,
        ),
        ("slurry_storage_underfloor", ManureTreatmentType.SLURRY_STORAGE_UNDERFLOOR),
        ("slurry_storage_outdoor", ManureTreatmentType.SLURRY_STORAGE_OUTDOOR),
        ("anaerobic_digestion", ManureTreatmentType.ANAEROBIC_DIGESTION),
        ("anaerobic_lagoon", ManureTreatmentType.ANAEROBIC_LAGOON),
        (
                "anaerobic_digestion_and_lagoon",
                ManureTreatmentType.ANAEROBIC_DIGESTION_AND_LAGOON,
        ),
        (
                "anaerobic_digestion_and_lagoon_with_split",
                ManureTreatmentType.ANAEROBIC_DIGESTION_AND_LAGOON_WITH_SPLIT,
        ),
        ("dummy", ManureTreatmentType.SLURRY_STORAGE_UNDERFLOOR),
    ],
)
def test_manure_treatment_type_get_type(
        manure_treatment_type_name: str, expected_manure_treatment_type: ManureTreatmentType
) -> None:
    # Assert
    assert (
            ManureTreatmentType.get_type(manure_treatment_type_name)
            == expected_manure_treatment_type
    )


# Test ManureTreatmentFactory
# ===========================


@pytest.mark.parametrize(
    "manure_treatment_type_name, custom_manure_treatment_config,"
    "expected_manure_treatment_class,expected_manure_treatment_config",
    [
        (
                "slurry storage underfloor",
                None,
                SlurryStorageUnderfloor,
                DefaultManureTreatmentConfigFactory.SLURRY_STORAGE_UNDERFLOOR_CONFIG,
        ),
        (
                "slurry storage underfloor",
                DefaultManureTreatmentConfigFactory.SLURRY_STORAGE_UNDERFLOOR_CONFIG,
                SlurryStorageUnderfloor,
                DefaultManureTreatmentConfigFactory.SLURRY_STORAGE_UNDERFLOOR_CONFIG,
        ),
        (
                "slurry storage outdoor",
                None,
                SlurryStorageOutdoor,
                DefaultManureTreatmentConfigFactory.SLURRY_STORAGE_OUTDOOR_CONFIG,
        ),
        (
                "slurry storage outdoor",
                DefaultManureTreatmentConfigFactory.SLURRY_STORAGE_OUTDOOR_CONFIG,
                SlurryStorageOutdoor,
                DefaultManureTreatmentConfigFactory.SLURRY_STORAGE_OUTDOOR_CONFIG,
        ),
        (
                "anaerobic lagoon",
                None,
                AnaerobicLagoon,
                DefaultManureTreatmentConfigFactory.ANAEROBIC_LAGOON_CONFIG,
        ),
        (
                "anaerobic lagoon",
                DefaultManureTreatmentConfigFactory.ANAEROBIC_LAGOON_CONFIG,
                AnaerobicLagoon,
                DefaultManureTreatmentConfigFactory.ANAEROBIC_LAGOON_CONFIG,
        ),
        (
                "anaerobic digestion",
                None,
                AnaerobicDigestion,
                DefaultManureTreatmentConfigFactory.ANAEROBIC_DIGESTION_CONFIG,
        ),
        (
                "anaerobic digestion",
                DefaultManureTreatmentConfigFactory.ANAEROBIC_DIGESTION_CONFIG,
                AnaerobicDigestion,
                DefaultManureTreatmentConfigFactory.ANAEROBIC_DIGESTION_CONFIG,
        ),
        (
                "anaerobic digestion and lagoon",
                None,
                AnaerobicDigestionAndLagoon,
                (
                        DefaultManureTreatmentConfigFactory.ANAEROBIC_DIGESTION_CONFIG,
                        DefaultManureTreatmentConfigFactory.ANAEROBIC_LAGOON_CONFIG,
                ),
        ),
        (
                "anaerobic digestion and lagoon",
                (
                        DefaultManureTreatmentConfigFactory.ANAEROBIC_DIGESTION_CONFIG,
                        DefaultManureTreatmentConfigFactory.ANAEROBIC_LAGOON_CONFIG,
                ),
                AnaerobicDigestionAndLagoon,
                (
                        DefaultManureTreatmentConfigFactory.ANAEROBIC_DIGESTION_CONFIG,
                        DefaultManureTreatmentConfigFactory.ANAEROBIC_LAGOON_CONFIG,
                ),
        ),
    ],
)
def test_manure_treatment_factory_get_instance(
        manure_treatment_type_name: str,
        custom_manure_treatment_config: ManureTreatmentConfig,
        expected_manure_treatment_class: Type[BaseManureTreatment],
        expected_manure_treatment_config: ManureTreatmentConfig,
        mocker: MockFixture,
) -> None:
    """Unit test for get_instance() method of ManureTreatmentFactory class."""
    # Arrange
    mock_weather = mocker.MagicMock()
    mock_time = mocker.MagicMock()

    # Act
    manure_treatment = ManureTreatmentFactory.get_instance(
        manure_treatment_type_name,
        mock_weather,
        mock_time,
        custom_manure_treatment_config,
    )

    # Assert
    assert isinstance(manure_treatment, expected_manure_treatment_class)
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
    "manure_treatment_type_name",
    [
        "slurry storage underfloor",
        "slurry storage outdoor",
        "anaerobic digestion",
        "anaerobic lagoon",
        "anaerobic digestion and lagoon",
        "anaerobic digestion and lagoon with split",
        "compost bedded pack barn",
    ],
)
def test_initialize_private_attributes_during_update(
        manure_treatment_type_name: str, mocker: MockFixture
) -> None:
    # Arrange
    manure_treatment = ManureTreatmentFactory.get_instance(
        manure_treatment_type_name=manure_treatment_type_name,
        weather=mocker.MagicMock(),
        time=mocker.MagicMock(),
        custom_manure_treatment_config=None,
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
        manure_separator=manure_separator,
    )

    # Assert
    assert manure_treatment._sim_day == sim_day
    assert manure_treatment._current_pen == current_pen
    assert manure_treatment._manure_handler_daily_output == manure_handler_daily_output
    assert (
            manure_treatment._current_manure_treatment_daily_input
            == manure_treatment_daily_input
    )
    assert manure_treatment._manure_separator == manure_separator


@pytest.mark.parametrize(
    "manure_treatment_type_name",
    [
        "slurry storage underfloor",
        "slurry storage outdoor",
        "anaerobic digestion",
        "anaerobic lagoon",
        "compost bedded pack barn",
    ],
)
def test_initialize_daily_output_during_update(
        manure_treatment_type_name: str, mocker: MockFixture
) -> None:
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
            total_ammoniacal_nitrogen_removal_efficiency_for_treatment
        ),
        nitrogen_removal_efficiency_for_treatment=nitrogen_removal_efficiency_for_treatment,
        phosphorus_removal_efficiency_for_treatment=phosphorus_removal_efficiency_for_treatment,
        potassium_removal_efficiency_for_treatment=potassium_removal_efficiency_for_treatment,
        volatile_solids_removal_efficiency_for_treatment=volatile_solids_removal_efficiency_for_treatment,
        total_solids_removal_efficiency_for_treatment=total_solids_removal_efficiency_for_treatment,
    )
    manure_treatment = ManureTreatmentFactory.get_instance(
        manure_treatment_type_name=manure_treatment_type_name,
        weather=mocker.MagicMock(),
        time=mocker.MagicMock(),
        custom_manure_treatment_config=custom_manure_treatment_config,
    )
    manure_treatment_daily_input: LiquidManurePortionProtocol = mocker.MagicMock()
    manure_treatment_daily_input.simulation_day = simulation_day = 5
    manure_treatment_daily_input.pen_id = pen_id = 6
    manure_treatment_daily_input.liquid_manure_daily_volume = (
        liquid_manure_daily_volume
    ) = 100
    manure_treatment_daily_input.liquid_manure_total_solids = (
        liquid_manure_total_solids
    ) = 10
    manure_treatment_daily_input.liquid_manure_total_ammoniacal_nitrogen = (
        liquid_manure_total_ammoniacal_nitrogen
    ) = 20
    manure_treatment_daily_input.liquid_manure_nitrogen = liquid_manure_nitrogen = 30
    manure_treatment_daily_input.liquid_manure_total_volatile_solids = (
        liquid_manure_total_volatile_solids
    ) = 40
    manure_treatment_daily_input.liquid_manure_phosphorus = (
        liquid_manure_phosphorus
    ) = 50
    manure_treatment_daily_input.liquid_manure_potassium = liquid_manure_potassium = 60

    expected_manure_treatment_daily_output = ManureTreatmentDailyOutput(
        simulation_day=simulation_day,
        pen_id=pen_id,
        liquid_manure_total_ammoniacal_nitrogen=(
                liquid_manure_total_ammoniacal_nitrogen
                * (1 - total_ammoniacal_nitrogen_removal_efficiency_for_treatment)
        ),
        liquid_manure_nitrogen=(
                liquid_manure_nitrogen * (1 - nitrogen_removal_efficiency_for_treatment)
        ),
        liquid_manure_phosphorus=(
                liquid_manure_phosphorus * (1 - phosphorus_removal_efficiency_for_treatment)
        ),
        liquid_manure_potassium=(
                liquid_manure_potassium * (1 - potassium_removal_efficiency_for_treatment)
        ),
        liquid_manure_total_volatile_solids=(
                liquid_manure_total_volatile_solids
                * (1 - volatile_solids_removal_efficiency_for_treatment)
        ),
        liquid_manure_total_solids=(
                liquid_manure_total_solids
                * (1 - total_solids_removal_efficiency_for_treatment)
        ),
        daily_final_manure_volume=(
                liquid_manure_daily_volume
                - (
                        liquid_manure_total_solids
                        * total_solids_removal_efficiency_for_treatment
                )
                / 1000.0
        ),
    )

    # Act
    actual_daily_output = manure_treatment._initialize_daily_output_during_update(
        manure_treatment_daily_input=manure_treatment_daily_input
    )

    # Assert
    assert actual_daily_output == expected_manure_treatment_daily_output


@pytest.mark.parametrize(
    "manure_treatment_type_name",
    [
        "slurry storage underfloor",
        "slurry storage outdoor",
        "anaerobic digestion",
        "anaerobic lagoon",
        "anaerobic digestion and lagoon",
        "anaerobic digestion and lagoon with split",
        "compost bedded pack barn",
    ],
)
def test_get_current_day_temperature_and_rainfall(
        manure_treatment_type_name: str, mocker: MockFixture
) -> None:
    """Unit test for _get_current_day_average_temperature_celsius() and _get_current_day_rainfall()."""

    # Arrange
    expected_current_day_average_temperature_celsius = 10
    rainfall_mm = 20
    expected_rainfall_m = rainfall_mm / 1000.0
    mock_time = mocker.MagicMock()
    mock_time.year = 10
    mock_time.day = 1
    mock_current_day_conditions = mocker.MagicMock()
    setattr(mock_current_day_conditions, "mean_air_temperature", expected_current_day_average_temperature_celsius)
    setattr(mock_current_day_conditions, "precipitation", rainfall_mm)
    mock_weather = mocker.MagicMock()
    mock_weather.get_current_day_conditions.return_value = mock_current_day_conditions

    manure_treatment = ManureTreatmentFactory.get_instance(
        manure_treatment_type_name=manure_treatment_type_name,
        weather=mock_weather,
        time=mock_time,
    )

    # Act
    actual_current_day_average_temperature_celsius = (
        manure_treatment._get_current_day_average_temperature_celsius()
    )
    actual_current_day_rainfall = manure_treatment._get_current_day_rainfall()

    # Assert
    assert (
            actual_current_day_average_temperature_celsius
            == expected_current_day_average_temperature_celsius
    )
    assert actual_current_day_rainfall == expected_rainfall_m


@pytest.mark.parametrize(
    "manure_treatment_type_name",
    [
        "slurry storage underfloor",
        "slurry storage outdoor",
        "anaerobic digestion",
        "anaerobic lagoon",
        "anaerobic digestion and lagoon",
        "anaerobic digestion and lagoon with split",
        "compost bedded pack barn",
    ],
)
def test_accumulate_daily_output(
        manure_treatment_type_name: str, mocker: MockFixture
) -> None:
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
    expected_accumulated_output = (
            ManureTreatmentDailyOutput() + manure_treatment_daily_output
    )

    # Assert before
    assert manure_treatment._accumulated_output == ManureTreatmentDailyOutput()

    # Act
    manure_treatment._accumulate_daily_output(
        manure_treatment_daily_output=manure_treatment_daily_output
    )

    # Assert after
    assert manure_treatment._accumulated_output == expected_accumulated_output


@pytest.mark.parametrize(
    "manure_treatment_type_name",
    [
        "slurry storage underfloor",
        "slurry storage outdoor",
        "anaerobic digestion",
        "anaerobic lagoon",
        "anaerobic digestion and lagoon",
        "anaerobic digestion and lagoon with split",
    ],
)
def test_daily_update(manure_treatment_type_name: str, mocker: MockFixture) -> None:
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
        manure_treatment, "_initialize_private_attributes_during_update"
    )
    expected_manure_treatment_daily_output = ManureTreatmentDailyOutput()
    patch_for_daily_update_helper = mocker.patch.object(
        manure_treatment,
        "_daily_update_helper",
        return_value=expected_manure_treatment_daily_output,
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
        simulation_day,
        mock_pen,
        mock_manure_handler_daily_output,
        mock_manure_treatment_daily_input,
        mock_manure_separator,
    )
    patch_for_daily_update_helper.assert_called_once()
    assert actual_manure_treatment_daily_output == expected_manure_treatment_daily_output


# Test SlurryStorageUnderfloor and SlurryStorageOutdoor
# =====================================================


@pytest.mark.parametrize(
    "slurry_storage_treatment_type_name",
    [
        "slurry storage underfloor",
        "slurry storage outdoor",
    ],
)
def test_slurry_storage_daily_update_helper(
        slurry_storage_treatment_type_name: str, mocker: MockFixture
) -> None:
    """Unit test for _daily_update_helper() in both slurry storage treatments."""
    # Arrange
    slurry_storage = ManureTreatmentFactory.get_instance(
        manure_treatment_type_name=slurry_storage_treatment_type_name,
        weather=mocker.MagicMock(),
        time=mocker.MagicMock,
    )
    mock_accumulated_output: ManureTreatmentDailyOutput = mocker.MagicMock()
    mock_accumulated_output.liquid_manure_total_solids = (
        liquid_manure_total_solids
    ) = 20.0
    mock_accumulated_output.daily_final_manure_volume = final_manure_volume = 30.0
    mock_accumulated_output.liquid_manure_total_ammoniacal_nitrogen = (
        liquid_manure_total_ammoniacal_nitrogen
    ) = 40.0
    slurry_storage._accumulated_output = mock_accumulated_output
    patch_for_accumulate_daily_output = mocker.patch.object(
        slurry_storage, "_accumulate_daily_output"
    )

    mock_pen = mocker.MagicMock()
    mock_pen.num_animals = num_animals = 100
    mock_pen.barn_area_from_pen_type = barn_area_from_pen_type = 1000.0
    slurry_storage._current_pen = mock_pen

    initial_manure_treatment_daily_output = ManureTreatmentDailyOutput()
    slurry_storage._current_manure_treatment_daily_input = (
        current_manure_treatment_daily_input
    ) = mocker.MagicMock()
    patch_for_initialize_daily_output_during_update = mocker.patch.object(
        slurry_storage,
        "_initialize_daily_output_during_update",
        return_value=initial_manure_treatment_daily_output,
    )

    expected_methane_loss = 10.0
    expected_new_accumulated_liquid_manure_total_solids = 30.0
    patch_for_calc_methane_emission = mocker.patch.object(
        slurry_storage,
        "calc_methane_emission",
        return_value=[
            expected_methane_loss,
            expected_new_accumulated_liquid_manure_total_solids,
        ],
    )

    expected_ammonia_loss = 50.0
    expected_new_accumulated_liquid_manure_total_ammoniacal_nitrogen = 60.0
    patch_for_calc_ammonia_emission = mocker.patch.object(
        slurry_storage,
        "calc_ammonia_emission",
        return_value=[
            expected_ammonia_loss,
            expected_new_accumulated_liquid_manure_total_ammoniacal_nitrogen,
        ],
    )

    # Act
    actual_manure_treatment_daily_output = slurry_storage._daily_update_helper()

    # Assert
    patch_for_initialize_daily_output_during_update.assert_called_once_with(
        current_manure_treatment_daily_input
    )
    patch_for_accumulate_daily_output.assert_called_once_with(
        initial_manure_treatment_daily_output
    )

    patch_for_calc_methane_emission.assert_called_once_with(liquid_manure_total_solids)
    assert (
            slurry_storage._accumulated_output.liquid_manure_total_solids
            == expected_new_accumulated_liquid_manure_total_solids
    )
    assert actual_manure_treatment_daily_output.storage_methane == expected_methane_loss

    patch_for_calc_ammonia_emission.assert_called_once_with(
        num_animals=num_animals,
        barn_area=barn_area_from_pen_type,
        accumulated_manure_volume=final_manure_volume,
        accumulated_manure_total_ammoniacal_nitrogen=liquid_manure_total_ammoniacal_nitrogen,
    )
    assert (
            slurry_storage._accumulated_output.liquid_manure_total_ammoniacal_nitrogen
            == expected_new_accumulated_liquid_manure_total_ammoniacal_nitrogen
    )
    assert actual_manure_treatment_daily_output.storage_ammonia == expected_ammonia_loss


@pytest.mark.parametrize(
    "slurry_storage_treatment_type_name, is_enclosed",
    [
        ("slurry storage underfloor", True),
        ("slurry storage outdoor", False),
    ],
)
def test_slurry_storage_calc_methane_emission(
        slurry_storage_treatment_type_name: str, is_enclosed: bool, mocker: MockFixture
) -> None:
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
        slurry_storage,
        "_get_current_day_average_temperature_celsius",
        return_value=temperature_celsius,
    )
    expected_methane_loss = 2.0
    patch_for_calc_methane_emission_for_slurry_storage = mocker.patch(
        "RUFAS.routines.manure.manure_treatments.slurry_storage_underfloor."
        "GasEmissionsCalculator.methane_emission_for_slurry_storage",
        return_value=expected_methane_loss,
    )
    expected_new_accumulated_liquid_manure_total_solids = max(
        accumulated_liquid_manure_total_solids - expected_methane_loss, 0.0
    )

    # Act
    (
        actual_methane_loss,
        actual_new_accumulated_liquid_manure_total_solids,
    ) = slurry_storage.calc_methane_emission(
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
    assert (
            actual_new_accumulated_liquid_manure_total_solids
            == expected_new_accumulated_liquid_manure_total_solids
    )


@pytest.mark.parametrize(
    "slurry_storage_treatment_type_name",
    [
        "slurry storage underfloor",
        "slurry storage outdoor",
    ],
)
def test_slurry_storage_calc_ammonia_emission(
        slurry_storage_treatment_type_name: str, mocker: MockFixture
) -> None:
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
        slurry_storage,
        "_get_current_day_average_temperature_celsius",
        return_value=temperature_celsius,
    )
    expected_ammonia_loss = 2.0
    patch_for_calc_ammonia_emission_for_slurry_storage = mocker.patch(
        "RUFAS.routines.manure.manure_treatments.slurry_storage_underfloor."
        "GasEmissionsCalculator.ammonia_emission",
        return_value=expected_ammonia_loss,
    )
    expected_new_accumulated_manure_total_ammoniacal_nitrogen = max(
        accumulated_manure_total_ammoniacal_nitrogen - expected_ammonia_loss, 0.0
    )

    # Act
    (
        actual_ammonia_loss,
        actual_new_accumulated_manure_total_ammoniacal_nitrogen,
    ) = slurry_storage.calc_ammonia_emission(
        num_animals=num_animals,
        barn_area=barn_area,
        accumulated_manure_volume=accumulated_manure_volume,
        accumulated_manure_total_ammoniacal_nitrogen=accumulated_manure_total_ammoniacal_nitrogen,
    )

    # Assert
    patch_for_get_current_day_average_temperature_celsius.assert_called_once()
    patch_for_calc_ammonia_emission_for_slurry_storage.assert_called_once_with(
        num_animals=num_animals,
        barn_area=barn_area,
        total_ammoniacal_nitrogen=accumulated_manure_total_ammoniacal_nitrogen / num_animals,
        mass=accumulated_manure_volume * ManureConstants.MANURE_DENSITY / num_animals,
        temperature_celsius=temperature_celsius,
    )
    assert actual_ammonia_loss == expected_ammonia_loss
    assert (
            actual_new_accumulated_manure_total_ammoniacal_nitrogen
            == expected_new_accumulated_manure_total_ammoniacal_nitrogen
    )


# Test SlurryStorageUnderfloor specific methods
# ==========================================


def test_slurry_storage_underfloor_init(mocker: MockFixture) -> None:
    """Unit test for __init__() in slurry_storage_underfloor.py."""
    # Arrange
    mock_weather = mocker.MagicMock()
    mock_time = mocker.MagicMock()
    mock_manure_treatment_config = mocker.MagicMock()
    mock_manure_treatment_config.storage_time_period = storage_time_period = 120

    def mock_base_manure_treatment(
            self, weather, time, manure_treatment_config: ManureTreatmentConfig
    ) -> None:
        self.weather = weather
        self.time = time
        self.config = manure_treatment_config

    mocker.patch(
        "RUFAS.routines.manure.manure_treatments.base_manure_treatment.BaseManureTreatment.__init__",
        new=mock_base_manure_treatment,
    )

    # Act
    slurry_storage_underfloor = SlurryStorageUnderfloor(
        weather=mock_weather,
        time=mock_time,
        manure_treatment_config=mock_manure_treatment_config,
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

    def mock_base_manure_treatment(
            self, weather, time, manure_treatment_config: ManureTreatmentConfig
    ) -> None:
        self.weather = weather
        self.time = time
        self.config = manure_treatment_config

    mocker.patch(
        "RUFAS.routines.manure.manure_treatments.base_manure_treatment.BaseManureTreatment.__init__",
        new=mock_base_manure_treatment,
    )

    # Act
    slurry_storage_outdoor = SlurryStorageOutdoor(
        weather=mock_weather,
        time=mock_time,
        manure_treatment_config=mock_manure_treatment_config,
    )

    # Assert
    assert slurry_storage_outdoor.storage_time_period == storage_time_period
    assert slurry_storage_outdoor.freeboard_input == freeboard_input


def test_slurry_storage_outdoor_wastewater_volume(mocker: MockFixture) -> None:
    """Unit test for _wastewater_volume() in slurry_storage_outdoor.py."""
    # Case 1: There is a current manure treatment daily input
    # Arrange
    slurry_storage_outdoor = SlurryStorageOutdoor(
        weather=mocker.MagicMock(),
        time=mocker.MagicMock(),
        manure_treatment_config=mocker.MagicMock(),
    )
    mock_manure_treatment_daily_input = mocker.MagicMock()
    mock_manure_treatment_daily_input.liquid_manure_daily_volume = (
        expected_liquid_manure_daily_volume
    ) = 100.0
    slurry_storage_outdoor._current_manure_treatment_daily_input = (
        mock_manure_treatment_daily_input
    )

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
        manure_treatment_config=mocker.MagicMock(),
    )
    slurry_storage_outdoor._current_manure_treatment_daily_input = None

    # Act
    actual_wastewater_volume = slurry_storage_outdoor.wastewater_volume

    # Assert
    assert actual_wastewater_volume == 0.0


def test_slurry_storage_outdoor_treatment_volume(mocker: MockFixture) -> None:
    """Unit test for _treatment_volume() in slurry_storage_outdoor.py."""
    # Arrange
    slurry_storage_outdoor = SlurryStorageOutdoor(
        weather=mocker.MagicMock(),
        time=mocker.MagicMock(),
        manure_treatment_config=mocker.MagicMock(),
    )
    wastewater_volume = 100.0
    patch_for_wastewater_volume = mocker.patch(
        "RUFAS.routines.manure.manure_treatments.slurry_storage_outdoor.SlurryStorageOutdoor.wastewater_volume",
        new_callable=PropertyMock,
        return_value=wastewater_volume,
    )
    slurry_storage_outdoor.storage_time_period = storage_time_period = 120

    # Act
    actual_treatment_volume = slurry_storage_outdoor.treatment_volume

    # Assert
    assert actual_treatment_volume == wastewater_volume * storage_time_period
    patch_for_wastewater_volume.assert_called_once()


def test_slurry_storage_outdoor_total_pit_volume(mocker: MockFixture) -> None:
    """Unit test for _total_pit_volume() in slurry_storage_outdoor.py."""
    # Case 1: There is a current manure treatment daily input
    # Arrange
    slurry_storage_outdoor = SlurryStorageOutdoor(
        weather=mocker.MagicMock(),
        time=mocker.MagicMock(),
        manure_treatment_config=mocker.MagicMock(),
    )
    mock_manure_treatment_daily_input = mocker.MagicMock()
    slurry_storage_outdoor._current_manure_treatment_daily_input = (
        mock_manure_treatment_daily_input
    )
    treatment_volume = 100.0
    patch_for_treatment_volume = mocker.patch(
        "RUFAS.routines.manure.manure_treatments.slurry_storage_outdoor.SlurryStorageOutdoor.treatment_volume",
        new_callable=PropertyMock,
        return_value=treatment_volume,
    )
    freeboard_volume = 200.0
    patch_for_freeboard_volume = mocker.patch(
        "RUFAS.routines.manure.manure_treatments.slurry_storage_outdoor.SlurryStorageOutdoor.freeboard_volume",
        new_callable=PropertyMock,
        return_value=freeboard_volume,
    )
    precipitation_volume = 300.0
    patch_for_precipitation_volume = mocker.patch(
        "RUFAS.routines.manure.manure_treatments.slurry_storage_outdoor.SlurryStorageOutdoor.precipitation_volume",
        new_callable=PropertyMock,
        return_value=precipitation_volume,
    )
    expected_total_pit_volume = (
            treatment_volume + freeboard_volume + precipitation_volume
    )

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
        manure_treatment_config=mocker.MagicMock(),
    )
    slurry_storage_outdoor._current_manure_treatment_daily_input = None

    # Act
    actual_total_pit_volume = slurry_storage_outdoor.total_pit_volume

    # Assert
    assert actual_total_pit_volume == 0.0


def test_slurry_storage_outdoor_pit_depth(mocker: MockFixture) -> None:
    """Unit test for _pit_depth() in slurry_storage_outdoor.py."""
    # Arrange
    slurry_storage_outdoor = SlurryStorageOutdoor(
        weather=mocker.MagicMock(),
        time=mocker.MagicMock(),
        manure_treatment_config=mocker.MagicMock(),
    )
    expected_pit_depth = 3.657

    # Act
    actual_pit_depth = slurry_storage_outdoor.pit_depth

    # Assert
    assert actual_pit_depth == expected_pit_depth


def test_slurry_storage_outdoor_pit_slope(mocker: MockFixture) -> None:
    """Unit test for _pit_slope() in slurry_storage_outdoor.py."""
    # Arrange
    slurry_storage_outdoor = SlurryStorageOutdoor(
        weather=mocker.MagicMock(),
        time=mocker.MagicMock(),
        manure_treatment_config=mocker.MagicMock(),
    )
    expected_pit_slope = 2.0

    # Act
    actual_pit_slope = slurry_storage_outdoor.pit_slope

    # Assert
    assert actual_pit_slope == expected_pit_slope


def test_slurry_storage_outdoor_calc_abc(mocker: MockFixture) -> None:
    """Unit test for _calc_abc() in slurry_storage_outdoor.py."""
    # Arrange
    slurry_storage_outdoor = SlurryStorageOutdoor(
        weather=mocker.MagicMock(),
        time=mocker.MagicMock(),
        manure_treatment_config=mocker.MagicMock(),
    )
    pit_depth = 3.0
    patch_for_pit_depth = mocker.patch(
        "RUFAS.routines.manure.manure_treatments.slurry_storage_outdoor.SlurryStorageOutdoor.pit_depth",
        new_callable=PropertyMock,
        return_value=pit_depth,
    )
    pit_slope = 2.0
    patch_for_pit_slope = mocker.patch(
        "RUFAS.routines.manure.manure_treatments.slurry_storage_outdoor.SlurryStorageOutdoor.pit_slope",
        new_callable=PropertyMock,
        return_value=pit_slope,
    )
    treatment_volume = 100.0
    patch_for_treatment_volume = mocker.patch(
        "RUFAS.routines.manure.manure_treatments.slurry_storage_outdoor.SlurryStorageOutdoor.treatment_volume",
        new_callable=PropertyMock,
        return_value=treatment_volume,
    )
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


def test_slurry_storage_outdoor_pit_width(mocker: MockFixture) -> None:
    """Unit test for pit_width() in slurry_storage_outdoor.py."""
    # Case 1: There is a current manure treatment daily input
    # Arrange
    slurry_storage_outdoor = SlurryStorageOutdoor(
        weather=mocker.MagicMock(),
        time=mocker.MagicMock(),
        manure_treatment_config=mocker.MagicMock(),
    )
    mock_manure_treatment_daily_input = mocker.MagicMock()
    slurry_storage_outdoor._current_manure_treatment_daily_input = (
        mock_manure_treatment_daily_input
    )
    a, b, c = 2.0, 10.0, 4.0
    patch_for_calc_abc = mocker.patch(
        "RUFAS.routines.manure.manure_treatments.slurry_storage_outdoor.SlurryStorageOutdoor._calc_abc",
        return_value=(a, b, c),
    )
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
        manure_treatment_config=mocker.MagicMock(),
    )
    slurry_storage_outdoor._current_manure_treatment_daily_input = None

    # Act
    actual_pit_width = slurry_storage_outdoor.pit_width

    # Assert
    assert actual_pit_width == 0.0


def test_slurry_storage_outdoor_pit_length(mocker: MockFixture) -> None:
    """Unit test for pit_length() in slurry_storage_outdoor.py."""
    # Arrange
    slurry_storage_outdoor = SlurryStorageOutdoor(
        weather=mocker.MagicMock(),
        time=mocker.MagicMock(),
        manure_treatment_config=mocker.MagicMock(),
    )
    pit_width = 10.0
    patch_for_pit_width = mocker.patch(
        "RUFAS.routines.manure.manure_treatments.slurry_storage_outdoor.SlurryStorageOutdoor.pit_width",
        new_callable=PropertyMock,
        return_value=pit_width,
    )
    expected_pit_length = pit_width * 3

    # Act
    actual_pit_length = slurry_storage_outdoor.pit_length

    # Assert
    assert actual_pit_length == expected_pit_length
    patch_for_pit_width.assert_called_once()


def test_slurry_storage_outdoor_pit_surface_area(mocker: MockFixture) -> None:
    """Unit test for pit_surface_area() in slurry_storage_outdoor.py."""
    # Arrange
    slurry_storage_outdoor = SlurryStorageOutdoor(
        weather=mocker.MagicMock(),
        time=mocker.MagicMock(),
        manure_treatment_config=mocker.MagicMock(),
    )
    pit_width = 10.0
    patch_for_pit_width = mocker.patch(
        "RUFAS.routines.manure.manure_treatments.slurry_storage_outdoor.SlurryStorageOutdoor.pit_width",
        new_callable=PropertyMock,
        return_value=pit_width,
    )
    pit_length = 30.0
    patch_for_pit_length = mocker.patch(
        "RUFAS.routines.manure.manure_treatments.slurry_storage_outdoor.SlurryStorageOutdoor.pit_length",
        new_callable=PropertyMock,
        return_value=pit_length,
    )
    expected_pit_surface_area = pit_width * pit_length

    # Act
    actual_pit_surface_area = slurry_storage_outdoor.pit_surface_area

    # Assert
    assert actual_pit_surface_area == expected_pit_surface_area
    patch_for_pit_width.assert_called_once()
    patch_for_pit_length.assert_called_once()


def test_slurry_storage_outdoor_pit_volume(mocker: MockFixture) -> None:
    """Unit test for pit_volume() in slurry_storage_outdoor.py."""
    # Arrange
    slurry_storage_outdoor = SlurryStorageOutdoor(
        weather=mocker.MagicMock(),
        time=mocker.MagicMock(),
        manure_treatment_config=mocker.MagicMock(),
    )
    pit_length = 30.0
    patch_for_pit_length = mocker.patch(
        "RUFAS.routines.manure.manure_treatments.slurry_storage_outdoor.SlurryStorageOutdoor.pit_length",
        new_callable=PropertyMock,
        return_value=pit_length,
    )
    pit_width = 10.0
    patch_for_pit_width = mocker.patch(
        "RUFAS.routines.manure.manure_treatments.slurry_storage_outdoor.SlurryStorageOutdoor.pit_width",
        new_callable=PropertyMock,
        return_value=pit_width,
    )
    pit_depth = 2.0
    patch_for_pit_depth = mocker.patch(
        "RUFAS.routines.manure.manure_treatments.slurry_storage_outdoor.SlurryStorageOutdoor.pit_depth",
        new_callable=PropertyMock,
        return_value=pit_depth,
    )
    pit_slope = 0.1
    patch_for_pit_slope = mocker.patch(
        "RUFAS.routines.manure.manure_treatments.slurry_storage_outdoor.SlurryStorageOutdoor.pit_slope",
        new_callable=PropertyMock,
        return_value=pit_slope,
    )
    expected_pit_volume = (
            pit_length * pit_width * pit_depth
            - (pit_slope * (pit_depth ** 2)) * (pit_length + pit_width)
            + (4 * pit_slope * (pit_depth ** 3) / 3)
    )

    # Act
    actual_pit_volume = slurry_storage_outdoor.pit_volume

    # Assert
    assert actual_pit_volume == expected_pit_volume
    assert patch_for_pit_length.call_count == 2
    assert patch_for_pit_width.call_count == 2
    assert patch_for_pit_depth.call_count == 3
    assert patch_for_pit_slope.call_count == 2


def test_slurry_storage_outdoor_precipitation_volume(mocker: MockFixture) -> None:
    """Unit test for precipitation_volume() in slurry_storage_outdoor.py."""
    # Arrange
    slurry_storage_outdoor = SlurryStorageOutdoor(
        weather=mocker.MagicMock(),
        time=mocker.MagicMock(),
        manure_treatment_config=mocker.MagicMock(),
    )
    rainfall = 10.0
    patch_for_get_current_day_rainfall = mocker.patch(
        "RUFAS.routines.manure.manure_treatments.slurry_storage_outdoor.SlurryStorageOutdoor"
        "._get_current_day_rainfall",
        return_value=rainfall,
    )
    pit_surface_area = 300.0
    patch_for_pit_surface_area = mocker.patch(
        "RUFAS.routines.manure.manure_treatments.slurry_storage_outdoor.SlurryStorageOutdoor.pit_surface_area",
        new_callable=PropertyMock,
        return_value=pit_surface_area,
    )
    expected_precipitation_volume = rainfall * pit_surface_area

    # Act
    actual_precipitation_volume = slurry_storage_outdoor.precipitation_volume

    # Assert
    assert actual_precipitation_volume == expected_precipitation_volume
    patch_for_get_current_day_rainfall.assert_called_once()
    patch_for_pit_surface_area.assert_called_once()


def test_slurry_storage_outdoor_freeboard_volume(mocker: MockFixture) -> None:
    """Unit test for freeboard_volume() in slurry_storage_outdoor.py."""
    # Arrange
    slurry_storage_outdoor = SlurryStorageOutdoor(
        weather=mocker.MagicMock(),
        time=mocker.MagicMock(),
        manure_treatment_config=mocker.MagicMock(),
    )
    slurry_storage_outdoor.freeboard_input = freeboard_input = 10.0
    pit_surface_area = 300.0
    patch_for_pit_surface_area = mocker.patch(
        "RUFAS.routines.manure.manure_treatments.slurry_storage_outdoor.SlurryStorageOutdoor.pit_surface_area",
        new_callable=PropertyMock,
        return_value=pit_surface_area,
    )
    expected_freeboard_volume = freeboard_input * pit_surface_area

    # Act
    actual_freeboard_volume = slurry_storage_outdoor.freeboard_volume

    # Assert
    assert actual_freeboard_volume == expected_freeboard_volume
    patch_for_pit_surface_area.assert_called_once()


# Test AnaerobicLagoon specific methods
# =====================================


@pytest.mark.parametrize(
    "anaerobic_treatment_class", [AnaerobicLagoon, AnaerobicDigestion]
)
def test_calc_daily_sludge_output(
        anaerobic_treatment_class: Union[Type[AnaerobicLagoon], Type[AnaerobicDigestion]],
        mocker: MockFixture,
) -> None:
    """Unit test for _calc_daily_sludge_output() in slurry_storage_outdoor.py."""
    # Arrange
    mock_manure_treatment_config = mocker.MagicMock()
    mock_manure_treatment_config.total_solids_removal_efficiency_for_treatment = (
        total_solids_removal_efficiency_for_treatment
    ) = 0.5
    mock_manure_treatment_config.volatile_solids_removal_efficiency_for_treatment = (
        volatile_solids_removal_efficiency_for_treatment
    ) = 0.4
    mock_manure_treatment_config.nitrogen_removal_efficiency_for_treatment = (
        nitrogen_removal_efficiency_for_treatment
    ) = 0.3
    mock_manure_treatment_config.phosphorus_removal_efficiency_for_treatment = (
        phosphorus_removal_efficiency_for_treatment
    ) = 0.2
    mock_manure_treatment_config.potassium_removal_efficiency_for_treatment = (
        potassium_removal_efficiency_for_treatment
    ) = 0.1

    anaerobic_treatment = anaerobic_treatment_class(
        weather=mocker.MagicMock(),
        time=mocker.MagicMock(),
        manure_treatment_config=mock_manure_treatment_config,
    )
    mock_manure_treatment_daily_input = mocker.MagicMock()
    mock_manure_treatment_daily_input.liquid_manure_total_solids = (
        liquid_manure_total_solids
    ) = 10.0
    mock_manure_treatment_daily_input.liquid_manure_total_volatile_solids = (
        liquid_manure_total_volatile_solids
    ) = 5.0
    mock_manure_treatment_daily_input.liquid_manure_nitrogen = (
        liquid_manure_nitrogen
    ) = 2.0
    mock_manure_treatment_daily_input.liquid_manure_phosphorus = (
        liquid_manure_phosphorus
    ) = 1.0
    mock_manure_treatment_daily_input.liquid_manure_potassium = (
        liquid_manure_potassium
    ) = 0.5

    mock_manure_treatment_daily_output = ManureTreatmentDailyOutput()

    expected_sludge_manure_total_solids = (
            liquid_manure_total_solids * total_solids_removal_efficiency_for_treatment
    )
    expected_sludge_manure_total_volatile_solids = (
            liquid_manure_total_volatile_solids
            * volatile_solids_removal_efficiency_for_treatment
    )
    expected_sludge_manure_nitrogen = (
            liquid_manure_nitrogen * nitrogen_removal_efficiency_for_treatment
    )
    expected_sludge_manure_phosphorus = (
            liquid_manure_phosphorus * phosphorus_removal_efficiency_for_treatment
    )
    expected_sludge_manure_potassium = (
            liquid_manure_potassium * potassium_removal_efficiency_for_treatment
    )
    expected_sludge_manure_daily_volume = (
            liquid_manure_total_volatile_solids * 0.03 / ManureConstants.MANURE_DENSITY
    )

    # Act
    actual_daily_output = anaerobic_treatment._calc_daily_sludge_output(
        daily_output=mock_manure_treatment_daily_output,
        manure_treatment_daily_input=mock_manure_treatment_daily_input,
    )

    # Assert
    assert actual_daily_output is not mock_manure_treatment_daily_output
    assert actual_daily_output.sludge_manure_total_solids == approx(
        expected_sludge_manure_total_solids
    )
    assert actual_daily_output.sludge_manure_total_volatile_solids == approx(
        expected_sludge_manure_total_volatile_solids
    )
    assert actual_daily_output.sludge_manure_nitrogen == approx(
        expected_sludge_manure_nitrogen
    )
    assert actual_daily_output.sludge_manure_phosphorus == approx(
        expected_sludge_manure_phosphorus
    )
    assert actual_daily_output.sludge_manure_potassium == approx(
        expected_sludge_manure_potassium
    )
    assert actual_daily_output.sludge_manure_daily_volume == approx(
        expected_sludge_manure_daily_volume
    )


@pytest.mark.parametrize(
    "initial_methane_emission, volatile_solids, volatile_solids_factor,"
    "expected_methane_emission, expected_liquid_manure_volatile_solids",
    [
        (100.0, 300.0, 3, 100.0, 0.0),  # Normal case
        (50.0, 100.0, 2, 50.0, 0.0),  # Another normal case
        (0.0, 10.0, 3, 0.0, 10.0),  # Zero methane emission
        (50.0, 50.0, 1, 50.0, 0.0),  # Methane emission equal to volatile solids
        (150.0, 100.0, 1, 150.0, 0.0),  # Methane emission exceeding volatile solids
        (-50.0, 100.0, 1, 0.0, 100.0),  # Negative methane emission
    ],
)
def test_anaerobic_lagoon_update_methane_emission(
        mocker: MockFixture,
        initial_methane_emission: float,
        volatile_solids: float,
        volatile_solids_factor: int,
        expected_methane_emission: float,
        expected_liquid_manure_volatile_solids: float,
) -> None:
    """
    Unit test for _update_methane_emission() in anaerobic_lagoon.py.

    This test checks that the _update_methane_emission() method correctly calculates
    methane emission based on the given liquid_manure_total_volatile_solids and temperature,
    and updates the storage_methane and liquid_manure_total_volatile_solids
    of the accumulated output.

    """
    # Arrange
    current_liquid_manure_total_volatile_solids = volatile_solids
    mock_daily_output = mocker.MagicMock(spec=ManureTreatmentDailyOutput)
    mock_daily_output.liquid_manure_total_volatile_solids = (
        current_liquid_manure_total_volatile_solids
    )
    patch_for_calc_methane_emission_for_slurry_storage = mocker.patch(
        "RUFAS.routines.manure.manure_treatments.anaerobic_lagoon"
        ".GasEmissionsCalculator.methane_emission_from_slurry_storage",
        return_value=initial_methane_emission,
    )

    anaerobic_lagoon = AnaerobicLagoon(
        mocker.MagicMock(), mocker.MagicMock(), mocker.MagicMock()
    )
    anaerobic_lagoon._accumulated_output = mocker.MagicMock(
        spec=ManureTreatmentDailyOutput
    )
    anaerobic_lagoon._accumulated_output.storage_methane = 0.0
    anaerobic_lagoon._accumulated_output.liquid_manure_total_volatile_solids = 0.0
    mock_temp_value = 25.0
    patch_for_get_current_day_average_temperature_celsius = mocker.patch.object(
        anaerobic_lagoon,
        "_get_current_day_average_temperature_celsius",
        return_value=mock_temp_value,
    )

    # Act
    anaerobic_lagoon._update_methane_emission(mock_daily_output)

    # Assert
    patch_for_calc_methane_emission_for_slurry_storage.assert_called_once_with(
        total_volatile_solids=current_liquid_manure_total_volatile_solids,
        temp=mock_temp_value,
    )
    patch_for_get_current_day_average_temperature_celsius.assert_called_once()
    assert mock_daily_output.storage_methane == expected_methane_emission
    assert (
            anaerobic_lagoon._accumulated_output.storage_methane
            == expected_methane_emission
    )
    assert (
            anaerobic_lagoon._accumulated_output.liquid_manure_total_volatile_solids
            == expected_liquid_manure_volatile_solids
    )


@pytest.mark.parametrize(
    "liquid_manure_ammoniacal_nitrogen, urine_ammoniacal_nitrogen, "
    "housing_ammonia, mock_storage_ammonia_emission_value",
    [
        (1.0, 2.0, 0.5, 10.0),  # Normal case
        (0.0, 0.0, 0.0, 0.0),  # Zero ammoniacal nitrogen
    ],
)
def test_anaerobic_lagoon_update_ammonia_emission(
        mocker: MockFixture,
        liquid_manure_ammoniacal_nitrogen: float,
        urine_ammoniacal_nitrogen: float,
        housing_ammonia: float,
        mock_storage_ammonia_emission_value: float,
) -> None:
    """
    Unit test for _update_ammonia_emission() in anaerobic_lagoon.py.

    This test checks that the _update_ammonia_emission() method correctly calculates
    ammonia emission based on given parameters and updates the storage_ammonia
    of the accumulated output.

    """
    # Arrange
    mock_daily_output = mocker.MagicMock(spec=ManureTreatmentDailyOutput)
    mock_daily_output.liquid_manure_total_ammoniacal_nitrogen = (
        liquid_manure_ammoniacal_nitrogen
    )
    mock_current_pen = mocker.MagicMock()
    mock_current_pen.manure.urine_total_ammoniacal_nitrogen = urine_ammoniacal_nitrogen
    mock_manure_handler_daily_output = mocker.MagicMock()
    mock_manure_handler_daily_output.housing_ammonia = housing_ammonia

    patch_for_calc_storage_ammonia_emission = mocker.patch(
        "RUFAS.routines.manure.manure_treatments.anaerobic_lagoon"
        ".GasEmissionsCalculator.storage_ammonia_emission",
        return_value=mock_storage_ammonia_emission_value,
    )

    anaerobic_lagoon = AnaerobicLagoon(
        mocker.MagicMock(), mocker.MagicMock(), mocker.MagicMock()
    )
    anaerobic_lagoon._accumulated_output = mocker.MagicMock(
        spec=ManureTreatmentDailyOutput
    )
    anaerobic_lagoon._accumulated_output.storage_ammonia = 0.0
    anaerobic_lagoon._current_pen = mock_current_pen
    anaerobic_lagoon._manure_handler_daily_output = mock_manure_handler_daily_output
    mock_temp_value = 25.0
    patch_for_get_current_day_average_temperature_celsius = mocker.patch.object(
        anaerobic_lagoon,
        "_get_current_day_average_temperature_celsius",
        return_value=mock_temp_value,
    )

    # Act
    anaerobic_lagoon._update_ammonia_emission(mock_daily_output)

    # Assert
    total_ammoniacal_nitrogen = max(
        mock_daily_output.liquid_manure_total_ammoniacal_nitrogen
        + mock_current_pen.manure.urine_total_ammoniacal_nitrogen
        - mock_manure_handler_daily_output.housing_ammonia,
        0.0,
    )
    patch_for_calc_storage_ammonia_emission.assert_called_once_with(
        num_animals=mock_current_pen.num_animals,
        manure_total_ammoniacal_nitrogen=total_ammoniacal_nitrogen,
        manure_volume=mock_daily_output.daily_final_manure_volume,
        manure_density=ManureConstants.LIQUID_MANURE_DENSITY,
        total_solids=mock_daily_output.liquid_manure_total_solids,
        temp=mock_temp_value,
    )
    patch_for_get_current_day_average_temperature_celsius.assert_called_once()
    assert mock_daily_output.storage_ammonia == mock_storage_ammonia_emission_value
    assert (
            anaerobic_lagoon._accumulated_output.storage_ammonia
            == mock_storage_ammonia_emission_value
    )


def test_anaerobic_lagoon_daily_update_helper(mocker: MockFixture) -> None:
    """
    Unit test for _daily_update_helper() in anaerobic_lagoon.py.

    This test checks that the _daily_update_helper() method correctly initializes
    and updates the daily output, including final manure volume, precipitation volume,
    rainfall, sludge output, methane and ammonia emissions, and returns the daily output.

    """
    # Arrange
    anaerobic_lagoon = AnaerobicLagoon(
        mocker.MagicMock(), mocker.MagicMock(), mocker.MagicMock()
    )
    mock_daily_output = mocker.MagicMock(spec=ManureTreatmentDailyOutput)
    mock_daily_output.daily_final_manure_volume = daily_final_manure_volume = 100.0

    patch_for_initialize_daily_output_during_update = mocker.patch.object(
        anaerobic_lagoon,
        "_initialize_daily_output_during_update",
        return_value=mock_daily_output,
    )

    adjusted_final_manure_volume = 150.0
    patch_for_adjust_final_manure_volume = mocker.patch.object(
        anaerobic_lagoon,
        "_adjust_final_manure_volume",
        return_value=adjusted_final_manure_volume,
    )

    patch_for_set_daily_final_manure_volume = mocker.patch.object(
        mock_daily_output, "set_daily_final_manure_volume"
    )

    patch_for_calc_daily_sludge_output = mocker.patch.object(
        anaerobic_lagoon, "_calc_daily_sludge_output", return_value=mock_daily_output
    )

    patch_for_adjust_accumulated_output = mocker.patch.object(
        anaerobic_lagoon, "_adjust_accumulated_output", return_value=mock_daily_output
    )

    patch_for_update_methane_emission = mocker.patch.object(
        anaerobic_lagoon, "_update_methane_emission"
    )

    patch_for_update_ammonia_emission = mocker.patch.object(
        anaerobic_lagoon, "_update_ammonia_emission"
    )

    precipitation_volume = 10.0
    patch_for_precipitation_volume_property = mocker.patch(
        "RUFAS.routines.manure.manure_treatments.anaerobic_lagoon."
        "AnaerobicLagoon.precipitation_volume",
        new_callable=PropertyMock,
        return_value=precipitation_volume,
    )

    # Act
    result = anaerobic_lagoon._daily_update_helper()

    # Assert
    patch_for_initialize_daily_output_during_update.assert_called_once_with(
        anaerobic_lagoon._current_manure_treatment_daily_input
    )
    patch_for_adjust_final_manure_volume.assert_called_once_with(
        daily_final_manure_volume
    )
    patch_for_set_daily_final_manure_volume.assert_called_once_with(
        adjusted_final_manure_volume
    )
    patch_for_calc_daily_sludge_output.assert_called_once_with(
        mock_daily_output, anaerobic_lagoon._current_manure_treatment_daily_input
    )
    patch_for_adjust_accumulated_output.assert_called_once_with(mock_daily_output)
    patch_for_update_methane_emission.assert_called_once_with(mock_daily_output)
    patch_for_update_ammonia_emission.assert_called_once_with(mock_daily_output)
    assert patch_for_precipitation_volume_property.call_count == 1

    assert result == mock_daily_output
    assert anaerobic_lagoon._accumulated_precipitation_volume == precipitation_volume


@pytest.mark.parametrize(
    "simulation_day, storage_time_period",
    [
        (1, 100),
        (100, 100),
        (101, 100),
    ],
)
def test_adjust_final_manure_volume(
        simulation_day: int, storage_time_period: int, mocker: MockFixture
) -> None:
    """Unit test for _adjust_final_manure_volume() in anaerobic_lagoon.py."""
    # Arrange
    anaerobic_lagoon = AnaerobicLagoon(
        weather=mocker.MagicMock(),
        time=mocker.MagicMock(),
        manure_treatment_config=mocker.MagicMock(),
    )
    anaerobic_lagoon._sim_day = simulation_day
    anaerobic_lagoon.storage_time_period = storage_time_period
    current_day_final_manure_volume = 10.0
    precipitation_volume = 20.0
    patch_for_precipitation_volume_property = mocker.patch(
        "RUFAS.routines.manure.manure_treatments.anaerobic_lagoon."
        "AnaerobicLagoon.precipitation_volume",
        new_callable=PropertyMock,
        return_value=precipitation_volume,
    )
    flushing_volume = 30.0
    patch_for_flushing_volume_property = mocker.patch(
        "RUFAS.routines.manure.manure_treatments.anaerobic_lagoon."
        "AnaerobicLagoon.flushing_volume",
        new_callable=PropertyMock,
        return_value=flushing_volume,
    )

    # Act
    actual_adjusted_final_manure_volume = anaerobic_lagoon._adjust_final_manure_volume(
        current_day_final_manure_volume
    )

    # Assert
    patch_for_precipitation_volume_property.assert_called_once()
    if simulation_day % storage_time_period > 1:
        patch_for_flushing_volume_property.assert_called_once()
        expected_adjusted_final_manure_volume = (
                current_day_final_manure_volume + precipitation_volume - flushing_volume
        )
        assert (
                actual_adjusted_final_manure_volume == expected_adjusted_final_manure_volume
        )
    else:
        patch_for_flushing_volume_property.assert_not_called()
        assert (
                actual_adjusted_final_manure_volume
                == current_day_final_manure_volume + precipitation_volume
        )


def test_sludge_accumulation_volume_property(mocker: MockFixture) -> None:
    """Unit test for sludge_accumulation_volume property in anaerobic_lagoon.py."""
    # Arrange
    anaerobic_lagoon = AnaerobicLagoon(
        weather=mocker.MagicMock(),
        time=mocker.MagicMock(),
        manure_treatment_config=mocker.MagicMock(),
    )
    expected_sludge_accumulation_volume = 10.0
    anaerobic_lagoon._accumulated_output = mocker.MagicMock()
    anaerobic_lagoon._accumulated_output.sludge_manure_daily_volume = (
        expected_sludge_accumulation_volume
    )

    # Act
    actual_sludge_accumulation_volume = anaerobic_lagoon.sludge_accumulation_volume

    # Assert
    assert actual_sludge_accumulation_volume == expected_sludge_accumulation_volume


def test_flushing_volume_property(mocker: MockFixture) -> None:
    """Unit test for flushing_volume property in anaerobic_lagoon.py."""
    # Arrange
    anaerobic_lagoon = AnaerobicLagoon(
        weather=mocker.MagicMock(),
        time=mocker.MagicMock(),
        manure_treatment_config=mocker.MagicMock(),
    )
    expected_flushing_volume = 10.0
    anaerobic_lagoon._manure_handler_daily_output = mocker.MagicMock()
    anaerobic_lagoon._manure_handler_daily_output.cleaning_water_volume = (
        expected_flushing_volume
    )

    # Act
    actual_flushing_volume = anaerobic_lagoon.flushing_volume

    # Assert
    assert actual_flushing_volume == expected_flushing_volume


def test_adjust_accumulated_output(mocker: MockFixture) -> None:
    """
    Unit test for _adjust_accumulated_output() in anaerobic_lagoon.py.

    This test checks that the _adjust_accumulated_output() method correctly resets the
    accumulated output on the first day of every storage time period or adds the daily
    output to the accumulated output on other days.

    """
    # Arrange
    mocker.patch(
        "RUFAS.routines.manure.manure_treatments.anaerobic_lagoon."
        "AnaerobicLagoon.__init__",
        return_value=None,
    )
    anaerobic_lagoon = AnaerobicLagoon(
        mocker.MagicMock(), mocker.MagicMock(), mocker.MagicMock()
    )
    mock_flushing_volume_property = mocker.patch(
        "RUFAS.routines.manure.manure_treatments.anaerobic_lagoon."
        "AnaerobicLagoon.flushing_volume",
        new_callable=PropertyMock,
    )

    mock_manure_treatment_daily_output = mocker.MagicMock()
    mock_manure_treatment_daily_output_cloned = mocker.MagicMock()
    mock_manure_treatment_daily_output.clone.return_value = (
        mock_manure_treatment_daily_output_cloned
    )

    mock_accumulated_output = mocker.MagicMock()
    mock_new_accumulated_output = mocker.MagicMock()
    mock_new_accumulated_output.daily_final_manure_volume = (
        daily_final_manure_volume
    ) = 10.0
    mock_accumulated_output.__add__ = mocker.MagicMock(
        return_value=mock_new_accumulated_output
    )
    anaerobic_lagoon._accumulated_output = mock_accumulated_output

    # Case 1: Reset on the first day of storage time period
    anaerobic_lagoon._sim_day = 1
    anaerobic_lagoon.storage_time_period = 10

    # Act
    result1 = anaerobic_lagoon._adjust_accumulated_output(
        mock_manure_treatment_daily_output
    )

    # Assert
    mock_manure_treatment_daily_output.clone.assert_called_once()
    assert result1 == mock_manure_treatment_daily_output_cloned

    # Reset mock calls
    mock_manure_treatment_daily_output.clone.reset_mock()

    # Case 2: Accumulate on other days, consider flushing_volume
    anaerobic_lagoon._sim_day = 2
    flushing_volume = 50.0
    mock_flushing_volume_property.return_value = flushing_volume

    # Act
    result2 = anaerobic_lagoon._adjust_accumulated_output(
        mock_manure_treatment_daily_output
    )

    # Assert
    mock_accumulated_output.__add__.assert_called_once_with(
        mock_manure_treatment_daily_output
    )
    assert result2 == mock_new_accumulated_output
    assert (
            result2.daily_final_manure_volume == daily_final_manure_volume - flushing_volume
    )


def test_volume_needed_property(mocker: MockFixture) -> None:
    """Unit test for volume_needed() in anaerobic_lagoon.py."""
    # Arrange
    anaerobic_lagoon = AnaerobicLagoon(
        weather=mocker.MagicMock(),
        time=mocker.MagicMock(),
        manure_treatment_config=mocker.MagicMock(),
    )
    mock_accumulated_output = mocker.MagicMock()
    mock_accumulated_output.daily_final_manure_volume = daily_final_manure_volume = 10.0
    anaerobic_lagoon._accumulated_output = mock_accumulated_output

    sludge_accumulation_volume = 20.0
    patch_for_sludge_accumulation_volume_property = mocker.patch(
        "RUFAS.routines.manure.manure_treatments.anaerobic_lagoon."
        "AnaerobicLagoon.sludge_accumulation_volume",
        new_callable=PropertyMock,
        return_value=sludge_accumulation_volume,
    )

    # Act
    actual_volume_needed = anaerobic_lagoon.volume_needed

    # Assert
    patch_for_sludge_accumulation_volume_property.assert_called_once()
    assert (
            actual_volume_needed == daily_final_manure_volume + sludge_accumulation_volume
    )


def test_anaerobic_lagoon_depth(mocker: MockFixture) -> None:
    """
    Unit test for the lagoon_depth property in anaerobic_lagoon.py.

    This test checks that the lagoon_depth property returns the constant value defined in the class,
    representing the depth of the lagoon in meters (m).

    """
    # Arrange
    anaerobic_lagoon = AnaerobicLagoon(
        weather=mocker.MagicMock(),
        time=mocker.MagicMock(),
        manure_treatment_config=mocker.MagicMock(),
    )
    expected_anaerobic_lagoon_depth = AnaerobicLagoon.LAGOON_DEPTH

    # Act
    actual_anaerobic_lagoon_depth = anaerobic_lagoon.lagoon_depth

    # Assert
    assert actual_anaerobic_lagoon_depth == expected_anaerobic_lagoon_depth


def test_anaerobic_lagoon_slope(mocker: MockFixture) -> None:
    """
    Unit test for the lagoon_slope property in anaerobic_lagoon.py.

    This test checks that the lagoon_slope property returns the constant value defined in the class,
    representing the slope of the lagoon (unitless).
    """
    # Arrange
    anaerobic_lagoon = AnaerobicLagoon(
        weather=mocker.MagicMock(),
        time=mocker.MagicMock(),
        manure_treatment_config=mocker.MagicMock(),
    )
    expected_anaerobic_lagoon_slope = AnaerobicLagoon.LAGOON_SLOPE

    # Act
    actual_anaerobic_lagoon_slope = anaerobic_lagoon.lagoon_slope

    # Assert
    assert actual_anaerobic_lagoon_slope == expected_anaerobic_lagoon_slope


@pytest.mark.parametrize(
    "lagoon_depth, lagoon_slope, volume_needed, expected_a, expected_b, expected_c, raises_error",
    [
        (3.0, 2.0, 100.0, 9.0, -72.0, 44.0, False),  # Generic case
        (0.0, 2.0, 100.0, 0.0, 0.0, -100.0, True),  # a = 0 case
        (1.0, 1.0, 10.0, 3.0, -4.0, -8.66666, False),  # Another generic case
        (
                1e-9,
                2.0,
                100.0,
                3e-9,
                -8e-18,
                -100,
                False,
        ),  # Edge case with small lagoon_depth
    ],
)
def test_anaerobic_lagoon_calc_lagoon_width_coefficients(
        mocker: MockFixture,
        lagoon_depth: float,
        lagoon_slope: float,
        volume_needed: float,
        expected_a: float,
        expected_b: float,
        expected_c: float,
        raises_error: bool,
) -> None:
    """
    Unit test for _calc_lagoon_width_coefficients() in anaerobic_lagoon.py.

    This test checks that the method correctly calculates the coefficients for the quadratic equation
    used to determine the width of the lagoon based on depth, slope, and volume needed.

    """
    # Arrange
    anaerobic_lagoon = AnaerobicLagoon(
        weather=mocker.MagicMock(),
        time=mocker.MagicMock(),
        manure_treatment_config=mocker.MagicMock(),
    )
    mocker.patch(
        "RUFAS.routines.manure.manure_treatments.anaerobic_lagoon.AnaerobicLagoon.lagoon_depth",
        new_callable=PropertyMock,
        return_value=lagoon_depth,
    )
    mocker.patch(
        "RUFAS.routines.manure.manure_treatments.anaerobic_lagoon.AnaerobicLagoon.lagoon_slope",
        new_callable=PropertyMock,
        return_value=lagoon_slope,
    )
    mocker.patch(
        "RUFAS.routines.manure.manure_treatments.anaerobic_lagoon.AnaerobicLagoon.volume_needed",
        new_callable=PropertyMock,
        return_value=volume_needed,
    )

    # Act & Assert
    if raises_error:
        with pytest.raises(ValueError):
            anaerobic_lagoon._calc_lagoon_width_coefficients()
    else:
        (
            actual_a,
            actual_b,
            actual_c,
        ) = anaerobic_lagoon._calc_lagoon_width_coefficients()
        assert actual_a == approx(expected_a)
        assert actual_b == approx(expected_b)
        assert actual_c == approx(expected_c)


@pytest.mark.parametrize(
    "a, b, c, expected_width",
    [
        (2.0, -10.0, 4.0, 4.561553),  # Generic case
        (2.0, -8.0, 4.0, 3.414213),  # Another generic case
        (4.0, 4.0, 4.0, 0.0),  # Negative discriminant case
        (2.0, 10.0, 4.0, 0.0),  # Both roots negative
        (2.0, 0.0, 0.0, 0.0),  # b = 0, c = 0 case
    ],
)
def test_anaerobic_lagoon_width(
        mocker: MockFixture, a: float, b: float, c: float, expected_width: float
) -> None:
    """
    Unit test for lagoon_width property in anaerobic_lagoon.py.

    This test checks that the method correctly calculates the width of the lagoon based on the coefficients of the
    quadratic equation derived from lagoon depth, slope, and volume needed.

    """
    # Arrange
    anaerobic_lagoon = AnaerobicLagoon(
        weather=mocker.MagicMock(),
        time=mocker.MagicMock(),
        manure_treatment_config=mocker.MagicMock(),
    )
    mocker.patch.object(
        anaerobic_lagoon, "_calc_lagoon_width_coefficients", return_value=(a, b, c)
    )

    # Act & Assert
    assert anaerobic_lagoon.lagoon_width == approx(expected_width)


@pytest.mark.parametrize("lagoon_width", [5.0, 10.0, 15.0, 20.0, 25.0])
def test_anaerobic_lagoon_length(mocker: MockFixture, lagoon_width: float) -> None:
    """
    Unit test for lagoon_length property in anaerobic_lagoon.py.

    This test checks that the method correctly calculates the length of the lagoon based on the given width.
    The length of the lagoon is assumed to be three times the width.

    """
    # Arrange
    anaerobic_lagoon = AnaerobicLagoon(
        weather=mocker.MagicMock(),
        time=mocker.MagicMock(),
        manure_treatment_config=mocker.MagicMock(),
    )
    patch_for_lagoon_width_property = mocker.patch(
        "RUFAS.routines.manure.manure_treatments.anaerobic_lagoon."
        "AnaerobicLagoon.lagoon_width",
        new_callable=PropertyMock,
        return_value=lagoon_width,
    )
    expected_anaerobic_lagoon_length = lagoon_width * 3

    # Act
    actual_anaerobic_lagoon_length = anaerobic_lagoon.lagoon_length

    # Assert
    patch_for_lagoon_width_property.assert_called_once()
    assert actual_anaerobic_lagoon_length == approx(expected_anaerobic_lagoon_length)


@pytest.mark.parametrize(
    "lagoon_width, lagoon_length",
    [
        (5.0, 15.0),  # Generic case
        (10.0, 30.0),  # Generic case
        (15.0, 45.0),  # Generic case
        (0.0, 0.0),  # Zero width and length
        (10.0, 0.0),  # Zero length
        (0.0, 30.0),  # Zero width
    ],
)
def test_anaerobic_lagoon_surface_area(
        mocker: MockFixture, lagoon_width: float, lagoon_length: float
) -> None:
    """
    Unit test for lagoon_surface_area property in anaerobic_lagoon.py.

    This test checks that the method correctly calculates the surface area
    of the lagoon based on the given width and length.

    """
    # Arrange
    anaerobic_lagoon = AnaerobicLagoon(
        weather=mocker.MagicMock(),
        time=mocker.MagicMock(),
        manure_treatment_config=mocker.MagicMock(),
    )
    patch_for_lagoon_width_property = mocker.patch(
        "RUFAS.routines.manure.manure_treatments.anaerobic_lagoon."
        "AnaerobicLagoon.lagoon_width",
        new_callable=PropertyMock,
        return_value=lagoon_width,
    )
    patch_for_lagoon_length_property = mocker.patch(
        "RUFAS.routines.manure.manure_treatments.anaerobic_lagoon."
        "AnaerobicLagoon.lagoon_length",
        new_callable=PropertyMock,
        return_value=lagoon_length,
    )
    expected_anaerobic_lagoon_surface_area = lagoon_width * lagoon_length

    # Act
    actual_anaerobic_lagoon_surface_area = anaerobic_lagoon.lagoon_surface_area

    # Assert
    patch_for_lagoon_width_property.assert_called_once()
    patch_for_lagoon_length_property.assert_called_once()
    assert actual_anaerobic_lagoon_surface_area == approx(
        expected_anaerobic_lagoon_surface_area
    )


@pytest.mark.parametrize(
    "lagoon_length, lagoon_width, lagoon_depth, lagoon_slope, expected_volume",
    [
        (30.0, 10.0, 5.0, 0.01, 1491.666667),  # Standard case with moderate slope
        (
                50.0,
                20.0,
                5.0,
                0.02,
                4968.333333,
        ),  # Larger lagoon dimensions and higher slope
        (20.0, 15.0, 3.0, 0.03, 891.63),  # Smaller depth and higher slope
        (0.0, 0.0, 0.0, 0.0, 0.0),  # Edge case: zero dimensions
        (50.0, 50.0, 0.0, 0.01, 0.0),  # Edge case: zero depth
        (50.0, 50.0, 5.0, 0.0, 12500.0),  # Edge case: zero slope
    ],
)
def test_calc_modeled_lagoon_volume(
        mocker: MockFixture,
        lagoon_length: float,
        lagoon_width: float,
        lagoon_depth: float,
        lagoon_slope: float,
        expected_volume: float,
) -> None:
    """
    Unit test for _calc_modeled_lagoon_volume() in anaerobic_lagoon.py.

    This test verifies that the method correctly calculates the modeled lagoon volume
    based on different scenarios, including standard cases, larger and smaller lagoon dimensions,
    various slopes, and edge cases with zero dimensions.

    """
    # Arrange
    anaerobic_lagoon = AnaerobicLagoon(
        weather=mocker.MagicMock(),
        time=mocker.MagicMock(),
        manure_treatment_config=mocker.MagicMock(),
    )
    mocker.patch(
        "RUFAS.routines.manure.manure_treatments.anaerobic_lagoon.AnaerobicLagoon.lagoon_length",
        new_callable=PropertyMock,
        return_value=lagoon_length,
    )
    mocker.patch(
        "RUFAS.routines.manure.manure_treatments.anaerobic_lagoon.AnaerobicLagoon.lagoon_width",
        new_callable=PropertyMock,
        return_value=lagoon_width,
    )
    mocker.patch(
        "RUFAS.routines.manure.manure_treatments.anaerobic_lagoon.AnaerobicLagoon.lagoon_depth",
        new_callable=PropertyMock,
        return_value=lagoon_depth,
    )
    mocker.patch(
        "RUFAS.routines.manure.manure_treatments.anaerobic_lagoon.AnaerobicLagoon.lagoon_slope",
        new_callable=PropertyMock,
        return_value=lagoon_slope,
    )

    # Act
    actual_modeled_lagoon_volume = anaerobic_lagoon._calc_modeled_lagoon_volume()

    # Assert
    assert actual_modeled_lagoon_volume == approx(expected_volume)


@pytest.mark.parametrize(
    "current_day_rainfall, lagoon_surface_area, expected_precipitation_volume",
    [
        (10.0, 300.0, 3000.0),  # Generic case with rainfall and surface area
        (20.0, 400.0, 8000.0),  # Increased rainfall and surface area
        (0.0, 1000.0, 0.0),  # Zero rainfall, should result in zero volume
        (50.0, 0.0, 0.0),  # Zero surface area, should result in zero volume
        (5.5, 200.0, 1100.0),  # Fractional rainfall with different surface area
        (100.0, 50.0, 5000.0),  # More rainfall with smaller surface area
    ],
)
def test_anaerobic_lagoon_precipitation_volume(
        mocker: MockFixture,
        current_day_rainfall: float,
        lagoon_surface_area: float,
        expected_precipitation_volume: float,
) -> None:
    """
    Unit test for property precipitation_volume in anaerobic_lagoon.py.

    This test checks that the calculation of additional lagoon volume needed for precipitation
    is performed correctly, taking into account the current day's rainfall and the lagoon surface area.

    """
    # Arrange
    anaerobic_lagoon = AnaerobicLagoon(
        weather=mocker.MagicMock(),
        time=mocker.MagicMock(),
        manure_treatment_config=mocker.MagicMock(),
    )
    mocker.patch.object(
        anaerobic_lagoon, "_get_current_day_rainfall", return_value=current_day_rainfall
    )
    mocker.patch(
        "RUFAS.routines.manure.manure_treatments.anaerobic_lagoon."
        "AnaerobicLagoon.lagoon_surface_area",
        new_callable=PropertyMock,
        return_value=lagoon_surface_area,
    )

    # Act
    actual_precipitation_volume = anaerobic_lagoon.precipitation_volume

    # Assert
    assert actual_precipitation_volume == approx(expected_precipitation_volume)


@pytest.mark.parametrize(
    "freeboard_input, lagoon_surface_area, expected_freeboard_volume",
    [
        (0.5, 300.0, 150.0),  # Generic case with freeboard input and surface area
        (0.0, 400.0, 0.0),  # Zero freeboard input, should result in zero volume
        (1.0, 0.0, 0.0),  # Zero surface area, should result in zero volume
        (0.2, 500.0, 100.0),  # Different freeboard input with different surface area
    ],
)
def test_anaerobic_lagoon_freeboard_volume(
        mocker: MockFixture,
        freeboard_input: float,
        lagoon_surface_area: float,
        expected_freeboard_volume: float,
) -> None:
    """
    Unit test for property freeboard_volume in anaerobic_lagoon.py.

    This test checks that the calculation of additional lagoon volume needed for freeboard
    is performed correctly, taking into account the freeboard input and the lagoon surface area.

    """
    # Arrange
    anaerobic_lagoon = AnaerobicLagoon(
        weather=mocker.MagicMock(),
        time=mocker.MagicMock(),
        manure_treatment_config=mocker.MagicMock(),
    )
    anaerobic_lagoon.freeboard_input = freeboard_input
    mocker.patch(
        "RUFAS.routines.manure.manure_treatments.anaerobic_lagoon."
        "AnaerobicLagoon.lagoon_surface_area",
        new_callable=PropertyMock,
        return_value=lagoon_surface_area,
    )

    # Act
    actual_freeboard_volume = anaerobic_lagoon.freeboard_volume

    # Assert
    assert actual_freeboard_volume == approx(expected_freeboard_volume)


@pytest.mark.parametrize(
    "sludge_accumulation_volume, calculated_sludge_accumulation_volume, lower_bound, upper_bound, expected",
    [
        # Normal case, calculated value within bounds
        (150.0, 100.0, 0.2, 0.8, 100.0),
        # Calculated value below lower bound
        (150.0, 50.0, 0.2, 0.8, 50.0),
        # Calculated value above upper bound
        (150.0, 200.0, 0.2, 0.8, 120.0),
        # Lower and upper bounds are equal
        (150.0, 100.0, 0.5, 0.5, 75.0),
        # Lower and upper bounds are zero
        (150.0, 100.0, 0.0, 0.0, 0.0),
        # Error cases
        # Calculated value is negative
        (150.0, -10.0, 0.2, 0.8, ValueError),
        # Lower bound is negative
        (150.0, 100.0, -0.2, 0.8, ValueError),
        # Upper bound is less than lower bound
        (150.0, 100.0, 0.8, 0.2, ValueError),
    ],
)
def test_bound_sludge_accumulation_volume(
        mocker: MockFixture,
        sludge_accumulation_volume: float,
        calculated_sludge_accumulation_volume: float,
        lower_bound: float,
        upper_bound: float,
        expected: float,
) -> None:
    """
    Unit test for _bound_sludge_accumulation_volume() in anaerobic_lagoon.py.

    This test checks that the _bound_sludge_accumulation_volume() method correctly bounds the calculated
    sludge accumulation volume according to the specified lower and upper bounds, given as proportions
    of the current sludge accumulation volume.

    """
    # Arrange
    anaerobic_lagoon = AnaerobicLagoon(
        weather=mocker.MagicMock(),
        time=mocker.MagicMock(),
        manure_treatment_config=mocker.MagicMock(),
    )
    patch_for_sludge_accumulation_volume_property = mocker.patch(
        "RUFAS.routines.manure.manure_treatments.anaerobic_lagoon."
        "AnaerobicLagoon.sludge_accumulation_volume",
        new_callable=PropertyMock,
        return_value=sludge_accumulation_volume,
    )

    # Act & Assert
    if expected == ValueError:
        with pytest.raises(ValueError):
            anaerobic_lagoon._bound_sludge_accumulation_volume(
                calculated_sludge_accumulation_volume=calculated_sludge_accumulation_volume,
                lower_bound=lower_bound,
                upper_bound=upper_bound,
            )
    else:
        actual_bound_sludge_accumulation_volume = anaerobic_lagoon._bound_sludge_accumulation_volume(
            calculated_sludge_accumulation_volume=calculated_sludge_accumulation_volume,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
        )
        assert patch_for_sludge_accumulation_volume_property.call_count == 2
        assert actual_bound_sludge_accumulation_volume == approx(expected)


# Test AnaerobicDigestion-specific methods
# ========================================


def test_daily_update_helper(mocker: MockFixture) -> None:
    """Unit test for _daily_update_helper() in anaerobic_lagoon.py."""
    # Arrange
    anaerobic_digestion = AnaerobicDigestion(
        weather=mocker.MagicMock(),
        time=mocker.MagicMock(),
        manure_treatment_config=mocker.MagicMock(),
    )
    current_manure_treatment_daily_input = mocker.MagicMock()
    anaerobic_digestion._current_manure_treatment_daily_input = (
        current_manure_treatment_daily_input
    )
    initial_daily_output = mocker.MagicMock()
    patch_for_initialize_daily_output_during_update = mocker.patch.object(
        anaerobic_digestion,
        "_initialize_daily_output_during_update",
        return_value=initial_daily_output,
    )
    daily_output_with_sludge_output = mocker.MagicMock()
    patch_for_calc_daily_sludge_output = mocker.patch.object(
        anaerobic_digestion,
        "_calc_daily_sludge_output",
        return_value=daily_output_with_sludge_output,
    )
    complete_daily_output = mocker.MagicMock()
    patch_for_calc_anaerobic_digestion_daily_output = mocker.patch.object(
        anaerobic_digestion,
        "_calc_anaerobic_digestion_daily_output",
        return_value=complete_daily_output,
    )
    patch_for_accumulate_daily_output = mocker.patch.object(
        anaerobic_digestion, "_accumulate_daily_output"
    )

    # Act
    actual_daily_output = anaerobic_digestion._daily_update_helper()

    # Assert
    patch_for_initialize_daily_output_during_update.assert_called_once_with(
        current_manure_treatment_daily_input
    )
    patch_for_calc_daily_sludge_output.assert_called_once_with(
        initial_daily_output, current_manure_treatment_daily_input
    )
    patch_for_calc_anaerobic_digestion_daily_output.assert_called_once_with(
        daily_output_with_sludge_output
    )
    patch_for_accumulate_daily_output.assert_called_once_with(complete_daily_output)
    assert actual_daily_output == complete_daily_output


def test_calc_anaerobic_digestion_daily_output(mocker: MockFixture) -> None:
    """Unit test for _calc_anaerobic_digestion_daily_output() in anaerobic_digestion.py."""
    # Arrange
    mock_manure_treatment_config = mocker.MagicMock()
    mock_manure_treatment_config.hydraulic_retention_time = (
        hydraulic_retention_time
    ) = 12
    mock_manure_treatment_config.top_cover_volume_fraction = (
        top_cover_volume_fraction
    ) = 0.4
    mock_manure_treatment_config.biogas_generation_ratio = biogas_generation_ratio = 0.6
    mock_manure_treatment_config.evaporation_fraction = evaporation_fraction = 0.1
    anaerobic_digestion = AnaerobicDigestion(
        weather=mocker.MagicMock(),
        time=mocker.MagicMock(),
        manure_treatment_config=mock_manure_treatment_config,
    )
    mock_manure_handler_daily_output = mocker.MagicMock()
    mock_manure_handler_daily_output.liquid_manure_total_solids = (
        liquid_manure_total_solids
    ) = 50.0
    mock_manure_handler_daily_output.liquid_manure_total_volatile_solids = (
        liquid_manure_total_volatile_solids
    ) = 35.0
    anaerobic_digestion._manure_handler_daily_output = mock_manure_handler_daily_output

    mock_manure_treatment_daily_output = mocker.MagicMock()
    mock_manure_treatment_daily_output.daily_final_manure_volume = (
        daily_final_manure_volume
    ) = 100.0
    mock_manure_treatment_daily_output.clone.return_value = (
        mock_manure_treatment_daily_output
    )

    moisture_content = 0.5
    patch_for_calc_moisture_content = mocker.patch.object(
        anaerobic_digestion, "_calc_moisture_content", return_value=moisture_content
    )

    average_temperature_celsius = 20.0
    patch_for_get_current_day_average_temperature_celsius = mocker.patch.object(
        anaerobic_digestion,
        "_get_current_day_average_temperature_celsius",
        return_value=average_temperature_celsius,
    )

    specific_input_energy = 70.0
    patch_for_calc_specific_input_energy = mocker.patch.object(
        anaerobic_digestion,
        "_calc_specific_input_energy",
        return_value=specific_input_energy,
    )

    methane_generation_volume = 200.0
    patch_for_calc_methane_volume_via_Chen_equation = mocker.patch(
        "RUFAS.routines.manure.manure_treatments.anaerobic_digestion."
        "GasEmissionsCalculator.methane_volume_via_Chen_equation",
        return_value=methane_generation_volume,
    )

    biogas_energy_content = 500.0
    patch_for_calc_biogas_energy_content = mocker.patch(
        "RUFAS.routines.manure.manure_treatments.anaerobic_digestion."
        "GasEmissionsCalculator.biogas_energy_content",
        return_value=biogas_energy_content,
    )

    expected_biogas = biogas_generation_ratio * liquid_manure_total_volatile_solids
    expected_heating_input_energy = (
            specific_input_energy
            * daily_final_manure_volume
            * GeneralConstants.LITERS_TO_CUBIC_METERS
    )
    expected_evaporated_water = evaporation_fraction * daily_final_manure_volume
    expected_biogas_energy_content = biogas_energy_content
    expected_minimum_digester_volume = (
            daily_final_manure_volume * hydraulic_retention_time
    )
    expected_top_cover_volume = (
            expected_minimum_digester_volume * top_cover_volume_fraction
    )

    # Act
    actual_anaerobic_digestion_daily_output = (
        anaerobic_digestion._calc_anaerobic_digestion_daily_output(
            mock_manure_treatment_daily_output
        )
    )

    # Assert
    mock_manure_treatment_daily_output.clone.assert_called_once()
    patch_for_calc_moisture_content.assert_called_once_with(
        total_daily_mass=daily_final_manure_volume,
        liquid_manure_total_solids=liquid_manure_total_solids,
    )
    patch_for_get_current_day_average_temperature_celsius.assert_called_once()
    patch_for_calc_specific_input_energy.assert_called_once_with(
        average_temperature_celsius, moisture_content
    )
    patch_for_calc_methane_volume_via_Chen_equation.assert_called_once_with(
        manure_total_volatile_solids=liquid_manure_total_volatile_solids,
        hydraulic_retention_time=hydraulic_retention_time,
    )
    patch_for_calc_biogas_energy_content.assert_called_once_with(
        methane_volume=methane_generation_volume
    )

    assert actual_anaerobic_digestion_daily_output.biogas == approx(expected_biogas)
    assert actual_anaerobic_digestion_daily_output.heating_input_energy == approx(
        expected_heating_input_energy
    )
    assert actual_anaerobic_digestion_daily_output.evaporated_water == approx(
        expected_evaporated_water
    )
    assert actual_anaerobic_digestion_daily_output.biogas_energy_content == approx(
        expected_biogas_energy_content
    )
    assert actual_anaerobic_digestion_daily_output.minimum_digester_volume == approx(
        expected_minimum_digester_volume
    )
    assert actual_anaerobic_digestion_daily_output.top_cover_volume == approx(
        expected_top_cover_volume
    )


@pytest.mark.parametrize(
    "total_daily_mass",
    [
        -1.0,
        0.0,
        0.5,
        1.0,
        100.0,
    ],
)
def test_calc_moisture_content(total_daily_mass: float) -> None:
    """Unit test for _calc_moisture_content() in anaerobic_digestion.py."""
    # Arrange
    liquid_manure_total_solids = 20.0
    if total_daily_mass > 0:
        expected_moisture_content = 1 - (liquid_manure_total_solids / total_daily_mass)
    else:
        expected_moisture_content = 0.0

    # Act
    actual_moisture_content = AnaerobicDigestion._calc_moisture_content(
        total_daily_mass=total_daily_mass,
        liquid_manure_total_solids=liquid_manure_total_solids,
    )

    # Assert
    assert actual_moisture_content == approx(expected_moisture_content)


def test_calc_specific_input_energy(mocker: MockFixture) -> None:
    """Unit test for _calc_specific_input_energy() in anaerobic_digestion.py."""
    # Arrange
    mock_manure_treatment_config = mocker.MagicMock()
    mock_manure_treatment_config.anaerobic_digestion_temperature_set_point = (
        anaerobic_digestion_temperature_set_point
    ) = 35.0
    anaerobic_digestion = AnaerobicDigestion(
        weather=mocker.MagicMock(),
        time=mocker.MagicMock(),
        manure_treatment_config=mock_manure_treatment_config,
    )
    average_temperature_celsius = 20.0
    moisture_content = 0.5
    effluent_temperature = 30.0
    patch_for_bound_influent_temperature = mocker.patch.object(
        anaerobic_digestion,
        "_bound_influent_temperature",
        return_value=effluent_temperature,
    )
    influent_heat_capacity = 4.2
    anaerobic_digestion_heat_capacity = 5.8
    patch_for_calc_manure_heat_capacity = mocker.patch.object(
        anaerobic_digestion,
        "_calc_manure_heat_capacity",
        side_effect=[influent_heat_capacity, anaerobic_digestion_heat_capacity],
    )
    average_manure_heat_capacity = (
                                           influent_heat_capacity + anaerobic_digestion_heat_capacity
                                   ) / 2
    expected_heating_input_energy = average_manure_heat_capacity * (
            anaerobic_digestion_temperature_set_point - effluent_temperature
    )

    # Act
    actual_heating_input_energy = anaerobic_digestion._calc_specific_input_energy(
        average_temperature_celsius=average_temperature_celsius,
        moisture_content=moisture_content,
    )

    # Assert
    patch_for_bound_influent_temperature.assert_called_once_with(
        average_temperature_celsius
    )
    assert patch_for_calc_manure_heat_capacity.call_args_list == [
        call(average_temperature_celsius, moisture_content),
        call(anaerobic_digestion_temperature_set_point, moisture_content),
    ]
    assert actual_heating_input_energy == approx(expected_heating_input_energy)


@pytest.mark.parametrize("average_temperature_celsius", [3.9, 4.0, 4.1])
def test_bound_influent_temperature(average_temperature_celsius: float) -> None:
    """Unit test for _bound_influent_temperature() in anaerobic_digestion.py."""
    # Arrange
    if average_temperature_celsius <= 4.0:
        expected_bound_influent_temperature = 4.0
    else:
        expected_bound_influent_temperature = average_temperature_celsius

    # Act
    actual_bound_influent_temperature = AnaerobicDigestion._bound_influent_temperature(
        average_temperature_celsius=average_temperature_celsius
    )

    # Assert
    assert actual_bound_influent_temperature == approx(
        expected_bound_influent_temperature
    )


def test_calc_manure_heat_capacity() -> None:
    """Unit test for _calc_manure_heat_capacity() in anaerobic_digestion.py."""
    # Arrange
    average_temperature_celsius = 20.0
    moisture_content = 0.5
    expected_manure_heat_capacity = (
            0.68298
            + 0.025662 * average_temperature_celsius
            + 0.01306 * moisture_content * 100
    )

    # Act
    actual_manure_heat_capacity = AnaerobicDigestion._calc_manure_heat_capacity(
        average_temperature_celsius=average_temperature_celsius,
        moisture_content=moisture_content,
    )

    # Assert
    assert actual_manure_heat_capacity == approx(expected_manure_heat_capacity)


# Test AnaerobicDigestionAndLagoon class
# ======================================


def test_anaerobic_digestion_and_lagoon_init(mocker: MockFixture) -> None:
    """Unit test for __init__() in anaerobic_digestion_and_lagoon.py."""
    # Arrange
    mock_weather = mocker.MagicMock()
    mock_time = mocker.MagicMock()
    mock_manure_treatment_config = (mocker.MagicMock(), mocker.MagicMock())

    def mock_base_manure_treatment(
            self, weather, time, manure_treatment_config: ManureTreatmentConfig
    ) -> None:
        self.weather = weather
        self.time = time
        self.config = manure_treatment_config

    mocker.patch(
        "RUFAS.routines.manure.manure_treatments.base_manure_treatment.BaseManureTreatment.__init__",
        new=mock_base_manure_treatment,
    )

    patch_for_anaerobic_digestion_init = mocker.patch(
        "RUFAS.routines.manure.manure_treatments.anaerobic_digestion_and_lagoon.AnaerobicDigestion.__init__",
        return_value=None,
    )
    patch_for_anaerobic_lagoon_init = mocker.patch(
        "RUFAS.routines.manure.manure_treatments.anaerobic_digestion_and_lagoon.AnaerobicLagoon.__init__",
        return_value=None,
    )

    # Act
    anaerobic_digestion_and_lagoon = AnaerobicDigestionAndLagoon(
        weather=mock_weather,
        time=mock_time,
        manure_treatment_config=mock_manure_treatment_config,
    )

    # Assert
    patch_for_anaerobic_digestion_init.assert_called_once_with(
        mock_weather, mock_time, mock_manure_treatment_config[0]
    )
    assert anaerobic_digestion_and_lagoon.anaerobic_digestion_daily_output is None
    patch_for_anaerobic_lagoon_init.assert_called_once_with(
        mock_weather, mock_time, mock_manure_treatment_config[1]
    )


def test_create_anaerobic_digestion_daily_output(mocker: MockFixture) -> None:
    """Unit test for _create_anaerobic_digestion_daily_output() in anaerobic_digestion_and_lagoon.py."""
    # Arrange
    mocker.patch(
        "RUFAS.routines.manure.manure_treatments.anaerobic_digestion_and_lagoon"
        ".AnaerobicDigestionAndLagoon.__init__",
        return_value=None,
    )
    anaerobic_digestion_and_lagoon = AnaerobicDigestionAndLagoon(
        weather=mocker.MagicMock(),
        time=mocker.MagicMock(),
        manure_treatment_config=(mocker.MagicMock(), mocker.MagicMock()),
    )
    anaerobic_digestion_and_lagoon._manure_handler_daily_output = (
        mock_manure_handler_daily_output
    ) = mocker.MagicMock()
    anaerobic_digestion_and_lagoon._current_manure_treatment_daily_input = (
        mock_current_manure_treatment_daily_input
    ) = mocker.MagicMock()
    anaerobic_digestion_and_lagoon._current_pen = mock_current_pen = mocker.MagicMock()
    anaerobic_digestion_and_lagoon._sim_day = mock_sim_day = mocker.MagicMock()
    mock_anaerobic_digestion_daily_output = mocker.MagicMock()
    mock_anaerobic_digestion = mocker.MagicMock()
    mock_anaerobic_digestion.daily_update.return_value = (
        mock_anaerobic_digestion_daily_output
    )
    anaerobic_digestion_and_lagoon._anaerobic_digestion = mock_anaerobic_digestion

    # Act
    actual_anaerobic_digestion_daily_output = (
        anaerobic_digestion_and_lagoon._create_anaerobic_digestion_daily_output()
    )

    # Assert
    mock_anaerobic_digestion.daily_update.assert_called_once_with(
        manure_handler_daily_output=mock_manure_handler_daily_output,
        manure_treatment_daily_input=mock_current_manure_treatment_daily_input,
        pen=mock_current_pen,
        sim_day=mock_sim_day,
    )
    assert (
            actual_anaerobic_digestion_daily_output == mock_anaerobic_digestion_daily_output
    )


@pytest.mark.parametrize("manure_separator_exists", [True, False])
def test_anaerobic_digestion_and_lagoon_daily_update_helper(
        manure_separator_exists: bool, mocker: MockFixture
) -> None:
    """Unit test for _daily_update_helper() in anaerobic_digestion_and_lagoon.py."""
    # Arrange
    mocker.patch(
        "RUFAS.routines.manure.manure_treatments.anaerobic_digestion_and_lagoon"
        ".AnaerobicDigestionAndLagoon.__init__",
        return_value=None,
    )
    anaerobic_digestion_and_lagoon = AnaerobicDigestionAndLagoon(
        weather=mocker.MagicMock(),
        time=mocker.MagicMock(),
        manure_treatment_config=(mocker.MagicMock(), mocker.MagicMock()),
    )
    mock_anaerobic_digestion_daily_output = mocker.MagicMock()
    patch_for_create_anaerobic_digestion_daily_output = mocker.patch.object(
        anaerobic_digestion_and_lagoon,
        "_create_anaerobic_digestion_daily_output",
        return_value=mock_anaerobic_digestion_daily_output,
    )

    if manure_separator_exists:
        mock_manure_separator = mocker.MagicMock()
        mock_manure_separator.daily_update.return_value = (
            mock_manure_separator_daily_output
        ) = mocker.MagicMock()
    else:
        mock_manure_separator = None
        mock_manure_separator_daily_output = None
    anaerobic_digestion_and_lagoon._manure_separator = mock_manure_separator

    mock_anaerobic_lagoon = mocker.MagicMock()
    mock_anaerobic_lagoon.daily_update.return_value = (
        mock_anaerobic_lagoon_daily_output
    ) = mocker.MagicMock()
    anaerobic_digestion_and_lagoon._anaerobic_lagoon = mock_anaerobic_lagoon

    anaerobic_digestion_and_lagoon._manure_handler_daily_output = (
        mock_manure_handler_daily_output
    ) = mocker.MagicMock()
    anaerobic_digestion_and_lagoon._current_pen = mock_current_pen = mocker.MagicMock()
    anaerobic_digestion_and_lagoon._sim_day = mock_sim_day = mocker.MagicMock()

    # Act
    actual_anaerobic_lagoon_daily_output = (
        anaerobic_digestion_and_lagoon._daily_update_helper()
    )

    # Assert
    patch_for_create_anaerobic_digestion_daily_output.assert_called_once()
    assert (
            anaerobic_digestion_and_lagoon.anaerobic_digestion_daily_output
            == mock_anaerobic_digestion_daily_output
    )

    if manure_separator_exists:
        mock_manure_separator.daily_update.assert_called_once_with(
            manure_separator_daily_input=mock_anaerobic_digestion_daily_output
        )
    assert (
            anaerobic_digestion_and_lagoon._manure_separator_daily_output
            == mock_manure_separator_daily_output
    )

    if manure_separator_exists:
        mock_anaerobic_lagoon.daily_update.assert_called_once_with(
            manure_handler_daily_output=mock_manure_handler_daily_output,
            manure_treatment_daily_input=mock_manure_separator_daily_output,
            pen=mock_current_pen,
            sim_day=mock_sim_day,
        )
    else:
        mock_anaerobic_lagoon.daily_update.assert_called_once_with(
            manure_handler_daily_output=mock_manure_handler_daily_output,
            manure_treatment_daily_input=mock_anaerobic_digestion_daily_output,
            pen=mock_current_pen,
            sim_day=mock_sim_day,
        )

    assert actual_anaerobic_lagoon_daily_output == mock_anaerobic_lagoon_daily_output


# Test CompostBeddedPackBarn specific methods
# ==========================================


def test_compost_bedded_pack_barn_init(mocker: MockFixture) -> None:
    """Unit test for __init__() in CompostBeddedPackBarn in compost_bedded_pack_barn.py"""
    # Arrange
    mock_weather = mocker.MagicMock()
    mock_time = mocker.MagicMock()
    mock_manure_treatment_config = mocker.MagicMock()

    def mock_base_manure_treatment(
            self, weather, time, manure_treatment_config: ManureTreatmentConfig
    ) -> None:
        self.weather = weather
        self.time = time
        self.config = manure_treatment_config

    mocker.patch(
        "RUFAS.routines.manure.manure_treatments.base_manure_treatment.BaseManureTreatment.__init__",
        new=mock_base_manure_treatment,
    )

    # Act
    cbpb = CompostBeddedPackBarn(
        weather=mock_weather,
        time=mock_time,
        manure_treatment_config=mock_manure_treatment_config,
    )

    # Assert
    assert cbpb.weather == mock_weather
    assert cbpb.time == mock_time


@pytest.mark.parametrize(
    'manure_total_solids, bedding_total_solids, manure_volatile_solids,'
    'moisture_effect, days_since_last_tillage, lag,'
    'carbon_fraction_available_in_manure, carbon_fraction_available_in_bedding,'
    'mock_temp, mock_methane_emission, mock_carbon_decomposition,'
    'expected_outputs',
    [
        # Normal case
        (10.0, 5.0, 7.0,
         0.5, 7, 3,
         0.4, 0.6,
         25.0, 1.0, 0.5,
         (6.0, 13.0, 2.0)),

        # Zero values
        (0.0, 0.0, 0.0,
         0.0, 0, 0,
         0.0, 0.0,
         0.0, 0.0, 0.0,
         (0.0, 0.0, 0.0)),

        # Larger values and lower temperature
        (100.0, 50.0, 70.0,
         0.8, 10, 5,
         0.5, 0.7,
         10.0, 5.0, 3.0,
         (65.0, 139.0, 11.0)),

        # Values at upper limits or where multipliers are maxed
        (10.0, 5.0, 7.0,
         1.0, 7, 3,
         1.0, 1.0,
         35.0, 2.0, 1.0,
         (5.0, 11.0, 4.0))
    ]
)
def test_calc_dry_matter_changes(
        mocker: MockFixture,
        manure_total_solids: float,
        bedding_total_solids: float,
        manure_volatile_solids: float,
        moisture_effect: float,
        days_since_last_tillage: int,
        lag: int,
        carbon_fraction_available_in_manure: float,
        carbon_fraction_available_in_bedding: float,
        mock_temp: float,
        mock_methane_emission: float,
        mock_carbon_decomposition: float,
        expected_outputs: tuple[float, float, float]
) -> None:
    """
    Unit test for _calc_dry_matter_changes() in CompostBeddedPackBarn in compost_bedded_pack_barn.py

    This test verifies that the method correctly calculates changes in dry matter based on various parameters.
    """

    # Arrange
    mocker.patch(
        'RUFAS.routines.manure.manure_treatments.compost_bedded_pack_barn.CompostBeddedPackBarn.__init__',
        return_value=None
    )
    cbpb = CompostBeddedPackBarn(weather=mocker.MagicMock(), time=mocker.MagicMock(),
                                 manure_treatment_config=mocker.MagicMock())

    mocker.patch.object(cbpb, '_get_current_day_average_temperature_celsius', return_value=mock_temp)

    mocker.patch.object(GasEmissionsCalculator, 'ifsm_methane_emission', return_value=mock_methane_emission)

    mocker.patch.object(GasEmissionsCalculator, 'total_carbon_decomposition',
                        return_value=mock_carbon_decomposition)

    # Act
    result = cbpb._calc_dry_matter_changes(
        manure_total_solids,
        bedding_total_solids,
        manure_volatile_solids,
        moisture_effect,
        days_since_last_tillage,
        lag,
        carbon_fraction_available_in_manure,
        carbon_fraction_available_in_bedding
    )

    # Assert
    assert result == approx(expected_outputs)


def test_compost_bedded_pack_barn_daily_update_helper(mocker: MockFixture) -> None:
    """
    Unit test for _daily_update_helper() in CompostBeddedPackBarn in compost_bedded_pack_barn.py
    """

    # Arrange
    weather_mock = mocker.MagicMock()
    time_mock = mocker.MagicMock()
    manure_treatment_config_mock = mocker.MagicMock()
    daily_input_mock = mocker.MagicMock()
    daily_input_mock.liquid_manure_nitrogen = 1
    daily_input_mock.liquid_manure_total_volatile_solids = 2
    daily_input_mock.liquid_manure_total_solids = 3
    daily_input_mock.liquid_manure_daily_volume = 4
    daily_input_mock.liquid_manure_potassium = 5
    daily_input_mock.liquid_manure_phosphorus = 6

    mocker.patch("RUFAS.routines.manure.manure_treatments.compost_bedded_pack_barn"
                 ".CompostBeddedPackBarn.__init__",
                 return_value=None)
    remaining_volatile_solids = 4
    remaining_total_solids = 5
    dry_matter_loss = 6
    mocker.patch("RUFAS.routines.manure.manure_treatments.compost_bedded_pack_barn"
                 ".CompostBeddedPackBarn._calc_dry_matter_changes",
                 return_value=(remaining_volatile_solids, remaining_total_solids, dry_matter_loss))

    expected_storage_methane = 10
    mocker.patch(
        'RUFAS.routines.manure.manure_treatments.compost_bedded_pack_barn'
        '.GasEmissionsCalculator.ifsm_methane_emission',
        return_value=expected_storage_methane)

    total_nitrogen_loss_from_cbpb = 11
    mocker.patch(
        'RUFAS.routines.manure.manure_treatments.compost_bedded_pack_barn'
        '.GasEmissionsCalculator.total_nitrogen_loss_from_compost_bedded_pack_barn',
        return_value=total_nitrogen_loss_from_cbpb)

    nitrogen_loss_from_ammonia_emission = 12
    mocker.patch(
        'RUFAS.routines.manure.manure_treatments.compost_bedded_pack_barn'
        '.GasEmissionsCalculator.nitrogen_loss_in_compost_bedded_pack_barn_from_ammonia_emission',
        return_value=nitrogen_loss_from_ammonia_emission)

    nitrogen_loss_from_nitrous_oxide_emission = 13
    mocker.patch(
        'RUFAS.routines.manure.manure_treatments.compost_bedded_pack_barn'
        '.GasEmissionsCalculator.nitrogen_loss_in_compost_bedded_pack_barn_from_nitrous_oxide_emission',
        return_value=nitrogen_loss_from_nitrous_oxide_emission)

    compost_bedded_pack_barn = CompostBeddedPackBarn(weather_mock, time_mock, manure_treatment_config_mock)
    compost_bedded_pack_barn._current_manure_treatment_daily_input = daily_input_mock
    compost_bedded_pack_barn._manure_handler_daily_output = mocker.MagicMock()
    config_mock = mocker.MagicMock()
    config_mock.potassium_removal_efficiency_for_treatment = 0.5
    config_mock.phosphorus_removal_efficiency_for_treatment = 0.5
    compost_bedded_pack_barn.config = config_mock
    pen_mock = mocker.MagicMock()
    pen_mock.manure.inorganic_phosphorus_fraction = 0.4
    pen_mock.manure.organic_phosphorus_fraction = 0.6
    pen_mock.manure.non_water_inorganic_phosphorus_fraction = 0.3
    pen_mock.manure.non_water_organic_phosphorus_fraction = 0.7
    compost_bedded_pack_barn._current_pen = pen_mock
    mocker.patch.object(compost_bedded_pack_barn, '_get_current_day_average_temperature_celsius', return_value=20)
    mocker.patch.object(compost_bedded_pack_barn, '_accumulate_daily_output')

    expected_manure_nitrogen = daily_input_mock.liquid_manure_nitrogen - total_nitrogen_loss_from_cbpb
    expected_manure_organic_nitrogen = (ManureConstants.COMPOST_BEDDING_ORGANIC_NITROGEN_FRACTION *
                                        expected_manure_nitrogen)
    expected_manure_inorganic_nitrogen = expected_manure_nitrogen - expected_manure_organic_nitrogen
    expected_manure_inorganic_nitrogen_ammonium = (
            ManureConstants.COMPOST_BEDDING_INORGANIC_NITROGEN_AMMONIUM_FRACTION * expected_manure_inorganic_nitrogen
    )
    expected_solid_manure_daily_mass = remaining_total_solids / (
            daily_input_mock.liquid_manure_total_solids / (daily_input_mock.liquid_manure_daily_volume *
                                                           ManureConstants.SOLID_MANURE_DENSITY)
    )
    expected_manure_potassium = (daily_input_mock.liquid_manure_potassium *
                                 (1 - config_mock.potassium_removal_efficiency_for_treatment))
    expected_manure_phosphorus = (daily_input_mock.liquid_manure_phosphorus *
                                  (1 - config_mock.phosphorus_removal_efficiency_for_treatment))
    expected_water_extractable_inorganic_phosphorus = (pen_mock.manure.inorganic_phosphorus_fraction *
                                                       expected_manure_phosphorus)
    expected_water_extractable_organic_phosphorus = (pen_mock.manure.organic_phosphorus_fraction *
                                                     expected_manure_phosphorus)
    expected_non_water_extractable_inorganic_phosphorus = (pen_mock.manure.non_water_inorganic_phosphorus_fraction *
                                                           expected_manure_phosphorus)
    expected_non_water_extractable_organic_phosphorus = (pen_mock.manure.non_water_organic_phosphorus_fraction *
                                                         expected_manure_phosphorus)

    # Act
    result = compost_bedded_pack_barn._daily_update_helper()

    # Assert
    assert isinstance(result, ManureTreatmentDailyOutput)
    assert result.solid_manure_nitrogen == expected_manure_nitrogen
    assert result.solid_manure_organic_nitrogen == expected_manure_organic_nitrogen
    assert result.solid_manure_inorganic_nitrogen == expected_manure_inorganic_nitrogen
    assert result.solid_manure_inorganic_nitrogen_ammonium == expected_manure_inorganic_nitrogen_ammonium
    assert result.solid_manure_daily_mass == expected_solid_manure_daily_mass
    assert result.solid_manure_potassium == expected_manure_potassium
    assert result.solid_manure_phosphorus == expected_manure_phosphorus
    assert result.solid_manure_water_extractable_inorganic_phosphorus == expected_water_extractable_inorganic_phosphorus
    assert result.solid_manure_water_extractable_organic_phosphorus == expected_water_extractable_organic_phosphorus
    assert result.solid_manure_non_water_extractable_inorganic_phosphorus == \
           expected_non_water_extractable_inorganic_phosphorus
    assert result.solid_manure_non_water_extractable_organic_phosphorus == \
           expected_non_water_extractable_organic_phosphorus
    assert result.storage_methane == expected_storage_methane
    assert result.storage_ammonia == nitrogen_loss_from_ammonia_emission
    assert result.storage_nitrous_oxide == nitrogen_loss_from_nitrous_oxide_emission
