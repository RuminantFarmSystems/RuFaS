import pytest
from pytest_mock import MockerFixture
from pytest_lazyfixture import lazy_fixture

from RUFAS.routines.animal.animal_reporter import AnimalReporter
from RUFAS.routines.animal.animal_manager import AnimalManager
from RUFAS.routines.animal.animal_reporter import om


@pytest.fixture
def animal_manager_fixture(mocker: MockerFixture):
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

    return animal_manager


def test___init__():
    pass


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

    assert om.variables_pool["AnimalReporter.report_daily_animal_data.num_animals"][
        "info_maps"
    ] == [{}]


def test_report_milk():
    """Unit test for function report_milk in file
    routines/animal/ration/animal_reporter.py"""
    pass


def test_report_ration_interval_data(animal_manager_fixture, mocker: MockerFixture):
    """Unit test for function report_ration_interval_data in file
    routines/animal/ration/animal_reporter.py"""
    feed = mocker.MagicMock()
    pen1 = mocker.MagicMock()
    pen2 = mocker.MagicMock()
    animal_manager_fixture.all_pens = [pen1, pen2]
    for pen in animal_manager_fixture.all_pens:
        pen.ration_nutrient_amount = {"dummy1": 100}
        pen.ration_nutrient_conc = {"dummy2": 200}
        pen.ration_per_animal = {"dummy3": 300, "status": 1, "objective": 2}

    mocker.patch(
        "RUFAS.routines.animal.ration.ration_driver.RationReporter.report_ration_supply",
        return_value=None,
    )

    AnimalReporter.report_ration_interval_data(animal_manager_fixture, feed)

    # report_ration_interval = om.variables_pool[
    #     "AnimalReporter.report_ration_interval_data.____"
    # ]["values"]


def test_report_daily_ration():
    """Unit test for function report_daily_ration in file
    routines/animal/ration/animal_reporter.py"""
    pass
