import pytest
from RUFAS.biophysical.manure.processor import Processor


def test_processor_init_error() -> None:
    """Test that base Processor class throws appropriate error when initialized."""
    with pytest.raises(TypeError):
        Processor(is_housing_emissions_calculator=True)


# TODO: test with a child or grandchild of Processor, either in #2098 or #2099
# def test_check_manure_stream_compatibility() -> None:
#     """Tests that ManureStreams are correctly checked for compatibility."""
#     pass
