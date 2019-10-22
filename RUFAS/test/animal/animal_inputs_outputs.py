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
        'type' : "Barn"
    }
    
    lactating_cow_expected_rqmts_1 = {
        'FU': {'op': '<=', 'val': 7.566673489860807},
        'ME_DM': {'op': '>=', 'val': 57.238188330372566},
        'RDP_DM': {'op': '>=', 'val': 2.0347001114951313},
        'RU': {'op': '>=', 'val': 0},
        'RUP_DM': {'op': '>=', 'val': 1.2716733909335047}}
    
    lactating_cow_expected_ration_1 = {
        'status' : 'Optimal',
        'objective' : 4.536948317,
        'Corn_grain' : 0.0,
        'Legume_hay' : 13.669348,
        'Cotton_seed' : 6.0651063,
        'Roasted_soybean' : 2.4089406,
        'Rye_hay' : 0.0
    }    