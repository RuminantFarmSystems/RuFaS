class TractorImplement:
    @property
    def mass_kg(self) -> float:
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

    def calculate_functional_draft(self) -> float:
        pass
