################################################################################
"""
RUFAS: Ruminant Farm Systems Model
File name: inputs_outputs.py
Description: This file contains the class which stores the input and expected
    outputs of the manure excretion subroutines unit tests.
Author(s): Joseph Merhi, jm2257@cornell.edu
"""
################################################################################


class AnimalInputOutputs:
    feed_info_0 = {
        "feed_database": "input/databases/feeds.sqlite",
        "feeds_table": "user_feeds",
        "feed_quality_table": "feed_quality",
        "nutrient_table": "nutrients",

        "purchased_feeds": [2, 26, 36, 86, 118, 136, 139],
        "purchased_feeds_costs": {"2": 0.17, "26": 0.1, "36": 0, "86": 0,
                                  "118": 0.39, "136": 0.53, "139": 0.25},
        "growing_feeds": [87],

        "storage_options": {
            "storage_1": {
                "storage_type": "bag",
                "moisture": "direct_cut",
                "additive": "preservative",
                "packing_density": 14,
                "inoculation": "heterofermentative",
                "bunk_type": "open_floor",
                "ventilation": True,
                "removal_rate": 6,
                "initial_dry_matter": 0
            },
            "storage_2": {
                "storage_type": "bag",
                "moisture": "direct_cut",
                "additive": "preservative",
                "packing_density": 14,
                "inoculation": "heterofermentative",
                "bunk_type": "open_floor",
                "ventilation": True,
                "removal_rate": 6,
                "initial_dry_matter": 0
            }
        }
    }

    ration_formulation0 = {
        '2': 0.0,
        '26': 4.887924,
        '36': 11.581502,
        '86': 0.0,
        '118': 10.027916,
        '136': 0.0,
        '139': 0.137716,
        'status': 'Optimal',
        'objective': 4.434108608742826
    }

    lactating_input_1 = {
        'BW': 714,
        'days_milk': 125,
        'milk_protein': 3.5,
        'milk_prod': 45,
        'p_feces_excrt': 26,
        'p_urine': 1.42,
        'methane_model': "IPCC",
        'milk_fat': 3.4,
        'ME_intake': 68
    }

    lactating_input_2 = {
        'BW': 714,
        'days_milk': 125,
        'milk_protein': 3.5,
        'milk_prod': 45,
        'p_feces_excrt': 26,
        'p_urine': 1.42,
        'methane_model': "Mutian",
        'milk_fat': 3.4,
        'ME_intake': 68
    }

    lactating_input_3 = {
        'BW': 714,
        'days_milk': 125,
        'milk_protein': 3.5,
        'milk_prod': 45,
        'p_feces_excrt': 26,
        'p_urine': 1.42,
        'methane_model': "Mills",
        'milk_fat': 3.4,
        'ME_intake': 68
    }

    expected_lactating_manure_1 = {
        "U": 0.36656083645578613,
        "TAN_s": 0.13515288710255696,
        "MN": 629.376708032217,
        "Mkg": 78.80088816613554,
        "TSd": 8.238886718791626,
        "VSd": 8368.032667449977,
        "VSnd": 931.2272211295405,
        "WIP_frac": 0.00017398281058831814,
        "WOP_frac": 1.7398281058831816e-05,
        "p_excrt_manure": 27.42,
        "p_frac": 0.00034796562117663627,
        "K_manure": 147.30299001717202,
        "CH4_manure": 616.3540081290207
    }

    expected_lactating_manure_2 = {
        "U": 0.36656083645578613,
        "TAN_s": 0.13515288710255696,
        "MN": 629.376708032217,
        "Mkg": 78.80088816613554,
        "TSd": 8.238886718791626,
        "VSd": 8368.032667449977,
        "VSnd": 931.2272211295405,
        "WIP_frac": 0.00017398281058831814,
        "WOP_frac": 1.7398281058831816e-05,
        "p_excrt_manure": 27.42,
        "p_frac": 0.00034796562117663627,
        "K_manure": 147.30299001717202,
        "CH4_manure": 436.0681549509677
    }

    expected_lactating_manure_3 = {
        "U": 0.36656083645578613,
        "TAN_s": 0.13515288710255696,
        "MN": 629.376708032217,
        "Mkg": 78.80088816613554,
        "TSd": 8.238886718791626,
        "VSd": 8368.032667449977,
        "VSnd": 931.2272211295405,
        "WIP_frac": 0.00017398281058831814,
        "WOP_frac": 1.7398281058831816e-05,
        "p_excrt_manure": 27.42,
        "p_frac": 0.00034796562117663627,
        "K_manure": 147.30299001717202,
        "CH4_manure": 417.8712493649146
    }

    dry_input_1 = {
        'BW': 714,
        'milk_prod': 45,
        'p_feces_excrt': 26,
        'p_urine': 1.42,
        'ME_intake': 68
    }

    expected_dry_manure_1 = {
        "U": 0.340,
        "TAN_s": 0.14,
        "MN": 636.5491134747106,
        "Mkg": 37.552,
        "TSd": 7.474040323999999,
        "VSd": 7087.413,
        "VSnd": 859.390,
        "WIP_frac": 0.00036509373668513,
        "WOP_frac": 3.6509373668513e-05,
        "p_excrt_manure": 27.42,
        "p_frac": 0.00073018747337026,
        "K_manure": 401.18008039999995,
        "CH4_manure": 417.8712493649146
    }

    heifer_input_1 = {
        'BW': 714,
        'p_feces_excrt': 26,
        'p_urine': 1.42,
    }

    expected_heifer_manure_1 = {
        "U": 0.340,
        "TAN_s": 0.14,
        "MN": 590.1758812976,
        "Mkg": 88.438835388,
        "TSd": 5.997599999999999,
        "VSd": 7087.413,
        "VSnd": 859.390,
        "WIP_frac": 0.0001550223941761706,
        "WOP_frac": 1.550223941761706e-05,
        "p_excrt_manure": 27.42,
        "p_frac": 0.0003100447883523412,
        "K_manure": 401.18008039999995,
        "CH4_manure": 411.53941717008
    }

    calf_input_1 = {
        'BW': 714,
        'p_feces_excrt': 26,
        'p_urine': 1.42,
    }

    expected_calf_manure_1 = {
        "U": 0.340,
        "TAN_s": 0.14,
        "MN": 532.407,
        "Mkg": 40.4838,
        "TSd": 6.640199999999999,
        "VSd": 7087.413,
        "VSnd": 859.390,
        "WIP_frac": 0.00033865398011056276,
        "WOP_frac": 3.386539801105628e-05,
        "p_excrt_manure": 27.42,
        "p_frac": 0.0006773079602211255,
        "K_manure": 0,
        "CH4_manure": 135.00303075956646
    }
