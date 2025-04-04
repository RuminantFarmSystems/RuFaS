class MethaneMitigationCalculator:
    @staticmethod
    def mitigate_methane(
        neutral_detergent_fiber_concentration: float,
        ethyl_ester_concentration: float,
        starch_concentration: float,
        methane_mitigation_method: str,
        methane_mitigation_additive_amount: float,
    ) -> float:
        """
        Calculates reduction in methane yield (%) due to addition of certain methane mitigation feed additive.

        Notes
        -----
        3-NOP methane yield reduction: [AN.MET.8]
        Monensin methane yield reduction: [AN.MET.9]

        Parameters
        ----------
        neutral_detergent_fiber_concentration : float
            Concentration of neutral detergent fiber (NDF) in the ration.
        ethyl_ester_concentration : float
            Concentration of ether extract (EE) in the ration.
        starch_concentration : float
            Concentration of starch in the ration.
        methane_mitigation_method: str
            Methane mitigation method used to reduce enteric methane emissions, including "3-NOP", "Monensin" and
            "EssentialOils".
        methane_mitigation_additive_amount: float
            The amount of methane mitigation feed additive that is added, mg/kg dry matter intake (DMI).
            The recommended dose for 3-NOP is
            between 40 and 100 mg/kg DMI, while that for monensin is between 20 and 36 mg/kg DMI.

        Returns
        -------
        float
            Reduction in methane yield (methane production/DMI), %.

        References
        ----------
        (Kebreab et al., 2023;  Cabezas-Garcia, unpublished)

        """

        if methane_mitigation_method == "3-NOP":
            methane_yield_reduction = (
                -30.8
                - 0.226 * (methane_mitigation_additive_amount - 70.5)
                + 0.906 * (neutral_detergent_fiber_concentration - 32.9)
                + 3.871 * (ethyl_ester_concentration - 4.2)
                - 0.337 * (starch_concentration - 21.1)
            )
        elif methane_mitigation_method == "Monensin":
            methane_yield_reduction = 6.36 - 0.277 * methane_mitigation_additive_amount - 0.182 * starch_concentration
        else:
            methane_yield_reduction = 0.0

        return methane_yield_reduction
