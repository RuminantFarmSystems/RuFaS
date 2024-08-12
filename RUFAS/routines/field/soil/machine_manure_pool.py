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
            super()._determine_decomposed_surface_manure(temperature_factor))
        return {
            "decomposed_machine_manure_mass_change": decomposed_machine_manure_mass_change,
            "decomposed_machine_manure_coverage_change": decomposed_machine_manure_coverage_change
        }

    def determine_assimilated_machine_surface_manure(self,
                                                     temperature_factor: float,
                                                     field_size: float) -> Dict:
        """
        Determines how much machine manure is assimilated into the soil profile and how much the manure coverage is
        reduced by on the current day.

        Parameters
        ----------
        temperature_factor : float
            The temperature factor on the current day (unitless).
        field_size : float
            The area of the field (ha).

        Returns
        -------
        Dict (keys listed below)
            assimilated_machine_manure: amount of machine-applied manure that is assimilated on a given day (kg).
            machine_manure_coverage: amount of decrease in the fraction of field covered by machine-applied manure on a
                given day (unitless).

        """
        assimilated_machine_manure, machine_manure_coverage = \
            super()._determine_assimilated_surface_manure(temperature_factor, field_size)

        return {
            "assimilated_machine_manure": assimilated_machine_manure,
            "machine_manure_coverage": machine_manure_coverage
        }
