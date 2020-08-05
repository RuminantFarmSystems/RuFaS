def get_ration():
    return {'2': 0.75,
            '24': 5,
            '36': 2,
            '38': 4,
            '91': 5,
            '102': 3,
            '137': 0.32,
            'status': 'Optimal',
            'objective': 4.5}


def get_nutrient_rqmts():
    nutrient_rqmts = {'FU': {'op': '<=', 'val': 7.566673489860807},
                      'RU': {'op': '>=', 'val': 0},
                      'ME_DM': {'op': '>=', 'val': 57.238188330372566},
                      'RDP_DM': {'op': '>=', 'val': 2.0347001114951313},
                      'RUP_DM': {'op': '>=', 'val': 1.2716733909335047}}
    DMIest = 27.620363504458798
    DBW = -0.4125
    return nutrient_rqmts, DMIest, DBW
