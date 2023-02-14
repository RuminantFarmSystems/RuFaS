from typing import Optional
from math import exp, log, atan, sin

from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData

"""
This module follows MUSLE (Modified Universal Soil Loss Equation) in section 4:1.1 of SWAT
"""


class SoilErosion:
    def __init__(self, soil_data: Optional[SoilData]):
        self.data = soil_data or SoilData()  # Initialize with defaults, if not given

    def erode(self, minimum_cover_management_factor: float, surface_residue: float) -> None:
        """this is the main routine for SoilErosion. It is responsible for running all the necessary soil erosion
            methods and updating attributes as necessary

        Args:
            minimum_cover_management_factor: minimum value for cover and management factor for water erosion applicable
                to land cover/plant (unitless)
            surface_residue: amount of residue on the soil surface (kg per hectare)

        """
        erodibility_factor = self._determine_soil_erodibility_factor(self.data.percent_sand_content,
                                                                     self.data.percent_silt_content,
                                                                     self.data.soil_layers[0].percent_clay_content,
                                                                     self.data.soil_layers[0]
                                                                                        .percent_organic_carbon_content)
        cover_factor = self._determine_cover_management_factor(minimum_cover_management_factor, surface_residue)
        support_practice_factor = self._determine_support_practice_factor()
        topographic_factor = self._determine_topographic_factor(self.data.slope_length,
                                                                self.data.average_slope_fraction)
        fragment_factor = self._determine_coarse_fragment_factor(self.data.percent_rock_content)

        if self.data.peak_runoff_rate is None:
            raise TypeError("SoilData peak_runoff_rate cannot be NoneType")
            return
        elif self.data.surface_runoff_volume is None:
            raise TypeError("SoilData surface_runoff_rate cannot be NoneType")
            return
        self.data.eroded_sediment += self._determine_sediment_yield(self.data.surface_runoff_volume,
                                                                   self.data.peak_runoff_rate, self.data.field_size,
                                                                   erodibility_factor, cover_factor,
                                                                   support_practice_factor, topographic_factor,
                                                                   fragment_factor)

    # --- Static methods ---
    @staticmethod
    def _determine_coarse_sand_factor(percent_sand_content: float, percent_silt_content: float) -> float:
        """calculates factor based on sand content for use in determining soil erodibility factor

        Args:
            percent_sand_content: percent of soil content that is sand
            percent_silt_content: percent of soil content that is silt

        Returns:
            factor based on sand content (unitless)

        SWAT Reference: 4:1.1.6
        """
        return 0.2 + 0.3 * exp((-0.256) * percent_sand_content * (1 - (percent_silt_content / 100)))

    @staticmethod
    def _determine_clay_silt_ratio_factor(percent_silt_content: float, percent_clay_content: float) -> float:
        """calculates factor based on the clay-silt ratio for use in calculating soil erodibility factor

        Args:
            percent_silt_content: percent of silt in the given layer of soil
            percent_clay_content: percent of clay in the given layer of soil

        Returns:
            clay-silt ratio factor (unitless)

        SWAT Reference: 4:1.1.7
        """
        if percent_silt_content == 0 and percent_clay_content == 0:
            raise ValueError("Cannot have percent silt content and percent clay content both be 0")
        return (percent_silt_content / (percent_clay_content + percent_silt_content)) ** 0.3

    @staticmethod
    def _determine_carbon_content_factor(percent_organic_carbon: float) -> float:
        """calculates factor based on percent of organic carbon content for use in calculating soil erodibility factor

        Args:
            percent_organic_carbon: percent of organic carbon content in the given layer of soil

        Returns:
            organic carbon percent factor in the given layer of soil

        SWAT Reference: 4:1.1.8
        """
        return 1 - ((0.25 * percent_organic_carbon) / (percent_organic_carbon +
                                                       exp(3.72 - (2.95 * percent_organic_carbon))))

    @staticmethod
    def _determine_high_sand_factor(percent_sand_content: float) -> float:
        """calculates factor based on percent sand content for use in calculating soil erodibility factor

        Args:
            percent_sand_content: percent of sand in the given layer of soil

        Returns:
            factor for adjusting soil erodibility factor based on high sand contents

        SWAT Reference: 4:1.1.9
        """
        inverse_sand_percentage = 1 - (percent_sand_content / 100)
        # TODO: better name for this variable
        return 1 - ((0.7 * inverse_sand_percentage) / (inverse_sand_percentage + exp(-5.51 + 22.9 *
                                                                                     inverse_sand_percentage)))

    @staticmethod
    def _determine_soil_erodibility_factor(percent_sand_content: float, percent_silt_content: float,
                                           percent_clay_content: float, percent_organic_carbon_content: float) -> float:
        """calculates the soil erodibility factor for use in calculating the sediment yield on a given day

        Args:
            percent_sand_content: percent of sand in the given layer of soil
            percent_silt_content: percent of silt in the given layer of soil
            percent_clay_content: percent of clay in the given layer of soil
            percent_organic_carbon_content: percent of organic carbon content in the given layer of soil

        Returns:
            the soil erodibility factor (unitless)

        SWAT Reference: 4:1.1.5
        """
        coarse_sand_factor = SoilErosion._determine_coarse_sand_factor(percent_sand_content, percent_silt_content)
        clay_silt_factor = SoilErosion._determine_clay_silt_ratio_factor(percent_silt_content, percent_clay_content)
        carbon_content_factor = SoilErosion._determine_carbon_content_factor(percent_organic_carbon_content)
        high_sand_factor = SoilErosion._determine_high_sand_factor(percent_sand_content)
        return coarse_sand_factor * clay_silt_factor * carbon_content_factor * high_sand_factor

    @staticmethod
    def _determine_cover_management_factor(minimum_cover_management_factor: float, surface_residue: float) -> float:
        """calculates cover and management factor for use in calculating sediment yield

        Args:
            minimum_cover_management_factor: minimum value for cover and management factor for land cover (unitless)
            surface_residue: amount of residue on the soil surface (kg per hectare)

        Returns:
            the cover and management factor (unitless)

        SWAT Reference: 4:1.1.10
        """
        if minimum_cover_management_factor <= 0:
            raise ValueError("Minimum cover and management cannot be less than or equal to 0")
        first_multiplicative_term = log(0.8) - log(minimum_cover_management_factor)
        second_multiplicative_term = exp(-0.00115 * surface_residue)
        second_additive_term = log(minimum_cover_management_factor)
        return exp(first_multiplicative_term * second_multiplicative_term + second_additive_term)

    @staticmethod
    def _determine_support_practice_factor() -> float:
        """TODO: implement this for version 2 (only applies to fields that are doing contour tillage/planting,
            stripcropping, and/or terracing) SWAT Reference: section 4:1.1.3"""
        return 1

    @staticmethod
    def _determine_exponential_term(average_subbasin_slope: float) -> float:
        """calculates the exponential term, which is used to calculate the topographic factor

        Args:
            average_subbasin_slope: average slope fraction of the subbasin (unitless)

        Returns:
            the exponential term (unitless)

        SWAT Reference: 4:1.1.13
        """
        return 0.6 * (1 - exp(-35.835 * average_subbasin_slope))

    @staticmethod
    def _determine_topographic_factor(slope_length: float, average_subbasin_slope: float) -> float:
        """calculates expected ratio of soil loss per unit area from a field slope to that from a 22.1 m length of
            uniform 9% slope under otherwise identical conditions (a.k.a the topographic factor)

        Args:
            slope_length: length of the slope (m)
            average_subbasin_slope: average slope fraction of the subbasin (m rise over m run)

        Returns:
            the topographic factor (unitless)

        SWAT Reference: 4:1.1.12
        """
        # Note: arctan(tan(x)) == x does not always hold, it is only true from -90 to 90 degrees, inclusive. It is safe
        # to use here because there will never be a field at an angle < -90 or > 90 degrees
        slope_angle_in_rad = atan(average_subbasin_slope)
        exponential_term = SoilErosion._determine_exponential_term(average_subbasin_slope)
        first_term = (slope_length / 22.1) ** exponential_term
        second_term = 65.41 * (sin(slope_angle_in_rad) ** 2) + 4.56 * sin(slope_angle_in_rad) + 0.065
        return first_term * second_term

    @staticmethod
    def _determine_coarse_fragment_factor(percent_rock_content: float) -> float:
        """calculates coarse fragment factor for use in calculating sediment yield

        Args:
            percent_rock_content: percent rock in first soil layer

        Returns:
            coarse fragment factor (unitless)

        SWAT Reference: 4:1.1.15
        """
        return exp(-0.053 * percent_rock_content)

    @staticmethod
    def _determine_sediment_yield(surface_area_runoff: float, peak_runoff_rate: float, field_area: float,
                                  soil_erodibility_factor: float, cover_management_factor: float,
                                  support_practice_factor: float, topographic_factor: float,
                                  coarse_fragment_factor: float) -> float:
        """calculates the sediment yield for a given day

        Args:
            surface_area_runoff: surface runoff volume (mm per hectare)
            peak_runoff_rate: peak runoff rate (meters cubed per second)
            field_area: area of the field/HRU that contains this soil (hectares)
            soil_erodibility_factor: factor for how easily the soil erodes (unitless)
            cover_management_factor: ratio of soil loss from land cropped under given conditions to corresponding loss
                from clean-tilled, continuous fallow(unitless)
            support_practice_factor: ratio of soil loss with specific support practice to corresponding loss with
                up-and-down slope culture (unitless)
            topographic_factor: expected ratio of soil loss per unit area from a field slope to that from a 22.1 m
                length of uniform 9% slope under identical conditions (unitless)
            coarse_fragment_factor: factor that adjusts for percent rock in the first soil layer (unitless)

        Returns:
            sediment yield on a given day (metric tons)
        """
        term_with_exponent = (surface_area_runoff * peak_runoff_rate * field_area) ** 0.56
        return (11.8 * term_with_exponent * soil_erodibility_factor * cover_management_factor * support_practice_factor
                * topographic_factor * coarse_fragment_factor)
