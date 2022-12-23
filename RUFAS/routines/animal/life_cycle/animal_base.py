"""
RUFAS: Ruminant Farm Systems Model
File name: animal_base.py
Author(s): Manfei Li, mli497@wisc.edu
           Militsa Sotirova, militsasotrirova@gmail.com
           Tayler Hansen, tlhansen@cornell.edu
Description: This file initialize common parameters including ID, breed,
birth date, and age for all animals to be identified.
"""
###############################################################################

from RUFAS.routines.animal.life_cycle.animal_events import AnimalEvents


class PenHistory:
    def __init__(self, start, end, pen, classes_in_pen):
        self.start_date = start
        self.end_date = end
        self.pen = pen
        self.classes_in_pen = classes_in_pen


class BodyWeightHistory:
    def __init__(self, sim_day, days_born, body_weight):
        self.simulation_day = sim_day
        self.days_born = days_born
        self.body_weight = body_weight


class AnimalBase(object):
    config = {}
    nutrients = None

    @staticmethod
    def set_nutrient_list(nutrients):
        AnimalBase.nutrients = nutrients

    @staticmethod
    def set_config(config):
        AnimalBase.config = config

    def __init__(self, args):
        """
        Initializes common parameters for all animals
        Args:
            args.breed: breed of the cow
            args.birth_date: the date of the simulation when the calf was born
            args.days_born: age of the animal
            arg.semen_used: semen used in the dam for the calf
            (optional: include the following to assign animal information)
                        args.birth_weight: the birth weight of the animal
                        args.body_weight: current body weight of the animal
                        args.wean_weight: the wean weight of the animal
                        args.mature_body_weight: the mature body weight of the animal
                        args.events: events of the animal
        """
        self.id = args['id']
        self.breed = args['breed']
        self.birth_date = args['birth_date']
        self.days_born = args['days_born']
        self.semen_used = self.config['semen_type']

        self.culled = False
        self.do_not_breed = False
        self.body_weight_history = []
        self.events = AnimalEvents()
        self.pen_history = []
        self.daily_growth = 0
        self.nutrient_rqmts = {}
        self.set_default_nutrient_rqmts()
        self.dry_matter_intake = 0
        self.manure_excretion = {}
        self.ration_formulation = {'objective': 0.00}
        self.DMIest = 0
        #self.DBW = 0
        self.p_animal = 0
        self.p_intake = 0
        self.p_conc = 0
        self.p_excrt = 0
        self.birth_weight = 0
        self.body_weight = 0
        self.mature_body_weight = 0
        self.p_req = 0
        self.dP_reserves = 0
        self.p_excess = 0
        self.p_gest = 0
        self.p_growth = 0
        self.p_maint_feces = 0
        self.conceptus_weight = 0
        self.calf_birth_weight = 0
        self.tissue_changed = 0

        if 'body_weight_history' in args:
            self.body_weight_history = args['body_weight_history']
            self.pen_history = args['pen_history']
        if 'conceptus_weight' in args:
            self.conceptus_weight = args['conceptus_weight']
        if 'calf_birth_weight' in args:
            self.calf_birth_weight = args['calf_birth_weight']

    def set_default_nutrient_rqmts(self):
        """
        Sets the default nutrient requirement values to be 0.
        """
        for key in self.nutrients:
            self.nutrient_rqmts[key] = {'op': '', 'val': 0}

    def set_ration(self, ration, DMI):
        """
        Sets this animal's ration formulation.

        Args:
            ration: dictionary representing the calculated ration
            DMI: the dry matter intake from @ration
        """
        self.ration_formulation = ration
        self.dry_matter_intake = DMI

    def set_p_intake(self, p_intake, p_conc):
        """
        Sets this animal's phosphorus intake.

        Args:
            p_intake: the phosphorus intake
            p_conc: the concentration of P in the ration
        """
        self.p_intake = p_intake
        self.p_conc = p_conc

    def daily_p_update(self):
        """
        Calculates this animal's daily phosphorus update.
        """
        # Amount of P in diet greater than animal requirements (A.1G.A.1)
        self.p_excess = max(self.p_intake - self.p_req, 0)

        # change in body P reserves (g), must be <= 0 (A.1G.A.2)
        dP_reserves_prev = self.dP_reserves

        if self.p_intake < self.p_req:
            self.dP_reserves = self.p_intake - self.p_req + self.dP_reserves
        elif self.p_intake >= self.p_req and self.dP_reserves < 0:
            self.dP_reserves = 0.7 * self.p_excess + self.dP_reserves
        else:
            self.dP_reserves = 0

        # amount of P in the animal (A.1G.A.3)
        self.p_animal = self.p_animal + self.p_gest + self.p_growth + \
            (self.dP_reserves - dP_reserves_prev)

    def calc_base_manure(self):
        """
        Calculates the values needed for animal class manure calculations.

        Returns:
            p_urine: amount of P required for urine production (g)
            p_feces_excrt: amount of P excreted by an animal (g)
        """

        # amount of P required for urine production (g) (A.1G.B.1)
        p_urine = 0.000002 * self.body_weight * 1000

        # excess P in the diet (g) (A.1G.A.1)
        self.p_excess = max(self.p_intake - self.p_req, 0)


        # amount of P excreted by an animal (g) (A.1G.B.2)
        if self.dP_reserves == 0 and self.p_intake >= self.p_req:
            p_feces_excrt = self.p_intake - self.p_req + self.p_maint_feces
        elif self.dP_reserves < 0 and self.p_intake >= self.p_req and \
                self.p_excess >= (-1) * self.dP_reserves / 0.7:
            p_feces_excrt = self.p_intake - self.p_req + self.p_maint_feces + \
                self.dP_reserves / 0.7
        else:
            p_feces_excrt = self.p_maint_feces


        return p_urine, p_feces_excrt

    def set_p_purchased(self):
        """
        Sets this animal's phosphorus value as a purchased animal.
        """
        # (A.1G.C.1) from P tracking
        self.p_animal = 0.0072 * self.body_weight * 1000
        

    def update_pen_history(self, curr_pen, curr_day, classes_in_pen):
        """
        Updates the animal's pen history by either appending to the existing
        history if the animal is in a different pen than it was the last time
        this method is called or modifying the last element in the pen_history
        list to reflect the current simulation day.

        Args:
            curr_pen: the pen that the animal is currently in
            curr_day: the current simulation day
            classes_in_pen: the classes in the animal's current pen
        """
        last_pen = self.pen_history[-1].pen if len(
            self.pen_history) > 0 else None
        if last_pen is None or last_pen != curr_pen:
            self.pen_history.append(PenHistory(curr_day, curr_day, curr_pen,
                                               list(classes_in_pen)))
        else:  # last_pen == curr_pen
            self.pen_history[-1].end_date = curr_day
            self.pen_history[-1].classes_in_pen = list(classes_in_pen)

    def update_body_weight_history(self, sim_day):
        """
        Updates the animal's body weight history by appending a
        BodyWeightHistory object to the list.

        Args:
            sim_day: simulation day
        """
        self.body_weight_history.append(BodyWeightHistory(sim_day,
                                                          self.days_born,
                                                          self.body_weight))
