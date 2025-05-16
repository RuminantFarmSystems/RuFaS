import pytest
from RUFAS.biophysical.manure.digester.digester import Digester


def test_processor_init_error() -> None:
    """Test that base Digester class throws appropriate error when initialized."""
    with pytest.raises(TypeError):
        Digester(name="test digester", is_housing_emissions_calculator=False)  # type: ignore[abstract]
