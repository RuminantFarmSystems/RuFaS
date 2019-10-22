class AnimalInputsOutputs:
    lactating_cow_input_1 = { 
        'BW' : 650,
        'BCS' : 3.5,
        'CBW' : 45,
        'CI' : 390,
        'concentrate' : 6,
        'CP_Milk' : 3.2,
        'DOP' : 30,
        'DHD' : 1.6,
        'DVD' : 0.1,
        'DIM' : 100,
        'fat_milk' : 3.5,
        'lactose_milk' : 4.85,
        'milk' : 40,
        'parity' : 2,
        'type' : "barn",
        'mPrt' : 3.2
    }
    
    lactating_cow_expected_rqmts_1 = {
        'FU': {'op': '<=', 'val': 7.566673489860807},
        'ME_DM': {'op': '>=', 'val': 60.692875830372564},
        'RDP_DM': {'op': '>=', 'val': 2.0347001114951313},
        'RU': {'op': '>=', 'val': 0},
        'RUP_DM': {'op': '>=', 'val': 1.2716733909335047}
        }
    
    lactating_cow_expected_ration_1 = {
        'status' : 'Optimal',
        'objective' : 4.7985611960800005,
        'Corn_grain' : 0.065729461,
        'Legume_hay' : 12.951222,
        'Cotton_seed' : 7.9816535,
        'Roasted_soybean' : 2.3135948,
        'Rye_hay' : 0.0
    }  
    
    lactating_cow_input_ration_1 = {
        'Corn_grain': 0,
        'Legume_hay': 13.5588,
        'Cotton_seed': 6.3620,
        'Roasted_soybean': 2.3964,
        'Rye_hay': 0,
        'status': 'Optimal',
        'objective': 4.5756
    }
            
    lactating_cow_expected_manure_1 = {
        'U' :  0.34007492378760407,
        'TAN_s' :  0.1400150775776793,
        'MN' :  532.4074003089993,
        'Mkg' :  70.82359257209554,
        'VSd' :  7087.427669573749,
        'VSnd' :  859.3916402321569
    }  