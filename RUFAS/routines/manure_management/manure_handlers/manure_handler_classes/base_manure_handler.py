"""
RUFAS: Ruminant Farm Systems Model

File name: base_handler.py

Description:

Author(s):  William Donovan, wmdonovan@wisc.edu
            Yunus Mohammed, ymm26@cornell.edu 
"""

from RUFAS.routines.manure_management.data_models.constants import ManureManagementConstants as Constants
from RUFAS.routines.manure_management.data_models.simple_pen import SimplePen
from RUFAS.routines.manure_management.manure_handlers.bedding.bedding_enum import BeddingEnum
from RUFAS.routines.manure_management.manure_handlers.bedding.bedding_manager import BeddingManager
from RUFAS.routines.manure_management.manure_handlers.manure_handler_init_data import ManureHandlerInitData
from RUFAS.routines.manure_management.manure_handlers.manure_handler_variables import ManureHandlerVariables
from RUFAS.routines.manure_management.sand_separators.sand_separation_lane import SandSeparationLane


class BaseManureHandler:
    """
    Description
    ------------

    Attributes
    ----------

    """

    def __init__(self,
                 pen: SimplePen,
                 handler_data: ManureHandlerInitData):
        self.pen = pen
        self.handler_init_data = handler_data
        # self.reception_pit = reception_pit
        self.sand_lane = None

        self.bedding_manager = BeddingManager.get_instance(pen.bedding_type)
        self.cow_num = len(self.pen.animals_in_pen)
        self.flush_water_daily = self.cow_num * self.handler_init_data.water_use_rate
        self.flush_water_volume = 0.0

        self.flush_water_volume_mlk = 0  # TODO: unused
        self.flow_rate = 0  # TODO: unused

        self.daily_vars = ManureHandlerVariables()

    # TODO: unused
    def init_sand_lane(self, sand_lane_data):
        if self.bedding_manager.bedding_enum is BeddingEnum.SAND:
            self.sand_lane = SandSeparationLane(sand_lane_data)

    def reset_daily_variables(self):
        self.daily_vars = ManureHandlerVariables()
        self.flush_water_volume = 0.0

    def update(self, pen: SimplePen):
        """
        Description:
            Calls functions to calculate nutrient losses and transformations during
            manure handling.
            "pseudocode_manure_management" MS.3
        """
        self.update_daily_variables(pen)
        # self.flush_water()
        # self.N_loss()
        # self.P_loss()
        # self.K_loss()
        # self.solids()
        # if self.bedding_manager.bedding_enum is BeddingEnum.SAND:
        #     self.sand_lane.sand_lane()
        # self.CH4_effluent()
        # self.WIP_WOP()

    def update_daily_variables(self, pen: SimplePen):
        self.daily_vars += ManureHandlerVariables.get_instance_from_pen(pen)

    def flush_water(self):
        """
        Description:
            Calculates Flush Water Volume and passes it to the associated separa
            "pseudocode_manure_management" MS.3.A
        """

        self.flush_water_volume = sum([
            self.daily_vars.raw_manure,
            self.flush_water_daily,
            self.bedding_manager.bedding_washed
        ])
        # self.reception_pit.flush_water_volume += self.flush_water_volume

    def N_loss(self):
        """
        Description:
            Updates Nitrogen mass in the reception_pit from excreted manure
            "pseudocode_manure_management" MS.3.B
        """

        # self.reception_pit.N = self.daily_vars.N_excreted
        pass

    def P_loss(self):
        """
        Description:
            Updates Phosphorus mass in the reception_pit from excreted manure
    "       pseudocode_manure_management" MS.3.C
        """

        # self.reception_pit.P = self.daily_vars.P_excreted
        pass

    def K_loss(self):
        """
        Description:
            Updates Potassium mass in the reception_pit from excreted manure
            "pseudocode_manure_management" MS.3.D
        """

        # self.reception_pit.K = self.daily_vars.K_excreted
        pass

    def solids(self):
        """
        Description:
            Updates Total and Volatile Solids in the reception_pit from excreted manure
            "pseudocode_manure_management" MS.3.E
        """
        self.daily_vars.TS_loss = self.flush_water_volume * Constants.TS_loss_perc
        self.daily_vars.VS_loss = self.daily_vars.TS_loss * Constants.VS_loss_perc

        # self.reception_pit.TS += self.daily_vars.TS_loss
        # self.reception_pit.VS += self.daily_vars.VS_loss
        pass

    # TODO: move to sand lane class
    # def sand_lane(self):
    #     """
    #     Description:
    #         Sand separation lane. Method only called for sand bedding.
    #     """
    #     sand_lane = self.sand_lane
    #     sand_lane.sand_washed_with_water = self.bedding_mass_per_day  # kg/day
    #     sand_lane.sand_mass_separated = sand_lane.sand_separation_efficiency * \
    #                                     sand_lane.sand_washed_with_water  # kg/day
    #     sand_lane.sand_volume_separated = sand_lane.sand_mass_separated / self.bedding_density  # m3/day

    def CH4_effluent(self):
        # self.reception_pit.CH4 += self.daily_vars.CH4
        pass

    def WIP_WOP(self):
        # self.reception_pit.WIP += self.daily_vars.WIP
        # self.reception_pit.WOP += self.daily_vars.WOP
        pass
