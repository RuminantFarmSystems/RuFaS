"""Unit tests for BeefNRCRequirementsCalculator — NRC 2016 equations."""

from typing import Any

import pytest
from RUFAS.biophysical.animal.data_types.animal_enums import Sex
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.nutrition_data_structures import NutritionRequirements
from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.nutrients.beef_nrc_requirements_calculator import BeefNRCRequirementsCalculator


@pytest.fixture(scope="module")
def calc() -> Any:
    """BeefNRCRequirementsCalculator class."""
    return BeefNRCRequirementsCalculator


@pytest.mark.unit
def test_calculate_sbw(calc: Any) -> None:
    """SBW must be 0.96 × BW."""
    assert calc._calculate_sbw(400.0) == pytest.approx(384.0)


@pytest.mark.unit
def test_calculate_ebw(calc: Any) -> None:
    """EBW must be 0.891 × SBW (NRC 2016 Ch. 12)."""
    assert calc._calculate_ebw(384.0) == pytest.approx(384.0 * 0.891)


@pytest.mark.unit
def test_calculate_eqsbw(calc: Any) -> None:
    """EQSBW = SBW × (SRW/MSBW) normalises across frame sizes.

    320 kg steer, mature_BW=600 → MSBW=576, SBW=307.2, SRW=478 → EQSBW≈255.
    This exactly matches NRC 2016 Box 12-1.
    """
    sbw = 320.0 * 0.96  # 307.2
    msbw = 600.0 * 0.96  # 576.0
    assert calc._calculate_eqsbw(sbw, msbw) == pytest.approx(307.2 * (478.0 / 576.0), rel=1e-6)


@pytest.mark.unit
def test_calculate_eqebw(calc: Any) -> None:
    """EQEBW = 0.891 × EQSBW — the weight basis used in the NEg equation."""
    assert calc._calculate_eqebw(255.0) == pytest.approx(255.0 * 0.891)


@pytest.mark.unit
def test_maintenance_energy_angus_steer_thermoneutral(calc: Any) -> None:
    """NEm at 20 °C (a2=0): NEm = SBW^0.75 × (0.077 × BE × SEX)."""
    sbw = 384.0
    # a2 = max(0, 0.0007 × (20-20)) = 0; BE=1.0 (Angus), SEX=1.0 (steer)
    expected = sbw**0.75 * (0.077 * 1.0 * 1.0 + 0.0)
    result = calc._calculate_maintenance_energy(
        sbw=sbw,
        breed="Angus",
        sex=Sex.STEER,
        housing="Open_Lot",
        mud_condition="none",
        temperature_c=20.0,
    )
    assert result == pytest.approx(expected, rel=1e-6)


@pytest.mark.unit
def test_maintenance_energy_cold_adds_a2(calc: Any) -> None:
    """NEm at 10 °C must add a2 = 0.0007 × (20-10) = 0.007 per SBW^0.75."""
    sbw = 384.0
    a2 = 0.0007 * (20.0 - 10.0)  # = 0.007
    expected = sbw**0.75 * (0.077 * 1.0 * 1.0 + a2)
    result = calc._calculate_maintenance_energy(
        sbw=sbw,
        breed="Angus",
        sex=Sex.STEER,
        housing="Open_Lot",
        mud_condition="none",
        temperature_c=10.0,
    )
    assert result == pytest.approx(expected, rel=1e-6)


@pytest.mark.unit
def test_maintenance_energy_mud_mild(calc: Any) -> None:
    """NEm with mild mud must be 1.08× the no-mud value."""
    sbw = 384.0
    base = calc._calculate_maintenance_energy(
        sbw=sbw,
        breed="Angus",
        sex=Sex.STEER,
        housing="Open_Lot",
        mud_condition="none",
        temperature_c=20.0,
    )
    result = calc._calculate_maintenance_energy(
        sbw=sbw,
        breed="Angus",
        sex=Sex.STEER,
        housing="Open_Lot",
        mud_condition="mild",
        temperature_c=20.0,
    )
    assert result == pytest.approx(base * 1.08, rel=1e-6)


@pytest.mark.unit
def test_maintenance_energy_cold_stress(calc: Any) -> None:
    """NEm at -10 °C must be greater than at thermoneutral."""
    sbw = 384.0
    base = calc._calculate_maintenance_energy(
        sbw=sbw,
        breed="Angus",
        sex=Sex.STEER,
        housing="Open_Lot",
        mud_condition="none",
        temperature_c=20.0,
    )
    cold = calc._calculate_maintenance_energy(
        sbw=sbw,
        breed="Angus",
        sex=Sex.STEER,
        housing="Open_Lot",
        mud_condition="none",
        temperature_c=-10.0,
    )
    assert cold > base


@pytest.mark.unit
def test_growth_energy_zero_ebg(calc: Any) -> None:
    """NEg must be 0 when EBG <= 0."""
    assert calc._calculate_growth_energy(eqebw=300.0, ebg=0.0) == pytest.approx(0.0)


@pytest.mark.unit
def test_growth_energy_positive(calc: Any) -> None:
    """NEg = RE = 0.0635 × EQEBW^0.75 × EBG^1.097.

    EBG = 0.956 × ADG (NOT 0.891 × ADG — that's the EBW/SBW conversion, not EBG).
    """
    eqsbw = 384.0 * (478.0 / (600.0 * 0.96))
    eqebw = eqsbw * 0.891
    adg = 1.4
    ebg = adg * 0.956
    expected = 0.0635 * (eqebw**0.75) * (ebg**1.097)
    result = calc._calculate_growth_energy(eqebw=eqebw, ebg=ebg)
    assert result == pytest.approx(expected, rel=1e-6)


@pytest.mark.unit
def test_np_growth_zero_when_adg_zero(calc: Any) -> None:
    """NPg must be 0 when ADG = 0."""
    assert calc._calculate_np_growth(adg=0.0, ne_growth=3.0) == pytest.approx(0.0)


@pytest.mark.unit
def test_np_growth_box12_1(calc: Any) -> None:
    """NPg must match NRC 2016 Box 12-1: ADG=1.365, RE=4.97 → NPg ≈ 219 g/d."""
    adg = 1.365
    ne_growth = 4.97
    expected = adg * (268.0 - 29.4 * ne_growth / adg)
    result = calc._calculate_np_growth(adg=adg, ne_growth=ne_growth)
    assert result == pytest.approx(expected, rel=1e-6)


@pytest.mark.unit
def test_dmi_receiving_period(calc: Any) -> None:
    """DMI during receiving period must be <= full DMI and above minimum floor."""
    full = calc._calculate_dmi(body_weight=400.0, ne_diet_concentration=2.0, days_on_feed=22)
    receiving = calc._calculate_dmi(body_weight=400.0, ne_diet_concentration=2.0, days_on_feed=10)
    assert receiving <= full
    assert receiving >= 400.0 * 0.015 - 1e-9


@pytest.mark.unit
def test_dmi_minimum_floor(calc: Any) -> None:
    """DMI must not fall below 1.5 % BW regardless of diet energy."""
    result = calc._calculate_dmi(body_weight=400.0, ne_diet_concentration=5.0, days_on_feed=30)
    assert result >= 400.0 * 0.015 - 1e-9


@pytest.mark.unit
def test_metabolizable_protein_zero_growth(calc: Any) -> None:
    """MP maintenance = 3.8 × BW^0.75 (live weight basis) when NPg = 0."""
    body_weight = 400.0
    mp_maint = 3.8 * (body_weight**0.75)
    result = calc._calculate_metabolizable_protein(body_weight=body_weight, np_growth=0.0, eqsbw=310.0)
    assert result == pytest.approx(mp_maint, rel=1e-6)


@pytest.mark.unit
def test_metabolizable_protein_box12_1(calc: Any) -> None:
    """MP must match NRC 2016 Box 12-1 anchor: 320 kg Angus steer → MP = 691 g/d.

    Box 12-1 exact values: BW=320, EQSBW=255, NPg=219.1, eff_g=0.543,
    MPg=403, MPm=288 → total MP=691 g/d.
    """
    body_weight = 320.0
    np_growth = 219.1
    eqsbw = 255.0
    result = calc._calculate_metabolizable_protein(body_weight=body_weight, np_growth=np_growth, eqsbw=eqsbw)
    assert result == pytest.approx(691.0, abs=2.0)


@pytest.mark.unit
def test_calculate_requirements_returns_nutrition_requirements(calc: Any) -> None:
    """calculate_requirements must return NutritionRequirements; pregnancy/lactation/activity = 0."""
    result = calc.calculate_requirements(
        body_weight=400.0,
        mature_body_weight=600.0,
        animal_type=AnimalType.FEEDLOT_STEER,
        breed="Angus",
        sex=Sex.STEER,
        days_on_feed=30,
        target_adg=1.4,
        implant_adg_factor=1.0,
        housing="Open_Lot",
        mud_condition="none",
        temperature_c=20.0,
        ne_diet_concentration=2.27,
        process_based_phosphorus_requirement=0.0,
    )
    assert isinstance(result, NutritionRequirements)
    assert result.pregnancy_energy == pytest.approx(0.0)
    assert result.lactation_energy == pytest.approx(0.0)
    assert result.activity_energy == pytest.approx(0.0)
    assert result.maintenance_energy > 0.0
    assert result.growth_energy > 0.0
    assert result.dry_matter > 0.0


@pytest.mark.unit
def test_calculate_requirements_rejects_dairy_type(calc: Any) -> None:
    """calculate_requirements must raise ValueError for non-feedlot animal types."""
    with pytest.raises(ValueError):
        calc.calculate_requirements(
            body_weight=400.0,
            mature_body_weight=600.0,
            animal_type=AnimalType.LAC_COW,
            breed="Holstein",
            sex=Sex.FEMALE,
            days_on_feed=0,
            target_adg=0.0,
            implant_adg_factor=1.0,
            housing="Barn",
            mud_condition="none",
            temperature_c=20.0,
            ne_diet_concentration=1.5,
            process_based_phosphorus_requirement=0.0,
        )


# ── NRC 2016 benchmark validation ─────────────────────────────────────────────
# All benchmark tests use thermoneutral conditions (temperature_c=20.0) so
# the cold-stress a2 term equals 0 and NEm reduces to SBW^0.75 × 0.077 × BE × SEX.
# This matches the environment assumed in NRC 2016 Box 12-1 and Chapter 12 tables.


def _expected_nem(
    bw: float,
    breed: str = "Angus",
    sex: Sex = Sex.STEER,
    temp: float = 20.0,
) -> float:
    """Expected NEm using NRC 2016 Eq. 11-1 + cold-stress a2 term (Eq. 11-2)."""
    sbw: float = bw * 0.96
    be: float = AnimalModuleConstants.BREED_NEm_MULTIPLIER[breed]
    sx: float = AnimalModuleConstants.SEX_NEm_MULTIPLIER[sex]
    a2: float = max(0.0, 0.0007 * (20.0 - temp))
    return sbw**0.75 * (0.077 * be * sx + a2)


def _expected_neg(bw: float, mbw: float, target_adg: float) -> float:
    """Expected NEg: RE = 0.0635 × EQEBW^0.75 × EBG^1.097 (NRC 2016 Ch. 12)."""
    sbw: float = bw * 0.96
    msbw: float = mbw * 0.96
    eqsbw: float = sbw * (478.0 / msbw)
    eqebw: float = eqsbw * 0.891
    ebg: float = target_adg * 0.956
    if ebg <= 0.0:
        return 0.0
    return 0.0635 * (eqebw**0.75) * (ebg**1.097)


def _expected_dmi(bw: float, ne_conc: float = 2.27) -> float:
    """Expected DMI from NRC 2016 Eq. 10-1 (outside receiving period)."""
    ne_c: float = max(ne_conc, 0.95)
    ne_m_intake: float = (bw**0.75) * (0.2435 * ne_c - 0.0466 * ne_c**2 - 0.0869)
    dmi: float = ne_m_intake / ne_c if ne_m_intake > 0.0 else 0.0
    return max(dmi, AnimalModuleConstants.FEEDLOT_MIN_DMI_RATIO * bw)


@pytest.mark.validation
@pytest.mark.nrc2016
def test_box12_1_mp_anchor(calc: Any) -> None:
    """PRIMARY ANCHOR: NRC 2016 Box 12-1 — 320 kg Angus steer, ADG=1.365 → MP=691 g/d.

    Formula chain verified against published values:
    EQSBW=255, RE=4.97, NPg=219, eff_g=0.543, MPg=403, MPm=288 → total MP=691 g/d.
    Tolerance ±0.5 % (≤3.5 g/d).
    """
    result = calc.calculate_requirements(
        body_weight=320.0,
        mature_body_weight=600.0,
        animal_type=AnimalType.FEEDLOT_STEER,
        breed="Angus",
        sex=Sex.STEER,
        days_on_feed=60,
        target_adg=1.365,
        implant_adg_factor=1.0,
        housing="Open_Lot",
        mud_condition="none",
        temperature_c=20.0,
        ne_diet_concentration=2.27,
        process_based_phosphorus_requirement=0.0,
    )
    assert result.metabolizable_protein == pytest.approx(691.0, rel=0.005)


@pytest.mark.validation
@pytest.mark.nrc2016
@pytest.mark.parametrize(
    "bw,mbw,breed,sex,animal_type_name",
    [
        (300.0, 550.0, "Angus", Sex.STEER, "FEEDLOT_STEER"),
        (400.0, 550.0, "Angus", Sex.STEER, "FEEDLOT_STEER"),
        (500.0, 550.0, "Angus", Sex.STEER, "FEEDLOT_STEER"),
        (400.0, 680.0, "Charolais", Sex.STEER, "FEEDLOT_STEER"),
        (350.0, 480.0, "Angus", Sex.FEMALE, "FEEDLOT_HEIFER"),
    ],
)
def test_nem_matches_formula_thermoneutral(
    calc: Any,
    bw: float,
    mbw: float,
    breed: str,
    sex: Sex,
    animal_type_name: str,
) -> None:
    """NEm must match the closed-form formula within 0.5 % at thermoneutral (a2=0)."""
    animal_type = AnimalType[animal_type_name]
    result = calc.calculate_requirements(
        body_weight=bw,
        mature_body_weight=mbw,
        animal_type=animal_type,
        breed=breed,
        sex=sex,
        days_on_feed=30,
        target_adg=1.4,
        implant_adg_factor=1.0,
        housing="Open_Lot",
        mud_condition="none",
        temperature_c=20.0,
        ne_diet_concentration=2.27,
        process_based_phosphorus_requirement=0.0,
    )
    expected = _expected_nem(bw, breed=breed, sex=sex, temp=20.0)
    assert result.maintenance_energy == pytest.approx(expected, rel=0.005)


@pytest.mark.validation
@pytest.mark.nrc2016
@pytest.mark.parametrize(
    "bw,mbw,target_adg",
    [
        (300.0, 550.0, 1.0),
        (400.0, 550.0, 1.4),
        (500.0, 550.0, 1.2),
    ],
)
def test_neg_matches_formula(
    calc: Any,
    bw: float,
    mbw: float,
    target_adg: float,
) -> None:
    """NEg must match RE = 0.0635 × EQEBW^0.75 × EBG^1.097 within 0.5 %."""
    result = calc.calculate_requirements(
        body_weight=bw,
        mature_body_weight=mbw,
        animal_type=AnimalType.FEEDLOT_STEER,
        breed="Angus",
        sex=Sex.STEER,
        days_on_feed=30,
        target_adg=target_adg,
        implant_adg_factor=1.0,
        housing="Open_Lot",
        mud_condition="none",
        temperature_c=20.0,
        ne_diet_concentration=2.27,
        process_based_phosphorus_requirement=0.0,
    )
    expected = _expected_neg(bw, mbw, target_adg)
    assert result.growth_energy == pytest.approx(expected, rel=0.005)


@pytest.mark.validation
@pytest.mark.nrc2016
@pytest.mark.parametrize("bw", [300.0, 400.0, 500.0])
def test_dmi_matches_eq10_1(calc: Any, bw: float) -> None:
    """DMI must match NRC 2016 Eq. 10-1 within 0.5 % outside the receiving period."""
    ne_conc = 2.27
    result = calc.calculate_requirements(
        body_weight=bw,
        mature_body_weight=550.0,
        animal_type=AnimalType.FEEDLOT_STEER,
        breed="Angus",
        sex=Sex.STEER,
        days_on_feed=30,
        target_adg=1.4,
        implant_adg_factor=1.0,
        housing="Open_Lot",
        mud_condition="none",
        temperature_c=20.0,
        ne_diet_concentration=ne_conc,
        process_based_phosphorus_requirement=0.0,
    )
    expected = _expected_dmi(bw, ne_conc)
    assert result.dry_matter == pytest.approx(expected, rel=0.005)


@pytest.mark.unit
def test_np_growth_clamped_to_zero_when_formula_goes_negative() -> None:
    """_calculate_np_growth must return 0.0, not negative, when ne_growth is large relative to ADG.

    When ADG is small and ne_growth is large, the formula ADG × (268 - 29.4 × RE/ADG)
    can go negative, corrupting downstream Ca/P calculations. The guard must clamp to 0.
    """
    result = BeefNRCRequirementsCalculator._calculate_np_growth(adg=0.1, ne_growth=10.0)
    assert result == pytest.approx(0.0)
