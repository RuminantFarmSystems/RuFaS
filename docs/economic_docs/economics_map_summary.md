# Economics map narrative

This document summarizes how each cost or revenue item in `input/data/EEE/economics_map.json` is intended to connect biophysical outputs with commodity price inputs and any preprocessing needed before aggregation. It is meant to stay in sync with the map so later code changes keep the economic intent intact.

## Animal module

- **Purchased heifers** – Uses the counted number of purchased heifers reported by `AnimalModuleReporter.report_life_cycle_manager_data.bought_heifer_num` and multiplies by the bred heifer price from `commodity_prices.cow_dairy_heifer_bred_t3.dollar_per_animal.csv`.
- **Semen purchased** – Sums daily AI events across heifers and cows (`AnimalModuleReporter._record_heiferIIs_conception_rate.heiferII_total_num_ai_performed` and `AnimalModuleReporter._record_cows_conception_rate.cow_total_num_ai_performed`). The semen price file is chosen from the user’s management input (`animal.animal_config.management_decisions.semen_type`) and can be conventional, sexed, or beef semen price per straw. Preprocessing aggregates daily counts and selects the matching semen price series.
- **Bedding requirements** – Daily head counts per pen from `AnimalModuleReporter.report_daily_pen_total.number_of_animals_in_pen_.*` are matched to the bedding type declared for each pen (`animal.pen_information..*.manure_streams.0.bedding_name`). Price files differ by bedding material (sand, straw, sawdust, manure solids, compost bedded pack) and are annual dollars per head; preprocessing maps head counts to the correct bedding price by pen.
- **Animal – Labor hours** – Uses per-day labor hours from `Economic_inputs.Animal.labor_hours_per_day` scaled by hourly wage in `farm_services.labor_hours.dollar_per_hour.csv`.
- **Animal investment (fuel, utilities, water)** – Daily consumption from the economic inputs (`gasoline_liters_per_day`, `diesel_liters_per_day`, `propane_liters_per_day`, `natural_gas_megajoule_per_day`, `electricity_kwh_per_day`, `water_cubic_meter_per_day`) is paired with the corresponding commodity price series for gasoline, diesel, wholesale propane, industrial natural gas, industrial electricity, and municipal water.

### Animal revenue

- **FPCM (Milk Production)** – Uses fat- and protein-corrected milk computed during preprocessing (`Economic_preprocessing.Animal.FPCM`) and multiplies by the retail milk price series in `commodity_prices.milk_retail.dollar_per_liter.csv`. Preprocessing follows the FPCM calculation logic in `economic_preprocessing.json` to transform raw milk outputs.
- **Sold calves** – Revenues come from sold calf weights (`AnimalModuleReporter.report_sold_animal_information_sort_by_sell_day.sold_calves_sold_weight`) valued with `commodity_prices.calves_all.dollar_per_kilogram.csv`.
- **Sold heifer IIs** – Sold weights from `report_sold_animal_information_sort_by_sell_day.heiferII_sold_weight` use `commodity_prices.cow_dairy_heifer_open.dollar_per_animal.csv`.
- **Sold heifer IIIs** – Counts from life-cycle manager reports (`sold_heiferII_num` and `sold_heiferIII_oversupply_num`) are summed before applying the bred heifer price (`cow_dairy_heifer_bred_t3`).
- **Sold cows** – Sold cow counts (`report_sold_animal_information_sort_by_sell_day.sold_cows_sold_count`) are multiplied by `commodity_prices.cows_milk.dollar_per_animal.csv` after summing the counts.
- **Carbon credits from enteric emissions reduction** – Daily enteric methane emissions per pen (`report_enteric_methane_emission.enteric_methane_emission.*`) are summed and converted to tonnes before applying the carbon credit price in `commodity_prices.carbon_credits_enteric.dollar_per_tonne.csv`.

## Manure module

### Costs

- **Purchased manure** – Off-farm manure mass (`ManureManager._record_manure_request_results.off_farm_manure.total_manure_mass`) is priced using `commodity_prices.bedding_manure_solids.dollar_per_kilogram.csv`.
- **General manure operational labor** – Daily labor hours from `Economic_inputs.Manure.general.labor_hours` are valued with `farm_services.labor_hours.dollar_per_hour.csv`.
- **Slurry storage operational costs** – Daily labor, diesel, gasoline, propane, natural gas, electricity, and water consumption from `Economic_inputs.Manure.slurry_storage` are paired with the corresponding wage or commodity price files (labor hours; diesel/gasoline per liter; propane per liter; industrial natural gas per megajoule; residential, commercial, or industrial electricity per kWh; municipal water per cubic meter).
- **Digester operational costs** – Similar daily inputs from `Economic_inputs.Manure.digester` map to wage or commodity price series for labor, diesel, gasoline, propane, industrial natural gas, multiple electricity tariffs, and municipal water. Additional digester operating costs reference helper methods in `digester_costs.py`, applying natural gas, industrial electricity, and digester carbon credit price files as needed.
- **Manure disposal quantity and transport** – Manually provided disposal mass and transport distance (`Economic_inputs.Manure.manure_disposal_*`) use user-specified per-kilogram and per-kilometer prices; these entries are fully manual with no linked commodity series.

### Revenue

- **Sold manure** – Manual manure sales values (`Economic_inputs.Manure.manure_sales`) are multiplied by `commodity_prices.bedding_manure_solids.dollar_per_kilogram.csv`; future logic could scale sales to total manure production.
- **Digester co-products** – Placeholders for fertilizer nutrients, bedding solids, RNG, electricity, and carbon credits reference future outputs from the manure module. Current mappings list the relevant commodity price files (net fertilizer N/P/K per kilogram; manure solids per kilogram; industrial natural gas per megajoule for RNG; industrial electricity per kWh; carbon credit price per tonne), with preprocessing deferred until those outputs are available.

## Feed storage module

### Costs

- **Purchased feed costs** – Feed purchase costs recorded per ration interval (`FeedManager.purchase_feed.ration_interval_*_cost`) should be either prorated across days until the next ration reformulation or left as interval totals with zeroes on non-purchase days. Commodity price series for each feed ingredient are available for historical comparisons or scaling, though the current logic uses the recorded costs directly.
- **Feed storage labor** – Daily labor hours from `Economic_inputs.Feed_storage.labor_hours_per_day` use the labor wage series in `farm_services.labor_hours.dollar_per_hour.csv`.

### Revenue

- **Feed sales** – Harvest yields per field (`CropManagement._record_yield.harvest_yield.field='field_.*'`) are matched to the corresponding feed commodity price series (same set used for purchased feed) to value feed sold from each harvest event.

## Soil and crop module

### Costs

- **Nitrogen, phosphorus, potassium fertilizer use** – Fertilizer masses from the schedules are summed across applications (see fertilizer schedule inputs) and priced using the net N/P/K commodity price series per kilogram.
- **Other fertilizer types** – Placeholder entries for ammonium nitrate, super phosphate, and urea using the listed net fertilizer price files when those outputs are available.
- **Seed costs** – Each field’s `crop_specification` selects the matching seed price file (e.g., corn_seed, soybean_seed), and field area is converted from hectares to square meters (divide by 10,000). Because seed purchases are scenario-level events, total seed cost per field is evenly allocated across all simulation days.
- **Land purchase and rental** – Manual entries for land purchased or rented over the whole simulation (`Economic_inputs.Soil_and_crop.land_ha_purchased` and `land_ha_rented`) are valued with per-hectare purchase (`capital_costs.land_ha`) or rental (`farm_services.land_ha_rent`) price files. Land purchases are single-scenario values rather than per-day series.
- **Crop labor hours** – Daily labor from `Economic_inputs.Soil_and_crop.labor_hours_per_day` multiplied by the labor wage series.
- **Crop water consumption** – Daily irrigation uptake (`FieldDataReporter.send_crop_daily_variables.water_uptake.*`) uses `commodity_prices.water_irrigation.dollar_per_cubic_meter.csv`.
- **Tractor hours for crops** – Pending tractor and implement outputs will map to hourly tractor service price files for small, medium, and large tractors.

### Revenue

- **Carbon credits from soil conservation practice** – Scenario-level carbon credits (`Economic_inputs.Soil_and_crop.carbon_credits_whole_simulation_tonnes`) are priced with `commodity_prices.carbon_credits_soil.dollar_per_tonne.csv`; future work may scale credits to crop outputs or conservation scenarios.
