################################################################################
'''
RUFAS: Ruminant Farm Systems Model
File name: pen.py
Description: The class which represents a pen on the farm.
Author(s): Militsa Sotirova, militsasotirova@gmail.com
'''
################################################################################
from animal_object import AnimalObject
#from RUFAS.routines.animal import ration

class Pen:
    #unique pen ID, from input file
    id = -1
    #list of all animals in this pen, dete
    animals_in_pen = []
    #list of all the classes to which the animals in the pen belong to
    classes_in_pen = []
    #distance to milking parlor, km, from input file
    dist_to_parlor = -1
    #number of stalls, from input file
    num_stalls = -1
    #stocking density of pen, calculated when animals in pen are updated in update_animals()
    stocking_density = -1
    #housing type of the pen, from input file
    housing_type = ""
    #bedding type of the pen, from input file
    bedding_type = ""
    #freestall or tiestall, from input file
    pen_type = "" 
    #average nutrient requirements of the animals in the pen
    avg_nutrient_rqmts = {}
    #ration for all the animals in the pen
    daily_ration = {}
    #total manure excretion of the animals in the pen
    manure = {}
    #average milk production of the animals in the pen
    avg_milk_production = -1
    #average growth of the animals in the pen
    avg_growth = -1
    
    def __init__(self, id, dist_to_parlor, num_stalls, housing_type, bedding_type, pen_type):
        '''
        Initializes a pen with the arguments. More information about each above.
        '''
        self.id = id
        self.dist_to_parlor = dist_to_parlor
        self.num_stalls = num_stalls
        self.housing_type = housing_type
        self.bedding_type = bedding_type
        self.pen_type = pen_type
    
    def update_animals(self, new_animals):
        '''
        Sets the list of animals to @new_animals and calculates the stocking density.
        Args:
            new_animals: list of new animals in the pen
        '''
        self.animals_in_pen = new_animals
        self.stocking_density = len(self.animals_in_pen) / self.num_stalls * 100 
        
    def calc_avg_nutrient_rqmts(self):
        '''
        Finds the average nutrient requirements of the animals in the pen.
        '''
        if (len(self.animals_in_pen) == 0):
            print('There are no animals in the pen with ID', self.id, '- cannot calculate average nutrient requirements.')
        
        sum_dict = {}
        for key in self.animals_in_pen[0].nutrient_rqmts.keys():
            sum_dict[key] = 0
        
        #find sums of nutrients for each animal in the pen
        for animal in self.animals_in_pen:
            for key in sum_dict.keys():
                sum_dict[key] += animal.nutrient_rqmts[key]['val']
                
        #divide by number of animals to find average
        num_animals = len(self.animals_in_pen)
        for key in sum_dict:
            avg_value = sum_dict[key]/ num_animals
            self.avg_nutrient_rqmts[key] = {'op': self.animals_in_pen[0].nutrient_rqmts[key]['op'], 'val': avg_value}
            
        print(self.avg_nutrient_rqmts)
    
    def calc_ration(self, feed):
        '''
        Calculates the ration for the pen using the average nutrient requirements.
        Args:
            feed: instance of the Feed class, used to determine characteristics of available feeds
        '''
        ration_per_animal = ration.optimize(feed, self.avg_nutrient_rqmts)
        num_animals = len(self.animals_in_pen)
        for key in ration_per_animal:
            if (key == 'status'):
                self.daily_ration[key] = ration_per_animal[key]
                
            else: #feeds and price
                self.daily_ration[key] = ration_per_animal[key] * num_animals
        
    def calc_manure(self):
        '''
        Calculates the total manure excretion of the animals in the pen.
        '''
        pass
    
    def calc_avg_milk(self):
        '''
        Calculates the average milk production of the animals in the pen.
        '''
        pass
    
    def calc_avg_growth(self):
        '''
        Calculates the average growth of the animals in the pen.
        '''
        pass
        









#Some test code 
p = Pen(9, 6, 4, "housing_type", "bedding_type", "pen_type")
animals = []
for i in range(0, 100):
    cow = AnimalObject(i, 9, 2)
    cow.calc_nutrient_rqmts()
    animals.append(cow)
    
p.update_animals(animals)

p.calc_avg_nutrient_rqmts()
    

    
    
    
    