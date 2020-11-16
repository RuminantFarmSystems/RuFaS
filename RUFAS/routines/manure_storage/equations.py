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


$Constants
-------------

TOTAL_HOURS_IN_A_DAY = 24
MINS_IN_AN_HOUR = 60
CENT = 100
LTRS_IN_M3 = 1000
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


Equations
------------

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

cleaning_method = CLEANING_METHOD                                                             #Either Flushing or Scraping
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
tan = tan_as_excreted * (percent_time_spent_per_day/CENT)                                                                  #kg/day
p2o5 = p2o5_as_excreted * (percent_time_spent_per_day/CENT)                                                                #kg/day
k2o = k2o_as_excreted * (percent_time_spent_per_day/CENT)                                                                  #kg/day




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
tn_as_excreted = Sum( num_type_[type] *  ANIMAL_[type]_TN for type in Types )
n_as_excreted_fr = Sum( num_type_[type] *  ANIMAL_[type]_N for type in Types )
p2o5_as_excreted = Sum( num_type_[type] *  ANIMAL_[type]_P2O5 for type in Types )
k2O_as_excreted = Sum( num_type_[type] *  ANIMAL_[type]_K2O for type in Types )
density = MILKING_CENTER_AND_HOLDING_PEN_DENSITY

Bedding
bedding_mass_per_day = LC[SB or OB] * total_animals            # kg/day
volume_per_day = mass_per_day / LC[SB or OB]_density   # m3/day

Cleaning
cleaning_method = [flushing/scraping]
flush_water = [cleaning_method]_water_volume_fr * total_animals  #ltrs/day



time_spent_per_day_fr = HOURS_IN_A_DAY - time_spent_per_day_lc   #hrs
percent_time_spent_per_day_fr = CENT - percent_time_spent_per_day_lc       # some percentage


MANURE GENERATED
total_waste_volume = ((raw_manure/manure_densiy)*percent_time_spent_per_day/CENT) + (flush_water/1000) + total_waste_volume_received_mlk + sand_volume_separated  #m3/day
****Some numbers not understood, ask Varma****
ts_manure_bedding_rfw_percent = [1-2] % #some input
ts_manure_bedding_rfw = (total_solids_excreted * percent_time_spent_per_day/CENT) + total_solids_mlk + ts_rfw_contribution      #kg/day
ts_g_per_L = total_solids_manure_bedding_rfw / total_waste_volume         #g/L
vs_manure_bedding_rfw = (volatile_solids_fr * percent_time_spent_per_day/CENT) + volatile_solids_mlk + vs_rfw     #kg/day
vs_manure_bedding_rfw_g_per_l = vs_manure_bedding_rfw / total_waste_volume    #g/L
n_manure_bedding_rfw = (n_as_excreted_fr * percent_time_spent_per_day/CENT) + nitrogen_mlk + n_rfw     #kg/day
n_manure_bedding_rfw_g_per_l = n_manure_bedding_rfw / total_waste_volume    #g/L 
"""