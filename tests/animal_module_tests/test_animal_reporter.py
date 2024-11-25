import pytest
from mock.mock import call
from pytest_mock import MockerFixture

from RUFAS.output_manager import OutputManager
from RUFAS.routines.animal.animal_manager import AnimalManager
from RUFAS.routines.animal.animal_module_reporter import AnimalModuleReporter
from RUFAS.routines.animal.life_cycle import animal_constants
from RUFAS.routines.animal.life_cycle.pen_history import PenHistory
from RUFAS.time import Time
from RUFAS.units import MeasurementUnits

om = OutputManager()


@pytest.fixture
def animal_manager_fixture(mocker: MockerFixture) -> AnimalManager:
    mocker.patch("RUFAS.routines.animal.animal_manager.AnimalManager.__init__", return_value=None)
    animal_manager = AnimalManager(
        data=mocker.MagicMock(),
        feed=mocker.MagicMock(),
        weather=mocker.MagicMock(),
        time=mocker.MagicMock(),
        feed_emissions_estimator=mocker.MagicMock(),
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


def test_data_padder() -> None:
    """Unit test for function data_padder in file routines/animal/animal_module_reporter.py"""
    reference_variable = "reference"
    om.variables_pool = {}
    om.variables_pool[reference_variable] = {}
    om.variables_pool[reference_variable]["values"] = [0, 1, 2, 3, 4]

    # Act
    AnimalModuleReporter.data_padder(
        reference_variable,
        full_variable_to_add="full_variable",
        thing_to_add=0,
        simulation_day=100,
        info_map={"class": "dummyclass", "function": "dummyfunction", "units": MeasurementUnits.ANIMALS},
        units=MeasurementUnits.ANIMALS,
    )

    # Assert
    full_variable_added = om.variables_pool["dummyclass.dummyfunction.full_variable"]["values"]
    assert full_variable_added[-1] == 0
    assert len(full_variable_added) == 4


def test_data_padder_no_data_to_pad() -> None:
    """Unit test for function data_padder in file routines/animal/animal_module_reporter.py"""
    reference_variable = "reference"
    om.variables_pool = {}
    om.variables_pool[reference_variable] = {}

    # Act
    AnimalModuleReporter.data_padder(
        reference_variable,
        full_variable_to_add="full_variable",
        thing_to_add=0,
        simulation_day=0,
        info_map={"class": "dummyclass", "function": "dummyfunction"},
        units={"test": "dummy"},
    )

    # Assert
    assert "dummyclass.dummyfunction.full_variable" not in om.variables_pool


def test_report_daily_animal_population(mocker: MockerFixture) -> None:
    """Unit test for function report_daily_animal_population in file
    routines/animal/ration/animal_module_reporter.py"""
    mocker.patch("RUFAS.routines.animal.animal_manager.AnimalManager.__init__", return_value=None)
    animal_manager = AnimalManager(
        data=mocker.MagicMock(),
        feed=mocker.MagicMock(),
        weather=mocker.MagicMock(),
        time=mocker.MagicMock(),
        feed_emissions_estimator=mocker.MagicMock(),
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

    report_daily_animal_total = om.variables_pool["AnimalModuleReporter.report_daily_animal_population.num_animals"][
        "values"
    ]
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

    assert om.variables_pool["AnimalModuleReporter.report_daily_animal_population.num_animals"]["info_maps"] == [
        {
            "data_origin": [("AnimalManager", "daily_updates")],
            "units": MeasurementUnits.ANIMALS.value,
        }
    ]


def test_report_milk(mocker: MockerFixture) -> None:
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
    pen.animals_in_pen = {
        0: mocker.MagicMock(),
        1: mocker.MagicMock(),
        2: mocker.MagicMock(),
    }
    for idx, animal in enumerate(list(pen.animals_in_pen.values())):
        animal.days_in_milk = test_milk_data_update["days_in_milk"]
        animal.estimated_daily_milk_produced = test_milk_data_update["estimated_daily_milk_produced"]
        animal.mPrt = test_milk_data_update["milk_protein"]
        animal.fat_percent = test_milk_data_update["milk_fat"]
        animal.lactose_milk = test_milk_data_update["milk_lactose"]
        animal.milking = test_milk_data_update["lactating"]
        animal.calves = test_milk_data_update["parity"]
        animal.id = test_milk_data_update["cow_id"]
        animal.pen_history = [
            PenHistory(start_date=0, end_date=0, pen=test_milk_data_update["pen_id"], classes_in_pen=[])
        ]
    # act
    AnimalModuleReporter.report_milk(pen, simulation_day)
    # assert
    assert om.variables_pool["AnimalModuleReporter.report_milk.milk_data_at_milk_update"]["values"] == [
        test_milk_data_update,
        test_milk_data_update,
        test_milk_data_update,
    ]
    assert om.variables_pool["AnimalModuleReporter.report_milk.milk_data_at_milk_update"]["info_maps"] == [
        {
            "data_origin": [("Cow", "milking_update")],
            "units": {
                "days_in_milk": MeasurementUnits.DAYS.value,
                "estimated_daily_milk_produced": MeasurementUnits.KILOGRAMS_PER_DAY.value,
                "milk_protein": MeasurementUnits.KILOGRAMS_PER_DAY.value,
                "milk_fat": MeasurementUnits.KILOGRAMS_PER_DAY.value,
                "milk_lactose": MeasurementUnits.KILOGRAMS_PER_DAY.value,
                "lactating": MeasurementUnits.UNITLESS.value,
                "parity": MeasurementUnits.UNITLESS.value,
                "cow_id": MeasurementUnits.UNITLESS.value,
                "pen_id": MeasurementUnits.UNITLESS.value,
                "simulation_day": MeasurementUnits.SIMULATION_DAY.value,
            },
        },
        {
            "data_origin": [("Cow", "milking_update")],
            "units": {
                "days_in_milk": MeasurementUnits.DAYS.value,
                "estimated_daily_milk_produced": MeasurementUnits.KILOGRAMS_PER_DAY.value,
                "milk_protein": MeasurementUnits.KILOGRAMS_PER_DAY.value,
                "milk_fat": MeasurementUnits.KILOGRAMS_PER_DAY.value,
                "milk_lactose": MeasurementUnits.KILOGRAMS_PER_DAY.value,
                "lactating": MeasurementUnits.UNITLESS.value,
                "parity": MeasurementUnits.UNITLESS.value,
                "cow_id": MeasurementUnits.UNITLESS.value,
                "pen_id": MeasurementUnits.UNITLESS.value,
                "simulation_day": MeasurementUnits.SIMULATION_DAY.value,
            },
        },
        {
            "data_origin": [("Cow", "milking_update")],
            "units": {
                "days_in_milk": MeasurementUnits.DAYS.value,
                "estimated_daily_milk_produced": MeasurementUnits.KILOGRAMS_PER_DAY.value,
                "milk_protein": MeasurementUnits.KILOGRAMS_PER_DAY.value,
                "milk_fat": MeasurementUnits.KILOGRAMS_PER_DAY.value,
                "milk_lactose": MeasurementUnits.KILOGRAMS_PER_DAY.value,
                "lactating": MeasurementUnits.UNITLESS.value,
                "parity": MeasurementUnits.UNITLESS.value,
                "cow_id": MeasurementUnits.UNITLESS.value,
                "pen_id": MeasurementUnits.UNITLESS.value,
                "simulation_day": MeasurementUnits.SIMULATION_DAY.value,
            },
        },
    ]


def test_report_ration_interval_data(animal_manager_fixture: AnimalManager, mocker: MockerFixture) -> None:
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
    animal_manager_fixture.formulation_interval = mocker.MagicMock()
    for pen in animal_manager_fixture.all_pens:
        pen.ration_nutrient_amount = test_data["ration_nutrient_amount"]
        pen.ration_nutrient_conc = test_data["ration_nutrient_conc"]
        pen.ration_per_animal = test_data["ration_per_animal"]
        pen.MEdiet = test_data["MEdiet"]
        pen.avg_nutrient_rqmts = test_data["avg_nutrient_rqmts"]

    mock_ration_report = mocker.patch(
        "RUFAS.routines.animal.ration.ration_driver.RationReporter.report_ration_supply",
        return_value="ration_supply_report",
    )

    mock_add_variable = mocker.patch("RUFAS.routines.animal.animal_module_reporter.om.add_variable")

    for pen in animal_manager_fixture.all_pens:
        AnimalModuleReporter.report_ration_interval_data(pen, feed, 1)

    assert mock_ration_report.call_count == 2
    assert mock_add_variable.call_count == 10


def test_report_daily_ration(animal_manager_fixture: AnimalManager, mocker: MockerFixture) -> None:
    """Unit test for function report_daily_ration in file
    routines/animal/ration/animal_module_reporter.py"""
    test_data = {
        "ration_per_animal": {
            "dummy1": 300,
            "dummy2": 100,
            "status": 1,
            "objective": 2,
        },
        "formatted_ration_1": {
            "dry_matter_intake_total": 400,
            "byproducts_total": 100,
            "dummy1": 300,
            "dummy2": 100,
        },
        "formatted_ration_2": {
            "dry_matter_intake_total": 800,
            "byproducts_total": 200,
            "dummy1": 600,
            "dummy2": 200,
        },
    }
    pen1 = mocker.MagicMock()
    pen1.id = "1"
    pen1.animals_in_pen = {0: mocker.MagicMock()}
    pen1.animal_combination.name = "combo1"
    pen2 = mocker.MagicMock()
    pen2.id = "2"
    pen2.animals_in_pen = {0: mocker.MagicMock(), 1: mocker.MagicMock()}
    pen2.animal_combination.name = "combo2"
    animal_manager_fixture.all_pens = [pen1, pen2]
    for pen in animal_manager_fixture.all_pens:
        pen.ration_per_animal = test_data["ration_per_animal"]
    mocker.patch("RUFAS.routines.animal.animal_module_reporter.AnimalModuleReporter.report_daily_feed_emissions")
    mock_available_feeds = {}
    mock_available_feeds["dummy1"] = {"Fd_Category": "NA"}
    mock_available_feeds["dummy2"] = {"Fd_Category": "By-Product/Other"}
    AnimalModuleReporter.report_daily_ration(animal_manager_fixture, mock_available_feeds)

    for i in range(1, 2):
        assert om.variables_pool[
            f"AnimalModuleReporter.report_daily_ration.ration_daily_feed_totals_for_pen_{i}_combo{i}"
        ]["values"] == [test_data[f"formatted_ration_{i}"]]


def test_report_daily_pen_total(mocker: MockerFixture) -> None:
    """Unit test for function report_daily_pen_total in file
    routines/animal/ration/animal_module_reporter.py"""
    pen_list = [mocker.MagicMock(), mocker.MagicMock(), mocker.MagicMock(), mocker.MagicMock()]
    for i in range(len(pen_list)):
        pen_list[i].id = i
        pen_list[i].animal_combination.name = "some_name"
        pen_list[i].animals_in_pen = [i] * i
    simulation_day = 0
    AnimalModuleReporter.report_daily_pen_total(simulation_day, pen_list)
    for i in range(len(pen_list)):
        assert om.variables_pool[f"AnimalModuleReporter.report_daily_pen_total.number_of_animals_in_pen_{i}_some_name"][
            "values"
        ] == [i]
    for i in range(len(pen_list)):
        pen_list[i].animals_in_pen = [i] * (i + 1)
    AnimalModuleReporter.report_daily_pen_total(simulation_day, pen_list)
    for i in range(1, 2):
        assert om.variables_pool[f"AnimalModuleReporter.report_daily_pen_total.number_of_animals_in_pen_{i}_some_name"][
            "values"
        ] == [i, i + 1]


def test_report_animal_module_manure() -> None:
    test_output_dict = {
        "prefix": "dummy",
        "manure": {"urea": 100, "urine": 200},
    }
    test_dict = {"example": test_output_dict}

    AnimalModuleReporter.report_animal_module_manure(test_dict)

    # for i in range(1, 2):
    #     assert om.variables_pool[f"AnimalModuleReporter.report_animal_module_manure.dummy_property{i}"]["values"] == [
    #         100 * i
    #     ]
    assert om.variables_pool["AnimalModuleReporter.report_animal_module_manure.dummy_urea"]["values"] == [100]
    assert om.variables_pool["AnimalModuleReporter.report_animal_module_manure.dummy_urine"]["values"] == [200]


def test_report_life_cycle_manager_data(mocker: MockerFixture) -> None:
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
    life_cycle_manager.num_cow_for_parity = {
        "1": 100,
        "2": 200,
        "3": 300,
        "greater_than_3": 400,
    }
    life_cycle_manager.avg_calving_to_preg_time = {
        "1": 100,
        "2": 200,
        "3": 300,
        "greater_than_3": 400,
    }
    life_cycle_manager.avg_age_for_calving = {
        "1": 100,
        "2": 200,
        "3": 300,
        "greater_than_3": 400,
    }

    sim_day = 42
    mock_add_variable = mocker.patch("RUFAS.routines.animal.animal_module_reporter.om.add_variable")

    # act
    AnimalModuleReporter.report_life_cycle_manager_data(life_cycle_manager, sim_day)

    # assert
    assert mock_add_variable.call_count == 49


@pytest.mark.parametrize(
    "animal_id, animal_type, body_weight, sold_at_day, " "cull_reason, days_in_milk, calves",
    [
        (1, "Cow", 100, 10, "low production", 150, 2),
        (1, "Cow", 100, 10, animal_constants.DEATH_CULL, 150, 2),
        (1, "Cow", 150, None, None, None, None),
        (2, "Calf", 50, 20, "male", 100, 1),
        (2, "Calf", 50, None, None, None, None),
        (3, "HeiferII", 200, 30, "disease", 200, 2),
        (3, "HeiferII", 200, None, None, None, None),
        (4, "HeiferIII", 300, 40, "disease", 250, 3),
        (4, "HeiferIII", 300, None, None, None, None),
    ],
)
def test_report_sold_animal_information(
    animal_id: int,
    animal_type: str,
    body_weight: float,
    sold_at_day: int,
    cull_reason: str,
    days_in_milk: int,
    calves: int,
    mocker: MockerFixture,
) -> None:
    """Unit test for function report_sold_animal_information in file routines/animal/animal_module_reporter.py"""
    # Arrange
    mock_animal = mocker.MagicMock()
    mock_animal.id = animal_id
    mock_animal.__class__.__name__ = animal_type
    mock_animal.body_weight = body_weight
    optional_attrs_dict = {
        "sold_at_day": sold_at_day,
        "cull_reason": cull_reason,
        "days_in_milk": days_in_milk,
        "calves": calves,
    }
    none_str = "NA"
    for attr, value in optional_attrs_dict.items():
        if value is not None:
            setattr(mock_animal, attr, value)
        else:
            setattr(mock_animal, attr, none_str)
    mock_animal_sell_report = {
        "id": mock_animal.id,
        "animal_type": mock_animal.__class__.__name__,
        "sold_at_day": mock_animal.sold_at_day,
        "body_weight": mock_animal.body_weight,
        "cull_reason": mock_animal.cull_reason,
        "days_in_milk": mock_animal.days_in_milk,
        "parity": mock_animal.calves,
    }
    life_cycle_manager = mocker.MagicMock()
    life_cycle_manager.sold_calves_info = [mock_animal_sell_report] if animal_type == "Calf" else []
    life_cycle_manager.sold_heiferIIs_info = [mock_animal_sell_report] if animal_type == "HeiferII" else []
    life_cycle_manager.sold_heiferIIIs_info = [mock_animal_sell_report] if animal_type == "HeiferIII" else []
    life_cycle_manager.sold_and_died_cows_info = [mock_animal_sell_report] if animal_type == "Cow" else []

    patch_for_add_variable = mocker.patch("RUFAS.routines.animal" ".animal_module_reporter.om.add_variable")
    assert patch_for_add_variable.call_count == 0

    # Act
    AnimalModuleReporter.report_sold_animal_information(life_cycle_manager)

    # Assert
    if cull_reason == animal_constants.DEATH_CULL:
        assert patch_for_add_variable.call_count == 0
        return

    patch_for_add_variable.assert_any_call("animal_id", animal_id, mocker.ANY)
    patch_for_add_variable.assert_any_call("animal_type", animal_type, mocker.ANY)
    patch_for_add_variable.assert_any_call("body_weight", body_weight, mocker.ANY)

    if sold_at_day is not None:
        patch_for_add_variable.assert_any_call("sold_day", sold_at_day, mocker.ANY)
    else:
        patch_for_add_variable.assert_any_call("sold_day", none_str, mocker.ANY)

    if cull_reason is not None:
        patch_for_add_variable.assert_any_call("cull_reason", cull_reason, mocker.ANY)
    else:
        patch_for_add_variable.assert_any_call("cull_reason", none_str, mocker.ANY)

    if days_in_milk is not None:
        patch_for_add_variable.assert_any_call("days_in_milk", days_in_milk, mocker.ANY)
    else:
        patch_for_add_variable.assert_any_call("days_in_milk", none_str, mocker.ANY)

    if calves is not None:
        patch_for_add_variable.assert_any_call("parity", calves, mocker.ANY)
    else:
        patch_for_add_variable.assert_any_call("parity", none_str, mocker.ANY)


def test_report_305d_milk(mocker: MockerFixture) -> None:
    animal_manager = mocker.MagicMock()
    animal_manager.cows = [mocker.MagicMock(), mocker.MagicMock()]
    for cow in animal_manager.cows:
        cow.is_lactating = True
    animal_manager.cows[0].latest_milk_production_305days = 100
    animal_manager.cows[1].latest_milk_production_305days = 200

    # act
    AnimalModuleReporter.report_305d_milk(animal_manager)

    # assert it's 150
    assert om.variables_pool["AnimalModuleReporter.report_305d_milk.milk_production_305days_herd_mean"]["values"] == [
        150.0
    ]

    animal_manager.cows[0].latest_milk_production_305days = 0.0
    # re assert other case, different average
    AnimalModuleReporter.report_305d_milk(animal_manager)

    # assert it's 150
    assert om.variables_pool["AnimalModuleReporter.report_305d_milk.milk_production_305days_herd_mean"]["values"] == [
        150.0,
        200.0,
    ]


def test_report_daily_reports(mocker: MockerFixture) -> None:
    animal_manager = mocker.MagicMock()
    animal_manager.all_pens = [mocker.MagicMock(), mocker.MagicMock()]
    animal_manager.all_pens[0].animal_combination.name = "LAC_COW"

    patch_for_report_daily_animal_population = mocker.patch.object(
        AnimalModuleReporter, "report_daily_animal_population"
    )
    patch_for_report_life_cycle_manager_data = mocker.patch.object(
        AnimalModuleReporter, "report_life_cycle_manager_data", return_value=""
    )
    patch_for_report_report_daily_ration = mocker.patch.object(
        AnimalModuleReporter, "report_daily_ration", return_value=""
    )
    patch_for_report_305d_milk = mocker.patch.object(AnimalModuleReporter, "report_305d_milk", return_value="")
    patch_for_report_pen_manure_properties = mocker.patch.object(
        AnimalModuleReporter, "report_pen_manure_properties", return_value=""
    )
    patch_for_report_milk = mocker.patch.object(AnimalModuleReporter, "report_milk", return_value="")
    mock_available_feeds = mocker.MagicMock()
    patch_for_data_padder = mocker.patch.object(AnimalModuleReporter, "data_padder", return_value="")
    # act
    AnimalModuleReporter.report_daily_reports(animal_manager, mock_available_feeds)

    # assert
    patch_for_report_daily_animal_population.assert_called_once_with(animal_manager)
    patch_for_report_life_cycle_manager_data.assert_called_once_with(
        animal_manager.life_cycle_manager, animal_manager.simulation_day
    )
    patch_for_report_report_daily_ration.assert_called_once_with(animal_manager, mock_available_feeds)
    patch_for_report_305d_milk.assert_called_once_with(animal_manager)
    assert patch_for_report_pen_manure_properties.call_count == len(animal_manager.all_pens)
    patch_for_report_milk.assert_called_once_with(animal_manager.all_pens[0], animal_manager.simulation_day)
    patch_for_data_padder.assert_called()


def test_report_end_of_simulation(mocker: MockerFixture) -> None:
    animal_manager = mocker.MagicMock()
    animal_manager.heiferIIs = mocker.MagicMock()
    animal_manager.cows = mocker.MagicMock()

    time = mocker.MagicMock(auto_spec=Time)
    time.simulation_day = mocker.MagicMock()

    patch_for_plan_animal_allocation = mocker.patch.object(
        AnimalModuleReporter, "report_sold_animal_information", return_value=""
    )
    patch_for_record_animal_events = mocker.patch.object(AnimalModuleReporter, "_record_animal_events")
    patch_for_record_heiferIIs_conception_rate = mocker.patch.object(
        AnimalModuleReporter, "_record_heiferIIs_conception_rate"
    )
    patch_for_record_cows_conception_rate = mocker.patch.object(AnimalModuleReporter, "_record_cows_conception_rate")

    # act
    AnimalModuleReporter.report_end_of_simulation(animal_manager, time, animal_manager.heiferIIs, animal_manager.cows)

    # assert
    assert patch_for_plan_animal_allocation.call_count == 1
    patch_for_plan_animal_allocation.assert_called_once_with(animal_manager)
    assert patch_for_record_animal_events.call_args_list == [
        call(animal_manager.cows, time.simulation_day),
        call(animal_manager.heiferIIs, time.simulation_day),
    ]
    patch_for_record_heiferIIs_conception_rate.assert_called_once()
    patch_for_record_cows_conception_rate.assert_called_once()
