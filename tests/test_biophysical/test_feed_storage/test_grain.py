import pytest

from RUFAS.biophysical.feed_storage.grain import Grain


@pytest.fixture
def grain() -> Grain:
    """
    Pytest fixture to create a Grain instance for testing.

    Returns
    -------
    Grain
        An instance of the Grain class.
    """
    mock_grain_config: dict[str, str | float | list[str]] = {
        "name": "corn_grain",
        "rufas_id": 1,
        "field_name": "field_1",
        "crop_name": "corn",
        "initial_storage_dry_matter": 45.0,
        "post_wilting_moisture_percentage": 40.0,
        "bale_density": 200.0,
        "capacity": 1_000_000.0,
    }
    return Grain(config=mock_grain_config)
