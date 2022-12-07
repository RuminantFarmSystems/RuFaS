from math import exp
import warnings
from RUFAS.output_manager import OutputManager

"""
This module is based upon the "Crop Yield" section of the SWAT model (5.2.4)
"""

class Yields():
    def __init__(self):
        self.heat_fraction = 0.6  # also in root_development.py
        self.optimal_harvest_index = 3.5
        self.water_deficiency = 0.2  # also in water_dynamics.py
        self.min_harvest_index = 0.2
        self.potential_harvest_index = None
        self.harvest_index = None
    def obtain_yields(self):
        # calc_HI_max(crop_type)
        # calc_HI_act(crop_type)
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

    def determine_potential_harvest_index(self):
        """updates the potential harvest index for the day"""
        self.potential_harvest_index = self.calc_potential_harvest_index(self.heat_fraction, self.optimal_harvest_index)

    def adjust_harvest_index(self):
        """adjusts the plant's harvest index for """
        # TODO: how to pass collect warnings from calc_actual_harvest_index and pass them to output manager?
        self.harvest_index = self.calc_actual_harvest_index(self.potential_harvest_index, self.min_harvest_index,
                                                            self.water_deficiency)

    @staticmethod
    def calc_potential_harvest_index(heat_fraction, optimal_harvest_index):
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
    def calc_actual_harvest_index(harvest_index: float, min_harvest_index: float, water_deficiency: float) -> float:
        """calculates the actual harvest index for a given day, adjusted for water deficiency

        Args:
            harvest_index: potential harvest index
            min_harvest_index: harvest index in drought conditions; minimum possible harvest index for the plant
            water_deficiency: water deficiency factor for the plant

        Returns: actual harvest index
        """
        if harvest_index < 0:
            warnings.warn("harvest index is less than zero, setting to zero", Warning)
            harvest_index = 0
        if harvest_index < min_harvest_index:
            warnings.warn("harvest index is lower than minimum possible harvest index, setting it to the minimum",
                          Warning)
            harvest_index = min_harvest_index

        adj_harvest_index = (harvest_index - min_harvest_index) * water_deficiency / \
                            (water_deficiency + exp(6.13 - 0.883 * water_deficiency)) + min_harvest_index
        return max(adj_harvest_index, 0)  # bound to zero


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
# def calc_HI_act(crop_type):
#     """
#     Description:
#         Calculates the actual harvest index (HI_actual).
#         "pseudocode_crop" C.10.C.1
#
#     Args:
#         crop_type: an instance of a crop class
#     """
#
#     term1 = crop_type.HI_max - crop_type.HI_min
#     exp_part = exp(6.13 - (0.883 * crop_type.gamma_wu))
#     term2 = crop_type.gamma_wu / (crop_type.gamma_wu + exp_part)
#
#     crop_type.HI_actual = term1 * term2 + crop_type.HI_min
#
# # TODO: add documentation and pseudocode reference - GitHub Issue #170
# def calc_dry_down(crop_type):
#     # TODO: stand in for more sophisticated dry down method - GitHub Issue #162
#     """
#     Description:
#         "pseudocode_crop"?
#     """
#     crop_type.bio_AG -= (crop_type.bio_AG * crop_type.biomass_dry_down_percent)
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
