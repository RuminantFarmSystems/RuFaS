################################################################################
'''
RUFAS: Ruminant Farm Systems Model
File name: pen.py
Description: The class which represents a pen on the farm.
Author(s): Militsa Sotirova, militsasotirova@gmail.com
'''
################################################################################
from RUFAS.routines.animal.ration.lactating_cow_ration import optimize, set_globals


class Pen:
    # unique pen ID, from input file
    id = -1
    
    # list of all animals in this pen
    animals_in_pen = []
    
    # boolean: False if len(self.animals_in_pen) == 0 (i.e. there are no animals in the pen)
    pen_populated = False
    
    # set (no repeats) of all the classes to which the animals in the pen belong to
    classes_in_pen = set()
    
    # vertical distance to milking parlor, km, from input file
    vertical_dist_to_parlor = 0
    
    # horizontal distance to milking parlor, km, from input file
    horizontal_dist_to_parlor = 0
    
    # number of stalls, from input file
    num_stalls = 0
    
    # stocking density of pen, calculated when animals in pen are updated in update_animals()
    stocking_density = 0
    
    # housing type of the pen, from input file
    housing_type = ""
    
    # bedding type of the pen, from input file
    bedding_type = ""
    
    # freestall or tiestall, from input file
    pen_type = "" 
    
    # average nutrient requirements of the animals in the pen, used for ration formulation
    avg_nutrient_rqmts = {}
    
    # average body weight of the animals in the pen, used for ration formulation
    avg_BW = 0
    
    # average dry matter intake estimation of the animals in the pen, used for ration formulation
    avg_DMIest = 0
    
    # average change in (delta) body weight of the animals in the pen, used for ration formulation
    avg_DBW = 0
    
    # average milk production of the animals in the pen, used for (lactating cow) ration formulation
    avg_milk = 0
    
    # average milk crude protein content of the animals in the pen, used for (lactating cow) ration formulation
    avg_CP_milk = 0
    
    # ration for all the animals in the pen
    daily_ration = {}
    
    # total manure excretion of the animals in the pen
    manure = {}
    
    # average growth of the animals in the pen
    avg_growth = 0
    
    def __init__(self, id, vert_dist, horiz_dist, num_stalls, housing_type, bedding_type, pen_type):
        '''
        Initializes a pen with the arguments. More information about each above.
        '''
        self.id = id
        self.vertical_dist_to_parlor = vert_dist
        self.horizontal_dist_to_parlor = horiz_dist
        self.num_stalls = num_stalls
        self.housing_type = housing_type
        self.bedding_type = bedding_type
        self.pen_type = pen_type
    
    def update_animals(self, new_animals):
        '''
        Sets the list of animals to new_animals and calculates the stocking density and each animal's walking distance.
        Args:
            new_animals: list of new animals in the pen
        '''
        self.pen_populated = not (len(self.animals_in_pen) == 0)
        self.animals_in_pen = new_animals
        self.stocking_density = len(self.animals_in_pen) / self.num_stalls * 100 
        self.calc_daily_walking_dist()
        
        # sets the current animal classes in the pen
        for animal in self.animals_in_pen:
            stage = type(animal).__name__
            self.classes_in_pen.add(stage)
            
    def call_animal_nutrient_rqmts(self):
        '''
        Calls each animal's nutrient requirement calculation methods.
        '''
        for animal in self.animals_in_pen:
            animal.calc_nutrient_rqmts()
    
    def calc_avg_nutrient_rqmts(self):
        '''
        Finds the average nutrient requirements and necessary ration stats of the animals in the pen.
        '''
        first_animal_rqmts = self.animals_in_pen[0]._nutrient_rqmts
        sum_dict = {}
        for key in first_animal_rqmts.keys():
            sum_dict[key] = 0
        
        sum_BW = 0
        sum_DMIest = 0
        sum_DBW = 0
        sum_milk = 0
        sum_CP_milk = 0
        
        # find sums of nutrients and necessary ration stats for each animal in the pen
        for animal in self.animals_in_pen:
            curr_rqmts = animal._nutrient_rqmts
            for key in sum_dict.keys():
                sum_dict[key] += curr_rqmts[key]['val']
            
            sum_BW += animal._body_weight
            sum_DMIest += animal._DMIest
            sum_DBW += animal._DBW
            if type(animal).__name__ == 'Cow': 
                sum_milk += animal._estimated_daily_milk_produced
                sum_CP_milk += animal._CP_milk
                
        # divide by number of animals to find averages
        num_animals = len(self.animals_in_pen)
        for key in sum_dict:
            avg_value = sum_dict[key] / num_animals
            self.avg_nutrient_rqmts[key] = {'op': self.animals_in_pen[0]._nutrient_rqmts[key]['op'], 'val': avg_value}
            
        self.avg_BW = sum_BW / num_animals
        self.avg_DMIest = sum_DMIest / num_animals
        self.avg_DBW = sum_DBW / num_animals
        self.avg_milk = sum_milk / num_animals
        self.avg_CP_milk = sum_CP_milk / num_animals   
             
    def calc_ration(self, feed):
        '''
        Calculates the ration for the pen using the average nutrient requirements.
        Args:
            feed: instance of the Feed class, used to determine characteristics of available feeds
        '''
        # sets ration's necessary fields for ration formulation calculation
        set_globals(self.avg_DMIest, self.avg_BW, self.avg_DBW, self.avg_milk, self.avg_CP_milk)
        ration_per_animal = optimize(feed, self.avg_nutrient_rqmts)
        # TODO: if infeasible, recalculate with milk production reduced by 0.5 kg
        
        for animal in self.animals_in_pen:
            animal.set_ration(ration_per_animal)
            
        # set ration for whole pen by multiplying calculated ration by number of animals in the pen
        num_animals = len(self.animals_in_pen)
        for key in ration_per_animal:
            if (key == 'status'):
                self.daily_ration[key] = ration_per_animal[key]
                
            else:  # feeds and price
                self.daily_ration[key] = ration_per_animal[key] * num_animals
        
    def calc_manure(self, feed):
        '''
        Calculates the total manure excretion of the animals in the pen.
        '''
        for animal in self.animals_in_pen:
            animal.calc_manure_excretion(feed)
        
        #obtain keys of manure composition calculations
        first_animal_manure = self.animals_in_pen[0]._manure_excretion
        for key in first_animal_manure.keys():
            self.manure[key] = 0
        
        # find sums of manure components for each animal in the pen for total manure in pen
        for animal in self.animals_in_pen:
            curr_manure = animal._manure_excretion
            for key in self.manure.keys():
                self.manure[key] += curr_manure[key]
    
    def calc_avg_growth(self):
        '''
        Calculates the average growth of the animals in the pen.
        '''
        sum = 0
        for animal in self.animals_in_pen:
            sum += animal._daily_growth
        self.avg_growth = sum / len(self.animals_in_pen)
        
    def calc_daily_walking_dist(self):
        '''
        Sets the daily walking distance for cows.
        '''
        if 'Cow' in self.classes_in_pen:
            for animal in self.animals_in_pen:
                if type(animal).__name__ == 'Cow':
                    animal.calc_daily_walking_dist(self.vertical_dist_to_parlor, self.horizontal_dist_to_parlor)
            
    def clear(self):
        '''
        Clears the pen for re-allocation.
        '''
        self.animals_in_pen = []
        self.classes_in_pen = set()
        self.stocking_density = 0
        self.avg_nutrient_rqmts = {}
        self.avg_BW = 0
        self.avg_DMIest = 0
        self.avg_DBW = 0
        self.avg_milk = 0
        self.avg_CP_milk = 0
        self.daily_ration = {}
        self.manure = {}
        self.avg_growth = 0
