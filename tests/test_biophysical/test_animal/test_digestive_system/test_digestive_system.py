from unittest.mock import MagicMock, PropertyMock
from RUFAS.biophysical.animal.animal_config import AnimalConfig
import pytest
from pytest_mock import MockerFixture
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.digestive_system import DigestiveSystemInputs
from RUFAS.biophysical.animal.data_types.nutrition_data_structures import NutritionSupply
from RUFAS.biophysical.animal.digestive_system.digestive_system import DigestiveSystem
from RUFAS.biophysical.animal.digestive_system.enteric_methane_calculator import EntericMethaneCalculator
from RUFAS.biophysical.animal.digestive_system.manure_excretion_calculator import ManureExcretionCalculator
from RUFAS.biophysical.animal.data_types.animal_manure_excretions import AnimalManureExcretions
from RUFAS.output_manager import OutputManager


def test_digestive_system_init() -> None:
    """
    Test the initialization of the DigestiveSystem class.
    """
    digestive_system = DigestiveSystem()

    assert isinstance(digestive_system.manure_excretion, AnimalManureExcretions)
    assert isinstance(digestive_system.phosphorus_excreted, float)
    assert digestive_system.phosphorus_excreted == 0.0


@pytest.mark.parametrize(
    "animal_type, methane_func, manure_func",
    [
        (AnimalType.CALF, "calculate_calf_methane", "calculate_calf_manure"),
        (AnimalType.HEIFER_I, "calculate_heifer_methane", "calculate_heifer_manure"),
        (AnimalType.HEIFER_II, "calculate_heifer_methane", "calculate_heifer_manure"),
        (AnimalType.HEIFER_III, "calculate_heifer_methane", "calculate_heifer_manure"),
    ],
)
def test_process_digestion_valid_animals(
    animal_type: AnimalType, methane_func: str, manure_func: str, mocker: MockerFixture
) -> None:
    """
    Test the process_digestion function for valid animal types.
    """
    digestive_system = DigestiveSystem()
    mocker.patch.object(
        AnimalConfig,
        "methane_model",
        {
            "calves": object(),
            "heiferIs": object(),
            "heiferIIs": object(),
            "heiferIIIs": object(),
        },
    )

    mock_inputs = MagicMock(spec=DigestiveSystemInputs)
    mock_inputs.animal_type = animal_type
    mock_inputs.body_weight = 100.0
    mock_inputs.nutrients = {"energy": 10.0}
    mock_inputs.phosphorus_intake = 0.5
    mock_inputs.phosphorus_requirement = 0.4
    mock_inputs.phosphorus_reserves = 0.3
    mock_inputs.phosphorus_endogenous_loss = 0.2

    mock_manure_excretion = mocker.MagicMock(spec=AnimalManureExcretions)

    mock_methane = mocker.patch.object(EntericMethaneCalculator, methane_func, return_value=5.0)
    mock_manure = mocker.patch.object(ManureExcretionCalculator, manure_func, return_value=(0.3, mock_manure_excretion))

    digestive_system.process_digestion(mock_inputs)

    mock_methane.assert_called()
    mock_manure.assert_called()
    assert digestive_system.enteric_methane_emission == 5.0
    assert digestive_system.phosphorus_excreted == 0.3
    assert digestive_system.manure_excretion is mock_manure_excretion


def test_process_digestion_cow(mocker: MockerFixture) -> None:
    """
    Test process_digestion for cow type with proper methane and manure calculations.
    """
    digestive_system = DigestiveSystem()

    mock_inputs = DigestiveSystemInputs(
        animal_type=AnimalType.LAC_COW,
        body_weight=600.0,
        nutrients=NutritionSupply(
            metabolizable_energy=50.0,
            maintenance_energy=10.0,
            lactation_energy=15.0,
            growth_energy=20.0,
            metabolizable_protein=5.0,
            calcium=0.5,
            phosphorus=0.3,
            dry_matter=50.0,
            wet_matter=50.0,
            ndf_supply=40.0,
            forage_ndf_supply=30.0,
            fat_supply=5.0,
            crude_protein=10.0,
            adf_supply=20.0,
            digestible_energy_supply=45.0,
            tdn_supply=60.0,
            lignin_supply=5.0,
            ash_supply=5.0,
            potassium_supply=0.5,
            starch_supply=5.0,
            byproduct_supply=5.0,
        ),
        days_in_milk=150,
        metabolizable_energy_intake=25.0,
        phosphorus_intake=0.4,
        phosphorus_requirement=0.3,
        phosphorus_reserves=0.2,
        phosphorus_endogenous_loss=0.1,
        daily_milk_produced=30.0,
        fat_content=3.5,
        protein_content=16.0,
    )

    mock_manure_excretion = mocker.MagicMock(spec=AnimalManureExcretions)
    mock_methane = mocker.patch.object(EntericMethaneCalculator, "calculate_cow_methane", return_value=8.0)
    mock_manure = mocker.patch.object(
        ManureExcretionCalculator, "calculate_cow_manure", return_value=(0.6, mock_manure_excretion)
    )

    digestive_system.process_digestion(mock_inputs)

    mock_methane.assert_called()
    mock_manure.assert_called()
    assert digestive_system.enteric_methane_emission == 8.0
    assert digestive_system.phosphorus_excreted == 0.6
    assert digestive_system.manure_excretion is mock_manure_excretion


def test_process_digestion_unsupported_animal(mocker: MockerFixture) -> None:
    """
    Test process_digestion raises RuntimeError for unsupported AnimalType.
    """
    digestive_system = DigestiveSystem()
    mock_inputs = DigestiveSystemInputs(
        animal_type=MagicMock(spec=AnimalType),
        body_weight=600.0,
        nutrients=NutritionSupply(
            metabolizable_energy=50.0,
            maintenance_energy=10.0,
            lactation_energy=15.0,
            growth_energy=20.0,
            metabolizable_protein=5.0,
            calcium=0.5,
            phosphorus=0.3,
            dry_matter=50.0,
            wet_matter=50.0,
            ndf_supply=40.0,
            forage_ndf_supply=30.0,
            fat_supply=5.0,
            crude_protein=10.0,
            adf_supply=20.0,
            digestible_energy_supply=45.0,
            tdn_supply=60.0,
            lignin_supply=5.0,
            ash_supply=5.0,
            potassium_supply=0.5,
            starch_supply=5.0,
            byproduct_supply=5.0,
        ),
        days_in_milk=150,
        metabolizable_energy_intake=25.0,
        phosphorus_intake=0.4,
        phosphorus_requirement=0.3,
        phosphorus_reserves=0.2,
        phosphorus_endogenous_loss=0.1,
        daily_milk_produced=30.0,
        fat_content=3.5,
        protein_content=16.0,
    )
    mock_add_error = mocker.patch.object(OutputManager, "add_error")

    with pytest.raises(TypeError, match="Unsupported animal types"):
        digestive_system.process_digestion(mock_inputs)

    mock_add_error.assert_called_once()


def test_process_digestion_unexpected_execution_path(mocker: MockerFixture) -> None:
    """
    Test process_digestion raises RuntimeError for unexpected execution path.
    """
    digestive_system = DigestiveSystem()
    mock_inputs = DigestiveSystemInputs(
        animal_type=AnimalType.LAC_COW,
        body_weight=600.0,
        nutrients=NutritionSupply(
            metabolizable_energy=50.0,
            maintenance_energy=10.0,
            lactation_energy=15.0,
            growth_energy=20.0,
            metabolizable_protein=5.0,
            calcium=0.5,
            phosphorus=0.3,
            dry_matter=50.0,
            wet_matter=50.0,
            ndf_supply=40.0,
            forage_ndf_supply=30.0,
            fat_supply=5.0,
            crude_protein=10.0,
            adf_supply=20.0,
            digestible_energy_supply=45.0,
            tdn_supply=60.0,
            lignin_supply=5.0,
            ash_supply=5.0,
            potassium_supply=0.5,
            starch_supply=5.0,
            byproduct_supply=5.0,
        ),
        days_in_milk=150,
        metabolizable_energy_intake=25.0,
        phosphorus_intake=0.4,
        phosphorus_requirement=0.3,
        phosphorus_reserves=0.2,
        phosphorus_endogenous_loss=0.1,
        daily_milk_produced=30.0,
        fat_content=3.5,
        protein_content=16.0,
    )
    mocker.patch.object(type(mock_inputs.animal_type), "is_cow", new_callable=PropertyMock, return_value=False)

    mock_add_error = mocker.patch.object(OutputManager, "add_error")

    with pytest.raises(
        RuntimeError, match="Unexpected execution path in process_digestion. Animal type: AnimalType.LAC_COW"
    ):
        digestive_system.process_digestion(mock_inputs)

    mock_add_error.assert_called_once()


@pytest.mark.parametrize(
    "body_weight, phosphorus_intake, phosphorus_requirement, phosphorus_reserves, phosphorus_endogenous_loss,"
    "expected_fecal_phosphorus, expected_urine_phosphorus_required",
    [
        # Case 1: phosphorus_reserves == 0 and phosphorus_intake >= phosphorus_requirement
        (500.0, 40.0, 30.0, 0.0, 5.0, 1.0, 10.0),
        # Case 2: phosphorus_reserves < 0 and conditions met for the middle branch
        (600.0, 50.0, 30.0, -7.0, 4.0, 1.2, 50.0 - 30.0 + 4.0 + (-7.0 / 0.7)),
        # Case 3: Default to endogenous loss due to unmet condition
        (700.0, 25.0, 30.0, -10.0, 6.0, 1.4, 6.0),
        # Edge case: phosphorus_intake equals phosphorus_requirement, and reserves = 0
        (400.0, 30.0, 30.0, 0.0, 3.0, 0.8, 0.0),
        # Edge case: phosphorus_intake < phosphorus_requirement
        (450.0, 20.0, 30.0, 0.0, 2.0, 0.9, 2.0),
    ],
)
def test_calculate_base_manure(
    body_weight: float,
    phosphorus_intake: float,
    phosphorus_requirement: float,
    phosphorus_reserves: float,
    phosphorus_endogenous_loss: float,
    expected_fecal_phosphorus: float,
    expected_urine_phosphorus_required: float,
) -> None:
    digestive_system = DigestiveSystem()
    actual_urine_phosphorus_required, actual_fecal_phosphorus = digestive_system._calculate_base_manure(
        body_weight, phosphorus_intake, phosphorus_requirement, phosphorus_reserves, phosphorus_endogenous_loss
    )

    assert actual_urine_phosphorus_required == pytest.approx(expected_urine_phosphorus_required)
    assert actual_fecal_phosphorus == pytest.approx(expected_fecal_phosphorus)
