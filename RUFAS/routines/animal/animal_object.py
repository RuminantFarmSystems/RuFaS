# import ration

class AnimalObject:
    # unique animal ID, from input file
    id = -1
    
    # days in milk, days
    DIM = -1
    
    # age of cow (units??)
    age = -1
    
    # how many times per day the animal is milked
    times_milked_per_day = -1
    
    # daily vertical distance, km
    DVD = -1
    
    # daily horizontal distance, km
    DHD = -1
    
    # nutrient requirements for this animal 
    nutrient_rqmts = {}
    
    # ration given to this animal
    ration_formulation = {}
    
    # this animal's manure excretion components
    manure_excretion = {}
    
    # daily growth (units??)
    daily_growth = -1
    
    # milk production, kg
    milk_production = -1
    
    def __init__(self, id, DIM, age, times_milked_per_day):
        '''
        Initializes an animal with the arguments. More information about each above.
        '''
        self.id = id
        self.DIM = DIM
        self.age = age
        self.times_milked_per_day = times_milked_per_day
    
    def calc_nutrient_rqmts(self):
        '''
        Calculates this animal's nutrient requirements.
        '''
        # self.nutrient_rqmts = ration.calculate_rqmts(BW, BCS, CBW, CI, concentrate, CP_Milk, DOP, DHD, DVD,
                        # DIM, fat_milk, lactose_milk, milk, parity, type, nutrients_list)
        self.nutrient_rqmts = {'FU': {'op': '<=', 'val': 7.566673489860807}, 'RU': {'op': '>=', 'val': 0}, 'ME_DM': {'op': '>=', 'val': 57.238188330372566}, 'RDP_DM': {'op': '>=', 'val': 2.0347001114951313}, 'RUP_DM': {'op': '>=', 'val': 1.2716733909335047}}
            
    def calc_daily_walking_dist(self, vertical_dist_to_parlor, horizontal_dist_to_parlor):
        '''
        Calculates and sets the animal's daily vertical and horizontal walking distance (DVD and DHD).
        Args:
            vertical_dist_to_parlor: number, km
            horizontal_dist_to_parlor: number, km
        '''
        # multiplied by 2 for return trip
        DVD = 2 * vertical_dist_to_parlor * self.times_milked_per_day
        DHD = 2 * horizontal_dist_to_parlor * self.times_milked_per_day
        
    def get_nutrient_rqmts(self):
        '''
        Returns this animal's nutrient requirements.
        Returns:
            self.nutrient_rqmts: dictionary which stores nutrient requirements
        '''
        return self.nutrient_rqmts
    
    def get_manure_excretion(self):
        '''
        Returns this animal's manure excretion.
        Returns:
            self.manure_excretion: dictionary which stores manure excretion
        '''
        return self.manure_excretion
    
    def get_daily_growth(self):
        '''
        Returns this animal's daily growth.
        Returns:
            self.daily_growth: number which stores daily growth
        '''
        return self.daily_growth
    
    def get_milk_production(self):
        '''
        Returns this animal's milk production.
        Returns:
            self.milk_production: number which stores milk production
        '''
        return self.milk_production
    
    def set_ration(self, ration_formulation):
        '''
        Sets this animal's ration formulation.
        Args:
            ration_formulation: dictionary representing the calculated ration
        '''
        self.ration_formulation = ration_formulation
        
    def calc_manure_excretion(self, feed):
        '''
        Calculates and sets the animal's manure excretion.
        '''
        # self.manure_excretion = manure_excretion.manure_calculations(this.ration_formulation, feed, BW, DIM, mPrt)
        pass
        
        
