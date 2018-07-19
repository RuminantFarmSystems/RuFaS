import random
import numpy as np

    # initial a cow with ID
class Cow(object):
    ID = 0

    global next_id
    def next_id(self):
        Cow.ID = Cow.ID + 1
        return Cow.ID
    
    # define cow with weight, age, and type
    def __init__(self, mean, stv, cow_type, date, days_born=0):
        self.weight = np.random.normal(mean, stv)
        self.days_born = days_born
        self.type = cow_type
        self.birthday = date
        self.culled = False

        # Determine the sex of the cow 
        sex_rand = random.random()
        if sex_rand < 0.1:  
            self.sex = 'M'
        else:
            self.sex = 'F'

        if  self.sex == 'F':
            self.id = next_id(self)
            self.preg_days = -12
            self.concept_days = -1
            self.days_in_milk = -1
            self.next_estrus_date = -1
            self.num_birth = 0     # num of cattles born
            self.first_estrus = False   # First estrus after calving
    
    # sell male calve    
    def sold(self):
        return self.sex == 'M'

    def is_culled(self):
        return self.culled
        
    def is_preg(self):
        if (self.preg_days == -12):
            return False
        else:
            return True

    def is_milk(self):
        if (self.days_in_milk == -1):
            return False
        else:
            return True
    # weight gain with average daily gain
    def update(self, weight_increase):
        feed = self.weight * 0.03
        manure = 0.06 * self.weight

        self.days_born = self.days_born + 1 
        self.weight = self.weight + weight_increase

        return manure, feed