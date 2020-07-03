from .hardcoded_ration import get_nutrient_rqmts, get_ration


def optimize(feed, rqmts):
    return get_ration()


def calculate_rqmts(BW, BCS, CBW, pasture_concentrate, CP_Milk, DOP, DHD,
                    DVD, DIM, fat_milk, lactose_milk, milk, parity,
                    farming_type, nutrients_list):
    return get_nutrient_rqmts()


def set_globals(DMIest, BW, DBW, milk, CP_milk):
    pass
