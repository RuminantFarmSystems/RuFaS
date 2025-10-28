from typing import Optional

from RUFAS.biophysical.field.crop.crop_data import CropData, PlantCategory
from RUFAS.biophysical.field.soil.soil_data import SoilData


class Dormancy:
    """
    A class for managing crop dormancy operations.

    Parameters
    ----------
    crop_data : Optional[CropData], optional
        A `CropData` object containing specifications and attributes for a crop.
        If not provided, a default `CropData` object is used.
    minimum_lai_during_dormancy : Optional[float], default 0.75
        Minimum leaf area index for plants (perennials and trees only).

    Attributes
    ----------
    data : CropData
        A reference to the `crop_data` object on which dormancy operations will be conducted.
    minimum_lai_during_dormancy : Optional[float]
        Minimum leaf area index for plants (perennials and trees only).

    Notes
    -----
    - This method is used if the crop remains uncut after reaching maturity. It reduces the crop's biomass
    based on species-specific water content, simulating the natural dry-down process.
    - SWAT Appendix-A section A.1.12 says that the default 0.75 is from pre-2009 versions of SWAT and users are
    now allowed to modify this value. But it does not provide values for any of the listed plant species and gives
    no information about how this value can be measured or calculated.

    """

    def __init__(
        self,
        crop_data: Optional[CropData] = None,
        minimum_lai_during_dormancy: Optional[float] = 0.75,
    ) -> None:
        self.data = crop_data or CropData
        self.minimum_lai_during_dormancy = minimum_lai_during_dormancy

    def enter_dormancy(self, soil_data: SoilData) -> None:
        """
        Performs the transition from active to dormant in a crop.

        Parameters
        ----------
        soil_data : SoilData
            SoilData instance of the soil profile that this crop is growing in.
        Methods
        -------
        enter_dormancy(soil_data: SoilData) -> None
            Performs the transition of a crop from active to dormant. Warm Annuals and Warm Annual Legumes do not
            experience dormancy. Only Trees and Perennials experience biomass loss when entering dormancy.

        find_threshold_daylength(minimum_daylength: float, dormancy_threshold: float) -> float
            Calculates the threshold daylength for dormancy based on minimum daylength and dormancy threshold.

        find_dormancy_threshold(abs_latitude: float) -> float
            Calculates the dormancy threshold based on the absolute latitude value.

        Notes
        -----
        When method is called, the crop's status is set to dormant, biomass is removed from plant and converted to
        residue, and the leaf area index is reset (if the current leaf area index is greater than the minimum leaf area
        index during dormancy for this crop).

        Note that Warm Annuals and Warn Annual Legumes do not experience dormancy, and only Trees and Perennials
        experience biomass loss when entering dormancy.

        References
        ----------
        SWAT Theoretical documentation section 5:1.2

        """
        if (
            self.data.plant_category == PlantCategory.WARM_ANNUAL
            or self.data.plant_category == PlantCategory.WARM_ANNUAL_LEGUME
        ):
            return

        if self.data.is_dormant:
            return

        self.data.is_dormant = True
        if self.data.plant_category == PlantCategory.TREE or self.data.is_perennial:
            residue = self.data.biomass * self.data.dormancy_loss_fraction * (self.data.dry_matter_percentage / 100)
            nitrogen = residue * self.data.yield_nitrogen_fraction
            soil_data.crop_yield_nitrogen = nitrogen
            soil_data.soil_layers[0].plant_residue = residue
            soil_data.plant_residue_lignin_composition = self.data.lignin_dry_matter_percentage / 100

            self.data.biomass *= 1 - self.data.dormancy_loss_fraction

            self.data.leaf_area_index = min(self.data.leaf_area_index, self.minimum_lai_during_dormancy)

    @staticmethod
    def find_threshold_daylength(minimum_daylength: float, dormancy_threshold: float) -> float:
        """
        Calculates the threshold daylength for dormancy.

        Parameters
        ----------
        minimum_daylength : float
            The minimum daylength for the watershed during the year (hours).
        dormancy_threshold : float
            The dormancy threshold for this field (hours).

        References
        ----------
        SWAT Theoretical documentation 5:1.2.1

        Returns
        -------
        float
            Threshold daylength for dormancy (hours)

        """
        return minimum_daylength + dormancy_threshold

    @staticmethod
    def find_dormancy_threshold(abs_latitude: float) -> float:
        """
        Calculates the dormancy threshold based on the absolute latitude.

        Parameters
        ----------
        abs_latitude : float
            The absolute latitude value (degrees above or below the equator).

        References
        ----------
        SWAT Theoretical documentation equations 5:1.2.2 - 5:1.2.4

        Returns
        -------
        float
            The dormancy threshold for this latitude (hours).

        """
        is_near_pole = abs_latitude > 40
        if is_near_pole:
            return 1.0

        is_near_equator = abs_latitude < 20
        if is_near_equator:
            return 0.0

        is_middle = 20 <= abs_latitude <= 40
        if is_middle:
            return (abs_latitude - 20.0) / 20.0
