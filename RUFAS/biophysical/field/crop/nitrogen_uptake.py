from typing import Optional

from RUFAS.output_manager import OutputManager
from RUFAS.biophysical.field.crop.crop_data import CropData
from RUFAS.biophysical.field.crop.non_water_uptake import NonWaterUptake
from RUFAS.biophysical.field.soil.soil_data import SoilData


class NitrogenUptake(NonWaterUptake):
    """
    Manages nitrogen incorporation in crops.

    Parameters
    ----------
    crop_data : Optional[CropData], optional
        An instance of `CropData` containing crop specifications and attributes.
        Defaults to a new instance of `CropData` if not provided.
    nutrient_distro_param : float, default 10.0
        Nitrogen uptake distribution parameter (unitless).
    nutrient_shapes : Optional[List[float]], default None
        Shape coefficients for nitrogen uptake equations (unitless).
    previous_nutrient: Optional[float], default None
        Nitrogen in biomass on the previous day (kg/ha).
    potential_nutrient_uptake : Optional[float], default None
        Potential nitrogen uptake under ideal conditions (kg/ha).
    layer_nutrient_potentials : Optional[float], default None
        Potential nitrogen uptake from each soil layer (kg/ha).
    unmet_nutrient_demands : Optional[float], default None
        Unmet nitrogen demands by overlaying soil layers (kg/ha).
    nutrient_requests : Optional[float], default None
        Nitrogen requested from each soil layer (kg/ha).
    actual_nutrient_uptakes : Optional[List[float]], default None
        Actual nitrogen uptake from each soil layer (kg/ha).
    total_nutrient_uptake : Optional[float], default None
        Total nitrogen uptake by the plant (kg/ha).
    fixed_nitrogen : Optional[float], default None
        Total nitrogen fixed by the plant (kg/ha).
    nitrate_factor : Optional[float], default None
        Soil nitrate factor (unitless).
    fixation_stage_factor : Optional[float], default None
        Growth stage factor for nitrogen-fixing symbiotes (unitless).

    Attributes
    ----------
    nutrient_distro_param : float
        Nitrogen uptake distribution parameter (unitless).
    nutrient_shapes : Optional[List[float]]
        Shape coefficients for nitrogen uptake equations (unitless).
    previous_nutrient : Optional[float]
        Nitrogen in biomass on the previous day (kg/ha).
    potential_nutrient_uptake : Optional[float]
        Potential nitrogen uptake under ideal conditions (kg/ha).
    layer_nutrient_potentials : Optional[float]
        Potential nitrogen uptake from each soil layer (kg/ha).
    unmet_nutrient_demands : Optional[float]
        Unmet nitrogen demands by overlaying soil layers (kg/ha).
    nutrient_requests : Optional[float]
        Nitrogen requested from each soil layer (kg/ha).
    actual_nutrient_uptakes : Optional[List[float]]
        Actual nitrogen uptake from each soil layer (kg/ha).
    total_nutrient_uptake : Optional[float]
        Total nitrogen uptake by the plant (kg/ha).
    fixed_nitrogen : Optional[float]
        Total nitrogen fixed by the plant (kg/ha).
    nitrate_factor : Optional[float]
        Soil nitrate factor (unitless).
    fixation_stage_factor : Optional[float]
        Growth stage factor for nitrogen-fixing symbiotes (unitless).

    References
    ----------
    'Nitrogen Uptake' section (5:2.3.1) of the SWAT model.

    """

    def __init__(
        self,
        crop_data: Optional[CropData] = None,
        nutrient_distro_param: float = 10.0,
        nutrient_shapes: Optional[list[float]] = None,
        previous_nutrient: Optional[float] = None,
        potential_nutrient_uptake: Optional[float] = None,
        layer_nutrient_potentials: Optional[float] = None,
        unmet_nutrient_demands: Optional[float] = None,
        nutrient_requests: Optional[float] = None,
        actual_nutrient_uptakes: Optional[list[float]] = None,
        total_nutrient_uptake: Optional[float] = None,
        fixed_nitrogen: Optional[float] = None,
        nitrate_factor: Optional[float] = None,
        fixation_stage_factor: Optional[float] = None,
    ):
        super().__init__(
            crop_data,
            nutrient_distro_param,
            nutrient_shapes,
            previous_nutrient,
            potential_nutrient_uptake,
            layer_nutrient_potentials,
            unmet_nutrient_demands,
            nutrient_requests,
            actual_nutrient_uptakes,
            total_nutrient_uptake,
        )
        self.fixed_nitrogen = fixed_nitrogen
        self.nitrate_factor = nitrate_factor
        self.fixation_stage_factor = fixation_stage_factor

    def uptake(self, soil_data: SoilData) -> None:
        """
        Main nitrogen incorporation function that runs all nitrogen processes and stores nitrogen as biomass.

        Parameters
        ----------
        soil_data : SoilData
            The SoilData object that tracks soil properties and nitrogen content.

        Notes
        -----
        Calling this function executes all nitrogen incorporation routines. It calculates the amount of nitrogen
        the plant desires based on its current growth stage and the available nitrogen in the soil. The function
        then extracts nitrogen from the accessible soil profile. If there's any unmet nitrogen demand, the plant
        may attempt to fix atmospheric nitrogen. The nitrogen from both extraction and fixation is then added to
        the plant's biomass, contributing to its growth.

        """
        self.uptake_main_process(soil_data, "nitrogen", "nitrate_content")

        layer_nitrates = soil_data.get_vectorized_layer_attribute("nitrate_content")
        total_accessible_nitrates = sum(self.access_layers(layer_nitrates))
        soil_water_factor = soil_data.soil_water_factor
        self.try_fixation(total_accessible_nitrates, soil_water_factor)

        self.crop_data.nitrogen = self.determine_stored_nutrient(
            self.total_nutrient_uptake,
            self.crop_data.nitrogen,
            self.fixed_nitrogen,
        )

    def try_fixation(self, total_accessible_nitrates: float, soil_water_factor: float) -> None:
        """
        Attempts to fix nitrogen if the plant is capable of nitrogen fixation.

        Parameters
        ----------
        total_accessible_nitrates : float
            The total amount of nitrates accessible to the plant's roots (kg/ha).
        soil_water_factor : float
            A factor representing the availability of water in the soil, affecting the plant's ability to fix nitrogen
            (unitless).

        Notes
        -----
        If the plant species is a nitrogen fixer, this method simulates the fixation of atmospheric nitrogen, enhancing
        the nitrogen content available to the plant. If the plant is not a nitrogen fixer, no action is taken, and the
        method does not affect the plant or soil properties. The humorous note implies that non-nitrogen fixing plants
        do not adversely affect themselves when this method is called.

        """
        if self.crop_data.is_nitrogen_fixer:
            self.update_fixation_attributes(total_accessible_nitrates)
            self.fix_nitrogen(soil_water_factor)
        else:
            self.fixed_nitrogen = 0

    def update_fixation_attributes(self, total_accessible_nitrates: float) -> None:
        """
        Updates attributes necessary for nitrogen fixation.

        Parameters
        ----------
        total_accessible_nitrates : float
            The total nitrates accessible to the plant's roots.

        """
        self.nitrate_factor = self._determine_nitrate_factor(total_accessible_nitrates)
        self.fixation_stage_factor = self._determine_fixation_stage_factor(self.crop_data.heat_fraction)

    def fix_nitrogen(self, water_factor: float) -> None:
        """
        Fixes nitrogen, based on any remaining demand not met by actual uptake.

        Parameters
        ----------
        water_factor : float
            A factor representing the availability of water in the soil, affecting the efficiency of nitrogen fixation
            (unitless).

        """
        unmet_demand = self.potential_nutrient_uptake - self.total_nutrient_uptake
        if unmet_demand > 0:
            self.fixed_nitrogen = self._determine_fixed_nitrogen(
                unmet_demand,
                stage_factor=self.fixation_stage_factor,
                water_factor=water_factor,
                nitrate_factor=self.nitrate_factor,
            )
        else:
            self.fixed_nitrogen = 0

    @staticmethod
    def _determine_nitrate_factor(total_accessible_nitrates: float) -> float:
        """
        Calculates soil nitrate factor.

        Parameters
        ----------
        total_accessible_nitrates : float
            Total nitrates available in the soil layers accessible to roots (kg nitrate / ha).

        Returns
        -------
        float
            The soil nitrate factor, in the range [0.0, 1.0].

        References
        ----------
        SWAT Theoretical documentation equations 5:2.3.15, 5:2.3.16, 5:2.3.17

        Notes
        -----
        Equation 5:2.3.16 in the SWAT Theoretical documentation (and associated SWAT code in the file nfix.f) is
        seemingly wrong. This equation originates from the EPIC model (see line 31 of NFIX.f90). Also note that in EPIC,
        the total accessible nitrates in the soil profile are divided by the amount of residue (`RD(JKK)`), which RuFaS
        does not do.

        """
        if total_accessible_nitrates <= 100:
            return 1
        elif total_accessible_nitrates <= 300:
            return 1.5 - (0.005 * total_accessible_nitrates)
        else:
            return 0

    @staticmethod
    def _determine_fixation_stage_factor(heat_fraction: float) -> float:
        """
        Calculates the fixation symbiotic growth stage factor.

        Parameters
        ----------
        heat_fraction : float
            The accumulated fraction of potential heat units (PHU).

        Returns
        -------
        float
            The growth stage factor for symbiotic organisms involved in nitrogen fixation (unitless).

        Notes
        -----
        The symbiotic organisms that fix nitrogen exist at different densities depending upon the age of the plant. This
        growth stage factor reflects the density and activity level of these symbiotic organisms relative to the plant's
        growth stage.

        References
        ----------
        SWAT 2:2.3.10 - 2:2.3.14

        """
        if heat_fraction <= 0.15:
            return 0

        elif heat_fraction <= 0.3:
            return (6.67 * heat_fraction) - 1

        elif heat_fraction <= 0.55:
            return 1

        elif heat_fraction <= 0.75:
            return 3.75 - (5 * heat_fraction)

        else:
            return 0

    @staticmethod
    def _determine_fixed_nitrogen(
        demand: float, stage_factor: float, water_factor: float, nitrate_factor: float
    ) -> float:
        """
        Calculates the amount of nitrogen fixed by a plant.

        Parameters
        ----------
        demand : float
            Nitrogen demand not met by uptake from soil (kg/ha).
        stage_factor : float
            Growth stage factor, ranging from 0 to 1 (unitless).
        water_factor : float
            Soil water factor, ranging from 0 to 1 (unitless).
        nitrate_factor : float
            Soil nitrate factor, ranging from 0 to 1 (unitless).

        Returns
        -------
        float
            The amount of nitrogen added to plant biomass through fixation, capped at the demand (kg/ha).

        References
        ----------
        SWAT 5:2.3.9

        """
        info_map = {
            "class": NitrogenUptake.__class__.__name__,
            "function": NitrogenUptake._determine_fixed_nitrogen.__name__,
        }
        om = OutputManager()
        if not 0 <= stage_factor <= 1:
            om.add_error(
                "Invalid stage_factor.", f"stage_factor must be between 0 and 1, received {stage_factor}.", info_map
            )
            raise ValueError("stage_factor must be between 0 and 1")
        if not 0 <= water_factor <= 1:
            om.add_error(
                "Invalid water_factor.", f"water_factor must be between 0 and 1, received {water_factor}.", info_map
            )
            raise ValueError("water_factor must be between 0 and 1")
        if not 0 <= nitrate_factor <= 1:
            om.add_error(
                "Invalid nitrate_factor.",
                f"nitrate_factor must be between 0 and 1, received {nitrate_factor}.",
                info_map,
            )
            raise ValueError("nitrate_factor must be between 0 and 1")

        fixed = demand * stage_factor * min(water_factor, nitrate_factor, 1)
        return min(fixed, demand)
