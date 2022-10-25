from __future__ import annotations

from dataclasses import asdict, astuple, dataclass, field

from RUFAS.routines.manure_management.misc.units import Units


@dataclass
class TreatmentOutput:
    TAN_s: float = 0.0  # g/L
    manure_nitrogen: float = 0.0  # kg
    TSd: float = 0.0  # kg
    VSd: float = 0.0  # kg
    VSnd: float = 0.0  # kg
    VS_total: float = 0.0  # kg
    p_excrt_manure: float = 0.0  # kg
    K_manure: float = 0.0  # kg
    total_daily_mass: float = 0.0  # L
    final_volume: float = 0.0  # m^3

    def clone(self) -> TreatmentOutput:
        return TreatmentOutput(**asdict(self))

    def __add__(self, other: TreatmentOutput) -> TreatmentOutput:
        """
        Add two StorageOptionVariables objects by summing
        their corresponding attributes.

        Args:
            other: the StorageOptionVariables object to be added to the `self` object

        Returns:
            A new StorageOptionVariables object with summed attributes.
            The original operands remain intact.

        """

        if not isinstance(other, TreatmentOutput):
            raise TypeError('Cannot add a non-StorageOptionVariables object to a '
                            'StorageOptionVariables object.')

        return TreatmentOutput(*[
            attr1 + attr2 for attr1, attr2 in zip(astuple(self), astuple(other))
        ])

    def __str__(self) -> str:
        res = ['Treatment output']
        for key, val in asdict(self).items():
            res.append(f'{key:40}: {val:20,.2f} {getattr(Units, key, ""):<10}')
        return '\n'.join(res)


@dataclass
class AnaerobicDigestionOutput(TreatmentOutput):
    biogas: float = 0.0  # biogas production per day (m3/day)
    biogas_energy_content: float = 0.0  # biogas energy content (MJ/m3)
    methane_generation_volume: float = 0.0
    input_energy_heating: float = 0.0
    top_cover_volume: float = 0.0
    evaporated_water:float=0.0

    def __post_init__(self):
        self.total_daily_mass = 0.0  # TODO convert effluent volume to total daily mass

    def clone(self) -> TreatmentOutput:
        return AnaerobicDigestionOutput(**asdict(self))



@dataclass
class AggregatedManureOutputforField(TreatmentOutput):
    """Description: This class is an API for field application of stored manure
        The attributes of this dataclass should be identical to the attributes
        expected in the RUFAS.routines.field.field_management.manure_application update_all method. 
    """
    mass: float = 0.0  # total manure mass kg
    N_mass:float=0.0
    P_mass:float=0.0
    K_mass:float=0.0
    WIP:float=0.0
    WOP:float=0.0
    DM:float=0.0
    def convert_treatment_output_to_field_outputs(self,daily_output):
        """converts TreatmentOutputs attributes to attributes names in class"""
        self.N_mass=daily_output.manure_nitrogen
        self.P_mass=daily_output.p_excrt_manure
        self.K_mass=daily_output.K_manure
        self.mass =daily_output.total_daily_mass 
        self.DM =daily_output.DM
        self.WIP =self.P_mass.self.mass*0.5/self.mass/1000
        self.WOP =self.P_mass.self.mass*0.05/self.mass/1000


@dataclass
class SludgeOutput(TreatmentOutput):
    """Description: This class is for tracking sludge accumulated properties. 
    """
    TS: float = 0.0  
    VS: float = 0.0  
    N_mass:float=0.0
    P_mass:float=0.0
    K_mass:float=0.0

