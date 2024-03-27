import pytest
from pytest_mock import MockerFixture
from RUFAS.routines.feed_storage.sileage import Sileage, Bunker, Pile, Bag
from RUFAS.routines.feed_storage.enums import CropCategory, CropType
from RUFAS.routines.feed_storage.harvested_crop import HarvestedCrop
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.time import Time
from RUFAS.output_manager import OutputManager
from .sample_crop_data import sample_crop_data

om = OutputManager()


@pytest.fixture
def sileage() -> Sileage:
    return Sileage()


@pytest.fixture
def harvested_crop() -> HarvestedCrop:
    """
    Pytest fixture to create a HarvestedCrop instance for testing.

    Returns
    -------
    HarvestedCrop
        An instance of the HarvestedCrop class.
    """
    category = CropCategory.SMALL_GRAIN
    crop_type = CropType.WHEAT
    return HarvestedCrop(category=category, type=crop_type, **sample_crop_data)  # type: ignore[arg-type]


def test_acceptable_crops(sileage: Sileage) -> None:
    assert sileage.acceptable_crops == [
        CropCategory.ALFALFA,
        CropCategory.CORN,
        CropCategory.GRASS,
        CropCategory.SMALL_GRAIN,
    ]


@pytest.mark.parametrize(
    "effluent,loss,loss_coeff,percentage,expected_loss",
    [
        (30.0, 20.0, 0.03, 5.0, 40.0),
        (25.0, 15.0, 0.2, 6.0, 30.0),
        (0.0, 0.0, 0.0, 0.0, 0.0),
    ],
)
def test_process_degradations(
    sileage: Sileage,
    mocker: MockerFixture,
    effluent: float,
    loss: float,
    loss_coeff: float,
    percentage: float,
    expected_loss: float,
) -> None:
    """Tests process_degradations in the Sileage class."""
    expected_info_map = {
        "class": sileage.__class__.__name__,
        "function": sileage.process_degradations.__name__,
        "units": "kg",
    }
    mock_conditions = mocker.MagicMock(autospec=CurrentDayConditions)
    mock_time = mocker.MagicMock(autospec=Time)
    mock_first_crop = mocker.MagicMock(autospec=HarvestedCrop)
    mock_second_crop = mocker.MagicMock(autospec=HarvestedCrop)
    sileage.stored = [mock_first_crop, mock_second_crop]
    mock_estimate_effluent = mocker.patch.object(sileage, "estimate_maximum_effluent", return_value=effluent)
    mock_dry_matter_loss = mocker.patch.object(sileage, "calculate_dry_matter_loss_to_effluent", return_value=loss)
    mock_protein_loss = mocker.patch.object(sileage, "calculate_protein_loss_coefficient", return_value=percentage)
    mock_npn_loss = mocker.patch.object(
        sileage, "calculate_non_protein_nitrogen_loss_coefficient", return_value=loss_coeff
    )
    mock_calc_nutrient_percentage = mocker.patch.object(sileage, "recalculate_nutrient_percentage")
    mock_set_mass = mocker.patch.object(sileage, "set_mass_attributes_after_loss")
    mock_add_var = mocker.patch.object(om, "add_variable")
    mock_storage_process_degradations = mocker.patch("RUFAS.routines.feed_storage.storage.Storage.process_degradations")

    sileage.process_degradations(mock_conditions, mock_time)

    expected_estimate_calls = [mocker.call(mock_first_crop), mocker.call(mock_second_crop)]
    expected_dry_matter_loss_calls = [
        mocker.call(mock_first_crop, effluent, mock_time),
        mocker.call(mock_second_crop, effluent, mock_time),
    ]
    expected_protein_loss_calls = [mocker.call(mock_first_crop, loss), mocker.call(mock_second_crop, loss)]
    expected_npn_loss_calls = [mocker.call(mock_first_crop, loss), mocker.call(mock_second_crop, loss)]
    expected_calc_nutrient_percentage_call_count = len(sileage.stored) * 2
    expected_set_mass_calls = [mocker.call(mock_first_crop, loss), mocker.call(mock_second_crop, loss)]

    mock_estimate_effluent.assert_has_calls(expected_estimate_calls)
    mock_dry_matter_loss.assert_has_calls(expected_dry_matter_loss_calls)
    mock_protein_loss.assert_has_calls(expected_protein_loss_calls)
    mock_npn_loss.assert_has_calls(expected_npn_loss_calls)
    assert mock_calc_nutrient_percentage.call_count == expected_calc_nutrient_percentage_call_count
    mock_set_mass.assert_has_calls(expected_set_mass_calls)
    mock_add_var.assert_called_once_with("effluent_dry_matter_loss", expected_loss, expected_info_map)
    mock_storage_process_degradations.assert_called_once_with(mock_conditions, mock_time)
    mock_first_crop.crude_protein_percent = percentage
    mock_first_crop.non_protein_nitrogen = percentage
    mock_second_crop.crude_protein_percent = percentage
    mock_second_crop.non_protein_nitrogen = percentage


@pytest.mark.parametrize(
    "dry_matter,mass,expected",
    [
        (31, 100.0, 0.0),
        (30, 100.0, 0.0),
        (25, 200.0, 10.0),
        (1, 150.0, 43.5),
        (0, 250.0, 75.0),
    ],
)
def test_estimate_maximum_effluent(
    sileage: Sileage,
    harvested_crop: HarvestedCrop,
    mocker: MockerFixture,
    dry_matter: float,
    mass: float,
    expected: float,
) -> None:
    """
    Test the estimate_maximum_effluent method of the Sileage class.
    """
    harvested_crop.stored_fresh_mass = mass
    harvested_crop.stored_dry_matter_percentage = dry_matter
    actual = sileage.estimate_maximum_effluent(harvested_crop)

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize(
    "dry_matter,max_effluent,days,expected",
    [
        (100.0, 25.0, 8, 0.0207),
        (350.0, 40.0, 2, 0.002365714),
        (30.0, 55.0, 12, 0.0),
        (400.0, 12.0, 1, 0.0003105),
        (100.0, 0.0, 4, 0.0),
    ],
)
def test_calculate_dry_matter_loss_to_effluent(
    sileage: Sileage,
    mocker: MockerFixture,
    harvested_crop: HarvestedCrop,
    dry_matter: float,
    max_effluent: float,
    days: int,
    expected: float,
) -> None:
    """
    Test the calculate_dry_matter_loss_to_effluent method of the Sileage class.
    """
    mock_time = mocker.MagicMock(autospec=Time)
    mock_dry_matter_mass = mocker.patch(
        "RUFAS.routines.feed_storage.harvested_crop.HarvestedCrop.dry_matter_mass",
        new_callable=mocker.PropertyMock,
        return_value=dry_matter,
    )
    mock_days_stored = mocker.patch.object(harvested_crop, "days_stored", return_value=days)
    actual = sileage.calculate_dry_matter_loss_to_effluent(harvested_crop, max_effluent, mock_time)

    assert pytest.approx(actual) == expected
    mock_dry_matter_mass.assert_called_once()
    mock_days_stored.assert_called_once_with(mock_time)


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
def test_calculate_protein_loss_coefficient(
    sileage: Sileage, harvested_crop: HarvestedCrop, protein: float, effluent: float, expected: float
) -> None:
    """Test the calculate_protein_loss_coefficient method in the Storage class."""
    harvested_crop.crude_protein_percent = protein
    actual = sileage.calculate_protein_loss_coefficient(harvested_crop, effluent)

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
def test_calculate_non_protein_nitrogen_loss_coefficient(
    sileage: Sileage, harvested_crop: HarvestedCrop, nitrogen: float, protein: float, effluent: float, expected: float
) -> None:
    """Test the calculate_non_protein_nitrogen_loss_coefficient method in the Storage class."""
    harvested_crop.crude_protein_percent = protein
    harvested_crop.non_protein_nitrogen = nitrogen
    actual = sileage.calculate_non_protein_nitrogen_loss_coefficient(harvested_crop, effluent)

    assert pytest.approx(actual) == expected


@pytest.fixture
def bunker() -> Bunker:
    return Bunker()


def test_bunker_initialization(bunker: Bunker) -> None:
    pass


def test_calculate_protein_loss_in_bunker(bunker: Bunker) -> None:
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


def test_calculate_protein_loss_in_pile(pile: Pile) -> None:
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


def test_calculate_protein_loss_in_bag(bag: Bag) -> None:
    pass


def test_calculate_dry_matter_loss_to_gas_in_bag(bag: Bag) -> None:
    pass


def test_calculate_dry_matter_loss_to_effluent_in_bag(bag: Bag) -> None:
    pass
