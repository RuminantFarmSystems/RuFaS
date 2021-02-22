import unittest


class ManureStorageInitializationTest(unittest.TestCase):

    def setUp(self):
        pen_data = {
            'pen0':
                {
                    'id': 0,
                    'bedding_type': 'sand',
                    'manure_handling': 'manual_scraping',
                    'manure_separator': 'sedimentation',
                    'manure_storage': 'storage_pit'
                },
            'pen1':
                {
                    'id': 1,
                    'bedding_type': 'organic',
                    'manure_handling': 'flush_system',
                    'manure_separator': 'decanting_centrifuge',
                    'manure_storage': 'anaerobic_lagoon'
                },
            'pen2':
                {
                    'id': 2,
                    'bedding_type': 'sawdust',
                    'manure_handling': 'automatic_alley_scrapers',
                    'manure_separator': 'slope_screen',
                    'manure_storage': 'xyz'
                }
        }

        manure = {'U': 0.34007492378760407,
                  'TAN_s': 0.1400150775776793,
                  'MN': 532.4074003089993,
                  'Mkg': 70.82359257209554,
                  'TSd': 8.24163244,
                  'VSd': 7087.427669573749,
                  'VSnd': 859.3916402321569,
                  'WIP_frac': 1.4119588737072899e-05,
                  'WOP_frac': 1.4119588737072899e-06,
                  'p_excrt_manure': 21.3465366,
                  'p_frac': 0.00031381,
                  'K_manure': 94.56725,
                  'CH4': 529.229415,
                  }
        super().setUp(pen_data=pen_data, manure=manure)

    def test_init(self):
        pass


if __name__ == '__main__':
    unittest.main()
