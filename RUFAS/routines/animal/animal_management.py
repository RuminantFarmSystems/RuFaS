################################################################################
'''
RUFAS: Ruminant Farm Systems Model
File name: animal_management.py
Description: The class which manages all of the animal routines and keeps track of
    all animals and pens. All operations are as described in the Animal Module
    Information Flow document on Basecamp (such as daily animal updates and
    pen allocation). Method calls cascade through from the animal management
    class to pen to each individual animal in that pen. The life cycle of each animal
    is controlled by an instance of the LifeCycleManager class, and this instance
    updates the animals daily.
Author(s): Militsa Sotirova, militsasotirova@gmail.com
'''
################################################################################
from RUFAS.routines.animal.pen import Pen
from RUFAS.routines.animal.clustering_pen_grouping import grouping
from RUFAS.routines.animal.life_cycle.life_cycle import LifeCycleManager
from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase

def daily_animal_routine(animal_management, feed, weather, time):
    '''Executes daily routines relating to Animals.

    Args:
        animal : instance of the Animal class
        feed : instance of the Feed class
        weather : instance of the Weather class
        time : instance of the Time class
    '''
    animal_management.daily_updates(feed, time)


def daily_animal_update(animal, weather, time):
    pass


class AnimalManagement:
    # list of all the animals in the simulations
    calves = []
    heiferIs = []
    heiferIIs = []
    heiferIIIs = []
    cows = []

    # list of all the pens on the farm
    all_pens = []

    # simulation length, days
    sim_length = -1

    # instance of LifeCycleManager class
    life_cycle_manager = None

    # housing type: barn or pasture
    housing = ""

    # concentrate supplementation when farming type is "pasture", kg
    pasture_concentrate = -1

    ration_user_input = False

    # how often a ration is calculated, days
    formulation_interval = 0

    # day in the simulation
    simulation_day = 0

    # if False, there are no animals being simulated on the farm
    simulate_animals = False

    def __init__(self, data, config, feed):
        '''
        Initializes the pens and animals in the simulation with data from the json file.
        Args:
            data: dictionary with the animal information from the input json file
        '''
        self.sim_length = config.sim_length
        self.life_cycle_manager = LifeCycleManager(data['animal_config'])
        AnimalBase.set_config(data['animal_config'])
        AnimalBase.set_nutrient_list(feed.nutrient_rqmts)
        self.init_pens(data['pen_information'])
        self.init_animals(data['herd_information'], feed)
        self.housing = data['housing']
        self.pasture_concentrate = data['pasture_concentrate']
        self.ration_user_input = data['ration']['user_input']
        self.formulation_interval = data['ration']['formulation_interval']

    def init_pens(self, data):
        '''
        Populates the list of pens with the information from the input json file.
        Args:
            data: dictionary with the pen information from the input json file
        '''
        for pen_name in data:
            pen_data = data[pen_name]
            pen_id = pen_data['id']
            vertical_dist_to_parlor = pen_data['vertical_dist_to_milking_parlor']
            horizontal_dist_to_parlor = pen_data['horizontal_dist_to_milking_parlor']
            num_stalls = pen_data['number_of_stalls']
            housing_type = pen_data['housing_type']
            bedding_type = pen_data['bedding_type']
            pen_type = pen_data['pen_type']
            pen = Pen(pen_id, vertical_dist_to_parlor, horizontal_dist_to_parlor, num_stalls, housing_type, bedding_type, pen_type)
            self.all_pens.append(pen)

    def init_animals(self, data, feed):
        '''
        Populates the list of animals with the information from the input json file.
        Args:
            data: dictionary with the herd information from the input json file
        '''
        calf_num = data['calf_num']
        heiferI_num = data['heiferI_num']
        heiferII_num = data['heiferII_num']
        heiferIII_num = data['heiferIII_num']
        cow_num = data['cow_num']
        replace_num = data['replace_num']
        herd_num = data['herd_num']

        if herd_num == 0:
            self.simulate_animals = False
            print("herd_num is 0 -> no animals will be simulated")
            if not calf_num == 0:
                print("Warning: herd_num is 0, but calf_num is not. Setting calf_num = 0.")
                calf_num = 0
            if not heiferI_num == 0:
                print("Warning: herd_num is 0, but heiferI_num is not. Setting heiferI_num = 0.")
                heiferI_num = 0
            if not heiferII_num == 0:
                print("Warning: herd_num is 0, but heiferII_num is not. Setting heiferII_num = 0.")
                heiferII_num = 0
            if not heiferIII_num == 0:
                print("Warning: herd_num is 0, but heiferIII_num is not. Setting heiferIII_num = 0.")
                heiferIII_num = 0
            if not cow_num == 0:
                print("Warning: herd_num is 0, but cow_num is not. Setting cow_num = 0.")
                cow_num = 0
        else:
            self.simulate_animals = True

        self.life_cycle_manager.initialize_herd(herd_num, calf_num, heiferI_num, heiferII_num, heiferIII_num, cow_num, replace_num)
        self.calves = self.life_cycle_manager.calves
        self.heiferIs = self.life_cycle_manager.heiferIs
        self.heiferIIs = self.life_cycle_manager.heiferIIs
        self.heiferIIIs = self.life_cycle_manager.heiferIIIs
        self.cows = self.life_cycle_manager.cows
        self.init_nutrient_rqmts(feed)
        self.pen_allocation()

    def init_nutrient_rqmts(self, feed):
        '''
        Calculates initial nutrient requirements at the beginning of the simulation for initial pen allocation.
        '''
        # average vertical & horizontal distance (VD, HD) of pens to milking parlor
        avg_VD_parlor, avg_HD_parlor = self.avg_pen_dist()

        for calf in self.calves:
            calf.calc_nutrient_rqmts()

        for heiferI in self.heiferIs:
            heiferI.calc_nutrient_rqmts()

        for heiferII in self.heiferIIs:
            heiferII.calc_nutrient_rqmts()

        for heiferIII in self.heiferIIIs:
            heiferIII.calc_nutrient_rqmts()

        for cow in self.cows:
            # uses average distances from pens to milking parlor
            cow.calc_init_nutrient_rqmts(avg_VD_parlor, avg_HD_parlor, self.housing, self.pasture_concentrate, feed)

    def avg_pen_dist(self):
        '''
        Calculates the average distance from a pen to the milking parlor.
        Returns:
            average vertical distance from milking parlor
            average horizontal distance from milking parlor
        '''
        # vertical distance
        VD_sum = 0

        # horizontal distance
        HD_sum = 0
        for pen in self.all_pens:
            VD_sum += pen.vertical_dist_to_parlor
            HD_sum += pen.horizontal_dist_to_parlor

        return VD_sum / len(self.all_pens), HD_sum / len(self.all_pens)

    def calc_nutrient_rqmts(self, feed):
        '''
        Calls each animal's method to calculate its nutrient requirements.
        '''
        for pen in self.all_pens:
            pen.call_animal_nutrient_rqmts(self.housing, self.pasture_concentrate, feed)

    def pen_allocation(self):
        '''
        Allocates the animals in all_animals to pens in all_pens based on the animals' characteristics.
        TEMPORARY HARD-CODE FOR TESTING PURPOSES.
        '''

        self.all_pens[0].update_animals(self.calves)
        self.all_pens[1].update_animals(self.heiferIs)
        self.all_pens[2].update_animals(self.heiferIIs)
        self.all_pens[3].update_animals(self.heiferIIIs)

        #separate into lactating and dry cow pens
        lactating_cows = []
        dry_cows = []

        for cow in self.cows:
            if cow._milking:
                lactating_cows.append(cow)
            else:
                dry_cows.append(cow)
        self.all_pens[4].update_animals(dry_cows)

        for i in range(len(lactating_cows)):
            lactating_cows[i].ID = i + 1

        df = grouping(lactating_cows)
        if isinstance(df, list):
            cows_2 = []
            cows_3 = []
            cows_4 = []
            cows_6 = []
            cows_7 = []
            cows_8 = []
            cows_9 = []
            cows_22 = []
            cows_23 = []
            cows_24 = []
            cows_25 = []
            cows_26 = []
            cows_27 = []
            cows_28 = []

            for i in range(len(df[0]) - 1):
                ID = df[0][i]
                if df[1][i] == 2:
                    cows_2.append(lactating_cows[df[0][i] - 1])
                elif df[1][i] == 3:
                    cows_3.append(lactating_cows[df[0][i] - 1])
                elif df[1][i] == 4:
                    cows_4.append(lactating_cows[df[0][i] - 1])
                elif df[1][i] == 6:
                    cows_6.append(lactating_cows[df[0][i] - 1])
                elif df[1][i] == 7:
                    cows_7.append(lactating_cows[df[0][i] - 1])
                elif df[1][i] == 8:
                    cows_8.append(lactating_cows[df[0][i] - 1])
                elif df[1][i] == 9:
                    cows_9.append(lactating_cows[df[0][i] - 1])
                elif df[1][i] == 22:
                    cows_22.append(lactating_cows[df[0][i] - 1])
                elif df[1][i] == 23:
                    cows_23.append(lactating_cows[df[0][i] - 1])
                elif df[1][i] == 24:
                    cows_24.append(lactating_cows[df[0][i] - 1])
                elif df[1][i] == 25:
                    cows_25.append(lactating_cows[df[0][i] - 1])
                elif df[1][i] == 26:
                    cows_26.append(lactating_cows[df[0][i] - 1])
                elif df[1][i] == 27:
                    cows_27.append(lactating_cows[df[0][i] - 1])
                else:
                    cows_28.append(lactating_cows[df[0][i] - 1])


            #allocation of lactating cows into pens (based on number of pens available)

            n = len(self.all_pens)

            if n == 8:
                #combining groupings of cows with similar ration requirments
                #due to sparsity of pens
                lactating_group_1 = cows_2 + cows_3 + cows_4 + cows_6 + cows_7 + cows_8 + cows_9
                lactating_group_2 = cows_22 + cows_23 + cows_24 + cows_25
                lactating_group_3 = cows_26 + cows_27 + cows_28
                self.all_pens[5].update_animals(lactating_group_1)
                self.all_pens[6].update_animals(lactating_group_2)
                self.all_pens[7].update_animals(lactating_group_3)

            elif n == 9:
                #combining groupings of cows with similar ration requirments
                #due to sparsity of pens
                lactating_group_1 = cows_2 + cows_3 + cows_4 + cows_6
                lactating_group_2 = cows_7 + cows_8 + cows_9
                lactating_group_3 = cows_22 + cows_23 + cows_24
                lactating_group_4 = cows_25 + cows_26 + cows_27 + cows_28
                self.all_pens[5].update_animals(lactating_group_1)
                self.all_pens[6].update_animals(lactating_group_2)
                self.all_pens[7].update_animals(lactating_group_3)
                self.all_pens[8].update_animals(lactating_group_4)

            elif n == 10:
                #combining groupings of cows with similar ration requirments
                #due to sparsity of pens
                lactating_group_1 = cows_2 + cows_3 + cows_4 + cows_6
                lactating_group_2 = cows_7 + cows_8 + cows_9
                lactating_group_3 = cows_22 + cows_23 + cows_24
                lactating_group_4 = cows_25 + cows_26
                lactating_group_5 = cows_27 + cows_28
                self.all_pens[5].update_animals(lactating_group_1)
                self.all_pens[6].update_animals(lactating_group_2)
                self.all_pens[7].update_animals(lactating_group_3)
                self.all_pens[8].update_animals(lactating_group_4)
                self.all_pens[9].update_animals(lactating_group_5)

            elif n == 11:
                #combining groupings of cows with similar ration requirments
                #due to sparsity of pens
                lactating_group_1 = cows_2 + cows_3 + cows_4 + cows_6
                lactating_group_2 = cows_7 + cows_8
                lactating_group_3 = cows_9
                lactating_group_4 = cows_22 + cows_23 + cows_24
                lactating_group_5 = cows_25 + cows_26
                lactating_group_6 = cows_27 + cows_28
                self.all_pens[5].update_animals(lactating_group_1)
                self.all_pens[6].update_animals(lactating_group_2)
                self.all_pens[7].update_animals(lactating_group_3)
                self.all_pens[8].update_animals(lactating_group_4)
                self.all_pens[9].update_animals(lactating_group_5)
                self.all_pens[10].update_animals(lactating_group_6)

            elif n == 12:
                #combining groupings of cows with similar ration requirments
                #due to sparsity of pens
                lactating_group_1 = cows_2 + cows_3 + cows_4
                lactating_group_2 = cows_7 + cows_6
                lactating_group_3 = cows_8
                lactating_group_4 = cows_9
                lactating_group_5 = cows_22 + cows_23 + cows_24
                lactating_group_6 = cows_25 + cows_26
                lactating_group_7 = cows_27 + cows_28
                self.all_pens[5].update_animals(lactating_group_1)
                self.all_pens[6].update_animals(lactating_group_2)
                self.all_pens[7].update_animals(lactating_group_3)
                self.all_pens[8].update_animals(lactating_group_4)
                self.all_pens[9].update_animals(lactating_group_5)
                self.all_pens[10].update_animals(lactating_group_6)
                self.all_pens[11].update_animals(lactating_group_7)

            elif n == 13:
                #combining groupings of cows with similar ration requirments
                #due to sparsity of pens
                lactating_group_1 = cows_2 + cows_3 + cows_4
                lactating_group_2 = cows_7 + cows_6
                lactating_group_3 = cows_8
                lactating_group_4 = cows_9
                lactating_group_5 = cows_22 + cows_23
                lactating_group_6 = cows_24
                lactating_group_7 = cows_25 + cows_26
                lactating_group_8 = cows_27 + cows_28
                self.all_pens[5].update_animals(lactating_group_1)
                self.all_pens[6].update_animals(lactating_group_2)
                self.all_pens[7].update_animals(lactating_group_3)
                self.all_pens[8].update_animals(lactating_group_4)
                self.all_pens[9].update_animals(lactating_group_5)
                self.all_pens[10].update_animals(lactating_group_6)
                self.all_pens[11].update_animals(lactating_group_7)
                self.all_pens[12].update_animals(lactating_group_8)

            elif n == 14:
                #combining groupings of cows with similar ration requirments
                #due to sparsity of pens
                lactating_group_1 = cows_2 + cows_3 + cows_4
                lactating_group_2 = cows_7 + cows_6
                lactating_group_3 = cows_8
                lactating_group_4 = cows_9
                lactating_group_5 = cows_22 + cows_23
                lactating_group_6 = cows_24
                lactating_group_7 = cows_25
                lactating_group_8 = cows_26
                lactating_group_9 = cows_27 + cows_28
                self.all_pens[5].update_animals(lactating_group_1)
                self.all_pens[6].update_animals(lactating_group_2)
                self.all_pens[7].update_animals(lactating_group_3)
                self.all_pens[8].update_animals(lactating_group_4)
                self.all_pens[9].update_animals(lactating_group_5)
                self.all_pens[10].update_animals(lactating_group_6)
                self.all_pens[11].update_animals(lactating_group_7)
                self.all_pens[12].update_animals(lactating_group_8)
                self.all_pens[13].update_animals(lactating_group_9)

            elif n == 15:
                #combining groupings of cows with similar ration requirments
                #due to sparsity of pens
                lactating_group_1 = cows_2 + cows_3 + cows_4
                lactating_group_2 = cows_7 + cows_6
                lactating_group_3 = cows_22 + cows_23


                self.all_pens[5].update_animals(lactating_group_1)
                self.all_pens[6].update_animals(lactating_group_2)
                self.all_pens[7].update_animals(cows_8)
                self.all_pens[8].update_animals(cows_9)
                self.all_pens[9].update_animals(lactating_group_3)
                self.all_pens[10].update_animals(cows_24)
                self.all_pens[11].update_animals(cows_25)
                self.all_pens[12].update_animals(cows_26)
                self.all_pens[13].update_animals(cows_27)
                self.all_pens[14].update_animals(cows_28)

            elif n == 16:
                #combining groupings of cows with similar ration requirments
                #due to sparsity of pens
                lactating_group_1 = cows_2 + cows_3 + cows_4
                lactating_group_2 = cows_7 + cows_6

                self.all_pens[5].update_animals(lactating_group_1)
                self.all_pens[6].update_animals(lactating_group_2)
                self.all_pens[7].update_animals(cows_8)
                self.all_pens[8].update_animals(cows_9)
                self.all_pens[9].update_animals(cows_22)
                self.all_pens[10].update_animals(cows_23)
                self.all_pens[11].update_animals(cows_24)
                self.all_pens[12].update_animals(cows_25)
                self.all_pens[13].update_animals(cows_26)
                self.all_pens[14].update_animals(cows_27)
                self.all_pens[15].update_animals(cows_28)

            elif n == 17:
                #combining groupings of cows with similar ration requirments
                #due to sparsity of pens
                lactating_group_1 = cows_2 + cows_3 + cows_4

                self.all_pens[5].update_animals(lactating_group_1)
                self.all_pens[6].update_animals(cows_6)
                self.all_pens[7].update_animals(cows_7)
                self.all_pens[8].update_animals(cows_8)
                self.all_pens[9].update_animals(cows_9)
                self.all_pens[10].update_animals(cows_22)
                self.all_pens[11].update_animals(cows_23)
                self.all_pens[12].update_animals(cows_24)
                self.all_pens[13].update_animals(cows_25)
                self.all_pens[14].update_animals(cows_26)
                self.all_pens[15].update_animals(cows_27)
                self.all_pens[16].update_animals(cows_28)

            elif n == 18:
                lactating_group_1 = cows_2 + cows_2
                self.all_pens[5].update_animals(lactating_group_1)
                self.all_pens[6].update_animals(cows_4)
                self.all_pens[7].update_animals(cows_6)
                self.all_pens[8].update_animals(cows_7)
                self.all_pens[9].update_animals(cows_8)
                self.all_pens[10].update_animals(cows_9)
                self.all_pens[11].update_animals(cows_22)
                self.all_pens[12].update_animals(cows_23)
                self.all_pens[13].update_animals(cows_24)
                self.all_pens[14].update_animals(cows_25)
                self.all_pens[15].update_animals(cows_26)
                self.all_pens[16].update_animals(cows_27)
                self.all_pens[17].update_animals(cows_28)


            else:
                self.all_pens[5].update_animals(cows_2)
                self.all_pens[6].update_animals(cows_3)
                self.all_pens[7].update_animals(cows_4)
                self.all_pens[8].update_animals(cows_6)
                self.all_pens[9].update_animals(cows_7)
                self.all_pens[10].update_animals(cows_8)
                self.all_pens[11].update_animals(cows_9)
                self.all_pens[12].update_animals(cows_22)
                self.all_pens[13].update_animals(cows_23)
                self.all_pens[14].update_animals(cows_24)
                self.all_pens[15].update_animals(cows_25)
                self.all_pens[16].update_animals(cows_26)
                self.all_pens[17].update_animals(cows_27)
                self.all_pens[18].update_animals(cows_28)


        #if len(lactating_cows) > 10:
        #    print(len(lactating_cows))
        #    lactating_cows[117789]
    #def pen_grouping(self):
    #    cows = self.all_pens[5]
    #    for i in range(len(cows)):
    #        cows[i].ID = i + 1


    def clear_pens(self):
        '''
        Removes animals from pens for re-allocation.
        '''
        for pen in self.all_pens:
            pen.clear()

    def calc_avg_nutrient_rqmts(self):
        '''
        Calls each pens's method to calculate the average nutrient requirements of the animals inside.
        '''
        for pen in self.all_pens:
            if pen.pen_populated:
                pen.calc_avg_nutrient_rqmts()

    def calc_ration(self, feed):
        '''
        Calls each pens's method to calculate the ration for that pen.
        Args:
            feed: instance of the Feed class, used to determine characteristics of available feeds
        '''
        for pen in self.all_pens:
            if pen.pen_populated:
                pen.calc_ration(self.housing, self.pasture_concentrate, feed)

    def calc_manure_excretion(self, feed):
        '''
        Calls each animal's method to calculate manure excretion to find the total for each pen.
        '''
        for pen in self.all_pens:
            if pen.pen_populated:
                pen.calc_manure(feed)

    def calc_avg_growth(self):
        '''
        Calls each pen's method to calculate the average growth of animals in the pen.
        '''
        for pen in self.all_pens:
            if pen.pen_populated:
                pen.calc_avg_growth()

    def daily_updates(self, feed, time):
        '''
        Executes daily routines relating to Animals.
        Args:
            feed : instance of the Feed class
            time : instance of the Time class
        '''
        if self.simulate_animals:
            self.life_cycle_manager.daily_update(self.simulation_day, self.sim_length)

            if self.end_ration_interval():
                self.calc_nutrient_rqmts(feed)  # per animal, new requirements calculated based on previous ration interval's housing
                self.clear_pens()
                self.pen_allocation()
                self.calc_avg_nutrient_rqmts()  # per pen
                self.calc_ration(feed)  # per pen
                self.calc_manure_excretion(feed)  # per pen
                self.calc_avg_growth()  # per pen

        # other daily actions

    def end_ration_interval(self):
        '''Checks whether it is the day to formulate a new ration.

        Returns:
            bool: True if today is the day a new ration has to be formulated,
                false otherwise.
        '''
        return (self.simulation_day % self.formulation_interval) == 1 or self.formulation_interval == 1

    def annual_reset(self):
        pass
