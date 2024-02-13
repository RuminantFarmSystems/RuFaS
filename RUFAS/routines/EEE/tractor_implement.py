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
    def operation_time_hr(self) -> float:
        # TODO implement
        return 0

    def calculate_drawbar_power(self) -> float:
        """
        Calculates Drawbar Power (kW) which is the power required by the implement for propulsion forward if it
        requires a transfer of tractor power to its wheel drives for this purpose.
        Implements Helper Function 414  in EEE Functions file.
        """
        field_speed_km_per_hr = 10.00  # Constant 585 in EEE Functions file # TODO get the value from IM
        functional_draft = self.calculate_functional_draft
        return functional_draft * field_speed_km_per_hr * 1.2 / 3600

    def calculate_functional_draft(self) -> float:  # TODO imeplement
        pass

    def calculate_needed_PTO(self, crop_yield_ton_per_ha: float, field_production_size_ha: float) -> float:
        """Calculates PTO_Power (kW) from the tractor to power the implement's operation"""
        E = 0  # TODO get the correct value
        F = 0  # TODO get the correct value
        G = 0  # TODO get the correct value
        E + (F * self.width_m) + (G * crop_yield_ton_per_ha * field_production_size_ha / self.operation_time_hr)
