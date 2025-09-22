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
    return Grain()
