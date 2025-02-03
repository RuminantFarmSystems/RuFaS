import pytest

from RUFAS.biophysical.manure.processor import Processor


def test_processor_init_error() -> None:
    """Test that base Processor class throws appropriate error when initialized."""
    with pytest.raises(TypeError):
        Processor()
