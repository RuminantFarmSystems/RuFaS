"""
Notes
--------
mlk suffix means milking center and holding pen
fr suffix means freestall/tiestall
ts prefix means total_solids
vs prefix means volatle_solids
n -> nitrogen
p-> phosphorus
k-> potassium
rfw-> recycled flush water
mcf-> methane conversion factor
ms -> manure handled in system
sls -> solid liquid separator
strg_p -> Storage Pond
hrt-> hydraulic retention time
vsdf-> volatile solids destroyed
mcf-> methane conversion factor
ms-> manure handled in system
anae_lag-> anaerobic lagoon
anae_dig-> anaerobic digestion



$Constants
-------------

TOTAL_HOURS_IN_A_DAY = 24
MINS_IN_AN_HOUR = 60
CENT = 100
M3_IN_LTRS = 1000
DAYS_IN_A_YEAR = 365 or 366
KG_TO_G = 1000
#Considering separating constants for both types of pens

#Excreta and related constants
animal A manure = ANIMAL_A_MANURE   # kg/[(head)(day)]
animal B manure = ANIMAL_B_MAURE    # kg/[(head)(day)]
animal C manure = ANIMAL_C_MAURE    # kg/[(head)(day)]

animal A solids = ANIMAL_A_SOLID    # kg/[(head)(day)]
animal B solids = ANIMAL_B_SOLID    # kg/[(head)(day)]
animal C solids = ANIMAL_C_SOLID    # kg/[(head)(day)]

animal A volatile = ANIMAL_A_VOLATILE    # kg/[(head)(day)]
animal B volatile = ANIMAL_B_VOLATILE    # kg/[(head)(day)]
animal C volatile = ANIMAL_C_VOLATILE    # kg/[(head)(day)]

animal A TAN = ANIMAL_A_TAN      # kg/[(head)(day)]
animal B TAN = ANIMAL_B_TAN      # kg/[(head)(day)]
animal C TAN = ANIMAL_C_TAN      # kg/[(head)(day)]

animal A N = ANIMAL_A_N     # kg/[(head)(day)]
animal B N = ANIMAL_B_N     # kg/[(head)(day)]
animal C N = ANIMAL_C_N     # kg/[(head)(day)]

animal A P2O5 = ANIMAL_A_P2O5     # kg/[(head)(day)]
animal B P2O5 = ANIMAL_B_P2O5     # kg/[(head)(day)]
animal C P2O5 = ANIMAL_C_P2O5     # kg/[(head)(day)]

animal A K2O = ANIMAL_A_K2O     # kg/[(head)(day)]
animal B K2O = ANIMAL_B_K2O     # kg/[(head)(day)]
animal C K2O = ANIMAL_C_K2O     # kg/[(head)(day)]

manure_density = MANURE_DENSITY     # kg/m3

Cleaning Constants
Milking and Holding
flushing_water_volume_mlk = 50    #ltrs/day
scraping_water_volume_mlk = 10    #ltrs/day

FreeStall
flushing_water_volume_fr = 830    #ltrs/day
scraping_water_volume_fr = 10    #ltrs/day



Bedding
LCOB = 1.97 kg/animal/day
LCOB_density = 250 kg/m3

LCSB = 22.23 kg/animal/day
LCSB_density = 1500 kg/m2


BO = 0.24                         #m3 CH4/ kg VS    may vary form 0.1-0.24, 

Equations
------------

PEN 1

Milking Center & Holding Pen
\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

Animal Type A = num_type_A      # in head per day
Animal Type B = num_type_B
Animal Type C = num_type_C

Types = [A, B, C]

total_animals = num_type_A + num_type_B + num_type_C                                          #animals
raw_manure = Sum( num_type_[type] *  ANIMAL_[type]_MANURE for type in Types )                 #kg/day
total_solids_excreted = Sum( num_type_[type] *  ANIMAL_[type]_SOLID for type in Types )       #kg/day
volatile_solids_excreted = Sum( num_type_[type] *  ANIMAL_[type]_VOLATILE for type in Types )          #kg/day
n_as_excreted = Sum( num_type_[type] *  ANIMAL_[type]_N for type in Types )               #kg/day
tan_as_excreted = Sum( num_type_[type] *  ANIMAL_[type]_TN for type in Types )                 #kg/day
p2o5_as_excreted = Sum( num_type_[type] *  ANIMAL_[type]_P2O5 for type in Types )             #kg/day
k2O_as_excreted = Sum( num_type_[type] *  ANIMAL_[type]_K2O for type in Types )               #kg/day
density = MILKING_CENTER_AND_HOLDING_PEN_DENSITY                                              #kg/m3

average_time_spent_milking = 60                                                               #some input between [60..90] mins/day
number_of_milkings_day = 2                                                                    #some int [2..4]  /day

cleaning_method = CLEANING_METHOD                                                             #Always Flushing
fresh_water = [cleaning_method]_water_volume_mlk * total_animals                              #ltrs/day


time_of_cleaning = ERROR: EQUATION DOES NOT SEEM RIGHT                                        #times/day

time_spent_per_day_mlk = (average_time_spent_milking * number_of_milkings)/MINS_IN_AN_HOUR        #hours/day
percent_time_spent_per_day_mlk = time_spent_per_day * CENT/ HOURS_IN_A_DAY                        # in %

MANURE GENREATED
total_waste_volume_received_mlk = (raw_manure/manure_density)*(percent_time_spent_per_day/CENT) + (fresh_water/M3_IN_LTRS)     #m3/day
total_solids_mlk = total_solids_excreted * (percent_time_spent_per_day/CENT)                                                   #kg/day
volatile_solids_mlk = volatile_solids_excreted * (percent_time_spent_per_day/CENT)                                             #kg/day
nitrogen_mlk = n_as_excreted * (percent_time_spent_per_day/CENT)                                                               #kg/day
tan_mlk = tan_as_excreted * (percent_time_spent_per_day/CENT)                                                                  #kg/day
p2o5_mlk = p2o5_as_excreted * (percent_time_spent_per_day/CENT)                                                                #kg/day
k2o_mlk = k2o_as_excreted * (percent_time_spent_per_day/CENT)                                                                  #kg/day




FreeStall / TieStall
\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

Animal Type A = num_type_A      # in head per day
Animal Type B = num_type_B
Animal Type C = num_type_C

Types = [A, B, C]

total_animals = num_type_A + num_type_B + num_type_C
raw_manure = Sum( num_type_[type] *  ANIMAL_[type]_MANURE for type in Types )
total_solids_excreted = Sum( num_type_[type] *  ANIMAL_[type]_SOLID for type in Types )
volatile_solids_fr = Sum( num_type_[type] *  ANIMAL_[type]_VOLATILE for type in Types )
tan_as_excreted_fr = Sum( num_type_[type] *  ANIMAL_[type]_TN for type in Types )
n_as_excreted_fr = Sum( num_type_[type] *  ANIMAL_[type]_N for type in Types )
p2o5_as_excreted_fr = Sum( num_type_[type] *  ANIMAL_[type]_P2O5 for type in Types )
k2O_as_excreted_fr = Sum( num_type_[type] *  ANIMAL_[type]_K2O for type in Types )
density = MILKING_CENTER_AND_HOLDING_PEN_DENSITY

Bedding
bedding_type = [SAND/ ORGANIC]
bedding_mass_per_day = LC[SB or OB] * total_animals            # kg/day
volume_per_day = mass_per_day / LC[SB or OB]_density   # m3/day

Cleaning
cleaning_method = [flushing/scraping]
flush_water = [cleaning_method]_water_volume_fr * total_animals  #ltrs/day

Sand Separation Lane/Mechanical Separators [IFF Sand Bedding]
sand_washed_with_water_or_scraped = bedding_mass_per_day   #kg/day
sand_separation_efficiency = [60 to 90]%          #some input
sand_mass_separated = sand_separation_efficiency * sand_washed_with_water  #kg/day
sand_volume_sepatated = sand_mass_separated / LC[SB or OB]_density    #m3/day

time_spent_per_day_fr = HOURS_IN_A_DAY - time_spent_per_day_lc   #hrs
percent_time_spent_per_day_fr = CENT - percent_time_spent_per_day_lc       # some percentage


MANURE GENERATED
total_waste_volume_fr = ((raw_manure/manure_densiy)*percent_time_spent_per_day/CENT) + (flush_water/1000) + total_waste_volume_received_mlk + sand_volume_separated  #m3/day
ts_manure_bedding_rfw_percent = [1-2] % #some input
ts_manure_bedding_rfw = (total_solids_excreted * percent_time_spent_per_day/CENT) + total_solids_mlk + ts_rfw_contribution      #kg/day
ts_g_per_L = total_solids_manure_bedding_rfw / total_waste_volume         #g/L
vs_manure_bedding_rfw = (volatile_solids_fr * percent_time_spent_per_day/CENT) + volatile_solids_mlk + vs_rfw     #kg/day
vs_manure_bedding_rfw_g_per_l = vs_manure_bedding_rfw / total_waste_volume    #g/L
n_manure_bedding_rfw = (n_as_excreted_fr * percent_time_spent_per_day/CENT) + nitrogen_mlk + n_rfw     #kg/day
n_manure_bedding_rfw_g_per_l = n_manure_bedding_rfw / total_waste_volume    #g/L 
tan_manure_bedding_rfw = (tan_as_excreted_fr * percent_time_spent_per_day/CENT) + tan_mlk + tan_rfw     #kg/day
tan_manure_bedding_rfw_g_per_L =  tan_manure_bedding_rfw / total_waste_volume    #g/L
p_manure_bedding_rfw = (p2o5_as_excreted_fr * percent_time_spent_per_day/CENT) + p2o5_mlk + p2o5_rfw     #kg/day
p_manure_bedding_rfw_g_per_L =  p_manure_bedding_rfw / total_waste_volume    #g/L
k_manure_bedding_rfw = (k2o_as_excreted_fr * percent_time_spent_per_day/CENT) + k2o_mlk + k2o_rfw     #kg/day
k_manure_bedding_rfw_g_per_L =  k_manure_bedding_rfw / total_waste_volume    #g/L
___________________________________________________
## why these?## contribution from bedding
ts_of_bedding = 0     #kg/day
vs_of_bedding = 0     #kg/day
n_bedding = 0         #kg/day
tan_bedding = 0       #kg/day
p2o5_bedding = 0      #kg/day
k2o_bedding = 0       #kg/day
----------------------------------------------------
IFF flushing method
rfw = flush_water                                       #ltrs/day
ts_rfw_g_per_L = 1                                      #g/L, Some input 0.05-1.5
ts_rfw = (rfw * ts_rfw_g_per_L)/1000                    #kg/day
vs_rfw_g_per_L = 0.85                                   #g/L, Some input 
vs_rfw = (rfw * vs_rfw_g_per_L)/1000                    #kg/day
n_rfw_g_per_L = 0.12                                    #g/L, Some input 0.12-0.6
n_rfw = (rfw * n_rfw_g_per_L)/1000                      #kg/day
tan_rfw_g_per_L = 0.12                                  #g/L, Some input 0.12-0.6
tan_rfw = (rfw * tan_rfw_g_per_L)/1000                  #kg/day
p2o5_rfw_g_per_L = 0.04                                 #g/L, Some input 0.04-0.148
p2o5_rfw = (rfw * p2o5_rfw_g_per_L)/1000                #kg/day
k2o_rfw_g_per_L = 0.285                                 #g/L, Some input 0.285-0.717
k2o_rfw = (rfw * k2o_rfw_g_per_L)/1000                  #kg/day






ANAEROBIC LAGOON

Input for anaerobic lagoon could come from main barn/cleaning or any other pre-treatment methods. Equations here so far just reflects the main barn equations. Need to add the dynamism when coding up in python. We could do some processingof the input before passing it to the anaerobic lagoon.



Side Calculations
vs_per_day = 




FACULTATIVE LAGOON
\\\\\\\\\\\\\\\\\\\\\\\\\\\\

waste_water_volume_lag = total_waste_volume_fr                                                                        #m3/day, Day1 (why this)
flushing_recycled = flush_water / M3_IN_LTRS                                                                      #m3/day
reduced_volume = waste_water_volume_lag - flushing_recycled                                                           #m3/day, Day2-Day180 (why this)
ts_lag = ts_manure_bedding_rfw                                                                                    #kg/day
ts_lag_g_per_L = ts_lag / waste_water_volume_lag                                                                      #g/L
vs_loading_lag = vs_manure_bedding_rfw                                                                            #kg/day
vs_loading_lag_g_per_L = vs_lag / waste_water_volume_lag                                                              #g/L
hydraulic_retention_time = 180                                                                                    #days, some inpuut 90-180
volumetric_loading_rate = vs_loading_lag / (waste_water_volume_lag * hydraulic_retention_time)                        #kg/m3/day   (some unused info)
minimum_treatment_volume = waste_water_volume_lag + (reduced_volume * hydraulic_retention_time)                       #m3
sludge_per_ts = 0.00251                                                                                           #m3/kg, (some input 0.00274-0.00455)
sludge_accumulation_period = 5                                                                                    #years, some input 5-20
sludge_accumulation_volume = ts_lag * sludge_per_ts * sludge_accumulation_period * DAYS_IN_YEAR                   #m3/5years  #!not okay with unit
storm_event_m3 = 1366                                                                                             #m3, some input
storm_event_inch = 6.3                                                                                            #inches, some input
free_board_m3 = 1366                                                                                              #m3, some input
free_board_foot = 6.3                                                                                             #foot, some input
total_lagoon_volume = minimum_treatment_volume + sludge_accumulation_volume                                       #m3  !!! storm_event_m3 +cfree_board_m3 eliminated?

--------------------------------------------------------------------------------------------------------------
Side Calculations
------------------
CH4 - CO2
vs_per_day = vs_loading_lag/total_animals
vs_per_year = vs_per_day * DAYS_IN_A_YEAR
vs_destroyed = 0.57                                                                   # kg VS/animal/day
bo = BO                                                                               #Constant for now                                                  
mcf = 0.79                                                                            #Some input? fraction.
ms = 0.90
factor_m3_CH4_to_kg_per_m3 = 0.66                                                     #kg/m3
methane_collection_efficiency= 0.00                                                   # fraction
methane_emission_daily = vs_per_day * bo * mcf * ms * factor_m3_CH4_to_kg_per_m3      #kg/animal/day
CH4_to_CO2 = 30                                                                       #CO2/CH4
co2_equivalent_daily = methane_emission_daily * CH4_to_CO2                            #kg/animal/day
methane_emission_yearly = vs_per_year * bo * mcf * ms * factor_m3_CH4_to_kg_per_m3    #kg/animal/year
co2_equivalent_daily = methane_emission_yearly * CH4_to_CO2                           #kg/animal/year

--------- 
n_excretion_rate_daily_direct = n_manure_bedding_rfw / total_animals                                                        #kg N/animal/day
n_excretion_rate_yearly = n_excretion_rate_daily * DAYS_IN_A_YEAR                                                           #kg N/animal/day
kg_n20n_to_kg_co2 = 44/28 = 1.57                                                                                            #kg co2/kg n2o/animal/day
n2o_to_co2 = 310                                                                                                            #kg co2/kg n2o

Direct
fraction_mms = [0.70 .. 1.00]                                                                                               #some fraction % , input
emission_factor_n20_direct = 0.002                                                                                          #kg N2O-N/kg N, some fraction input
direct_nitrus_oxide_daily = n_excretion_rate_daily * fraction_mms * emission_factor_n20_direct * kg_n20n_to_kg_co2          #kg n2o/animal/day
co2_from_n2o_daily = direct_nitrus_oxide_daily * n2o_to_co2                                                                 #kg co2/animal/day 
direct_nitrus_oxide_yearly = n_excretion_rate_yearly * fraction_mms * emission_factor_n20_direct * kg_n20n_to_kg_co2        #kg n2o/animal/year
co2_from_n2o_yearly = direct_nitrus_oxide_yearly * n2o_to_co2                                                               #kg co2/animal/year  

Indirect
fraction_n_to_nh3_nox = 0.25                                                                                                            #some fraction % , input
emission_factor_n20_indirect = 0.01                                                                                                     #kg N2O-N/kg N, some fraction input
indirect_nitrus_oxide_daily = n_excretion_rate_daily * fraction_n_to_nh3_nox * emission_factor_n20_indirect * kg_n20n_to_kg_co2         #kg n2o/animal/day
co2_from_n2o_daily =  indirect_nitrus_oxide_daily * n2o_to_co2                                                                          #kg co2/animal/day 
direct_nitrus_oxide_yearly = n_excretion_rate_yearly * fraction_n_to_nh3_nox * emission_factor_n20_indirect * kg_n20n_to_kg_co2         #kg n2o/animal/year
co2_from_n2o_yearly = indirect_nitrus_oxide_yearly * n2o_to_co2                                                                         #kg co2/animal/year  


FACULTATIVE LAGOON EFFLUENT CHARACTERISTICS
waste_water_volume_eff = minimum_treatment_volume                                                                            #m3
waste_water_volume_days_eff = hydrualic_retention_time                                                                       #days
ts_eff_rate = [0.75 .. 0.85]                                                                                                 #some input, 75-85%
ts_eff = ts_lag_g_per_l - (ts_lag / waste_water_volume_lag) * ts_eff_rate                                                    #g/L
vs_loading_eff_rate = [0.8 .. 0.9]                                                                                           #some input, 80-90%
vs_loading_eff = vs_loading_lag_g_per_l - (vs_loading_lag / waste_water_volume_lag) * vs_loading_eff_rate                    #g/L
n_eff_rate = [0.6 .. 0.8]                                                                                                    #some input, 60-80%
n_eff = n_manure_bedding_rfw_g_per_l - (n_manure_bedding_rfw / waste_water_volume_lag) * n_eff_rate                          #g/L
tan_eff_rate = [0.6 .. 0.8]                                                                                                  #some input, 60-80%
tan_eff = tan_manure_bedding_rfw_g_per_l - (tan_manure_bedding_rfw / waste_water_volume_lag) * tan_eff_rate                  #g/L
p_eff_rate = [0.6 .. 0.8]                                                                                                    #some input, 60-80%
p_eff = p_manure_bedding_rfw_g_per_l - (p_manure_bedding_rfw / waste_water_volume_lag) * p_eff_rate                          #g/L
k_eff_rate = [0.2 .. 0.3]                                                                                                    #some input, 20-30%
k_eff = k_manure_bedding_rfw_g_per_l - (k_manure_bedding_rfw / waste_water_volume_lag) * k_eff_rate                          #g/L

FACULTATIVE LAGOON SLUDGE NUTRIENT VALUE
sludge_volume_years = sludge_accumulation_period                             #years, some input , some values not used, just a reminder...
sludge_volume = sludge_accumulation_volume                                   #m3
ts_lag_vaue_g_per_l = 40..70                                                 #g/L, some input [40 .. 70]
ts_lag_val = ts_lag_vaue_g_per_l * sludge_volume                             #kg
n_lag_vaue_g_per_l = 1.99 .. 2.99                                            #g/L, some input [1.99 .. 2.99]
n_lag_val = n_lag_vaue_g_per_l * sludge_volume                               #kg 
p_lag_vaue_g_per_l = 1.07 .. 5.02                                            #g/L, some input [1.07 .. 5.02]
p_lag_val = p_lag_vaue_g_per_l * sludge_volume                               #kg 
k_lag_vaue_g_per_l = 1.10 .. 1.75                                            #g/L, some input [1.10 .. 1.75]
k_lag_val = k_lag_vaue_g_per_l * sludge_volume                               #kg 






SOLID LIQUID SEPARATOR
\\\\\\\\\\\\\\\\\\\\\\\\\\\\

ROTATION SCREEN (DT360 MANURE SEPARATOR)

Digestor Effluent
rotating_screen_and_roller_press = 0.75 mm                                                #some input/ constant
total_volume_sls = total_waste_volume_received_fr * M3_IN_LTRS                            #ltrs/day
ts_sls = ts_manure_bedding_rfw                                                            #kg/day,   from fr
ts_sls_g_per_l = ts_sls * G_TO_KG / total_volume_sls                                      #g/ltrs
vs_sls = vs_manure_bedding_rfw                                                            #kg/day
vs_sls_g_per_l = vs_sls * G_TO_KG / total_volume_sls                                      #g/ltrs
n_sls = n_manure_bedding_rfw                                                              #kg/day
n_sls_g_per_l = n_sls * G_TO_KG / total_volume_sls                                        #g/ltrs  
tan_sls = tan_manure_bedding_rfw                                                          #kg/day
tan_sls_g_per_l = tan_sls * G_TO_KG / total_volume_sls                                    #g/ltrs  
p_sls = p_manure_bedding_rfw                                                              #kg/day
p_sls_g_per_l = p_sls * G_TO_KG / total_volume_sls                                        #g/ltrs  
k_sls = k_manure_bedding_rfw                                                              #kg/day
k_sls_g_per_l = k_sls * G_TO_KG / total_volume_sls                                        #g/ltrs  


Removal Efficiency
flow_rate = total_volume_sls                                                              #ltrs/day
ts_efficiency = [0.20-0.40]                                                               #Some input, %
ts_removed_sls = ts_sls * ts_efficiency                                                   #kg/day
ts_removed_sls_g_per_l = ts_sls_g_per_l * ts_efficiency                                   #g/ltrs
vs_efficiency = 0.85                                                                      #Some input, %
vs_removed_sls = vs_sls * vs_efficiency                                                   #kg/day
vs_removed_sls_g_per_l = vs_sls_g_per_l * vs_efficiency                                   #g/ltrs
n_efficiency = [0.10-0.50]                                                                #Some input, %
n_removed_sls = n_sls * n_efficiency                                                      #kg/day
p_efficiency = [0.10-0.50]                                                                #Some input, %
p_removed_sls = p_sls * p_efficiency                                                      #kg/day
k_efficiency = [0.10-0.50]                                                                #Some input, %
k_removed_sls = k_sls * k_efficiency                                                      #kg/day

Effluent Solid
dry_solid = ts_removed_sls                                                                #kg/day
vs_effluent_s = vs_removed_sls                                                            #kg/day
n_effluent_s = n_removed_sls                                                              #kg/day
p_effluent_s = p_removed_sls                                                              #kg/day
k_effluent_s = k_removed_sls                                                              #kg/day
total_wet_weight_mass_fraction = [0.25-0.32]                                              #some faction
total_wet_weight_mass = dry_solid / total_wet_weight_mass_fraction                        #kg/day

Effluent Liquid - Storage Pond, Significance? 
volume_factor = 0.7                                                                       #Some fractional input
volume_eff_liq_ltrs = flow_rate - total_mass_wet_weight                                   #ltrs/day  
volume_eff_liq_m3 = volume_eff_liq_ltrs / M3_IN_LTRS                                      #m3/day
ts_effluent_liq = ts_sls - ts_removed_sls                                                 #kg/day
ts_effluent_liq_g_per_l = ts_sls_g_per_l - ts_removed_sls_g_per_l                         #g/l
vs_effluent_liq = vs_sls - vs_removed_sls                                                 #kg/day
vs_effluent_liq_g_per_l = vs_sls_g_per_l - vs_removed_sls_g_per_l                         #g/l
n_effluent_liq = n_sls - n_removed_sls                                                    #kg/day
n_effluent_liq_g_per_l = n_effluent_liq * KG_TO_G/volume_eff_liq_ltrs                     #g/l
p_effluent_liq = p_sls - p_removed_sls                                                    #kg/day
p_effluent_liq_g_per_l = p_effluent_liq * KG_TO_G/volume_eff_liq_ltrs                     #g/l
k_effluent_liq = n_sls - k_removed_sls                                                    #kg/day
k_effluent_liq_g_per_l = k_effluent_liq * KG_TO_G/volume_eff_liq_ltrs                     #g/l





Storage Pond
--------------
Input for storage pond could come from main barn/cleaning or any other pre-treatment methods. Equations here so far just reflects the main barn equations. Need to add the dynamism when coding up in python. We could do some processingof the input before passing it to the storage pond.
Storage Pond (Attributes)
waste_water_volume_strg_p = total_waste_volume_fr                                                                       #m3/day
flushing_recycled_strg_p = flush_water / M3_IN_LITRES                                                                   #m3/day
reduced_volume_strg_p = waste_water_volume_strg_p - flushing_recycled_strg_p                                            #m3/day
ts_strg_p = ts_manure_bedding_rfw                                                                                       #kg/day
ts_strg_p_g_per_l = ts_strg_p / waste_water_volume_strg_p                                                               #g/L
vs_loading_strg_p = vs_manure_bedding_rfw                                                                               #kg/day
vs_strg_p_g_per_l = vs_strg_p / waste_water_volume_strg_p                                                               #g/L
hrt_strg_p = [90..180]                                                                                                  #days, some input
manure_and_waste_water_volume_strg_p = waste_water_volume_strg_p + (reduced_volume_strg_p * hrt_strg_p)                 #m3
total_pond_volume = manure_and_waste_water_volume_strg_p                                                                #m3

Gas Emission Calculations
CH4
vs_strg_p_per_animal_day = vs_loading_strg_p / total_animals                                                            #kg/animal/day
vs_strg_p_per_animal_day = vs_strg_p_per_animal_day * DAYS_IN_A_YEAR                                                    #kg/animal/year
vsdf = None                                                                                                             #dummy for now
bo = 0.24                                                                                                               #m3 CH4 / kg VS, some input/constant      
mcf = 0.79                                                                                                              #some percentage
ms = 0.90                                                                                                               #some percentage
m3_CH4_to_kg_per_m3 = 0.67                                                                                              #kg/m3 , some input/constant
methane_collection_efficiency = 0.0                                                                                     #some percentage, input/constant  Dummy for now.
methane_emmision_daily = vs_strg_p_per_animal_day * bo * mcf * ms *  m3_CH4_to_kg_per_m3                                #kg/animal/day
co2_from_methane_daily = methane_emmision_daily * CH4_to_CO2                                                            #kg/animal/day
methane_emmision_yearly = vs_strg_p_per_animal_year * bo * mcf * ms *  m3_CH4_to_kg_per_m3                              #kg/animal/year
co2_from_methane_yearly = methane_emmision_yearly * CH4_to_CO2                                                          #kg/animal/year
---N---
n_excretion_rate_daily_direct = n_manure_bedding_rfw / total_animals                                                        #kg N/animal/day       
n_excretion_rate_yearly = n_excretion_rate_daily * DAYS_IN_A_YEAR                                                           #kg N/animal/day        
kg_n20n_to_kg_co2 = 44/28 = 1.57                                                                                            #kg co2/kg n2o/animal/day
n2o_to_co2 = 310                                                                                                            #kg co2/kg n2o
---N Direct---
fraction_mms = [0.70 .. 1.00]                                                                                               #some fraction % , input
emission_factor_n20_direct = 0.002                                                                                          #kg N2O-N/kg N, some fraction input
direct_nitrus_oxide_daily = n_excretion_rate_daily * fraction_mms * emission_factor_n20_direct * kg_n20n_to_kg_co2          #kg n2o/animal/day
co2_from_dir_n2o_daily = direct_nitrus_oxide_daily * n2o_to_co2                                                             #kg co2/animal/day 
direct_nitrus_oxide_yearly = n_excretion_rate_yearly * fraction_mms * emission_factor_n20_direct * kg_n20n_to_kg_co2        #kg n2o/animal/year
co2_from_dir_n2o_yearly = direct_nitrus_oxide_yearly * n2o_to_co2                                                           #kg co2/animal/year  
---N Indirect---
fraction_n_to_nh3_nox = 0.25                                                                                                            #some fraction % , input
emission_factor_n20_indirect = 0.01                                                                                                     #kg N2O-N/kg N, some fraction input
indirect_nitrus_oxide_daily = n_excretion_rate_daily * fraction_n_to_nh3_nox * emission_factor_n20_indirect * kg_n20n_to_kg_co2         #kg n2o/animal/day
co2_from_indir_n2o_daily =  indirect_nitrus_oxide_daily * n2o_to_co2                                                                    #kg co2/animal/day 
direct_nitrus_oxide_yearly = n_excretion_rate_yearly * fraction_n_to_nh3_nox * emission_factor_n20_indirect * kg_n20n_to_kg_co2         #kg n2o/animal/year
co2_from_indir_n2o_yearly = indirect_nitrus_oxide_yearly * n2o_to_co2                                                                   #kg n2o/animal/year

Storage Pond (Gas Attributes)
methane_emission_strg_p = methane_emmision_daily                                                                      #kg/animal/day
co2_equivalent_of_methane_strg_p = co2_from_methane_daily                                                             #kg/animal/day
direct_nitrous_oxide_strg_p = direct_nitrus_oxide_daily                                                               #kg NO2/animal/day
co2_from_dir_n2o_strg_p = co2_from_dir_n2o_daily                                                                      #kg CO2/animal/day
indirect_nitrous_oxide_strg_p = direct_nitrus_oxide_daily                                                             #kg NO2/animal/day
co2_from_indir_n2o_strg_p = co2_from_indir_n2o_daily                                                                  #kg CO2/animal/day

Pond Effluent Characteristics
waste_water_volume_strg_p_eff = waste_water_volume_strg_p                                                             #m3/day
ts_strg_p_eff_ratio = [0.10..0.30]                                                                                    #some input percentage
ts_strg_p_eff = ts_strg_p_g_per_l - (ts_strg_p / waste_water_volume_strg_p) * ts_strg_p_eff_ratio                     #g/L
vs_loading_strg_p_eff_ratio = 0.85                                                                                    #some constant/input percentage
vs_loading_strg_p_eff = vs_loading_strg_p_eff_ratio * ts_strg_p_eff                                                   #g/L
n_strg_p_eff_ratio = [0.10..0.30]                                                                                                       #some input percentage
n_strg_p_eff = n_manure_bedding_rfw_g_per_L - ((n_manure_bedding_rfw / waste_water_volume_strg_p) * n_strg_p_eff_ratio)                 #g/L
tan_strg_p_eff_ratio = [0.10..0.30]                                                                                                     #some input percentage
tan_strg_p_eff = tan_manure_bedding_rfw_g_per_L - ((tan_manure_bedding_rfw / waste_water_volume_strg_p) * tan_strg_p_eff_ratio)         #g/L
p_strg_p_eff_ratio = [0.10..0.30]                                                                                                       #some input percentage
p_strg_p_eff = p_manure_bedding_rfw_g_per_L - ((p_manure_bedding_rfw / waste_water_volume_strg_p) * p_strg_p_eff_ratio)                 #g/L
k_strg_p_eff_ratio = [0.10..0.30]                                                                                                       #some input percentage
k_strg_p_eff = k_manure_bedding_rfw_g_per_L - ((k_manure_bedding_rfw / waste_water_volume_strg_p) * k_strg_p_eff_ratio)                 #g/L


Anaerobic Digestion
--------------------

Anaerobic Digestion-Complete Stirred Tank Reactor

waste_water_volume_anae_dig = total_waste_volume_fr                                                                                                                               #m3/day
ts_anae_dig = ts_manure_bedding_rfw                                                                                                                                               #kg/day 
ts_anae_dig_g_per_l = ts_anae_dig / waste_water_volume_anae_dig                                                                                                                   #g/L
vs_loading_anae_dig = vs_manure_bedding_rfw                                                                                                                                       #kg/day
vs_anae_dig_g_per_l = vs_anae_dig / waste_water_volume_anae_dig                                                                                                                   #g/L
sludge_accumulation_rate_anae_dig = [0.02..0.4]                                                                                                                                   #some input percentage between 0.02 and 0.04 (i.e 2% and 4%)
sludge_accumulation_period_anae_dig = [1..5]                                                                                                                                      #years, Some input between 1 and 5 years
sludge_accumulation_volume_anae_dig = vs_loading_anae_dig * sludge_accumulation_rate_anae_dig * sludge_accumulation_period_anae_dig * DAYS_IN_A_YEAR/ M3_IN_LTRS                  #m3
hrt_anae_dig = [20..30]                                                                                                                                                           #days,  some input between 20 and 30 days
minimum_volume_treatment_anae_dig = waste_water_volume_anae_dig * hrt_anae_dig                                                                                                    #m3
top_cover_volume_anae_dig_percent (gas storage) = [0.1..0.3]                                                                                                                      #some percentage between 10% and 30%
top_cover_volume_anae_dig (gas strorage) = top_cover_volume_anae_dig_percent * minimum_volume_treatment_anae_dig                                                                  #m3
digester_volume_anae_dig = minimum_volume_treatment_anae_dig + sludge_accumulation_volume_anae_dig + top_cover_volume_anae_dig                                                    #m3
vs_loading_rate_anae_dig = vs_loading_anae_dig / digester_volume_anae_dig                                                                                                         #kg/m3/day
biogas_generation_percent_anae_dig = [0.15..0.38]                                                                                                                                 #m3/kg of VS Some input between 0.15 and 0.38 m3/kg of VS
biogas_generated_anae_dig = vs_loading_anae_dig * biogas_generation_percent_anae_dig                                                                                              #m3/day 
methane_generation_percent_anae_dig = [0.5..0.65]                                                                                                                                 #Some percentage input between 50% and 65% 
methane_generated_anae_dig = methane_generation_percent_anae_dig * biogas_generated_anae_dig                                                                                      #m3/day 


Digestor Effluent Characteristics
waste_water_volume_eff_anae_dig = waste_water_volume_anae_dig                                                                                                                     #m3/day
waste_water_volume_evaporation_anae_dig = [0.02..0.05]                                                                                                                            #some input between 2% and 5%
ts_eff_loss_percent_anae_dig = [0.40..0.60]                                                                                                                                       #some input 40% and 60%
ts_eff_anae_dig = ts_anae_dig_g_per_l - (ts_anae_dig_g_per_l * ts_eff_percent_anae_dig)                                                                                           #g/L
vs_loading_eff_loss_percent_anae_dig = [0.30..0.40]                                                                                                                               #some input 30% and 40%
vs_loading_eff_anae_dig = vs_loading_anae_dig_g_per_l - (vs_loading_anae_dig_g_per_l * vs_loading_eff_percent_anae_dig)                                                           #g/L
n_eff_loss_percent_anae_dig = [0.00..0.05]                                                                                                                                        #percent, some input between 0 and 5%
n_eff_anae_dig = n_manure_bedding_rfw_g_per_l - (n_manure_bedding_rfw_g_per_l * n_eff_loss_percent_anae_dig)                                                                      #g/L
p_eff_loss_percent_anae_dig = [0.00..0.05]                                                                                                                                        #percent, some input between 0 and 5%
p_eff_anae_dig = p_manure_bedding_rfw_g_per_l - (p_manure_bedding_rfw_g_per_l * p_eff_loss_percent_anae_dig)                                                                      #g/L
k_eff_loss_percent_anae_dig = [0.00..0.05]                                                                                                                                        #percent, some input between 0 and 5%
k_eff_anae_dig = k_manure_bedding_rfw_g_per_l - (k_manure_bedding_rfw_g_per_l * k_eff_loss_percent_anae_dig)                                                                      #g/L
"""