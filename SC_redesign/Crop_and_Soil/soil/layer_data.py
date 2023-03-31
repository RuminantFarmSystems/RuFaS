from dataclasses import dataclass
from typing import Optional

"""
Each instance of this class represents a layer of soil. Each SoilData object should contain a list of LayerData objects
to represent its soil
"""


@dataclass
class LayerData:
    top_depth: Optional[float] = None
    """top depth of the layer (mm)"""
    bottom_depth: Optional[float] = None
    """bottom depth of the layer (mm)"""
    nitrate: float = 1.5
    """nitrate level of the layer (kg/ha)"""
    phosphate: float = 0.05
    """phosphate content of the layer (kg/ha)"""
    soil_water_concentration: float = 0.25  # arbitrary
    """soil water concentration of the layer (mm)"""
    water_content:  Optional[float] = None
    """water present in the layer (mm)"""
    field_capacity_water_concentration: float = 0.3  # arbitrary
    """water concentration of soil layer at field capacity (mm water / mm soil)"""
    wilting_point_water_concentration: float = 0.2  # arbitrary
    """water concentration of soil layer at wilting point (mm water / mm soil)"""
    saturation_point_water_concentration: float = 0.5
    """water concentration of soil layer at saturation point (mm water / mm soil)"""
    soil_evaporation_compensation_coefficient: float = 1
    """coefficient that allows user to modify depth distribution used to meet the soil evaporative demand (unitless)
        (SWAT 2:2.3.17)"""

    # --- Percolation
    temperature: float = 15.05
    """current temperature of this soil layer (degrees Celsius)"""
    saturated_hydraulic_conductivity: float = 9.5
    """saturated hydraulic conductivity for this layer of soil (mm per hour)"""

    # --- Temperature
    bulk_density: float = 1.4
    """bulk density of the soil layer (Mg per cubic meter) (provided by user, but SWAT 2:3.1.1 has an equation for
        calculating this field as well)"""
    previous_day_temperature: Optional[float] = None
    """temperature of soil layer on the previous day (degrees C)"""

    # --- Erosion
    percent_organic_carbon_content: float = 1.2
    """organic carbon content expressed as percent of soil in this layer (unitless)"""
    percent_clay_content: float = 18.7
    """clay content expressed as percent of soil in this layer (unitless)"""
    percent_sand_content: float = 14.5
    """sand content expressed as percent of soil in this layer (unitless)"""
    percent_silt_content: float = 64.5
    """silt content expressed as percent of soil in this layer (unitless)"""
    percent_rock_content: float = 1
    """rock content expressed as percent of soil in this layer (unitless)"""

    # --- Decomposition
    decomposition_moisture_effect: Optional[float] = None
    """moisture effect on decomposition factor (unitless) (pseudocode_soil S.6.A.2)"""

    # --- pool_gas_partition
    # (pseudocode_soil S.6.A.1)
    plant_metabolic_active_carbon_usage: Optional[float] = None
    """plant metabolic carbon decomposed into active carbon (kg/ha) (pseudocode_soil S.6.B.I.6)"""
    plant_metabolic_active_carbon_loss: Optional[float] = None
    """plant metabolic carbon being lost as carbon dioxide during decomposition into active carbon (kg/ha)"""
    plant_metabolic_active_carbon_remaining: Optional[float] = None
    """plant metabolic carbon decomposed to active carbon after accounting for carbon dioxide loss (kg/ha)"""


    plant_structural_active_carbon_usage: Optional[float] = None
    """plant structural carbon decomposed into active carbon (kg/ha) (pseudocode_soil S.6.B.I.11)"""
    plant_structural_active_carbon_loss: Optional[float] = None
    """plant structural carbon being lost as carbon dioxide during decomposition into active carbon (kg/ha)"""
    plant_structural_active_carbon_remaining: Optional[float] = None
    """plant metabolic carbon decomposed to active carbon after accounting for carbon dioxide loss (kg/ha)"""

    plant_structural_slow_carbon_usage: Optional[float] = None
    """plant structural carbon decomposed into slow carbon (kg/ha) (pseudocode_soil S.6.B.I.11)"""
    plant_structural_slow_carbon_loss: Optional[float] = None
    """plant structural carbon being lost as carbon dioxide during decomposition into slow carbon (kg/ha)"""
    plant_structural_slow_carbon_remaining: Optional[float] = None
    """plant metabolic carbon decomposed to slow carbon after accounting for carbon dioxide loss (kg/ha)"""

    soil_metabolic_active_carbon_usage: Optional[float] = None
    """soil metabolic carbon decomposed into active carbon (kg/ha) (pseudocode_soil S.6.B.II.8)"""
    soil_metabolic_active_carbon_loss: Optional[float] = None
    """soil metabolic carbon being lost as carbon dioxide during decomposition into active carbon (kg/ha)"""
    soil_metabolic_active_carbon_remaining: Optional[float] = None
    """soil metabolic carbon decomposed to active carbon after accounting for carbon dioxide loss (kg/ha)"""

    soil_structural_active_carbon_usage: Optional[float] = None
    """soil structural carbon decomposed into active carbon (kg/ha) (pseudocode_soil S.6.B.II.11)"""
    soil_structural_active_carbon_loss: Optional[float] = None
    """soil structural carbon being lost as carbon dioxide during decomposition into active carbon (kg/ha)"""
    soil_structural_active_carbon_remaining: Optional[float] = None
    """soil structural carbon decomposed to active carbon after accounting for carbon dioxide loss (kg/ha)"""

    soil_structural_slow_carbon_usage: Optional[float] = None
    """soil structural carbon decomposed into slow carbon (kg/ha) (pseudocode_soil S.6.B.II.11)"""
    soil_structural_slow_carbon_loss: Optional[float] = None
    """soil structural carbon being lost as carbon dioxide during decomposition into slow carbon (kg/ha)"""
    soil_structural_slow_carbon_remaining: Optional[float] = None
    """soil structural carbon decomposed to slow carbon after accounting for carbon dioxide loss (kg/ha)"""

    active_carbon_decomposition_rate: Optional[float] = None
    """rate at which active carbon is decomposed into slow or passive carbon and CO2 (%) (pseudocode_soil S.6.C.2)"""
    carbon_lost_adjusted_factor: Optional[float] = None
    """adjusted factor of CO2 loss from the decomposition of active carbon (pseudocode_soil S.6.C.6)"""

    # pseudocode_soil S.6.C.3
    active_carbon_decomposition_amount: Optional[float] = None
    """active carbon decomposed into slow or passive carbon and CO2 (kg/ha)"""
    active_carbon_amount: Optional[float] = None
    """active carbon stored in the soil (kg/ha)"""

    # pseudocode_soil S.6.C.4
    slow_carbon_amount: Optional[float] = None
    """slow carbon stored in the soil (kg/ha)"""
    slow_carbon_decomposition_amount: Optional[float] = None
    """slow carbon decomposed into active or passive carbon and CO2 (kg/ha)"""

    # pseudocode_soil S.6.C.5
    passive_carbon_decomposition_amount: Optional[float] = None
    """passive carbon decomposed into active or passive carbon and CO2 (kg/ha)"""
    passive_carbon_amount: Optional[float] = None
    """passive carbon stored in the soil (kg/ha)"""

    # pseudocode_soil S.6.C.7
    active_carbon_to_slow_amount: Optional[float] = None
    """active carbon decomposed into slow carbon (kg/ha)"""
    active_carbon_to_slow_loss: Optional[float] = None
    """active carbon lost as CO2 during decomposition into slow carbon (kg/ha)"""

    # pseudocode_soil S.6.C.8
    active_carbon_to_passive_amount: Optional[float] = None
    """active carbon decomposed into passive carbon (kg/ha)"""

    # pseudocode_soil S.6.C.9
    slow_to_active_carbon_amount: Optional[float] = None
    """slow carbon decomposed into active carbon (kg/ha)"""
    slow_carbon_co2_lost_amount: Optional[float] = None
    """slow carbon lost as CO2 during decomposition (kg/ha)"""
    slow_to_passive_carbon_amount: Optional[float] = None
    """slow carbon decomposed into passive carbon (kg/ha)"""

    # pseudocode_soil S.6.C.10
    passive_to_active_carbon_amount: Optional[float] = None
    """passive carbon decomposed into active carbon (kg/ha)"""
    passive_carbon_co2_lost_amount: Optional[float] = None
    """passive carbon lost as CO2 during decomposition (kg/ha)"""

    # pseudocode_soil S.6.C.11
    plant_active_decompose_carbon: Optional[float] = None
    """plant carbon decomposed into the active carbon pool (kg/ha)"""
    soil_active_decompose_carbon: Optional[float] = None
    """soil carbon decomposed into the active carbon pool (kg/ha)"""

    # --- Phosphorus
    labile_phosphorus_content: float = 0
    """Labile phosphorus content of this soil layer (kg phosphorus / ha)"""
    active_phosphorus_content: float = 0
    """Active phosphorus content of this soil layer (kg phosphorus / ha)"""

    # --- Residue partition
    plant_metabolic_to_soil_carbon_amount: Optional[float] = None
    """metabolic carbon incorporated into soil during tillage (kg/ha)"""

    def __post_init__(self):
        """Initialize all attributes in the dataclass that depend on other attributes"""
        self.water_content = self.soil_water_concentration * self.layer_thickness

    @property
    def layer_thickness(self) -> float:
        """thickness of soil layer (mm)"""
        if self.top_depth < 0 or self.bottom_depth <= 0 or self.top_depth >= self.bottom_depth:
            raise ValueError(f"Expected positive values for top and bottom depths of soil layer where top < bottom, "
                             f"received top: '{self.top_depth}', bottom: '{self.bottom_depth}'.")
        return self.bottom_depth - self.top_depth

    @property
    def depth_of_layer_center(self) -> float:
        """depth beneath the surface of the center this layer (mm)"""
        return self.top_depth + (self.layer_thickness / 2)

    @property
    def field_capacity_content(self) -> float:
        """volume of water in layer when at field capacity (mm)"""
        return self.field_capacity_water_concentration * self.layer_thickness

    @property
    def wilting_point_content(self) -> float:
        """amount of water in layer when at wilting point (mm)"""
        return self.wilting_point_water_concentration * self.layer_thickness

    @property
    def saturation_content(self) -> float:
        """volume of water in layer when saturated (mm)"""
        return self.saturation_point_water_concentration * self.layer_thickness

    @property
    def excess_water_available(self) -> float:
        """volume of water available for percolation in the soil layer (mm)
        SWAT Reference: 2:3.2.1, 2
        """
        return max(0.0, self.water_content - self.field_capacity_content)

    @property
    def acceptable_percolation_amount(self) -> float:
        """volume of water that can be accepted by layer before reaching saturation (mm)"""
        return max(0.0, self.saturation_content - self.water_content)

    @property
    def percent_organic_matter_content(self) -> float:
        """percent organic matter content of this soil layer
        TODO: remove this field from all the soil inputs, because the given values for OM_percent are not equal to value
            that SWAT would calculate based on the percent organic carbon content
        SWAT Reference: 4:1.1.4
        """
        return 1.72 * self.percent_organic_carbon_content

    @property
    def soil_water_content(self):
        """volume of soil water in the layer (mm)"""
        return self.soil_water_concentration / self.layer_thickness

    @property
    def water_factor(self):
        """relative water saturation (%)"""

        # pseudocode_soil S.4.B.1
        if self.soil_water_content <= self.field_capacity_content:
            return (self.soil_water_content - self.wilting_point_content) / (
                    self.field_capacity_content - self.wilting_point_content)
        else:
            return (self.saturation_content - self.soil_water_content) / (
                    self.saturation_content - self.field_capacity_content)

    @property
    def silt_clay_content(self):
        """silt and clay fraction in the soil (unitless)"""
        return self.percent_silt_content / self.percent_clay_content
