################################################################################
'''
RUFAS: Ruminant Farm Systems Model
File name: animal_management.py
Description: The class which manages all of the animal routines and keeps track of 
    all animals and pens.
Author(s): Militsa Sotirova, militsasotirova@gmail.com
'''
################################################################################
import pen, animal_object


class AnimalManagement:
    # list of all the animals in the simulations
    all_animals = []
    # list of all the pens on the farm
    all_pens = []
    
    def __init__(self, data):
        '''
        Initializes the pens and animals in the simulation with data from the json file.
        Args:
            data: dictionary with the animal information from the input json file
        '''
        init_pens(data['penInformation'])
        init_animals(data['Herd'])
        
    def init_pens(self, data):
        '''
        Populates the list of pens with the information from the input json file.
        Args:
            data: dictionary with the pen information from the input json file
        '''
        for penName in data:
            id = penName["id"]
            dist_to_parlor = penName["walking_dist_to_milking_parlor"]
            num_stalls = penName["number_of_stalls"]
            housing_type = penName["housing_type"]
            bedding_type = penName["bedding_type"]
            pen_type = penName["pen_type"]
            pen = Pen(id, dist_to_parlor, num_stalls, housing_type, bedding_type, pen_type)
            all_pens.append(pen) 
    
    def init_animals(self, data):
        '''
        Populates the list of animnals with the information from the input json file.
        Args:
            data: dictionary with the herd information from the input json file
        '''
        pass
    
    def calc_nutrient_rqmts(self):
        '''
        Calls each animal's method to calculate its nutrient requirements.
        '''
        for animal in self.all_animals:
            animal.calc_nutrient_rqmts()
    
    def pen_allocation(self):
        '''
        Allocates the animals in all_animals to pens in all_pens based on the animals' characteristics.
        '''
        pass
      
    def calc_avg_nutrient_rqmts(self):
        '''
        Calls each pens's method to calculate the average nutrient requirements of the animals inside.
        '''
        for pen in self.all_pens:
            pen.calc_avg_nutrient_rqmts()
    
    def calc_ration(self, feed):
        '''
        Calls each pens's method to calculate the ration for that pen.
        Args:
            feed: instance of the Feed class, used to determine characteristics of available feeds
        '''
        for pen in self.all_pens:
            pen.calc_ration(feed)
    
    def calc_manure_excretion(self):
        '''
        Calls each animal's method to calculate manure excretion to find the total for each pen.
        '''
        pass
    
    def calc_avg_milk(self):
        '''
        Calls each pen's method to calculate the average milk production of animals in the pen. 
        '''
        for pen in self.all_pens:
            pen.calc_avg_milk()
    
    def calc_avg_growth(self):
        '''
        Calls each pen's method to calculate the average growth of animals in the pen. 
        '''
        for pen in self.all_pens:
            pen.calc_avg_growth()
    
    def daily_action(self):
        # placeholder for method call to life cycle update to update animal states
        calc_nutrient_rqmts()  # per animal
        pen_allocation()
        calc_avg_nutrient_rqmts()  # per pen
        calc_ration()  # per pen
        calc_manure_excretion()  # per pen
        calc_avg_milk()  # per pen
        calc_avg_growth()  # per pen
    
