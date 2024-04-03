from abc import ABC, abstractmethod


class MethaneMitigationMethod(ABC):
    """A class representing a methane mitigation method. This is a base class and should be subclassed."""

    @abstractmethod
    def calculate(self, nutrient_concentrations: dict, additive_amount: float) -> float:
        """Calculate the reduction in methane yield.

        This is a placeholder and should be overridden by subclasses.

        Parameters
        ----------
        nutrient_concentrations : dict
            A dictionary containing nutrient concentrations.
        additive_amount : float
            The amount of additive.

        Returns
        -------
        float
            The reduction in methane yield.

        """
        pass


class NOP(MethaneMitigationMethod):
    """A class representing the 3-NOP methane mitigation method."""

    def calculate(self, nutrient_concentrations: dict, additive_amount: float) -> float:
        """Calculate the reduction in methane yield for the 3-NOP method.

        Parameters
        ----------
        nutrient_concentrations : dict
            A dictionary containing nutrient concentrations.
        additive_amount : float
            The amount of 3-NOP additive.

        Returns
        -------
        float
            The reduction in methane yield.

        """
        NDF_concentration = nutrient_concentrations["NDF"]
        EE_concentration = nutrient_concentrations["EE"]
        starch_concentration = nutrient_concentrations["starch"]
        return (
            -30.8
            - 0.226 * (additive_amount - 70.5)
            + 0.906 * (NDF_concentration - 32.9)
            + 3.871 * (EE_concentration - 4.2)
            - 0.337 * (starch_concentration - 21.1)
        )


class Monensin(MethaneMitigationMethod):
    """A class representing the Monensin methane mitigation method."""

    def calculate(self, nutrient_concentrations: dict, additive_amount: float) -> float:
        """Calculate the reduction in methane yield for the Monensin method.

        Parameters
        ----------
        nutrient_concentrations : dict
            A dictionary containing nutrient concentrations.
        additive_amount : float
            The amount of Monensin additive.

        Returns
        -------
        float
            The reduction in methane yield.

        """
        starch_concentration = nutrient_concentrations["starch"]
        return 6.36 - 0.277 * additive_amount - 0.182 * starch_concentration


class EssentialOils(MethaneMitigationMethod):
    """A class representing the Essential Oils methane mitigation method."""

    def calculate(self, nutrient_concentrations: dict, additive_amount: float) -> float:
        """Calculate the reduction in methane yield for the Essential Oils method.

        Parameters
        ----------
        nutrient_concentrations : dict
            A dictionary containing nutrient concentrations.
        additive_amount : float
            The amount of essential oils additive.

        Returns
        -------
        float
            The reduction in methane yield. This implementation always returns 0.0.

        """
        return 0.0


class Seaweed(MethaneMitigationMethod):
    """A class representing the Seaweed methane mitigation method."""

    def calculate(self, nutrient_concentrations: dict, additive_amount: float) -> float:
        """Calculate the reduction in methane yield for the Seaweed method.

        Parameters
        ----------
        nutrient_concentrations : dict
            A dictionary containing nutrient concentrations.
        additive_amount : float
            The amount of Seaweed additive.

        Returns
        -------
        float
            The reduction in methane yield. This implementation always returns 0.0.

        """
        return 0.0


class MethaneMitigationMethodManager:
    """A class to manage the creation and use of MethaneMitigationMethod subclasses."""

    @staticmethod
    def calculate_methane_mitigation(
        nutrient_concentrations: dict,
        methane_mitigation_method: str,
        methane_mitigation_additive_amount: float,
    ) -> float:
        """Calculate the reduction in methane yield for a given mitigation method.

        Parameters
        ----------
        nutrient_concentrations : dict
            A dictionary containing nutrient concentrations.
        methane_mitigation_method : str
            The name of the methane mitigation method. The accepted names are
            'nop', 'monensin', 'essentialoils', 'seaweed', '3-NOP', 'Monensin', 'Essential Oils', and 'Seaweed'.
        methane_mitigation_additive_amount : float
            The amount of additive.

        Returns
        -------
        float
            The reduction in methane yield.

        Raises
        ------
        ValueError
            If the mitigation method name is not recognized.

        """
        method_classes = {cls.__name__.lower(): cls for cls in MethaneMitigationMethod.__subclasses__()}

        # Map friendly names to class names if preferred
        friendly_name_map = {
            "3-NOP": "nop",
            "Monensin": "monensin",
            "Essential Oils": "essentialoils",
            "Seaweed": "seaweed",
        }

        # Translate friendly name to class name if needed
        if methane_mitigation_method in friendly_name_map:
            method_name = friendly_name_map[methane_mitigation_method]
        else:
            method_name = methane_mitigation_method.lower()

        try:
            mitigation_method = method_classes[method_name]()
            return mitigation_method.calculate(nutrient_concentrations, methane_mitigation_additive_amount)
        except KeyError:
            raise ValueError(
                f"{methane_mitigation_method} is not a recognized methane mitigation method. "
                f"Accepted methods are {list(method_classes.keys()) + list(friendly_name_map.keys())}."
            )
