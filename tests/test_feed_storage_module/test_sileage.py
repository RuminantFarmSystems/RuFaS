import pytest
from RUFAS.routines.feed_storage.sileage import Sileage, Bunker, Pile, Bag
from RUFAS.routines.feed_storage.enums import CropCategory


@pytest.fixture
def sileage() -> Sileage:
    return Sileage()


def test_acceptable_crops(sileage: Sileage) -> None:
    assert sileage.acceptable_crops == [
        CropCategory.ALFALFA,
        CropCategory.CORN,
        CropCategory.GRASS,
        CropCategory.SMALL_GRAIN,
    ]


@pytest.mark.parametrize(
    "dry_matter,percentage,category,temp,expected",
    [
        (100.0, 25.0, CropCategory.ALFALFA, 20.0, 1.378),
        (40.0, 20.0, CropCategory.ALFALFA, 6.0, 0.624),
        (150.0, 19.0, CropCategory.ALFALFA, 10.0, 0.0),
        (200.0, 23.0, CropCategory.ALFALFA, 46.0, 0.0),
        (140.0, 15.0, CropCategory.CORN, 30.0, 1.2096),
        (55.0, 66.0, CropCategory.GRASS, 25.0, 0.0),
        (120.0, 4.0, CropCategory.SMALL_GRAIN, 15.0, 0.0),
    ],
)
def test_calculate_dry_matter_loss_to_gas(
    sileage: Sileage, dry_matter: float, percentage: float, category: CropCategory, temp: float, expected: float
) -> None:
    """Tests calculate_dry_matter_loss_to_gas in Sileage."""
    actual = sileage.calculate_dry_matter_loss_to_gas(dry_matter, percentage, category, temp)

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize(
    "protein,effluent,expected",
    [
        (10.0, 0.05, 10.51052),
        (8.0, 0.3, 11.3),
        (2.0, 0.11, 2.210112),
        (3.0, 1.0, 3.0),
        (0.0, 0.13, 0.0),
        (5.0, 0.0, 0.0),
    ],
)
def test_calculate_crude_protein_loss_to_effluent(
    sileage: Sileage, protein: float, effluent: float, expected: float
) -> None:
    """Test the calculate_protein_loss_to_effluent method in the Storage class."""
    actual = sileage.calculate_protein_loss_to_effluent(protein, effluent)

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize(
    "nitrogen,protein,effluent,expected",
    [
        (3.2, 10.0, 0.3, 3.2199798),
        (2.3, 1.0, 0.1, 2.3402061),
        (2.3, 0.0, 0.1, 1.0),
        (1.3, 3.4, 1.0, 1.3),
        (0.0, 2.1, 0.11, 0.0),
        (2.3, 1.2, 0.0, 0.0),
    ],
)
def test_calculate_non_protein_nitrogen_loss_to_effluent(
    sileage: Sileage, nitrogen: float, protein: float, effluent: float, expected: float
) -> None:
    """Test the calculate_non_protein_nitrogen_loss_to_effluent method in the Storage class."""
    actual = sileage.calculate_non_protein_loss_to_effluent(nitrogen, protein, effluent)

    assert pytest.approx(actual) == expected


@pytest.fixture
def bunker() -> Bunker:
    return Bunker()


def test_bunker_initialization(bunker: Bunker) -> None:
    pass


def test_calculate_dry_matter_loss_to_gas_in_bunker(bunker: Bunker) -> None:
    pass


def test_calculate_dry_matter_loss_to_effluent_in_bunker(bunker: Bunker) -> None:
    pass


@pytest.fixture
def pile() -> Pile:
    return Pile()


def test_pile_initialization(pile: Pile) -> None:
    pass


def test_calculate_dry_matter_loss_to_gas_in_pile(pile: Pile) -> None:
    pass


def test_calculate_dry_matter_loss_to_effluent_in_pile(pile: Pile) -> None:
    pass


@pytest.fixture
def bag() -> Bag:
    return Bag()


def test_bag_initialization(bag: Bag) -> None:
    pass


def test_calculate_dry_matter_loss_to_gas_in_bag(bag: Bag) -> None:
    pass


def test_calculate_dry_matter_loss_to_effluent_in_bag(bag: Bag) -> None:
    pass
