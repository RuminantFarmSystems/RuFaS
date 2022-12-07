from __future__ import annotations

from RUFAS.routines.manure.beddings.bedding_classes import BaseBedding
from RUFAS.routines.manure.manure_handlers.manure_handler_daily_output import ManureHandlerDailyOutput
from RUFAS.routines.manure.pen.manure_management_pen import ManureManagementPen
from RUFAS.routines.manure.reception_pits.reception_pit_daily_output import ReceptionPitDailyOutput


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
        mh = manure_handler_daily_output
        daily_output = ReceptionPitDailyOutput(
                simulation_day=mh.simulation_day,
                pen_id=mh.pen_id,
                urea=mh.urea,
                TAN=mh.TAN,
                N=mh.N,
                TS=mh.TS + bedding.calc_total_bedding_dry_solids(pen.num_animals),
                VSd=mh.VSd,
                VSnd=mh.VSnd,
                VS_total=mh.VS_total,
                P=mh.P,
                K=mh.K,
                total_daily_manure_volume=mh.total_daily_manure_volume
        )
        return daily_output
