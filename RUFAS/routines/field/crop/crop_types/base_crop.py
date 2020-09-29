class BaseCrop:
    def __init__(self):

        self.grow_years = []
        self.repeat = 0
        self.planting_date = 0
        self.harvest_date = 0

        self.harvest_type = ''

        self.crop_name = 'null'
        self.crop_type = ''
        self.harvest_quality = 'null'
        self.feed_id = 'null'

        # Necessary variables for a null crop to run
        # These variables are used within the soil module and must
        # be declared and initialized even when a crop is not growing
        self.fr_PHU = 0
        self.fr_N = 0
        self.LAI_actual = 0
        self.z_root = 0
        self.biomass_actual = 0
        self.epco = 0
        self.N_fix = 0.0
        self.bio_N = 0
        self.bio_P = 0
        self.bio_AG = 0
        self.bio_BG = 0
        self.HI_actual = 0
        self.yield_actual = 0
        self.yield_annual = 0
        self.HI_min = 0
        self.HI_actual = 0
        self.HI_max = 0
