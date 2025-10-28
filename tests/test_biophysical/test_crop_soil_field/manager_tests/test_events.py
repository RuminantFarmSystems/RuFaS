from unittest.mock import MagicMock

import pytest

from RUFAS.data_structures.manure_supplement_methods import ManureSupplementMethod
from RUFAS.data_structures.tillage_implements import TillageImplement
from RUFAS.biophysical.field.crop.harvest_operations import HarvestOperation
from RUFAS.data_structures.events import (
    BaseFieldManagementEvent,
    FertilizerEvent,
    HarvestEvent,
    ManureEvent,
    PlantingEvent,
    TillageEvent,
)
from RUFAS.data_structures.manure_types import ManureType


@pytest.mark.parametrize(
    "year,day,current_year,current_day,expected",
    [
        (1, 120, 1, 120, True),
        (2, 200, 2, 201, False),
        (3, 90, 4, 90, False),
        (2, 1, 3, 144, False),
    ],
)
def test_occurs_today(year: int, day: int, current_year: int, current_day: int, expected: bool) -> None:
    """Tests that BaseFieldManagementEvent objects can correctly determine whether they run on a given day."""
    mocked_time = MagicMock()
    setattr(mocked_time, "current_calendar_year", current_year)
    setattr(mocked_time, "current_julian_day", current_day)
    event = BaseFieldManagementEvent(year, day)

    actual = event.occurs_today(mocked_time)

    assert actual == expected


@pytest.mark.parametrize(
    "event1,event2,expected",
    [
        (BaseFieldManagementEvent(1, 120), BaseFieldManagementEvent(1, 120), True),
        (BaseFieldManagementEvent(2, 120), BaseFieldManagementEvent(1, 120), False),
        (3, BaseFieldManagementEvent(1, 120), False),
    ],
)
def test_event_equality(event1, event2, expected: bool) -> None:
    """Tests that equality is tested correctly between BaseFieldManagementEvent objects."""
    actual = event1 == event2
    assert actual == expected


@pytest.mark.parametrize(
    "event,expected",
    [
        (BaseFieldManagementEvent(1, 120), hash((1, 120))),
        (BaseFieldManagementEvent(3, 15), hash((3, 15))),
        (BaseFieldManagementEvent(6, 1), hash((6, 1))),
    ],
)
def test_event_hash(event: BaseFieldManagementEvent, expected: float) -> None:
    """Tests that hash returns correctly for BaseFieldManagementEvent objects."""
    assert event.__hash__() == expected


@pytest.mark.parametrize(
    "planting_event1,planting_event2,expected",
    [
        (
            PlantingEvent(crop_reference="corn", year=1, day=20, heat_scheduled_harvest=True),
            PlantingEvent(crop_reference="corn", year=1, day=20, heat_scheduled_harvest=True),
            True,
        ),
        (
            PlantingEvent(crop_reference="corn", year=3, day=20, heat_scheduled_harvest=True),
            PlantingEvent(crop_reference="corn", year=1, day=21, heat_scheduled_harvest=True),
            False,
        ),
        (
            PlantingEvent(crop_reference="corn", year=1, day=20, heat_scheduled_harvest=True),
            PlantingEvent(crop_reference="corn", year=1, day=20, heat_scheduled_harvest=False),
            False,
        ),
        (
            PlantingEvent(crop_reference="njnj", year=1, day=20, heat_scheduled_harvest=True),
            PlantingEvent(crop_reference="corn", year=1, day=20, heat_scheduled_harvest=True),
            False,
        ),
        (
            2,
            PlantingEvent(crop_reference="corn", year=1, day=20, heat_scheduled_harvest=True),
            False,
        ),
    ],
)
def test_planting_event_equality(planting_event1, planting_event2, expected: bool) -> None:
    """Tests that equality is tested correctly between PlantingEvent objects."""
    actual = planting_event1 == planting_event2
    assert actual == expected


@pytest.mark.parametrize(
    "planting_event,expected",
    [
        (
            PlantingEvent(crop_reference="corn", year=1, day=20, heat_scheduled_harvest=True),
            hash(("corn", 1, 20, True)),
        )
    ],
)
def test_planting_event_hash(planting_event: PlantingEvent, expected: float) -> None:
    """Tests that hash returns correctly for PlantingEvent objects."""
    assert planting_event.__hash__() == expected


@pytest.mark.parametrize(
    "harvest_event1,harvest_event2,expected",
    [
        (
            HarvestEvent(crop_reference="corn", year=1, day=20),
            HarvestEvent(crop_reference="corn", year=1, day=20),
            True,
        ),
        (
            HarvestEvent(crop_reference="corn", year=3, day=20),
            HarvestEvent(crop_reference="corn", year=1, day=21),
            False,
        ),
        (
            HarvestEvent(crop_reference="corn", year=1, day=20),
            HarvestEvent(crop_reference="corn", year=1, day=20, operation="RUFAS"),
            False,
        ),
        (
            HarvestEvent(crop_reference="popcorn", year=1, day=20),
            HarvestEvent(crop_reference="corn", year=1, day=20),
            False,
        ),
        (2, HarvestEvent(crop_reference="corn", year=1, day=20), False),
    ],
)
def test_harvest_event_equality(harvest_event1, harvest_event2, expected: bool) -> None:
    """Tests that equality is tested correctly between HarvestEvent objects."""
    actual = harvest_event1 == harvest_event2
    assert actual == expected


@pytest.mark.parametrize(
    "harvest_event,expected",
    [
        (
            HarvestEvent(crop_reference="corn", year=1, day=20),
            hash((1, 20, "corn", HarvestOperation.HARVEST_KILL)),
        )
    ],
)
def test_harvest_event_hash(harvest_event: HarvestEvent, expected: float) -> None:
    """Tests that hash returns correctly for HarvestEvent objects."""
    assert harvest_event.__hash__() == expected


@pytest.mark.parametrize(
    "tillage_event1,tillage_event2,expected",
    [
        (
            TillageEvent(
                tillage_depth=9.24,
                incorporation_fraction=0.77,
                mixing_fraction=0.131,
                implement=TillageImplement.SUBSOILER,
            ),
            TillageEvent(
                tillage_depth=9.24,
                incorporation_fraction=0.77,
                mixing_fraction=0.131,
                implement=TillageImplement.SUBSOILER,
            ),
            True,
        ),
        (
            TillageEvent(
                tillage_depth=10.24,
                incorporation_fraction=0.77,
                mixing_fraction=0.131,
                implement=TillageImplement.MOLDBOARD_PLOW,
            ),
            TillageEvent(
                tillage_depth=9.24,
                incorporation_fraction=0.77,
                mixing_fraction=0.131,
                implement=TillageImplement.MOLDBOARD_PLOW,
            ),
            False,
        ),
        (
            TillageEvent(
                tillage_depth=9.24,
                incorporation_fraction=0.87,
                mixing_fraction=0.131,
                implement=TillageImplement.COULTER_CHISEL_PLOW,
            ),
            TillageEvent(
                tillage_depth=9.24,
                incorporation_fraction=0.77,
                mixing_fraction=0.131,
                implement=TillageImplement.COULTER_CHISEL_PLOW,
            ),
            False,
        ),
        (
            TillageEvent(
                tillage_depth=9.24,
                incorporation_fraction=0.87,
                mixing_fraction=0.131,
                implement=TillageImplement.DISK_HARROW,
            ),
            TillageEvent(
                tillage_depth=9.24,
                incorporation_fraction=0.77,
                mixing_fraction=0.214,
                implement=TillageImplement.DISK_HARROW,
            ),
            False,
        ),
        (
            TillageEvent(
                tillage_depth=9.24,
                incorporation_fraction=0.77,
                mixing_fraction=0.131,
                implement=TillageImplement.DISK_HARROW,
            ),
            TillageEvent(
                tillage_depth=9.24,
                incorporation_fraction=0.77,
                mixing_fraction=0.131,
                implement=TillageImplement.SEEDBED_CONDITIONER,
            ),
            False,
        ),
        (
            2,
            TillageEvent(
                tillage_depth=9.24,
                incorporation_fraction=0.77,
                mixing_fraction=0.131,
                implement=TillageImplement.CULTIVATOR,
            ),
            False,
        ),
    ],
)
def test_tillage_event_equality(tillage_event1, tillage_event2, expected: bool) -> None:
    """Tests that equality is tested correctly between TillageEvent objects."""
    actual = tillage_event1 == tillage_event2
    assert actual == expected


@pytest.mark.parametrize(
    "tillage_event,expected",
    [
        (
            TillageEvent(
                tillage_depth=9.24,
                incorporation_fraction=0.77,
                mixing_fraction=0.131,
                implement=TillageImplement.CULTIVATOR,
            ),
            hash((1, 160, 9.24, 0.77, 0.131, TillageImplement.CULTIVATOR)),
        )
    ],
)
def test_tillage_event_hash(tillage_event: TillageEvent, expected: float) -> None:
    """Tests that hash returns correctly for TillageEvent objects."""
    assert tillage_event.__hash__() == expected


@pytest.mark.parametrize(
    "manure_event1,manure_event2,expected",
    [
        (
            ManureEvent(
                year=1,
                day=65,
                nitrogen_mass=9.24,
                phosphorus_mass=7.7,
                manure_type=ManureType.LIQUID,
                manure_supplement_method=ManureSupplementMethod.NONE,
                field_coverage=1.30,
                application_depth=7.4,
                surface_remainder_fraction=0.75,
            ),
            ManureEvent(
                year=1,
                day=65,
                nitrogen_mass=9.24,
                phosphorus_mass=7.7,
                field_coverage=1.30,
                manure_type=ManureType.LIQUID,
                manure_supplement_method=ManureSupplementMethod.NONE,
                application_depth=7.4,
                surface_remainder_fraction=0.75,
            ),
            True,
        ),
        (
            ManureEvent(
                year=1,
                day=65,
                nitrogen_mass=9.24,
                phosphorus_mass=7.7,
                field_coverage=1.30,
                manure_type=ManureType.LIQUID,
                manure_supplement_method=ManureSupplementMethod.NONE,
                application_depth=7.4,
                surface_remainder_fraction=0.75,
            ),
            ManureEvent(
                year=1,
                day=65,
                nitrogen_mass=3.24,
                phosphorus_mass=7.7,
                field_coverage=1.30,
                manure_type=ManureType.LIQUID,
                manure_supplement_method=ManureSupplementMethod.NONE,
                application_depth=7.4,
                surface_remainder_fraction=0.75,
            ),
            False,
        ),
        (
            ManureEvent(
                year=1,
                day=65,
                nitrogen_mass=9.24,
                phosphorus_mass=6.7,
                field_coverage=1.30,
                manure_type=ManureType.LIQUID,
                manure_supplement_method=ManureSupplementMethod.NONE,
                application_depth=7.4,
                surface_remainder_fraction=0.75,
            ),
            ManureEvent(
                year=1,
                day=65,
                nitrogen_mass=9.24,
                phosphorus_mass=7.7,
                field_coverage=1.30,
                manure_type=ManureType.LIQUID,
                manure_supplement_method=ManureSupplementMethod.NONE,
                application_depth=7.4,
                surface_remainder_fraction=0.75,
            ),
            False,
        ),
        (
            ManureEvent(
                year=1,
                day=65,
                nitrogen_mass=9.24,
                phosphorus_mass=7.7,
                field_coverage=2.30,
                manure_type=ManureType.LIQUID,
                manure_supplement_method=ManureSupplementMethod.NONE,
                application_depth=7.4,
                surface_remainder_fraction=0.75,
            ),
            ManureEvent(
                year=1,
                day=65,
                nitrogen_mass=9.24,
                phosphorus_mass=7.7,
                field_coverage=1.30,
                manure_type=ManureType.LIQUID,
                manure_supplement_method=ManureSupplementMethod.NONE,
                application_depth=7.4,
                surface_remainder_fraction=0.75,
            ),
            False,
        ),
        (
            ManureEvent(
                year=1,
                day=65,
                nitrogen_mass=9.24,
                phosphorus_mass=7.7,
                field_coverage=2.30,
                manure_type=ManureType.LIQUID,
                manure_supplement_method=ManureSupplementMethod.NONE,
                application_depth=5.4,
                surface_remainder_fraction=0.75,
            ),
            ManureEvent(
                year=1,
                day=65,
                nitrogen_mass=9.24,
                phosphorus_mass=7.7,
                field_coverage=1.30,
                manure_type=ManureType.LIQUID,
                manure_supplement_method=ManureSupplementMethod.NONE,
                application_depth=7.4,
                surface_remainder_fraction=0.75,
            ),
            False,
        ),
        (
            ManureEvent(
                year=1,
                day=65,
                nitrogen_mass=9.24,
                phosphorus_mass=7.7,
                field_coverage=2.30,
                manure_type=ManureType.LIQUID,
                manure_supplement_method=ManureSupplementMethod.NONE,
                application_depth=7.4,
                surface_remainder_fraction=0.35,
            ),
            ManureEvent(
                year=1,
                day=65,
                nitrogen_mass=9.24,
                phosphorus_mass=7.7,
                field_coverage=1.30,
                manure_type=ManureType.LIQUID,
                manure_supplement_method=ManureSupplementMethod.NONE,
                application_depth=7.4,
                surface_remainder_fraction=0.75,
            ),
            False,
        ),
        (
            2,
            ManureEvent(
                year=1,
                day=65,
                nitrogen_mass=9.24,
                phosphorus_mass=7.7,
                field_coverage=1.30,
                manure_type=ManureType.LIQUID,
                manure_supplement_method=ManureSupplementMethod.NONE,
                application_depth=7.4,
                surface_remainder_fraction=0.75,
            ),
            False,
        ),
    ],
)
def test_manure_event_equality(manure_event1, manure_event2, expected: bool) -> None:
    """Tests that equality is tested correctly between ManureEvent objects."""
    actual = manure_event1 == manure_event2
    assert actual == expected


@pytest.mark.parametrize(
    "manure_event,expected",
    [
        (
            ManureEvent(
                year=1,
                day=65,
                nitrogen_mass=9.24,
                phosphorus_mass=7.7,
                manure_type=ManureType.LIQUID,
                manure_supplement_method=ManureSupplementMethod.NONE,
                field_coverage=1.30,
                application_depth=7.4,
                surface_remainder_fraction=0.75,
            ),
            hash((1, 65, 9.24, 7.7, ManureType.LIQUID, 1.30, 7.4, 0.75)),
        )
    ],
)
def test_manure_event_hash(manure_event: ManureEvent, expected: float) -> None:
    """Tests that hash returns correctly for ManureEvent objects."""
    assert manure_event.__hash__() == expected


@pytest.mark.parametrize(
    "fertilizer_event1,fertilizer_event2,expected",
    [
        (
            FertilizerEvent(
                mix_name="20-10-10",
                year=1,
                day=27,
                nitrogen_mass=7.7,
                phosphorus_mass=9.24,
                potassium_mass=8.4,
                depth=1.30,
                surface_remainder_fraction=1.20,
            ),
            FertilizerEvent(
                mix_name="20-10-10",
                year=1,
                day=27,
                nitrogen_mass=7.7,
                phosphorus_mass=9.24,
                potassium_mass=8.4,
                depth=1.30,
                surface_remainder_fraction=1.20,
            ),
            True,
        ),
        (
            FertilizerEvent(
                mix_name="20-10-10",
                year=1,
                day=27,
                nitrogen_mass=7.7,
                phosphorus_mass=9.24,
                potassium_mass=8.4,
                depth=1.30,
                surface_remainder_fraction=1.20,
            ),
            FertilizerEvent(
                mix_name="20-10-30",
                year=1,
                day=27,
                nitrogen_mass=7.7,
                phosphorus_mass=9.24,
                potassium_mass=8.4,
                depth=1.30,
                surface_remainder_fraction=1.20,
            ),
            False,
        ),
        (
            FertilizerEvent(
                mix_name="20-10-10",
                year=1,
                day=27,
                nitrogen_mass=7.7,
                phosphorus_mass=9.24,
                potassium_mass=8.4,
                depth=1.30,
                surface_remainder_fraction=1.20,
            ),
            FertilizerEvent(
                mix_name="20-10-10",
                year=1,
                day=27,
                nitrogen_mass=7.6,
                phosphorus_mass=9.24,
                potassium_mass=8.4,
                depth=1.30,
                surface_remainder_fraction=1.20,
            ),
            False,
        ),
        (
            FertilizerEvent(
                mix_name="20-10-10",
                year=1,
                day=27,
                nitrogen_mass=7.7,
                phosphorus_mass=9.25,
                potassium_mass=8.4,
                depth=1.30,
                surface_remainder_fraction=1.20,
            ),
            FertilizerEvent(
                mix_name="20-10-10",
                year=1,
                day=27,
                nitrogen_mass=7.7,
                phosphorus_mass=9.24,
                potassium_mass=8.4,
                depth=1.30,
                surface_remainder_fraction=1.20,
            ),
            False,
        ),
        (
            FertilizerEvent(
                mix_name="20-10-10",
                year=1,
                day=27,
                nitrogen_mass=7.7,
                phosphorus_mass=9.24,
                potassium_mass=8.4,
                depth=1.29,
                surface_remainder_fraction=1.20,
            ),
            FertilizerEvent(
                mix_name="20-10-10",
                year=1,
                day=27,
                nitrogen_mass=7.7,
                phosphorus_mass=9.24,
                potassium_mass=8.4,
                depth=1.30,
                surface_remainder_fraction=1.20,
            ),
            False,
        ),
        (
            FertilizerEvent(
                mix_name="20-10-10",
                year=1,
                day=27,
                nitrogen_mass=7.7,
                phosphorus_mass=9.24,
                potassium_mass=8.4,
                depth=1.30,
                surface_remainder_fraction=1.30,
            ),
            FertilizerEvent(
                mix_name="20-10-10",
                year=1,
                day=27,
                nitrogen_mass=7.7,
                phosphorus_mass=9.24,
                potassium_mass=8.4,
                depth=1.30,
                surface_remainder_fraction=1.20,
            ),
            False,
        ),
        (
            2,
            FertilizerEvent(
                mix_name="20-10-10",
                year=1,
                day=27,
                nitrogen_mass=7.7,
                phosphorus_mass=9.24,
                potassium_mass=8.4,
                depth=1.30,
                surface_remainder_fraction=1.20,
            ),
            False,
        ),
    ],
)
def test_fertilizer_event_equality(fertilizer_event1, fertilizer_event2, expected: bool) -> None:
    """Tests that equality is tested correctly between FertilizerEvent objects."""
    actual = fertilizer_event1 == fertilizer_event2
    assert actual == expected


@pytest.mark.parametrize(
    "fertilizer_event,expected",
    [
        (
            FertilizerEvent(
                mix_name="20-10-10",
                year=1,
                day=27,
                nitrogen_mass=7.7,
                phosphorus_mass=9.24,
                potassium_mass=8.4,
                depth=1.30,
                surface_remainder_fraction=1.20,
            ),
            hash((1, 27, "20-10-10", 7.7, 9.24, 8.4, 1.30, 1.20)),
        )
    ],
)
def test_fertilizer_event_hash(fertilizer_event: FertilizerEvent, expected: float) -> None:
    """Tests that hash returns correctly for FertilizerEvent objects."""
    assert fertilizer_event.__hash__() == expected
