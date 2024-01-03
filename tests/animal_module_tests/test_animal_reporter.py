import pytest
from pytest_mock import MockerFixture

from RUFAS.routines.animal.animal_module_reporter import AnimalModuleReporter
from RUFAS.routines.animal.animal_manager import AnimalManager

from RUFAS.output_manager import OutputManager

om = OutputManager()


@pytest.fixture
def animal_manager_fixture(mocker: MockerFixture):
    mocker.patch("RUFAS.routines.animal.animal_manager.AnimalManager.__init__", return_value=None)
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
    routines/animal/ration/animal_module_reporter.py"""
    mocker.patch("RUFAS.routines.animal.animal_manager.AnimalManager.__init__", return_value=None)
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
    om.variables_pool = {}
    AnimalModuleReporter.report_daily_animal_population(animal_manager)

    report_daily_animal_total = om.variables_pool["AnimalManager.daily_updates.num_animals"]["values"]
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

    assert om.variables_pool["AnimalManager.daily_updates.num_animals"]["info_maps"] == [{}]


def test_report_milk(mocker: MockerFixture):
    """Unit test for function report_milk in file
    routines/animal/ration/animal_module_reporter.py"""
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
        animal.estimated_daily_milk_produced = test_milk_data_update["estimated_daily_milk_produced"]
        animal.mPrt = test_milk_data_update["milk_protein"]
        animal.fat_percent = test_milk_data_update["milk_fat"]
        animal.lactose_milk = test_milk_data_update["milk_lactose"]
        animal.milking = test_milk_data_update["lactating"]
        animal.calves = test_milk_data_update["parity"]
        animal.id = test_milk_data_update["cow_id"]
        animal.pen_history[-1].pen = test_milk_data_update["pen_id"]
    # act
    AnimalModuleReporter.report_milk(pen, simulation_day)
    # assert
    assert om.variables_pool["Cow.milking_update.milk_data_at_milk_update"]["values"] == [
        test_milk_data_update,
        test_milk_data_update,
        test_milk_data_update,
    ]


def test_report_ration_interval_data(animal_manager_fixture, mocker: MockerFixture):
    """Unit test for function report_ration_interval_data in file
    routines/animal/ration/animal_module_reporter.py"""
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

    AnimalModuleReporter.report_ration_interval_data(animal_manager_fixture, feed, 1)

    for i in range(1, 2):
        assert om.variables_pool[f"AnimalManager._calc_ration_at_interval.ration_nutrient_amount_pen_{i}_combo{i}"][
            "values"
        ] == [test_data["ration_nutrient_amount"]]

        assert om.variables_pool[f"AnimalManager._calc_ration_at_interval.MEdiet_pen_{i}_combo{i}"]["values"] == [
            test_data["MEdiet"]
        ]

        assert om.variables_pool[f"AnimalManager._calc_ration_at_interval.avg_rqmts_pen_{i}_combo{i}"]["values"] == [
            test_data["avg_nutrient_rqmts"]
        ]

        assert om.variables_pool[f"AnimalManager._calc_ration_at_interval.ration_per_animal_for_pen_{i}_combo{i}"][
            "values"
        ] == [test_data["formatted_ration"]]

        assert om.variables_pool[f"AnimalManager._calc_ration_at_interval.ration_supply_report_for_pen_{i}_combo{i}"][
            "values"
        ] == ["ration_supply_report"]


def test_report_daily_ration(animal_manager_fixture, mocker: MockerFixture):
    """Unit test for function report_daily_ration in file
    routines/animal/ration/animal_module_reporter.py"""
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
    mocker.patch("RUFAS.routines.animal.animal_module_reporter.AnimalModuleReporter.report_daily_feed_emissions")
    AnimalModuleReporter.report_daily_ration(animal_manager_fixture)

    for i in range(1, 2):
        assert om.variables_pool[
            f"AnimalModuleReporter.report_daily_ration.ration_daily_feed_totals_for_pen_{i}_combo{i}"][
            "values"
        ] == [test_data[f"formatted_ration_{i}"]]


def test_report_animal_module_manure():
    test_output_dict = {"prefix": "dummy", "manure": {"property1": 100, "property2": 200}}
    test_dict = {"example": test_output_dict}

    AnimalModuleReporter.report_animal_module_manure(test_dict)

    for i in range(1, 2):
        assert om.variables_pool[f"AnimalManager.daily_updates.dummy_property{i}"]["values"] == [100 * i]


def test_report_pen_manure(mocker: MockerFixture):
    dummy_pen = mocker.MagicMock()
    dummy_pen.id = 1
    dummy_pen.animal_combination._name_ = "dummy_name"
    dummy_pen.manure = {"dummy_dict": 100}

    AnimalModuleReporter.report_pen_manure(dummy_pen)

    assert om.variables_pool["pen.calc_manure.pen_manure_data"]["values"] == [dummy_pen.manure]


def test_report_life_cycle_manager_data(mocker: MockerFixture):
    life_cycle_manager = mocker.MagicMock()
    keydict = {
        "sold_heiferIII_oversupply_num": 1,
        "bought_heifer_num": 2,
        "sold_heiferII_num": 3,
        "cow_herd_exit_num": 4,
        "GnRH_injection_num_h": 5,
        "GnRH_injection_num": 6,
        "PGF_injection_num": 7,
        "PGF_injection_num_h": 8,
        "ai_num": 9,
        "preg_check_num": 10,
        "preg_check_num_h": 11,
        "sold_calf_num": 12,
        "daily_milk_production": 13,
        "open_cow_num": 14,
        "vwp_cow_num": 15,
        "preg_cow_num": 16,
        "milking_cow_num": 17,
        "dry_cow_num": 18,
        "avg_days_in_milk": 19,
        "avg_days_in_preg": 20,
        "avg_cow_body_weight": 21,
        "avg_parity_num": 22,
        "avg_calving_interval": 23,
        "avg_breeding_to_preg_time": 24,
        "avg_heifer_culling_age": 25,
        "avg_cow_culling_age": 26,
        "avg_mature_body_weight": 27,
        "cull_reason_stats": 28,
    }
    for key, value in keydict.items():
        setattr(life_cycle_manager, key, value)
    life_cycle_manager.num_cow_for_parity = {"1": 100, "2": 200, "3": 300, "greater_than_3": 400}
    life_cycle_manager.avg_calving_to_preg_time = {"1": 100, "2": 200, "3": 300, "greater_than_3": 400}
    life_cycle_manager.avg_age_for_calving = {"1": 100, "2": 200, "3": 300, "greater_than_3": 400}

    sim_day = 42

    # act
    AnimalModuleReporter.report_life_cycle_manager_data(life_cycle_manager, sim_day)

    # assert
    for key, value in keydict.items():
        assert om.variables_pool[f"LifeCycleManager.daily_update.{key}"]["values"] == [keydict[key]]
    assert om.variables_pool["LifeCycleManager.daily_update.sim_day"]["values"] == [sim_day]
    for i in range(1, 3):
        assert om.variables_pool[f"LifeCycleManager.daily_update.num_cow_for_parity_{i}"]["values"] == [100 * i]
        assert om.variables_pool[f"LifeCycleManager.daily_update.calving_to_preg_time_{i}"]["values"] == [100 * i]
        assert om.variables_pool[f"LifeCycleManager.daily_update.avg_age_for_calving_{i}"]["values"] == [100 * i]
    assert om.variables_pool["LifeCycleManager.daily_update.num_cow_for_parity_greater_than_3"]["values"] == [400]
    assert om.variables_pool["LifeCycleManager.daily_update.calving_to_preg_time_greater_than_3"]["values"] == [400]
    assert om.variables_pool["LifeCycleManager.daily_update.avg_age_for_calving_greater_than_3"]["values"] == [400]


def test_report_sold_animal_information(mocker: MockerFixture):
    sold_animals = [mocker.MagicMock(), mocker.MagicMock(), mocker.MagicMock()]
    sold_report = {
        "id": [1, 2, 3],
        "cull_reason": ["low1", "low2"],
        "body_weight": [100, 200, 300],
        "days_in_milk": [100],
        "calves": [42],
    }
    sold_report_expected = {
        "animal_id": [1, 2, 3],
        "animal_type": ["dummy", "dummy", "dummy"],
        "cull_reason": ["low1", "low2", "NA"],
        "body_weight": [100, 200, 300],
        "days_in_milk": [100, "NA", "NA"],
        "parity": [42, "NA", "NA"],
    }
    animalcount = 0
    for animal in sold_animals:
        for key in sold_report.keys():
            if len(sold_report[key]) > animalcount:
                setattr(animal, key, sold_report[key][animalcount])
            else:
                delattr(animal, key)
        animalcount += 1

    for animal in sold_animals:
        animal.__class__.__name__ = "dummy"

    animal_manager = mocker.MagicMock()
    animal_manager.life_cycle_manager.sold_heiferIIs = [sold_animals[0]]
    animal_manager.life_cycle_manager.sold_heiferIIIs = [sold_animals[1]]
    animal_manager.life_cycle_manager.sold_and_died_cows = [sold_animals[2]]

    # act
    AnimalModuleReporter.report_sold_animal_information(animal_manager)

    # assert
    for key in sold_report_expected.keys():
        assert (
            om.variables_pool[f"AnimalModuleReporter.report_sold_animal_information.{key}"]["values"]
            == sold_report_expected[key]
        )


def test_report_305d_milk(mocker: MockerFixture):
    animal_manager = mocker.MagicMock()
    animal_manager.cows = [mocker.MagicMock(), mocker.MagicMock()]
    for cow in animal_manager.cows:
        cow.is_lactating = True
    animal_manager.cows[0].latest_milk_production_305days = 100
    animal_manager.cows[1].latest_milk_production_305days = 200

    # act
    AnimalModuleReporter.report_305d_milk(animal_manager)

    # assert it's 150
    assert om.variables_pool["cow.update_milk_production_history.milk_production_305days_herd_mean"]["values"] == [
        150.0
    ]

    animal_manager.cows[0].latest_milk_production_305days = 0.0
    # re assert other case, different average
    AnimalModuleReporter.report_305d_milk(animal_manager)

    # assert it's 150
    assert om.variables_pool["cow.update_milk_production_history.milk_production_305days_herd_mean"]["values"] == [
        150.0,
        200.0,
    ]


def test_report_daily_reports(mocker: MockerFixture):
    animal_manager = mocker.MagicMock()
    animal_manager.all_pens = [mocker.MagicMock(), mocker.MagicMock()]
    animal_manager.all_pens[0].animal_combination.name = "LAC_COW"

    patch_for_report_daily_animal_population = mocker.patch.object(AnimalModuleReporter,
                                                                   "report_daily_animal_population")
    patch_for_report_life_cycle_manager_data = mocker.patch.object(
        AnimalModuleReporter, "report_life_cycle_manager_data", return_value=""
    )
    patch_for_report_report_daily_ration = mocker.patch.object(AnimalModuleReporter, "report_daily_ration",
                                                               return_value="")
    patch_for_report_305d_milk = mocker.patch.object(AnimalModuleReporter, "report_305d_milk", return_value="")
    patch_for_report_pen_manure_properties = mocker.patch.object(
        AnimalModuleReporter, "report_pen_manure_properties", return_value=""
    )
    patch_for_report_milk = mocker.patch.object(AnimalModuleReporter, "report_milk", return_value="")

    # act
    AnimalModuleReporter.report_daily_reports(animal_manager)

    # assert
    patch_for_report_daily_animal_population.assert_called_once_with(animal_manager)
    patch_for_report_life_cycle_manager_data.assert_called_once_with(
        animal_manager.life_cycle_manager, animal_manager.simulation_day
    )
    patch_for_report_report_daily_ration.assert_called_once_with(animal_manager)
    patch_for_report_305d_milk.assert_called_once_with(animal_manager)
    assert patch_for_report_pen_manure_properties.call_count == len(animal_manager.all_pens)
    patch_for_report_milk.assert_called_once_with(animal_manager.all_pens[0], animal_manager.simulation_day)


def test_report_end_of_simulation(mocker: MockerFixture):
    animal_manager = mocker.MagicMock()
    patch_for_plan_animal_allocation = mocker.patch.object(
        AnimalModuleReporter, "report_sold_animal_information", return_value=""
    )

    # act
    AnimalModuleReporter.report_end_of_simulation(animal_manager, 100)

    # assert
    assert patch_for_plan_animal_allocation.call_count == 1
    patch_for_plan_animal_allocation.assert_called_once_with(animal_manager)
