from .harvested_crop import HarvestedCrop
from .storage import Storage
from .enums import CropCategory, BaleSize
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.general_constants import GeneralConstants
from RUFAS.time import Time


class Hay(Storage):
    """
    Represents a Hay storage subclass of Storage.

    Attributes
    ----------
    bale_diameter : BaleSize
        Enum representing the diameter of the hay bale in meters.
    additional_loss_coefficient : float, default 0.0
        Unitless factor used to determine the amount of additional gaseous dry matter loss.
    bale_density : float
        Density of the hay bale calculated based on its moisture content.
    bale_size : float
        Diameter of the hay bale in meters.

    Methods
    -------
    calculate_protein_loss():
        Calculates the protein loss in the hay.
    """

    def __init__(self, bale_diameter: BaleSize, capacity: float = float("inf")):
        super().__init__(capacity)
        self.acceptable_crops = [
            CropCategory.ALFALFA,
            CropCategory.GRASS,
            CropCategory.SMALL_GRAIN,
        ]
        self.bale_diameter = bale_diameter
        self.additional_loss_coefficient = 0.0

    @property
    def bale_density(self) -> float:
        """
        Calculate and return the density of the hay bale.

        Returns
        -------
        float
            The density of the hay bale.
        """
        densities = []
        for crop in self.stored:
            moisture_at_baling = 100 - crop.initial_dry_matter_percentage
            bale_density = self.calculate_bale_density(moisture_at_baling)
            densities.append(bale_density)
        average_density = sum(densities) / len(densities)
        return average_density

    @property
    def bale_size(self) -> float:
        """
        Return the size (diameter) of the hay bale.

        Returns
        -------
        float
            The diameter of the hay bale in meters.
        """
        return self.bale_diameter.value()

    def calculate_dry_matter_loss_to_gas(
        self, crop: HarvestedCrop, current_conditions: CurrentDayConditions, time: Time
    ) -> float:
        """
        Calculates the amount of gaseous dry matter lost.

        Parameters
        ----------
        crop : HarvestedCrop
            The stored crop that is losing dry matter.
        current_conditions : CurrentDayConditions
            Current conditions of the simulated day.
        time : Time
            Time instance containing the current time of the simulation.

        Returns
        -------
        float
            Amount of gaseous dry matter lost from the crop on the current day in kg.

        """
        cumulative_dry_matter_loss = self._calculate_cumulative_gaseous_dry_matter_loss(crop, current_conditions, time)
        cumulative_dry_matter_loss += self._calculate_additional_gaseous_loss(crop, current_conditions)
        current_dry_matter_loss = cumulative_dry_matter_loss - crop.previous_cumulative_dry_matter_loss
        crop.previous_cumulative_dry_matter_loss = cumulative_dry_matter_loss
        return current_dry_matter_loss

    def _calculate_cumulative_gaseous_dry_matter_loss(
        self, crop: HarvestedCrop, current_conditions: CurrentDayConditions, time: Time
    ) -> float:
        """
        Calculates the cumulative gaseous dry matter loss in hay.

        Parameters
        ----------
        crop : HarvestedCrop
            The stored crop that is losing dry matter.
        current_conditions : CurrentDayConditions
            Current conditions of the simulated day.
        time : Time
            Time instance containing the current time of the simulation.

        Returns
        -------
        float
            Total amount of gaseous dry matter loss from the hay since storage in kg.

        """
        moisture_factor = 1.0
        density = self.calculate_bale_density(crop.initial_dry_matter_percentage)
        heat = self.calculate_heat_generated(crop.initial_dry_matter_percentage, density)
        moisture_at_baling = (100 - crop.initial_dry_matter_percentage) / 100
        days_stored = crop.days_stored(time)
        days_stored_adjuster = 0.004 * days_stored
        dry_matter_at_baling = 1 - moisture_at_baling
        numerator = moisture_at_baling - moisture_factor * dry_matter_at_baling / (1 - days_stored_adjuster)
        denominator = dry_matter_at_baling * (14206 - 2433 * days_stored_adjuster) * (1 / (1 - days_stored_adjuster))
        first_thirty_days_loss = heat + 2433 * (numerator / denominator)

        total_loss = first_thirty_days_loss + 0.0001 * max(days_stored - 30, 0)

        return total_loss

    def _calculate_additional_gaseous_loss(
        self, crop: HarvestedCrop, current_conditions: CurrentDayConditions
    ) -> float:
        """
        Calculates additional gaseous dry matter loss.

        Parameters
        ----------
        crop : HarvestedCrop
            The stored crop that is losing dry matter.
        current_conditions : CurrentDayConditions
            Current conditions of the simulated day.

        Returns
        -------
        float
            Additional gaseous dry matter loss from hay in kg.

        """
        density = self.calculate_bale_density(crop.initial_dry_matter_percentage)
        rain_in_cm = current_conditions.rainfall * GeneralConstants.MM_TO_CM
        average_temp = (current_conditions.max_air_temperature + current_conditions.min_air_temperature) / 2
        return self.additional_loss_coefficient * rain_in_cm * average_temp / density * self.bale_size**3


class ProtectedIndoors(Hay):
    """
    Represents protected indoors hay storage, a subclass of Hay.
    """

    pass


class ProtectedWrapped(Hay):
    """
    Represents protected wrapped hay storage, a subclass of Hay.

    Attributes
    ----------
    additional_loss_coefficient : float, default 0.0000216
        Unitless factor used to determine the amount of additional gaseous dry matter loss.

    """

    def __init__(self, bale_diameter: BaleSize, capacity: float = float("inf")):
        super().__init__(bale_diameter, capacity)
        self.additional_loss_coefficient = 0.000_021_6


class ProtectedTarped(Hay):
    """
    Represents protected tarped hay storage, a subclass of Hay.

    Attributes
    ----------
    additional_loss_coefficient : float, default 0.0000216
        Unitless factor used to determine the amount of additional gaseous dry matter loss.

    """

    def __init__(self, bale_diameter: BaleSize, capacity: float = float("inf")):
        super().__init__(bale_diameter, capacity)
        self.additional_loss_coefficient = 0.000_010_8


class Unprotected(Hay):
    """
    Represents unprotected hay storage, a subclass of Hay.

    Attributes
    ----------
    additional_loss_coefficient : float, default 0.0000216
        Unitless factor used to determine the amount of additional gaseous dry matter loss.

    """

    def __init__(self, bale_diameter: BaleSize, capacity: float = float("inf")):
        super().__init__(bale_diameter, capacity)
        self.additional_loss_coefficient = 0.000_06
