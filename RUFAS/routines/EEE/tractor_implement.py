class TractorImplement:
    @property
    def mass_kg(self) -> float:
        # TODO implement
        return 0

    @property
    def width_m(self) -> float:
        # TODO implement
        return 0

    @property
    def field_capacity_ha_per_hr(self) -> float:
        # TODO implement
        return 0

    def calculate_operation_time_hr(self, field_production_size_ha: float) -> float:
        """
        Calculates number of hours taken by tractor given other factors like implement size to perform the operation.
        Implements Helper Function 416  in EEE Functions file.
        """
        return field_production_size_ha / self.field_capacity_ha_per_hr

    def calculate_drawbar_power(self) -> float:
        """
        Calculates Drawbar Power (kW) which is the power required by the implement for propulsion forward if it
        requires a transfer of tractor power to its wheel drives for this purpose.
        Implements Helper Function 414  in EEE Functions file.
        """
        field_speed_km_per_hr = 10.00  # Constant 585 in EEE Functions file # TODO get the value from IM
        functional_draft = self.calculate_functional_draft()
        return functional_draft * field_speed_km_per_hr * 1.2 / 3600

    def calculate_functional_draft(self) -> float:
        """
        Calculatse Functional draft in Newtons, the force required for pulling various planting implements and
        minor tillage tools operated at shallow depths.
        Implements Helper Function 417  in EEE Functions file.
        """
        pass

    def calculate_needed_PTO(self, crop_yield_ton_per_ha: float, field_production_size_ha: float) -> float:
        """
        Calculates PTO_Power (kW) from the tractor to power the implement's operation.
        Implements Helper Function 415  in EEE Functions file.
        """
        E = 0  # TODO get the correct value
        F = 0  # TODO get the correct value
        G = 0  # TODO get the correct value
        (
            E
            + (F * self.width_m)
            + (
                G
                * crop_yield_ton_per_ha
                * field_production_size_ha
                / self.calculate_operation_time_hr(field_production_size_ha)
            )
        )
