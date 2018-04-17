################################################################################
'''
RUFAS: Ruminant Farm Systems Model
File name: animal.py
Description:
Author(s): Kass Chupongstimun, kass_c@hotmail.com
'''
################################################################################

from RUFAS.routines.animal import ration

#-------------------------------------------------------------------------------
# Function: daily_animal_routine
#-------------------------------------------------------------------------------
def daily_animal_routine(animal, feed, weather, time):
    '''Executes daily routines relating to Animals.'''

    # Formulate ration using LP
    if not animal.user_input_ration:
        if animal.end_ration_interval(time.day):
            animal.formulate_optimized_ration(feed.all_feed, feed.feed_nutrition)

#-------------------------------------------------------------------------------
# Function: daily_animal_routine
#-------------------------------------------------------------------------------
def daily_animal_update(animal, weather, time):
    '''
    TODO: Add DocString
    '''
    pass

#-------------------------------------------------------------------------------
# Class: animal
#-------------------------------------------------------------------------------
class Animal():
    '''
    TODO: Add DocString
    '''

    def __init__(self, data):
        '''
        TODO: Add DocString
        '''

        self.housing = data['housing']
        self.user_input_ration = data['ration']['user_input']

        self.ration_formulation_interval = data['ration']['formulation_interval']

        #
        # ARE THESE DIRECT INPUTS OR INTERMEDIATES??????
        # Probably intermediates...
        #
        # HARD-CODED for now
        self.parity = 1.0
        self.WIM = 20.0
        self.AMF = 3.5
        self.BWR = 1.0
        self.base_NED = 1.0

        self.ration = {}

    #---------------------------------------------------------------------------
    # Method: formulate_optimized_ration
    #---------------------------------------------------------------------------
    def formulate_optimized_ration(self, feed, feed_nutrition):
        '''Formulates the least cost ration for the animals.

        1) Extract feed nutrition from Feed object
        2) Compile the information into the contraint and objective coefficients
           for the linear program
        3) Set up loop variables and enter formulation loop, for each loop,
           calculate requirements and linear program to solve for optimal
           solution. If the LP is not feasible, scale base milk production (in
           requirements) down by 5% and try again. Repeat until a feasible
           ration is found.
        '''

    #***************************************************************************
    # WARNING: EXTREMELY MESSY AND INTRACTABLE CODE BELOW
    #   I'M SORRY IF YOU HAVE TO TRY TO READ THIS
    #   WILL REFACTOR WHEN I HAVE TIME
    #   - Kass C.
    #***************************************************************************

        nutrients = feed_nutrition.keys()
        feed_types = feed.keys()

        # Constraints: minimum nutrition requirements for cows
        # values here are coefficients (on the LHS of the eq)
        #constraints = ration.calculate_constraints(feed, nutrients)
        constraints = {nutrient: [feed_nutrition[nutrient][feed_type] for feed_type in feed_types] for nutrient in nutrients}
        # Objective: minimize total cost of all feeds
        objective = {feed_type: feed[feed_type]['price'] for feed_type in feed_types}
        # Maximum allowed use for each feed type
        limits = {feed_type: feed[feed_type]['limit'] for feed_type in feed_types}

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
            # values here are requiremtnts (on the RHS of constraint eq)
            # milk_production_multiplier is passed as scaling factor
            #
            rqmts = ration.calculate_rqmts(
                self.parity, self.WIM, self.AMF, self.BWR, self.base_NED,
                self.housing, nutrients, milk_production_multiplier
            )
            formulated_ration = ration.optimize(
                constraints, rqmts, objective, limits, nutrients, feed_types
            )
            #
            # Ideally, we will use status == 'Infeasible', but due to bugs in
            # the GLPK routine outputting an 'Undefined' in some infeasible
            # cases, we have to just check for not optimal and re-iterate
            # accordingly
            #
            infeasible = (formulated_ration['status'] != 'Optimal')

        self.ration = formulated_ration
        self.ration['MP_reduction'] = milk_production_multiplier

    #---------------------------------------------------------------------------
    # Method: end_ration_interval
    #---------------------------------------------------------------------------
    def end_ration_interval(self, day):
        '''Checks whether it is the day to formulate a new ration.

        Returns:
            bool: True if today is the day a new ration has to be formulated,
                false otherwise.
        '''
        return (day % self.ration_formulation_interval) == 1

    #---------------------------------------------------------------------------
    # Method: annual_reset
    #---------------------------------------------------------------------------
    def annual_reset(self):
        '''
        TODO: Add DocString
        '''
        pass
