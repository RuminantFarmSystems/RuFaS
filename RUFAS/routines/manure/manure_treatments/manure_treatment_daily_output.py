from __future__ import annotations

from dataclasses import astuple
from dataclasses import dataclass


@dataclass
class ManureTreatmentDailyOutput:
    """Daily output of a manure treatment.

    Attributes:
        simulation_day: Number of days into the simulation.
        pen_id: ID of the pen that this output is associated with.
        TAN: Total ammonia nitrogen concentration, g/L.
        N: Amount of nitrogen in manure, kg.
        TS: Total amount of solids from the manure and the bedding, kg.
        VS_total: Total amount of volatile solids, kg.
        P: Amount of phosphorus excreted in manure, kg.
        K: Amount of potassium in manure, kg.
        final_manure_volume: Final manure volume after treatment, m^3.

    """
    simulation_day: int = -1
    pen_id: int = -1
    TAN: float = 0.0
    N: float = 0.0
    TS: float = 0.0
    VS_total: float = 0.0
    P: float = 0.0
    K: float = 0.0
    final_manure_volume: float = 0.0

    def __add__(self, other: ManureTreatmentDailyOutput) -> ManureTreatmentDailyOutput:
        """Adds corresponding attributes between this output and another.

        Args:
            other: ManureTreatmentDailyOutput object to add.

        Returns:
            ManureTreatmentDailyOutput with corresponding attributes summed.

        """
        if not isinstance(other, ManureTreatmentDailyOutput):
            raise TypeError('Other must be of type ManureTreatmentDailyOutput.')

        return ManureTreatmentDailyOutput(*[
            attr1 + attr2 for attr1, attr2 in zip(astuple(self), astuple(other))
        ])


# TODO: move to a separate file
@dataclass
class AggregatedManureDailyOutputForFieldManure(ManureTreatmentDailyOutput):
    """Description: This class is an API for field application of stored manure
        The attributes of this dataclass should be identical to the attributes
        expected in the RUFAS.routines.field.field_management.manure_application update_all method.
    """
    mass: float = 0.0  # total manure mass kg
    N_mass: float = 0.0
    P_mass: float = 0.0
    K_mass: float = 0.0
    WIP: float = 0.0
    WOP: float = 0.0
    DM: float = 0.0

    def convert_treatment_output_to_field_outputs(self,
                                                  daily_output: ManureTreatmentDailyOutput,
                                                  WIP_frac: float,
                                                  WOP_frac: float
                                                  ):
        """converts TreatmentOutputs attributes to attribute names in class"""
        self.N_mass = daily_output.N
        self.P_mass = daily_output.P
        self.K_mass = daily_output.K
        self.mass = daily_output.total_daily_mass
        self.DM = daily_output.DM
        self.WIP = daily_output.VS_total * WIP_frac
        self.WOP = daily_output.VS_total * WOP_frac
