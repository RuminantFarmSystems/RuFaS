import pytest
from RUFAS.routines.feed_storage.sileage import Sileage, Bunker, Pile, Bag
from RUFAS.routines.feed_storage.enums import CropCategory


@pytest.fixture
def sileage() -> Sileage:
    return Sileage()


def test_acceptable_crops(sileage: Sileage):
    assert sileage.acceptable_crops == [
        CropCategory.ALFALFA,
        CropCategory.CORN,
        CropCategory.GRASS,
        CropCategory.SMALL_GRAIN,
    ]


def test_calculate_protein_loss(sileage: Sileage):
    pass


def test_calculate_dry_matter_loss_to_gas(sileage: Sileage):
    pass


def test_calculate_dry_matter_loss_to_effluent(sileage: Sileage):
    pass


@pytest.fixture
def bunker() -> Bunker:
    return Bunker()


def test_bunker_initialization(bunker: Bunker):
    pass


def test_calculate_protein_loss_in_bunker(bunker: Bunker):
    pass


def test_calculate_dry_matter_loss_to_gas_in_bunker(bunker: Bunker):
    pass


def test_calculate_dry_matter_loss_to_effluent_in_bunker(bunker: Bunker):
    pass


@pytest.fixture
def pile() -> Pile:
    return Pile()


def test_pile_initialization(pile: Pile):
    pass


def test_calculate_protein_loss_in_pile(pile: Pile):
    pass


def test_calculate_dry_matter_loss_to_gas_in_pile(pile: Pile):
    pass


def test_calculate_dry_matter_loss_to_effluent_in_pile(pile: Pile):
    pass


@pytest.fixture
def bag() -> Bag:
    return Bag()


def test_bag_initialization(bag: Bag):
    pass


def test_calculate_protein_loss_in_bag(bag: Bag):
    pass


def test_calculate_dry_matter_loss_to_gas_in_bag(bag: Bag):
    pass


def test_calculate_dry_matter_loss_to_effluent_in_bag(bag: Bag):
    pass
