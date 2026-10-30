"""Quick RuFaS herd calculator: calculate values for MANUAL entry into animal JSON to create a fairly stable herd.

PRIMARY CALCULATIONS
- Annual number of female calves to retain and conventional-semen male calf rate
- Parity fractions (1, 2, 3, 4, 5+), rounded to whole percentage points
- Initial numbers of calves, Heifer I, Heifer II, and springer heifers

OUTPUT SECTIONS
1. Calculated results only.
2. All fields to update in the animal JSON, in the same order as that JSON,
   including calculated values, required user inputs, and optional defaults.
3. Other assumptions and inputs used for calculations (not animal JSON fields).

HOW TO USE
1. Edit values in EDIT INPUTS HERE.
2. Run: python helpful_scripts\herd_inputs_calculator\herd_inputs_calculator.py
3. Copy the values in Section 2 into the animal input JSON manually.
IMPORTANT:  calf_retention_method must be "count" for the calculated
   annual_keep_female_calf_num to be used.

To save a reference report, specify the location:
    python herd_inputs_calculator.py --output "C:/Users/you/Documents/herd_results.json"
You can also supply an existing folder to --output; the default filename is used.


Counts and milk yield are rounded to integers; fractions to whole percentages.
Separate buffers control replacement-calf retention and the additional female
calf production targeted through the male calf rate. Increasing the latter
lowers the male calf rate without changing the number of calves retained.
Parity rounding allocates exactly 100 percentage points.

"""

import argparse
import json
import math
from pathlib import Path

# ======================= EDIT INPUTS HERE =======================
# REQUIRED INPUTS (field names match RuFaS animal JSON)
COW_NUM = 1000  # herd_information.cow_num AND herd_information.herd_num
ANNUAL_SALE_PROB = 0.32  # animal_config.from_literature.culling.annual_sale_prob
ANNUAL_DEATH_PROB = 0.05  # animal_config.from_literature.culling.annual_death_prob
ANNUAL_MILK_YIELD = 12698000  # herd_information.annual_milk_yield, kg/year
MILKING_COW_FRACTION = 0.85  # herd_information.milking_cow_fraction

# OPTIONAL INPUTS (defaults used unless changed by user)
WEAN_DAY = 60  # animal_config.farm_level.calf.wean_day
CALVING_INTERVAL = 403  # animal_config.farm_level.repro.calving_interval
STILL_BIRTH_RATE = 0.03  # animal_config.from_literature.life_cycle.still_birth_rate
PREFRESH_DAY = 21  # animal_config.farm_level.repro.prefresh_day
BREEDING_START_DAY_H = 382  # animal_config.management_decisions.breeding_start_day_h
AGE_FIRST_CALVING_DAYS = 700  # assumption; no direct field in attached animal JSON
CALF_MORTALITY_RATE = 0.05  # animal_config.management_decisions.calf_mortality_rate
HEIFER_MORTALITY_RATE = 0.03  # animal_config.management_decisions.heifer_mortality_rate
PREGNANCY_LOSS_FRACTION = 0.02  # planning assumption; not a one-to-one JSON field
REPRO_CULL_FRACTION = 0.05  # planning assumption; not a one-to-one JSON field
REPLACEMENT_CALF_BUFFER_FRACTION = (
    0.10  # percent extra retained replacements (dairy female calves) above estimated need
)
MALE_CALF_RATE_BUFFER_FRACTION = (
    0.75  # percent extra male calf rate above estimated need; does NOT change count of number of calves to retain
)
# Both are assumptions, not direct RuFaS animal JSON fields.

# Relative shares of the L3+ portion of the herd (automatically normalized).
L3_SHARE_OF_L3_PLUS = 0.40
L4_SHARE_OF_L3_PLUS = 0.40
L5_PLUS_SHARE_OF_L3_PLUS = 0.20
# ===================== END EDIT INPUTS =====================


def round_whole(value):
    """Round nonnegative values to the nearest integer (0.5 rounds up)."""
    return math.floor(value + 0.5)


def round_parities_to_percentages(fractions):
    """Allocate 100 integer percentage points using largest remainders.

    The output decimals are multiples of 0.01 and their sum is exactly 1.00
    at the centesimal/integer-percentage level. Ties use parity order.
    """
    raw = [max(0.0, f * 100) for f in fractions]
    points = [math.floor(x) for x in raw]
    remaining = 100 - sum(points)
    if not 0 <= remaining <= len(points):
        raise ValueError("Internal error: lactation shares do not total 100%")
    order = sorted(range(len(points)), key=lambda i: (-(raw[i] - points[i]), i))
    for i in order[:remaining]:
        points[i] += 1
    assert sum(points) == 100

    # The percentages are exact hundredths conceptually, but Python floats
    # cannot represent most hundredths exactly. Make the final JSON values
    # pass even a strict Python float comparison: sum(values) == 1.0.
    values = [point / 100 for point in points]
    if sum(values) != 1.0:
        original = values[:]
        for pivot in range(len(values) - 1, -1, -1):
            for direction in (0, -1, 1, -2, 2, -3, 3):
                candidate = original[:]
                for _ in range(abs(direction)):
                    candidate[pivot] = math.nextafter(candidate[pivot], math.inf if direction > 0 else -math.inf)
                if 0 <= candidate[pivot] <= 1 and sum(candidate) == 1.0:
                    values = candidate
                    break
            if sum(values) == 1.0:
                break
        if sum(values) != 1.0:
            raise ArithmeticError("Could not make parity fractions sum to exactly 1.0")

    assert sum(values) == 1.0
    return {str(i + 1): values[i] for i in range(len(values))}


def calculate():
    """Return only final RuFaS input values, with JSON-compatible field names."""
    fractions = {
        "annual_sale_prob": ANNUAL_SALE_PROB,
        "annual_death_prob": ANNUAL_DEATH_PROB,
        "milking_cow_fraction": MILKING_COW_FRACTION,
        "still_birth_rate": STILL_BIRTH_RATE,
        "calf_mortality_rate": CALF_MORTALITY_RATE,
        "heifer_mortality_rate": HEIFER_MORTALITY_RATE,
        "pregnancy_loss_fraction": PREGNANCY_LOSS_FRACTION,
        "repro_cull_fraction": REPRO_CULL_FRACTION,
        "replacement_calf_buffer_fraction": REPLACEMENT_CALF_BUFFER_FRACTION,
        "male_calf_rate_buffer_fraction": MALE_CALF_RATE_BUFFER_FRACTION,
    }
    for name, value in fractions.items():
        if not 0 <= value <= 1:
            raise ValueError(f"{name} must be between 0 and 1: {value}")
    if COW_NUM <= 0 or CALVING_INTERVAL <= 0:
        raise ValueError("cow_num and calving_interval must be positive")
    if ANNUAL_MILK_YIELD < 0:
        raise ValueError("annual_milk_yield cannot be negative")
    if sum((PREGNANCY_LOSS_FRACTION, REPRO_CULL_FRACTION, HEIFER_MORTALITY_RATE, CALF_MORTALITY_RATE)) >= 1:
        raise ValueError("Combined replacement loss fractions must be below 1")
    if not 0 <= WEAN_DAY <= BREEDING_START_DAY_H:
        raise ValueError("wean_day must be between 0 and breeding_start_day_h")
    if BREEDING_START_DAY_H + PREFRESH_DAY > AGE_FIRST_CALVING_DAYS:
        raise ValueError("Age at first calving must be >= breeding start + prefresh days")
    if ANNUAL_SALE_PROB + ANNUAL_DEATH_PROB > 1:
        raise ValueError("annual_sale_prob + annual_death_prob must be <= 1")

    shares = (L3_SHARE_OF_L3_PLUS, L4_SHARE_OF_L3_PLUS, L5_PLUS_SHARE_OF_L3_PLUS)
    if any(s < 0 for s in shares) or sum(shares) <= 0:
        raise ValueError("L3+ relative shares must be nonnegative, with a positive total")
    shares = [s / sum(shares) for s in shares]

    cows_leaving = (ANNUAL_SALE_PROB + ANNUAL_DEATH_PROB) * COW_NUM
    annual_keep_calves = (
        (1 + REPLACEMENT_CALF_BUFFER_FRACTION)
        * cows_leaving
        / (1 - PREGNANCY_LOSS_FRACTION - REPRO_CULL_FRACTION - HEIFER_MORTALITY_RATE - CALF_MORTALITY_RATE)
    )
    other_calvings = (COW_NUM - cows_leaving) * 365 / CALVING_INTERVAL
    live_calves = (1 - STILL_BIRTH_RATE) * (cows_leaving + other_calvings)
    if live_calves <= 0:
        raise ValueError("Calculated live calves per year must be positive")
    # The MCR buffer acts ONLY on the female-calf production target.
    # A larger buffer lowers the male calf rate (more female calves born),
    # but leaves annual_keep_calves and initial calf/heifer counts unchanged.
    male_rate = 1 - (annual_keep_calves / live_calves) * (1 + MALE_CALF_RATE_BUFFER_FRACTION)
    if not 0 <= male_rate <= 1:
        raise ValueError("Calculated male calf rate is outside 0–1; check herd inputs")

    heifer_ii_days = AGE_FIRST_CALVING_DAYS - PREFRESH_DAY - BREEDING_START_DAY_H
    heifer_i_days = BREEDING_START_DAY_H - WEAN_DAY
    l1 = ANNUAL_SALE_PROB + ANNUAL_DEATH_PROB
    l2 = (1 - l1) / 2
    l3_plus = l2
    parity_fractions = round_parities_to_percentages([l1, l2, *(l3_plus * s for s in shares)])

    # Section 1: outputs calculated from the herd characteristics.
    calculated_values = {
        "herd_information.calf_num": round_whole(annual_keep_calves * WEAN_DAY / 365),
        "herd_information.heiferI_num": round_whole(
            (1 - CALF_MORTALITY_RATE) * annual_keep_calves * heifer_i_days / 365
        ),
        "herd_information.heiferII_num": round_whole(
            (1 - CALF_MORTALITY_RATE) * annual_keep_calves * heifer_ii_days / 365
        ),
        "herd_information.heiferIII_num_springers": round_whole(
            (1 - CALF_MORTALITY_RATE - HEIFER_MORTALITY_RATE - REPRO_CULL_FRACTION - PREGNANCY_LOSS_FRACTION)
            * annual_keep_calves
            * PREFRESH_DAY
            / 365
        ),
        "herd_information.parity_fractions": parity_fractions,
        "animal_config.farm_level.calf.male_calf_rate_conventional_semen": round_whole(male_rate * 100) / 100,
        "animal_config.farm_level.calf.annual_keep_female_calf_num": round_whole(annual_keep_calves),
    }

    # Section 2: ALL animal JSON fields to update, in the exact relative order
    # they appear in example_freestall_animal.json. Origin labels identify
    # calculated, user-defined, assumed/default, and required-setting values.
    animal_json_fields = {
        "herd_information.calf_num": calculated_values["herd_information.calf_num"],
        "herd_information.heiferI_num": calculated_values["herd_information.heiferI_num"],
        "herd_information.heiferII_num": calculated_values["herd_information.heiferII_num"],
        "herd_information.heiferIII_num_springers": calculated_values["herd_information.heiferIII_num_springers"],
        "herd_information.cow_num": round_whole(COW_NUM),
        "herd_information.herd_num": round_whole(COW_NUM),
        "herd_information.parity_fractions": parity_fractions,
        "herd_information.milking_cow_fraction": round_whole(MILKING_COW_FRACTION * 100) / 100,
        "herd_information.annual_milk_yield": round_whole(ANNUAL_MILK_YIELD),
        "animal_config.management_decisions.breeding_start_day_h": BREEDING_START_DAY_H,
        "animal_config.management_decisions.calf_mortality_rate": CALF_MORTALITY_RATE,
        "animal_config.management_decisions.heifer_mortality_rate": HEIFER_MORTALITY_RATE,
        "animal_config.farm_level.calf.male_calf_rate_conventional_semen": calculated_values[
            "animal_config.farm_level.calf.male_calf_rate_conventional_semen"
        ],
        "animal_config.farm_level.calf.calf_retention_method": "count",
        "animal_config.farm_level.calf.annual_keep_female_calf_num": calculated_values[
            "animal_config.farm_level.calf.annual_keep_female_calf_num"
        ],
        "animal_config.farm_level.calf.wean_day": WEAN_DAY,
        "animal_config.farm_level.repro.prefresh_day": PREFRESH_DAY,
        "animal_config.farm_level.repro.calving_interval": CALVING_INTERVAL,
        "animal_config.from_literature.culling.annual_death_prob": ANNUAL_DEATH_PROB,
        "animal_config.from_literature.culling.annual_sale_prob": ANNUAL_SALE_PROB,
        "animal_config.from_literature.life_cycle.still_birth_rate": STILL_BIRTH_RATE,
    }
    required_user = {
        "herd_information.cow_num",
        "herd_information.herd_num",
        "herd_information.milking_cow_fraction",
        "herd_information.annual_milk_yield",
        "animal_config.from_literature.culling.annual_death_prob",
        "animal_config.from_literature.culling.annual_sale_prob",
    }
    origins = {
        key: (
            "calculated"
            if key in calculated_values
            else (
                "required setting"
                if key.endswith("calf_retention_method")
                else "user input" if key in required_user else "optional/default"
            )
        )
        for key in animal_json_fields
    }

    # Section 3: calculation assumptions without direct animal JSON fields.
    other_inputs = {
        "age_first_calving_days": AGE_FIRST_CALVING_DAYS,
        "pregnancy_loss_fraction": PREGNANCY_LOSS_FRACTION,
        "repro_cull_fraction": REPRO_CULL_FRACTION,
        "replacement_calf_buffer_fraction": REPLACEMENT_CALF_BUFFER_FRACTION,
        "male_calf_rate_buffer_fraction": MALE_CALF_RATE_BUFFER_FRACTION,
        "L3_share_of_L3_plus": L3_SHARE_OF_L3_PLUS,
        "L4_share_of_L3_plus": L4_SHARE_OF_L3_PLUS,
        "L5_plus_share_of_L3_plus": L5_PLUS_SHARE_OF_L3_PLUS,
    }
    assert sum(parity_fractions.values()) == 1.0
    assert animal_json_fields["herd_information.cow_num"] == animal_json_fields["herd_information.herd_num"]
    return {
        "calculated_results": calculated_values,
        "animal_json_fields": animal_json_fields,
        "field_origins": origins,
        "other_inputs_and_assumptions": other_inputs,
    }


def display_value(key, value, origin=None):
    """Make decimal fractions easy to read without changing saved JSON values."""
    prefix = f"  [{origin}] " if origin else "  "
    if isinstance(value, dict):
        print(f"{prefix}{key} (parity 5 means 5+):")
        for parity, fraction in value.items():
            print(f"      {parity}: {fraction:.2f} ({round_whole(fraction * 100)}%)")
        print(f"      Total: {sum(value.values()):.2f} (100%)")
    elif (
        isinstance(value, float)
        and 0 <= value <= 1
        and ("fraction" in key or "rate" in key or "prob" in key or "share" in key)
    ):
        print(f"{prefix}{key}: {value:.2f} ({value * 100:.0f}%)")
    elif key == "herd_information.annual_milk_yield":
        print(f"{prefix}{key}: {value}")
    elif isinstance(value, (int, float)):
        print(f"{prefix}{key}: {value:,}")
    else:
        print(f"{prefix}{key}: {value}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        metavar="PATH",
        help="Save the reference JSON to this file or existing folder.",
    )
    args = parser.parse_args()
    results = calculate()
    print("\nRuFaS HERD CALCULATOR — VALUES FOR MANUAL ANIMAL JSON ENTRY")
    print("=" * 70)
    print("\n1. CALCULATED RESULTS")
    print("-" * 70)
    for key, value in results["calculated_results"].items():
        display_value(key, value)

    print("\n2. VALUES TO ENTER INTO ANIMAL JSON (IN JSON FIELD ORDER)")
    print("-" * 70)
    previous_section = None
    for key, value in results["animal_json_fields"].items():
        section = key.split(".")[0]
        if section != previous_section:
            print(f"\n  [{section}]")
            previous_section = section
        display_value(key, value, origin=results["field_origins"][key])

    print("\n  IMPORTANT: calf_retention_method must be 'count' to use")
    print("             annual_keep_female_calf_num.")

    print("\n3. OTHER INPUTS AND ASSUMED VALUES (NOT ANIMAL JSON FIELDS)")
    print("-" * 70)
    for key, value in results["other_inputs_and_assumptions"].items():
        display_value(key, value)

    if args.output is not None:
        default_name = "rufas_herd_inputs_reference.json"
        path = args.output
        if path.is_dir():
            path = path / default_name
        if path.suffix.lower() != ".json":
            parser.error("--output must specify a .json filename or an existing directory")
        if not path.parent.is_dir():
            parser.error(f"Output directory does not exist: {path.parent}")
        export = {key: value for key, value in results.items() if key != "field_origins"}
        path.write_text(json.dumps(export, indent=2) + "\n", encoding="utf-8")
        print(f"\nReference report saved to: {path.resolve()}")
        print("Note: Saving within your Git repo may produce an untracked or modified file.")
    else:
        print("\nNo output files created; results are displayed above for manual entry.")


if __name__ == "__main__":
    main()
