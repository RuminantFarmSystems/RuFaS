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



$Constants
-------------

TOTAL_HOURS_IN_A_DAY = 24
MINS_IN_AN_HOUR = 60
CENT = 100
LTRS_IN_M3 = 1000
DAYS_IN_A_YEAR = 365 or 366
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
flush_water_rfw = 

time_of_cleaning = ERROR: EQUATION DOES NOT SEEM RIGHT                                        #times/day

time_spent_per_day_mlk = (average_time_spent_milking * number_of_milkings)/MINS_IN_AN_HOUR        #hours/day
percent_time_spent_per_day_mlk = time_spent_per_day * CENT/ HOURS_IN_A_DAY                        # in %

MANURE GENREATED
total_waste_volume_received_mlk = (raw_manure/manure_density)*(percent_time_spent_per_day/CENT) + (fresh_water/LTRS_IN_M3)     #m3/day
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
****Some numbers not understood, ask Varma****
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

Side Calculations
vs_per_day = 




FACULTATIVE LAGOON
\\\\\\\\\\\\\\\\\\\\\\\\\\\\

waste_water_volume_lag = total_waste_volume_fr                                                                        #m3/day, Day1 (why this)
flushing_recycled = flush_water / LTRS_IN_M3                                                                      #m3/day
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
Direct
n_excretion_rate_daily = n_manure_bedding_rfw / total_animals                                                               #kg N/animal/day
n_excretion_rate_yearly = n_excretion_rate_daily * DAYS_IN_A_YEAR                                                           #kg N/animal/day
fraction_mms = [0.70 .. 1.00]                                                                                               #some fraction % , input
emission_factor_n20_direct = 0.002                                                                                          #kg N2O-N/kg N, some fraction input
kg_n20n_to_kg_co2 = 44/28 = 1.57                                                                                            #kg co2/kg n2o/animal/day
direct_nitrus_oxide_daily = n_excretion_rate_daily * fraction_mms * emission_factor_n20_direct * kg_n20n_to_kg_n2o          #kg n2o/animal/day
n2o_to_co2 = 310                                                                                                            #kg co2/kg n2o
co2_from_n2o_daily = direct_nitrus_oxide_daily * n2o_to_co2                                                                 #kg co2/animal/day 
direct_nitrus_oxide_yearly = n_excretion_rate_yearly * fraction_mms * emission_factor_n20_direct * kg_n20n_to_kg_n2o        #kg n2o/animal/year
co2_from_n2o_yearly = direct_nitrus_oxide_yearly * n2o_to_co2                                                               #kg co2/animal/year  

Another set of N? Indirect, translate


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

\\\\\\\\\\\\\\\\\\\\\\\\\\\\
-

"""