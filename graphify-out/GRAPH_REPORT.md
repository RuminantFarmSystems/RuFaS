# Graph Report - RuFaS-MyForageSystem  (2026-06-09)

## Corpus Check
- 204 files · ~253,857 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 5840 nodes · 48684 edges · 47 communities detected
- Extraction: 10% EXTRACTED · 90% INFERRED · 0% AMBIGUOUS · INFERRED: 43776 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 60|Community 60]]
- [[_COMMUNITY_Community 65|Community 65]]
- [[_COMMUNITY_Community 66|Community 66]]
- [[_COMMUNITY_Community 67|Community 67]]
- [[_COMMUNITY_Community 68|Community 68]]
- [[_COMMUNITY_Community 69|Community 69]]
- [[_COMMUNITY_Community 70|Community 70]]
- [[_COMMUNITY_Community 71|Community 71]]
- [[_COMMUNITY_Community 72|Community 72]]
- [[_COMMUNITY_Community 73|Community 73]]
- [[_COMMUNITY_Community 74|Community 74]]
- [[_COMMUNITY_Community 75|Community 75]]
- [[_COMMUNITY_Community 76|Community 76]]
- [[_COMMUNITY_Community 77|Community 77]]
- [[_COMMUNITY_Community 78|Community 78]]
- [[_COMMUNITY_Community 79|Community 79]]

## God Nodes (most connected - your core abstractions)
1. `OutputManager` - 2046 edges
2. `GeneralConstants` - 1513 edges
3. `RufasTime` - 1448 edges
4. `MeasurementUnits` - 1155 edges
5. `Utility` - 1026 edges
6. `AnimalType` - 841 edges
7. `InputManager` - 807 edges
8. `AnimalModuleConstants` - 712 edges
9. `SoilData` - 695 edges
10. `AnimalConfig` - 693 edges

## Surprising Connections (you probably didn't know these)
- `main()` --calls--> `OutputManager`  [INFERRED]
  main.py → RUFAS/output_manager.py
- `CaseInsensitiveArgumentAction` --uses--> `OutputManager`  [INFERRED]
  main.py → RUFAS/output_manager.py
- `Parse command line options, if applicable` --uses--> `OutputManager`  [INFERRED]
  main.py → RUFAS/output_manager.py
- `main()` --calls--> `TaskManager`  [INFERRED]
  main.py → RUFAS/task_manager.py
- `main()` --calls--> `LogVerbosity`  [INFERRED]
  main.py → RUFAS/output_manager.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.0
Nodes (1021): Initialize genetic attributes., Calculate EBV and ranking index values., Recalculate genetic values at lactation start., Calculate TBV values for an animal entering the herd., Calculate TBV values for a newborn calf., Calculate Permanent Environment Effect (E_permanent) values., Calculate Permanent Environment Effect (E_permanent) values., Calculate Temporary Environment Effect (E_temporary) values. (+1013 more)

### Community 1 - "Community 1"
Cohesion: 0.0
Nodes (691): CarbonCycling, _determine_soil_active_carbon_fraction(), _determine_soil_mass(), _determine_soil_overall_carbon_fraction(), _determine_soil_passive_carbon_fraction(), _determine_soil_slow_carbon_fraction(), _determine_soil_volume(), _determine_total_carbon_CO2_lost() (+683 more)

### Community 2 - "Community 2"
Cohesion: 0.01
Nodes (593): BiomassAllocation, _determine_above_ground_biomass(), _determine_accumulated_biomass(), _determine_below_ground_biomass(), _determine_max_accumulation(), _intercept_radiation(), Partition the accumulated biomass into above ground and below ground portions., Partition the accumulated biomass into above ground and below ground portions. (+585 more)

### Community 3 - "Community 3"
Cohesion: 0.03
Nodes (576): Animal, AnimalGroupingScenario, The different scenarios for grouping animals on a farm.     Each scenario is a d, Get the animal subtype of the given heiferIII.          Parameters         -----, Get the animal subtype of the given heiferIII.          Parameters         -----, Get the animal subtype of the given cow.          Parameters         ----------, Get the animal subtype of the given cow.          Parameters         ----------, Get the animal type of the given animal.          Parameters         ---------- (+568 more)

### Community 4 - "Community 4"
Cohesion: 0.05
Nodes (535): AnimalConfig, initialize_animal_config(), AnimalConfig class that holds all the animal configuration parameters from user, Initialize the animal config from the input manager user input data., Initialize the animal config from the input manager user input data., Cow reproduction program for the specified animal.          This property retrie, Retrieve the CowTAISubProtocol associated with the cow's ovsynch program if the, Setter method for the cow_ovsynch_program property.          Parameters (+527 more)

### Community 5 - "Community 5"
Cohesion: 0.02
Nodes (322): make_empty_manure_stream(), ManureStream, This class packages manure data for transfer between the Animal and Manure modul, ManureNutrients, A class to store the relevant manure nutrient information to be passed to the cr, Return a new ManureNutrients with all numeric nutrient/mass         fields zeroe, Add two ManureNutrients objects together.          Parameters         ----------, Multiply a ManureNutrients object by a scalar (left multiplication, i.e. ManureN (+314 more)

### Community 6 - "Community 6"
Cohesion: 0.03
Nodes (190): HerdManager, AvailableFeedsBuilder, FeedFulfillmentResults, IdealFeeds, PlanningCycleAllowance, _process_feed_library(), PurchaseAllowance, RuntimePurchaseAllowance (+182 more)

### Community 7 - "Community 7"
Cohesion: 0.02
Nodes (121): ABC, AnimalHealth, AnimalHealthStatus, Calculator class representing the health status of the animal.     Will be the a, Disease, Base function for disease risk determination.          Parameters         ------, Takes in incidence rate and compares it to RNG to deterine if animal will develo, Probability mass function to get the risk period. (+113 more)

### Community 8 - "Community 8"
Cohesion: 0.01
Nodes (121): _record_animal_events(), _record_cows_conception_rate(), _record_heiferIIs_conception_rate(), _report_all_animals_genetic_history(), report_end_of_simulation(), report_sold_animal_information(), report_sold_animal_information_sort_by_sell_day(), report_stillborn_calves_information() (+113 more)

### Community 9 - "Community 9"
Cohesion: 0.07
Nodes (1): milk_statistics()

### Community 10 - "Community 10"
Cohesion: 0.16
Nodes (18): _calculate_activity_energy_requirements(), _calculate_calcium_requirement(), _calculate_dry_matter_intake(), _calculate_growth_energy_requirements(), _calculate_maintenance_energy_requirements(), _calculate_phosphorus_requirement(), _calculate_pregnancy_energy_requirements(), _calculate_protein_requirement() (+10 more)

### Community 11 - "Community 11"
Cohesion: 0.11
Nodes (3): make_empty_evaluation_results(), make_empty_nutrition_requirements(), make_empty_nutrition_supply()

### Community 12 - "Community 12"
Cohesion: 0.23
Nodes (10): Calculates the base manure production in terms of phosphorus for an animal., Calculates the base manure production in terms of phosphorus for an animal., Processes the digestion for different types of animals by calculating methane em, calculate_cow_methane(), _calculate_cow_mills_methane(), _calculate_dry_cow_enteric_methane(), calculate_heifer_methane(), _calculate_IPCC_methane() (+2 more)

### Community 13 - "Community 13"
Cohesion: 0.27
Nodes (7): calculate_anaerobic_coefficient(), calculate_carbon_decomposition(), calculate_carbon_decomposition_rate(), calculate_ifsm_methane_emission(), calculate_max_microbial_decomposition_rate(), calculate_methane_conversion_factor(), calculate_slow_fraction_decomposition_rate()

### Community 16 - "Community 16"
Cohesion: 0.4
Nodes (3): Initialize the RationConfig class with the provided feed information. If the inp, RationConfig provides a structured way to represent the collection of animal req, RationConfig

### Community 17 - "Community 17"
Cohesion: 0.5
Nodes (2): Initialize an event from a string.          Parameters         ----------, Add a cow life event.          Parameters         ----------         animal_age

### Community 20 - "Community 20"
Cohesion: 1.0
Nodes (2): get_adjusted_schedule(), get_schedule()

### Community 21 - "Community 21"
Cohesion: 1.0
Nodes (1): Parses a unit string to handle units with exponents.          Parameters

### Community 22 - "Community 22"
Cohesion: 1.0
Nodes (1): Extracts the units from a key.          Parameters         ----------         ke

### Community 23 - "Community 23"
Cohesion: 1.0
Nodes (1): Combines two unit dictionaries by adding or subtracting their exponents.

### Community 24 - "Community 24"
Cohesion: 1.0
Nodes (1): Simplify the units by cancelling out common units in the numerator and denominat

### Community 25 - "Community 25"
Cohesion: 1.0
Nodes (1): Converts two dictionaries of units (numerator and denominator) back to a single

### Community 36 - "Community 36"
Cohesion: 1.0
Nodes (1): Checks if maturity has been reached based on the fraction of potential heat unit

### Community 37 - "Community 37"
Cohesion: 1.0
Nodes (1): Indicates if the plant is in its growing season.          Returns         ------

### Community 38 - "Community 38"
Cohesion: 1.0
Nodes (1): Checks if a user-defined harvest index is given, which triggers a harvest index

### Community 39 - "Community 39"
Cohesion: 1.0
Nodes (1): Check if the plant is in senescence.          Returns         -------         bo

### Community 40 - "Community 40"
Cohesion: 1.0
Nodes (1): Calculate the maximum amount of water that can be held in the canopy.          R

### Community 41 - "Community 41"
Cohesion: 1.0
Nodes (1): Calculate the fraction of potential heat units accumulated by the plant.

### Community 45 - "Community 45"
Cohesion: 1.0
Nodes (1): Calculate the amount of water in the soil profile when completely saturated (mm)

### Community 52 - "Community 52"
Cohesion: 1.0
Nodes (1): True if the animal is a heifer, False otherwise

### Community 53 - "Community 53"
Cohesion: 1.0
Nodes (1): True if the animal is a cow, False otherwise

### Community 60 - "Community 60"
Cohesion: 1.0
Nodes (1): Calculates reduction in methane yield (%) due to addition of certain methane mit

### Community 65 - "Community 65"
Cohesion: 1.0
Nodes (1): Data class containing crop variables based on SWAT database.      Attributes

### Community 66 - "Community 66"
Cohesion: 1.0
Nodes (1): Initialize all attributes with defaults that depend on other attributes after th

### Community 67 - "Community 67"
Cohesion: 1.0
Nodes (1): Checks if maturity has been reached based on the fraction of potential heat unit

### Community 68 - "Community 68"
Cohesion: 1.0
Nodes (1): Indicates if the plant is in its growing season.          Returns         ------

### Community 69 - "Community 69"
Cohesion: 1.0
Nodes (1): Checks if a user-defined harvest index is given, which triggers a harvest index

### Community 70 - "Community 70"
Cohesion: 1.0
Nodes (1): Check if the plant is in senescence.          Returns         -------         bo

### Community 71 - "Community 71"
Cohesion: 1.0
Nodes (1): Calculate the maximum amount of water that can be held in the canopy.          R

### Community 72 - "Community 72"
Cohesion: 1.0
Nodes (1): Calculate the fraction of potential heat units accumulated by the plant.

### Community 73 - "Community 73"
Cohesion: 1.0
Nodes (1): Calculate the amount of water in the soil profile when completely saturated (mm)

### Community 74 - "Community 74"
Cohesion: 1.0
Nodes (1): Initialize a new AnimalEvents object.

### Community 75 - "Community 75"
Cohesion: 1.0
Nodes (1): Initialize event from a string          Args:                 events_str: string

### Community 76 - "Community 76"
Cohesion: 1.0
Nodes (1): Add a cow life event          Args:                 animal_age: the date counter

### Community 77 - "Community 77"
Cohesion: 1.0
Nodes (1): Return the most recent age at which the event_description happened          Para

### Community 78 - "Community 78"
Cohesion: 1.0
Nodes (1): Method for adding two AnimalEvents objects.

### Community 79 - "Community 79"
Cohesion: 1.0
Nodes (1): Initialize the RationConfig class with the provided feed information. If the inp

## Knowledge Gaps
- **426 isolated node(s):** `A list of acceptable units used within the RuFaS model.`, `Returns the value of the enum member as its string representation.`, `Parses a unit string to handle units with exponents.          Parameters`, `Extracts the units from a key.          Parameters         ----------         ke`, `Combines two unit dictionaries by adding or subtracting their exponents.` (+421 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 9`** (28 nodes): `calf_birth_weight()`, `calves()`, `calving_interval()`, `calving_interval_history()`, `conceptus_weight()`, `cow_ovsynch_program()`, `cow_presynch_program()`, `cow_reproduction_program()`, `cow_resynch_program()`, `daily_distance()`, `daily_horizontal_distance()`, `daily_vertical_distance()`, `days_in_milk()`, `days_in_pregnancy()`, `dead()`, `future_cull_date()`, `future_death_date()`, `gestation_length()`, `heifer_reproduction_program()`, `heifer_reproduction_sub_program()`, `is_milking()`, `is_pregnant()`, `milk_statistics()`, `set_nutrient_standard()`, `setup_lactation_curve_parameters()`, `sold()`, `stillborn()`, `animal.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 17`** (4 nodes): `.add_event()`, `.init_from_string()`, `Initialize an event from a string.          Parameters         ----------`, `Add a cow life event.          Parameters         ----------         animal_age`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 20`** (3 nodes): `get_adjusted_schedule()`, `get_schedule()`, `hormone_delivery_schedule.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 21`** (1 nodes): `Parses a unit string to handle units with exponents.          Parameters`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 22`** (1 nodes): `Extracts the units from a key.          Parameters         ----------         ke`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 23`** (1 nodes): `Combines two unit dictionaries by adding or subtracting their exponents.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 24`** (1 nodes): `Simplify the units by cancelling out common units in the numerator and denominat`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 25`** (1 nodes): `Converts two dictionaries of units (numerator and denominator) back to a single`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 36`** (1 nodes): `Checks if maturity has been reached based on the fraction of potential heat unit`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 37`** (1 nodes): `Indicates if the plant is in its growing season.          Returns         ------`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 38`** (1 nodes): `Checks if a user-defined harvest index is given, which triggers a harvest index`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 39`** (1 nodes): `Check if the plant is in senescence.          Returns         -------         bo`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 40`** (1 nodes): `Calculate the maximum amount of water that can be held in the canopy.          R`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 41`** (1 nodes): `Calculate the fraction of potential heat units accumulated by the plant.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 45`** (1 nodes): `Calculate the amount of water in the soil profile when completely saturated (mm)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 52`** (1 nodes): `True if the animal is a heifer, False otherwise`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 53`** (1 nodes): `True if the animal is a cow, False otherwise`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 60`** (1 nodes): `Calculates reduction in methane yield (%) due to addition of certain methane mit`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 65`** (1 nodes): `Data class containing crop variables based on SWAT database.      Attributes`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 66`** (1 nodes): `Initialize all attributes with defaults that depend on other attributes after th`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 67`** (1 nodes): `Checks if maturity has been reached based on the fraction of potential heat unit`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 68`** (1 nodes): `Indicates if the plant is in its growing season.          Returns         ------`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 69`** (1 nodes): `Checks if a user-defined harvest index is given, which triggers a harvest index`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 70`** (1 nodes): `Check if the plant is in senescence.          Returns         -------         bo`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 71`** (1 nodes): `Calculate the maximum amount of water that can be held in the canopy.          R`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 72`** (1 nodes): `Calculate the fraction of potential heat units accumulated by the plant.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 73`** (1 nodes): `Calculate the amount of water in the soil profile when completely saturated (mm)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 74`** (1 nodes): `Initialize a new AnimalEvents object.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 75`** (1 nodes): `Initialize event from a string          Args:                 events_str: string`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 76`** (1 nodes): `Add a cow life event          Args:                 animal_age: the date counter`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 77`** (1 nodes): `Return the most recent age at which the event_description happened          Para`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 78`** (1 nodes): `Method for adding two AnimalEvents objects.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 79`** (1 nodes): `Initialize the RationConfig class with the provided feed information. If the inp`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `OutputManager` connect `Community 0` to `Community 1`, `Community 2`, `Community 3`, `Community 4`, `Community 5`, `Community 6`, `Community 7`, `Community 8`, `Community 12`, `Community 13`?**
  _High betweenness centrality (0.299) - this node is a cross-community bridge._
- **Why does `GeneralConstants` connect `Community 0` to `Community 1`, `Community 2`, `Community 3`, `Community 4`, `Community 5`, `Community 6`, `Community 7`, `Community 8`, `Community 12`?**
  _High betweenness centrality (0.229) - this node is a cross-community bridge._
- **Why does `SoilData` connect `Community 1` to `Community 8`, `Community 0`, `Community 2`, `Community 6`?**
  _High betweenness centrality (0.120) - this node is a cross-community bridge._
- **Are the 1964 inferred relationships involving `OutputManager` (e.g. with `CaseInsensitiveArgumentAction` and `Parse command line options, if applicable`) actually correct?**
  _`OutputManager` has 1964 INFERRED edges - model-reasoned connections that need verification._
- **Are the 1511 inferred relationships involving `GeneralConstants` (e.g. with `LogVerbosity` and `OriginLabel`) actually correct?**
  _`GeneralConstants` has 1511 INFERRED edges - model-reasoned connections that need verification._
- **Are the 1441 inferred relationships involving `RufasTime` (e.g. with `Weather` and `The `Weather` class manages all weather data used to run a single simulation.`) actually correct?**
  _`RufasTime` has 1441 INFERRED edges - model-reasoned connections that need verification._
- **Are the 1151 inferred relationships involving `MeasurementUnits` (e.g. with `LogVerbosity` and `OriginLabel`) actually correct?**
  _`MeasurementUnits` has 1151 INFERRED edges - model-reasoned connections that need verification._