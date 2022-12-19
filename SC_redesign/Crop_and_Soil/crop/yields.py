from math import exp

"""
This module is based upon the "Crop Yield" section of the SWAT model (5.2.4)
"""

class Yields():
    def __init__(self):
        self.heat_fraction = 0.6  # also in root_development.py
        self.optimal_harvest_index = 3.5
        self.water_deficiency = 0.2  # also in water_dynamics.py
        self.min_harvest_index = 0.2
        self.is_mature = True
        self.above_ground_biomass = 15  # kg
        self.dry_down_percent = 0.2

        self.potential_harvest_index = None
        self.harvest_index = None

    def obtain_yields(self):
        self.potential_harvest_index = self.determine_potential_harvest_index(self.heat_fraction,
                                                                             self.optimal_harvest_index)
        self.harvest_index = self.adjust_harvest_index(self.potential_harvest_index,
                                                       self.min_harvest_index,
                                                       self.water_deficiency)
        self.above_ground_biomass = self.adjust_biomass_for_dry_down(self.above_ground_biomass, self.dry_down_percent)
        #
        # if crop_type.fr_PHU > 1.0:
        #     calc_dry_down(crop_type)
        #
        # calc_yield_max(crop_type)
        # calc_yield_act(crop_type)
        # calc_harvest_quality(crop_type)
        # calc_nutrient_removal(crop_type)
        # calc_residue(soil, crop_type, field_management, time)
        # calc_quality_assessment(crop_type)
        pass

    @staticmethod
    def determine_potential_harvest_index(heat_fraction, optimal_harvest_index):
        """calculates the potential harvest index for a plant on a given day

        Args:
            heat_fraction: fraction of potential heat units
            optimal_harvest_index: potential harvest index for the plant at maturity under ideal conditions

        SWAT Reference: 5:2.4.1

        Returns: potential harvest index for the day
        """
        heat_percent = 100 * heat_fraction
        return optimal_harvest_index * heat_percent / (heat_percent + exp(11.1 - 10 * heat_fraction))

    @staticmethod
    def adjust_harvest_index(harvest_index: float, min_harvest_index: float, water_deficiency: float) -> float:
        """calculates the actual harvest index for a given day, adjusted for water deficiency

        Args:
            min_harvest_index: harvest index in drought conditions; minimum possible harvest index for the plant,
                [0, Inf)
            harvest_index: potential harvest index for the day, [min_harvest_index, Inf)
            water_deficiency: water deficiency factor for the plant

        Details: values of min_harvest_index and harvest_index are input below their bounds, they are updated to
        equal their lower bounds.

        SWAT Reference:

        Returns: actual harvest index
        """
        harvest_index = max(harvest_index, 0)  # bound to zero
        harvest_index = max(harvest_index, min_harvest_index)  # prevent harvest_index < min_harvest_index

        adj_harvest_index = (harvest_index - min_harvest_index) * water_deficiency / \
                            (water_deficiency + exp(6.13 - 0.883 * water_deficiency)) + min_harvest_index
        return max(adj_harvest_index, 0)  # bound to zero

    @staticmethod
    def adjust_biomass_for_dry_down(above_ground_biomass: float, dry_down_percent: float) -> float:
        # TODO: stand in for more sophisticated dry down method - GitHub Issue #162
        """ calculates the above ground biomass after water mass is lost in dry-down

        Args:
             above_ground_biomass: plant biomass stored above ground (non-root biomass)
             dry_down_percent: mass lost as water during dry-down, as a percentage of above ground biomass.

        Returns: the above ground biomass, after dry-down
        """
        return above_ground_biomass - (above_ground_biomass * dry_down_percent)




# -- OLD
# def update_all(soil, crop_type, field_management, time):
#     """
#     Description:
#         Runs all the yield calculations
#
#     Args:
#         soil: an instance of the Soil class specified in soil.py representing
#             the current state of the soil profile
#         crop_type: an instance of a crop class
#         field_management: an instance of the FieldManagement class
#             specified in field_management.py
#         time: an instance of the Time class specified in classes.py
#     """
#
#
#     calc_HI_max(crop_type)
#     calc_HI_act(crop_type)
#
#     if crop_type.fr_PHU > 1.0:
#         calc_dry_down(crop_type)
#
#     calc_yield_max(crop_type)
#     calc_yield_act(crop_type)
#     calc_harvest_quality(crop_type)
#     calc_nutrient_removal(crop_type)
#     calc_residue(soil, crop_type, field_management, time)
#     calc_quality_assessment(crop_type)
#
#
#
#
#     # top = 100 * crop_type.fr_PHU
#     # bottom = 100 * crop_type.fr_PHU + exp(11.1 - (10 * crop_type.fr_PHU))
#     # crop_type.HI_max = crop_type.HI_opt * top / bottom
#

#
#
# def calc_yield_max(crop_type):
#     """
#     Description:
#         Calculates maximum crop yield at harvest.
#         "pseudocode_crop" C.10.D.1
#
#     Args:
#         crop_type: an instance of a crop class
#     """
#
#     crop_type.yield_max = crop_type.bio_AG * crop_type.HI_actual
#
#
# def calc_yield_act(crop_type):
#     """
#     Description:
#         Calculates actual crop yield at harvest.
#         "pseudocode_crop" C.10.E.1
#
#     Args:
#         crop_type: an instance of a crop class
#     """
#
#     crop_type.yield_actual = crop_type.yield_max * crop_type.harvest_eff
#
#
# def calc_quality_assessment(crop_type):  #TODO: Stand in for more sophisticated method - GitHub Issue #161
#     """
#     Description:
#          Assesses quality of feed at harvest
#         "Feed Inventory Pseudocode" F.1.1
#     Args:
#         crop_type: the crop for which a quality is being assessed
#     """
#     crop_type.harvest_quality = 'mid_mature'
#     crop_type.feed_id = crop_type.feed_id
#     if crop_type.crop_name.startswith('corn'):
#         if crop_type.harvest_quality == 'immature':
#             crop_type.feed_id = '35g'
#             crop_type.NDF_harvest_percent = 0.541
#         elif crop_type.harvest_quality == 'mid_mature':
#             crop_type.feed_id = '36g'
#             crop_type.NDF_harvest_percent = 0.45
#         elif crop_type.harvest_quality == 'mature':
#             crop_type.feed_id = '37g'
#             crop_type.NDF_harvest_percent = 0.445
#
#
# def calc_nutrient_removal(crop_type):
#     """
#     Description:
#         Calculates the amount of nitrogen and phosphorus removed in the yield.
#         "pseudocode_crop" C.10.F.1/2
#
#     Args:
#         crop_type: an instance of a crop class
#     """
#
#     crop_type.N_yield = crop_type.fr_N * crop_type.yield_actual
#     crop_type.P_yield = crop_type.fr_P * crop_type.yield_actual
#
#
# def calc_residue(soil, crop_type, field_management, time):
#     """
#     Description:
#         Updates the current residue.
#         "pseudocode_crop" C.10.H.1/4/5
#
#     Args:
#         soil: an instance of the Soil class
#         crop_type: an instance of a crop class
#         field_management: an instance of the FieldManagement class
#         time: an instance of the Time class specified in classes.py
#     """
#     # for carbon, needs to be calculated only at harvest
#     # C.3.A.4
#     crop_type.bio_BG = crop_type.fr_root * crop_type.biomass_actual
#     soil.soil_layers[0].tillage_percent = 0.55 #TODO: hard coded value - GitHub Issue #163
#
#     # lignin residue reset at harvest
#     soil.AG_lignin_res_percent = 17  # TODO: should depend upon crops and management - GitHub Issue #163
#     soil.BG_lignin_res_percent = 17  # TODO: should depend upon crops and management - GitHub Issue #163
#
#     d_residue = 0
#     if time.day == crop_type.kill_day or crop_type.crop_type == 'annual':
#         d_residue = crop_type.biomass_actual - crop_type.yield_actual
#         kill(crop_type, field_management, time)
#     else:
#         bio_frac = crop_type.yield_actual / crop_type.biomass_actual
#         cut(crop_type, bio_frac)
#
#     soil.residue += d_residue
#
#     soil.residue_harvest = soil.residue
#
# # TODO: missing pseudocode in pseudocode_crop Google Doc - GitHub Issue #168
# def calc_harvest_quality(crop_type): # TODO: Stand in for more sophisticated method - GitHub Issue #161
#     """
#     Description:
#         Calculate quality of yield for grouping in feed storage
#         "pseudocode_crop" C.10.G
#     Args:
#         crop_type: an instance of a crop class
#     """
#     crop_type.harvest_quality = "good"
#
#
# def kill(crop_type, field_management, time):
#     """
#     Description:
#         Kills the crop.
#         NOTE: Any day-of-yield values reset here will be reported to the output
#         handler as 0. To reset after reporting see crop.daily_reset()
#         "pseudocode_crop" C.10.H.4
#
#     Args:
#         crop_type: an instance of a crop class
#         field_management: an instance of the FieldManagement class
#         time: an instance of the Time class as specified in classes.py
#     """
#     crop_type.accumulated_HU = 0
#     crop_type.prev_accumulated_HU = 0
#
#     crop_type.fr_PHU = 0
#     crop_type.prev_fr_PHU = 0
#
#     crop_type.LAI_actual = 0
#     crop_type.fr_LAI_max = 0
#
#     crop_type.biomass_actual = 0
#     crop_type.prev_biomass_actual = 0
#     crop_type.bio_AG = 0
#
#     crop_type.z_root = 0
#     crop_type.fr_root = 0
#
#     crop_type.bio_P = 0
#     crop_type.bio_N = 0
#
#     crop_type.ET_annual = 0
#
#     crop_type.planted = False
#     crop_type.growing = False
#     crop_type.killed = True
#
#     # FM.2.2
#     till_management = field_management.managed_applications['tillage']
#     if (time.calendar_year, -1) in till_management.applications:
#         till_management.schedule_application(time)
#
#
# def cut(crop_type, bio_frac):
#     """
#     Description:
#         Cuts the crop without killing it
#         "pseudocode_crop" C.10.H.2/3
#
#     Args:
#         crop_type: an instance of a crop class
#         bio_frac: fraction of biomass removed during the cut
#     """
#
#     crop_type.accumulated_HU = crop_type.accumulated_HU * (1 - bio_frac)
#     crop_type.fr_PHU = crop_type.accumulated_HU / crop_type.PHU
#
#     crop_type.LAI_actual = crop_type.LAI_actual * (1 - bio_frac)
#     crop_type.fr_LAI_max = 0
#
#     crop_type.biomass_actual -= crop_type.yield_actual
#
#     crop_type.bio_P = crop_type.bio_P * (1 - bio_frac)
#     crop_type.bio_N = crop_type.bio_N * (1 - bio_frac)
#
#     crop_type.ET_annual = 0
