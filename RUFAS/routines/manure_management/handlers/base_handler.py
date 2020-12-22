from .sand_lane import SandLane


class BaseHandler:
    def __init__(self, handler_data):

        self.sand_lane = None

        if handler_data is None or handler_data['default']:
            self.default = True
            self.set_defaults()
        else:
            self.water_use_rate = handler_data['water_use_rate']
            self.time_per_cleaning = handler_data['time_per_cleaning']
            self.cleanings_per_day = handler_data['cleanings_per_day']
            self.init_sand_lane(handler_data['sand_lane'])

        self.density = 0
        self.bedding_added = 0
        self.flush_water_volume = 0
        self.bedding_washed_percent = 0
        self.bedding_washed = 0
        self.bedding_dry_matter = 0

        self.TS_loss = 0
        self.VS_loss = 0

        self.TS_loss_perc = 0
        self.VS_loss_perc = 0
        self.flow_rate = 0
        self.NH4 = 0

        self.bedding = None

        self.flush_water_volume_mlk = 0

    def init_sand_lane(self, sand_lane_data):
        if self.bedding == 'sand':
            self.sand_lane = SandLane(sand_lane_data)

    def set_defaults(self):
        if self.bedding.startswith("organic"):
            self.bedding_added = 11.8
            self.bedding_dry_matter = 0.9
            self.bedding_washed_percent = 0.5
            self.density = 250
        elif self.bedding.startswith("sand"):
            self.bedding_added = 20
            self.bedding_dry_matter = 0.9
            self.bedding_washed_percent = 0.8
            self.density = 1500
