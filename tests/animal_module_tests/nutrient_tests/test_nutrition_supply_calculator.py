import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal.nutrients.nutrition_supply_calculator import FeedInRation, NutritionSupplyCalculator
from RUFAS.data_structures.feed_storage_animal_connection import Feed, RUFAS_ID


@pytest.fixture
def feeds(mocker: MockerFixture) -> tuple[Feed, Feed, Feed]:
    """Mock feeds to be used for testing."""
    mocker.patch.object(Feed, "__init__", return_value=None)
    feed_1, feed_2, feed_3 = Feed(), Feed(), Feed()
    feed_1.rufas_id, feed_2.rufas_id, feed_3.rufas_id = 1, 2, 3
    return [feed_1, feed_2, feed_3]


@pytest.mark.parametrize(
    "cp, kd, nb, na, protein_passage_rates, expected",
    [
        ((4.0, 6.0, 5.0), (10.0, 9.0, 12.0), (21.0, 40.0, 50.0), (30.0, 60.0, 20.0), {1: 3.0, 2: 4.5, 3: 1.2}, {1: 1.846154, 2: 5.200000, 3: 3.272727})
    ]
)
def test_calculated_rdp_percentages(feeds: tuple[Feed, Feed, Feed], cp: tuple[float, float, float], kd: tuple[float, float, float], nb: tuple[float, float, float], na: tuple[float, float, float], protein_passage_rates: dict[RUFAS_ID, float], expected: dict[RUFAS_ID, float]) -> None:
    """Test that Rumen Degradable Protein percentages are calculated correctly."""
    feeds[0].CP, feeds[1].CP, feeds[2].CP = cp
    feeds[0].Kd, feeds[1].Kd, feeds[2].Kd = kd
    feeds[0].N_B, feeds[1].N_B, feeds[2].N_B = nb
    feeds[0].N_A, feeds[1].N_A, feeds[2].N_A = na
    feeds_in_ration = [FeedInRation(1.0, feeds[0]), FeedInRation(1.0, feeds[1]), FeedInRation(1.0, feeds[2])]

    actual = NutritionSupplyCalculator._calculate_rumen_degradable_protein_percentages(feeds_in_ration, protein_passage_rates)

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize(
    "cp, rdp_percentages, expected",
    [
        ((15.0, 20.0, 4.0), {1: 3.0, 2: 4.0, 3: 0.5}, {1: 12.0, 2: 16.0, 3: 3.5}),
        ((20.0, 3.0, 12.0), {1: 15.0, 2: 3.0, 3: 5.0}, {1: 5.0, 2: 0.0, 3: 7.0}),
    ]
)
def test_calculate_rup_percentages(feeds: tuple[Feed, Feed, Feed], cp: tuple[float, float, float], rdp_percentages: dict[RUFAS_ID, float], expected: dict[RUFAS_ID, float]) -> None:
    """Test that Rumen Undegradable Protein percentages are calculated correctly."""
    feeds[0].CP, feeds[1].CP, feeds[2].CP = cp
    feeds_in_ration = [FeedInRation(1.0, feeds[0]), FeedInRation(1.0, feeds[1]), FeedInRation(1.0, feeds[2])]

    actual = NutritionSupplyCalculator._calculate_rumen_undegradable_protein_percentages(feeds_in_ration, rdp_percentages)

    assert actual == expected


@pytest.mark.parametrize(
    "ndf, feed_amounts, expected",
    [
        ((1.3, 2.0, 0.5), (20.0, 5.0, 10.0), 0.41)
    ]
)
def test_calculate_ndf_content(feeds: tuple[Feed, Feed, Feed], ndf: tuple[float, float, float], feed_amounts: tuple[float, float, float], expected: float) -> None:
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
    ]
)
def test_calculate_fat_content(feeds: tuple[Feed, Feed, Feed], ee: tuple[float, float, float], feed_amounts: tuple[float, float, float], expected: float) -> None:
    """Test that fat content of a ration is calculated correctly."""
    feeds[0].EE, feeds[1].EE, feeds[2].EE = ee
    feeds_in_ration = [
        FeedInRation(feed_amounts[0], feeds[0]),
        FeedInRation(feed_amounts[1], feeds[1]),
        FeedInRation(feed_amounts[2], feeds[2]),
    ]

    actual = NutritionSupplyCalculator._calculate_fat_content(feeds_in_ration)

    assert pytest.approx(actual) == expected
    