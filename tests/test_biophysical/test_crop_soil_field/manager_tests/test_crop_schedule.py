from typing import Any
import pytest
from pytest_mock.plugin import MockerFixture

from RUFAS.biophysical.field.crop.harvest_operations import HarvestOperation
from RUFAS.biophysical.field.manager.crop_schedule import CropSchedule
from RUFAS.data_structures.events import HarvestEvent, PlantingEvent


@pytest.mark.parametrize(
    "name,crop_ref,plant_years,plant_days,harvest_years,harvest_days,harvest_ops,heat_sched,"
    "plant_skip,harvest_skip,pat_repeat,expected",
    [
        (
            "test_1",
            "corn",
            [1990, 1991],
            [120],
            [1990, 1991],
            [255, 255],
            ["harvest_kill", "harvest_kill"],
            False,
            2,
            2,
            3,
            {
                "plant_years": [1990, 1991],
                "plant_days": [120, 120],
                "harvest_years": [1990, 1991],
                "harvest_days": [255, 255],
                "harvest_ops": [
                    HarvestOperation.HARVEST_KILL,
                    HarvestOperation.HARVEST_KILL,
                ],
            },
        ),
        (
            "test_2",
            "beans",
            [1990, 1991, 1992],
            [120, 121, 121],
            [1990, 1991, 1992],
            [255, 255, 260],
            ["harvest_only", "harvest_only", "harvest_kill"],
            True,
            2,
            4,
            3,
            {
                "plant_years": [1990, 1991, 1992],
                "plant_days": [120, 121, 121],
                "harvest_years": [1990, 1991, 1992],
                "harvest_days": [255, 255, 260],
                "harvest_ops": [
                    HarvestOperation.HARVEST_ONLY,
                    HarvestOperation.HARVEST_ONLY,
                    HarvestOperation.HARVEST_KILL,
                ],
            },
        ),
        (
            "test_3",
            "greens",
            [1999],
            [130],
            [2000],
            [220],
            ["harvest_kill"],
            False,
            0,
            0,
            10,
            {
                "plant_years": [1999],
                "plant_days": [130],
                "harvest_years": [2000],
                "harvest_days": [220],
                "harvest_ops": [HarvestOperation.HARVEST_KILL],
            },
        ),
    ],
)
def test_crop_schedule_init(
    name: str,
    crop_ref: str,
    plant_years: list[int],
    plant_days: list[int],
    harvest_years: list[int],
    harvest_days: list[int],
    harvest_ops: list[str],
    heat_sched: bool,
    plant_skip: int,
    harvest_skip: int,
    pat_repeat: int,
    expected: dict[str, list[Any]],
) -> None:
    """Tests that CropSchedule's get initialized correctly."""
    crop_schedule = CropSchedule(
        name,
        crop_ref,
        plant_years,
        plant_days,
        harvest_years,
        harvest_days,
        harvest_ops,
        heat_sched,
        plant_skip,
        harvest_skip,
        pat_repeat,
    )
    assert crop_schedule.name == name
    assert crop_schedule.crop_reference == crop_ref
    assert crop_schedule.planting_years == expected.get("plant_years")
    assert crop_schedule.planting_days == expected.get("plant_days")
    assert crop_schedule.harvest_years == expected.get("harvest_years")
    assert crop_schedule.harvest_days == expected.get("harvest_days")
    assert crop_schedule.harvest_operations == expected.get("harvest_ops")
    assert crop_schedule.heat_scheduled == heat_sched
    assert crop_schedule.pattern_skip == plant_skip
    assert crop_schedule.planting_skip == plant_skip
    assert crop_schedule.harvesting_skip == harvest_skip
    assert crop_schedule.pattern_repeat == pat_repeat


@pytest.mark.parametrize(
    "name,years,days,expected",
    [
        (
            "test_1",
            [1990, 1989],
            [],
            "'test_1': expected all years to be > 0 and in non-descending order, received " "'[1990, 1989]'.",
        ),
        (
            "test_2",
            [1998, 1999, 2000],
            [200, 200, 367],
            "'test_2': expected all days to be in range [1, 366], received '[200, 200, " "367]'.",
        ),
        (
            "test_3",
            [1997, 1998],
            [90, 120, 90],
            "test_3 Mismatch in length of parameters. Provided parameters are: planting_years=[1997, 1998],"
            " planting_days=[90, 120, 90]. Lengths are: {'planting_years': 2, 'planting_days': 3}.",
        ),
    ],
)
def test_validate_planting_parameters(name: str, years: list[int], days: list[int], expected: str) -> None:
    """Tests that the errors are raised properly when crop planting parameters are invalid."""
    with pytest.raises(ValueError) as e:
        test = CropSchedule(name, "test_crop", years, days, [2000], [240], ["harvest_kill"], False, 1, 1)
        test._validate_planting_parameters()
    assert str(e.value) == expected


@pytest.mark.parametrize(
    "name,years,days,operations,expected",
    [
        (
            "test_1",
            [1996, 1993],
            [200],
            ["harvest_kill"],
            "'test_1': expected all years to be > 0 and in non-descending order, received " "'[1996, 1993]'.",
        ),
        (
            "test_2",
            [1999, 2000],
            [200, 0],
            ["harvest_kill"],
            "'test_2': expected all days to be in range [1, 366], received '[200, 0]'.",
        ),
        (
            "test_3",
            [1998, 1999, 2000],
            [200, 200],
            ["harvest_only", "harvest_kill"],
            (
                "test_3 Mismatch in length of parameters. Provided parameters are: "
                "planting_years=[1998, 1999, 2000], planting_days=[200, 200], "
                "harvest_operations=[<HarvestOperation.HARVEST_ONLY: 'harvest_only'>, "
                "<HarvestOperation.HARVEST_KILL: 'harvest_kill'>]. Lengths are: "
                "{'planting_years': 3, 'planting_days': 2, 'harvest_operations': 2}."
            ),
        ),
        (
            "test_4",
            [1998, 1999, 1999],
            [200, 200, 240],
            ["harvest_only", "harvest_kill", "harvest_only"],
            "'test_4': expected the final harvest operation to be the only one that kills the crop, received "
            "'[<HarvestOperation.HARVEST_ONLY: 'harvest_only'>, <HarvestOperation.HARVEST_KILL: 'harvest_kill'>, "
            "<HarvestOperation.HARVEST_ONLY: 'harvest_only'>]'.",
        ),
    ],
)
def test_validate_harvest_parameters(
    name: str, years: list[int], days: list[int], operations: list[str], expected: str
) -> None:
    """Tests that harvest schedule parameters are valid."""
    with pytest.raises(ValueError) as e:
        test = CropSchedule(name, "test_crop", [1990], [130], years, days, operations, False, 1, 1)
        test._validate_harvest_parameters()
    assert str(e.value) == expected


@pytest.mark.parametrize(
    "years,days,heat_scheduled,skip,repeat,expected",
    [
        (
            [1, 3, 4],
            [120, 100, 100],
            False,
            1,
            1,
            [
                PlantingEvent("test_crop", False, 1, 120),
                PlantingEvent("test_crop", False, 3, 100),
                PlantingEvent("test_crop", False, 4, 100),
                PlantingEvent("test_crop", False, 6, 120),
                PlantingEvent("test_crop", False, 8, 100),
                PlantingEvent("test_crop", False, 9, 100),
            ],
        ),
        (
            [2, 4],
            [115, 115],
            True,
            2,
            2,
            [
                PlantingEvent("test_crop", True, 2, 115),
                PlantingEvent("test_crop", True, 4, 115),
                PlantingEvent("test_crop", True, 7, 115),
                PlantingEvent("test_crop", True, 9, 115),
                PlantingEvent("test_crop", True, 12, 115),
                PlantingEvent("test_crop", True, 14, 115),
            ],
        ),
        (
            [1, 2, 5],
            [120, 120, 110],
            False,
            2,
            0,
            [
                PlantingEvent("test_crop", False, 1, 120),
                PlantingEvent("test_crop", False, 2, 120),
                PlantingEvent("test_crop", False, 5, 110),
            ],
        ),
    ],
)
def test_generate_planting_events(
    years: list[int],
    days: list[int],
    heat_scheduled: bool,
    skip: int,
    repeat: int,
    expected: list[PlantingEvent],
) -> None:
    """Tests that planting events are correctly generated by CropSchedule objects."""
    crop_sched = CropSchedule(
        "test_name",
        "test_crop",
        years,
        days,
        [1],
        [240],
        ["harvest_kill"],
        heat_scheduled,
        skip,
        0,
        repeat,
    )
    actual = crop_sched.generate_planting_events()
    assert actual == expected


@pytest.mark.parametrize(
    "years,days,harvest_ops,heat_scheduled,skip,repeat,expected",
    [
        (
            [1, 2, 6],
            [245, 245, 240],
            ["harvest_only", "harvest_only", "harvest_kill"],
            False,
            1,
            1,
            [
                HarvestEvent("test", HarvestOperation.HARVEST_ONLY, 1, 245),
                HarvestEvent("test", HarvestOperation.HARVEST_ONLY, 2, 245),
                HarvestEvent("test", HarvestOperation.HARVEST_KILL, 6, 240),
                HarvestEvent("test", HarvestOperation.HARVEST_ONLY, 8, 245),
                HarvestEvent("test", HarvestOperation.HARVEST_ONLY, 9, 245),
                HarvestEvent("test", HarvestOperation.HARVEST_KILL, 13, 240),
            ],
        ),
        (
            [1, 1],
            [200, 260],
            ["harvest_only", "harvest_kill"],
            False,
            2,
            2,
            [
                HarvestEvent("test", HarvestOperation.HARVEST_ONLY, 1, 200),
                HarvestEvent("test", HarvestOperation.HARVEST_KILL, 1, 260),
                HarvestEvent("test", HarvestOperation.HARVEST_ONLY, 4, 200),
                HarvestEvent("test", HarvestOperation.HARVEST_KILL, 4, 260),
                HarvestEvent("test", HarvestOperation.HARVEST_ONLY, 7, 200),
                HarvestEvent("test", HarvestOperation.HARVEST_KILL, 7, 260),
            ],
        ),
        (
            [1, 2, 3],
            [240, 240, 240],
            ["harvest_only", "harvest_only", "harvest_kill"],
            True,
            1,
            2,
            [
                HarvestEvent("test", HarvestOperation.HARVEST_KILL, 3, 240),
                HarvestEvent("test", HarvestOperation.HARVEST_KILL, 7, 240),
                HarvestEvent("test", HarvestOperation.HARVEST_KILL, 11, 240),
            ],
        ),
    ],
)
def test_generate_harvest_events(
    years: list[int],
    days: list[int],
    harvest_ops: list[str],
    heat_scheduled: bool,
    skip: int,
    repeat: int,
    expected: list[HarvestEvent],
) -> None:
    """Tests that harvest events are correctly generated by CropSchedule objects."""
    crop_sched = CropSchedule(
        "test_name",
        "test",
        [1],
        [120],
        years,
        days,
        harvest_ops,
        heat_scheduled,
        0,
        skip,
        repeat,
    )
    actual = crop_sched.generate_harvest_events()
    assert expected == actual


@pytest.mark.parametrize(
    "rotation",
    [
        # Basic annual crop: plant -> harvest_only -> harvest_kill
        {
            "planting_years": [1],
            "planting_days": [100],
            "harvest_years": [1, 1],
            "harvest_days": [180, 220],
            "harvest_operations": [
                HarvestOperation.HARVEST_ONLY.value,
                HarvestOperation.HARVEST_KILL.value,
            ],
        },
        # Overwintering crop: plant one year, harvest the next
        {
            "planting_years": [1],
            "planting_days": [300],
            "harvest_years": [2],
            "harvest_days": [120],
            "harvest_operations": [HarvestOperation.HARVEST_KILL.value],
        },
        # Re-established crop after termination
        {
            "planting_years": [1, 1],
            "planting_days": [100, 230],
            "harvest_years": [1, 1],
            "harvest_days": [220, 260],
            "harvest_operations": [
                HarvestOperation.HARVEST_KILL.value,
                HarvestOperation.KILL_ONLY.value,
            ],
        },
        # Same-day planting and harvest should be allowed because planting sorts first
        {
            "planting_years": [1],
            "planting_days": [100],
            "harvest_years": [1],
            "harvest_days": [100],
            "harvest_operations": [HarvestOperation.HARVEST_ONLY.value],
        },
    ],
)
def test_validate_crop_schedule_event_order_valid(rotation: dict[str, object], mocker: MockerFixture) -> None:
    """Valid crop schedule event orders do not raise an error."""
    mock_add_error = mocker.patch("RUFAS.biophysical.field.manager.crop_schedule.OutputManager.add_error")
    CropSchedule.validate_crop_schedule_event_order(rotation, "valid_schedule")
    assert mock_add_error.call_count == 0


@pytest.mark.parametrize(
    "rotation, expected_message",
    [
        (
            # Harvest before any planting
            {
                "planting_years": [1],
                "planting_days": [100],
                "harvest_years": [1],
                "harvest_days": [90],
                "harvest_operations": [HarvestOperation.HARVEST_ONLY.value],
            },
            "harvest_only on year 1, day 90 occurs before an active planting event",
        ),
        (
            # Additional harvest after terminating harvest, without another planting
            {
                "planting_years": [1],
                "planting_days": [100],
                "harvest_years": [1, 1],
                "harvest_days": [200, 220],
                "harvest_operations": [
                    HarvestOperation.HARVEST_KILL.value,
                    HarvestOperation.HARVEST_ONLY.value,
                ],
            },
            "harvest_only on year 1, day 220 occurs before an active planting event",
        ),
        (
            # Kill before planting
            {
                "planting_years": [1],
                "planting_days": [150],
                "harvest_years": [1],
                "harvest_days": [100],
                "harvest_operations": [HarvestOperation.KILL_ONLY.value],
            },
            "kill_only on year 1, day 100 occurs before an active planting event",
        ),
    ],
)
def test_validate_crop_schedule_event_order_invalid(
    rotation: dict[str, object],
    expected_message: str,
    mocker: MockerFixture,
) -> None:
    """Invalid crop schedule event orders raise and log an error."""
    mock_add_error = mocker.patch("RUFAS.biophysical.field.manager.crop_schedule.OutputManager.add_error")

    with pytest.raises(ValueError, match=expected_message):
        CropSchedule.validate_crop_schedule_event_order(rotation, "bad_schedule")

    assert mock_add_error.call_count == 1


def test_validate_crop_schedule_event_order_invalid_harvest_operation(
    mocker: MockerFixture,
) -> None:
    """Unsupported harvest operations raise and log an error."""
    rotation = {
        "planting_years": [1],
        "planting_days": [100],
        "harvest_years": [1],
        "harvest_days": [150],
        "harvest_operations": ["bad_operation"],
    }
    mock_add_error = mocker.patch("RUFAS.biophysical.field.manager.crop_schedule.OutputManager.add_error")

    expected_message = (
        "Invalid crop schedule 'bad_schedule': harvest operation 'bad_operation' "
        "on year 1, day 150 is not supported."
    )

    with pytest.raises(ValueError, match=expected_message):
        CropSchedule.validate_crop_schedule_event_order(rotation, "bad_schedule")

    mock_add_error.assert_called_once()
