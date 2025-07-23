import pytest
from typing import Type

from RUFAS.biophysical.manure.digester.continuous_mix import ContinuousMix
from RUFAS.biophysical.manure.handler.parlor_cleaning import ParlorCleaningHandler
from RUFAS.biophysical.manure.handler.single_stream_handler import SingleStreamHandler
from RUFAS.biophysical.manure.processor import Processor
from RUFAS.biophysical.manure.processor_enum import ProcessorType
from RUFAS.biophysical.manure.separator.separator import Separator
from RUFAS.biophysical.manure.storage.anaerobic_lagoon import AnaerobicLagoon
from RUFAS.biophysical.manure.storage.bedded_pack import BeddedPack
from RUFAS.biophysical.manure.storage.composting import Composting
from RUFAS.biophysical.manure.storage.open_lot import OpenLot
from RUFAS.biophysical.manure.storage.slurry_storage_outdoor import SlurryStorageOutdoor
from RUFAS.biophysical.manure.storage.slurry_storage_underfloor import SlurryStorageUnderfloor


@pytest.mark.parametrize(
    "input_str, expected_class",
    [
        ("RotaryScreen", Separator),
        ("ScrewPress", Separator),
        ("ContinuousMix", ContinuousMix),
        ("ParlorCleaningHandler", ParlorCleaningHandler),
        ("AlleyScraper", SingleStreamHandler),
        ("ManualScraper", SingleStreamHandler),
        ("FlushSystem", SingleStreamHandler),
        ("AnaerobicLagoon", AnaerobicLagoon),
        ("SlurryStorageOutdoor", SlurryStorageOutdoor),
        ("SlurryStorageUnderfloor", SlurryStorageUnderfloor),
        ("Composting", Composting),
        ("BeddedPack", BeddedPack),
        ("OpenLot", OpenLot),
    ],
)
def test_get_processor_class_valid(input_str: str, expected_class: Type["Processor"]) -> None:
    assert ProcessorType.get_processor_class(input_str) is expected_class


def test_get_processor_class_invalid() -> None:
    with pytest.raises(ValueError, match="Unknown processor type: invalid_processor."):
        ProcessorType.get_processor_class("invalid_processor")
