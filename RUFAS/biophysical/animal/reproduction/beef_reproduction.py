"""Beef cow-calf reproduction — natural-service seasonal breeding (NRC 2016 Ch.13)."""

from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants


def calculate_seasonal_conception_probability(
    body_condition_score: float,
    bull_to_cow_ratio: int,
    days_since_calving: int,
    conception_rate_multiplier: float = 1.0,
) -> float:
    """
    NRC 2016 Ch.13-informed daily conception probability for natural-service seasonal breeding.

    Parameters
    ----------
    body_condition_score : float
        Body condition on 1-9 scale. Cows below 5 have reduced conception.
    bull_to_cow_ratio : int
        Cows per bull. Above 30 reduces probability.
    days_since_calving : int
        Days postpartum. Below 45 = postpartum anestrus (probability = 0.0).
    conception_rate_multiplier : float
        Scenario lever scaling the calibrated base daily probability. Defaults
        to 1.0, which reproduces unmodified calibrated behaviour. Supplied by
        the caller from configuration; this function does not read config, so
        it stays a pure function of its arguments.

    Returns
    -------
    float
        Daily conception probability in [0.0, 1.0].

    Notes
    -----
    Simplified single-draw-per-day model; a full 21-day estrus-cycle model is
    out of scope for PR-B (documented limitation, Step 9). Calibrated so that
    aggregate seasonal pregnancy rate across a 63-day breeding season at BCS=5
    and 25:1 bull ratio approaches the USDA 91.5% calved-per-cow-exposed reference
    (excluding stillbirth/preweaning mortality applied separately).

    The BCS factor has a floor of 0.5 at BCS=1, meaning even severely thin cows
    retain 50% of base daily conception probability. This is a pragmatic model
    floor to avoid zero-probability traps in simulation; it is NOT derived from a
    specific NRC 2016 equation (the NRC gives qualitative guidance, not a precise
    mathematical adjustment function).
    """
    if days_since_calving < AnimalModuleConstants.BEEF_POSTPARTUM_ANESTRUS_DAYS:
        return 0.0

    bcs_factor = min(
        1.0,
        max(
            AnimalModuleConstants.BEEF_CONCEPTION_BCS_FLOOR,
            (body_condition_score - 1) / AnimalModuleConstants.BEEF_CONCEPTION_BCS_DIVISOR,
        ),
    )
    bull_factor = min(1.0, AnimalModuleConstants.BEEF_CONCEPTION_BULL_RATIO_REFERENCE / max(bull_to_cow_ratio, 1))
    probability = (
        AnimalModuleConstants.BEEF_CONCEPTION_BASE_DAILY_PROB * bcs_factor * bull_factor * conception_rate_multiplier
    )
    # Defensive guard, unreachable under validated inputs: both adjustment
    # factors cap at 1.0, so exceeding 1.0 requires a multiplier of 24.75.
    return min(1.0, probability)
