class SandLane:
    def __init__(self, sand_lane_data):
        if sand_lane_data is None or sand_lane_data['default']:
            self.default_sand_lane()
        else:
            self.sand_separated = sand_lane_data['sand_separated']

    def default_sand_lane(self):
        self.sand_separated = 0.6
