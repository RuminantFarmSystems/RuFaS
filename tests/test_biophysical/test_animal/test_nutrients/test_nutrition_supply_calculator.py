import sys
from typing import Any

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal.data_types.nutrition_data_structures import NutritionSupply
from RUFAS.biophysical.animal.nutrients.nutrition_supply_calculator import FeedInRation, NutritionSupplyCalculator
from RUFAS.data_structures.feed_storage_to_animal_connection import (
    RUFAS_ID,
    Feed,
    FeedCategorization,
    FeedComponentType,
    NutrientStandard,
)
from RUFAS.units import MeasurementUnits


@pytest.fixture
def feeds(mocker: MockerFixture) -> tuple[Feed, Feed, Feed]:
    """Mock feeds used for testing."""
    feed_1, feed_2, feed_3 = mocker.Mock(spec=Feed), mocker.Mock(spec=Feed), mocker.Mock(spec=Feed)
    feed_1.rufas_id, feed_2.rufas_id, feed_3.rufas_id = 1, 2, 3
    feed_1.feed_type = FeedComponentType.FORAGE
    feed_2.feed_type = FeedComponentType.CONC
    feed_3.feed_type = FeedComponentType.FORAGE
    return (feed_1, feed_2, feed_3)


@pytest.fixture
def mock_feeds() -> list[Feed]:
    """Provides a set of mock feeds with all required attributes."""
    feed1 = Feed(
        rufas_id=1,
        feed_type=FeedComponentType.FORAGE,
        is_fat=False,
        DM=90.0,
        CP=10.0,
        EE=2.5,
        NDF=60.0,
        ADF=30.0,
        lignin=5.0,
        ash=10.0,
        calcium=1.0,
        phosphorus=1.0,
        potassium=0.5,
        starch=10.0,
        TDN=50.0,
        Fd_Category=FeedCategorization.ANIMAL_PROTEIN,
        N_A=1.0,
        N_B=2.0,
        N_C=3.0,
        Kd=0.1,
        dRUP=0.2,
        ADICP=0.3,
        NDICP=0.4,
        magnesium=0.1,
        sodium=0.2,
        chlorine=0.3,
        sulfur=0.1,
        is_wetforage=False,
        units=MeasurementUnits.KILOGRAMS,
        limit=sys.maxsize,
        lower_limit=0.0,
        DE=15.0,
        amount_available=100.0,
        on_farm_cost=0.2,
        purchase_cost=0.3,
        buffer=0.0,
    )

    feed2 = Feed(
        rufas_id=2,
        feed_type=FeedComponentType.CONC,
        is_fat=False,
        DM=85.0,
        CP=15.0,
        EE=4.0,
        NDF=70.0,
        ADF=40.0,
        lignin=10.0,
        ash=15.0,
        calcium=1.5,
        phosphorus=1.5,
        potassium=1.0,
        starch=20.0,
        TDN=40.0,
        Fd_Category=FeedCategorization.GRASS_LEGUME_FORAGE,
        N_A=1.1,
        N_B=2.1,
        N_C=3.1,
        Kd=0.15,
        dRUP=0.25,
        ADICP=0.35,
        NDICP=0.45,
        magnesium=0.15,
        sodium=0.25,
        chlorine=0.35,
        sulfur=0.15,
        is_wetforage=False,
        units=MeasurementUnits.KILOGRAMS,
        limit=sys.maxsize,
        lower_limit=0.0,
        DE=18.0,
        amount_available=200.0,
        on_farm_cost=0.25,
        purchase_cost=0.35,
        buffer=0.0,
    )

    feed3 = Feed(
        rufas_id=3,
        feed_type=FeedComponentType.MINERAL,
        is_fat=False,
        DM=80.0,
        CP=20.0,
        EE=15.0,
        NDF=80.0,
        ADF=50.0,
        lignin=15.0,
        ash=20.0,
        calcium=2.0,
        phosphorus=2.0,
        potassium=1.5,
        starch=30.0,
        TDN=60.0,
        Fd_Category=FeedCategorization.VITAMIN_MINERAL,
        N_A=1.2,
        N_B=2.2,
        N_C=3.2,
        Kd=0.2,
        dRUP=0.3,
        ADICP=0.4,
        NDICP=0.5,
        magnesium=0.2,
        sodium=0.3,
        chlorine=0.4,
        sulfur=0.2,
        is_wetforage=False,
        units=MeasurementUnits.KILOGRAMS,
        limit=sys.maxsize,
        lower_limit=0.0,
        DE=25.0,
        amount_available=300.0,
        on_farm_cost=0.3,
        purchase_cost=0.4,
        buffer=0.0,
    )

    return [feed1, feed2, feed3]


@pytest.mark.parametrize(
    "ration_formulation, body_weight, expected_supply",
    [
        (
            {1: 20.0, 2: 30.0, 3: 4.0},
            550.0,
            NutritionSupply(
                metabolizable_energy=7300.0,
                maintenance_energy=1000.0,
                lactation_energy=1100.0,
                growth_energy=1200.0,
                metabolizable_protein=1.7,
                calcium=1.5,
                phosphorus=1.6,
                dry_matter=54.0,
                wet_matter=62.5163,
                ndf_supply=10.0,
                forage_ndf_supply=12.0,
                fat_supply=11.0,
                crude_protein=1.5,
                adf_supply=1.0,
                digestible_energy_supply=28.0,
                tdn_supply=6.0,
                lignin_supply=0.5,
                ash_supply=0.3,
                potassium_supply=0.2,
                starch_supply=2.0,
                byproduct_supply=1.0,
            ),
        ),
    ],
)
def test_calculate_nutrient_supply(
    mock_feeds: list[Feed],
    mocker: MockerFixture,
    ration_formulation: dict[int, float],
    body_weight: float,
    expected_supply: NutritionSupply,
) -> None:
    """Test that the nutritive and energy content of a ration is calculated correctly."""

    mocker.patch.object(NutritionSupplyCalculator, "_calculate_nutrient_intake_discount", return_value=0.3)
    mocker.patch.object(
        NutritionSupplyCalculator, "_calculate_actual_metabolizable_energy", return_value={1: 100.0, 2: 150.0, 3: 200.0}
    )
    mocker.patch.object(NutritionSupplyCalculator, "_calculate_actual_maintenance_net_energy", return_value=1000.0)
    mocker.patch.object(NutritionSupplyCalculator, "_calculate_actual_lactation_net_energy", return_value=1100.0)
    mocker.patch.object(NutritionSupplyCalculator, "_calculate_actual_growth_net_energy", return_value=1200.0)
    mocker.patch.object(NutritionSupplyCalculator, "_calculate_calcium_supply", return_value=1.5)
    mocker.patch.object(NutritionSupplyCalculator, "_calculate_phosphorus_supply", return_value=1.6)
    mocker.patch.object(NutritionSupplyCalculator, "_calculate_metabolizable_protein_supply", return_value=1.7)
    mocker.patch.object(
        NutritionSupplyCalculator, "_calculate_forage_neutral_detergent_fiber_content", return_value=12.0
    )
    mocker.patch.object(NutritionSupplyCalculator, "_calculate_digestible_energy", return_value=28.0)
    mocker.patch.object(NutritionSupplyCalculator, "_calculate_byproducts_supply", return_value=1.0)

    def mock_nutritive_content(_: Any, nutrient: str) -> float:
        values = {
            "NDF": 10.0,
            "EE": 11.0,
            "CP": 1.5,
            "ADF": 1.0,
            "TDN": 6.0,
            "lignin": 0.5,
            "ash": 0.3,
            "potassium": 0.2,
            "starch": 2.0,
        }
        return values.get(nutrient, 0.0)

    nutritive_mock = mocker.patch.object(
        NutritionSupplyCalculator, "_calculate_nutritive_content", side_effect=mock_nutritive_content
    )

    actual_supply = NutritionSupplyCalculator.calculate_nutrient_supply(mock_feeds, ration_formulation, body_weight)

    assert actual_supply.metabolizable_energy == expected_supply.metabolizable_energy
    assert actual_supply.maintenance_energy == expected_supply.maintenance_energy
    assert actual_supply.lactation_energy == expected_supply.lactation_energy
    assert actual_supply.growth_energy == expected_supply.growth_energy
    assert actual_supply.metabolizable_protein == expected_supply.metabolizable_protein
    assert actual_supply.calcium == expected_supply.calcium
    assert actual_supply.phosphorus == expected_supply.phosphorus
    assert actual_supply.dry_matter == expected_supply.dry_matter
    assert actual_supply.ndf_supply == expected_supply.ndf_supply
    assert actual_supply.forage_ndf_supply == expected_supply.forage_ndf_supply
    assert actual_supply.fat_supply == expected_supply.fat_supply
    assert actual_supply.crude_protein == expected_supply.crude_protein
    assert actual_supply.adf_supply == expected_supply.adf_supply
    assert actual_supply.digestible_energy_supply == expected_supply.digestible_energy_supply
    assert actual_supply.tdn_supply == expected_supply.tdn_supply
    assert actual_supply.lignin_supply == expected_supply.lignin_supply
    assert actual_supply.ash_supply == expected_supply.ash_supply
    assert actual_supply.potassium_supply == expected_supply.potassium_supply
    assert actual_supply.starch_supply == expected_supply.starch_supply
    assert actual_supply.byproduct_supply == expected_supply.byproduct_supply
    assert actual_supply.nitrogen_supply == expected_supply.nitrogen_supply
    assert actual_supply.wet_matter == pytest.approx(expected_supply.wet_matter, rel=1e-5)

    nutritive_mock.assert_called()


@pytest.mark.parametrize(
    "amounts, tdn, weight, expected",
    [
        ((40.0, 10.0, 0.5), (30.0, 55.0, 77.0), 515.0, 1.0),
        ((30.0, 20.0, 10.0), (90.0, 88.0, 60.0), 600.0, 0.6),
        ((1.0, 1.0, 1.0), (61.0, 61.0, 61.0), 700.0, 1.0),
    ],
)
def test_calculate_nutrient_intake_discount(
    feeds: tuple[Feed, Feed, Feed],
    amounts: tuple[float, float, float],
    tdn: tuple[float, float, float],
    weight: float,
    expected: float,
) -> None:
    """Test that discount for Total Digestable Nutrients (TDN) and Digestible Energy (DE) are calculated correctly."""
    feeds[0].TDN, feeds[1].TDN, feeds[2].TDN = tdn
    feeds_in_ration = [
        FeedInRation(amounts[0], feeds[0]),
        FeedInRation(amounts[1], feeds[1]),
        FeedInRation(amounts[2], feeds[2]),
    ]

    actual = NutritionSupplyCalculator._calculate_nutrient_intake_discount(feeds_in_ration, weight)

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize(
    "amounts, feed_types, is_fat, de, ee, actual_digestible, expected",
    [
        (
            (30.0, 31.0, 20.0),
            (FeedComponentType.MINERAL, FeedComponentType.FORAGE, FeedComponentType.CONC),
            (True, True, False),
            (100.0, 115.0, 130.0),
            (1.1, 1.8, 2.0),
            {3: 90.0},
            {1: 0.0, 2: 115.0, 3: 90.45},
        ),
        (
            (20.0, 11.0, 40.0),
            (FeedComponentType.MINERAL, FeedComponentType.FORAGE, FeedComponentType.CONC),
            (True, False, False),
            (90.0, 99.0, 108.0),
            (1.1, 1.8, 3.5),
            {2: 110.0, 3: 130.0},
            {1: 0.0, 2: 110.65, 3: 130.8523},
        ),
    ],
)
def test_calculate_actual_metabolizable_energy(
    feeds: tuple[Feed, Feed, Feed],
    amounts: tuple[float, float, float],
    feed_types: tuple[FeedComponentType, FeedComponentType, FeedComponentType],
    is_fat: tuple[bool, bool, bool],
    de: tuple[float, float, float],
    ee: tuple[float, float, float],
    actual_digestible: dict[RUFAS_ID, float],
    expected: dict[RUFAS_ID, float],
) -> None:
    """Test that actual net energy needed for lactation is calculated correctly."""
    feeds[0].feed_type, feeds[1].feed_type, feeds[2].feed_type = feed_types
    feeds[0].is_fat, feeds[1].is_fat, feeds[2].is_fat = is_fat
    feeds[0].DE, feeds[1].DE, feeds[2].DE = de
    feeds[0].EE, feeds[1].EE, feeds[2].EE = ee
    feeds_in_ration = [
        FeedInRation(amounts[0], feeds[0]),
        FeedInRation(amounts[1], feeds[1]),
        FeedInRation(amounts[2], feeds[2]),
    ]

    actual = NutritionSupplyCalculator._calculate_actual_metabolizable_energy(feeds_in_ration, actual_digestible)

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize(
    "amounts, is_fat, actual_metabolizable, expected",
    [
        (
            (30.0, 31.0, 20.0),
            (True, True, False),
            {1: 99.0, 2: 95.0, 3: 100.0},
            189849.6,
        ),
        (
            (20.0, 11.0, 40.0),
            (True, False, False),
            {1: 109.0, 2: 82.0, 3: 103.0},
            462426.652,
        ),
    ],
)
def test_calculate_actual_maintenance_net_energy(
    feeds: tuple[Feed, Feed, Feed],
    amounts: tuple[float, float, float],
    is_fat: tuple[bool, bool, bool],
    actual_metabolizable: dict[RUFAS_ID, float],
    expected: float,
) -> None:
    """Test that actual net energy needed for lactation is calculated correctly."""
    feeds[0].is_fat, feeds[1].is_fat, feeds[2].is_fat = is_fat
    feeds_in_ration = [
        FeedInRation(amounts[0], feeds[0]),
        FeedInRation(amounts[1], feeds[1]),
        FeedInRation(amounts[2], feeds[2]),
    ]

    actual = NutritionSupplyCalculator._calculate_actual_maintenance_net_energy(feeds_in_ration, actual_metabolizable)

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize(
    "amounts, feed_types, is_fat, ee, actual_metabolizable, actual_digestible, expected",
    [
        (
            (30.0, 31.0, 20.0),
            (FeedComponentType.MINERAL, FeedComponentType.FORAGE, FeedComponentType.CONC),
            (True, True, False),
            (1.1, 1.8, 2.0),
            {3: 90.0},
            {2: 110.0},
            3989.6,
        ),
        (
            (20.0, 11.0, 40.0),
            (FeedComponentType.MINERAL, FeedComponentType.FORAGE, FeedComponentType.CONC),
            (True, False, False),
            (1.1, 1.8, 3.5),
            {2: 110.0, 3: 130.0},
            {},
            4499.179,
        ),
    ],
)
def test_calculate_actual_lactation_net_energy(
    feeds: tuple[Feed, Feed, Feed],
    amounts: tuple[float, float, float],
    feed_types: tuple[FeedComponentType, FeedComponentType, FeedComponentType],
    is_fat: tuple[bool, bool, bool],
    ee: tuple[float, float, float],
    actual_metabolizable: dict[RUFAS_ID, float],
    actual_digestible: dict[RUFAS_ID, float],
    expected: float,
) -> None:
    """Test that actual net energy needed for lactation is calculated correctly."""
    feeds[0].feed_type, feeds[1].feed_type, feeds[2].feed_type = feed_types
    feeds[0].is_fat, feeds[1].is_fat, feeds[2].is_fat = is_fat
    feeds[0].EE, feeds[1].EE, feeds[2].EE = ee
    feeds_in_ration = [
        FeedInRation(amounts[0], feeds[0]),
        FeedInRation(amounts[1], feeds[1]),
        FeedInRation(amounts[2], feeds[2]),
    ]

    actual = NutritionSupplyCalculator._calculate_actual_lactation_net_energy(
        feeds_in_ration, actual_metabolizable, actual_digestible
    )

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize(
    "amounts, feed_types, is_fat, actual_metabolizable_energy, expected",
    [
        (
            (30.0, 31.0, 20.0),
            (FeedComponentType.MINERAL, FeedComponentType.FORAGE, FeedComponentType.CONC),
            (True, True, False),
            {1: 100.0, 2: 120.0, 3: 90.0},
            154257.0,
        ),
        (
            (20.0, 11.0, 40.0),
            (FeedComponentType.MINERAL, FeedComponentType.FORAGE, FeedComponentType.CONC),
            (True, False, False),
            {1: 60.0, 2: 110.0, 3: 130.0},
            1118990.85,
        ),
    ],
)
def test_calculate_actual_growth_net_energy(
    feeds: tuple[Feed, Feed, Feed],
    amounts: tuple[float, float, float],
    feed_types: tuple[FeedComponentType, FeedComponentType, FeedComponentType],
    is_fat: tuple[bool, bool, bool],
    actual_metabolizable_energy: dict[RUFAS_ID, float],
    expected: float,
) -> None:
    """Test that actual net energy for growth is calculated correctly."""
    feeds[0].feed_type, feeds[1].feed_type, feeds[2].feed_type = feed_types
    feeds[0].is_fat, feeds[1].is_fat, feeds[2].is_fat = is_fat
    feeds_in_ration = [
        FeedInRation(amounts[0], feeds[0]),
        FeedInRation(amounts[1], feeds[1]),
        FeedInRation(amounts[2], feeds[2]),
    ]

    actual = NutritionSupplyCalculator._calculate_actual_growth_net_energy(feeds_in_ration, actual_metabolizable_energy)

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize(
    "amounts, feed_types, ca, expected",
    [
        (
            (30.0, 33.0, 20.0),
            (FeedComponentType.FORAGE, FeedComponentType.CONC, FeedComponentType.FORAGE),
            (0.9, 1.1, 0.22),
            312.0,
        ),
        (
            (20.0, 23.0, 15.0),
            (FeedComponentType.CONC, FeedComponentType.MINERAL, FeedComponentType.VITAMINS),
            (1.2, 0.95, 0.5),
            351.575,
        ),
        (
            (20.0, 20.0, 20.0),
            (FeedComponentType.MINERAL, FeedComponentType.MINERAL, FeedComponentType.MINERAL),
            (100.0, 100.0, 100.0),
            57000.0,
        ),
    ],
)
def test_calculate_calcium_supply(
    feeds: tuple[Feed, Feed, Feed],
    amounts: tuple[float, float, float],
    feed_types: tuple[FeedComponentType, FeedComponentType, FeedComponentType],
    ca: tuple[float, float, float],
    expected: float,
) -> None:
    """Test that the supply of calcium in a ration is calculated correctly."""
    feeds[0].feed_type, feeds[1].feed_type, feeds[2].feed_type = feed_types[0], feed_types[1], feed_types[2]
    feeds[0].calcium, feeds[1].calcium, feeds[2].calcium = ca[0], ca[1], ca[2]
    feeds_in_ration = [
        FeedInRation(amounts[0], feeds[0]),
        FeedInRation(amounts[1], feeds[1]),
        FeedInRation(amounts[2], feeds[2]),
    ]

    actual = NutritionSupplyCalculator._calculate_calcium_supply(feeds_in_ration)

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize(
    "amounts, feed_types, phos, expected",
    [
        (
            (30.0, 33.0, 20.0),
            (FeedComponentType.FORAGE, FeedComponentType.CONC, FeedComponentType.FORAGE),
            (0.9, 1.1, 0.22),
            455.06,
        ),
        (
            (20.0, 23.0, 15.0),
            (FeedComponentType.CONC, FeedComponentType.MINERAL, FeedComponentType.VITAMINS),
            (1.2, 0.95, 0.5),
            342.8,
        ),
        (
            (20.0, 20.0, 20.0),
            (FeedComponentType.MINERAL, FeedComponentType.MINERAL, FeedComponentType.MINERAL),
            (100.0, 100.0, 100.0),
            48_000.0,
        ),
    ],
)
def test_calculate_phosphorus_supply(
    feeds: tuple[Feed, Feed, Feed],
    amounts: tuple[float, float, float],
    feed_types: tuple[FeedComponentType, FeedComponentType, FeedComponentType],
    phos: tuple[float, float, float],
    expected: float,
) -> None:
    """Test that supply of phosphorus in a ration is calculated correctly."""
    feeds[0].feed_type, feeds[1].feed_type, feeds[2].feed_type = feed_types[0], feed_types[1], feed_types[2]
    feeds[0].phosphorus, feeds[1].phosphorus, feeds[2].phosphorus = phos[0], phos[1], phos[2]
    feeds_in_ration = [
        FeedInRation(amounts[0], feeds[0]),
        FeedInRation(amounts[1], feeds[1]),
        FeedInRation(amounts[2], feeds[2]),
    ]

    actual = NutritionSupplyCalculator._calculate_phosphorus_supply(feeds_in_ration)

    assert actual == expected


@pytest.mark.parametrize(
    "dry_matter, amounts, actual_tdn, weight, drup, expected",
    [(50.0, (25.0, 24.0, 0.75), {1: 1.3, 2: 2.33, 3: 3.1}, 450.0, {1: 70.0, 2: 80.0, 3: 77.0}, 412.32484)],
)
def test_calculate_metabolizable_protein_supply(
    feeds: tuple[Feed, Feed, Feed],
    mocker: MockerFixture,
    dry_matter: float,
    amounts: tuple[float, float, float],
    actual_tdn: dict[RUFAS_ID, float],
    weight: float,
    drup: tuple[float, float, float],
    expected: float,
) -> None:
    """Test that the metabolizable protein content of a ration is calculated correctly."""
    feeds[0].dRUP, feeds[1].dRUP, feeds[2].dRUP = drup
    feeds_in_ration = [
        FeedInRation(amounts[0], feeds[0]),
        FeedInRation(amounts[1], feeds[1]),
        FeedInRation(amounts[2], feeds[2]),
    ]
    mock_calc_conc = mocker.patch.object(
        NutritionSupplyCalculator, "_calculate_percentage_of_concentrates", return_value=1.1
    )
    mock_calc_rates = mocker.patch.object(
        NutritionSupplyCalculator, "_calculate_protein_passage_rates", return_value={1: 4.0, 2: 5.0, 3: 4.5}
    )
    mock_calc_rdp = mocker.patch.object(
        NutritionSupplyCalculator,
        "_calculate_rumen_degradable_protein_percentages",
        return_value={1: 1.8, 2: 1.6, 3: 2.1},
    )
    mock_calc_rup = mocker.patch.object(
        NutritionSupplyCalculator,
        "_calculate_rumen_undegradable_protein_percentages",
        return_value={1: 10.0, 2: 15.0, 3: 17.0},
    )

    actual = NutritionSupplyCalculator._calculate_metabolizable_protein_supply(
        feeds_in_ration, dry_matter, actual_tdn, weight
    )

    assert pytest.approx(actual) == expected
    mock_calc_conc.assert_called_once_with(feeds_in_ration, dry_matter)
    mock_calc_rates.assert_called_once_with(feeds_in_ration, dry_matter, weight, 1.1)
    mock_calc_rdp.assert_called_once_with(feeds_in_ration, {1: 4.0, 2: 5.0, 3: 4.5})
    mock_calc_rup.assert_called_once()


@pytest.mark.parametrize(
    "amounts, dry_matter, feed_types, expected",
    [
        (
            (20.0, 30.0, 0.5),
            50.5,
            (FeedComponentType.FORAGE, FeedComponentType.FORAGE, FeedComponentType.CONC),
            0.990099,
        ),
        (
            (10.0, 33.0, 10.0),
            53.0,
            (FeedComponentType.FORAGE, FeedComponentType.CONC, FeedComponentType.FORAGE),
            62.264151,
        ),
        (
            (20.0, 30.0, 15.0),
            65.0,
            (FeedComponentType.FORAGE, FeedComponentType.MINERAL, FeedComponentType.VITAMINS),
            0.0,
        ),
    ],
)
def test_calculate_percentage_of_concentrates(
    feeds: tuple[Feed, Feed, Feed],
    amounts: tuple[float, float, float],
    dry_matter: float,
    feed_types: tuple[FeedComponentType, FeedComponentType, FeedComponentType],
    expected: float,
) -> None:
    """Test that the percentage of a ration made up of concentrates is calculated correclty."""
    feeds[0].feed_type, feeds[1].feed_type, feeds[2].feed_type = feed_types
    feeds_in_ration = [
        FeedInRation(amounts[0], feeds[0]),
        FeedInRation(amounts[1], feeds[1]),
        FeedInRation(amounts[2], feeds[2]),
    ]

    actual = NutritionSupplyCalculator._calculate_percentage_of_concentrates(feeds_in_ration, dry_matter)

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize(
    "ndf, dry_matter_intake, weight, concentrates, feed_type, is_wet, expected",
    [
        ((1.3, 2.0, 0.5), 30.0, 500.0, 1.0, FeedComponentType.CONC, False, {1: 11.134, 2: 11.134, 3: 11.134}),
        (
            (2.3, 1.8, 3.5),
            35.0,
            600.0,
            1.1,
            FeedComponentType.FORAGE,
            False,
            {1: 6.1093667, 2: 6.1178667, 3: 6.0889667},
        ),
        ((1.0, 1.0, 1.0), 50.0, 600.0, 0.5, FeedComponentType.MINERAL, True, {1: 8.170667, 2: 8.170667, 3: 8.170667}),
        ((1.0, 1.0, 1.0), 50.0, 600.0, 0.5, FeedComponentType.MINERAL, False, {1: 0.0, 2: 0.0, 3: 0.0}),
    ],
)
def test_calculate_protein_passage_rates(
    feeds: tuple[Feed, Feed, Feed],
    ndf: tuple[float, float, float],
    dry_matter_intake: float,
    weight: float,
    concentrates: float,
    feed_type: FeedComponentType,
    is_wet: bool,
    expected: dict[RUFAS_ID, float],
) -> None:
    """Test that protein passage rates are calculated correctly."""
    feeds[0].NDF, feeds[1].NDF, feeds[2].NDF = ndf
    feeds[0].feed_type, feeds[1].feed_type, feeds[2].feed_type = feed_type, feed_type, feed_type
    feeds[0].is_wetforage, feeds[1].is_wetforage, feeds[2].is_wetforage = is_wet, is_wet, is_wet
    feeds_in_ration = [FeedInRation(1.0, feeds[0]), FeedInRation(1.0, feeds[1]), FeedInRation(1.0, feeds[2])]

    actual = NutritionSupplyCalculator._calculate_protein_passage_rates(
        feeds_in_ration, dry_matter_intake, weight, concentrates
    )

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize(
    "cp, kd, nb, na, protein_passage_rates, expected",
    [
        (
            (4.0, 6.0, 5.0),
            (10.0, 0.0, 12.0),
            (21.0, 40.0, 50.0),
            (30.0, 60.0, 20.0),
            {1: 3.0, 2: 0.0, 3: 1.2},
            {1: 1.846154, 2: 0.0, 3: 3.272727},
        )
    ],
)
def test_calculate_rumen_degradable_protein_percentages(
    feeds: tuple[Feed, Feed, Feed],
    cp: tuple[float, float, float],
    kd: tuple[float, float, float],
    nb: tuple[float, float, float],
    na: tuple[float, float, float],
    protein_passage_rates: dict[RUFAS_ID, float],
    expected: dict[RUFAS_ID, float],
) -> None:
    """Test that Rumen Degradable Protein percentages are calculated correctly."""
    feeds[0].CP, feeds[1].CP, feeds[2].CP = cp
    feeds[0].Kd, feeds[1].Kd, feeds[2].Kd = kd
    feeds[0].N_B, feeds[1].N_B, feeds[2].N_B = nb
    feeds[0].N_A, feeds[1].N_A, feeds[2].N_A = na
    feeds_in_ration = [FeedInRation(1.0, feeds[0]), FeedInRation(1.0, feeds[1]), FeedInRation(1.0, feeds[2])]

    actual = NutritionSupplyCalculator._calculate_rumen_degradable_protein_percentages(
        feeds_in_ration, protein_passage_rates
    )

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize(
    "cp, rdp_percentages, expected",
    [
        ((15.0, 20.0, 4.0), {1: 3.0, 2: 4.0, 3: 0.5}, {1: 12.0, 2: 16.0, 3: 3.5}),
        ((20.0, 3.0, 12.0), {1: 15.0, 2: 3.0, 3: 5.0}, {1: 5.0, 2: 0.0, 3: 7.0}),
    ],
)
def test_calculate_rumen_undegradable_protein_percentages(
    feeds: tuple[Feed, Feed, Feed],
    cp: tuple[float, float, float],
    rdp_percentages: dict[RUFAS_ID, float],
    expected: dict[RUFAS_ID, float],
) -> None:
    """Test that Rumen Undegradable Protein percentages are calculated correctly."""
    feeds[0].CP, feeds[1].CP, feeds[2].CP = cp
    feeds_in_ration = [FeedInRation(1.0, feeds[0]), FeedInRation(1.0, feeds[1]), FeedInRation(1.0, feeds[2])]

    actual = NutritionSupplyCalculator._calculate_rumen_undegradable_protein_percentages(
        feeds_in_ration, rdp_percentages
    )

    assert actual == expected


@pytest.mark.parametrize("ndf, feed_amounts, expected", [((1.3, 2.0, 0.5), (20.0, 5.0, 10.0), 0.31)])
def test_calculate_ndf_content(
    feeds: tuple[Feed, Feed, Feed],
    ndf: tuple[float, float, float],
    feed_amounts: tuple[float, float, float],
    expected: float,
) -> None:
    """Test that Neutral Detergent Fiber of a ration is calculated correctly."""
    feeds[0].NDF, feeds[1].NDF, feeds[2].NDF = ndf
    feeds_in_ration = [
        FeedInRation(feed_amounts[0], feeds[0]),
        FeedInRation(feed_amounts[1], feeds[1]),
        FeedInRation(feed_amounts[2], feeds[2]),
    ]

    actual = NutritionSupplyCalculator._calculate_forage_neutral_detergent_fiber_content(feeds_in_ration)

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize(
    "ndf, feed_types, feed_amounts, expected",
    [
        (
            (1.3, 2.0, 0.5),
            (FeedComponentType.FORAGE, FeedComponentType.FORAGE, FeedComponentType.FORAGE),
            (20.0, 5.0, 10.0),
            0.41,
        ),
        (
            (1.3, 2.0, 0.5),
            (FeedComponentType.FORAGE, FeedComponentType.CONC, FeedComponentType.FORAGE),
            (20.0, 5.0, 10.0),
            0.31,
        ),
        (
            (1.3, 2.0, 0.5),
            (FeedComponentType.CONC, FeedComponentType.CONC, FeedComponentType.CONC),
            (20.0, 5.0, 10.0),
            0.0,
        ),
    ],
)
def test_calculate_forage_neutral_detergent_fiber_content(
    feeds: tuple[Feed, Feed, Feed],
    ndf: tuple[float, float, float],
    feed_types: tuple[FeedComponentType, FeedComponentType, FeedComponentType],
    feed_amounts: tuple[float, float, float],
    expected: float,
) -> None:
    """Test that Neutral Detergent Fiber supplied by forages in a ration is calculated correctly."""
    feeds[0].NDF, feeds[1].NDF, feeds[2].NDF = ndf
    feeds[0].feed_type, feeds[1].feed_type, feeds[2].feed_type = feed_types
    feeds_in_ration = [
        FeedInRation(feed_amounts[0], feeds[0]),
        FeedInRation(feed_amounts[1], feeds[1]),
        FeedInRation(feed_amounts[2], feeds[2]),
    ]

    actual = NutritionSupplyCalculator._calculate_forage_neutral_detergent_fiber_content(feeds_in_ration)

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize(
    "ee, feed_amounts, expected",
    [
        ((2.1, 1.0, 0.0), (10.0, 20.0, 0.5), 0.41),
        ((0.0, 0.0, 0.0), (20.0, 20.0, 20.0), 0.0),
        ((3.0, 3.0, 3.0), (10.0, 20.0, 15.0), 1.35),
    ],
)
def test_calculate_fat_content(
    feeds: tuple[Feed, Feed, Feed],
    ee: tuple[float, float, float],
    feed_amounts: tuple[float, float, float],
    expected: float,
) -> None:
    """Test that fat content of a ration is calculated correctly."""
    feeds[0].EE, feeds[1].EE, feeds[2].EE = ee
    feeds_in_ration = [
        FeedInRation(feed_amounts[0], feeds[0]),
        FeedInRation(feed_amounts[1], feeds[1]),
        FeedInRation(feed_amounts[2], feeds[2]),
    ]

    actual = NutritionSupplyCalculator._calculate_nutritive_content(feeds_in_ration, "EE")

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize(
    "de_values, feed_amounts, nutrient_standard, expected",
    [
        ((1.2, 2.5, 3.0), (10.0, 20.0, 5.0), NutrientStandard.NRC, 77.0),
        ((1.0, 2.0, 3.5), (15.0, 10.0, 8.0), NutrientStandard.NASEM, 63.0),
        ((0.0, 0.0, 0.0), (20.0, 20.0, 20.0), NutrientStandard.NRC, 0.0),
        ((1.5, 0.5, 2.0), (12.0, 8.0, 15.0), NutrientStandard.NRC, 52.0),
    ],
)
def test_calculate_digestible_energy(
    feeds: tuple[Feed, Feed, Feed],
    de_values: tuple[float, float, float],
    feed_amounts: tuple[float, float, float],
    nutrient_standard: NutrientStandard,
    expected: float,
) -> None:
    """Test that digestible energy of a ration is calculated correctly."""
    setattr(NutritionSupplyCalculator, "nutrient_standard", nutrient_standard)
    de_attribute = "DE_Base" if nutrient_standard is NutrientStandard.NASEM else "DE"
    setattr(feeds[0], de_attribute, de_values[0])
    setattr(feeds[1], de_attribute, de_values[1])
    setattr(feeds[2], de_attribute, de_values[2])

    feeds_in_ration = [
        FeedInRation(feed_amounts[0], feeds[0]),
        FeedInRation(feed_amounts[1], feeds[1]),
        FeedInRation(feed_amounts[2], feeds[2]),
    ]

    actual = NutritionSupplyCalculator._calculate_digestible_energy(feeds_in_ration)

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize(
    "fd_categories, feed_amounts, expected",
    [
        # Case 1: All feeds are categorized as byproducts
        (
            (
                FeedCategorization.BY_PRODUCT_OTHER,
                FeedCategorization.BY_PRODUCT_OTHER,
                FeedCategorization.BY_PRODUCT_OTHER,
            ),
            (10.0, 5.0, 15.0),
            30.0,
        ),
        # Case 2: No feeds are byproducts (various other categories)
        (
            (
                FeedCategorization.ENERGY_SOURCE,
                FeedCategorization.GRASS_LEGUME_FORAGE,
                FeedCategorization.VITAMIN_MINERAL,
            ),
            (10.0, 5.0, 15.0),
            0.0,
        ),
        # Case 3: Some feeds are byproducts, others are not
        (
            (
                FeedCategorization.BY_PRODUCT_OTHER,
                FeedCategorization.GRAIN_CROP_FORAGE,
                FeedCategorization.BY_PRODUCT_OTHER,
            ),
            (8.0, 12.0, 10.0),
            18.0,
        ),
        # Case 4: No feed amounts (edge case)
        (
            (
                FeedCategorization.BY_PRODUCT_OTHER,
                FeedCategorization.BY_PRODUCT_OTHER,
                FeedCategorization.BY_PRODUCT_OTHER,
            ),
            (0.0, 0.0, 0.0),
            0.0,
        ),
        # Case 5: Only one byproduct feed
        (
            (FeedCategorization.ANIMAL_PROTEIN, FeedCategorization.BY_PRODUCT_OTHER, FeedCategorization.PLANT_PROTEIN),
            (20.0, 15.0, 10.0),
            15.0,
        ),
        # Case 6: Edge case with unusual categories (ensuring robustness)
        (
            (FeedCategorization.FATTY_ACID_SUPPLEMENT, FeedCategorization.PASTURE, FeedCategorization.FAT_SUPPLEMENT),
            (5.0, 10.0, 8.0),
            0.0,
        ),
    ],
)
def test_calculate_byproducts_supply(
    feeds: tuple[Feed, Feed, Feed],
    fd_categories: tuple[FeedCategorization, FeedCategorization, FeedCategorization],
    feed_amounts: tuple[float, float, float],
    expected: float,
) -> None:
    """Test that byproduct supply is calculated correctly using the full FeedCategorization enum."""
    feeds[0].Fd_Category = fd_categories[0]
    feeds[1].Fd_Category = fd_categories[1]
    feeds[2].Fd_Category = fd_categories[2]
    feeds_in_ration = [
        FeedInRation(feed_amounts[0], feeds[0]),
        FeedInRation(feed_amounts[1], feeds[1]),
        FeedInRation(feed_amounts[2], feeds[2]),
    ]

    actual = NutritionSupplyCalculator._calculate_byproducts_supply(feeds_in_ration)

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize(
    "nutrient, nutrient_values, feed_amounts, expected",
    [
        # Case 1: Crude Protein (CP) calculation
        ("CP", (18.0, 14.0, 22.0), (10.0, 5.0, 15.0), 5.8),
        # Case 2: Ether Extract (EE) calculation
        ("EE", (5.0, 10.0, 2.0), (10.0, 20.0, 15.0), 2.8),
        # Case 3: Neutral Detergent Fiber (NDF) calculation
        ("NDF", (45.0, 55.0, 30.0), (12.0, 8.0, 20.0), 15.8),
        # Case 4: No feed amounts (Edge case)
        ("ADF", (30.0, 40.0, 35.0), (0.0, 0.0, 0.0), 0.0),
        # Case 5: Nutrient not present in one feed
        ("starch", (10.0, 0.0, 25.0), (10.0, 5.0, 15.0), 4.75),
    ],
)
def test_calculate_nutritive_content(
    feeds: tuple[Feed, Feed, Feed],
    nutrient: str,
    nutrient_values: tuple[float, float, float],
    feed_amounts: tuple[float, float, float],
    expected: float,
) -> None:
    """Test that nutritive content of a ration is calculated correctly for various nutrients."""
    setattr(feeds[0], nutrient, nutrient_values[0])
    setattr(feeds[1], nutrient, nutrient_values[1])
    setattr(feeds[2], nutrient, nutrient_values[2])

    feeds_in_ration = [
        FeedInRation(feed_amounts[0], feeds[0]),
        FeedInRation(feed_amounts[1], feeds[1]),
        FeedInRation(feed_amounts[2], feeds[2]),
    ]

    actual = NutritionSupplyCalculator._calculate_nutritive_content(feeds_in_ration, nutrient)

    assert pytest.approx(actual, rel=1e-5) == expected
