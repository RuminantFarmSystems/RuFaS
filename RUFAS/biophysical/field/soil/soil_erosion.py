from math import atan, exp, log, sin
from typing import Optional

from RUFAS.general_constants import GeneralConstants
from RUFAS.biophysical.field.soil.soil_data import SoilData

"""
This module follows MUSLE (Modified Universal Soil Loss Equation) in section 4:1.1 of SWAT.
"""


class SoilErosion:
    """
    Manages and simulates soil erosion based on the Modified Universal Soil Loss Equation (MUSLE).

    Parameters
    ----------
    soil_data : SoilData, optional
        The SoilData object used by this module to track and simulate erosion.
    field_size : float, optional, default=None
        The size of the field (ha).

    Attributes
    ----------
    data : SoilData
        The SoilData instance used for tracking and simulating soil erosion throughout the simulation process.

    """

    def __init__(self, soil_data: Optional[SoilData], field_size: Optional[float] = None):
        """This method initializes the SoilData object that this module will work with, or create one if none provided.

        Parameters
        ----------
        soil_data : SoilData, optional
            The SoilData object used by this module to track erosion, creates new one if one is not provided.
        field_size : float, optional
            Used to initialize a SoilData object for this module to work with, if a pre-configured SoilData object is
            not provided (ha)

        """
        self.data = soil_data or SoilData(field_size=field_size)

    def erode(
        self,
        field_size: float,
        minimum_cover_management_factor: float,
        surface_residue: float,
        rainfall: float,
    ) -> None:
        """
        Main routine for SoilErosion. Runs necessary soil erosion methods and updates attributes.

        Parameters
        ----------
        field_size : float
            Size of the field that contains this Soil object (hectares).
        minimum_cover_management_factor : float
            Minimum value for cover and management factor for water erosion applicable to land cover/plant (unitless).
        surface_residue : float
            Amount of residue on the soil surface (kg per hectare).
        rainfall : float
            Amount of rain that fell on the field on the current day (mm).

        Notes
        -----
        This method calculates the mass of soil that gets eroded from the soil profile based on the content of the soil,
        how the soil is being farmed, how much rainfall there is and how much of that rain gets absorbed into the soil,
        and the geometry of the field.

        """
        erodibility_factor = self._determine_soil_erodibility_factor(
            self.data.soil_layers[0].sand_fraction,
            self.data.soil_layers[0].silt_fraction,
            self.data.soil_layers[0].clay_fraction,
            self.data.soil_layers[0].organic_carbon_fraction,
        )
        cover_factor = self._determine_cover_management_factor(minimum_cover_management_factor, surface_residue)
        support_practice_factor = self._determine_support_practice_factor()
        topographic_factor = self._determine_topographic_factor(
            self.data.slope_length, self.data.average_subbasin_slope
        )
        fragment_factor = self._determine_coarse_fragment_factor(self.data.soil_layers[0].rock_fraction)

        peak_runoff_rate = self._determine_peak_runoff_rate(
            self.data.accumulated_runoff,
            rainfall,
            self.data.slope_length,
            self.data.manning,
            self.data.average_subbasin_slope,
            field_size,
        )

        if self.data.accumulated_runoff is None:
            raise TypeError("SoilData accumulated_runoff cannot be NoneType")
        self.data.surface_runoff_volume = self.data.accumulated_runoff / field_size
        sediment_yield = self._determine_sediment_yield(
            self.data.surface_runoff_volume,
            peak_runoff_rate,
            field_size,
            erodibility_factor,
            cover_factor,
            support_practice_factor,
            topographic_factor,
            fragment_factor,
        )
        self.data.eroded_sediment = self._determine_adjusted_sediment_yield(sediment_yield, self.data.snow_content)

        # Update annual totals
        self.data.annual_eroded_sediment_total += self.data.eroded_sediment
        self.data.annual_surface_runoff_total += self.data.surface_runoff_volume

    # --- Static methods ---
    @staticmethod
    def _determine_coarse_sand_factor(sand_fraction: float, silt_fraction: float) -> float:
        """
        Calculates the coarseness factor of soil erodibility.

        Parameters
        ----------
        sand_fraction : float
            Fraction of soil content that is sand.
        silt_fraction : float
            Fraction of soil content that is silt.

        Notes
        -------
        The coarseness of a soil affects the overall erodibility of the soil. Specifically, soils with high levels of
        coarse-sand content will have relatively low erodibility compared to soils with less sand.

        Returns
        -------
        float
            Coarseness factor of erodibility, based on sand content (unitless).

        References
        ----------
        SWAT Theoretical documentation eqn. 4:1.1.6

        """
        return 0.2 + 0.3 * exp((-0.256) * sand_fraction * GeneralConstants.FRACTION_TO_PERCENTAGE * (1 - silt_fraction))

    @staticmethod
    def _determine_clay_silt_ratio_factor(silt_fraction: float, clay_fraction: float) -> float:
        """
        Calculates the component factor of erodibility that is based on the clay-silt ratio.

        Parameters
        ----------
        silt_fraction : float
            Fraction of silt in the given layer of soil.
        clay_fraction : float
            Fraction of clay in the given layer of soil.

        Notes
        -----
        The clay-silt ratio affects the erodibility of the soil, specifically soils with a high ratio of clay to
        silt are less susceptible to erosion than soils with lower ratios of clay to silt.

        Returns
        -------
        float
            The clay-silt ratio factor, based on clay and silt content (unitless).

        References
        ----------
        SWAT Theoretical documentation eqn. 4:1.1.7

        """
        if silt_fraction == 0 and clay_fraction == 0:
            return 1
        return (silt_fraction / (clay_fraction + silt_fraction)) ** 0.3

    @staticmethod
    def _determine_carbon_content_factor(organic_carbon_fraction: float) -> float:
        """
        Calculate a factor based on the fraction of organic carbon content for use in calculating soil erodibility
        factor.

        Parameters
        ----------
        organic_carbon_fraction : float
            The fraction of organic carbon content in the given layer of soil.

        Notes
        -------
        The amount of organic carbon content in the soil affects the erodibility of the soil. Soils with higher amounts
        of organic carbon content will have less erosion compared to soils with lower organic carbon content.

        Returns
        -------
        float
            The carbon factor of erodibility based on the organic carbon content of the soil (unitless).

        References
        ----------
        SWAT Theoretical documentation eqn. 4:1.1.8

        """
        return 1 - (
            (0.25 * organic_carbon_fraction * GeneralConstants.FRACTION_TO_PERCENTAGE)
            / (
                organic_carbon_fraction * GeneralConstants.FRACTION_TO_PERCENTAGE
                + exp(3.72 - (2.95 * organic_carbon_fraction * GeneralConstants.FRACTION_TO_PERCENTAGE))
            )
        )

    @staticmethod
    def _determine_high_sand_factor(sand_fraction: float) -> float:
        """
        Calculate a factor based on the percent sand content for use in calculating soil erodibility factor.

        Parameters
        ----------
        sand_fraction : float
            The fraction of sand in the given layer of soil.

        Notes
        -----
        When a soil has an extremely high sand content, it reduces the erodibility of that soil.

        Returns
        -------
        float
            The high sand content factor of erodibility, based on the amount of sand in the soil (unitless).

        References
        ----------
        SWAT Theoretical documentation eqn. 4:1.1.9

        """
        not_sand_fraction = 1 - sand_fraction
        return 1 - ((0.7 * not_sand_fraction) / (not_sand_fraction + exp(-5.51 + 22.9 * not_sand_fraction)))

    @staticmethod
    def _determine_soil_erodibility_factor(
        sand_fraction: float,
        silt_fraction: float,
        clay_fraction: float,
        organic_carbon_fraction: float,
    ) -> float:
        """
        Calculate the soil erodibility factor for use in calculating the sediment yield on a given day.

        Parameters
        ----------
        sand_fraction : float
            Fraction of sand in the given layer of soil.
        silt_fraction : float
            Fraction of silt in the given layer of soil.
        clay_fraction : float
            Fraction of clay in the given layer of soil.
        organic_carbon_fraction : float
            Fraction of organic carbon content in the given layer of soil.

        Notes
        -----
        Some soils are more prone to erosion than others, based on how much sand, silt, clay, and organic carbon
        they contain.

        Returns
        -------
        float
            The soil erodibility factor based on its coarse sand content, clay-silt ratio, clay content, and organic
            carbon content (compound unit, irrelevant).

        Reference
        ---------
        SWAT Theoretical documentation eqn. 4:1.1.5

        """

        coarse_sand_factor = SoilErosion._determine_coarse_sand_factor(sand_fraction, silt_fraction)
        clay_silt_factor = SoilErosion._determine_clay_silt_ratio_factor(silt_fraction, clay_fraction)
        carbon_content_factor = SoilErosion._determine_carbon_content_factor(organic_carbon_fraction)
        high_sand_factor = SoilErosion._determine_high_sand_factor(sand_fraction)
        return coarse_sand_factor * clay_silt_factor * carbon_content_factor * high_sand_factor

    @staticmethod
    def _determine_cover_management_factor(minimum_cover_management_factor: float, surface_residue: float) -> float:
        """
        Calculate cover and management factor for use in calculating sediment yield.

        Parameters
        ----------
        minimum_cover_management_factor : float
            Minimum value for cover and management factor for land cover (unitless).
        surface_residue : float
            Amount of residue on the soil surface (kg per hectare).

        Notes
        -----
        This factor accounts for what is planted in and/or physically covering the field. Erodibility is affected by
        this because rainfall energy is either reduced or entirely eliminated when it hits the plant canopy or
        residue on the soil surface, which means less energy is transferred to soil when the water reaches it.

        Returns
        -------
        float
            The cover and management factor (unitless).

        References
        ----------
        SWAT Theoretical documentation eqn. 4:1.1.10

        """
        if minimum_cover_management_factor <= 0:
            raise ValueError("Minimum cover and management cannot be less than or equal to 0")
        first_multiplicative_term = log(0.8) - log(minimum_cover_management_factor)
        second_multiplicative_term = exp(-0.00115 * surface_residue)
        second_additive_term = log(minimum_cover_management_factor)
        return exp(first_multiplicative_term * second_multiplicative_term + second_additive_term)

    @staticmethod
    def _determine_support_practice_factor() -> float:
        """SWAT Reference: section 4:1.1.3 (only applies to fields that are doing contour tillage/planting,
        stripcropping, and/or terracing)"""
        return 1

    @staticmethod
    def _determine_exponential_term(average_subbasin_slope: float) -> float:
        """
        Calculate the exponential term used to determine the topographic factor.

        Parameters
        -----------
        average_subbasin_slope : float
            Average slope fraction of the subbasin (unitless).

        Returns
        -------
        float
            The exponential term (unitless).

        References
        ----------
        SWAT Theoretical documentation eqn. 4:1.1.13

        """
        return 0.6 * (1 - exp(-35.835 * average_subbasin_slope))

    @staticmethod
    def _determine_topographic_factor(slope_length: float, average_subbasin_slope: float) -> float:
        """
        Calculate the topographic factor, which represents the expected ratio of soil loss per unit area from a field
        slope to that from a 22.1 m length of uniform 9% slope under otherwise identical conditions.

        Parameters
        -----------
        slope_length : float
            Length of the slope (m).
        average_subbasin_slope : float
            Average slope fraction of the subbasin (m rise over m run).

        Returns
        -------
        float
            The topographic factor (unitless).

        References
        ----------
        SWAT Theoretical documentation eqn. 4:1.1.12

        Notes
        -----
        The length and slope of a soil have an effect on erodibility, with shorter lengths and steeper slopes
        resulting in more soil erosion. A shorter length means more erosion because sediment does not have to travel
        as far to reach channels and be removed from the soil. A steeper slope means that there is less
        resistance against the gravitational forces acting on a piece of sediment as it moves down the slope,
        resulting in the soil eroding more easily.

        arctan(tan(x)) == x does not always hold, it is only true from -90 to 90 degrees, inclusive. It is safe to use
        here because there will never be a field at an angle < -90 or > 90 degrees.

        """
        slope_angle_in_rad = atan(average_subbasin_slope)
        exponential_term = SoilErosion._determine_exponential_term(average_subbasin_slope)
        first_term = (slope_length / 22.1) ** exponential_term
        second_term = 65.41 * (sin(slope_angle_in_rad) ** 2) + 4.56 * sin(slope_angle_in_rad) + 0.065
        return first_term * second_term

    @staticmethod
    def _determine_coarse_fragment_factor(rock_fraction: float) -> float:
        """
        Calculate the coarse fragment factor for use in calculating sediment yield.

        Parameters
        -----------
        rock_fraction : float
            Fraction rock in the first soil layer.

        Notes
        -----
        The mass of rocks is much greater than particles of sand, silt, clay, etc., requiring significantly more force
        to move them off a field, resulting in slower erosion in soils with higher rock content.

        Returns
        -------
        float
            Coarse fragment factor based on the rock content of the soil (unitless).

        References
        ----------
        SWAT Theoretical documentation eqn. 4:1.1.15

        """
        return exp(-0.053 * rock_fraction * GeneralConstants.FRACTION_TO_PERCENTAGE)

    @staticmethod
    def _determine_peak_runoff_rate(
        surface_runoff: float,
        rainfall: float,
        slope_length: float,
        manning: float,
        average_subbasin_slope: float,
        field_size: float,
    ) -> float:
        """
        Determines the maximum runoff flow rate that occurs with a given rainfall event.

        Parameters
        ----------
        surface_runoff : float
            Amount of rainfall that did not infiltrate into the soil on the current day (mm).
        rainfall : float
            Amount of rainfall on the current day (mm).
        slope_length : float
            Length of the subbasin slope (m).
        manning : float
            Manning roughness coefficient for the subbasin (unitless).
        average_subbasin_slope : float
            Average slope length of the subbasin expressed as rise over run (meters / meters).
        field_size : float
            Size of the field (ha)

        Returns
        -------
        float
            Peak runoff rate (cubic meters per second).

        References
        ----------
        SWAT Theoretical documentation equation 2:1.3.1

        Notes
        -----
        This equation actually demands the area of the subbasin, not the field, as a parameter. But the field area was
        used in the old code, and is used here until the data for subbasin areas can be found.

        """
        if rainfall == 0.0:
            return 0.0
        runoff_coefficient = SoilErosion._determine_runoff_coefficient(surface_runoff, rainfall)
        rainfall_intensity = SoilErosion._determine_rainfall_intensity(
            rainfall, slope_length, manning, average_subbasin_slope
        )
        field_size_in_square_km = field_size * GeneralConstants.HECTARES_TO_SQUARE_KILOMETERS
        return (runoff_coefficient * rainfall_intensity * field_size_in_square_km) / 3.6

    @staticmethod
    def _determine_runoff_coefficient(surface_runoff: float, rainfall: float) -> float:
        """
        Calculates the surface runoff coefficient for the current day.

        Parameters
        ----------
        surface_runoff : float
            Amount of rainfall that did not infiltrate into the soil on the current day (mm).
        rainfall : float
            Amount of rainfall on the current day (mm).

        Returns
        -------
        float
            Ratio of runoff to rainfall on the current day (unitless).

        References
        ----------
        SWAT Theoretical documentation equation 2:1.3.15

        """
        return surface_runoff / rainfall

    @staticmethod
    def _determine_rainfall_intensity(
        rainfall: float,
        slope_length: float,
        manning: float,
        average_subbasin_slope: float,
    ) -> float:
        """
        Determines the average rainfall rate during the time of concentration.

        Parameters
        ----------
        rainfall : float
            Amount of rain that fell on the current day (mm).
        slope_length : float
            Length of the subbasin slope (m).
        manning : float
            Manning roughness coefficient for the subbasin (unitless).
        average_subbasin_slope : float
            Average slope length of the subbasin expressed as rise over run (meters / meters).

        Returns
        -------
        float
            Rainfall intensity (mm / hour).

        References
        ----------
        SWAT Theoretical documentation equation 2:1.3.16

        """
        time_of_concentration = SoilErosion._determine_time_of_concentration(
            slope_length, manning, average_subbasin_slope
        )
        half_hour_rainfall_fraction = SoilErosion._determine_half_hour_rainfall_fraction(rainfall)
        fraction_of_rain_during_time_of_concentration = (
            SoilErosion._determine_fraction_rainfall_during_time_of_concentration(
                time_of_concentration, half_hour_rainfall_fraction
            )
        )
        rain_during_time_of_concentration = fraction_of_rain_during_time_of_concentration * rainfall
        return rain_during_time_of_concentration / time_of_concentration

    @staticmethod
    def _determine_time_of_concentration(slope_length: float, manning: float, average_subbasin_slope) -> float:
        """
        Calculates the time of concentration for the subbasin.

        Parameters
        ----------
        slope_length : float
            Length of the subbasin slope (m).
        manning : float
            Manning roughness coefficient for the subbasin (unitless).
        average_subbasin_slope : float
            Average slope length of the subbasin expressed as rise over run (m / m).

        Returns
        -------
        float
            RufasTime of concentration (hour).

        References
        ----------
        SWAT Theoretical documentation section 2:1.3.6

        Notes
        -----
        According to the SWAT Theoretical documentation, "the time of concentration is the amount of time from the
        beginning of a rainfall event until the entire subbasin area is contributing to flow at the outlet.". In SWAT,
        this is calculated as the overland flow time of concentration plus the channel flow time of concentration, but
        in this version of the RuFaS Field module as well as the previous one, it is only the overland flow time of
        concentration. This equation in SWAT also assumes an average flow rate of 6.35 mm per hour.

        """
        adjusted_slope_length = slope_length**0.6
        adjusted_manning = manning**0.6
        adjusted_average_slope_length = average_subbasin_slope**0.3
        return (adjusted_slope_length * adjusted_manning) / (18 * adjusted_average_slope_length)

    @staticmethod
    def _determine_half_hour_rainfall_fraction(rainfall: float) -> float:
        """
        Calculates the fraction of total rainfall that falls during the half-hour of most intense rainfall of this storm
        event.

        Parameters
        ----------
        rainfall : float
            Amount of rain that fell on the current day (mm).

        Returns
        -------
        float
            The fraction of total rainfall that fell during the half-hour of most intense rainfall on the current day
            (unitless).

        References
        ----------
        SWAT Theoretical documentation section 1:3.2.2

        Notes
        -----
        This method for calculating the maximum half-hour rainfall is from the old version of the Field module, and has
        been significantly simplified from the method in SWAT.

        """
        upper_limit = 1 - exp(-125 / (rainfall + 5))
        lower_limit = 0.02083
        return (lower_limit + upper_limit) / 2

    @staticmethod
    def _determine_fraction_rainfall_during_time_of_concentration(
        time_of_concentration: float, half_hour_rainfall_fraction: float
    ) -> float:
        """
        Calculates the fraction of rainfall that occurs over the time of concentration.

        Parameters
        ----------
        time_of_concentration : float
            RufasTime of concentration for this subbasin (hours).
        half_hour_rainfall_fraction : float
            Fraction of rainfall that falls during half-hour of highest rainfall intensity (unitless).

        Returns
        -------
        float
            Fraction of rainfall that occurs over the time of concentration (unitless).

        References
        ----------
        SWAT Theoretical documentation equation 2:1.3.19

        """
        product = 2 * time_of_concentration * log(1 - half_hour_rainfall_fraction)
        return 1 - exp(product)

    @staticmethod
    def _determine_sediment_yield(
        surface_area_runoff: float,
        peak_runoff_rate: float,
        field_area: float,
        soil_erodibility_factor: float,
        cover_management_factor: float,
        support_practice_factor: float,
        topographic_factor: float,
        coarse_fragment_factor: float,
    ) -> float:
        """
        Calculate the sediment yield for a given day.

        Parameters
        ----------
        surface_area_runoff : float
            Surface runoff volume (mm per hectare).
        peak_runoff_rate : float
            Peak runoff rate (cubic meters per second).
        field_area : float
            Area of the field/HRU that contains this soil (hectares).
        soil_erodibility_factor : float
            Factor for how easily the soil erodes (unitless).
        cover_management_factor : float
            Ratio of soil loss from land cropped under given conditions to corresponding loss from clean-tilled,
            continuous fallow (unitless).
        support_practice_factor : float
            Ratio of soil loss with specific support practice to corresponding loss with up-and-down slope culture
            (unitless).
        topographic_factor : float
            Expected ratio of soil loss per unit area from a field slope to that from a 22.1 m length of uniform 9%
            slope under identical conditions (unitless).
        coarse_fragment_factor : float
            Factor that adjusts for the percent rock in the first soil layer (unitless).

        Returns
        -------
        float
            Sediment yield on a given day (metric tons).

        """
        term_with_exponent = (surface_area_runoff * peak_runoff_rate * field_area) ** 0.56
        return (
            11.8
            * term_with_exponent
            * soil_erodibility_factor
            * cover_management_factor
            * support_practice_factor
            * topographic_factor
            * coarse_fragment_factor
        )

    @staticmethod
    def _determine_adjusted_sediment_yield(sediment_yield: float, snow_water_content: float) -> float:
        """
        Adjust the sediment yield based on the amount of snow cover.

        Parameters
        ----------
        sediment_yield : float
            Sediment yield on a given day (metric tons).
        snow_water_content : float
            Water content of the snow cover (mm).

        Returns
        -------
        float
            The sediment yield on a given day adjusted for the water content of the snow cover.

        Reference
        ---------
        SWAT Theoretical documentation eqn. 4:1.3.1

        """
        return sediment_yield / exp((3 * snow_water_content) / 25.4)
