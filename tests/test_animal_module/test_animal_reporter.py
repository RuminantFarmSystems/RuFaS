import pytest
from pytest_mock import MockerFixture

# from pytest_lazyfixture import lazy_fixture

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


def test_report_daily_animal_population(mocker: MockerFixture):
    """Unit test for function report_daily_animal_population in file
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

    AnimalReporter.report_daily_animal_population(animal_manager)

    report_daily_animal_total = om.variables_pool[
        "AnimalReporter.report_daily_animal_population.num_animals"
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

    assert om.variables_pool["AnimalReporter.report_daily_animal_population.num_animals"][
        "info_maps"
    ] == [{}]


def test_report_milk(mocker: MockerFixture):
    """Unit test for function report_milk in file
    routines/animal/ration/animal_reporter.py"""
    test_milk_data_update = {
        "days_in_milk": 1,
        "estimated_daily_milk_produced": 2,
        "milk_protein": 3,
        "milk_fat": 4,
        "milk_lactose": 5,
        "lactating": 6,
        "parity": 7,
        "cow_id": 8,
        "pen_id": 9,
        "simulation_day": 10,
    }
    simulation_day = test_milk_data_update["simulation_day"]
    pen = mocker.MagicMock()
    pen.animals_in_pen = [mocker.MagicMock(), mocker.MagicMock(), mocker.MagicMock()]
    for idx, animal in enumerate(pen.animals_in_pen):
        animal.days_in_milk = test_milk_data_update["days_in_milk"]
        animal.estimated_daily_milk_produced = test_milk_data_update[
            "estimated_daily_milk_produced"
        ]
        animal.mPrt = test_milk_data_update["milk_protein"]
        animal.fat_percent = test_milk_data_update["milk_fat"]
        animal.lactose_milk = test_milk_data_update["milk_lactose"]
        animal.milking = test_milk_data_update["lactating"]
        animal.calves = test_milk_data_update["parity"]
        animal.id = test_milk_data_update["cow_id"]
        animal.pen_history[-1].pen = test_milk_data_update["pen_id"]
    # act
    AnimalReporter.report_milk(pen, simulation_day)
    # assert
    assert om.variables_pool["cow.milking_update.milk_data_at_milk_update"][
        "values"
    ] == [test_milk_data_update, test_milk_data_update, test_milk_data_update]


def test_report_ration_interval_data(animal_manager_fixture, mocker: MockerFixture):
    """Unit test for function report_ration_interval_data in file
    routines/animal/ration/animal_reporter.py"""
    test_data = {
        "ration_nutrient_amount": {"dummy1": 100},
        "ration_nutrient_conc": {"dummy2": 200},
        "ration_per_animal": {"dummy3": 300, "status": 1, "objective": 2},
        "formatted_ration": {"dry_matter_intake_total": 300, "dummy3": 300},
        "MEdiet": 500,
        "avg_nutrient_rqmts": {
            "avg_BW": 1,
        },
    }
    feed = mocker.MagicMock()
    pen1 = mocker.MagicMock()
    pen1.id = "1"
    pen1.animal_combination.name = "combo1"
    pen2 = mocker.MagicMock()
    pen2.id = "2"
    pen2.animal_combination.name = "combo2"
    animal_manager_fixture.all_pens = [pen1, pen2]
    for pen in animal_manager_fixture.all_pens:
        pen.ration_nutrient_amount = test_data["ration_nutrient_amount"]
        pen.ration_nutrient_conc = test_data["ration_nutrient_conc"]
        pen.ration_per_animal = test_data["ration_per_animal"]
        pen.MEdiet = test_data["MEdiet"]
        pen.avg_nutrient_rqmts = test_data["avg_nutrient_rqmts"]

    mocker.patch(
        "RUFAS.routines.animal.ration.ration_driver.RationReporter.report_ration_supply",
        return_value="ration_supply_report",
    )

    AnimalReporter.report_ration_interval_data(animal_manager_fixture, feed)

    for i in range(1, 2):
        assert om.variables_pool[
            f"AnimalReporter.report_ration_interval_data.ration_nutrient_amount_pen_{i}_combo{i}"
        ]["values"] == [test_data["ration_nutrient_amount"]]

        assert om.variables_pool[
            f"AnimalReporter.report_ration_interval_data.MEdiet_pen_{i}_combo{i}"
        ]["values"] == [test_data["MEdiet"]]

        assert om.variables_pool[
            f"AnimalReporter.report_ration_interval_data.avg_rqmts_pen_{i}_combo{i}"
        ]["values"] == [test_data["avg_nutrient_rqmts"]]

        assert om.variables_pool[
            f"AnimalReporter.report_ration_interval_data.ration_per_animal_for_pen_{i}_combo{i}"
        ]["values"] == [test_data["formatted_ration"]]

        assert om.variables_pool[
            f"AnimalReporter.report_ration_interval_data.ration_supply_report_for_pen_{i}_combo{i}"
        ]["values"] == ["ration_supply_report"]


def test_report_daily_ration(animal_manager_fixture, mocker: MockerFixture):
    """Unit test for function report_daily_ration in file
    routines/animal/ration/animal_reporter.py"""
    test_data = {
        "ration_per_animal": {"dummy3": 300, "status": 1, "objective": 2},
        "formatted_ration_1": {"dry_matter_intake_total": 300, "dummy3": 300},
        "formatted_ration_2": {"dry_matter_intake_total": 600, "dummy3": 600},
    }
    pen1 = mocker.MagicMock()
    pen1.id = "1"
    pen1.animals_in_pen = [mocker.MagicMock()]
    pen1.animal_combination.name = "combo1"
    pen2 = mocker.MagicMock()
    pen2.id = "2"
    pen2.animals_in_pen = [mocker.MagicMock(), mocker.MagicMock()]
    pen2.animal_combination.name = "combo2"
    animal_manager_fixture.all_pens = [pen1, pen2]
    for pen in animal_manager_fixture.all_pens:
        pen.ration_per_animal = test_data["ration_per_animal"]
    AnimalReporter.report_daily_ration(animal_manager_fixture)

    for i in range(1, 2):
        assert om.variables_pool[
            f"AnimalReporter.report_daily_ration.ration_daily_feed_totals_for_pen_{i}_combo{i}"
        ]["values"] == [test_data[f"formatted_ration_{i}"]]


def test_report_animal_module_manure():
    pass


def test_report_pen_manure():
    pass


def test_report_life_cycle_manager_data():
    pass
