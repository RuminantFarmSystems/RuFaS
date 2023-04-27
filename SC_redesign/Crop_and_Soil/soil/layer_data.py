from dataclasses import dataclass, field, InitVar
from typing import Optional
from math import log, exp

from SC_redesign.Crop_and_Soil.crop_and_soil_constants import MEGAGRAMS_TO_KILOGRAMS, HECTARES_TO_SQUARE_MILLIMETERS, \
    CUBIC_MILLIMETERS_TO_CUBIC_METERS, KILOGRAMS_TO_MILLIGRAMS, MILLIGRAMS_TO_KILOGRAMS, \
    FRACTION_OF_HUMIC_NITROGEN_IN_ACTIVE_POOL

"""
Each instance of this class represents a layer of soil. Each SoilData object should contain a list of LayerData objects
to represent its soil
"""


@dataclass
class LayerData:
    field_size: InitVar[float] = None
    """Size of the field (ha)
        Note: this attribute is only used for initialization. After that it cannot be used.
    """
    residue: InitVar[float] = 0
    """Amount of residue on the soil surface when this soil layer is initialized (kg / ha)
        Note: this attribute is only used for initialization. After that it cannot be used.
    """
    top_depth: Optional[float] = None
    """top depth of the layer (mm)"""
    bottom_depth: Optional[float] = None
    """bottom depth of the layer (mm)"""
    soil_water_concentration: float = 0.25  # arbitrary
    """soil water concentration of the layer (mm)"""
    water_content: float = field(init=False)
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
    percolated_water: float = 0
    """Amount of water that percolated out of the soil layer on the current day (mm)"""

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
    """plant metabolic carbon decomposed into active carbon (kg/ha) (pseudocode_soil S.6.B.I.)"""
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
    initial_labile_inorganic_phosphorus_concentration: float = None
    """Concentration of labile inorganic phosphorus at the beginning of the simulation (mg / kg soil)
        Note: default = 25, is from page 208 (bottom paragraph) of the SWAT theoretical documentation, and is reasonable
        for soil in the plow layer of cropland.
    """
    mean_phosphorus_sorption_parameter: float = None
    """Parameter that determines the equilibria of the different inorganic phosphorus pools and has been adjusted so it
        is not sensitive to large immediate changes in the soil chemistry (unitless).
        Note: This value is very important, and is used a lot in both SurPhos and SWAT (SurPhos theoretical
        documentation refers to it as the "Phosphorus Sorption Coefficient" - see eqn. [18], and SWAT theoretical
        documentation as the "Phosphorus Availability Index" - section 3:2.1). In SWAT this value is entered by the
        user, but as Pete Vadas found this was not a well understood or easily measured parameter, so SurPhos uses an
        equation to compute it based off other soil attributes.
    """
    labile_inorganic_phosphorus_content: float = 0
    """Labile inorganic phosphorus content of this soil layer (kg / ha)"""
    active_inorganic_phosphorus_content: float = 0
    """Active inorganic phosphorus content of this soil layer (kg / ha)"""
    stable_inorganic_phosphorus_content: float = 0
    """Stable inorganic phosphorus content of this soil layer (kg / ha)"""

    active_inorganic_unbalanced_counter: int = 0
    """The number of days that the active inorganic phosphorus pool has been greater than it would be when in
        equilibrium with the labile inorganic phosphorus pool."""
    labile_inorganic_unbalanced_counter: int = 0
    """The number of days that the labile inorganic phosphorus pool has been greater than the it would be when in
            equilibrium with the active inorganic phosphorus pool."""
    previous_phosphorus_balance: float = None
    """The phosphorus balance on the previous day (unitless)"""

    # --- Residue partition
    plant_metabolic_to_soil_carbon_amount: Optional[float] = None
    """metabolic carbon incorporated into soil during tillage (kg/ha)"""
    plant_structural_carbon_amount: Optional[float] = None
    """amount of plant structural carbon (kg/ha)"""
    plant_metabolic_carbon_amount: Optional[float] = None
    """plant metabolic carbon amount (hg/ha)"""
    tillage_fraction: Optional[float] = None
    """Fraction of metabolic carbon incorporated into soil during tillage (unitless)"""
    # TODO: needs to create a method to update this, not sure where it would be
    structural_carbon_transfer_amount: Optional[float] = None
    """the amount of transfer of structural carbon during tillage (kg/ha)"""
    soil_dry_matter_residue_amount: Optional[float] = None
    """the amount of soil dry matter residue at harvest (kg/ha)"""
    plant_dry_matter_residue_amount: Optional[float] = None
    """the amount of plant dry matter residue at harvest (kg/ha)"""
    plant_residue_metabolic_fraction: Optional[float] = None
    """fraction of plant residue that is metabolic (unitless)"""
    plant_structural_to_slow_or_active_rate: Optional[float] = None
    """the rate at which above ground structural carbon decomposes into slow or active carbon (unitless)"""
    weighted_residue_dry_matter_lignin_fraction: Optional[float] = None
    """the weighted fractional of lignin amount in residue dry matter (unitless)"""
    soil_residue_lignin_fraction: Optional[float] = None
    """the fraction of soil residue that's comprised of lignin (unitless)"""
    soil_lignin_to_nitrogen_fraction: Optional[float] = None
    """soil lignin to nitrogen fraction(unitless)"""
    soil_residue_metabolic_fraction: Optional[float] = None
    """the fraction of soil residue that is metabolic(unitless)"""
    soil_metabolic_carbon_amount: Optional[float] = None
    """soil metabolic carbon amount (kg/ha)"""
    soil_structural_carbon_amount: Optional[float] = None
    """amount of soil structural carbon decomposed into slow or active carbon (kg/ha)"""

    # ---- Nitrogen
    initial_soil_nitrate_concentration: Optional[float] = None
    """Concentration of nitrates in this soil layer at beginning of the simulation (mg / kg soil)"""
    nitrate_content: Optional[float] = None
    """Nitrate (NO3) content of this soil layer (kg / ha)"""
    ammonium_content: float = 0
    """Ammonium (NH4+) content of this soil layer (kg / ha)"""
    active_organic_nitrogen_content: float = field(init=False)
    """Active organic nitrogen content of this soil layer (kg / ha)"""
    stable_organic_nitrogen_content: float = field(init=False)
    """Stable organic nitrogen content of this soil layer (kg / ha)"""
    fresh_organic_nitrogen_content: float = 0
    """Fresh organic nitrogen content of this soil layer (kg / ha)
        Note: all layers except the top layer are initialized with 0 fresh organic nitrogen."""

    humus_mineralization_rate_factor: float = 0.0003
    """Rate factor for humus mineralization of active organic nutrients (nitrogen and phosphorus) (unitless)
        Reference: SWAT Input .BSN file."""

    # --- Carbon cycling
    soil_overall_carbon_fraction: Optional[float] = None
    """the total fraction of carbon in the soil (unitless)"""
    total_soil_carbon_amount: Optional[float] = None
    """the total amount of soil carbon (kg/ha)"""
    annual_decomposition_carbon_CO2_lost: Optional[float] = None
    """amount of total carbon lost as CO2 during decomposition(kg/ha)"""
    annual_carbon_CO2_lost: Optional[float] = None
    """total amount of carbon lost as CO2 (kg/ha)"""

    def __post_init__(self, field_size: float, residue: float):
        """Initialize all attributes in the dataclass that depend on other attributes

        Parameters
        ----------
        field_size: float
            Size of the field (ha)
        residue: float
            Amount of residue on the soil surface when this soil layer is initialized (kg / ha)

        Raises
        ------
        TypeError
            If the field size is None (meaning it likely was not included when the SoilData() object was initialized).
        ValueError
            If the field size specified is not greater than 0.
        ValueError
            If either the top or bottom depths are negative, or the top depth is greater than the bottom depth.

        References
        ----------
        SWAT Theoretical documentation eqn. 3:2.1.1, 2 and last paragraph on page 208 (for phosphorus initialization)

        """
        if self.top_depth < 0 or self.bottom_depth <= 0 or self.top_depth >= self.bottom_depth:
            raise ValueError(f"Expected positive values for top and bottom depths of soil layer where top < bottom, "
                             f"received top: '{self.top_depth}', bottom: '{self.bottom_depth}'.")

        if field_size is None:
            raise TypeError("'field_size' attribute is NoneType, must be given value when LayerData is initialized.")
        elif field_size <= 0:
            raise ValueError(f"Expected field_size to be greater than 0, received '{field_size}'.")

        self.water_content = self.soil_water_concentration * self.layer_thickness

        # ---- Phosphorus initialization operations --------------------------------------------------------------------
        if self.initial_labile_inorganic_phosphorus_concentration is None:
            self.initial_labile_inorganic_phosphorus_concentration = 25

        self.mean_phosphorus_sorption_parameter = self.calculate_phosphorus_sorption_parameter(
            self.percent_clay_content, self.initial_labile_inorganic_phosphorus_concentration,
            self.percent_organic_carbon_content)

        initial_active_inorganic_phosphorus_concentration = \
            self.initial_labile_inorganic_phosphorus_concentration * \
            ((1 - self.mean_phosphorus_sorption_parameter) / self.mean_phosphorus_sorption_parameter)
        initial_stable_inorganic_phosphorus_concentration = 4 * initial_active_inorganic_phosphorus_concentration

        self.labile_inorganic_phosphorus_content = self.determine_soil_nutrient_area_density(
            self.initial_labile_inorganic_phosphorus_concentration, self.bulk_density, self.layer_thickness, field_size)
        self.active_inorganic_phosphorus_content = self.determine_soil_nutrient_area_density(
            initial_active_inorganic_phosphorus_concentration, self.bulk_density, self.layer_thickness, field_size)
        self.stable_inorganic_phosphorus_content = self.determine_soil_nutrient_area_density(
            initial_stable_inorganic_phosphorus_concentration, self.bulk_density, self.layer_thickness, field_size)
        # --------------------------------------------------------------------------------------------------------------

        self._initialize_nitrogen_pools(field_size, residue)

    def _initialize_nitrogen_pools(self, field_size: float, residue: float) -> None:
        """Initializes the nitrogen pools in the soil layer

        Parameters
        ----------
        field_size: float
            Size of the field (ha)
        residue: float
            Amount of residue on the soil surface when this soil layer is initialized (kg / ha)

        References
        ----------
        SWAT Theoretical documentation eqn. 3:1.1.1 - 5 and paragraph beneath eqn. 3:1.1.4

        Notes
        -----
        The active humic nitrogen fraction is defined as 0.02 in the SWAT Theoretical documentation page 186, beneath
        eqn. 3:1.1.4.

        """
        if self.initial_soil_nitrate_concentration is None:
            # SWAT eqn. 3:1.1.1
            self.initial_soil_nitrate_concentration = 7 * exp(-1 * self.depth_of_layer_center / 1000)

        self.nitrate_content = self.determine_soil_nutrient_area_density(self.initial_soil_nitrate_concentration,
                                                                         self.bulk_density, self.layer_thickness,
                                                                         field_size)

        # SWAT eqn. 3:1.1.2
        humic_organic_nitrogen_concentration = (10 ** 4) * (self.percent_organic_carbon_content / 14)

        initial_active_organic_nitrogen_concentration = humic_organic_nitrogen_concentration * \
            FRACTION_OF_HUMIC_NITROGEN_IN_ACTIVE_POOL         # SWAT eqn. 3:1.1.3
        initial_stable_organic_nitrogen_concentration = humic_organic_nitrogen_concentration * \
            (1 - FRACTION_OF_HUMIC_NITROGEN_IN_ACTIVE_POOL)    # SWAT eqn. 3:1.1.4

        self.active_organic_nitrogen_content = self.determine_soil_nutrient_area_density(
            initial_active_organic_nitrogen_concentration, self.bulk_density, self.layer_thickness, field_size)
        self.stable_organic_nitrogen_content = self.determine_soil_nutrient_area_density(
            initial_stable_organic_nitrogen_concentration, self.bulk_density, self.layer_thickness, field_size)

        if self.top_depth == 0:
            self.fresh_organic_nitrogen_content = 0.0015 * residue  # SWAT eqn. 3:1.1.5

    def add_to_labile_phosphorus(self, phosphorus_to_add: float, field_size: float) -> None:
        """This method is a wrapper for adding a specified mass of phosphorus to the labile phosphorus content of this
            soil layer.

        Parameters
        ----------
            phosphorus_to_add : float
                Amount of phosphorus to add (kg)
            field_size : float
                Size of the field (ha)

        """
        self.labile_inorganic_phosphorus_content = self._add_phosphorus_to_pool(
            self.labile_inorganic_phosphorus_content, phosphorus_to_add, field_size)

    def add_to_active_phosphorus(self, phosphorus_to_add: float, field_size: float) -> None:
        """This method is a wrapper for adding a specified mass of phosphorus to the active phosphorus content of this
            soil layer.

        Parameters
        ----------
            phosphorus_to_add : float
                Amount of phosphorus to add (kg)
            field_size : float
                Size of the field (ha)

        """
        self.active_inorganic_phosphorus_content = self._add_phosphorus_to_pool(
            self.active_inorganic_phosphorus_content, phosphorus_to_add, field_size)

    @staticmethod
    def _add_phosphorus_to_pool(pool_to_add_to: float, phosphorus_to_add: float, field_size: float) -> float:
        """This is a generic method to be used by wrapper functions to add phosphorus to any of the phosphorus pools.

        Parameters
        ----------
        pool_to_add_to : float
            The phosphorus pool in this soil layer that is having phosphorus added (kg / ha)
        phosphorus_to_add : float
            Amount of phosphorus to add (kg)
        field_size : float
            Size of the field (ha)

        Returns
        -------
        float
            The new value of the phosphorus pool that was added to (kg / ha)

        Notes
        -----
        Before adding the new phosphorus to the specified pool, it first extracts the current amount of phosphorus
        in the pool in kg, then adds the new phosphorus, and then converts the new amount of phosphorus from kg to kg
        per ha.

        """
        phosphorus_pool_amount = pool_to_add_to * field_size
        phosphorus_pool_amount += phosphorus_to_add
        return phosphorus_pool_amount / field_size

    @staticmethod
    def calculate_phosphorus_sorption_parameter(percent_clay_content: float, labile_inorganic_phosphorus: float,
                                                percent_organic_carbon_content: float) -> float:
        """Calculates the phosphorus sorption coefficient based on the current soil conditions.

        Parameters
        ----------
        percent_clay_content : float
            Percent of this soil layer that is clay, expressed in range [0, 100] (unitless)
        labile_inorganic_phosphorus : float
            Amount of labile inorganic phosphorus in this soil layer (mg / kg soil)
        percent_organic_carbon_content : float
            Percent of this soil layer that is organic carbon, expressed in range [0, 100] (unitless)

        Returns
        -------
        float
            The phosphorus sorption parameter based on how much clay, organic carbon, and labile inorganic phosphorus
            are in the soil layer.

        References
        ----------
        SurPhos theoretical documentation eqn. [18], APLE theoretical documentation paragraph below eqn. [11]

        Notes
        -----
        The upper bound used here is 0.7 instead of 0.9 as specified in the APLE theoretical documentation, because 0.7
        is used in the SurPhos code (see pminrl.f, line 49).

        """
        adjusted_clay_content = max(10 ** -8, percent_clay_content)
        first_term = -0.045 * log(adjusted_clay_content)
        second_term = 0.001 * labile_inorganic_phosphorus
        third_term = 0.035 * percent_organic_carbon_content
        return max(0.05, min(0.7, first_term + second_term - third_term + 0.43))

    @staticmethod
    def determine_soil_phosphorus_concentration(labile_phosphorus: float, bulk_density: float,
                                                layer_thickness: float, field_size: float) -> float:
        """Calculates the concentration of phosphorus in a soil layer.

        Parameters
        ----------
        labile_phosphorus : float
            Labile phosphorus content of this soil layer (kg / ha)
        bulk_density : float
            Bulk density of the soil layer (Megagram / cubic meter)
        layer_thickness : float
            Thickness of the soil layer (mm)
        field_size : float
            Area of the field (ha)

        Returns
        -------
        float
            The concentration of phosphorus in the soil layer (mg phosphorous / kg soil)

        """
        soil_volume_in_cubic_meters = layer_thickness * (field_size * HECTARES_TO_SQUARE_MILLIMETERS) * \
            CUBIC_MILLIMETERS_TO_CUBIC_METERS
        soil_mass_in_kg = bulk_density * MEGAGRAMS_TO_KILOGRAMS * soil_volume_in_cubic_meters
        soil_phosphorus_mass_in_mg = labile_phosphorus * field_size * KILOGRAMS_TO_MILLIGRAMS
        return soil_phosphorus_mass_in_mg / soil_mass_in_kg

    @staticmethod
    def determine_soil_nutrient_area_density(nutrient_concentration: float, bulk_density: float,
                                             layer_thickness: float, field_size: float) -> float:
        """Converts a concentration of nutrients in the soil from (mg / kg soil) to (kg / ha)

        Parameters
        ----------
        nutrient_concentration : float
            Nutrient concentration of this soil layer (mg / kg soil)
        bulk_density : float
            Bulk density of the soil layer (Megagram / cubic meter)
        layer_thickness : float
            Thickness of the soil layer (mm)
        field_size : float
            Area of the field (ha)

        Returns
        -------
        float
            The area concentration of nutrients in the soil layer (kg / ha)

        """
        soil_volume_in_cubic_meters = layer_thickness * (field_size * HECTARES_TO_SQUARE_MILLIMETERS) * \
            CUBIC_MILLIMETERS_TO_CUBIC_METERS
        soil_mass_in_kg = bulk_density * MEGAGRAMS_TO_KILOGRAMS * soil_volume_in_cubic_meters
        total_nutrient_mass_in_kg = nutrient_concentration * soil_mass_in_kg * MILLIGRAMS_TO_KILOGRAMS
        return total_nutrient_mass_in_kg / field_size

    # TODO: coordinate with Matthew to find best place for this so that it can be accessed by multiple modules
    @property
    def calculate_nutrient_cycling_water_factor(self) -> float:
        """The nutrient cycling water factor (unitless)

        References
        ----------
        SWAT eqn. 3:1.2.2

        Notes
        -----
        This factor is lower bounded at 0.05

        """
        return max(0.05, self.water_content / self.field_capacity_content)

    @property
    def calculate_nutrient_cycling_temp_factor(self) -> float:
        """The nutrient cycling temperature factor (unitless)

        References
        ----------
        SWAT eqn. 3:1.2.1

        Notes
        -----
        This factor is lower bounded at 0.1

        """
        second_term = self.temperature / (self.temperature + exp(9.93 - 0.312 * self.temperature))
        factor = 0.9 * second_term + 0.1
        return max(0.1, factor)

    @property
    def available_water_capacity(self):
        """available water capacity of the soil layer (mm)

        SWAT Equation: 5:2.2.6"""
        return self.field_capacity_content - self.wilting_point_content

    @property
    def layer_thickness(self) -> float:
        """thickness of soil layer (mm)"""
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
    def percent_organic_matter_proportion(self) -> float:
        """percent organic matter content of this soil layer

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

    def do_annual_reset(self):
        self.annual_carbon_CO2_lost = 0
        self.annual_decomposition_carbon_CO2_lost = 0
