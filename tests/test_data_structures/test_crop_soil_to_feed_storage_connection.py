import copy
from datetime import date, datetime, timedelta
from typing import cast

import pytest
from pytest_mock import MockerFixture

from RUFAS.data_structures.crop_soil_to_feed_storage_connection import HarvestedCrop

from RUFAS.general_constants import GeneralConstants
from RUFAS.rufas_time import RufasTime
from tests.test_biophysical.test_feed_storage.sample_crop_data import sample_crop_data


def test_attributes(mocker: MockerFixture) -> None:
    """Tests that HarvestedCrop's are initialized correctly."""
    mock_effluent = mocker.patch.object(HarvestedCrop, "estimate_maximum_effluent", return_value=10.0)
    mock_bale_density = mocker.patch.object(HarvestedCrop, "_calculate_bale_density", return_value=200.0)
    mock_heat_generated = mocker.patch.object(
        HarvestedCrop, "_calculate_total_sensible_heat_generated", return_value=900.0
    )
    crop = HarvestedCrop(**sample_crop_data)
    assert crop.dry_matter_mass == sample_crop_data["dry_matter_mass"]
    assert crop.dry_matter_percentage == sample_crop_data["dry_matter_percentage"]
    assert crop.initial_dry_matter_percentage == sample_crop_data["dry_matter_percentage"]
    assert crop.initial_dry_matter_mass == 100.0
    assert crop.dry_matter_digestibility == sample_crop_data["dry_matter_digestibility"]
    assert crop.crude_protein_percent == sample_crop_data["crude_protein_percent"]
    assert crop.non_protein_nitrogen == sample_crop_data["non_protein_nitrogen"]
    assert crop.starch == sample_crop_data["starch"]
    assert crop.adf == sample_crop_data["adf"]
    assert crop.ndf == sample_crop_data["ndf"]
    assert crop.lignin == sample_crop_data["lignin"]
    assert crop.sugar == sample_crop_data["sugar"]
    assert crop.ash == sample_crop_data["ash"]
    assert crop.estimated_maximum_effluent == 10.0
    assert crop.bale_density == 200.0
    assert crop.total_sensible_heat_generated == 900.0

    mock_effluent.assert_called_once()
    mock_bale_density.assert_called_once()
    mock_heat_generated.assert_called_once()


def test_harvest_and_storage_time_with_rufas_time(mocker: MockerFixture) -> None:
    """Test that RufasTime objects passed into HarvestedCrop are converted to dates."""
    mock_datetime = datetime(2025, 6, 7)
    mocker.patch.object(HarvestedCrop, "fresh_mass", new_callable=mocker.PropertyMock, return_value=100.0)
    mocker.patch.object(HarvestedCrop, "estimate_maximum_effluent", return_value=10.0)
    mocker.patch.object(HarvestedCrop, "_calculate_bale_density", return_value=200.0)
    mocker.patch.object(HarvestedCrop, "_calculate_total_sensible_heat_generated", return_value=900.0)

    rufas_time = RufasTime(
        start_date=mock_datetime,
        end_date=mock_datetime + timedelta(days=10),
        current_date=mock_datetime,
    )

    crop = HarvestedCrop(
        config_name="test_crop",
        field_name="test_field",
        harvest_time=cast(date, rufas_time),
        storage_time=cast(date, rufas_time),
        dry_matter_mass=100.0,
        dry_matter_percentage=50.0,
        dry_matter_digestibility=70.0,
        crude_protein_percent=10.0,
        non_protein_nitrogen=5.0,
        starch=30.0,
        adf=7.0,
        ndf=15.0,
        lignin=3.0,
        sugar=20.0,
        ash=6.0,
    )

    assert crop.harvest_time == mock_datetime.date()
    assert crop.storage_time == mock_datetime.date()


@pytest.mark.parametrize(
    "initial_fresh_mass, initial_dry_matter_mass, mass_to_remove, expected_fresh_mass, expected_dmp",
    [
        # Normal case: partial removal
        (100.0, 40.0, 10.0, 90.0, (30.0 / 90.0) * GeneralConstants.FRACTION_TO_PERCENTAGE),
        # Edge case: full removal
        (50.0, 20.0, 40.0, 0.0, 0.0),
    ],
)
def test_remove_dry_matter_mass(
    initial_fresh_mass: float,
    initial_dry_matter_mass: float,
    mass_to_remove: float,
    expected_fresh_mass: float,
    expected_dmp: float,
) -> None:
    """Test the removal of dry matter mass and corresponding updates to the crop."""
    crop = HarvestedCrop(
        config_name="test_crop",
        field_name="test_field",
        harvest_time=date(2025, 6, 1),
        storage_time=date(2025, 6, 2),
        dry_matter_mass=initial_dry_matter_mass,
        dry_matter_percentage=(initial_dry_matter_mass / initial_fresh_mass) * 100,
        dry_matter_digestibility=70.0,
        crude_protein_percent=10.0,
        non_protein_nitrogen=5.0,
        starch=30.0,
        adf=7.0,
        ndf=15.0,
        lignin=3.0,
        sugar=20.0,
        ash=6.0,
    )

    crop.remove_dry_matter_mass(mass_to_remove)

    assert crop.fresh_mass == expected_fresh_mass
    assert crop.dry_matter_percentage == pytest.approx(expected_dmp, abs=1e-6)


@pytest.mark.parametrize(
    "initial_fresh_mass, initial_dry_matter_mass, mass_to_remove, expected_fresh_mass",
    [
        (100.0, 40.0, 25.0, 37.5),  # Normal removal
        (50.0, 20.0, 0.0, 50.0),  # Zero removal
        (30.0, 12.0, 12.0, 0.0),  # Remove all fresh mass
    ],
)
def test_remove_feed_mass_valid(
    initial_fresh_mass,
    initial_dry_matter_mass: float,
    mass_to_remove: float,
    expected_fresh_mass: float,
) -> None:
    crop = HarvestedCrop(
        config_name="test_crop",
        field_name="test_field",
        harvest_time=date(2025, 6, 1),
        storage_time=date(2025, 6, 2),
        dry_matter_mass=initial_dry_matter_mass,
        dry_matter_percentage=(initial_dry_matter_mass / initial_fresh_mass) * 100,
        dry_matter_digestibility=70.0,
        crude_protein_percent=10.0,
        non_protein_nitrogen=5.0,
        starch=30.0,
        adf=7.0,
        ndf=15.0,
        lignin=3.0,
        sugar=20.0,
        ash=6.0,
    )
    crop.remove_feed_mass(mass_to_remove)
    assert crop.fresh_mass == expected_fresh_mass


@pytest.mark.parametrize(
    "initial_fresh_mass, initial_dry_matter_mass, dm_to_remove",
    [
        (50.0, 20.0, 25.0),  # request 25 kg DM, but only 20 kg DM available → error
    ],
)
def test_remove_feed_mass_invalid(
    initial_fresh_mass: float,
    initial_dry_matter_mass: float,
    dm_to_remove: float,
) -> None:
    crop = HarvestedCrop(
        config_name="test_crop",
        field_name="test_field",
        harvest_time=date(2025, 6, 1),
        storage_time=date(2025, 6, 2),
        dry_matter_mass=20,
        dry_matter_percentage=(initial_dry_matter_mass / initial_fresh_mass) * 100,
        dry_matter_digestibility=70.0,
        crude_protein_percent=10.0,
        non_protein_nitrogen=5.0,
        starch=30.0,
        adf=7.0,
        ndf=15.0,
        lignin=3.0,
        sugar=20.0,
        ash=6.0,
    )

    with pytest.raises(ValueError, match=r"Cannot remove"):
        crop.remove_feed_mass(dm_to_remove)


@pytest.mark.parametrize(
    "mass,percentage,expected",
    [
        (25.0, 25.0, 100),
        (230.0, 22.0, 1045.4545454545455),
        (145.0, 100.0, 145.0),
        (20.4, 0.0, 0.0),
        (0.0, 0.0, 0.0),
    ],
)
def test_fresh_mass(mass: float, percentage: float, expected: float) -> None:
    """Test dry_matter_mass property in Harvested Crop."""
    crop_data = copy.deepcopy(sample_crop_data)
    crop_data["dry_matter_mass"] = mass
    crop_data["dry_matter_percentage"] = percentage
    crop = HarvestedCrop(**crop_data)

    actual = crop.fresh_mass

    assert actual == expected


@pytest.mark.parametrize("dry_matter,mass,expected", ((30.0, 100.0, 0.0), (15.0, 200.0, 200.0), (35.0, 150.0, 0.0)))
def test_estimate_maximum_effluent(dry_matter: float, mass: float, expected: float) -> None:
    """Tests _estimate_maximum_effluent in HarvestedCrop."""
    crop = HarvestedCrop(**sample_crop_data)
    crop.dry_matter_percentage = dry_matter
    crop.dry_matter_mass = mass

    actual = crop.estimate_maximum_effluent()

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize("dry_matter_percentage,expected", [(30.0, 408.0), (15.0, 474.0), (95.0, 122.0)])
def test_calculate_bale_density(dry_matter_percentage: float, expected: float) -> None:
    """Tests _calculate_bale_density in HarvestedCrop."""
    crop = HarvestedCrop(**sample_crop_data)
    crop.dry_matter_percentage = dry_matter_percentage

    actual = crop._calculate_bale_density()

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize(
    "dry_matter_percentage,density,expected",
    [(30.0, 200.0, 1212.69585225), (50.0, 330.0, 985.1530725), (90.0, 150.0, 45.8198056)],
)
def test_calculate_total_sensible_heat_generated(dry_matter_percentage: float, density: float, expected: float) -> None:
    """Tests _calculate_total_sensible_heat_generated in HarvestedCrop."""
    crop = HarvestedCrop(**sample_crop_data)
    crop.dry_matter_percentage = dry_matter_percentage
    crop.bale_density = density

    actual = crop._calculate_total_sensible_heat_generated()

    assert pytest.approx(actual) == expected
