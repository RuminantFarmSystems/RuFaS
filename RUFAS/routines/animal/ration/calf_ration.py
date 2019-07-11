def optimize(feed, rqmts):
    pass

def calculate_rqmts():
    nutrient_rqmts = {'FU': {'op': '<=', 'val': 7.566673489860807}, 'RU': {'op': '>=', 'val': 0}, 'ME_DM': {'op': '>=', 'val': 57.238188330372566}, 'RDP_DM': {'op': '>=', 'val': 2.0347001114951313}, 'RUP_DM': {'op': '>=', 'val': 1.2716733909335047}}
    DMIest = 27.620363504458798 
    DBW = -0.4125
    return nutrient_rqmts, DMIest, DBW