#import ration

class AnimalObject:
    id = -1
    DIM = -1
    age = -1
    nutrient_rqmts = {}
    
    def __init__(self, id, DIM, age):
        self.id = id
        self.DIM = DIM
        self.age = age
    
    def calc_nutrient_rqmts(self):
        #self.nutrient_rqmts = ration.calculate_rqmts(BW, BCS, CBW, CI, concentrate, CP_Milk, DOP, DHD, DVD,
                        #DIM, fat_milk, lactose_milk, milk, parity, type, nutrients_list)
        self.nutrient_rqmts = {'FU': {'op': '<=', 'val': 7.566673489860807}, 'RU': {'op': '>=', 'val': 0}, 'ME_DM': {'op': '>=', 'val': 57.238188330372566}, 'RDP_DM': {'op': '>=', 'val': 2.0347001114951313}, 'RUP_DM': {'op': '>=', 'val': 1.2716733909335047}}
        
        pass
        
        