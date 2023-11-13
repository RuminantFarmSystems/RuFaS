# import pytest
from pytest_mock import MockerFixture

from RUFAS.routines.animal.animal_reporter import AnimalReporter
from RUFAS.routines.animal.animal_manager import AnimalManager
from RUFAS.routines.animal.animal_reporter import om


def test_report_daily_animal_data(mocker: MockerFixture):
    """Unit test for function report_daily_animal_data in file
    routines/animal/ration/animal_reporter.py"""
    mocker.patch(
        "RUFAS.routines.animal.animal_manager.AnimalManager.__init__", return_value=None
    )
    animal_manager = AnimalManager(
        data=mocker.MagicMock(),
        config=mocker.MagicMock(),
        feed=mocker.MagicMock(),
        weather=mocker.MagicMock(),
        time=mocker.MagicMock(),
    )
    animal_manager.simulation_day = 42
    animal_manager.calves = [mocker.MagicMock()]
    animal_manager.heiferIs = [mocker.MagicMock(), mocker.MagicMock()]
    animal_manager.heiferIIs = [
        mocker.MagicMock(),
        mocker.MagicMock(),
        mocker.MagicMock(),
    ]
    animal_manager.heiferIIIs = [
        mocker.MagicMock(),
        mocker.MagicMock(),
        mocker.MagicMock(),
        mocker.MagicMock(),
    ]
    animal_manager.cows = [
        mocker.MagicMock(),
        mocker.MagicMock(),
        mocker.MagicMock(),
        mocker.MagicMock(),
        mocker.MagicMock(),
        mocker.MagicMock(),
    ]
    for cow in animal_manager.cows:
        cow.is_lactating = True
    animal_manager.cows[0].is_lactating = False

    AnimalReporter.report_daily_animal_data(animal_manager)

    report_daily_animal_total = om.variables_pool[
        "AnimalReporter.report_daily_animal_data.num_animals"
    ]["values"]
    assert report_daily_animal_total == [
        sum(
            (
                len(animal_manager.calves),
                len(animal_manager.heiferIs),
                len(animal_manager.heiferIIs),
                len(animal_manager.heiferIIIs),
                len(animal_manager.cows),
            )
        )
    ]

    assert om.variables_pool[
        "AnimalReporter.report_daily_animal_data.num_animals"
    ]["info_maps"] == [{}]
