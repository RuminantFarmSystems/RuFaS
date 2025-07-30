from dataclasses import InitVar, dataclass, field
from math import exp, log
from typing import Optional

from RUFAS.general_constants import GeneralConstants
from RUFAS.user_constants import UserConstants


@dataclass
class LayerData:
    """
    Each instance of this class represents a layer of soil. Each SoilData object should contain a list of LayerData
    objects to represent its soil.

    Attributes
    ----------
    field_size : InitVar[float], optional
        Size of the field (ha). Note: this attribute is only used for initialization. After that, it cannot be used.
    residue : InitVar[float], optional
        Amount of residue on the soil surface when this soil layer is initialized (kg / ha). Note: this attribute is
        only used for initialization. After that, it cannot be used.
    top_depth : float, optional
        Top depth of the layer (mm).
    bottom_depth : float, optional
        Bottom depth of the layer (mm).
    pH : float, default 7.0
        pH of the soil layer.
    soil_water_concentration : float, optional, default 0.25
        Soil water concentration of the layer (mm water / mm soil).
    water_content : float, optional
        Water present in the layer (mm).
    field_capacity_water_concentration : float, optional, default 0.3
        Water concentration of soil layer at field capacity (mm water / mm soil).
    wilting_point_water_concentration : float, optional, default 0.2
        Water concentration of soil layer at wilting point (mm water / mm soil).
    saturation_point_water_concentration : float, optional, default 0.5
        Water concentration of soil layer at saturation point (mm water / mm soil).
    evaporated_water_content : float, optional, default 0.0
        Amount of water that evaporated out of the layer on the current day (mm).
    soil_evaporation_compensation_coefficient : float, optional, default 1.0
        Coefficient that allows the user to modify depth distribution used to meet the soil evaporative demand
        (unitless).
    temperature : float, optional, default 15.05
        Current temperature of this soil layer (degrees Celsius).
    saturated_hydraulic_conductivity : float, optional, default 9.5
        Saturated hydraulic conductivity for this layer of soil (mm per hour).
    percolated_water : float, default 0.0
        Amount of water that percolated out of the soil layer on the current day (mm).
    bulk_density : float, default 1.4
        Bulk density of the soil layer (Mg per cubic meter) (provided by user, but SWAT 2:3.1.1 has an equation for
        calculating this field as well).
    previous_day_temperature : float, optional, default None
        Temperature of soil layer on the previous day (degrees C).
    decomposition_temperature_effect : float, optional, default None
        Temperature effect on decomposition factor (unitless) (pseudocode_soil S.6.A.1).
    organic_carbon_fraction : float, default 0.012
        Organic carbon content expressed as fraction of soil in this layer (unitless).
    clay_fraction : float, default 0.187
        Clay content expressed as fraction of soil in this layer (unitless).
    sand_fraction : float, default 0.145
        Sand content expressed as fraction of soil in this layer (unitless).
    silt_fraction : float, default 0.645
        Silt content expressed as fraction of soil in this layer (unitless).
    rock_fraction : float, default 0.01
        Rock content expressed as fraction of soil in this layer (unitless).
    decomposition_moisture_effect : float, default 0.0
        Moisture effect on decomposition factor (unitless) (pseudocode_soil S.6.A.2).
    plant_metabolic_active_carbon_usage : float, default 0.0
        Plant metabolic carbon decomposed into active carbon (kg/ha) (pseudocode_soil S.6.B.I.).
    plant_metabolic_active_carbon_loss : float, default 0.0
        Plant metabolic carbon being lost as carbon dioxide during decomposition into active carbon (kg/ha).
    plant_metabolic_active_carbon_remaining : float, default 0.0
        Plant metabolic carbon decomposed to active carbon after accounting for carbon dioxide loss (kg/ha).
    plant_structural_active_carbon_usage : float, default 0.0
        Plant structural carbon decomposed into active carbon (kg/ha) (pseudocode_soil S.6.B.I.11).
    plant_structural_active_carbon_loss : float, default 0.0
        Plant structural carbon being lost as carbon dioxide during decomposition into active carbon (kg/ha).
    plant_structural_active_carbon_remaining : float, default 0.0
        Plant structural carbon decomposed to active carbon after accounting for carbon dioxide loss (kg/ha).
    plant_structural_slow_carbon_usage : float, default 0.0
        Plant structural carbon decomposed into slow carbon (kg/ha) (pseudocode_soil S.6.B.I.11).
    plant_structural_slow_carbon_loss : float, default 0.0
        Plant structural carbon being lost as carbon dioxide during decomposition into slow carbon (kg/ha).
    plant_structural_slow_carbon_remaining : float, default 0.0
        Plant structural carbon decomposed to slow carbon after accounting for carbon dioxide loss (kg/ha).
    soil_metabolic_active_carbon_usage : float, default 0.0
        Soil metabolic carbon decomposed into active carbon (kg/ha) (pseudocode_soil S.6.B.II.8).
    soil_metabolic_active_carbon_loss : float, default 0.0
        Soil metabolic carbon being lost as carbon dioxide during decomposition into active carbon (kg/ha).
    soil_metabolic_active_carbon_remaining : float, default 0.0
        Soil metabolic carbon decomposed to active carbon after accounting for carbon dioxide loss (kg/ha).
    soil_structural_active_carbon_usage : float, default 0.0
        Soil structural carbon decomposed into active carbon (kg/ha) (pseudocode_soil S.6.B.II.11).
    soil_structural_active_carbon_loss : float, default 0.0
        Soil structural carbon being lost as carbon dioxide during decomposition into active carbon (kg/ha).
    soil_structural_active_carbon_remaining : float, default 0.0
        Soil structural carbon decomposed to active carbon after accounting for carbon dioxide loss (kg/ha).
    soil_structural_slow_carbon_usage : float, default 0.0
        Soil structural carbon decomposed into slow carbon after accounting for carbon dioxide loss (kg/ha)
        (pseudocode_soil S.6.B.II.11).
    soil_structural_slow_carbon_loss : float, default 0.0
        Soil structural carbon being lost as carbon dioxide during decomposition into slow carbon (kg/ha).
    soil_structural_slow_carbon_remaining : float, default 0.0
        Soil structural carbon decomposed to slow carbon after accounting for carbon dioxide loss (kg/ha).
    active_carbon_decomposition_rate : float, default 0.0
        Rate at which active carbon is decomposed into slow or passive carbon and CO2 (%) (pseudocode_soil S.6.C.2).
    carbon_lost_adjusted_factor : float, default 0.0
        Adjusted factor of CO2 loss from the decomposition of active carbon (pseudocode_soil S.6.C.6).
    active_carbon_decomposition_amount : float, default 0.0
        Active carbon decomposed into slow or passive carbon and CO2 (kg/ha).
    active_carbon_amount : float, default None
        Active carbon stored in the layer (kg/ha).
    slow_carbon_amount : float, optional, default None
        Slow carbon stored in the soil (kg/ha).
    slow_carbon_decomposition_amount : float, default 0.0
        Slow carbon decomposed into active or passive carbon and CO2 (kg/ha).
    passive_carbon_decomposition_amount : float, default 0.0
        Passive carbon decomposed into active or passive carbon and CO2 (kg/ha).
    passive_carbon_amount : float, optional, default None
        Passive carbon stored in the soil (kg/ha).
    active_carbon_to_slow_amount : float, default 0.0
        Active carbon decomposed into slow carbon (kg/ha).
    active_carbon_to_slow_loss : float, default 0.0
        Active carbon lost as CO2 during decomposition into slow carbon (kg/ha).
    active_carbon_to_passive_amount : float, default 0.0
        Active carbon decomposed into passive carbon (kg/ha).
    slow_to_active_carbon_amount : float, default 0.0
        Slow carbon decomposed into active carbon (kg/ha).
    slow_carbon_co2_lost_amount : float, default 0.0
        Slow carbon lost as CO2 during decomposition (kg/ha).
    slow_to_passive_carbon_amount : float, default 0.0
        Slow carbon decomposed into passive carbon (kg/ha).
    passive_to_active_carbon_amount : float, default 0.0
        Passive carbon decomposed into active carbon (kg/ha).
    passive_carbon_co2_lost_amount : float, default 0.0
        Passive carbon lost as CO2 during decomposition (kg/ha).
    plant_active_decompose_carbon : float, default 0.0
        Plant carbon decomposed into the active carbon pool (kg/ha).
    soil_active_decompose_carbon : float, default 0.0
        Soil carbon decomposed into the active carbon pool (kg/ha).
    initial_labile_inorganic_phosphorus_concentration : float, default None
        Concentration of labile inorganic phosphorus at the beginning of the simulation (mg/kg soil).
        Note: default = 25, is from page 208 (bottom paragraph) of the SWAT theoretical documentation, and is reasonable
        for soil in the plow layer of cropland.
    mean_phosphorus_sorption_parameter : float, default None
        Parameter that determines the equilibria of the different inorganic phosphorus pools and has been adjusted so it
        is not sensitive to large immediate changes in the soil chemistry (unitless).
        Note: This value is very important, and is used a lot in both SurPhos and SWAT (SurPhos theoretical
        documentation refers to it as the "Phosphorus Sorption Coefficient" - see eqn. [18], and SWAT theoretical
        documentation as the "Phosphorus Availability Index" - section 3:2.1). In SWAT this value is entered by the
        user, but as Pete Vadas found this was not a well understood or easily measured parameter, so SurPhos uses an
        equation to compute it based off other soil attributes.
    labile_inorganic_phosphorus_content : float, default 0
        Labile inorganic phosphorus content of this soil layer (kg/ha).
    active_inorganic_phosphorus_content : float, default 0
        Active inorganic phosphorus content of this soil layer (kg/ha).
    stable_inorganic_phosphorus_content : float, default 0
        Stable inorganic phosphorus content of this soil layer (kg/ha).
    fresh_organic_phosphorus_content : float, default 0
        Fresh organic phosphorus content of this soil layer (kg/ha).
    active_inorganic_unbalanced_counter : int, default 0
        The number of days that the active inorganic phosphorus pool has been greater than it would be when in
        equilibrium with the labile inorganic phosphorus pool.
    labile_inorganic_unbalanced_counter : int, default 0
        The number of days that the labile inorganic phosphorus pool has been greater than it would be when in
        equilibrium with the active inorganic phosphorus pool.
    previous_phosphorus_balance : float, default None
        The phosphorus balance on the previous day (unitless).
    percolated_phosphorus : float, default 0.0
        Amount of phosphorus removed from the layer by water percolating out (kg/ha).
    plant_metabolic_to_soil_carbon_amount : float, default 0.0
        Metabolic carbon incorporated into soil during tillage (kg/ha).
    structural_litter_amount : float, default 0.0
        Amount of plant structural carbon (kg/ha).
    metabolic_litter_amount : float, default 0.0
        Plant metabolic carbon amount (hg/ha).
    tillage_fraction : float, default 0.0
        Fraction of metabolic carbon incorporated into soil during tillage (unitless).
    structural_carbon_transfer_amount : float, default 0.0
        The amount of transfer of structural carbon during tillage (kg/ha).
    plant_residue : float, default 0.0
        Residue added to the soil which is to be transferred to the metabolic and structural litter pools (kg/ha).
    soil_dry_matter_residue_amount : float, default 0.0
        The amount of soil dry matter residue at harvest (kg/ha).
    plant_dry_matter_residue_amount : float, default 0.0
        The amount of plant dry matter residue at harvest (kg/ha).
    plant_residue_metabolic_fraction : float, default 0.0
        Fraction of plant residue that is metabolic (unitless).
    plant_structural_to_slow_or_active_rate : float, default 0.0
        The rate at which above-ground structural carbon decomposes into slow or active carbon (unitless).
    weighted_residue_dry_matter_lignin_fraction : float, default 0.0
        The weighted fraction of lignin amount in residue dry matter (unitless).
    soil_residue_lignin_fraction : float, default 0.17
        The fraction of soil residue that's comprised of lignin (unitless).
    soil_lignin_to_nitrogen_fraction : float, default 0.0
        Soil lignin to nitrogen fraction (unitless).
    soil_residue_metabolic_fraction : float, default 0.0
        The fraction of soil residue that is metabolic (unitless).
    soil_metabolic_carbon_amount : float, default 0.0
        Soil metabolic carbon amount (kg/ha).
    soil_structural_carbon_amount : float, default 0.0
        Amount of soil structural carbon decomposed into slow or active carbon (kg/ha).
    soil_structural_to_slow_or_active_rate : float, default 0.0
        The rate at which below-ground structural carbon decomposes into slow or active carbon (unitless).
    initial_soil_nitrate_concentration : float, optional, default None
        Concentration of nitrates in this soil layer at the beginning of the simulation (mg/kg soil).
    initial_soil_ammonium_concentration : float, optional, default None
        Concentration of ammonium in this soil layer at the beginning of the simulation (mg/kg soil).
    nitrate_content : float, optional, default None
        Nitrate (NO3) content of this soil layer (kg/ha).
    ammonium_content : float, optional, default None
        Ammonium (NH4+) content of this soil layer (kg/ha).
    active_organic_nitrogen_content : float, default 0.0
        Active organic nitrogen content of this soil layer (kg/ha).
    stable_organic_nitrogen_content : float, default 0.0
        Stable organic nitrogen content of this soil layer (kg/ha).
    fresh_organic_nitrogen_content : float, default 0.0
        Fresh organic nitrogen content of this soil layer (kg/ha).
        Note: all layers except the top layer are initialized with 0 fresh organic nitrogen.
    nitrous_oxide_emissions : float, default 0.0
        Amount of nitrous oxide emitted from this soil layer on the current day (kg/ha).
    annual_nitrous_oxide_emissions_total : float, default 0.0
        Cumulative total amount of nitrates that have denitrified in a year (kg/ha).
    dinitrogen_emissions : float, default 0.0
        Amount of dinitrogen emitted from this soil layer on the current day (kg/ha).
    ammonium_volatilization_cation_exchange_factor : float, default 0.15
        Exchange factor that accounts for the soil's cation exchange capacity (unitless).
        Reference: SWAT Theoretical documentation eqn. 3:1.3.5.
    ammonia_emissions : float, default 0.0
        Amount of ammonium that volatilized out of the soil layer on the current day (kg/ha).
    annual_ammonia_emissions_total : float, default 0.0
        Cumulative total of ammonium volatilized in this year (kg/ha).
    percolated_nitrates : float, default 0.0
        Amount of nitrates removed from the soil layer by water percolating out (kg/ha).
    percolated_ammonium : float, default 0.0
        Amount of ammonium removed from the soil layer by water percolating out (kg/ha).
    percolated_active_organic_nitrogen : float, default 0.0
        Amount of active organic nitrogen removed from the soil layer by water percolating out (kg/ha).
    soil_overall_carbon_fraction : float, optional, default None
        The total fraction of carbon in the soil (unitless).
    total_soil_carbon_amount : float, optional, default None
        The total amount of soil carbon (kg/ha).
    annual_decomposition_carbon_CO2_lost : float, optional, default None
        Amount of total carbon lost as CO2 during decomposition (kg/ha).
    annual_carbon_CO2_lost : float, optional, default None
        Total amount of carbon lost as CO2 (kg/ha).

    """

    field_size: InitVar[float] = None
    residue: InitVar[float] = 0
    top_depth: Optional[float] = None
    bottom_depth: Optional[float] = None

    pH: float = 7.0

    # --- Water
    soil_water_concentration: float = 0.25  # arbitrary
    water_content: float = field(init=False)
    field_capacity_water_concentration: float = 0.3  # arbitrary
    wilting_point_water_concentration: float = 0.2  # arbitrary
    saturation_point_water_concentration: float = 0.5

    # --- Evaporation
    evaporated_water_content: float = 0.0
    soil_evaporation_compensation_coefficient: float = 1

    # --- Percolation
    temperature: float = 15.05
    saturated_hydraulic_conductivity: float = 9.5
    percolated_water: float = 0

    # --- Temperature
    bulk_density: float = 1.4
    previous_day_temperature: Optional[float] = None
    decomposition_temperature_effect: Optional[float] = None

    # --- Erosion
    organic_carbon_fraction: float = 0.012
    clay_fraction: float = 0.187
    sand_fraction: float = 0.145
    silt_fraction: float = 0.645
    rock_fraction: float = 0.01

    # --- Decomposition
    decomposition_moisture_effect: float = 0.0

    # --- pool_gas_partition
    # (pseudocode_soil S.6.A.1)
    plant_metabolic_active_carbon_usage: float = 0.0
    plant_metabolic_active_carbon_loss: float = 0.0
    plant_metabolic_active_carbon_remaining: float = 0.0

    plant_structural_active_carbon_usage: float = 0.0
    plant_structural_active_carbon_loss: float = 0.0
    plant_structural_active_carbon_remaining: float = 0.0

    plant_structural_slow_carbon_usage: float = 0.0
    plant_structural_slow_carbon_loss: float = 0.0
    plant_structural_slow_carbon_remaining: float = 0.0

    soil_metabolic_active_carbon_usage: float = 0.0
    soil_metabolic_active_carbon_loss: float = 0.0
    soil_metabolic_active_carbon_remaining: float = 0.0

    soil_structural_active_carbon_usage: float = 0.0
    soil_structural_active_carbon_loss: float = 0.0
    soil_structural_active_carbon_remaining: float = 0.0

    soil_structural_slow_carbon_usage: float = 0.0
    soil_structural_slow_carbon_loss: float = 0.0
    soil_structural_slow_carbon_remaining: float = 0.0

    active_carbon_decomposition_rate: float = 0.0
    carbon_lost_adjusted_factor: float = 0.0

    # pseudocode_soil S.6.C.3
    active_carbon_decomposition_amount: float = 0.0
    active_carbon_amount: Optional[float] = None

    # pseudocode_soil S.6.C.4
    slow_carbon_amount: Optional[float] = None
    slow_carbon_decomposition_amount: float = 0.0

    # pseudocode_soil S.6.C.5
    passive_carbon_decomposition_amount: float = 0.0
    passive_carbon_amount: Optional[float] = None

    # pseudocode_soil S.6.C.7
    active_carbon_to_slow_amount: float = 0.0
    active_carbon_to_slow_loss: float = 0.0

    # pseudocode_soil S.6.C.8
    active_carbon_to_passive_amount: float = 0.0

    # pseudocode_soil S.6.C.9
    slow_to_active_carbon_amount: float = 0.0
    slow_carbon_co2_lost_amount: float = 0.0
    slow_to_passive_carbon_amount: float = 0.0

    # pseudocode_soil S.6.C.10
    passive_to_active_carbon_amount: float = 0.0
    passive_carbon_co2_lost_amount: float = 0.0

    # pseudocode_soil S.6.C.11
    plant_active_decompose_carbon: float = 0.0
    soil_active_decompose_carbon: float = 0.0

    # --- Phosphorus
    initial_labile_inorganic_phosphorus_concentration: float = None
    mean_phosphorus_sorption_parameter: float = None
    labile_inorganic_phosphorus_content: float = 0
    active_inorganic_phosphorus_content: float = 0
    stable_inorganic_phosphorus_content: float = 0
    fresh_organic_phosphorus_content: float = 0

    active_inorganic_unbalanced_counter: int = 0
    labile_inorganic_unbalanced_counter: int = 0
    previous_phosphorus_balance: float = None

    percolated_phosphorus: float = 0.0

    # --- Residue partition
    plant_metabolic_to_soil_carbon_amount: float = 0.0
    structural_litter_amount: float = 0.0
    metabolic_litter_amount: float = 0.0
    tillage_fraction: float = 0.0
    structural_carbon_transfer_amount: float = 0.0
    plant_residue: float = 0.0
    soil_dry_matter_residue_amount: float = 0.0
    plant_dry_matter_residue_amount: float = 0.0
    plant_residue_metabolic_fraction: float = 0.0
    plant_structural_to_slow_or_active_rate: float = 0.0
    weighted_residue_dry_matter_lignin_fraction: float = 0.0
    soil_residue_lignin_fraction: float = 0.17
    soil_lignin_to_nitrogen_fraction: float = 0.0
    soil_residue_metabolic_fraction: float = 0.0
    soil_metabolic_carbon_amount: float = 0.0
    soil_structural_carbon_amount: float = 0.0
    soil_structural_to_slow_or_active_rate: float = 0.0

    # ---- Nitrogen
    initial_soil_nitrate_concentration: Optional[float] = None
    initial_soil_ammonium_concentration: Optional[float] = None
    nitrate_content: Optional[float] = None
    ammonium_content: Optional[float] = None
    active_organic_nitrogen_content: float = field(init=False)
    stable_organic_nitrogen_content: float = field(init=False)
    fresh_organic_nitrogen_content: float = 0

    nitrous_oxide_emissions: float = 0.0
    annual_nitrous_oxide_emissions_total: float = 0.0

    dinitrogen_emissions: float = 0.0

    ammonium_volatilization_cation_exchange_factor: float = 0.15

    ammonia_emissions: float = 0.0
    annual_ammonia_emissions_total: float = 0.0

    percolated_nitrates: float = 0.0
    percolated_ammonium: float = 0.0
    percolated_active_organic_nitrogen: float = 0.0

    # --- Carbon cycling
    soil_overall_carbon_fraction: Optional[float] = None
    total_soil_carbon_amount: Optional[float] = None
    annual_decomposition_carbon_CO2_lost: Optional[float] = None
    annual_carbon_CO2_lost: Optional[float] = None

    def __post_init__(self, field_size: float, residue: float):
        """
        Initialize all attributes in the dataclass that depend on other attributes.

        Parameters
        ----------
        field_size: float
            Size of the field (ha).
        residue: float
            Amount of residue on the soil surface when this soil layer is initialized (kg / ha).

        Raises
        ------
        TypeError
            If the field size is None (meaning it likely was not included when the SoilData() object was initialized).
        ValueError
            If the field size specified is not greater than 0.
            If either the top or bottom depths are negative, or the top depth is greater than the bottom depth.

        References
        ----------
        SWAT Theoretical documentation eqn. 3:2.1.1, 2 and last paragraph on page 208 (for phosphorus initialization)

        """
        if self.top_depth < 0 or self.bottom_depth <= 0 or self.top_depth >= self.bottom_depth:
            raise ValueError(
                f"Expected positive values for top and bottom depths of soil layer where top < bottom, "
                f"received top: '{self.top_depth}', bottom: '{self.bottom_depth}'."
            )

        if field_size is None:
            raise TypeError("'field_size' attribute is NoneType, must be given value when LayerData is initialized.")
        elif field_size <= 0:
            raise ValueError(f"Expected field_size to be greater than 0, received '{field_size}'.")

        self.water_content = self.soil_water_concentration * self.layer_thickness

        # ---- Phosphorus initialization operations --------------------------------------------------------------------
        if self.initial_labile_inorganic_phosphorus_concentration is None:
            self.initial_labile_inorganic_phosphorus_concentration = 25

        self.mean_phosphorus_sorption_parameter = self.calculate_phosphorus_sorption_parameter(
            self.clay_fraction,
            self.initial_labile_inorganic_phosphorus_concentration,
            self.organic_carbon_fraction,
        )

        initial_active_inorganic_phosphorus_concentration = self.initial_labile_inorganic_phosphorus_concentration * (
            (1 - self.mean_phosphorus_sorption_parameter) / self.mean_phosphorus_sorption_parameter
        )
        initial_stable_inorganic_phosphorus_concentration = 4 * initial_active_inorganic_phosphorus_concentration

        self.labile_inorganic_phosphorus_content = self.determine_soil_nutrient_area_density(
            self.initial_labile_inorganic_phosphorus_concentration,
            self.bulk_density,
            self.layer_thickness,
            field_size,
        )
        self.active_inorganic_phosphorus_content = self.determine_soil_nutrient_area_density(
            initial_active_inorganic_phosphorus_concentration,
            self.bulk_density,
            self.layer_thickness,
            field_size,
        )
        self.stable_inorganic_phosphorus_content = self.determine_soil_nutrient_area_density(
            initial_stable_inorganic_phosphorus_concentration,
            self.bulk_density,
            self.layer_thickness,
            field_size,
        )
        # --------------------------------------------------------------------------------------------------------------

        self._initialize_nitrogen_pools(field_size, residue)

        self._initialize_carbon_pools(field_size, residue)

    def _initialize_nitrogen_pools(self, field_size: float, residue: float) -> None:
        """
        Initializes the nitrogen pools in the soil layer.

        Parameters
        ----------
        field_size: float
            Size of the field (ha).
        residue: float
            Amount of residue on the soil surface when this soil layer is initialized (kg / ha).

        References
        ----------
        SWAT Theoretical documentation eqn. 3:1.1.1 - 5 and paragraph beneath eqn. 3:1.1.4.

        Notes
        -----
        The active humic nitrogen fraction is defined as 0.02 in the SWAT Theoretical documentation page 186, beneath
        eqn. 3:1.1.4. SWAT does not specify how ammonium levels should be initialized, so this method assumes no
        ammonium is present if the user does not specify an initial amount.

        """
        if self.initial_soil_nitrate_concentration is None:
            # SWAT eqn. 3:1.1.1
            self.initial_soil_nitrate_concentration = 7 * exp(-1 * self.depth_of_layer_center / 1000)

        self.nitrate_content = self.determine_soil_nutrient_area_density(
            self.initial_soil_nitrate_concentration,
            self.bulk_density,
            self.layer_thickness,
            field_size,
        )

        if self.initial_soil_ammonium_concentration is None:
            self.initial_soil_ammonium_concentration = 0.0

        self.ammonium_content = self.determine_soil_nutrient_area_density(
            self.initial_soil_ammonium_concentration,
            self.bulk_density,
            self.layer_thickness,
            field_size,
        )

        # SWAT eqn. 3:1.1.2
        humic_organic_nitrogen_concentration = (10**4) * (
            self.organic_carbon_fraction / 14 * GeneralConstants.FRACTION_TO_PERCENTAGE
        )

        initial_active_organic_nitrogen_concentration = (
            humic_organic_nitrogen_concentration * UserConstants.FRACTION_OF_HUMIC_NITROGEN_IN_ACTIVE_POOL
        )  # SWAT eqn. 3:1.1.3
        initial_stable_organic_nitrogen_concentration = humic_organic_nitrogen_concentration * (
            1 - UserConstants.FRACTION_OF_HUMIC_NITROGEN_IN_ACTIVE_POOL
        )  # SWAT eqn. 3:1.1.4

        self.active_organic_nitrogen_content = self.determine_soil_nutrient_area_density(
            initial_active_organic_nitrogen_concentration,
            self.bulk_density,
            self.layer_thickness,
            field_size,
        )
        self.stable_organic_nitrogen_content = self.determine_soil_nutrient_area_density(
            initial_stable_organic_nitrogen_concentration,
            self.bulk_density,
            self.layer_thickness,
            field_size,
        )

        if self.top_depth == 0:
            self.fresh_organic_nitrogen_content = 0.0015 * residue  # SWAT eqn. 3:1.1.5

    def _initialize_carbon_pools(self, field_size: float, residue: float) -> None:
        """
        Initializes soil carbon pools based on the carbon content fraction of the layer.

        Parameters
        ----------
        field_size : float
            Size of the field (ha).
        residue : float
            Amount of residue on the soil surface when this soil layer is initialized (kg / ha).

        Notes
        -----
        The splits for the initialization of carbon pools are not empirical but generally are
        the same as values used by other models. The 50/50 split between litter pools is
        a heavy abstraction but a more accurate split cannot be predicted without knowing management
        practices prior to initialization.

        """
        soil_volume_in_cubic_meters = (
            self.layer_thickness
            * (field_size * GeneralConstants.HECTARES_TO_SQUARE_MILLIMETERS)
            * GeneralConstants.CUBIC_MILLIMETERS_TO_CUBIC_METERS
        )
        soil_mass_in_kg = self.bulk_density * GeneralConstants.MEGAGRAMS_TO_KILOGRAMS * soil_volume_in_cubic_meters
        self.total_soil_carbon_amount = soil_mass_in_kg * (self.organic_carbon_fraction) / field_size

        if self.top_depth == 0:
            self.active_carbon_amount = 0.02 * self.total_soil_carbon_amount
            self.slow_carbon_amount = 0.98 * self.total_soil_carbon_amount
            self.passive_carbon_amount = 0.0
            self.structural_litter_amount = (1 / 2) * residue
            self.metabolic_litter_amount = (1 / 2) * residue
        else:
            self.active_carbon_amount = 0.02 * self.total_soil_carbon_amount
            self.slow_carbon_amount = 0.54 * self.total_soil_carbon_amount
            self.passive_carbon_amount = 0.44 * self.total_soil_carbon_amount
            self.structural_litter_amount = 0.0
            self.metabolic_litter_amount = 0.0

    def add_to_labile_phosphorus(self, phosphorus_to_add: float, field_size: float) -> None:
        """
        This method is a wrapper for adding a specified mass of phosphorus to the labile phosphorus content of this
        soil layer.

        Parameters
        ----------
        phosphorus_to_add : float
            Amount of phosphorus to add (kg).
        field_size : float
            Size of the field (ha).

        """
        self.labile_inorganic_phosphorus_content = self._add_phosphorus_to_pool(
            self.labile_inorganic_phosphorus_content, phosphorus_to_add, field_size
        )

    def add_to_active_phosphorus(self, phosphorus_to_add: float, field_size: float) -> None:
        """
        This method is a wrapper for adding a specified mass of phosphorus to the active phosphorus content of this
        soil layer.

        Parameters
        ----------
        phosphorus_to_add : float
            Amount of phosphorus to add (kg).
        field_size : float
            Size of the field (ha).

        """
        self.active_inorganic_phosphorus_content = self._add_phosphorus_to_pool(
            self.active_inorganic_phosphorus_content, phosphorus_to_add, field_size
        )

    @staticmethod
    def _add_phosphorus_to_pool(pool_to_add_to: float, phosphorus_to_add: float, field_size: float) -> float:
        """
        This is a generic method to be used by wrapper functions to add phosphorus to any of the phosphorus pools.

        Parameters
        ----------
        pool_to_add_to : float
            The phosphorus pool in this soil layer that is having phosphorus added (kg / ha).
        phosphorus_to_add : float
            Amount of phosphorus to add (kg).
        field_size : float
            Size of the field (ha).

        Returns
        -------
        float
            The new value of the phosphorus pool that was added to (kg / ha).

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
    def calculate_phosphorus_sorption_parameter(
        clay_fraction: float,
        labile_inorganic_phosphorus: float,
        organic_carbon_fraction: float,
    ) -> float:
        """
        Calculates the phosphorus sorption coefficient based on the current soil conditions.

        Parameters
        ----------
        clay_fraction : float
            Fraction of this soil layer that is clay, expressed in range [0, 1.0] (unitless).
        labile_inorganic_phosphorus : float
            Amount of labile inorganic phosphorus in this soil layer (mg / kg soil).
        organic_carbon_fraction : float
            Fraction of this soil layer that is organic carbon, expressed in range [0, 1.0] (unitless).

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
        adjusted_clay_content = max(10**-8, (clay_fraction * GeneralConstants.FRACTION_TO_PERCENTAGE))
        first_term = -0.045 * log(adjusted_clay_content)
        second_term = 0.001 * labile_inorganic_phosphorus
        third_term = 0.035 * organic_carbon_fraction * GeneralConstants.FRACTION_TO_PERCENTAGE
        return max(0.05, min(0.7, first_term + second_term - third_term + 0.43))

    @staticmethod
    def determine_soil_nutrient_concentration(
        nutrient_content: float,
        bulk_density: float,
        layer_thickness: float,
        field_size: float,
    ) -> float:
        """
        Calculates the concentration of nutrients in a soil layer.

        Parameters
        ----------
        nutrient_content : float
            Nutrient content of this soil layer (kg / ha).
        bulk_density : float
            Bulk density of the soil layer (Megagram / cubic meter).
        layer_thickness : float
            Thickness of the soil layer (mm).
        field_size : float
            Area of the field (ha).

        Returns
        -------
        float
            The concentration of nutrients in the soil layer (mg / kg soil).

        """
        soil_volume_in_cubic_meters = (
            layer_thickness
            * (field_size * GeneralConstants.HECTARES_TO_SQUARE_MILLIMETERS)
            * GeneralConstants.CUBIC_MILLIMETERS_TO_CUBIC_METERS
        )
        soil_mass_in_kg = bulk_density * GeneralConstants.MEGAGRAMS_TO_KILOGRAMS * soil_volume_in_cubic_meters
        soil_phosphorus_mass_in_mg = nutrient_content * field_size * GeneralConstants.KG_TO_MILLIGRAMS
        return soil_phosphorus_mass_in_mg / soil_mass_in_kg

    @staticmethod
    def determine_soil_nutrient_area_density(
        nutrient_concentration: float,
        bulk_density: float,
        layer_thickness: float,
        field_size: float,
    ) -> float:
        """
        Converts a mass per mass concentration of nutrients in the soil to a mass per area concentration.

        Parameters
        ----------
        nutrient_concentration : float
            Nutrient concentration of this soil layer (mg / kg soil).
        bulk_density : float
            Bulk density of the soil layer (Megagram / cubic meter).
        layer_thickness : float
            Thickness of the soil layer (mm).
        field_size : float
            Area of the field (ha).

        Returns
        -------
        float
            The area concentration of nutrients in the soil layer (kg / ha).

        """
        soil_volume_in_cubic_meters = (
            layer_thickness
            * (field_size * GeneralConstants.HECTARES_TO_SQUARE_MILLIMETERS)
            * GeneralConstants.CUBIC_MILLIMETERS_TO_CUBIC_METERS
        )
        soil_mass_in_kg = bulk_density * GeneralConstants.MEGAGRAMS_TO_KILOGRAMS * soil_volume_in_cubic_meters
        total_nutrient_mass_in_kg = nutrient_concentration * soil_mass_in_kg * GeneralConstants.MILLIGRAMS_TO_KG
        return total_nutrient_mass_in_kg / field_size

    @property
    def nutrient_cycling_temp_factor(self) -> float:
        """
        Calculates the nutrient cycling temperature factor.

        Returns
        -------
        float
            Nutrient cycling temperature factor (unitless).

        References
        ----------
        SWAT Theoretical documentation eqn. 3:1.2.1

        Notes
        -----
        This factor is lower bounded at 0.1

        """
        second_term = self.temperature / (self.temperature + exp(9.93 - 0.312 * self.temperature))
        factor = 0.9 * second_term + 0.1
        return max(0.1, factor)

    @property
    def nutrient_cycling_water_factor(self) -> float:
        """
        Calculates the nutrient cycling water factor.

        Returns
        -------
        float
            Nutrient cycling water factor (unitless).

        References
        ----------
        SWAT Theoretical documentation eqn. 3:1.2.2

        Notes
        -----
        This factor is lower bounded at 0.05.

        """
        return max(0.05, self.water_content / self.field_capacity_content)

    @property
    def available_water_capacity(self) -> float:
        """
        Calculates available water capacity of the soil layer.

        Returns
        -------
        float
            Water capacity of the soil layer (mm).

        References
        ----------
        SWAT Equation: 5:2.2.6

        """
        return self.field_capacity_content - self.wilting_point_content

    @property
    def layer_thickness(self) -> float:
        """
        Calculates the thickness of soil layer.

        Returns
        -------
        float
            Thickness of soil layer (mm).

        """
        return self.bottom_depth - self.top_depth

    @property
    def depth_of_layer_center(self) -> float:
        """
        Calculates the depth beneath the surface of the center this layer.

        Returns
        -------
        float
            The depth beneath the surface of the center this layer (mm).

        """
        return self.top_depth + (self.layer_thickness / 2)

    @property
    def field_capacity_content(self) -> float:
        """
        Calculates the volume of water in layer when at field capacity.

        Returns
        -------
        float
            Volume of water in layer when at field capacity (mm).

        """
        return self.field_capacity_water_concentration * self.layer_thickness

    @property
    def wilting_point_content(self) -> float:
        """
        Calculates the amount of water in layer when at wilting point.

        Returns
        -------
        float
            Amount of water in layer when at wilting point (mm).

        """
        return self.wilting_point_water_concentration * self.layer_thickness

    @property
    def saturation_content(self) -> float:
        """
        Calculates the volume of water in layer when saturated.

        Returns
        -------
        float
            Volume of water in layer when saturated (mm).

        """
        return self.saturation_point_water_concentration * self.layer_thickness

    @property
    def excess_water_available(self) -> float:
        """
        Calculates the volume of water available for percolation in the soil layer.

        Returns
        -------
        float
            Volume of water available for percolation in the soil layer (mm).

        References
        ----------
        SWAT 2:3.2.1, 2

        """

        return max(0.0, self.water_content - self.field_capacity_content)

    @property
    def acceptable_percolation_amount(self) -> float:
        """
        Calculates the volume of water that can be accepted by layer before reaching saturation.

        Returns
        -------
        float
            Volume of water that can be accepted by layer before reaching saturation (mm).

        """
        return max(0.0, self.saturation_content - self.water_content)

    @property
    def water_factor(self) -> float:
        """
        Calculates relative water saturation.

        Returns
        -------
        float
            Relative water saturation (%).

        """

        # pseudocode_soil S.4.B.1
        if self.water_content <= self.field_capacity_content:
            return (self.water_content - self.wilting_point_content) / (
                self.field_capacity_content - self.wilting_point_content
            )
        else:
            return (self.saturation_content - self.water_content) / (
                self.saturation_content - self.field_capacity_content
            )

    @property
    def water_filled_pore_space(self) -> float:
        """Returns the fraction of pore space that is currently filled by water (unitless)."""
        return self.water_content / self.saturation_content

    @property
    def silt_clay_content(self):
        """
        Combined silt and clay fraction in the soil (unitless).

        References
        ----------
        pseudocode_soil eqn. [S.6.C.2]

        Notes
        -----
        This is not necessarily the correct way to calculate this value; because the documentation is so sparse, the
        correct way is unknown. In the old code this value was hardcoded to be 0.5, and this property attempts to
        generate a reasonable value close to that.

        """
        return self.silt_fraction + self.clay_fraction

    @property
    def carbon_emissions(self) -> float:
        """
        Calculates the total amount of CO2 respirated from the soil layer.

        Returns
        -------
        float
            Total amount of CO2 emitted from carbon decomposition in this layer. (kg/ha).

        """
        return self.active_carbon_to_slow_loss + self.slow_carbon_co2_lost_amount + self.passive_carbon_co2_lost_amount

    @property
    def carbon_residue_amount(self) -> float:
        """
        Tracks the total amount of carbon residue in a soil layer (kg / ha).

        """
        return self.metabolic_litter_amount + self.structural_litter_amount

    def do_annual_reset(self) -> None:
        """
        Reset the pools

        """
        self.annual_carbon_CO2_lost = 0
        self.annual_decomposition_carbon_CO2_lost = 0
        self.annual_nitrous_oxide_emissions_total = 0
        self.annual_volatilized_ammonium_total = 0
