import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal.digestive_system.manure_excretion_calculator import ManureExcretionCalculator
from RUFAS.data_structures.animal_manure_excretions import AnimalManureExcretions


@pytest.mark.parametrize(
    "body_weight,fecal_phosphorus,urine_phosphorus_required,nutrient_amounts,nutrient_concentrations,"
    "inorganic_phosphorus_fraction,total_phosphorus_excreted,organic_phosphorus_fraction,manure_phosphorus_excreted,"
    "manure_phosphorus_fraction",
    [(500000, 36.5, 22.8, {"dm": 24.3}, {"CP": 92.4}, 26.3, 56.2, 58.3, 77.7, 0.35)],
)
def test_calf_manure(
    body_weight: float,
    fecal_phosphorus: float,
    urine_phosphorus_required: float,
    nutrient_amounts: dict[str, float],
    nutrient_concentrations: dict[str, float],
    inorganic_phosphorus_fraction: float,
    total_phosphorus_excreted: float,
    organic_phosphorus_fraction: float,
    manure_phosphorus_excreted: float,
    manure_phosphorus_fraction: float,
    mocker: MockerFixture,
) -> None:
    """Tests that calf manure excretion is correctly calculated."""
    mock_phosphorus_excretion = mocker.patch.object(
        ManureExcretionCalculator,
        "_calculate_phosphorus_excretion_values",
        return_value=(
            total_phosphorus_excreted,
            inorganic_phosphorus_fraction,
            organic_phosphorus_fraction,
            manure_phosphorus_excreted,
            manure_phosphorus_fraction,
        ),
    )

    expected = (
        56.2,
        AnimalManureExcretions(
            urea=9.52,
            urine=2.0,
            manure_total_ammoniacal_nitrogen=1.137198447,
            urine_nitrogen=1.137198447,
            manure_nitrogen=2.52710766,
            manure_mass=83.83500000000001,
            total_solids=9.549900000000001,
            degradable_volatile_solids=1035.0,
            non_degradable_volatile_solids=115.0,
            inorganic_phosphorus_fraction=26.3,
            organic_phosphorus_fraction=58.3,
            non_water_inorganic_phosphorus_fraction=0.0,
            non_water_organic_phosphorus_fraction=0.0,
            phosphorus=77.7,
            phosphorus_fraction=0.35,
            potassium=0,
        ),
    )

    actual = ManureExcretionCalculator.calculate_calf_manure(
        body_weight, fecal_phosphorus, urine_phosphorus_required, nutrient_amounts, nutrient_concentrations
    )

    mock_phosphorus_excretion.assert_called_once_with(
        daily_milk_production=0,
        total_manure_excreted=83.83500000000001,
        fecal_phosphorus=fecal_phosphorus,
        urine_phosphorus_required=urine_phosphorus_required,
    )

    assert actual == expected


@pytest.mark.parametrize(
    "body_weight,fecal_phosphorus,urine_phosphorus_required,nutrient_amounts,nutrient_concentrations,"
    "inorganic_phosphorus_fraction,total_phosphorus_excreted,organic_phosphorus_fraction,manure_phosphorus_excreted,"
    "manure_phosphorus_fraction",
    [(500000, 36.5, 22.8, {"dm": 24.3}, {"CP": 92.4, "potassium": 23.6}, 26.3, 56.2, 58.3, 77.7, 0.35)],
)
def test_heifer_manure(
    body_weight: float,
    fecal_phosphorus: float,
    urine_phosphorus_required: float,
    nutrient_amounts: dict[str, float],
    nutrient_concentrations: dict[str, float],
    inorganic_phosphorus_fraction: float,
    total_phosphorus_excreted: float,
    organic_phosphorus_fraction: float,
    manure_phosphorus_excreted: float,
    manure_phosphorus_fraction: float,
    mocker: MockerFixture,
) -> None:
    """Tests manure excretion values for a growing heifer is calculated correctly."""
    mock_phosphorus_excretion = mocker.patch.object(
        ManureExcretionCalculator,
        "_calculate_phosphorus_excretion_values",
        return_value=(
            total_phosphorus_excreted,
            inorganic_phosphorus_fraction,
            organic_phosphorus_fraction,
            manure_phosphorus_excreted,
            manure_phosphorus_fraction,
        ),
    )

    expected = (
        total_phosphorus_excreted,
        AnimalManureExcretions(
            urea=176.35486046222226,
            urine=9.0,
            manure_total_ammoniacal_nitrogen=1.8577136560000003,
            urine_nitrogen=1.8577136560000003,
            manure_nitrogen=2.9968849600000005,
            manure_mass=-12198.9606,
            total_solids=7.058400000000001,
            degradable_volatile_solids=3285.0,
            non_degradable_volatile_solids=365.0,
            inorganic_phosphorus_fraction=26.3,
            organic_phosphorus_fraction=58.3,
            non_water_inorganic_phosphorus_fraction=0.0,
            non_water_organic_phosphorus_fraction=0.0,
            phosphorus=77.7,
            phosphorus_fraction=0.35,
            potassium=5734.800000000001,
        ),
    )
    actual = ManureExcretionCalculator.calculate_heifer_manure(
        body_weight, fecal_phosphorus, urine_phosphorus_required, nutrient_amounts, nutrient_concentrations
    )

    mock_phosphorus_excretion.assert_called_once_with(
        daily_milk_production=0,
        total_manure_excreted=-12198.9606,
        fecal_phosphorus=fecal_phosphorus,
        urine_phosphorus_required=urine_phosphorus_required,
    )

    assert actual == expected


@pytest.mark.parametrize(
    "days_in_milk,milk_protein,daily_milk_production,fecal_phosphorus,urine_phosphorus_required,"
    "nutrient_amounts,nutrient_concentrations,inorganic_phosphorus_fraction,total_phosphorus_excreted,"
    "organic_phosphorus_fraction,manure_phosphorus_excreted,manure_phosphorus_fraction",
    [
        (
            707,
            36.5,
            22.8,
            32.5,
            22.9,
            {"dm": 24.3, "ash": 69.4},
            {"CP": 92.4, "potassium": 23.6, "dm": 77.7, "NDF": 84.1, "ADF": 4.2},
            26.3,
            56.2,
            58.3,
            77.7,
            0.35,
        )
    ],
)
def test_lactating_cow_manure(
    days_in_milk: int,
    milk_protein: float,
    daily_milk_production: float,
    fecal_phosphorus: float,
    urine_phosphorus_required: float,
    nutrient_amounts: dict[str, float],
    nutrient_concentrations: dict[str, float],
    inorganic_phosphorus_fraction: float,
    total_phosphorus_excreted: float,
    organic_phosphorus_fraction: float,
    manure_phosphorus_excreted: float,
    manure_phosphorus_fraction: float,
    mocker: MockerFixture,
) -> None:
    """Test the manure excretion values for a lactating cow with information from the ration formulation."""
    mock_phosphorus_excretion = mocker.patch.object(
        ManureExcretionCalculator,
        "_calculate_phosphorus_excretion_values",
        return_value=(
            total_phosphorus_excreted,
            inorganic_phosphorus_fraction,
            organic_phosphorus_fraction,
            manure_phosphorus_excreted,
            manure_phosphorus_fraction,
        ),
    )
    expected = (
        total_phosphorus_excreted,
        AnimalManureExcretions(
            urea=11.62193070833374,
            urine=144.1778,
            manure_total_ammoniacal_nitrogen=2.1428728480000006,
            urine_nitrogen=2.1428728480000006,
            manure_nitrogen=2.3698028480000004,
            manure_mass=147.8078,
            total_solids=1.7327999999999986,
            degradable_volatile_solids=-17.1197,
            non_degradable_volatile_solids=-1.4015000000000057,
            inorganic_phosphorus_fraction=26.3,
            organic_phosphorus_fraction=58.3,
            non_water_inorganic_phosphorus_fraction=0.0,
            non_water_organic_phosphorus_fraction=0.0,
            phosphorus=77.7,
            phosphorus_fraction=0.35,
            potassium=3773.487,
        ),
    )

    actual = ManureExcretionCalculator._calculate_lactating_cow_manure(
        days_in_milk,
        milk_protein,
        daily_milk_production,
        fecal_phosphorus,
        urine_phosphorus_required,
        nutrient_amounts,
        nutrient_concentrations,
    )
    assert expected == actual
    mock_phosphorus_excretion.assert_called_once_with(
        daily_milk_production=daily_milk_production,
        total_manure_excreted=147.8078,
        fecal_phosphorus=fecal_phosphorus,
        urine_phosphorus_required=urine_phosphorus_required,
    )


@pytest.mark.parametrize(
    "body_weight,days_in_milk,milk_protein,daily_milk_production,fecal_phosphorus,"
    "urine_phosphorus_required,nutrient_amounts,nutrient_concentrations",
    [(43.2, 6, 225.3, 21.4, 14.3, 92.4, {"a": 56.2}, {"b": 58.3})],
)
def test_cow_manure_lactating(
    body_weight: float,
    days_in_milk: int,
    milk_protein: float,
    daily_milk_production: float,
    fecal_phosphorus: float,
    urine_phosphorus_required: float,
    nutrient_amounts: dict[str, float],
    nutrient_concentrations: dict[str, float],
    mocker: MockerFixture,
) -> None:
    """Tests that the lactating function is being called in the cow manure excretion routine."""
    mock_lactating_cow_manure = mocker.patch.object(ManureExcretionCalculator, "_calculate_lactating_cow_manure")
    ManureExcretionCalculator.calculate_cow_manure(
        True,
        body_weight,
        days_in_milk,
        milk_protein,
        daily_milk_production,
        fecal_phosphorus,
        urine_phosphorus_required,
        nutrient_amounts,
        nutrient_concentrations,
    )
    mock_lactating_cow_manure.assert_called_once_with(
        days_in_milk,
        milk_protein,
        daily_milk_production,
        fecal_phosphorus,
        urine_phosphorus_required,
        nutrient_amounts,
        nutrient_concentrations,
    )


@pytest.mark.parametrize(
    "body_weight,days_in_milk,milk_protein,daily_milk_production,fecal_phosphorus,"
    "urine_phosphorus_required,nutrient_amounts,nutrient_concentrations",
    [(43.2, 6, 225.3, 21.4, 14.3, 92.4, {"a": 56.2}, {"b": 58.3})],
)
def test_cow_manure_dry(
    body_weight: float,
    days_in_milk: int,
    milk_protein: float,
    daily_milk_production: float,
    fecal_phosphorus: float,
    urine_phosphorus_required: float,
    nutrient_amounts: dict[str, float],
    nutrient_concentrations: dict[str, float],
    mocker: MockerFixture,
) -> None:
    """Tests that the dry cow function is being called in the cow manure excretion routine."""
    mock_dry_cow_manure = mocker.patch.object(ManureExcretionCalculator, "_calculate_dry_cow_manure")
    ManureExcretionCalculator.calculate_cow_manure(
        False,
        body_weight,
        days_in_milk,
        milk_protein,
        daily_milk_production,
        fecal_phosphorus,
        urine_phosphorus_required,
        nutrient_amounts,
        nutrient_concentrations,
    )
    mock_dry_cow_manure.assert_called_once_with(
        body_weight,
        daily_milk_production,
        fecal_phosphorus,
        urine_phosphorus_required,
        nutrient_amounts,
        nutrient_concentrations,
    )
