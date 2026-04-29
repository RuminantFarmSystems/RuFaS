"""Hardcoded economics mapping derived from input/data/EEE/economics_map.json.

This file is generated to decouple the economics preprocessing from runtime JSON loading.
"""

from __future__ import annotations

from typing import Any, Dict

ECONOMIC_MAP: Dict[str, Dict[str, Dict[str, Dict[str, Any]]]] = {
    "Animal": {
        "Costs": {
            "Animal - Labor hours": {
                "input_manager": ["economic_inputs.Animal.labor_hours_per_day"],
                "economics_files": ["farm_services_labor_hours_dollar_per_hour"],
                "future_expansion": "more " "subcategories, " "e.g. vet, " "milker",
                "notes": "",
            },
            "Animal investment - Diesel consumption": {
                "input_manager": ["economic_inputs.Animal.diesel_liters_per_day"],
                "economics_files": ["commodity_prices_diesel_dollar_per_liter"],
                "notes": "",
            },
            "Animal investment - Electricity consumption": {
                "input_manager": ["economic_inputs.Animal.electricity_kwh_per_day"],
                "economics_files": ["commodity_prices_elec_industrial_dollar_per_kwh"],
                "notes": "",
            },
            "Animal investment - Gasoline consumption": {
                "input_manager": ["economic_inputs.Animal.gasoline_liters_per_day"],
                "economics_files": ["commodity_prices_gasoline_dollar_per_liter"],
                "notes": "",
            },
            "Animal investment - Natural gas consumption": {
                "input_manager": ["economic_inputs.Animal.natural_gas_megajoule_per_day"],
                "economics_files": ["commodity_prices_natgas_industrial_dollar_per_megajoule"],
                "notes": "",
            },
            "Animal investment - Propane consumption": {
                "input_manager": ["economic_inputs.Animal.propane_liters_per_day"],
                "economics_files": ["commodity_prices_propane_wholesale_dollar_per_liter"],
                "notes": "",
            },
            "Animal investment - Water consumption": {
                "input_manager": ["economic_inputs.Animal.water_cubic_meter_per_day"],
                "economics_files": ["commodity_prices_water_municipal_dollar_per_cubic_meter"],
                "notes": "",
            },
            "Bedding requirements": {
                "biophysical_simulation": ["AnimalModuleReporter.report_daily_pen_total.number_of_animals_in_pen_.*"],
                "input_manager": ["animal.pen_information.*.manure_streams.0.bedding_name"],
                "match_source": "input_manager",
                "wildcard_value_map": {
                    "0_CALF": "0",
                    "1_GROWING": "1",
                    "2_CLOSE_UP": "2",
                    "3_LAC_COW": "3"
                },
                "economics_files": {
                    "CBPB": "commodity_prices_bedding_compost_bedded_pack_dollar_per_head",
                    "manure_solids": "commodity_prices_bedding_manure_solids_dollar_per_head",
                    "sand": "commodity_prices_bedding_sand_dollar_per_head",
                    "sawdust": "commodity_prices_bedding_sawdust_dollar_per_head",
                    "straw": "commodity_prices_bedding_straw_dollar_per_head",
                },
                "preprocessing": "average number of animals in each pen",
            },
            "Purchased heifers": {
                "biophysical_simulation": ["AnimalModuleReporter.report_life_cycle_manager_data.bought_heifer_num"],
                "economics_files": ["commodity_prices_cow_dairy_heifer_bred_t3_dollar_per_animal"],
            },
            "Semen purchased": {
                "biophysical_simulation": [
                    "AnimalModuleReporter._record_heiferIIs_conception_rate.heiferII_total_num_ai_performed",
                    "AnimalModuleReporter._record_cows_conception_rate.cow_total_num_ai_performed",
                ],
                "economics_files": {
                    "beef": "commodity_prices_semen_beef_dollar_per_straw",
                    "conventional": "commodity_prices_semen_conventional_dollar_per_straw",
                    "input_manager_location": "animal.animal_config.management_decisions.semen_type",
                    "sexed": "commodity_prices_semen_sexed_dollar_per_straw",
                },
                "preprocessing": "daily sum of both " "biophysical " "outputs, select " "econ file from " "user input",
                "processing": "",
            },
        },
        "Revenue": {
            "Carbon credits from enteric emissions reduction": {
                "biophysical_simulation": [
                    "AnimalModuleReporter.report_enteric_methane_emission.enteric_methane_emission.*"
                ],
                "economics_files": ["commodity_prices_carbon_credits_enteric_dollar_per_tonne_CO2e"],
                "notes": "Sum "
                "across "
                "all "
                "pens "
                "(e.g. "
                "each "
                "of "
                "the "
                "pens "
                "captured "
                "by "
                ".*), "
                "then "
                "convert "
                "enteric_methane_emission "
                "to "
                "tonnes",
            },
            "FPCM (Milk Production)": {
                "biophysical_simulation": ["Economic_preprocessing.Animal.FPCM"],
                "economics_files": ["commodity_prices_milk_retail_dollar_per_liter"],
                "preprocessing": "FPCM "
                "calculation "
                "from raw "
                "values, "
                "see "
                "economic_preprocessing.json "
                "as "
                "example "
                "logic",
            },
            "Sold calves": {
                "biophysical_simulation": [
                    "AnimalModuleReporter.report_sold_animal_information_sort_by_sell_day.sold_calves_sold_weight"
                ],
                "economics_files": ["commodity_prices_calves_all_dollar_per_kilogram"],
            },
            "Sold cows": {
                "biophysical_simulation": [
                    "AnimalModuleReporter.report_sold_animal_information_sort_by_sell_day.sold_cows_sold_count"
                ],
                "economics_files": ["commodity_prices_cows_milk_dollar_per_animal"],
                "preprocessing": "sum number sold",
            },
            "Sold heifer IIIs": {
                "biophysical_simulation": [
                    "AnimalModuleReporter.report_life_cycle_manager_data.sold_heiferII_num",
                    "AnimalModuleReporter.report_life_cycle_manager_data.sold_heiferIII_oversupply_num",
                ],
                "economics_files": ["commodity_prices_cow_dairy_heifer_bred_t3_dollar_per_animal"],
                "preprocessing": "sum from both " "biophysical " "simulation " "locations",
            },
            "Sold heifer IIs": {
                "biophysical_simulation": [
                    "AnimalModuleReporter.report_sold_animal_information_sort_by_sell_day.heiferII_sold_weight"
                ],
                "economics_files": ["commodity_prices_cow_dairy_heifer_open_dollar_per_animal"],
            },
        },
    },
    "Feed_storage": {
        "Costs": {
            "Feed storage - Labor hours": {
                "input_manager": ["economic_inputs.Feed_storage.labor_hours_per_day"],
                "economics_files": ["farm_services_labor_hours_dollar_per_hour"],
            },
            "Purchased feed costs": {
                "biophysical_simulation": ["FeedManager.purchase_feed.ration_interval_*_cost"],
                "economics_files": [
                    "commodity_prices_alfalfa_hay_dollar_per_kilogram",
                    "commodity_prices_alfalfa_silage_dollar_per_kilogram",
                    "commodity_prices_almond_hulls_dollar_per_kilogram",
                    "commodity_prices_barley_silage_dollar_per_kilogram",
                    "commodity_prices_cotton_seed_hulls_dollar_per_kilogram",
                    "commodity_prices_cotton_seed_meal_dollar_per_kilogram",
                    "commodity_prices_cotton_seed_whole_dollar_per_kilogram",
                    "commodity_prices_corn_grain_dollar_per_kilogram",
                    "commodity_prices_corn_silage_dollar_per_kilogram",
                    "commodity_prices_distiller_grains_dried_10pct_dollar_per_kilogram",
                    "commodity_prices_distiller_grains_modified_wet_50pct_dollar_per_kilogram",
                    "commodity_prices_distiller_grains_wet_65pct_dollar_per_kilogram",
                    "commodity_prices_hay_excluding_alfalfa_dollar_per_kilogram",
                    "commodity_prices_hay_all_dollar_per_kilogram",
                    "commodity_prices_rye_grain_dollar_per_kilogram",
                    "commodity_prices_soybean_grain_dollar_per_kilogram",
                    "commodity_prices_soybean_hulls_dollar_per_kilogram",
                    "commodity_prices_soybean_meal_dollar_per_kilogram",
                    "commodity_prices_sundan_silage_dollar_per_kilogram",
                    "commodity_prices_winter_wheat_grain_dollar_per_kilogram",
                    "commodity_prices_calcium_phosphate_di_dollar_per_kilogram",
                    "commodity_prices_calf_starter_18cp_dollar_per_kilogram",
                    "commodity_prices_limestone_dollar_per_kilogram",
                ],
                "future_expansion": "cases "
                "where "
                "historical "
                "references "
                "are "
                "desired: "
                "Instead "
                "of "
                "cost, "
                "select "
                "from "
                "economics_input "
                "options, "
                "all "
                "end "
                "in "
                "'_dollar_per_kilogram', "
                "compare "
                "price "
                "in "
                "input "
                "to "
                "this "
                "price, "
                "scale "
                "accordingly "
                "(e.g. "
                "price "
                "was "
                "1, "
                "in "
                "file "
                "is "
                "2, "
                "double "
                "the "
                "final "
                "cost)",
                "processing": "no "
                "commodity "
                "price "
                "needed, "
                "just loop "
                "over each "
                "feed .*, "
                "report "
                "separately, "
                "but "
                "expanded "
                "evenly "
                "across the "
                "subsequent "
                "ration "
                "interval. "
                "To explain "
                "this a "
                "little "
                "more...this "
                "isn't "
                "reported "
                "daily, but "
                "on each "
                "ration "
                "formulation "
                "(usually "
                "the "
                "interval). "
                "So this "
                "price "
                "should be "
                "either "
                "prorated "
                "over the "
                "rest of "
                "the days, "
                "or the "
                "'gaps' for "
                "each day "
                "should be "
                "filled in "
                "with 0s. "
                "So if the "
                "ration "
                "interval "
                "cost was "
                "reported "
                "for day 0, "
                "and the "
                "next on "
                "day 30, "
                "either the "
                "price of "
                "day 0 "
                "should be "
                "evenly "
                "divided "
                "across "
                "days 0-29, "
                "or the "
                "whole "
                "price for "
                "0 should "
                "be "
                "assigned "
                "to the 0th "
                "day in the "
                "list, and "
                "for days "
                "1-29 a "
                "price of 0 "
                "is "
                "assigned.'",
            },
        },
        "Revenue": {
            "Feed_sales": {
                "biophysical_simulation": ["CropManagement._record_yield.harvest_yield.field='field_.*'"],
                "economics_files": [
                    "commodity_prices_alfalfa_hay_dollar_per_kilogram",
                    "commodity_prices_alfalfa_silage_dollar_per_kilogram",
                    "commodity_prices_almond_hulls_dollar_per_kilogram",
                    "commodity_prices_barley_silage_dollar_per_kilogram",
                    "commodity_prices_cotton_seed_hulls_dollar_per_kilogram",
                    "commodity_prices_cotton_seed_meal_dollar_per_kilogram",
                    "commodity_prices_cotton_seed_whole_dollar_per_kilogram",
                    "commodity_prices_corn_grain_dollar_per_kilogram",
                    "commodity_prices_corn_silage_dollar_per_kilogram",
                    "commodity_prices_distiller_grains_dried_10pct_dollar_per_kilogram",
                    "commodity_prices_distiller_grains_modified_wet_50pct_dollar_per_kilogram",
                    "commodity_prices_distiller_grains_wet_65pct_dollar_per_kilogram",
                    "commodity_prices_hay_excluding_alfalfa_dollar_per_kilogram",
                    "commodity_prices_hay_all_dollar_per_kilogram",
                    "commodity_prices_rye_grain_dollar_per_kilogram",
                    "commodity_prices_soybean_grain_dollar_per_kilogram",
                    "commodity_prices_soybean_hulls_dollar_per_kilogram",
                    "commodity_prices_soybean_meal_dollar_per_kilogram",
                    "commodity_prices_sundan_silage_dollar_per_kilogram",
                    "commodity_prices_winter_wheat_grain_dollar_per_kilogram",
                    "commodity_prices_calcium_phosphate_di_dollar_per_kilogram",
                    "commodity_prices_calf_starter_18cp_dollar_per_kilogram",
                    "commodity_prices_limestone_dollar_per_kilogram",
                ],
                "processing?": "Needs to loop "
                "over each field, "
                "each harvest, get "
                "total yield and "
                "map against the "
                "commodity prices "
                "here",
            }
        },
    },
    "Manure": {
        "Costs": {
            "Digester operational costs": {
                "biophysical_simulation": ["SEE " "NOTES"],
                "economics_files": [
                    "commodity_prices_natgas_industrial_dollar_per_megajoule",
                    "commodity_prices_elec_industrial_dollar_per_kwh",
                    "commodity_prices_digester_carbon_credits_dollar_per_tonne_CO2e",
                ],
                "notes": "Get outputs " "from methods in " "digester_costs.py",
            },
            "Digester operational costs - Diesel consumption": {
                "input_manager": ["economic_inputs.Manure.digester.diesel_liters_per_day"],
                "economics_files": ["commodity_prices_diesel_dollar_per_liter"],
                "notes": "",
            },
            "Digester operational costs - Electricity consumption": {
                "input_manager": ["economic_inputs.Manure.digester.kwh_per_day"],
                "economics_files": [
                    "commodity_prices_elec_residential_dollar_per_kwh",
                    "commodity_prices_elec_commercial_dollar_per_kwh",
                    "commodity_prices_elec_industrial_dollar_per_kwh",
                ],
                "notes": "",
            },
            "Digester operational costs - Gasoline consumption": {
                "input_manager": ["economic_inputs.Manure.digester.gasoline_liters_per_day"],
                "economics_files": ["commodity_prices_gasoline_dollar_per_liter"],
                "notes": "",
            },
            "Digester operational costs - Labor hours": {
                "input_manager": ["economic_inputs.Manure.digester.labor_hours_per_day"],
                "economics_files": ["farm_services_labor_hours_dollar_per_hour"],
                "notes": "",
            },
            "Digester operational costs - Natural gas consumption": {
                "input_manager": ["economic_inputs.Manure.digester.megajoules_per_day"],
                "economics_files": ["commodity_prices_natgas_industrial_dollar_per_megajoule"],
                "notes": "",
            },
            "Digester operational costs - Propane consumption": {
                "input_manager": ["economic_inputs.Manure.digester.propane_liters_per_day"],
                "economics_files": ["commodity_prices_propane_wholesale_dollar_per_liter"],
                "notes": "",
            },
            "Digester operational costs - Water consumption": {
                "input_manager": ["economic_inputs.Manure.digester.cubic_meters_water_per_day"],
                "economics_files": ["commodity_prices_water_municipal_dollar_per_cubic_meter"],
                "notes": "",
            },
            "General manure operational costs - Labor hours": {
                "input_manager": ["economic_inputs.Manure.general.labor_hours"],
                "economics_files": ["farm_services_labor_hours_dollar_per_hour"],
                "notes": "",
            },
            "Manure disposal quantity": {
                "input_manager": [
                    "economic_inputs.Manure.manure_disposal_kg",
                    "economic_inputs.Manure.manure_disposal_price_per_kg",
                ],
                "economics_files": [],
                "notes": "FULLY MANUAL",
            },
            "Manure disposal transport distance": {
                "input_manager": [
                    "economic_inputs.Manure.manure_disposal_transport_km",
                    "economic_inputs.Manure.manure_disposal_price_per_km",
                ],
                "economics_files": [],
                "notes": "FULLY " "MANUAL",
            },
            "Purchased manure": {
                "biophysical_simulation": [
                    "ManureManager._record_manure_request_results.off_farm_manure.total_manure_mass"
                ],
                "economics_files": ["commodity_prices_bedding_manure_solids_dollar_per_head"],
                "notes": "",
            },
            "Slurry storage operational costs - Diesel consumption": {
                "input_manager": ["economic_inputs.Manure.slurry_storage.diesel_liters_per_day"],
                "economics_files": ["commodity_prices_diesel_dollar_per_liter"],
                "notes": "",
            },
            "Slurry storage operational costs - Electricity consumption": {
                "input_manager": ["economic_inputs.Manure.slurry_storage.kwh_per_day"],
                "economics_files": [
                    "commodity_prices_elec_residential_dollar_per_kwh",
                    "commodity_prices_elec_commercial_dollar_per_kwh",
                    "commodity_prices_elec_industrial_dollar_per_kwh",
                ],
                "notes": "",
            },
            "Slurry storage operational costs - Gasoline consumption": {
                "input_manager": ["economic_inputs.Manure.slurry_storage.gasoline_liters_per_day"],
                "economics_files": ["commodity_prices_gasoline_dollar_per_liter"],
                "notes": "",
            },
            "Slurry storage operational costs - Labor hours": {
                "input_manager": ["economic_inputs.Manure.slurry_storage.labor_hours"],
                "economics_files": ["farm_services_labor_hours_dollar_per_hour"],
                "notes": "",
            },
            "Slurry storage operational costs - Natural gas consumption": {
                "input_manager": ["economic_inputs.Manure.slurry_storage.megajoules_per_day"],
                "economics_files": ["commodity_prices_natgas_industrial_dollar_per_megajoule"],
                "notes": "",
            },
            "Slurry storage operational costs - Propane consumption": {
                "input_manager": ["economic_inputs.Manure.slurry_storage.propane_liters_per_day"],
                "economics_files": ["commodity_prices_propane_wholesale_dollar_per_liter"],
                "notes": "",
            },
            "Slurry storage operational costs - Water consumption": {
                "input_manager": ["economic_inputs.Manure.slurry_storage.cubic_meters_water_per_day"],
                "economics_files": ["commodity_prices_water_municipal_dollar_per_cubic_meter"],
                "notes": "",
            },
        },
        "Revenue": {
            "Carbon credits from digester products and activities": {
                "biophysical_simulation": ["see " "future_expansion"],
                "economics_files": ["commodity_prices_carbon_credits_enteric_dollar_per_tonne_CO2e"],
                "future_expansion": "Placeholder "
                "for "
                "the "
                "future, "
                "scale "
                "to "
                "manure "
                "module "
                "outputs",
            },
            "Digester bedding co-product": {
                "biophysical_simulation": ["see " "future_expansion"],
                "economics_files": ["commodity_prices_bedding_manure_solids_dollar_per_head"],
                "future_expansion": "Placeholder "
                "for "
                "the "
                "future, "
                "scale "
                "to "
                "manure "
                "module "
                "outputs",
            },
            "Digester fertilizer production": {
                "biophysical_simulation": ["see " "future_expansion"],
                "economics_files": [
                    "commodity_prices_net_fertilizer_nitrogen_dollar_per_kilogram",
                    "commodity_prices_net_fertilizer_phosphorus_dollar_per_kilogram",
                    "commodity_prices_net_fertilizer_potassium_dollar_per_kilogram",
                ],
                "future_expansion": "Placeholder "
                "for "
                "the "
                "future, "
                "scale "
                "to "
                "manure "
                "module "
                "outputs",
            },
            "Electricity production from anaerobic digester": {
                "input_manager": ["economic_inputs.Manure.digester.kwh_per_day_produced"],
                "economics_files": ["commodity_prices_elec_industrial_dollar_per_kwh"],
                "future_expansion": "Placeholder "
                "for "
                "the "
                "future, "
                "scale "
                "to "
                "manure "
                "module "
                "outputs",
            },
            "Renewable natural gas (RNG) production": {
                "input_manager": ["economic_inputs.Manure.digester.digester_rng_produced"],
                "economics_files": ["commodity_prices_natgas_industrial_dollar_per_megajoule"],
                "future_expansion": "Placeholder "
                "for "
                "the "
                "future, "
                "scale "
                "to "
                "manure "
                "module "
                "outputs",
            },
            "Sold manure": {
                "input_manager": ["economic_inputs.Manure.manure_sales"],
                "economics_files": ["commodity_prices_bedding_manure_solids_dollar_per_head"],
                "future_expansion": "perhaps scale as "
                "a percentage of "
                "total manure "
                "produced? Or "
                "preprocessing for "
                "excess e.g. not "
                "applied to "
                "fields",
            },
        },
    },
    "Soil_and_crop": {
        "Costs": {
            "Crop labor hours": {
                "input_manager": ["economic_inputs.Soil_and_crop.labor_hours_per_day"],
                "economics_files": ["farm_services_labor_hours_dollar_per_hour"],
            },
            "Crop water consumption": {
                "biophysical_simulation": ["FieldDataReporter.send_crop_daily_variables.water_uptake.*"],
                "economics_files": ["commodity_prices_water_irrigation_dollar_per_cubic_meter"],
            },
            "Land purchase costs": {
                "input_manager": ["economic_inputs.Soil_and_crop.land_ha_purchased"],
                "economics_files": ["capital_costs_land_ha_dollar_per_hectare"],
                "notes": "This 'manual' "
                "entry in "
                "Economic_inputs "
                "fields is meant "
                "to be for an "
                "entire "
                "simulation, so "
                "is different "
                "from the "
                "'per_day' "
                "values, and "
                "instead should "
                "result only in "
                "a single value. "
                "The idea for "
                "this (and "
                "others that are "
                "similar, see "
                "variables with "
                "'whole_simulation' "
                "in them) is "
                "that it's a per "
                "scenario type "
                "value. Adding "
                "fields, giving "
                "a single cost "
                "to rent or buy "
                "manually.",
            },
            "Land rental costs": {
                "input_manager": ["economic_inputs.Soil_and_crop.land_ha_rented"],
                "economics_files": ["farm_services_land_ha_rent_dollar_per_hectare"],
            },
            "Nitrogen fertilizer used": {
                "biophysical_simulation": ["fertilizer_schedule " "SEE " "NOTES"],
                "economics_files": ["commodity_prices_net_fertilizer_nitrogen_dollar_per_kilogram"],
                "notes": "likely as "
                "'simple' "
                "as taking "
                "the sum of "
                "nitrogen_masses "
                "for each "
                "fertilizer_schedule "
                "file used "
                "in the "
                "simulation, "
                "but this "
                "requires "
                "some "
                "consulting "
                "with the "
                "soil and "
                "crop SMEs",
            },
            "Other fertilizer types used": {
                "biophysical_simulation": ["fertilizer_schedule " "SEE " "NOTES"],
                "economics_files": [
                    "commodity_prices_net_fertilizer_ammonium_nitrate_dollar_per_kilogram",
                    "commodity_prices_net_fertilizer_super_phosphate_44to46pct_dollar_per_kilogram",
                    "commodity_prices_net_fertilizer_urea_dollar_per_kilogram",
                ],
                "notes": "Placeholder " "for the " "future",
            },
            "Phosphorus fertilizer used": {
                "biophysical_simulation": ["fertilizer_schedule " "SEE " "NOTES"],
                "economics_files": ["commodity_prices_net_fertilizer_phosphorus_dollar_per_kilogram"],
                "notes": "likely "
                "as "
                "'simple' "
                "as "
                "taking "
                "the sum "
                "of "
                "phosphorus_masses "
                "for each "
                "fertilizer_schedule "
                "file "
                "used in "
                "the "
                "simulation, "
                "but this "
                "requires "
                "some "
                "consulting "
                "with the "
                "soil and "
                "crop "
                "SMEs",
            },
            "Potassium fertilizer used": {
                "biophysical_simulation": ["fertilizer_schedule " "SEE " "NOTES"],
                "economics_files": ["commodity_prices_net_fertilizer_potassium_dollar_per_kilogram"],
                "notes": "likely as "
                "'simple' "
                "as taking "
                "the sum "
                "of "
                "potassium_masses "
                "for each "
                "fertilizer_schedule "
                "file used "
                "in the "
                "simulation, "
                "but this "
                "requires "
                "some "
                "consulting "
                "with the "
                "soil and "
                "crop "
                "SMEs",
            },
            "Seeds costs": {
                "biophysical_simulation": [
                    "both " "below " "are " "from " "multiple " "input " "files, " "see " "preprocessing",
                    "field.crop_specification",
                    "field.field_size",
                ],
                "economics_files": [
                    "commodity_prices_*_dollar_per_square_meter",
                    "commodity_prices_barley_seed_dollar_per_square_meter",
                    "commodity_prices_corn_seed_dollar_per_square_meter",
                    "commodity_prices_cotton_seed_dollar_per_square_meter",
                    "commodity_prices_oat_seed_dollar_per_square_meter",
                    "commodity_prices_peanut_seed_dollar_per_square_meter",
                    "commodity_prices_rice_seed_dollar_per_square_meter",
                    "commodity_prices_sorghum_seed_dollar_per_square_meter",
                    "commodity_prices_soybean_seed_dollar_per_square_meter",
                    "commodity_prices_wheat_seed_dollar_per_square_meter",
                ],
                "preprocessing": "Map "
                "'crop_specification' "
                "in each field "
                "input file, "
                "e.g. CornSilage "
                "to corn_seed to "
                "get appropriate "
                "economics_file, "
                "ALSO convert "
                "the field_size "
                "from Ha to "
                "square meters "
                "(divide by "
                "10000). However "
                "- note this one "
                "isn't reported "
                "daily! So "
                "easiest way to "
                "handle this "
                "could be to "
                "divide the "
                "price for each "
                "field evenly "
                "across each day "
                "of the "
                "simulation. "
                "e.g. if the "
                "cost for "
                "corn_seed for a "
                "field_size of "
                "100 was 365, "
                "and the "
                "simulation was "
                "two years, the "
                "preprocessing "
                "would take all "
                "that and "
                "compute a price "
                "of 0.5 for each "
                "day in the "
                "simulation "
                "(e.g. a list "
                "consisting of "
                "0.5 repeated "
                "for each day of "
                "the sim).",
            },
            "Tractor hours for crops": {
                "biophysical_simulation": [
                    "Waiting " "on " "tractor_implement " "and " "other " "parts " "of " "EEE " "outputs"
                ],
                "economics_files": [
                    "farm_services_tractor_small_dollar_per_hour",
                    "farm_services_tractor_medium_dollar_per_hour",
                    "farm_services_tractor_large_dollar_per_hour",
                ],
            },
        },
        "Revenue": {
            "Carbon credits from soil conservation practice": {
                "input_manager": ["economic_inputs.Soil_and_crop.carbon_credits_whole_simulation_tonnes"],
                "economics_files": ["commodity_prices_carbon_credits_soil_dollar_per_tonne_CO2e"],
                "future_expansion": "scale " "this " "to " "crop " "outputs/scenarios",
            }
        },
    },
}
