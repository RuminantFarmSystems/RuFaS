class InternalReproSettings:
    """
    This class contains the internal reproduction settings that are not explicitly defined by the user.
    """
    HEIFER_REPRO_PROTOCOLS = {
        'SynchED': {
            '2P': {
                'when_estrus_not_detected': {
                    'repro_protocol': 'TAI',
                    'repro_sub_protocol': 'md5CG2P',
                    'repro_sub_properties': {
                        'conception_rate': 0.5
                    }
                }
            },
            'CP': {
                'when_estrus_not_detected': {
                    'repro_protocol': 'TAI',
                    'repro_sub_protocol': 'md5CG2P',
                    'repro_sub_properties': {
                        'conception_rate': 0.5
                    }
                }
            }
        }
    }
