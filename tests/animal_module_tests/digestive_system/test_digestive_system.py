from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal.data_types.animal_statistics import AnimalStatistics
from RUFAS.biophysical.animal.animal_properties.general_properties import GeneralProperties, Breed, Sex
from RUFAS.biophysical.animal.animal_properties.milk_production_properties import MilkProductionProperties
from RUFAS.biophysical.animal.animal_properties.nutrient_properties import NutrientProperties
from RUFAS.biophysical.animal.data_types.animal_events import AnimalEvents
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.milk_production_record import MilkProductionRecord
from RUFAS.biophysical.animal.digestive_system.digestive_system import DigestiveSystem
from RUFAS.biophysical.animal.digestive_system.enteric_methane_calculator import EntericMethaneCalculator
from RUFAS.biophysical.animal.digestive_system.manure_excretion_calculator import ManureExcretionCalculator
from RUFAS.biophysical.animal.data_types.animal_manure_excretions import AnimalManureExcretions
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager


@pytest.fixture
def mock_general_properties() -> GeneralProperties:
    return GeneralProperties(
        animal_type=AnimalType.CALF,
        birth_date="",
        birth_weight=0,
        body_weight=12,
        breed=Breed.HO,
        culled=False,
        days_born=0,
        days_in_preg=0,
        days_in_milk=0,
        dry_off_day_of_pregnancy=0,
        events=AnimalEvents(),
        future_cull_date=0,
        future_death_date=0,
        sex=Sex.FEMALE,
        id=0,
        mature_body_weight=0,
        nutrients={"p": 77.7, "dm": 5.23},
        sold=False,
        sold_at_day=0,
        wean_weight=0,
        nutrient_concentrations={"dm": 0.7},
        metabolizable_energy_intake=31.23,
        daily_milk_produced=17,
    )


@pytest.fixture
def mock_animal_nutrient_property() -> NutrientProperties:
    return NutrientProperties(
        estimated_daily_milk_produced=3,
        phosphorus_excess_in_diet=14.2,
        phosphorus_intake=56,
        phosphorus_requirement=0,
        phosphorus_reserves=0,
        total_phosphorus_in_animal=0,
        phosphorus_for_growth=0,
        phosphorus_endogenous_loss=0,
        ration_phosphorus_concentration=0,
        phosphorus_for_gestation=0,
        phosphorus_for_gestation_required_for_calf=0,
        fecal_phosphorus=0,
        urine_phosphorus_required=0,
    )


@pytest.fixture
def mock_milk_production_property() -> MilkProductionProperties:
    return MilkProductionProperties(
        crude_protein_content=0,
        true_protein_content=0,
        fat_content=0,
        lactose_content=0,
        milk_production_reduction=0,
        current_lactation_305_day_milk_produced=0,
        crude_protein_percent=0,
        true_protein_percent=0,
        fat_percent=0,
        lactose_percent=0,
        wood_l=0,
        wood_m=0,
        wood_n=0,
        milk_production_history=[
            MilkProductionRecord(simulation_day=0, days_in_milk=0, milk_production=0, days_born=0)
        ],
    )


@pytest.fixture
def mock_statistics() -> AnimalStatistics:
    return AnimalStatistics(methane_emission=0, phosphorus_excreted=0)


def test_daily_routine_calf(
    mock_general_properties: GeneralProperties,
    mock_milk_production_property: MilkProductionProperties,
    mock_animal_nutrient_property: NutrientProperties,
    mocker: MockerFixture,
) -> None:
    """Test the daily update when animal is calf."""
    expected_excretions = AnimalManureExcretions(
        urea=9.52,
        urine=2.0,
        manure_total_ammoniacal_nitrogen=4,
        urine_nitrogen=5,
        manure_nitrogen=6,
        manure_mass=7,
        total_solids=8,
        degradable_volatile_solids=9,
        non_degradable_volatile_solids=10,
        inorganic_phosphorus_fraction=11,
        organic_phosphorus_fraction=12,
        non_water_inorganic_phosphorus_fraction=0.0,
        non_water_organic_phosphorus_fraction=0.0,
        phosphorus=13,
        phosphorus_fraction=14,
        potassium=0,
    )
    mock_emission = mocker.patch.object(EntericMethaneCalculator, "calculate_calf_methane", return_value=15.3)
    mock_manure = mocker.patch.object(
        ManureExcretionCalculator, "calculate_calf_manure", return_value=(3, expected_excretions)
    )

    DigestiveSystem.METHANE_MODEL = "dummy model"
    DigestiveSystem.METHANE_MITIGATION_METHOD = "dummy_method"
    DigestiveSystem.METHANE_MITIGATION_ADDITIVE_AMOUNT = 16

    actual_statistics, actual_excretions = DigestiveSystem.process_digestion(
        mock_general_properties, mock_animal_nutrient_property, mock_milk_production_property
    )

    assert actual_statistics == {"enteric_methane_emission": 15.3, "phosphorus_excreted": 3}
    assert actual_excretions == expected_excretions

    mock_emission.assert_called_once_with("dummy model", 12)
    mock_manure.assert_called_once_with(12, 0, 0, {"dm": 5.23, "p": 77.7}, {"dm": 0.7})


def test_daily_routine_heifer(
    mock_general_properties: GeneralProperties,
    mock_milk_production_property: MilkProductionProperties,
    mock_animal_nutrient_property: NutrientProperties,
    mocker: MockerFixture,
) -> None:
    """Test the daily update when animal is heifer."""
    expected_excretions = AnimalManureExcretions(
        urea=9.52,
        urine=2.0,
        manure_total_ammoniacal_nitrogen=4,
        urine_nitrogen=5,
        manure_nitrogen=6,
        manure_mass=7,
        total_solids=8,
        degradable_volatile_solids=9,
        non_degradable_volatile_solids=10,
        inorganic_phosphorus_fraction=11,
        organic_phosphorus_fraction=12,
        non_water_inorganic_phosphorus_fraction=0.0,
        non_water_organic_phosphorus_fraction=0.0,
        phosphorus=13,
        phosphorus_fraction=14,
        potassium=0,
    )
    mock_general_properties.animal_type = AnimalType.HEIFER_II
    mock_emission = mocker.patch.object(EntericMethaneCalculator, "calculate_heifer_methane", return_value=15.3)
    mock_manure = mocker.patch.object(
        ManureExcretionCalculator, "calculate_heifer_manure", return_value=(3, expected_excretions)
    )

    DigestiveSystem.METHANE_MODEL = "dummy model"
    DigestiveSystem.METHANE_MITIGATION_METHOD = "dummy_method"
    DigestiveSystem.METHANE_MITIGATION_ADDITIVE_AMOUNT = 16

    actual_statistics, actual_excretions = DigestiveSystem.process_digestion(
        mock_general_properties, mock_animal_nutrient_property, mock_milk_production_property
    )

    assert actual_statistics == {"enteric_methane_emission": 15.3, "phosphorus_excreted": 3}
    assert actual_excretions == expected_excretions

    mock_emission.assert_called_once_with("dummy model", 5.23, {"dm": 0.7})
    mock_manure.assert_called_once_with(12, 0, 0, {"p": 77.7, "dm": 5.23}, {"dm": 0.7})


def test_daily_routine_cow(
    mock_general_properties: GeneralProperties,
    mock_milk_production_property: MilkProductionProperties,
    mock_animal_nutrient_property: NutrientProperties,
    mocker: MockerFixture,
) -> None:
    """Test the daily update when animal is cow."""
    expected_excretions = AnimalManureExcretions(
        urea=9.52,
        urine=2.0,
        manure_total_ammoniacal_nitrogen=4,
        urine_nitrogen=5,
        manure_nitrogen=6,
        manure_mass=7,
        total_solids=8,
        degradable_volatile_solids=9,
        non_degradable_volatile_solids=10,
        inorganic_phosphorus_fraction=11,
        organic_phosphorus_fraction=12,
        non_water_inorganic_phosphorus_fraction=0.0,
        non_water_organic_phosphorus_fraction=0.0,
        phosphorus=13,
        phosphorus_fraction=14,
        potassium=0,
    )
    mock_general_properties.animal_type = AnimalType.DRY_COW
    mock_emission = mocker.patch.object(EntericMethaneCalculator, "calculate_cow_methane", return_value=15.3)
    mock_manure = mocker.patch.object(
        ManureExcretionCalculator, "calculate_cow_manure", return_value=(3, expected_excretions)
    )

    DigestiveSystem.METHANE_MODEL = "dummy model"
    DigestiveSystem.METHANE_MITIGATION_METHOD = "dummy_method"
    DigestiveSystem.METHANE_MITIGATION_ADDITIVE_AMOUNT = 16

    actual_statistics, actual_excretions = DigestiveSystem.process_digestion(
        mock_general_properties, mock_animal_nutrient_property, mock_milk_production_property
    )

    assert actual_statistics == {"enteric_methane_emission": 15.3, "phosphorus_excreted": 3}
    assert actual_excretions == expected_excretions

    mock_emission.assert_called_once_with(
        False, 12, 0, 31.23, {"p": 77.7, "dm": 5.23}, {"dm": 0.7}, "dummy_method", 16, "dummy model"
    )
    mock_manure.assert_called_once_with(False, 12, 0, 0, 17, 0, 0, {"p": 77.7, "dm": 5.23}, {"dm": 0.7})


def test_daily_routine_error(
    mock_general_properties: GeneralProperties,
    mock_milk_production_property: MilkProductionProperties,
    mock_animal_nutrient_property: NutrientProperties,
    mocker: MockerFixture,
) -> None:
    """Test the daily update when animal is cow."""
    om = OutputManager()
    mock_animal = Mock()
    mock_animal.is_cow = False
    mock_general_properties.animal_type = mock_animal
    mock_add_error = mocker.patch.object(om, "add_error")

    try:
        DigestiveSystem.process_digestion(
            mock_general_properties, mock_animal_nutrient_property, mock_milk_production_property
        )
        assert False
    except TypeError as e:
        mock_add_error.assert_called_once()
        assert e.args[0] == "Unsupported animal types"
        assert True


def test_initialize_animal_methane_variables(mocker: MockerFixture) -> None:
    """Tests that class variables of DigestiveSystem are correctly initiated."""
    im = InputManager()
    mock_get_data = mocker.patch.object(
        im,
        "get_data",
        return_value={
            "methane_model": "test_model",
            "methane_mitigation": {
                "methane_mitigation_method": "test_mitigation_method",
                "methane_mitigation_additive_amount": 26.4,
            },
        },
    )
    DigestiveSystem.initialize_animal_methane_variables()
    assert DigestiveSystem.METHANE_MODEL == "test_model"
    assert DigestiveSystem.METHANE_MITIGATION_METHOD == "test_mitigation_method"
    assert DigestiveSystem.METHANE_MITIGATION_ADDITIVE_AMOUNT == 26.4
    mock_get_data.assert_called_once_with("animal.animal_config")
