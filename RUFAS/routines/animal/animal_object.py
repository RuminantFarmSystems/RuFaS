#import ration

class AnimalObject:
    id = -1
    DIM = -1
    age = -1
    nutrient_rqmts = {}
    times_milked_per_day = -1
    DVD = -1
    DHD = -1
    
    def __init__(self, id, DIM, age, times_milked_per_day):
        self.id = id
        self.DIM = DIM
        self.age = age
        self.times_milked_per_day = times_milked_per_day
    
    def calc_nutrient_rqmts(self):
        #self.nutrient_rqmts = ration.calculate_rqmts(BW, BCS, CBW, CI, concentrate, CP_Milk, DOP, DHD, DVD,
                        #DIM, fat_milk, lactose_milk, milk, parity, type, nutrients_list)
        self.nutrient_rqmts = {'FU': {'op': '<=', 'val': 7.566673489860807}, 'RU': {'op': '>=', 'val': 0}, 'ME_DM': {'op': '>=', 'val': 57.238188330372566}, 'RDP_DM': {'op': '>=', 'val': 2.0347001114951313}, 'RUP_DM': {'op': '>=', 'val': 1.2716733909335047}}
            
    def calc_daily_walking_dist(self, vertical_dist_to_parlor, horizontal_dist_to_parlor):
        '''
        Calculates and sets the animal's daily vertical and horizontal walking distance (DVD and DHD).
        Args:
            vertical_dist_to_parlor: number, km
            horizontal_dist_to_parlor: number, km
        '''
        #multiplied by 2 for return trip
        DVD = 2 * vertical_dist_to_parlor * self.times_milked_per_day
        DHD = 2 * horizontal_dist_to_parlor * self.times_milked_per_day
        
        