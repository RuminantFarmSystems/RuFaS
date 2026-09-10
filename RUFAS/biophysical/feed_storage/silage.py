import math
from dataclasses import replace

from RUFAS.general_constants import GeneralConstants
from RUFAS.data_structures.crop_soil_to_feed_storage_connection import HarvestedCrop
from RUFAS.output_manager import OutputManager
from RUFAS.rufas_time import RufasTime
from RUFAS.units import MeasurementUnits
from RUFAS.weather import Weather

from .storage import Storage

"""Fraction of effluent that is dry matter by mass."""
DRY_MATTER_FRACTION_OF_EFFLUENT = 0.1035
"""Number of days that loss of effluent occurs over after a crop is ensiled."""
EFFLUENT_CONSTRAINER = 10

"""
Shared respiration-model constants for the Preseal phase (Silostg.for:643, PRESEAL subroutine).
K and KM are Michaelis-Menten-derived diffusion constants; FC is the CO2-dependent respiration
correction factor; PSIA is atmospheric oxygen concentration (fraction). All four are fixed across
crop types in the source.

"""
PRESEAL_K = 9.0
PRESEAL_KM = 0.055
PRESEAL_FC = 0.756
PRESEAL_ATMOSPHERIC_OXYGEN_FRACTION = 0.21
"""Fixed initial silage pH under IFSM's no-acid-treatment default (Silostg.for:269-271, FACID=0)."""
PRESEAL_INITIAL_PH = 5.8
"""Preseal exposure time is capped at 3 days (Silostg.for:267) and floored at 0 (Silostg.for:268)."""
PRESEAL_EXPOSURE_CAP_DAYS = 3.0
"""Fallback exposure time (3 hours) for the newest plot in a silo with no successor yet (Silostg.for:261)."""
PRESEAL_FALLBACK_EXPOSURE_DAYS = 0.125
"""
Fraction of respired dry matter retained as water rather than lost as gas, per Silostg.for:697,708
(spec §5.1's own citation for this fact). Silostg.for:707-708's PLOT(NPL,11)/PLOT(NPL,3) update uses
a 72/180 gas-loss ratio; solving for the resulting fresh-mass change shows only that 72/180 leaves the
crop, while the complementary 108/180 stays as retained moisture. This constant is that retained
(1 - 72/180) fraction — see the `moisture_loss_kg` sign in `_finalize_preseal_loss` (Task 4).
Corrected per `/challenge-plan` finding #1 (cycle 1): the original ratio and its use in
`moisture_loss_kg` were inverted (wrong sign, ~4x wrong magnitude).
"""
PRESEAL_WATER_RETENTION_FRACTION = 1.0 - 72.0 / 180.0


def _clamp_preseal_fraction(fraction: float) -> float:
    """
    Clamps a Preseal dry-matter-loss fraction to [0.0, 1.0] (spec §6's floor/ceiling requirement for
    new Preseal/Infiltration code). Extracted as its own pure function so the boundary is directly
    unit-testable, since no realistic physical input drives the day-stepping loop in
    `calculate_preseal_loss` anywhere near this range on its own (`/challenge-plan` finding #3, cycle 3).

    Parameters
    ----------
    fraction : float
        The unclamped fraction.

    Returns
    -------
    float
        `fraction` clamped to [0.0, 1.0].

    """
    return max(0.0, min(fraction, 1.0))


def calculate_preseal_loss(
    crop: HarvestedCrop, exposure_days: float, exposed_area_m2: float, dry_matter_density_kg_per_m3: float
) -> dict[str, float]:
    """
    Calculates the dry matter lost to aerobic respiration before a silage plot is sealed, and the
    resulting temperature rise, by stepping through the exposure duration one day at a time.

    Parameters
    ----------
    crop : HarvestedCrop
        The crop being exposed prior to sealing. Not mutated by this function.
    exposure_days : float
        Total time this crop is exposed before being covered (days), already capped/floored by the
        caller per ``PRESEAL_EXPOSURE_CAP_DAYS``.
    exposed_area_m2 : float
        Surface area of this crop exposed to air (m2).
    dry_matter_density_kg_per_m3 : float
        Packed dry-matter density of the storage (kg DM / m3).

    Returns
    -------
    dict[str, float]
        ``dry_matter_loss_fraction`` (fraction of dry matter lost to respiration) and
        ``final_temperature`` (degrees C, after any self-heating during exposure).

    Notes
    -----
    Translated from ``Silostg.for:634-714`` (``PRESEAL``). The day-stepping loop is preserved
    deliberately — temperature rises each day from respiration heat, feeding into the next day's
    respiration rate (positive feedback). Collapsing this into one evaluation over the full exposure
    window would lose that self-heating effect (design spec §5.1). ``[FS.SIL.8]``.

    """
    total_dry_matter_mass_kg = crop.dry_matter_mass
    dry_matter_fraction = crop.dry_matter_percentage * GeneralConstants.PERCENTAGE_TO_FRACTION
    temperature = crop.temperature
    max_respiration_rate = (4.8 if crop.is_alfalfa else 2.9) * dry_matter_fraction

    thickness_cm = max(100.0, 100.0 * total_dry_matter_mass_kg / (exposed_area_m2 * dry_matter_density_kg_per_m3))
    diffusion_coefficient = 0.0086 * (273.0 + temperature) ** 2
    tortuosity = 2.0 / 3.0
    max_relative_density = 3.0 / (3.0 - dry_matter_fraction)
    relative_density = min(0.99 * max_relative_density, 0.001 * dry_matter_density_kg_per_m3 / dry_matter_fraction)
    porosity = 1.0 - relative_density / max_relative_density
    if dry_matter_fraction > 0.693:
        dry_matter_respiration_factor = 0.0384
    elif dry_matter_fraction > 0.20:
        dry_matter_respiration_factor = 1.93 - 5.46 * dry_matter_fraction + 3.94 * dry_matter_fraction**2
    else:
        dry_matter_respiration_factor = 1.0

    remaining_exposure_days = exposure_days
    dry_matter_loss_fraction = 0.0
    while remaining_exposure_days > 0.0:
        temperature_factor = 1.0 if temperature >= 25.0 else 0.178 * math.exp(0.069 * temperature)
        ph_factor = (PRESEAL_INITIAL_PH - 3.0) / 3.5
        respiration_rate = max_respiration_rate * dry_matter_respiration_factor * temperature_factor * ph_factor
        gamma = (
            relative_density
            * respiration_rate
            * (PRESEAL_KM + PRESEAL_ATMOSPHERIC_OXYGEN_FRACTION)
            * PRESEAL_FC
            / (diffusion_coefficient * porosity * tortuosity * PRESEAL_ATMOSPHERIC_OXYGEN_FRACTION)
        )
        c = math.sqrt(PRESEAL_K * gamma)
        average_respiration_rate = (
            -respiration_rate
            * PRESEAL_FC
            * (PRESEAL_KM + PRESEAL_ATMOSPHERIC_OXYGEN_FRACTION)
            * (
                math.log(PRESEAL_KM + PRESEAL_ATMOSPHERIC_OXYGEN_FRACTION * math.exp(-c * thickness_cm))
                - math.log(PRESEAL_KM + PRESEAL_ATMOSPHERIC_OXYGEN_FRACTION)
            )
            / (PRESEAL_ATMOSPHERIC_OXYGEN_FRACTION * c * thickness_cm)
        )
        loss_per_day = 0.0299 * average_respiration_rate / dry_matter_fraction

        day_step = min(1.0, remaining_exposure_days)
        loss_today = day_step * loss_per_day
        dry_matter_loss_fraction += loss_today
        remaining_exposure_days -= day_step

        temperature_rise = 8436.0 * loss_today * 0.7 / (2.22 / dry_matter_fraction - 1.22)
        temperature += temperature_rise

    dry_matter_loss_fraction = _clamp_preseal_fraction(dry_matter_loss_fraction)

    return {"dry_matter_loss_fraction": dry_matter_loss_fraction, "final_temperature": temperature}


class Silage(Storage):
    """
    Represents Silage storage, a subclass of ``Storage``.

    Parameters
    ----------
    config : dict[str, str | float | list[str]]
        Configuration dictionary for the silage storage.

    Attributes
    ----------
    om : OutputManager
        The singleton output manager used for model outputs.

    """

    def __init__(self, config: dict[str, str | float | list[str]]) -> None:
        super().__init__(config)
        self.om = OutputManager()

    def process_degradations(self, weather: Weather, time: RufasTime) -> None:
        """
        Processes the losses of nutrients and mass to effluent in the ensiled crops, and calls the parent
        implementation of ``process_degradations`` to handle the fermentative loss.

        Parameters
        ----------
        weather : Weather
            Weather instance containing all weather information for the simulation.
        time : RufasTime
            RufasTime instance tracking the current time of the simulation.

        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self.process_degradations.__name__,
            "units": MeasurementUnits.KILOGRAMS,
            "simulation_day": time.simulation_day,
            "prefix": self._prefix,
        }
        total_effluent_dry_matter_loss = 0.0
        total_effluent_moisture_loss = 0.0
        for crop in self.stored:
            effluent_loss_values = self._calculate_effluent_loss(crop, time)
            total_effluent_dry_matter_loss += effluent_loss_values["dry_matter_loss"]
            total_effluent_moisture_loss += effluent_loss_values["moisture_loss"]
            crop.non_protein_nitrogen = effluent_loss_values["non_protein_nitrogen"]
            crop.crude_protein_percent = effluent_loss_values["crude_protein_percent"]
            crop.dry_matter_mass = effluent_loss_values["dry_matter_mass"]
            crop.dry_matter_percentage = effluent_loss_values["dry_matter_percentage"]

        self.om.add_variable("total_effluent_dry_matter_loss", total_effluent_dry_matter_loss, info_map)
        self.om.add_variable("total_effluent_moisture_loss", total_effluent_moisture_loss, info_map)

        super().process_degradations(weather, time)

    def project_degradations(
        self, crops: list[HarvestedCrop], weather: Weather, time: RufasTime
    ) -> list[HarvestedCrop]:
        """
        Projects the state of crops currently stored at a given future date.

        Parameters
        ----------
        crops : list[HarvestedCrop]
            List of ``HarvestedCrop`` objects to project degradations for.
        weather : Weather
            Weather instance containing all weather information for the simulation.
        time : RufasTime
            RufasTime instance containing the date at which the state of the stored crops should be projected.

        Returns
        -------
        list[HarvestedCrop]
            Crops in the state they are projected to be in at the given date.

        """
        crops_projected_with_effluent_loss: list[HarvestedCrop] = []
        for crop in crops:
            effluent_loss_values = self._calculate_effluent_loss(crop, time)
            del effluent_loss_values["dry_matter_loss"]
            del effluent_loss_values["moisture_loss"]
            projected_crop = replace(crop, **effluent_loss_values)
            crops_projected_with_effluent_loss.append(projected_crop)

        return super().project_degradations(crops_projected_with_effluent_loss, weather, time)

    def _calculate_effluent_loss(self, crop: HarvestedCrop, time: RufasTime) -> dict[str, float]:
        """
        Calculates the attributes of a crop after effluent loss.

        Parameters
        ----------
        crop : HarvestedCrop
            ``HarvestedCrop`` to calculate effluent losses from.
        time : RufasTime
            RufasTime instance tracking the current time of the simulation.

        Returns
        -------
        dict[str, float]
            Mapping of the crop's attributes to their values after effluent loss.

        """
        post_loss_values = {
            "dry_matter_mass": crop.dry_matter_mass,
            "dry_matter_percentage": crop.dry_matter_percentage,
            "non_protein_nitrogen": crop.non_protein_nitrogen,
            "crude_protein_percent": crop.crude_protein_percent,
            "dry_matter_loss": 0.0,
            "moisture_loss": 0.0,
        }
        days_of_effluent_to_process = self.calculate_days_of_effluent_loss_to_process(crop, time)
        if days_of_effluent_to_process == 0:
            return post_loss_values

        crop.estimated_maximum_effluent = crop.estimate_maximum_effluent()
        dry_matter_loss = self.calculate_dry_matter_loss_to_effluent(
            crop.estimated_maximum_effluent, days_of_effluent_to_process
        )
        moisture_loss = self.calculate_moisture_loss_to_effluent(
            crop.estimated_maximum_effluent, days_of_effluent_to_process
        )

        dry_matter_loss_frac = dry_matter_loss / crop.dry_matter_mass
        post_loss_values["non_protein_nitrogen"] = self.calculate_non_protein_nitrogen_after_effluent_loss(
            crop.non_protein_nitrogen, crop.crude_protein_percent, dry_matter_loss_frac
        )

        post_loss_values["crude_protein_percent"] = self.calculate_crude_protein_after_effluent_loss(
            crop.crude_protein_percent, dry_matter_loss_frac
        )

        mass_attributes = self._calculate_mass_attributes_after_loss(crop, dry_matter_loss, moisture_loss)
        post_loss_values.update(mass_attributes | {"dry_matter_loss": dry_matter_loss, "moisture_loss": moisture_loss})
        return post_loss_values

    def calculate_days_of_effluent_loss_to_process(self, crop: HarvestedCrop, time: RufasTime) -> int:
        """
        Calculates the number of days of effluent loss to process for an ensiled crop.

        Parameters
        ----------
        crop : HarvestedCrop
            Ensiled crop that is being degraded.
        time : RufasTime
            RufasTime instance containing the current time of the simulation.

        Returns
        -------
        int
            Number of days to calculate effluent loss for.

        Notes
        -----
        Effluent loss is fixed at 10 days if the crop is still within the first 10 days of storage. After that period,
        it is calculated as the number of days since the last degradation.

        """
        days_since_storage = (time.current_date.date() - crop.storage_time).days

        if days_since_storage <= 10:
            return max(0, min(10, (time.current_date.date() - crop.last_time_degraded).days))
        else:
            return (time.current_date.date() - crop.last_time_degraded).days

    def calculate_dry_matter_loss_to_effluent(self, estimated_maximum_effluent: float, days_of_loss: int) -> float:
        """
        Calculates the dry matter loss to effluent.

        Parameters
        ----------
        estimated_maximum_effluent : float
            The estimated maximum effluent.
        days_of_loss : int
            The number of days effluent loss will be calculated for.

        Returns
        -------
        float
            The amount of dry matter lost to effluent (kg).

        References
        ----------
        Feed Storage Scientific Documentation, equations FS.SIL.4, FS.SIL.6, and FS.SIL.7.

        """
        return estimated_maximum_effluent * days_of_loss * DRY_MATTER_FRACTION_OF_EFFLUENT / EFFLUENT_CONSTRAINER

    def calculate_moisture_loss_to_effluent(self, estimated_maximum_effluent: float, days_of_loss: int) -> float:
        """
        Calculates the moisture loss to effluent.

        Parameters
        ----------
        estimated_maximum_effluent : float
            The estimated maximum effluent.
        days_of_loss : int
            The number of days effluent loss will be calculated for.

        Returns
        -------
        float
            The amount of moisture lost to effluent (kg).

        References
        ----------
        Feed Storage Scientific Documentation, equation FS.SIL.5.

        """
        return estimated_maximum_effluent * days_of_loss * (1 - DRY_MATTER_FRACTION_OF_EFFLUENT) / EFFLUENT_CONSTRAINER

    def calculate_non_protein_nitrogen_after_effluent_loss(
        self, initial_non_protein_nitrogen: float, initial_crude_protein: float, loss_fraction: float
    ) -> float:
        """
        Calculates the percentage of non-protein nitrogen in a stored crop after losing dry matter to effluent.

        Parameters
        ----------
        initial_non_protein_nitrogen : float
            Percentage of non-protein nitrogen in the crop before dry matter loss occurred.
        initial_crude_protein : float
            Percentage of crude protein in the crop before dry matter loss occurred.
        loss_fraction : float
            Fraction of dry matter that was lost to effluent.

        Returns
        -------
        float
            Percentage of non-protein nitrogen remaining in the stored crop.

        References
        ----------
        Feed Storage Scientific Documentation, equation FS.NUT.1.

        """
        if loss_fraction == 0.0:
            return initial_non_protein_nitrogen

        npn_fraction = initial_non_protein_nitrogen * GeneralConstants.PERCENTAGE_TO_FRACTION
        cp_fraction = initial_crude_protein * GeneralConstants.PERCENTAGE_TO_FRACTION

        numerator = npn_fraction * cp_fraction - 0.3 * loss_fraction
        denominator = cp_fraction - 0.3 * loss_fraction

        new_npn_fraction = numerator / denominator
        new_npn_percentage = new_npn_fraction * GeneralConstants.FRACTION_TO_PERCENTAGE
        return max(0.0, new_npn_percentage)

    def calculate_crude_protein_after_effluent_loss(self, initial_crude_protein: float, loss_fraction: float) -> float:
        """
        Calculates the percentage of crude protein in a stored crop after losing dry matter to effluent.

        Parameters
        ----------
        initial_crude_protein : float
            Percentage of crude protein in the crop before dry matter loss occurred.
        loss_fraction : float
            Fraction of dry matter that was lost to effluent.

        Returns
        -------
        float
            Percentage of crude protein remaining in the stored crop.

        References
        ----------
        Feed Storage Scientific Documentation, equation FS.NUT.1.

        """
        if loss_fraction == 0.0:
            return initial_crude_protein

        new_fraction = (initial_crude_protein * GeneralConstants.PERCENTAGE_TO_FRACTION - 0.3 * loss_fraction) / (
            1 - loss_fraction
        )
        new_percentage = new_fraction * GeneralConstants.FRACTION_TO_PERCENTAGE
        return max(0.0, new_percentage)


def _require_positive_config_float(config: dict[str, str | float | list[str]], key: str, class_name: str) -> float:
    """
    Reads and validates a required positive float from a storage config dict.

    Parameters
    ----------
    config : dict[str, str | float | list[str]]
        Configuration dictionary for the storage.
    key : str
        The config key to read.
    class_name : str
        Name of the calling storage class, for the error message.

    Returns
    -------
    float
        The validated, positive config value.

    Raises
    ------
    ValueError
        If the key is missing or its value is not a positive number.

    """
    value = config.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        raise ValueError(f"{class_name} requires a positive '{key}' in its config, got {value!r}.")
    return float(value)


class _RectangularSilage(Silage):
    """
    Shared base for Bunker and Pile: identical config shape (`width_m`, `height_m`,
    `dry_matter_density_kg_per_m3`) and, per Task 4, identical Preseal exposed-area geometry.
    Introduced per `/challenge-plan` finding #6 to remove byte-for-byte duplication between the two
    classes without adding a strategy/registry (still just plain subclassing — see YAGNI CHECK).

    Attributes
    ----------
    width_m : float
        Storage width (m). Required per-storage input — no reference-table fallback.
    height_m : float
        Storage wall height (m). Required per-storage input — no reference-table fallback.
    dry_matter_density_kg_per_m3 : float
        Packed dry-matter density (kg DM / m3). Required per-storage input (see Open Decisions §1).

    """

    def __init__(self, config: dict[str, str | float | list[str]]) -> None:
        super().__init__(config)
        self.width_m = _require_positive_config_float(config, "width_m", self.__class__.__name__)
        self.height_m = _require_positive_config_float(config, "height_m", self.__class__.__name__)
        self.dry_matter_density_kg_per_m3 = _require_positive_config_float(
            config, "dry_matter_density_kg_per_m3", self.__class__.__name__
        )


class Bunker(_RectangularSilage):
    """Represents the Bunker type of Silage storage. Config fields: see `_RectangularSilage`."""


class Pile(_RectangularSilage):
    """Represents the Pile type of Silage storage. Config fields: see `_RectangularSilage`."""


class Bag(Silage):
    """
    Represents the Bag type of Silage storage.

    Attributes
    ----------
    diameter_m : float
        Bag diameter (m). Required per-storage input — no reference-table fallback.
    dry_matter_density_kg_per_m3 : float
        Packed dry-matter density (kg DM / m3). Required per-storage input (see Open Decisions §1).

    """

    def __init__(self, config: dict[str, str | float | list[str]]) -> None:
        super().__init__(config)
        self.diameter_m = _require_positive_config_float(config, "diameter_m", self.__class__.__name__)
        self.dry_matter_density_kg_per_m3 = _require_positive_config_float(
            config, "dry_matter_density_kg_per_m3", self.__class__.__name__
        )
