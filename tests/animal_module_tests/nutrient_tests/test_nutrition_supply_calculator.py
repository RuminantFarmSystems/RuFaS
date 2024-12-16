import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal.nutrients.nutrition_supply_calculator import FeedInRation, NutritionSupplyCalculator
from RUFAS.data_structures.feed_storage_animal_connection import Feed, RUFAS_ID, Type


@pytest.fixture
def feeds(mocker: MockerFixture) -> tuple[Feed, Feed, Feed]:
    """Mock feeds to be used for testing."""
    mocker.patch.object(Feed, "__init__", return_value=None)
    feed_1, feed_2, feed_3 = Feed(), Feed(), Feed()
    feed_1.rufas_id, feed_2.rufas_id, feed_3.rufas_id = 1, 2, 3
    return [feed_1, feed_2, feed_3]


@pytest.mark.parametrize(
    "amounts, feed_types, is_fat, ee, actual_metabolizable, actual_digestable, expected",
    [
        (
            (30.0, 31.0, 20.0),
            (Type.MINERAL, Type.FORAGE, Type.CONC),
            (True, True, False),
            (1.1, 1.8, 2.0),
            {3: 90.0},
            {2: 110.0},
            3989.6,
        ),
        (
            (20.0, 11.0, 40.0),
            (Type.MINERAL, Type.FORAGE, Type.CONC),
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
    feed_types: tuple[Type, Type, Type],
    is_fat: tuple[bool, bool, bool],
    ee: tuple[float, float, float],
    actual_metabolizable: dict[RUFAS_ID, float],
    actual_digestable: dict[RUFAS_ID, float],
    expected: float,
) -> None:
    """Tests that actual net energy needed for lactation is calculated correctly."""
    feeds[0].feed_type, feeds[1].feed_type, feeds[2].feed_type = feed_types
    feeds[0].is_fat, feeds[1].is_fat, feeds[2].is_fat = is_fat
    feeds[0].EE, feeds[1].EE, feeds[2].EE = ee
    feeds_in_ration = [
        FeedInRation(amounts[0], feeds[0]),
        FeedInRation(amounts[1], feeds[1]),
        FeedInRation(amounts[2], feeds[2]),
    ]

    actual = NutritionSupplyCalculator._calculate_actual_lactation_net_energy(
        feeds_in_ration, actual_metabolizable, actual_digestable
    )

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize(
    "amounts, feed_types, is_fat, actual_metabolizable_energy, expected",
    [
        (
            (30.0, 31.0, 20.0),
            (Type.MINERAL, Type.FORAGE, Type.CONC),
            (True, True, False),
            {1: 100.0, 2: 120.0, 3: 90.0},
            154257.0,
        ),
        (
            (20.0, 11.0, 40.0),
            (Type.MINERAL, Type.FORAGE, Type.CONC),
            (True, False, False),
            {1: 60.0, 2: 110.0, 3: 130.0},
            1118990.85,
        ),
    ],
)
def test_calculate_actual_growth_net_energy(
    feeds: tuple[Feed, Feed, Feed],
    amounts: tuple[float, float, float],
    feed_types: tuple[Type, Type, Type],
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
        ((30.0, 33.0, 20.0), (Type.FORAGE, Type.CONC, Type.FORAGE), (0.9, 1.1, 0.22), 0.000312),
        ((20.0, 23.0, 15.0), (Type.CONC, Type.MINERAL, Type.VITAMINS), (1.2, 0.95, 0.5), 0.000351575),
    ],
)
def test_calculate_calcium_supply(
    feeds: tuple[Feed, Feed, Feed],
    amounts: tuple[float, float, float],
    feed_types: tuple[Type, Type, Type],
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
        ((30.0, 33.0, 20.0), (Type.FORAGE, Type.CONC, Type.FORAGE), (0.9, 1.1, 0.22), 0.00045506),
        ((20.0, 23.0, 15.0), (Type.CONC, Type.MINERAL, Type.VITAMINS), (1.2, 0.95, 0.5), 0.0003428),
    ],
)
def test_calculate_phosphorus_supply(
    feeds: tuple[Feed, Feed, Feed],
    amounts: tuple[float, float, float],
    feed_types: tuple[Type, Type, Type],
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
) -> float:
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
    "ndf, dry_matter_intake, weight, concentrates, feed_type, is_wet, expected",
    [
        ((1.3, 2.0, 0.5), 30.0, 500.0, 1.0, Type.CONC, False, {1: 11.134, 2: 11.134, 3: 11.134}),
        ((2.3, 1.8, 3.5), 35.0, 600.0, 1.1, Type.FORAGE, False, {1: 6.1093667, 2: 6.1178667, 3: 6.0889667}),
        ((1.0, 1.0, 1.0), 50.0, 600.0, 0.5, Type.MINERAL, True, {1: 8.170667, 2: 8.170667, 3: 8.170667}),
        ((1.0, 1.0, 1.0), 50.0, 600.0, 0.5, Type.MINERAL, False, {1: 0.0, 2: 0.0, 3: 0.0}),
    ],
)
def test_calculate_protein_passage_rates(
    feeds: tuple[Feed, Feed, Feed],
    ndf: tuple[float, float, float],
    dry_matter_intake: float,
    weight: float,
    concentrates: float,
    feed_type: Type,
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
            (10.0, 9.0, 12.0),
            (21.0, 40.0, 50.0),
            (30.0, 60.0, 20.0),
            {1: 3.0, 2: 4.5, 3: 1.2},
            {1: 1.846154, 2: 5.200000, 3: 3.272727},
        )
    ],
)
def test_calculated_rdp_percentages(
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
def test_calculate_rup_percentages(
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


@pytest.mark.parametrize("ndf, feed_amounts, expected", [((1.3, 2.0, 0.5), (20.0, 5.0, 10.0), 0.41)])
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

    actual = NutritionSupplyCalculator._calculate_neutral_detergent_fiber_content(feeds_in_ration)

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

    actual = NutritionSupplyCalculator._calculate_fat_content(feeds_in_ration)

    assert pytest.approx(actual) == expected
