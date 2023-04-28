from __future__ import annotations

from RUFAS.output_manager import OutputManager
from RUFAS.routines.manure.beddings.bedding_classes import BaseBedding
from RUFAS.routines.manure.manure_handlers.manure_handler_daily_output import ManureHandlerDailyOutput
from RUFAS.routines.manure.pen.manure_management_pen import ManureManagementPen
from RUFAS.routines.manure.reception_pits.reception_pit_daily_output import ReceptionPitDailyOutput

om = OutputManager()


class ReceptionPit:
    """Class for a reception pit.

    """

    @classmethod
    def daily_update(cls,
                     manure_handler_daily_output: ManureHandlerDailyOutput,
                     pen: ManureManagementPen,
                     bedding: BaseBedding
                     ) -> ReceptionPitDailyOutput:
        """Calculates and stores the daily output of the reception pit.

        Args:
            manure_handler_daily_output: The daily output of a manure handler.
            pen: A ManureManagementPen object.
            bedding: A BaseBedding object.

        Returns:
            The daily output of the reception pit.

        """
        bedding_data = {"bedding_mass_per_day": bedding.bedding_mass_per_day,
                        "bedding_density": bedding.bedding_density,
                        "bedding_dry_matter_content": bedding.bedding_dry_matter_content,
                        "bedding_cleaned_fraction": bedding.bedding_cleaned_fraction,
                        "bedding_type": bedding.bedding_type._name_,
                        }

        info_map = {"class": cls.__name__,
                    "function": cls.daily_update.__name__,
                    "manure_handler_daily_output": vars(manure_handler_daily_output),
                    "bedding": bedding_data,
                    }

        mh = manure_handler_daily_output
        daily_output = ReceptionPitDailyOutput(
            simulation_day=mh.simulation_day,
            pen_id=mh.pen_id,
            manure_urea=mh.manure_urea,
            liquid_manure_total_ammoniacal_nitrogen=mh.liquid_manure_total_ammoniacal_nitrogen,
            liquid_manure_nitrogen=mh.liquid_manure_nitrogen,
            liquid_manure_total_solids=mh.liquid_manure_total_solids +
            bedding.calc_total_bedding_dry_solids(pen.num_animals),
            manure_degradable_volatile_solids=mh.manure_degradable_volatile_solids,
            manure_non_degradable_volatile_solids=mh.manure_non_degradable_volatile_solids,
            liquid_manure_total_volatile_solids=mh.liquid_manure_total_volatile_solids,
            liquid_manure_phosphorus=mh.liquid_manure_phosphorus,
            liquid_manure_potassium=mh.liquid_manure_potassium,
            total_daily_manure_volume=mh.total_daily_manure_volume
        )
        om.add_variable("daily_output", vars(daily_output), info_map)

        return daily_output
