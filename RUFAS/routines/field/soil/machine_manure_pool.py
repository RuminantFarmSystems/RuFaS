from typing import Dict

from RUFAS.routines.field.soil.manure_pool import ManurePool


class MachineManurePool(ManurePool):
    def determine_decomposed_surface_machine_manure(self, temperature_factor: float) -> Dict[str, float]:
        """
        This method calculates how much manure in both the machine-applied pools decompose on a given day,
        and how much the field coverage changes as a result.

        Parameters
        ----------
        temperature_factor : float
            The temperature factor on the current day (unitless).

        Returns
        -------
        Dict (keys listed below)
            decomposed_machine_manure_mass_change: change in the mass of machine-applied manure on the field surface
                decomposed on this day (kg).
            decomposed_machine_manure_coverage_change: change in field coverage of machine-applied manure on the field
                surface (unitless).

        """
        decomposed_machine_manure_mass_change, decomposed_machine_manure_coverage_change = (
            super().determine_decomposed_surface_manure(temperature_factor)
        )
        return {
            "decomposed_machine_manure_mass_change": decomposed_machine_manure_mass_change,
            "decomposed_machine_manure_coverage_change": decomposed_machine_manure_coverage_change,
        }
