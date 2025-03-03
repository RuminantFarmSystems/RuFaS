import pytest
from RUFAS.biophysical.manure.processor import Processor


def test_processor_init_error() -> None:
    """Test that base Processor class throws appropriate error when initialized."""
    with pytest.raises(TypeError):
        Processor(name="test processor", is_housing_emissions_calculator=True)


# TODO: test with a grandchild of Processor in #2102, #2103, #2104, or #2105
def test_check_manure_stream_compatibility() -> None:
    """Tests that ManureStreams are correctly checked for compatibility."""
    pass
