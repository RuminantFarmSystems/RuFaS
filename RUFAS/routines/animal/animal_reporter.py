from RUFAS.output_manager import OutputManager
from RUFAS.routines.animal.ration.ration_driver import RationReporter
from RUFAS.routines.animal.pen import Pen

# from RUFAS.routines.animal import AnimalManager

om = OutputManager()


class AnimalReporter:
    def __init__():
        pass

    def report_daily_animal_data(animal_manager):
        info_map = {
            "class": AnimalReporter.__name__,
            "function": AnimalReporter.report_daily_animal_data.__name__,
        }
        om.add_variable("sim_day", animal_manager.simulation_day, info_map)
        om.add_variable(
            "num_animals",
            len(animal_manager.calves)
            + len(animal_manager.heiferIs)
            + len(animal_manager.heiferIIs)
            + len(animal_manager.heiferIIIs)
            + len(animal_manager.cows),
            info_map,
        )
        om.add_variable("num_calves", len(animal_manager.calves), info_map)
        om.add_variable("num_heiferIs", len(animal_manager.heiferIs), info_map)
        om.add_variable("num_heiferIIs", len(animal_manager.heiferIIs), info_map)
        om.add_variable("num_heiferIIIs", len(animal_manager.heiferIIIs), info_map)
        om.add_variable(
            "num_lactating_cows",
            len([cow for cow in animal_manager.cows if cow.is_lactating]),
            info_map,
        )
        om.add_variable(
            "num_dry_cows",
            len([cow for cow in animal_manager.cows if not cow.is_lactating]),
            info_map,
        )

    def report_ration_interval_data(animal_manager, feed):
        for pen in animal_manager.all_pens:
            nutrient_amount = pen.ration_nutrient_amount
            nutrient_conc = pen.ration_nutrient_conc
            ration_per_animal = pen.ration_per_animal
            ration_report = {}
            ration_report["nutrient_amount"] = nutrient_amount
            ration_report["nutrient_conc"] = nutrient_conc

            info_map = {
                "class": AnimalReporter.__name__,
                "function": AnimalReporter.report_ration_interval_data.__name__,
                f"number_animals_in_pen_{pen.id}": len(pen.animals_in_pen),
            }
            om.add_variable(
                f"ration_nutrient_amount_pen_{pen.id}", nutrient_amount, info_map
            )
            om.add_variable(f"MEdiet_pen_{pen.id}", pen.MEdiet, info_map)
            om.add_variable(f"avg_rqmts_pen_{pen.id}", pen.avg_nutrient_rqmts, info_map)
            om.add_variable(
                f"ration_per_animal_for_pen_{pen.id}", pen.ration_per_animal, info_map
            )
            if pen.animal_combination != Pen.AnimalCombination.CALF:
                ration_supply_report = RationReporter.report_ration_supply(
                    ration_per_animal,
                    feed.available_feeds,
                    ration_report,
                    pen.avg_nutrient_rqmts["avg_BW"],
                )
                om.add_variable(
                    f"ration_supply_report_for_pen_{pen.id}",
                    ration_supply_report,
                    info_map,
                )

    def report_milk(pen, simulation_day):
        info_map = {
            "class": AnimalReporter.__name__,
            "function": AnimalReporter.report_milk.__name__,
            "simulation_day": simulation_day,
        }

        for animal in pen.animals_in_pen:
            milk_data_update = {}
            milk_data_update["days_in_milk"] = animal.days_in_milk
            milk_data_update[
                "estimated_daily_milk_produced"
            ] = animal.estimated_daily_milk_produced
            milk_data_update["milk_protein"] = animal.mPrt
            milk_data_update["milk_fat"] = animal.fat_percent
            milk_data_update["milk_lactose"] = animal.lactose_milk
            milk_data_update["lactating"] = animal.milking
            milk_data_update["parity"] = animal.calves
            milk_data_update["cow_id"] = animal.id

            om.add_variable("milk_data_at_milk_update", milk_data_update, info_map)
