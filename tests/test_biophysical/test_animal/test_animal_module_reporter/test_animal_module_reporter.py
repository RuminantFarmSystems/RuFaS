from dataclasses import asdict
from typing import Any
from unittest.mock import MagicMock, call
from pytest_mock import MockerFixture
import pytest

from RUFAS.biophysical.animal import animal_constants
from RUFAS.biophysical.animal.animal_module_reporter import AnimalModuleReporter
from RUFAS.biophysical.animal.data_types.animal_combination import AnimalCombination
from RUFAS.biophysical.animal.data_types.animal_manure_excretions import AnimalManureExcretions
from RUFAS.biophysical.animal.data_types.animal_population import AnimalPopulationStatistics
from RUFAS.biophysical.animal.data_types.animal_typed_dicts import SoldAnimalTypedDict, StillbornCalfTypedDict
from RUFAS.biophysical.animal.data_types.herd_statistics import HerdStatistics
from RUFAS.biophysical.animal.data_types.milk_production import MilkProductionStatistics
from RUFAS.biophysical.animal.data_types.nutrition_data_structures import (
    NutritionSupply,
    NutritionRequirements,
    NutritionEvaluationResults,
)
from RUFAS.biophysical.animal.data_types.reproduction import HerdReproductionStatistics
from RUFAS.biophysical.animal.ration.amino_acid import EssentialAminoAcidRequirements
from RUFAS.data_structures.animal_to_manure_connection import ManureStream, PenManureData, StreamType
from RUFAS.general_constants import GeneralConstants
from RUFAS.output_manager import OutputManager
from RUFAS.rufas_time import RufasTime
from RUFAS.units import MeasurementUnits
from RUFAS.user_constants import UserConstants


@pytest.mark.parametrize(
    "reference_variable_name, reference_variable_value, actual_variable_name, current_actual_variable_value,"
    "actual_variable_value_to_add, simulation_day,expected_num_add_variable_calls",
    [
        ("ref_variable", [1, 2, 3, 4, 5], "dummy_variable", [2], 2, 1, 3),
        ("ref_variable", [1, 2, 3], "dummy_variable", [1, 2, 3], 2, 2, 0),
        ("ref_variable", [1, 2, 3], "dummy_variable", [], 2, 2, 2),
        ("ref_variable", [1, 2, 3], "dummy_variable", [1, 2, 3], 2, 0, 0),
    ],
)
def test_data_padder(
    reference_variable_name: str,
    reference_variable_value: list[Any],
    actual_variable_name: str,
    current_actual_variable_value: list[Any],
    actual_variable_value_to_add: Any,
    simulation_day: int,
    expected_num_add_variable_calls: int,
    mocker: MockerFixture,
) -> None:
    """Unit test for data_padder()"""
    om = OutputManager()
    mock_om_add_variable = mocker.patch.object(om, "add_variable")
    om.variables_pool = {
        reference_variable_name: {"values": reference_variable_value},
    }
    if current_actual_variable_value:
        om.variables_pool[actual_variable_name] = {"values": current_actual_variable_value}

    AnimalModuleReporter.data_padder(
        reference_variable_name,
        actual_variable_name,
        actual_variable_value_to_add,
        simulation_day,
        info_map={},
        units={},
    )

    assert mock_om_add_variable.call_count == expected_num_add_variable_calls


def test_report_milk(mocker: MockerFixture) -> None:
    """Unit test for report_milk()"""
    simulation_day = 10
    om = OutputManager()
    mock_om_add_variable = mocker.patch.object(om, "add_variable")
    milk_reports = [
        MilkProductionStatistics(
            cow_id=1,
            pen_id=1,
            days_in_milk=10,
            estimated_daily_milk_produced=88.8,
            milk_protein=12.3,
            milk_fat=3.4,
            milk_lactose=5.6,
            parity=1,
        ),
        MilkProductionStatistics(
            cow_id=2,
            pen_id=5,
            days_in_milk=435,
            estimated_daily_milk_produced=128.14,
            milk_protein=1.9,
            milk_fat=73,
            milk_lactose=7.9,
            parity=5,
        ),
        MilkProductionStatistics(
            cow_id=12345,
            pen_id=54321,
            days_in_milk=0,
            estimated_daily_milk_produced=0,
            milk_protein=0,
            milk_fat=0,
            milk_lactose=0,
            parity=2,
        ),
    ]

    info_map = {
        "class": AnimalModuleReporter.__name__,
        "function": AnimalModuleReporter.report_milk.__name__,
        "data_origin": [("MilkProduction", "perform_daily_milking_update")],
        "units": MilkProductionStatistics.UNITS,
    }
    expected_add_variable_calls = [
        call(
            "milk_data_at_milk_update",
            {
                "cow_id": 1,
                "pen_id": 1,
                "days_in_milk": 10,
                "estimated_daily_milk_produced": 88.8,
                "milk_protein": 12.3,
                "milk_fat": 3.4,
                "milk_lactose": 5.6,
                "parity": 1,
                "is_milking": True,
                "simulation_day": simulation_day,
            },
            info_map,
        ),
        call(
            "milk_data_at_milk_update",
            {
                "cow_id": 2,
                "pen_id": 5,
                "days_in_milk": 435,
                "estimated_daily_milk_produced": 128.14,
                "milk_protein": 1.9,
                "milk_fat": 73,
                "milk_lactose": 7.9,
                "parity": 5,
                "is_milking": True,
                "simulation_day": simulation_day,
            },
            info_map,
        ),
        call(
            "milk_data_at_milk_update",
            {
                "cow_id": 12345,
                "pen_id": 54321,
                "days_in_milk": 0,
                "estimated_daily_milk_produced": 0,
                "milk_protein": 0,
                "milk_fat": 0,
                "milk_lactose": 0,
                "parity": 2,
                "is_milking": False,
                "simulation_day": simulation_day,
            },
            info_map,
        ),
    ]
    AnimalModuleReporter.report_milk(milk_reports, simulation_day)
    assert mock_om_add_variable.call_args_list == expected_add_variable_calls


def test_ration_per_animal(mocker: MockerFixture) -> None:
    """Unit test for report_ration_per_animal()"""
    om = OutputManager()
    mock_om_add_variable = mocker.patch.object(om, "add_variable")
    AnimalModuleReporter.report_ration_per_animal(
        pen_base_name="0_CALF",
        ration_per_animal={1: 1.1, 2: 2.2, 3: 3.3},
        total_dry_matter=6.6,
        num_animals=8,
        simulation_day=10,
    )
    mock_om_add_variable.assert_called_once_with(
        "ration_per_animal_for_0_CALF",
        {"1": 1.1, "2": 2.2, "3": 3.3, "dry_matter_intake_total": 6.6},
        {
            "class": AnimalModuleReporter.__name__,
            "function": AnimalModuleReporter.report_ration_per_animal.__name__,
            "simulation_day": 10,
            "number_animals_in_pen": 8,
            "units": {
                "1": MeasurementUnits.KILOGRAMS,
                "2": MeasurementUnits.KILOGRAMS,
                "3": MeasurementUnits.KILOGRAMS,
                "dry_matter_intake_total": MeasurementUnits.KILOGRAMS,
            },
        },
    )


def test_report_nutrient_amounts(mocker: MockerFixture) -> None:
    """Unit test for report_nutrient_amounts()"""
    om = OutputManager()
    mock_om_add_variable = mocker.patch.object(om, "add_variable")
    average_nutrition_supply = NutritionSupply(
        metabolizable_energy=1.1,
        maintenance_energy=2.2,
        lactation_energy=3.3,
        growth_energy=4.4,
        metabolizable_protein=5.5,
        calcium=6.6,
        phosphorus=7.7,
        dry_matter=8.8,
        wet_matter=9.9,
        ndf_supply=10.1,
        forage_ndf_supply=1.1,
        fat_supply=2.2,
        crude_protein=3.3,
        adf_supply=4.4,
        digestible_energy_supply=5.5,
        tdn_supply=6.6,
        lignin_supply=7.7,
        ash_supply=8.8,
        potassium_supply=9.9,
        starch_supply=10.1,
        byproduct_supply=1.1,
    )
    expected_reported_nutrient_amounts = {
        "dm": 8.8,
        "CP": 3.3,
        "ADF": 4.4,
        "NDF": 10.1,
        "lignin": 7.7,
        "ash": 8.8,
        "phosphorus": 7.7 * GeneralConstants.GRAMS_TO_KG,
        "potassium": 9.9,
        "N": 3.3 * UserConstants.PROTEIN_TO_NITROGEN,
        "as_fed": 9.9,
        "EE": 2.2,
        "starch": 10.1,
        "TDN": 6.6,
        "DE": 5.5,
        "calcium": 6.6 * GeneralConstants.GRAMS_TO_KG,
        "fat": 2.2 * GeneralConstants.KG_TO_GRAMS,
        "fat_percentage": 25.0,
        "forage_ndf": 1.1,
        "forage_ndf_percent": 12.5,
        "ME": 1.1,
        "NE_maintenance_and_activity": 2.2,
        "NE_lactation": 3.3,
        "NE_growth": 4.4,
        "metabolizable_protein": 5.5,
    }

    AnimalModuleReporter.report_nutrient_amounts("0_CALF", average_nutrition_supply, 10, 8)
    mock_om_add_variable.assert_called_once_with(
        "ration_nutrient_amount_for_0_CALF",
        expected_reported_nutrient_amounts,
        {
            "class": AnimalModuleReporter.__name__,
            "function": AnimalModuleReporter.report_nutrient_amounts.__name__,
            "simulation_day": 8,
            "units": NutritionSupply.UNITS,
            "number_animals_in_pen": 10,
        },
    )


def test_report_average_nutrient_requirements(mocker: MockerFixture) -> None:
    """Unit test for report_average_nutrient_requirements()"""
    om = OutputManager()
    mock_om_add_variable = mocker.patch.object(om, "add_variable")

    average_body_weight = 188.8
    average_milk_production_reduction = 1.1
    average_nutrition_requirements = NutritionRequirements(
        maintenance_energy=1.1,
        growth_energy=2.2,
        pregnancy_energy=3.3,
        lactation_energy=4.4,
        metabolizable_protein=5.5,
        calcium=6.6,
        phosphorus=7.7,
        process_based_phosphorus=8.8,
        dry_matter=9.9,
        activity_energy=10.1,
        essential_amino_acids=EssentialAminoAcidRequirements(
            histidine=11.1,
            isoleucine=12.2,
            leucine=13.3,
            lysine=14.4,
            methionine=15.5,
            phenylalanine=16.6,
            threonine=17.7,
            thryptophan=18.8,
            valine=19.9,
        ),
    )
    expected_reported_average_nutrient_requirements = {
        "NEmaint_requirement": 1.1,
        "NEa_requirement": 10.1,
        "NEg_requirement": 2.2,
        "NEpreg_requirement": 3.3,
        "NEl_requirement": 4.4,
        "MP_requirement": 5.5,
        "Ca_requirement": 6.6,
        "P_req": 7.7,
        "P_req_process": 8.8,
        "DMIest_requirement": 9.9,
        "avg_BW": average_body_weight,
        "avg_milk_production_reduction_pen": average_milk_production_reduction,
        "avg_essential_amino_acid_requirement": EssentialAminoAcidRequirements(
            histidine=11.1,
            isoleucine=12.2,
            leucine=13.3,
            lysine=14.4,
            methionine=15.5,
            phenylalanine=16.6,
            threonine=17.7,
            thryptophan=18.8,
            valine=19.9,
        ),
    }
    AnimalModuleReporter.report_average_nutrient_requirements(
        "0_CALF", average_nutrition_requirements, average_body_weight, average_milk_production_reduction, 10, 8
    )
    mock_om_add_variable.assert_called_once_with(
        "avg_rqmts_for_0_CALF",
        expected_reported_average_nutrient_requirements,
        {
            "class": AnimalModuleReporter.__name__,
            "function": AnimalModuleReporter.report_average_nutrient_requirements.__name__,
            "number_animals_in_pen": 10,
            "simulation_day": 8,
            "units": NutritionRequirements.UNITS,
        },
    )


def test_report_average_nutrient_evaluation_results(mocker: MockerFixture) -> None:
    """Unit test for report_average_nutrient_evaluation_results()"""
    om = OutputManager()
    mock_om_add_variable = mocker.patch.object(om, "add_variable")
    average_nutrition_evaluation = NutritionEvaluationResults(
        total_energy=1.1,
        maintenance_energy=1.1,
        lactation_energy=4.4,
        growth_energy=2.2,
        metabolizable_protein=5.5,
        calcium=6.6,
        phosphorus=7.7,
        dry_matter=8.8,
        ndf_percent=9.9,
        forage_ndf_percent=10.1,
        fat_percent=11.2,
    )
    expected_reported_average_nutrient_evaluation_results = {
        "total_energy_difference": 1.1,
        "maintenance_energy_difference": 1.1,
        "lactation_energy_difference": 4.4,
        "growth_energy_difference": 2.2,
        "metabolizable_protein_difference": 5.5,
        "calcium_difference": 6.6,
        "phosphorus_difference": 7.7,
        "dry_matter_difference": 8.8,
        "ndf_percent_difference": 9.9,
        "forage_ndf_percent_difference": 10.1,
        "fat_percent_difference": 11.2,
    }

    AnimalModuleReporter.report_average_nutrient_evaluation_results("0_CALF", average_nutrition_evaluation, 10)
    assert mock_om_add_variable.call_args_list == [
        call(
            "avg_eval_results_for_0_CALF",
            expected_reported_average_nutrient_evaluation_results,
            {
                "class": AnimalModuleReporter.__name__,
                "function": AnimalModuleReporter.report_average_nutrient_evaluation_results.__name__,
                "simulation_day": 10,
                "units": NutritionEvaluationResults.UNITS,
            },
        ),
        call(
            "avg_eval_report_for_0_CALF",
            average_nutrition_evaluation.report,
            {
                "class": AnimalModuleReporter.__name__,
                "function": AnimalModuleReporter.report_average_nutrient_evaluation_results.__name__,
                "simulation_day": 10,
                "units": NutritionEvaluationResults.REPORT_UNITS,
            },
        ),
    ]


def test_report_me_diet(mocker: MockerFixture) -> None:
    """Unit test for report_me_diet()"""
    om = OutputManager()
    mock_om_add_variable = mocker.patch.object(om, "add_variable")
    AnimalModuleReporter.report_me_diet("0_CALF", 10, 8, 12)
    mock_om_add_variable.assert_called_once_with(
        "MEdiet_for_0_CALF",
        10,
        {
            "class": AnimalModuleReporter.__name__,
            "function": AnimalModuleReporter.report_me_diet.__name__,
            "number_animals_in_pen": 8,
            "simulation_day": 12,
            "units": MeasurementUnits.MEGACALORIES,
        },
    )


def test_report_daily_herd_total_ration(mocker: MockerFixture) -> None:
    """Unit test for report_daily_herd_total_ration()"""
    om = OutputManager()
    mock_om_add_variable = mocker.patch.object(om, "add_variable")

    herd_total_ration = {
        "1": 1.1,
        "2": 2.2,
        "3": 3.3,
        "4": 4.4,
        "5": 5.5,
        "6": 6.6,
    }
    units = {key: MeasurementUnits.KILOGRAMS for key in herd_total_ration.keys()}
    AnimalModuleReporter.report_daily_herd_total_ration(herd_total_ration, 10)
    mock_om_add_variable.assert_called_once_with(
        "ration_daily_feed_total_across_pens",
        herd_total_ration,
        {
            "class": AnimalModuleReporter.__name__,
            "function": AnimalModuleReporter.report_daily_herd_total_ration.__name__,
            "simulation_day": 10,
            "units": units,
        },
    )


def test_report_daily_ration_per_pen(mocker: MockerFixture) -> None:
    """Unit test for report_daily_ration_per_pen()"""
    om = OutputManager()
    mock_om_add_variable = mocker.patch.object(om, "add_variable")
    pen_ration = {
        "1": 1.1,
        "2": 2.2,
        "3": 3.3,
    }

    AnimalModuleReporter.report_daily_ration_per_pen("0", "CALF", pen_ration, 10)

    mock_om_add_variable.assert_called_once_with(
        "ration_daily_feed_totals_for_pen_0_CALF",
        pen_ration,
        {
            "class": AnimalModuleReporter.__name__,
            "function": AnimalModuleReporter.report_daily_ration_per_pen.__name__,
            "simulation_day": 10,
            "units": {key: MeasurementUnits.KILOGRAMS for key in pen_ration.keys()},
        },
    )


def test_report_enteric_methane_emission(mocker: MockerFixture) -> None:
    """Unit test for report_enteric_methane_emission()"""
    om = OutputManager()
    mock_om_add_variable = mocker.patch.object(om, "add_variable")
    emission = {"pen1": 1000.0}

    AnimalModuleReporter.report_enteric_methane_emission(emission)

    mock_om_add_variable.assert_called_once()


def test_report_manure_streams_key_error(mocker: MockerFixture) -> None:
    """Unit test for report_manure_streams() when the input has the wrong key"""
    om = OutputManager()
    mock_om_add_variable = mocker.patch.object(om, "add_variable")
    mock_om_add_error = mocker.patch.object(om, "add_error")

    manure_stream = ManureStream(
        water=1.1,
        ammoniacal_nitrogen=2.2,
        nitrogen=3.3,
        phosphorus=4.4,
        potassium=5.5,
        ash=6.6,
        non_degradable_volatile_solids=7.7,
        degradable_volatile_solids=8.8,
        total_solids=66.6,
        volume=9.9,
        methane_production_potential=10.1,
        pen_manure_data=PenManureData(
            num_animals=8,
            manure_deposition_surface_area=23.3,
            animal_combination=AnimalCombination.CALF,
            pen_type="",
            manure_urine_mass=1.1,
            manure_urine_nitrogen=2.2,
            stream_type=StreamType.GENERAL,
            total_bedding_mass=3.3,
            total_bedding_volume=4.4,
        ),
        bedding_non_degradable_volatile_solids=10,
    )
    manure_streams = {
        "stream_1": manure_stream,
    }
    manure_stream_dict = asdict(manure_stream)
    manure_stream_dict["total_volatile_solids"] = manure_stream.total_volatile_solids
    manure_stream_dict["mass"] = manure_stream.mass
    manure_stream_dict["total_bedding_mass"] = manure_stream.pen_manure_data.total_bedding_mass
    manure_stream_dict["total_bedding_volume"] = manure_stream.pen_manure_data.total_bedding_volume

    original_manure_stream_units = ManureStream.MANURE_STREAM_UNITS.copy()
    del ManureStream.MANURE_STREAM_UNITS["mass"]

    with pytest.raises(ValueError):
        AnimalModuleReporter.report_manure_streams(manure_streams, 10)

        mock_om_add_error.assert_called_once_with(
            "Manure Stream Keys Error",
            f"Expected keys: {set(original_manure_stream_units.keys())}, "
            f"received: {set(manure_stream_dict.keys())}.",
            {
                "class": AnimalModuleReporter.__name__,
                "function": AnimalModuleReporter.report_manure_streams.__name__,
                "data_origin": [("HerdManager", "daily_routines")],
                "simulation_day": 10,
            },
        )
        mock_om_add_variable.assert_not_called()
    ManureStream.MANURE_STREAM_UNITS = original_manure_stream_units


def test_report_manure_streams_stream_type_error(mocker: MockerFixture) -> None:
    """Unit test for report_manure_streams() when the input has the wrong data type."""
    om = OutputManager()
    mock_om_add_variable = mocker.patch.object(om, "add_variable")
    mock_om_add_error = mocker.patch.object(om, "add_error")
    manure_streams = {
        "stream_1": MagicMock(),
        "stream_2": MagicMock(),
        "stream_3": MagicMock(),
        "stream_4": MagicMock(),
    }

    with pytest.raises(ValueError):
        AnimalModuleReporter.report_manure_streams(manure_streams, 10)

        mock_om_add_error.assert_called_once_with(
            "Manure Stream Type Error",
            "This function requires either a ManureStream instance or a dictionary.",
            {
                "class": AnimalModuleReporter.__name__,
                "function": AnimalModuleReporter.report_manure_streams.__name__,
                "data_origin": [("HerdManager", "daily_routines")],
                "simulation_day": 10,
            },
        )
        mock_om_add_variable.assert_not_called()


def test_report_manure_streams_no_pen_manure(mocker: MockerFixture) -> None:
    """Unit test for report_manure_streams() when the input has no pen manure data."""
    om = OutputManager()
    mock_om_add_variable = mocker.patch.object(om, "add_variable")

    manure_stream = ManureStream(
        water=1.1,
        ammoniacal_nitrogen=2.2,
        nitrogen=3.3,
        phosphorus=4.4,
        potassium=5.5,
        ash=6.6,
        non_degradable_volatile_solids=7.7,
        degradable_volatile_solids=8.8,
        total_solids=66.6,
        volume=9.9,
        methane_production_potential=10.1,
        pen_manure_data=None,
        bedding_non_degradable_volatile_solids=10,
    )
    manure_streams = {
        "stream_1": manure_stream,
    }

    with pytest.raises(ValueError):
        AnimalModuleReporter.report_manure_streams(manure_streams, 10)
        mock_om_add_variable.assert_not_called()


def test_report_manure_streams(mocker: MockerFixture) -> None:
    """Unit test for report_manure_streams()"""
    om = OutputManager()
    mock_om_add_variable = mocker.patch.object(om, "add_variable")
    manure_streams = {
        "stream_1": ManureStream(
            water=1.1,
            ammoniacal_nitrogen=2.2,
            nitrogen=3.3,
            phosphorus=4.4,
            potassium=5.5,
            ash=6.6,
            non_degradable_volatile_solids=7.7,
            degradable_volatile_solids=8.8,
            total_solids=66.6,
            volume=9.9,
            methane_production_potential=10.1,
            pen_manure_data=PenManureData(
                num_animals=8,
                manure_deposition_surface_area=23.3,
                animal_combination=AnimalCombination.CALF,
                pen_type="",
                manure_urine_mass=1.1,
                manure_urine_nitrogen=2.2,
                stream_type=StreamType.GENERAL,
                total_bedding_mass=3.3,
                total_bedding_volume=4.4,
            ),
            bedding_non_degradable_volatile_solids=10.0,
        ),
        "stream_2": ManureStream(
            water=1.1,
            ammoniacal_nitrogen=2.2,
            nitrogen=3.3,
            phosphorus=4.4,
            potassium=5.5,
            ash=6.6,
            non_degradable_volatile_solids=7.7,
            degradable_volatile_solids=8.8,
            total_solids=66.6,
            volume=9.9,
            methane_production_potential=10.1,
            pen_manure_data=PenManureData(
                num_animals=8,
                manure_deposition_surface_area=23.3,
                animal_combination=AnimalCombination.CALF,
                pen_type="",
                manure_urine_mass=1.1,
                manure_urine_nitrogen=2.2,
                stream_type=StreamType.GENERAL,
                total_bedding_mass=3.3,
                total_bedding_volume=4.4,
            ),
            bedding_non_degradable_volatile_solids=10,
        ),
        "stream_3": ManureStream(
            water=2.1,
            ammoniacal_nitrogen=3.2,
            nitrogen=4.3,
            phosphorus=5.4,
            potassium=6.5,
            ash=7.6,
            non_degradable_volatile_solids=8.7,
            degradable_volatile_solids=9.8,
            total_solids=77.7,
            volume=10.9,
            methane_production_potential=11.1,
            pen_manure_data=PenManureData(
                num_animals=12,
                manure_deposition_surface_area=33.3,
                animal_combination=AnimalCombination.GROWING,
                pen_type="",
                manure_urine_mass=2.1,
                manure_urine_nitrogen=3.2,
                stream_type=StreamType.GENERAL,
                total_bedding_mass=3.3,
                total_bedding_volume=4.4,
            ),
            bedding_non_degradable_volatile_solids=10,
        ),
        "stream_4": ManureStream(
            water=3.1,
            ammoniacal_nitrogen=4.2,
            nitrogen=5.3,
            phosphorus=6.4,
            potassium=7.5,
            ash=8.6,
            non_degradable_volatile_solids=9.7,
            degradable_volatile_solids=10.8,
            total_solids=88.8,
            volume=11.9,
            methane_production_potential=12.1,
            pen_manure_data=PenManureData(
                num_animals=16,
                manure_deposition_surface_area=43.3,
                animal_combination=AnimalCombination.CLOSE_UP,
                pen_type="",
                manure_urine_mass=3.1,
                manure_urine_nitrogen=4.2,
                stream_type=StreamType.GENERAL,
                total_bedding_mass=3.3,
                total_bedding_volume=4.4,
            ),
            bedding_non_degradable_volatile_solids=10,
        ),
    }

    AnimalModuleReporter.report_manure_streams(manure_streams, 10)

    assert mock_om_add_variable.call_count == 16 * len(manure_streams)


def test_report_manure_excretions(mocker: MockerFixture) -> None:
    """Unit test for report_manure_excretions()"""
    om = OutputManager()
    mock_om_add_variable = mocker.patch.object(om, "add_variable")
    mock_data_padder = mocker.patch.object(AnimalModuleReporter, "data_padder")

    dummy_manure_excretion_data = AnimalManureExcretions(
        urea=1.1,
        urine=2.2,
        urine_nitrogen=3.3,
        manure_nitrogen=4.4,
        manure_total_ammoniacal_nitrogen=5.5,
        manure_mass=6.6,
        total_solids=7.7,
        degradable_volatile_solids=8.8,
        non_degradable_volatile_solids=9.9,
        inorganic_phosphorus_fraction=1.1,
        organic_phosphorus_fraction=2.2,
        non_water_inorganic_phosphorus_fraction=3.3,
        non_water_organic_phosphorus_fraction=4.4,
        phosphorus=5.5,
        phosphorus_fraction=6.6,
        potassium=7.7,
    )
    manure_excretions_by_pen: dict[str, AnimalManureExcretions] = {
        "0_CALF": dummy_manure_excretion_data,
        "1_GROWING": dummy_manure_excretion_data,
        "2_CLOSEUP": dummy_manure_excretion_data,
        "3_LAC_COW": dummy_manure_excretion_data,
    }

    AnimalModuleReporter.report_manure_excretions(manure_excretions_by_pen, 10)

    assert mock_data_padder.call_count == 16 * len(manure_excretions_by_pen)
    assert mock_om_add_variable.call_count == 16 * len(manure_excretions_by_pen)


def test_report_herd_statistics_data(mocker: MockerFixture) -> None:
    """Unit test for report_herd_statistics_data()"""
    om = OutputManager()
    mock_om_add_variable = mocker.patch.object(om, "add_variable")

    AnimalModuleReporter.report_herd_statistics_data(HerdStatistics(), 10)

    assert mock_om_add_variable.call_count == 57


def test_report_daily_pen_total(mocker: MockerFixture) -> None:
    """Unit test for report_daily_pen_total()"""
    om = OutputManager()
    mock_om_add_variable = mocker.patch.object(om, "add_variable")
    mock_data_padder = mocker.patch.object(AnimalModuleReporter, "data_padder")

    AnimalModuleReporter.report_daily_pen_total("1", "GROWING", 8, 10)

    mock_data_padder.assert_called_once_with(
        "AnimalModuleReporter.report_daily_pen_total.number_of_animals_in_pen_0_CALF",
        "AnimalModuleReporter.report_daily_pen_total.number_of_animals_in_pen_1_GROWING",
        0,
        10,
        info_map := {
            "class": AnimalModuleReporter.__name__,
            "function": AnimalModuleReporter.report_daily_pen_total.__name__,
            "units": MeasurementUnits.ANIMALS,
            "simulation_day": 10,
        },
        MeasurementUnits.ANIMALS,
    )
    mock_om_add_variable.assert_called_once_with("number_of_animals_in_pen_1_GROWING", 8, info_map)


def test_report_sold_animal_information(mocker: MockerFixture) -> None:
    """Unit test for report_sold_animal_information()"""
    om = OutputManager()
    mock_om_add_variable = mocker.patch.object(om, "add_variable")

    herd_statistics = HerdStatistics()
    herd_statistics.sold_calves_info = [
        SoldAnimalTypedDict(
            id=1,
            animal_type="Calf",
            sold_at_day=123,
            body_weight=456.78,
            cull_reason="NA",
            days_in_milk="NA",
            parity="NA",
        ),
        SoldAnimalTypedDict(
            id=2,
            animal_type="Calf",
            sold_at_day=123,
            body_weight=456.78,
            cull_reason="NA",
            days_in_milk="NA",
            parity="NA",
        ),
        SoldAnimalTypedDict(
            id=3,
            animal_type="Calf",
            sold_at_day=123,
            body_weight=456.78,
            cull_reason="NA",
            days_in_milk="NA",
            parity="NA",
        ),
    ]
    herd_statistics.sold_heiferIIs_info = [
        SoldAnimalTypedDict(
            id=4,
            animal_type="HeiferII",
            sold_at_day=123,
            body_weight=456.78,
            cull_reason="NA",
            days_in_milk="NA",
            parity="NA",
        ),
        SoldAnimalTypedDict(
            id=5,
            animal_type="HeiferII",
            sold_at_day=123,
            body_weight=456.78,
            cull_reason="NA",
            days_in_milk="NA",
            parity="NA",
        ),
        SoldAnimalTypedDict(
            id=6,
            animal_type="HeiferII",
            sold_at_day=123,
            body_weight=456.78,
            cull_reason="NA",
            days_in_milk="NA",
            parity="NA",
        ),
    ]
    herd_statistics.sold_heiferIIIs_info = [
        SoldAnimalTypedDict(
            id=7,
            animal_type="HeiferIII",
            sold_at_day=123,
            body_weight=456.78,
            cull_reason="NA",
            days_in_milk="NA",
            parity="NA",
        ),
        SoldAnimalTypedDict(
            id=8,
            animal_type="HeiferIII",
            sold_at_day=123,
            body_weight=456.78,
            cull_reason="NA",
            days_in_milk="NA",
            parity="NA",
        ),
        SoldAnimalTypedDict(
            id=9,
            animal_type="HeiferIII",
            sold_at_day=123,
            body_weight=456.78,
            cull_reason="NA",
            days_in_milk="NA",
            parity="NA",
        ),
    ]
    herd_statistics.sold_and_died_cows_info = [
        SoldAnimalTypedDict(
            id=10,
            animal_type="LacCow",
            sold_at_day=123,
            body_weight=456.78,
            cull_reason=animal_constants.UDDER_CULL,
            days_in_milk=18,
            parity=2,
        ),
        SoldAnimalTypedDict(
            id=11,
            animal_type="LacCow",
            sold_at_day=123,
            body_weight=456.78,
            cull_reason=animal_constants.DEATH_CULL,
            days_in_milk=88,
            parity=1,
        ),
        SoldAnimalTypedDict(
            id=12,
            animal_type="DryCow",
            sold_at_day=123,
            body_weight=456.78,
            cull_reason=animal_constants.LAMENESS_CULL,
            days_in_milk=0,
            parity=3,
        ),
    ]

    AnimalModuleReporter.report_sold_animal_information(herd_statistics)
    assert mock_om_add_variable.call_count == 11 * 7


def test_report_stillborn_calves_information(mocker: MockerFixture) -> None:
    """Unit test for report_stillborn_calves_information()"""
    om = OutputManager()
    mock_om_add_variable = mocker.patch.object(om, "add_variable")

    total_days = 188
    stillborn_calves = [
        StillbornCalfTypedDict(id=1, stillborn_day=0, birth_weight=23.3),
        StillbornCalfTypedDict(id=2, stillborn_day=0, birth_weight=23.3),
        StillbornCalfTypedDict(id=3, stillborn_day=0, birth_weight=23.3),
        StillbornCalfTypedDict(id=4, stillborn_day=1, birth_weight=23.3),
        StillbornCalfTypedDict(id=5, stillborn_day=5, birth_weight=23.3),
        StillbornCalfTypedDict(id=6, stillborn_day=7, birth_weight=23.3),
        StillbornCalfTypedDict(id=7, stillborn_day=18, birth_weight=23.3),
        StillbornCalfTypedDict(id=8, stillborn_day=23, birth_weight=23.3),
        StillbornCalfTypedDict(id=9, stillborn_day=23, birth_weight=23.3),
        StillbornCalfTypedDict(id=10, stillborn_day=188, birth_weight=23.3),
    ]
    AnimalModuleReporter.report_stillborn_calves_information(stillborn_calves, "stillborn_calves", total_days)
    mock_om_add_variable.assert_has_calls(
        [
            call(
                "stillborn_calves_first_stillborn_event",
                0,
                {
                    "class": AnimalModuleReporter.__name__,
                    "function": AnimalModuleReporter.report_stillborn_calves_information.__name__,
                    "units": MeasurementUnits.SIMULATION_DAY,
                },
            ),
            call(
                "stillborn_calves_last_stillborn_event",
                188,
                {
                    "class": AnimalModuleReporter.__name__,
                    "function": AnimalModuleReporter.report_stillborn_calves_information.__name__,
                    "units": MeasurementUnits.SIMULATION_DAY,
                },
            ),
        ]
    )
    assert mock_om_add_variable.call_count == 2 + (total_days + 1) * 2


def test_report_sold_animal_information_sort_by_sell_day(mocker: MockerFixture) -> None:
    """Unit test for report_sold_animal_information_sort_by_sell_day()"""
    om = OutputManager()
    mock_om_add_variable = mocker.patch.object(om, "add_variable")

    total_days = 188
    sold_animals = [
        SoldAnimalTypedDict(
            id=1, animal_type="Calf", sold_at_day=0, body_weight=23.3, cull_reason="NA", days_in_milk="NA", parity="NA"
        ),
        SoldAnimalTypedDict(
            id=2, animal_type="Calf", sold_at_day=0, body_weight=23.3, cull_reason="NA", days_in_milk="NA", parity="NA"
        ),
        SoldAnimalTypedDict(
            id=3,
            animal_type="HeiferI",
            sold_at_day=0,
            body_weight=23.3,
            cull_reason="NA",
            days_in_milk="NA",
            parity="NA",
        ),
        SoldAnimalTypedDict(
            id=4,
            animal_type="HeiferI",
            sold_at_day=1,
            body_weight=23.3,
            cull_reason="NA",
            days_in_milk="NA",
            parity="NA",
        ),
        SoldAnimalTypedDict(
            id=5,
            animal_type="HeiferII",
            sold_at_day=5,
            body_weight=23.3,
            cull_reason="NA",
            days_in_milk="NA",
            parity="NA",
        ),
        SoldAnimalTypedDict(
            id=6,
            animal_type="HeiferIII",
            sold_at_day=7,
            body_weight=23.3,
            cull_reason="NA",
            days_in_milk="NA",
            parity="NA",
        ),
        SoldAnimalTypedDict(
            id=7,
            animal_type="HeiferIII",
            sold_at_day=18,
            body_weight=23.3,
            cull_reason="NA",
            days_in_milk="NA",
            parity="NA",
        ),
        SoldAnimalTypedDict(
            id=8,
            animal_type="HeiferIII",
            sold_at_day=23,
            body_weight=23.3,
            cull_reason="NA",
            days_in_milk="NA",
            parity="NA",
        ),
        SoldAnimalTypedDict(
            id=9, animal_type="LacCow", sold_at_day=23, body_weight=23.3, cull_reason="NA", days_in_milk=10, parity=2
        ),
        SoldAnimalTypedDict(
            id=10, animal_type="DryCow", sold_at_day=23, body_weight=23.3, cull_reason="NA", days_in_milk=0, parity=1
        ),
    ]
    AnimalModuleReporter.report_sold_animal_information_sort_by_sell_day(sold_animals, "dummy", total_days)
    mock_om_add_variable.assert_has_calls(
        [
            call(
                "dummy_first_sell_event",
                1,
                {
                    "class": AnimalModuleReporter.__name__,
                    "function": AnimalModuleReporter.report_sold_animal_information_sort_by_sell_day.__name__,
                    "units": MeasurementUnits.SIMULATION_DAY,
                },
            ),
            call(
                "dummy_last_sell_event",
                23,
                {
                    "class": AnimalModuleReporter.__name__,
                    "function": AnimalModuleReporter.report_sold_animal_information_sort_by_sell_day.__name__,
                    "units": MeasurementUnits.SIMULATION_DAY,
                },
            ),
        ]
    )
    assert mock_om_add_variable.call_count == 2 + (total_days + 1) * 2


def test_report_305d_milk(mocker: MockerFixture) -> None:
    """Unit test for report_305d_milk()"""
    om = OutputManager()
    mock_om_add_variable = mocker.patch.object(om, "add_variable")

    AnimalModuleReporter.report_305d_milk(101.11)

    mock_om_add_variable.assert_called_once_with(
        "milk_production_305days_herd_mean",
        101.11,
        {
            "class": AnimalModuleReporter.__name__,
            "function": AnimalModuleReporter.report_305d_milk.__name__,
            "data_origin": [("MilkProduction", "perform_daily_milking_update")],
            "units": MeasurementUnits.KILOGRAMS,
        },
    )


def test_report_end_of_simulation_empty_sold_animal_info(mocker: MockerFixture) -> None:
    """Unit test for report_end_of_simulation() with no sold animals"""
    mock_report_sold_animal_information = mocker.patch.object(AnimalModuleReporter, "report_sold_animal_information")
    mock_report_sold_animal_information_sort_by_sell_day = mocker.patch.object(
        AnimalModuleReporter, "report_sold_animal_information_sort_by_sell_day"
    )
    mock_report_stillborn_calves_information = mocker.patch.object(
        AnimalModuleReporter, "report_stillborn_calves_information"
    )
    mock_record_animal_events = mocker.patch.object(AnimalModuleReporter, "_record_animal_events")
    mock_record_heiferIIs_conception_rate = mocker.patch.object(
        AnimalModuleReporter, "_record_heiferIIs_conception_rate"
    )
    mock_record_cows_conception_rate = mocker.patch.object(AnimalModuleReporter, "_record_cows_conception_rate")

    AnimalModuleReporter.report_end_of_simulation(
        herd_statistics := HerdStatistics(),
        herd_reproduction_statistics := HerdReproductionStatistics(),
        mock_time := MagicMock(auto_spec=RufasTime),
        {},
        {},
    )

    mock_report_sold_animal_information.assert_called_once_with(herd_statistics)
    empty_sold_animals = [{"sold_at_day": 0, "body_weight": 0}]
    assert mock_report_sold_animal_information_sort_by_sell_day.call_args_list == [
        call(empty_sold_animals, report_name, mock_time.simulation_day)
        for report_name in ["sold_calves", "heiferII", "heiferIII", "sold_and_died_cows", "sold_cows"]
    ]
    mock_report_stillborn_calves_information.assert_called_once_with(
        [{"stillborn_day": 0, "birth_weight": 0}], "stillborn_calves", mock_time.simulation_day
    )
    assert mock_record_animal_events.call_args_list == [
        call({}, mock_time.simulation_day),
        call({}, mock_time.simulation_day),
    ]
    mock_record_heiferIIs_conception_rate.assert_called_once_with(herd_reproduction_statistics)
    mock_record_cows_conception_rate.assert_called_once_with(herd_reproduction_statistics)


def test_report_end_of_simulation(mocker: MockerFixture) -> None:
    """Unit test for report_end_of_simulation()"""
    mock_report_sold_animal_information = mocker.patch.object(AnimalModuleReporter, "report_sold_animal_information")
    mock_report_sold_animal_information_sort_by_sell_day = mocker.patch.object(
        AnimalModuleReporter, "report_sold_animal_information_sort_by_sell_day"
    )
    mock_report_stillborn_calves_information = mocker.patch.object(
        AnimalModuleReporter, "report_stillborn_calves_information"
    )
    mock_record_animal_events = mocker.patch.object(AnimalModuleReporter, "_record_animal_events")
    mock_record_heiferIIs_conception_rate = mocker.patch.object(
        AnimalModuleReporter, "_record_heiferIIs_conception_rate"
    )
    mock_record_cows_conception_rate = mocker.patch.object(AnimalModuleReporter, "_record_cows_conception_rate")

    herd_statistics = HerdStatistics()
    herd_statistics.sold_calves_info = [
        SoldAnimalTypedDict(
            id=1, animal_type="Calf", sold_at_day=0, body_weight=23.3, cull_reason="NA", days_in_milk="NA", parity="NA"
        )
    ]
    herd_statistics.sold_heiferIIs_info = [
        SoldAnimalTypedDict(
            id=1,
            animal_type="Heifer",
            sold_at_day=0,
            body_weight=23.3,
            cull_reason="NA",
            days_in_milk="NA",
            parity="NA",
        )
    ]
    herd_statistics.sold_heiferIIIs_info = [
        SoldAnimalTypedDict(
            id=1,
            animal_type="Heifer",
            sold_at_day=0,
            body_weight=23.3,
            cull_reason="NA",
            days_in_milk="NA",
            parity="NA",
        )
    ]
    herd_statistics.sold_cows_info = [
        SoldAnimalTypedDict(
            id=1,
            animal_type="LacCow",
            sold_at_day=0,
            body_weight=23.3,
            cull_reason="NA",
            days_in_milk="NA",
            parity="NA",
        )
    ]
    herd_statistics.sold_and_died_cows_info = [
        SoldAnimalTypedDict(
            id=1,
            animal_type="LacCow",
            sold_at_day=0,
            body_weight=23.3,
            cull_reason="NA",
            days_in_milk="NA",
            parity="NA",
        )
    ]
    herd_statistics.stillborn_calf_info = [StillbornCalfTypedDict(id=1, stillborn_day=0, birth_weight=68.8)]

    AnimalModuleReporter.report_end_of_simulation(
        herd_statistics,
        herd_reproduction_statistics := HerdReproductionStatistics(),
        mock_time := MagicMock(auto_spec=RufasTime),
        {},
        {},
    )

    mock_report_sold_animal_information.assert_called_once_with(herd_statistics)
    assert mock_report_sold_animal_information_sort_by_sell_day.call_args_list == [
        call(sold_animals, report_name, mock_time.simulation_day)
        for sold_animals, report_name in [
            (herd_statistics.sold_calves_info, "sold_calves"),
            (herd_statistics.sold_heiferIIs_info, "heiferII"),
            (herd_statistics.sold_heiferIIIs_info, "heiferIII"),
            (herd_statistics.sold_and_died_cows_info, "sold_and_died_cows"),
            (herd_statistics.sold_cows_info, "sold_cows"),
        ]
    ]
    mock_report_stillborn_calves_information.assert_called_once_with(
        herd_statistics.stillborn_calf_info, "stillborn_calves", mock_time.simulation_day
    )
    assert mock_record_animal_events.call_args_list == [
        call({}, mock_time.simulation_day),
        call({}, mock_time.simulation_day),
    ]
    mock_record_heiferIIs_conception_rate.assert_called_once_with(herd_reproduction_statistics)
    mock_record_cows_conception_rate.assert_called_once_with(herd_reproduction_statistics)


def test__record_animal_events(mocker: MockerFixture) -> None:
    """Unit test for _record_animal_events()"""
    om = OutputManager()
    mock_om_add_variable = mocker.patch.object(om, "add_variable")
    animal_events_by_id = {
        "CALF_1": "dummy_event",
        "HEIFER_I_2": "dummy_event",
        "HEIFER_II_3": "dummy_event",
        "HEIFER_III_4": "dummy_event",
        "LAC_COW_5": "dummy_event",
        "DRY_COW_6": "dummy_event",
    }

    AnimalModuleReporter._record_animal_events(animal_events_by_id, 123)

    assert mock_om_add_variable.call_args_list == [
        call(
            f"{prefix}_day_{123}",
            event_str,
            {
                "class": AnimalModuleReporter.__name__,
                "function": AnimalModuleReporter._record_animal_events.__name__,
                "units": MeasurementUnits.UNITLESS,
            },
        )
        for prefix, event_str in animal_events_by_id.items()
    ]


def test_record_heiferIIs_conception_rate(mocker: MockerFixture) -> None:
    """Unit test for record_heiferIIs_conception_rate()"""
    om = OutputManager()
    mock_om_add_variable = mocker.patch.object(om, "add_variable")
    AnimalModuleReporter._record_heiferIIs_conception_rate(HerdReproductionStatistics())
    assert mock_om_add_variable.call_count == 12


def test_record_cows_conception_rate(mocker: MockerFixture) -> None:
    """Unit test for record_heiferIIs_conception_rate()"""
    om = OutputManager()
    mock_om_add_variable = mocker.patch.object(om, "add_variable")
    AnimalModuleReporter._record_cows_conception_rate(HerdReproductionStatistics())
    assert mock_om_add_variable.call_count == 3


def test_report_animal_population_statistics(mocker: MockerFixture) -> None:
    """Unit test for record_heiferIIs_conception_rate()"""
    om = OutputManager()
    mock_om_add_variable = mocker.patch.object(om, "add_variable")
    AnimalModuleReporter.report_animal_population_statistics(
        "dummy_prefix",
        AnimalPopulationStatistics(
            breed={"HO"},
            number_of_calves=1,
            number_of_heiferIs=2,
            number_of_heiferIIs=3,
            number_of_heiferIIIs=4,
            number_of_cows=5,
            number_of_replacement_heiferIIIS=6,
            number_of_lactating_cows=2,
            number_of_dry_cows=3,
            number_of_parity_1_cows=1,
            number_of_parity_2_cows=1,
            number_of_parity_3_cows=1,
            number_of_parity_4_cows=1,
            number_of_parity_5_cows=1,
            number_of_parity_6_or_more_cows=0,
            average_calf_age=1.1,
            average_heiferI_age=2.2,
            average_heiferII_age=3.3,
            average_heiferIII_age=4.4,
            average_cow_age=5.5,
            average_replacement_age=6.6,
            calf_age_distribution={"0-1": 1, "1-2": 2, "2-3": 3, "3-4": 4, "4-5": 5},
            heiferI_age_distribution={"0-1": 1, "1-2": 2, "2-3": 3, "3-4": 4, "4-5": 5},
            heiferII_age_distribution={"0-1": 1, "1-2": 2, "2-3": 3, "3-4": 4, "4-5": 5},
            heiferIII_age_distribution={"0-1": 1, "1-2": 2, "2-3": 3, "3-4": 4, "4-5": 5},
            cow_age_distribution={"0-1": 1, "1-2": 2, "2-3": 3, "3-4": 4, "4-5": 5},
            replacement_age_distribution={"0-1": 1, "1-2": 2, "2-3": 3, "3-4": 4, "4-5": 5},
            average_calf_body_weight=1.1,
            average_heiferI_body_weight=2.2,
            average_heiferII_body_weight=3.3,
            average_heiferIII_body_weight=4.4,
            average_cow_body_weight=5.5,
            average_replacement_body_weight=6.6,
            average_cow_days_in_pregnancy=7.7,
            average_cow_days_in_milk=8.8,
            average_cow_parity=9.9,
            average_cow_calving_interval=10.1,
        ),
    )
    assert mock_om_add_variable.call_count == 61
