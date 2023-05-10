from typing import Optional
from math import exp, log
from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData


class LeachingRunoffErosion:

    def __init__(self, soil_data: Optional[SoilData], field_size: Optional[float] = None):
        """This method initializes the SoilData object that this module will work with, or create one if none provided.

        Parameters
        ----------
        soil_data : SoilData, optional
            The SoilData object used by this module to track nitrogen leaching and runoff in the soil profile, creates
            new one if one is not provided.
        field_size : float, optional
            Used to initialize a SoilData object for this module to work with, if a pre-configured SoilData object is
            not provided (ha)

        """
        self.data = soil_data or SoilData(field_size=field_size)

    @staticmethod
    def _determine_nitrogen_concentration(soluble_nitrogen_amount: float,
                                          soil_water_runoff_sum: float,
                                          saturation_content: float) -> float:
        """This method determines the concentration of the inorganic pools NO3/NH4 in the top soil layer

        Parameters
        ----------
        soluble_nitrogen_amount: float
            amount of soluble nitrogen (kg /mm H20)
        soil_water_runoff_sum: float
            Sum of runoff and soil water for layer (mm H2O)
        saturation_content: float
            volume of water in layer when saturated (mm)

        Returns
        -------
        float
            the concentration of the inorganic pools NO3/NH4 in the top soil layer (kg /mm H20)

        References
        ----------
        SWAT Theoretical documentation eqn. 4:2.1.2

        Notes
        -----
        This equation has been modified for use in RuFaS, it no longer accounts for the fraction of porosity from which
        anions are excluded.

        """
        return soluble_nitrogen_amount * (1 - (exp(-soil_water_runoff_sum/saturation_content))/soil_water_runoff_sum)

    @staticmethod
    def _determine_nitrate_runoff_amount(nitrogen_concentration: float,
                                         runoff: float,
                                         runoff_extraction_coef: float) -> float:
        """This method determines the amount of nitrate runoff for the first layer

        Parameters
        ----------
        nitrogen_concentration: float
            the content of inorganic (nitrate or ammonium) nitrogen in the top soil layer (kg N/mm H20)
        runoff_extraction_coef: float
            coefficient of extraction for runoff (unitless)
        runoff: float
            daily runoff of H2O (mm)

        Returns
        -------
        float:
            the amount of nitrate runoff from the first layer (kg/ha)

        References
        ----------
        SWAT Theoretical documentation eqn. 4:2.1.5

        Notes
        -----
        The SWAT equation uses beta_NO3 as the runoff extraction coefficient (see SWAT Input file .BSN "NPERCO", page
        104). RuFaS instead simplifies the runoff extraction coefficient to be 0.1 for determining nitrate runoff and
        1.0 for ammonium runoff.
        """
        return nitrogen_concentration * runoff * runoff_extraction_coef

    @staticmethod
    def _determine_nitrogen_erosion_concentration(nitrogen_amount: float,
                                                  layer_thickness: float,
                                                  bulk_density: float) -> float:
        """This method calculates the soil nitrogen concentrations for the Fresh, Active, and Stable pools

        Parameters
        ----------
        nitrogen_amount: float
            amount of Fresh, Active, and Stable nitrogen (kg/ha)
        bulk_density: float
    `       bulk density of the soil layer (Mg per cubic meter)

        Returns
        -------
        float
            the soil nitrogen concentrations for the Fresh, Active, and Stable pools in soil(mg/kg)

        References
        ----------
        SWAT Theoretical documentation eqn. 4:2.2.2

        """
        return (100 * nitrogen_amount) / (bulk_density * layer_thickness)

    @staticmethod
    def _determine_erosion_nitrogen_loss_content(nitrogen_erosion_concentration: float,
                                                 daily_soil_lost: float,
                                                 enrichment_ratio: float) -> float:
        """This method determines nitrogen mass loss in erosion

        Parameters
        ----------
        nitrogen_erosion_concentration: float
            the soil nitrogen concentrations for the Fresh, Active, and Stable pools in soil(mg/kg)
        daily_soil_lost: float
            daily soil loss (Metric Tons/ha)
        enrichment_ratio: float
            Enrichment ratio (unitless)

        Returns
        -------
        float
            nitrogen mass loss in erosion (kg/ha)

        References
        ----------
        SWAT Theoretical documentation eqn. 4:2.2.1

        """
        return 0.001 * nitrogen_erosion_concentration * daily_soil_lost * enrichment_ratio

    @staticmethod
    def _determine_enrichment_ratio(daily_soil_lost: float) -> float:
        """This method determines the enrichment ratio

        Parameters
        ----------
        daily_soil_lost: float
            daily soil loss (Metric Tons/ha)

        Returns
        -------
        float
            enrichment ratio (unitless)

        References
        ----------
        pseudocode_soil S.4.C.5

        Notes
        -----
        TODO These numbers are modified ans suspected of retrieved from other references instead of SWAT, kept here
        issue #486

        """
        return exp(1.21 - 0.16 * log(daily_soil_lost * 1000))

    @staticmethod
    def _determine_nitrogen_percolation_water_concentration(nitrogen_content: float,
                                                            field_capacity_content: float,
                                                            percolation_amount: float) -> float:
        """Calculates concentration of nitrogen in the soil water for determining the amount of nitrogen leached between
            soil layers.

        Parameters
        ----------
        nitrogen_content : float
            Amount of nitrogen in a specific pool in this layer of soil (kg / ha)
        field_capacity_content : float
            Amount of water in this soil layer when at field capacity (mm)
        percolation_amount : float
            The amount of water that percolated out of this layer of soil on the current day (mm)

        Returns
        -------
        float
            The concentration of nitrogen in the soil layer for use in calculating the amount of nitrogen leached by
            percolation (kg / mm water)

        References
        ----------
        pseudocode_soil eqn. [S.4.C.6]

        Notes
        -----
        The origin of this equation is currently unknown, but reflects experimentally observed results.
        TODO: find equation, issue #495

        """
        return nitrogen_content / (field_capacity_content + percolation_amount)
