from __future__ import annotations

from dataclasses import asdict
from dataclasses import astuple
from dataclasses import dataclass


@dataclass
class TreatmentDailyOutput:
    simulation_day: int = -1
    pen_id: int = -1
    TAN_s: float = 0.0  # g/L
    N_manure: float = 0.0  # kg
    TSd: float = 0.0  # kg
    VSd: float = 0.0  # kg
    VSnd: float = 0.0  # kg
    VS_total: float = 0.0  # kg
    p_excrt_manure: float = 0.0  # kg
    K_manure: float = 0.0  # kg
    final_manure_volume: float = 0.0  # m^3

    def clone(self) -> TreatmentDailyOutput:
        return TreatmentDailyOutput(**asdict(self))

    def __add__(self, other: TreatmentDailyOutput) -> TreatmentDailyOutput:
        """Add two StorageOptionVariables objects by summing
        their corresponding attributes.

        Args:
            other: the StorageOptionVariables object to be added to the `self` object

        Returns:
            A new StorageOptionVariables object with summed attributes.
            The original operands remain intact.

        """

        if not isinstance(other, TreatmentDailyOutput):
            raise TypeError('Cannot add a non-StorageOptionVariables object to a '
                            'StorageOptionVariables object.')

        return TreatmentDailyOutput(*[
            attr1 + attr2 for attr1, attr2 in zip(astuple(self), astuple(other))
        ])



# TODO: move to a separate file
@dataclass
class AggregatedManureDailyOutputForField(TreatmentDailyOutput):
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

    def convert_treatment_output_to_field_outputs(self, daily_output):
        """converts TreatmentOutputs attributes to attribute names in class"""
        self.N_mass = daily_output.manure_nitrogen
        self.P_mass = daily_output.p_excrt_manure
        self.K_mass = daily_output.K_manure
        self.mass = daily_output.total_daily_mass
        self.DM = daily_output.DM
        self.WIP = daily_output.VS_total * 0.5
        self.WOP = daily_output.VS_total * 0.5

