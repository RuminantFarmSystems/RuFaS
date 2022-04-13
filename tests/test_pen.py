"""
RUFAS: Ruminant Farm Systems Model
File name: test_pen.py
Description: Implements test cases for the Pen class
Author(s): Pooya Hekmati, sh2235@cornell.edu, Anchey Peng, ap724@cornell.edu
"""

import pytest

from RUFAS.routines.animal.animal_management import AnimalManagement
from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase
from RUFAS.routines.animal.life_cycle.calf import Calf
from RUFAS.routines.animal.life_cycle.cow import Cow
from RUFAS.routines.animal.pen import Pen


@pytest.fixture
def pen():
    id_number = 0
    vert_dist = 0.1
    horiz_dist = 1.6
    num_stalls = 100
    housing_type = 'open air barn'
    bedding_type = 'sand'
    pen_type = 'freestall'
    manure_handling = "manual_scraping"
    manure_separator = "sedimentation"
    manure_storage = "storage_pit"
    animal_combination = Pen.AnimalCombination.CALF
    max_stocking_density = 1.2

    pen = Pen(id_number, vert_dist, horiz_dist, num_stalls, housing_type, bedding_type, pen_type, manure_handling,
              manure_separator, manure_storage, animal_combination, max_stocking_density)

    return pen


@pytest.fixture
def configured_animal_base():
    animal_config = {
        "management_decisions": {
            "breeding_start_day_h": 360,
            "heifer_repro_method": "TAI",
            "cow_repro_method": "TAI",
            "semen_type": "conventional",
            "days_in_preg_when_dry": 218,
            "lactation_curve": "wood",
            "heifer_repro_cull_time": 650,
            "repro_cull_time": 300,
            "do_not_breed_time": 300,
            "cull_milk_production": 22,
            "cow_times_milked_per_day": 1
        },
        "farm_level": {
            "calf": {
                "male_calf_rate_sexed_semen": 0.1,
                "male_calf_rate_conventional_semen": 0.53,
                "birth_weight_avg_ho": 43.9,
                "birth_weight_std_ho": 1.0,
                "birth_weight_avg_je": 35.2,
                "birth_weight_std_je": 0.9,
                "keep_female_calf_rate": 1,
                "wean_day": 60,
                "wean_length": 7,
                "milk_type": "whole"
            },
            "repro": {
                "estrus_detection_rate": 0.4,
                "estrus_service_rate": 0.9,
                "ed_conception_rate": 0.4,
                "heifer_TAI_protocol": "5dCG2P",
                "m5dCG2P_conception_rate": 0.6,
                "m5dCGP_conception_rate": 0.48,
                "heifer_user_defined_tai_cr": 0.0,
                "heifer_synchED_protocol": "2P",
                "cow_presynch_protocol": "Double OvSynch",
                "user_defined_presynch_length": 0,
                "cow_TAI_protocol": "OvSynch 56",
                "ovsynch56_conception_rate": 0.55,
                "ovsynch48_conception_rate": 0.4,
                "cosynch72_conception_rate": 0.4,
                "cosynch5d_conception_rate": 0.4,
                "cow_user_defined_tai_cr": 0.0,
                "cow_resynch_protocol": "TAIafterPD",
                "user_define_tai_length": 0,
                "voluntary_waiting_period": 45,
                "tai_program_start_day": 72,
                "conception_rate_decrease": 0.026,
                "avg_gestation_len": 278,
                "std_gestation_len": 6,
                "prefresh_day": 30,
                "num_21_days_repro": 15,
                "calving_interval": 400,
                "use_input_calving_interval": False

            },
            "bodyweight": {
                "target_heifer_preg_day": 420,
                "mature_body_weight_avg": 740.1,
                "mature_body_weight_std": 73.5
            }
        },
        "from_literature": {
            "repro": {
                "avg_estrus_cycle_heifer": 21,
                "std_estrus_cycle_heifer": 3,
                "preg_check_day_1": 32,
                "preg_loss_rate_1": 0.02,
                "preg_check_day_2": 91,
                "preg_loss_rate_2": 0.096,
                "preg_check_day_3": 200,
                "preg_loss_rate_3": 0.017,
                "avg_estrus_cycle_return": 19,
                "std_estrus_cycle_return": 11,
                "avg_estrus_cycle_cow": 21,
                "std_estrus_cycle_cow": 2.5,
                "avg_estrus_cycle_p": 10,
                "std_estrus_cycle_p": 2
            },
            "milking": {
                "wood_l": [[16.13, 23.61, 23.81], [14.07, 19.26, 19.21]],
                "wood_m": [[0.235, 0.227, 0.244], [0.186, 0.173, 0.190]],
                "wood_n": [[0.0019, 0.0032, 0.0036], [0.0021, 0.0028, 0.0032]],
                "wood_l_std": [[0.28, 0.54, 0.51], [0.39, 0.49, 0.47]],
                "wood_m_std": [[0.0046, 0.0064, 0.0060], [0.0076, 0.0071, 0.0069]],
                "wood_n_std": [[3.77e-5, 5.82e-5, 5.54e-5], [6.60e-5, 6.69e-5, 6.53e-5]]
            },
            "culling": {
                "parity_death_prob": [0.039, 0.056, 0.085, 0.117],
                "death_cull_prob": [0, 0.18, 0.32, 0.42, 0.48, 0.54, 0.60, 0.65, 0.70, 0.77, 0.83, 0.89, 0.95, 1],
                "parity_cull_prob": [0.169, 0.233, 0.301, 0.408],
                "mastitis_cull_prob": [0, 0.06, 0.12, 0.19, 0.30, 0.43, 0.56, 0.68, 0.78, 0.85, 0.90, 0.94, 0.97, 1],
                "feet_leg_cull_prob": [0, 0.03, 0.08, 0.16, 0.25, 0.36, 0.48, 0.59, 0.69, 0.78, 0.85, 0.90, 0.95, 1],
                "injury_cull_prob": [0, 0.08, 0.18, 0.28, 0.38, 0.47, 0.56, 0.64, 0.71, 0.78, 0.85, 0.90, 0.95, 1],
                "disease_cull_prob": [0, 0.04, 0.12, 0.24, 0.34, 0.42, 0.50, 0.57, 0.64, 0.72, 0.81, 0.89, 0.95, 1],
                "udder_cull_prob": [0, 0.12, 0.24, 0.33, 0.41, 0.48, 0.55, 0.62, 0.68, 0.76, 0.82, 0.89, 0.95, 1],
                "unkown_cull_prob": [0, 0.05, 0.11, 0.18, 0.27, 0.37, 0.45, 0.54, 0.62, 0.70, 0.77, 0.84, 0.92, 1],
                "cull_day_count": [0, 5, 15, 45, 90, 135, 180, 225, 270, 330, 380, 430, 480, 530]
            },
            "life_cycle": {
                "still_birth_rate": 0.065
            }
        }
    }
    AnimalBase.set_config(AnimalManagement.get_animal_config(animal_config))
    AnimalBase.set_nutrient_list(['FU', 'RU', 'ME_DM', 'RDP_DM', 'RUP_DM'])


@pytest.fixture
def calves(configured_animal_base):
    # values obtained from animals.sqlite
    calf_args = [
        {
            'id': 371311,
            'breed': 'HO',
            'birth_date': 0,
            'days_born': 59,
            'birth_weight': 43.0670514245424,
            'p_init': 0,
            'body_weight': 85.4163186586756,
            'wean_weight': 0,
            'mature_body_weight': 740.805298797198,
            'events': ""
        },
        {
            'id': 371505,
            'breed': 'HO',
            'birth_date': 0,
            'days_born': 59,
            'birth_weight': 44.2522820253739,
            'p_init': 0,
            'body_weight': 87.7670260169917,
            'wean_weight': 0,
            'mature_body_weight': 659.335379863653,
            'events': ""
        }, {
            'id': 371517,
            'breed': 'HO',
            'birth_date': 0,
            'days_born': 59,
            'birth_weight': 43.9094552960784,
            'p_init': 0,
            'body_weight': 87.0870863372219,
            'wean_weight': 0,
            'mature_body_weight': 701.290041921741,
            'events': ""
        }

    ]

    calves = [Calf(args) for args in calf_args]

    return calves


@pytest.fixture
def cows():
    cow_args = [
        {
            'id': 198202,
            'breed': "HO",
            'birth_date': 0,
            'days_born': 2594,
            'birth_weight': 44.6039387019561,
            'body_weight': 638.150195605097,
            'wean_weight': 88.464478425546,
            'mature_body_weight': 679.7008092855,
            'events': "days born 60: ['wean day'] days born 360: ['breeding start', 'inject gnrh'] days born 365: ['inject pgf'] days born 366: ['inject pgf'] days born 368: ['inject gnrh', 'inseminated with conventional', 'heifer not pregnant'] days born 400: ['pregnancy check 1'] days born 401: ['inject gnrh'] days born 406: ['inject pgf'] days born 407: ['inject pgf'] days born 409: ['inject gnrh', 'inseminated with conventional', 'heifer pregnant'] days born 441: ['pregnancy check 1'] days born 500: ['pregnancy check 2'] days born 609: ['pregnancy check 3'] days born 647: ['heiferii moving to heiferiii'] days born 677: ['new birth, start milking'] days born 721: ['inject PGF'] days born 735: ['inject PGF'] days born 747: ['Presynch ended', 'inject GnRH'] days born 754: ['inject PGF'] days born 756: ['inject GnRH'] days born 757: ['inseminated with conventional', 'cow pregnant'] days born 789: ['pregnancy check 1: confirmed'] days born 848: ['pregnancy loss happened between 1st and 2nd pregnancy check'] days born 849: ['inject GnRH'] days born 856: ['inject PGF'] days born 858: ['inject GnRH'] days born 859: ['inseminated with conventional', 'cow pregnant'] days born 891: ['pregnancy check 1: confirmed'] days born 950: ['pregnancy check 2: confirmed'] days born 1059: ['pregnancy check 3: confirmed'] days born 1077: ['dry'] days born 1147: ['new birth, start milking'] days born 1191: ['inject PGF'] days born 1205: ['inject PGF'] days born 1217: ['Presynch ended', 'inject GnRH'] days born 1224: ['inject PGF'] days born 1226: ['inject GnRH'] days born 1227: ['inseminated with conventional', 'cow not pregnant'] days born 1259: ['pregnancy check 1: not pregnant'] days born 1260: ['inject GnRH'] days born 1267: ['inject PGF'] days born 1269: ['inject GnRH'] days born 1270: ['inseminated with conventional', 'cow not pregnant'] days born 1302: ['pregnancy check 1: not pregnant'] days born 1303: ['inject GnRH'] days born 1310: ['inject PGF'] days born 1312: ['inject GnRH'] days born 1313: ['inseminated with conventional', 'cow pregnant'] days born 1345: ['pregnancy check 1: confirmed'] days born 1404: ['pregnancy loss happened between 1st and 2nd pregnancy check'] days born 1405: ['inject GnRH'] days born 1412: ['inject PGF'] days born 1414: ['inject GnRH'] days born 1415: ['inseminated with conventional', 'cow pregnant'] days born 1447: ['pregnancy check 1: confirmed'] days born 1506: ['pregnancy check 2: confirmed'] days born 1615: ['pregnancy check 3: confirmed'] days born 1633: ['dry'] days born 1696: ['new birth, start milking'] days born 1740: ['inject PGF'] days born 1754: ['inject PGF'] days born 1766: ['Presynch ended', 'inject GnRH'] days born 1773: ['inject PGF'] days born 1775: ['inject GnRH'] days born 1776: ['inseminated with conventional', 'cow pregnant'] days born 1808: ['pregnancy loss happened before 1st pregnancy check'] days born 1867: ['pregnancy loss happened between 1st and 2nd pregnancy check'] days born 1868: ['inject GnRH'] days born 1875: ['inject PGF'] days born 1877: ['inject GnRH'] days born 1878: ['inseminated with conventional', 'cow not pregnant'] days born 1910: ['pregnancy check 1: not pregnant'] days born 1911: ['inject GnRH'] days born 1918: ['inject PGF'] days born 1920: ['inject GnRH'] days born 1921: ['inseminated with conventional', 'cow not pregnant'] days born 1953: ['pregnancy check 1: not pregnant'] days born 1954: ['inject GnRH'] days born 1961: ['inject PGF'] days born 1963: ['inject GnRH'] days born 1964: ['inseminated with conventional', 'cow pregnant'] days born 1996: ['pregnancy check 1: confirmed'] days born 2055: ['pregnancy check 2: confirmed'] days born 2164: ['pregnancy check 3: confirmed'] days born 2182: ['dry'] days born 2244: ['new birth, start milking'] days born 2288: ['inject PGF'] days born 2302: ['inject PGF'] days born 2314: ['Presynch ended', 'inject GnRH'] days born 2321: ['inject PGF'] days born 2323: ['inject GnRH'] days born 2324: ['inseminated with conventional', 'cow not pregnant'] days born 2356: ['pregnancy check 1: not pregnant'] days born 2357: ['inject GnRH'] days born 2364: ['inject PGF'] days born 2366: ['inject GnRH'] days born 2367: ['inseminated with conventional', 'cow pregnant'] days born 2399: ['pregnancy check 1: confirmed'] days born 2458: ['pregnancy check 2: confirmed'] days born 2567: ['pregnancy check 3: confirmed'] days born 2585: ['dry']",
            'repro_program': 'TAI',
            'tai_method_h': '5dCG2P',
            'synch_ed_method_h': '2P',
            'estrus_count': 0,
            'estrus_day': 0,
            'tai_program_start_day_h': 401,
            'synch_ed_program_start_day_h': 0,
            'synch_ed_estrus_day': 0,
            'synch_ed_stop_day': 0,
            'conception_rate': 0.55,
            'ai_day': 2367,
            'abortion_day': 2356,
            'days_in_preg': 228,
            'gestation_length': 289,
            'p_gest_for_calf': 0,
            'calf_birth_weight': 44.4506873679546,
            'presynch_method': 'PreSynch',
            'tai_method_c': 'OvSynch 56',
            'resynch_method': 'TAIafterPD',
            'days_in_milk': 0,
            'parity': 4,
            'calving_interval': 548
        },
        {
            'id': 200671,
            'breed': "HO",
            'birth_date': 0,
            'days_born': 2730,
            'birth_weight': 42.1402659148756,
            'body_weight': 768.108864550138,
            'wean_weight': 83.5781940645034,
            'mature_body_weight': 793.965129143175,
            'events': "days born 60: ['wean day'] days born 360: ['breeding start', 'inject gnrh'] days born 365: ['inject pgf'] days born 366: ['inject pgf'] days born 368: ['inject gnrh', 'inseminated with conventional', 'heifer not pregnant'] days born 400: ['pregnancy check 1'] days born 401: ['inject gnrh'] days born 406: ['inject pgf'] days born 407: ['inject pgf'] days born 409: ['inject gnrh', 'inseminated with conventional', 'heifer not pregnant'] days born 441: ['pregnancy check 1'] days born 442: ['inject gnrh'] days born 447: ['inject pgf'] days born 448: ['inject pgf'] days born 450: ['inject gnrh', 'inseminated with conventional', 'heifer not pregnant'] days born 482: ['pregnancy check 1'] days born 483: ['inject gnrh'] days born 488: ['inject pgf'] days born 489: ['inject pgf'] days born 491: ['inject gnrh', 'inseminated with conventional', 'heifer not pregnant'] days born 523: ['pregnancy check 1'] days born 524: ['inject gnrh'] days born 529: ['inject pgf'] days born 530: ['inject pgf'] days born 532: ['inject gnrh', 'inseminated with conventional', 'heifer not pregnant'] days born 564: ['pregnancy check 1'] days born 565: ['inject gnrh'] days born 570: ['inject pgf'] days born 571: ['inject pgf'] days born 573: ['inject gnrh', 'inseminated with conventional', 'heifer pregnant'] days born 605: ['pregnancy check 1'] days born 664: ['pregnancy check 2'] days born 773: ['pregnancy check 3'] days born 816: ['heiferii moving to heiferiii'] days born 846: ['new birth, start milking'] days born 890: ['inject PGF'] days born 904: ['inject PGF'] days born 916: ['Presynch ended', 'inject GnRH'] days born 923: ['inject PGF'] days born 925: ['inject GnRH'] days born 926: ['inseminated with conventional', 'cow not pregnant'] days born 958: ['pregnancy check 1: not pregnant'] days born 959: ['inject GnRH'] days born 966: ['inject PGF'] days born 968: ['inject GnRH'] days born 969: ['inseminated with conventional', 'cow pregnant'] days born 1001: ['pregnancy check 1: confirmed'] days born 1060: ['pregnancy loss happened between 1st and 2nd pregnancy check'] days born 1061: ['inject GnRH'] days born 1068: ['inject PGF'] days born 1070: ['inject GnRH'] days born 1071: ['inseminated with conventional', 'cow pregnant'] days born 1103: ['pregnancy check 1: confirmed'] days born 1162: ['pregnancy check 2: confirmed'] days born 1271: ['pregnancy check 3: confirmed'] days born 1289: ['dry'] days born 1338: ['new birth, start milking'] days born 1382: ['inject PGF'] days born 1396: ['inject PGF'] days born 1408: ['Presynch ended', 'inject GnRH'] days born 1415: ['inject PGF'] days born 1417: ['inject GnRH'] days born 1418: ['inseminated with conventional', 'cow pregnant'] days born 1450: ['pregnancy check 1: confirmed'] days born 1509: ['pregnancy loss happened between 1st and 2nd pregnancy check'] days born 1510: ['inject GnRH'] days born 1517: ['inject PGF'] days born 1519: ['inject GnRH'] days born 1520: ['inseminated with conventional', 'cow pregnant'] days born 1552: ['pregnancy check 1: confirmed'] days born 1611: ['pregnancy check 2: confirmed'] days born 1720: ['pregnancy check 3: confirmed'] days born 1738: ['dry'] days born 1797: ['new birth, start milking'] days born 1841: ['inject PGF'] days born 1855: ['inject PGF'] days born 1867: ['Presynch ended', 'inject GnRH'] days born 1874: ['inject PGF'] days born 1876: ['inject GnRH'] days born 1877: ['inseminated with conventional', 'cow not pregnant'] days born 1909: ['pregnancy check 1: not pregnant'] days born 1910: ['inject GnRH'] days born 1917: ['inject PGF'] days born 1919: ['inject GnRH'] days born 1920: ['inseminated with conventional', 'cow not pregnant'] days born 1952: ['pregnancy check 1: not pregnant'] days born 1953: ['inject GnRH'] days born 1960: ['inject PGF'] days born 1962: ['inject GnRH'] days born 1963: ['inseminated with conventional', 'cow pregnant'] days born 1995: ['pregnancy check 1: confirmed'] days born 2054: ['pregnancy check 2: confirmed'] days born 2163: ['pregnancy check 3: confirmed'] days born 2181: ['dry'] days born 2239: ['new birth, start milking'] days born 2283: ['inject PGF'] days born 2297: ['inject PGF'] days born 2309: ['Presynch ended', 'inject GnRH'] days born 2316: ['inject PGF'] days born 2318: ['inject GnRH'] days born 2319: ['inseminated with conventional', 'cow not pregnant'] days born 2351: ['pregnancy check 1: not pregnant'] days born 2352: ['inject GnRH'] days born 2359: ['inject PGF'] days born 2361: ['inject GnRH'] days born 2362: ['inseminated with conventional', 'cow not pregnant'] days born 2394: ['pregnancy check 1: not pregnant'] days born 2395: ['inject GnRH'] days born 2402: ['inject PGF'] days born 2404: ['inject GnRH'] days born 2405: ['inseminated with conventional', 'cow not pregnant'] days born 2437: ['pregnancy check 1: not pregnant'] days born 2438: ['inject GnRH'] days born 2445: ['inject PGF'] days born 2447: ['inject GnRH'] days born 2448: ['inseminated with conventional', 'cow not pregnant'] days born 2480: ['pregnancy check 1: not pregnant'] days born 2481: ['inject GnRH'] days born 2488: ['inject PGF'] days born 2490: ['inject GnRH'] days born 2491: ['inseminated with conventional', 'cow pregnant'] days born 2523: ['pregnancy check 1: confirmed'] days born 2582: ['pregnancy check 2: confirmed'] days born 2691: ['pregnancy check 3: confirmed'] days born 2709: ['dry'] ",
            'repro_program': 'TAI',
            'tai_method_h': '5dCG2P',
            'synch_ed_method_h': '2P',
            'estrus_count': 0,
            'estrus_day': 0,
            'tai_program_start_day_h': 565,
            'synch_ed_program_start_day_h': 0,
            'synch_ed_estrus_day': 0,
            'synch_ed_stop_day': 0,
            'conception_rate': 0.55,
            'ai_day': 2491,
            'abortion_day': 2480,
            'days_in_preg': 240,
            'gestation_length': 284,
            'p_gest_for_calf': 0,
            'calf_birth_weight': 44.7480324010067,
            'presynch_method': 'PreSynch',
            'tai_method_c': 'OvSynch 56',
            'resynch_method': 'TAIafterPD',
            'days_in_milk': 0,
            'parity': 4,
            'calving_interval': 442
        },
        {
            'id': 205548,
            'breed': "HO",
            'birth_date': 0,
            'days_born': 2504,
            'birth_weight': 44.2234373261858,
            'body_weight': 680.362633071374,
            'wean_weight': 87.7098173636017,
            'mature_body_weight': 744.771291337697,
            'events': "days born 60: ['wean day'] days born 360: ['breeding start', 'inject gnrh'] days born 365: ['inject pgf'] days born 366: ['inject pgf'] days born 368: ['inject gnrh', 'inseminated with conventional', 'heifer not pregnant'] days born 400: ['pregnancy check 1'] days born 401: ['inject gnrh'] days born 406: ['inject pgf'] days born 407: ['inject pgf'] days born 409: ['inject gnrh', 'inseminated with conventional', 'heifer pregnant'] days born 441: ['pregnancy check 1'] days born 500: ['pregnancy check 2'] days born 609: ['pregnancy check 3'] days born 647: ['heiferii moving to heiferiii'] days born 677: ['new birth, start milking'] days born 721: ['inject PGF'] days born 735: ['inject PGF'] days born 747: ['Presynch ended', 'inject GnRH'] days born 754: ['inject PGF'] days born 756: ['inject GnRH'] days born 757: ['inseminated with conventional', 'cow pregnant'] days born 789: ['pregnancy check 1: confirmed'] days born 848: ['pregnancy check 2: confirmed'] days born 957: ['pregnancy check 3: confirmed'] days born 975: ['dry'] days born 1036: ['new birth, start milking'] days born 1080: ['inject PGF'] days born 1094: ['inject PGF'] days born 1106: ['Presynch ended', 'inject GnRH'] days born 1113: ['inject PGF'] days born 1115: ['inject GnRH'] days born 1116: ['inseminated with conventional', 'cow not pregnant'] days born 1148: ['pregnancy check 1: not pregnant'] days born 1149: ['inject GnRH'] days born 1156: ['inject PGF'] days born 1158: ['inject GnRH'] days born 1159: ['inseminated with conventional', 'cow not pregnant'] days born 1191: ['pregnancy check 1: not pregnant'] days born 1192: ['inject GnRH'] days born 1199: ['inject PGF'] days born 1201: ['inject GnRH'] days born 1202: ['inseminated with conventional', 'cow not pregnant'] days born 1234: ['pregnancy check 1: not pregnant'] days born 1235: ['inject GnRH'] days born 1242: ['inject PGF'] days born 1244: ['inject GnRH'] days born 1245: ['inseminated with conventional', 'cow not pregnant'] days born 1277: ['pregnancy check 1: not pregnant'] days born 1278: ['inject GnRH'] days born 1285: ['inject PGF'] days born 1287: ['inject GnRH'] days born 1288: ['inseminated with conventional', 'cow not pregnant'] days born 1320: ['pregnancy check 1: not pregnant'] days born 1321: ['inject GnRH'] days born 1328: ['inject PGF'] days born 1330: ['inject GnRH'] days born 1331: ['inseminated with conventional', 'cow pregnant'] days born 1363: ['pregnancy check 1: confirmed'] days born 1422: ['pregnancy check 2: confirmed'] days born 1531: ['pregnancy check 3: confirmed'] days born 1549: ['dry'] days born 1612: ['new birth, start milking'] days born 1656: ['inject PGF'] days born 1670: ['inject PGF'] days born 1682: ['Presynch ended', 'inject GnRH'] days born 1689: ['inject PGF'] days born 1691: ['inject GnRH'] days born 1692: ['inseminated with conventional', 'cow pregnant'] days born 1724: ['pregnancy check 1: confirmed'] days born 1783: ['pregnancy loss happened between 1st and 2nd pregnancy check'] days born 1784: ['inject GnRH'] days born 1791: ['inject PGF'] days born 1793: ['inject GnRH'] days born 1794: ['inseminated with conventional', 'cow not pregnant'] days born 1826: ['pregnancy check 1: not pregnant'] days born 1827: ['inject GnRH'] days born 1834: ['inject PGF'] days born 1836: ['inject GnRH'] days born 1837: ['inseminated with conventional', 'cow pregnant'] days born 1869: ['pregnancy check 1: confirmed'] days born 1928: ['pregnancy check 2: confirmed'] days born 2037: ['pregnancy check 3: confirmed'] days born 2055: ['dry'] days born 2123: ['new birth, start milking'] days born 2167: ['inject PGF'] days born 2181: ['inject PGF'] days born 2193: ['Presynch ended', 'inject GnRH'] days born 2200: ['inject PGF'] days born 2202: ['inject GnRH'] days born 2203: ['inseminated with conventional', 'cow not pregnant'] days born 2235: ['pregnancy check 1: not pregnant'] days born 2236: ['inject GnRH'] days born 2243: ['inject PGF'] days born 2245: ['inject GnRH'] days born 2246: ['inseminated with conventional', 'cow pregnant'] days born 2278: ['pregnancy check 1: confirmed'] days born 2337: ['pregnancy loss happened between 1st and 2nd pregnancy check'] days born 2338: ['inject GnRH'] days born 2345: ['inject PGF'] days born 2347: ['inject GnRH'] days born 2348: ['inseminated with conventional', 'cow pregnant'] days born 2380: ['pregnancy check 1: confirmed'] days born 2439: ['pregnancy check 2: confirmed']",
            'repro_program': 'TAI',
            'tai_method_h': '5dCG2P',
            'synch_ed_method_h': '2P',
            'estrus_count': 0,
            'estrus_day': 0,
            'tai_program_start_day_h': 401,
            'synch_ed_program_start_day_h': 0,
            'synch_ed_estrus_day': 0,
            'synch_ed_stop_day': 0,
            'conception_rate': 0.55,
            'ai_day': 2348,
            'abortion_day': 2337,
            'days_in_preg': 157,
            'gestation_length': 280,
            'p_gest_for_calf': 0,
            'calf_birth_weight': 44.6964834380077,
            'presynch_method': 'PreSynch',
            'tai_method_c': 'OvSynch 56',
            'resynch_method': 'TAIafterPD',
            'days_in_milk': 382,
            'parity': 4,
            'calving_interval': 511
        },
        {
            'id': 207271,
            'breed': "HO",
            'birth_date': 0,
            'days_born': 2491,
            'birth_weight': 43.8087397980726,
            'body_weight': 714.91629508637,
            'wean_weight': 86.8873339328441,
            'mature_body_weight': 745.771722103608,
            'events': "days born 60: ['wean day'] days born 360: ['breeding start', 'inject gnrh'] days born 365: ['inject pgf'] days born 366: ['inject pgf'] days born 368: ['inject gnrh', 'inseminated with conventional', 'heifer not pregnant'] days born 400: ['pregnancy check 1'] days born 401: ['inject gnrh'] days born 406: ['inject pgf'] days born 407: ['inject pgf'] days born 409: ['inject gnrh', 'inseminated with conventional', 'heifer pregnant'] days born 441: ['pregnancy check 1'] days born 500: ['pregnancy check 2'] days born 609: ['pregnancy check 3'] days born 652: ['heiferii moving to heiferiii'] days born 682: ['new birth, start milking'] days born 726: ['inject PGF'] days born 740: ['inject PGF'] days born 752: ['Presynch ended', 'inject GnRH'] days born 759: ['inject PGF'] days born 761: ['inject GnRH'] days born 762: ['inseminated with conventional', 'cow pregnant'] days born 794: ['pregnancy check 1: confirmed'] days born 853: ['pregnancy loss happened between 1st and 2nd pregnancy check'] days born 854: ['inject GnRH'] days born 861: ['inject PGF'] days born 863: ['inject GnRH'] days born 864: ['inseminated with conventional', 'cow not pregnant'] days born 896: ['pregnancy check 1: not pregnant'] days born 897: ['inject GnRH'] days born 904: ['inject PGF'] days born 906: ['inject GnRH'] days born 907: ['inseminated with conventional', 'cow not pregnant'] days born 939: ['pregnancy check 1: not pregnant'] days born 940: ['inject GnRH'] days born 947: ['inject PGF'] days born 949: ['inject GnRH'] days born 950: ['inseminated with conventional', 'cow pregnant'] days born 982: ['pregnancy check 1: confirmed'] days born 1041: ['pregnancy check 2: confirmed'] days born 1150: ['pregnancy check 3: confirmed'] days born 1168: ['dry'] days born 1224: ['new birth, start milking'] days born 1268: ['inject PGF'] days born 1282: ['inject PGF'] days born 1294: ['Presynch ended', 'inject GnRH'] days born 1301: ['inject PGF'] days born 1303: ['inject GnRH'] days born 1304: ['inseminated with conventional', 'cow pregnant'] days born 1336: ['pregnancy check 1: confirmed'] days born 1395: ['pregnancy loss happened between 1st and 2nd pregnancy check'] days born 1396: ['inject GnRH'] days born 1403: ['inject PGF'] days born 1405: ['inject GnRH'] days born 1406: ['inseminated with conventional', 'cow not pregnant'] days born 1438: ['pregnancy check 1: not pregnant'] days born 1439: ['inject GnRH'] days born 1446: ['inject PGF'] days born 1448: ['inject GnRH'] days born 1449: ['inseminated with conventional', 'cow not pregnant'] days born 1481: ['pregnancy check 1: not pregnant'] days born 1482: ['inject GnRH'] days born 1489: ['inject PGF'] days born 1491: ['inject GnRH'] days born 1492: ['inseminated with conventional', 'cow pregnant'] days born 1524: ['pregnancy check 1: confirmed'] days born 1583: ['pregnancy check 2: confirmed'] days born 1692: ['pregnancy check 3: confirmed'] days born 1710: ['dry'] days born 1772: ['new birth, start milking'] days born 1816: ['inject PGF'] days born 1830: ['inject PGF'] days born 1842: ['Presynch ended', 'inject GnRH'] days born 1849: ['inject PGF'] days born 1851: ['inject GnRH'] days born 1852: ['inseminated with conventional', 'cow pregnant'] days born 1884: ['pregnancy check 1: confirmed'] days born 1943: ['pregnancy check 2: confirmed'] days born 2052: ['pregnancy check 3: confirmed'] days born 2070: ['dry'] days born 2129: ['new birth, start milking'] days born 2173: ['inject PGF'] days born 2187: ['inject PGF'] days born 2199: ['Presynch ended', 'inject GnRH'] days born 2206: ['inject PGF'] days born 2208: ['inject GnRH'] days born 2209: ['inseminated with conventional', 'cow not pregnant'] days born 2241: ['pregnancy check 1: not pregnant'] days born 2242: ['inject GnRH'] days born 2249: ['inject PGF'] days born 2251: ['inject GnRH'] days born 2252: ['inseminated with conventional', 'cow pregnant'] days born 2284: ['pregnancy check 1: confirmed'] days born 2343: ['pregnancy check 2: confirmed'] days born 2452: ['pregnancy check 3: confirmed'] days born 2470: ['dry']",
            'repro_program': 'TAI',
            'tai_method_h': '5dCG2P',
            'synch_ed_method_h': '2P',
            'estrus_count': 0,
            'estrus_day': 0,
            'tai_program_start_day_h': 401,
            'synch_ed_program_start_day_h': 0,
            'synch_ed_estrus_day': 0,
            'synch_ed_stop_day': 0,
            'conception_rate': 0.55,
            'ai_day': 2252,
            'abortion_day': 2241,
            'days_in_preg': 240,
            'gestation_length': 283,
            'p_gest_for_calf': 0,
            'calf_birth_weight': 44.4085202008621,
            'presynch_method': 'PreSynch',
            'tai_method_c': 'OvSynch 56',
            'resynch_method': 'TAIafterPD',
            'days_in_milk': 0,
            'parity': 4,
            'calving_interval': 357
        }
    ]

    cows = [Cow(args) for args in cow_args]

    return cows


def test_update_animals():
    """Unit test for function update_animals in file routines/animal/pen.py"""
    pass


def test_call_animal_nutrient_rqmts():
    """Unit test for function call_animal_nutrient_rqmts in file routines/animal/pen.py"""
    pass


def test_calc_avg_nutrient_rqmts():
    """Unit test for function calc_avg_nutrient_rqmts in file routines/animal/pen.py"""
    pass


def test_calc_avg_stats():
    """Unit test for function calc_avg_stats in file routines/animal/pen.py"""
    pass


def test_calc_ration():
    """Unit test for function calc_ration in file routines/animal/pen.py"""
    pass


def test_calc_manure():
    """Unit test for function calc_manure in file routines/animal/pen.py"""
    pass


def test_reset_manure(pen):
    """Unit test for function reset_manure in file routines/animal/pen.py"""
    pen.manure = {}
    pen.calf_total = {}
    pen.heifer_total = {}
    pen.dry_total = {}
    pen.lactating_total = {}

    expected = {"U": 0,
                "TAN_s": 0,
                "MN": 0,
                "Mkg": 0,
                "TSd": 0,
                "VSd": 0,
                "VSnd": 0,
                "WIP_frac": 0,
                "WOP_frac": 0,
                "p_excrt_manure": 0,
                "p_frac": 0,
                "K_manure": 0,
                "CH4_manure": 0
                }

    pen.reset_manure()

    assert pen.manure == expected
    assert pen.calf_total == expected
    assert pen.heifer_total == expected
    assert pen.dry_total == expected
    assert pen.lactating_total == expected


@pytest.fixture
def calf_daily_growth_values():
    return [0.7445883642358595,
            0.7254529863013488,
            0.7342433606191534,
            ]


@pytest.fixture
def calves_with_daily_growth(calves, calf_daily_growth_values):
    for calf, daily_growth in zip(calves, calf_daily_growth_values):
        calf.daily_growth = daily_growth

    return calves


def test_calc_avg_growth(pen, calves_with_daily_growth, calf_daily_growth_values):
    """Unit test for function calc_avg_growth in file routines/animal/pen.py"""
    pen.animals_in_pen = calves_with_daily_growth
    pen.calc_avg_growth()

    actual = pen.avg_growth
    expected = sum(calf_daily_growth_values) / len(calf_daily_growth_values)

    assert actual == expected


def test_calc_daily_walking_dist():
    """Unit test for function calc_daily_walking_dist in file routines/animal/pen.py"""
    pass


def test_call_p_rqmts():
    """Unit test for function call_p_rqmts in file routines/animal/pen.py"""
    pass


def test_daily_p_update(pen):
    """Unit test for function daily_p_update in file routines/animal/pen.py"""

    # def daily_p_update(self):
    #     """
    #     Calls each animal's method to calculate daily phosphorus update.
    #     """
    #     if not len(self.animals_in_pen) == 0:
    #         total_p_animal = 0
    #         for animal in self.animals_in_pen:
    #             animal.daily_p_update()
    #             total_p_animal += animal.p_animal
    #         self.avg_p_animal = total_p_animal / len(self.animals_in_pen)


def test_set_up_new_animal():
    """Unit test for function set_up_new_animal in file routines/animal/pen.py"""
    pass


def test_clear(pen, calves):
    """Unit test for function clear in file routines/animal/pen.py"""
    pen.animals_in_pen = calves
    pen.pen_populated = True
    pen.avg_p_animal = 1.0

    pen.clear()

    assert pen.animals_in_pen == []
    assert pen.pen_populated is False
    assert pen.avg_p_animal == 0


def test_subset_class_feeds(mocker, pen):
    """Unit test for function subset_class_feeds in file routines/animal/pen.py"""

    feed_combinations = {
        Pen.AnimalCombination.CALF: {155, 156, 157},
        Pen.AnimalCombination.GROWING: {2, 51, 86, 136},
        Pen.AnimalCombination.CLOSE_UP: {2, 26, 86, 118, 136, 139},
        Pen.AnimalCombination.GROWING_AND_CLOSE_UP: {2, 51, 86, 136} | {2, 26, 86, 118, 136, 139},
        Pen.AnimalCombination.LAC_COW: {26, 86, 103, 118, 136, 139},
    }

    feed = mocker.MagicMock()
    feed.input_feed_combinations = feed_combinations

    pen.animal_combination = Pen.AnimalCombination.CALF
    pen.subset_class_feeds(feed)
    assert pen.allocated_feeds == {155, 156, 157}

    pen.animal_combination = Pen.AnimalCombination.GROWING
    pen.subset_class_feeds(feed)
    assert pen.allocated_feeds == {2, 51, 86, 136}

    pen.animal_combination = Pen.AnimalCombination.CLOSE_UP
    pen.subset_class_feeds(feed)
    assert pen.allocated_feeds == {2, 26, 86, 118, 136, 139}

    pen.animal_combination = Pen.AnimalCombination.GROWING_AND_CLOSE_UP
    pen.subset_class_feeds(feed)
    assert pen.allocated_feeds == {2, 51, 86, 136, 26, 86, 118, 136, 139}

    pen.animal_combination = Pen.AnimalCombination.LAC_COW
    pen.subset_class_feeds(feed)
    assert pen.allocated_feeds == {26, 86, 103, 118, 136, 139}
