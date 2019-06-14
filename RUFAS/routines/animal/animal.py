################################################################################
"""
RUFAS: Ruminant Farm Systems Model
File name: animal.py
Description:
Author(s): Kass Chupongstimun, kass_c@hotmail.com
"""
################################################################################

from RUFAS.routines.animal import ration, Herd, testing_ration

#-------------------------------------------------------------------------------
# Function: daily_animal_routine
#-------------------------------------------------------------------------------
def daily_animal_routine(animal, feed, weather, time):
    """Executes daily routines relating to Animals.

    Args:
        animal : instance of the Animal class
        feed : instance of the Feed class
        weather : instance of the Weather class
        time : instance of the Time class
    """

    # Formulate ration using LP
    if not animal.has_user_input_ration:
        if animal.end_ration_interval(time.day):
            animal.formulate_optimized_ration(feed)
    animal.herd.daily_update(time)

#-------------------------------------------------------------------------------
# Function: daily_animal_routine
#-------------------------------------------------------------------------------
def daily_animal_update(animal, weather, time):
    """
    TODO: Add DocString
    """
    pass

#-------------------------------------------------------------------------------
# Class: animal
#-------------------------------------------------------------------------------
class Animal():
    """
    Currently represents a Cow.
    """

    def __init__(self, data):
        """
        Constructs an instance of the Animal class

        Args:
            data : 2D dictionary which stores information about the cow
        """
        self.herd = Herd.Herd(data["Herd"])
        self.housing = data['housing']
        self.has_user_input_ration = data['ration']['user_input']

        self.ration_formulation_interval = data['ration']['formulation_interval']

        #
        # ARE THESE DIRECT INPUTS OR INTERMEDIATES??????
        # Probably intermediates...
        #
        # HARD-CODED for now
        self.parity = 1.0
        self.WIM = 20.0 # Week in milk
        self.AMF = 3.5
        self.BWR = 1.0
        self.base_NED = 1.0

        self.ration = {}

    #---------------------------------------------------------------------------
    # Method: formulate_optimized_ration
    #---------------------------------------------------------------------------
    def formulate_optimized_ration(self, feed):
        """Formulates the least cost ration for the animals.

        1) Extract feed nutrition from Feed object
        2) Compile the information into the constraint and objective coefficients
           for the linear program
        3) Set up loop variables and enter formulation loop, for each loop,
           calculate requirements and linear program to solve for optimal
           solution. If the LP is not feasible, scale base milk production (in
           requirements) down by 5% and try again. Repeat until a feasible
           ration is found.

        Args:
            feed : instance of the Feed class
        """

        # Loop variables
        infeasible = True
        # scaling factor for base_MY (milk production figure)
        milk_production_power = -1

        #
        # Loop until ration formulation is feasible
        # If not feasible, scale down milk production figure (base_MY)
        # and try again
        # base_MY is scaled down by 5% for every iteration
        #
        while infeasible:
            milk_production_power += 1
            milk_production_multiplier = 0.95**milk_production_power

            #
            # Constraints: minimum nutrition requirements for cows
            # values here are requirements (on the RHS of constraint eq)
            # milk_production_multiplier is passed as scaling factor
            #
            '''rqmts = ration.calculate_rqmts(
                self.parity, self.WIM, self.AMF, self.BWR, self.base_NED,
                self.housing, feed.nutrients_in_LP, milk_production_multiplier
            )
            formulated_ration = ration.optimize(feed, rqmts)'''
            #
            # Ideally, we will use status == 'Infeasible', but due to bugs in
            # the GLPK routine outputting an 'Undefined' in some infeasible
            # cases, we have to just check for not optimal and re-iterate
            # accordingly
            #
            formulated_ration = testing_ration.test_ration(feed)
            infeasible = (formulated_ration['status'] != 'Optimal')

        self.ration = formulated_ration
        self.ration['MP_reduction'] = milk_production_multiplier

    #---------------------------------------------------------------------------
    # Method: end_ration_interval
    #---------------------------------------------------------------------------
    def end_ration_interval(self, day):
        """Checks whether it is the day to formulate a new ration.

        Returns:
            bool: True if today is the day a new ration has to be formulated,
                false otherwise.
        """
        return (day % self.ration_formulation_interval) == 1 or self.ration_formulation_interval == 1

    #---------------------------------------------------------------------------
    # Method: annual_reset
    #---------------------------------------------------------------------------
    def annual_reset(self):
        """
        TODO: Add DocString
        """
        pass
