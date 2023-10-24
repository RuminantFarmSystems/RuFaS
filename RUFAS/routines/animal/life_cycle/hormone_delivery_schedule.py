from __future__ import annotations

from typing import Literal


class HormoneDeliverySchedule:
    HEIFER_REPRO_PROTOCOLS = {
        'md5CG2P': {
            0: {'deliver_hormones': ['GnRH']},
            5: {'deliver_hormones': ['PGF']},
            6: {'deliver_hormones': ['PGF']},
            8: {'deliver_hormones': ['GnRH']},
            9: {'set_ai_day': True, 'set_conception_rate': True}
        },
        'md5CGP': {
            0: {'deliver_hormones': ['GnRH']},
            5: {'deliver_hormones': ['PGF']},
            8: {'deliver_hormones': ['PGF']},
            9: {'set_ai_day': True, 'set_conception_rate': True}
        },
        '2P': {
            0: {'deliver_hormones': ['PGF']},
            14: {'deliver_hormones': ['PGF']},
            15: {'set_ai_day': True, 'set_conception_rate': True}
        },
        'CP': {
            0: {'deliver_hormones': ['PGF']},
            7: {'deliver_hormones': ['PGF']},
            8: {'set_ai_day': True, 'set_conception_rate': True}
        }
    }

    COW_REPRO_PROTOCOLS = {
        'OvSynch 48': {
            0: {'deliver_hormones': ['GnRH']},
            7: {'deliver_hormones': ['PGF']},
            9: {'deliver_hormones': ['GnRH']},
            10: {'deliver_hormones': ['GnRH']},
            11: {'set_ai_day': True, 'set_conception_rate': True}
        },
        'OvSynch 56': {
            0: {'deliver_hormones': ['GnRH']},
            7: {'deliver_hormones': ['PGF']},
            9: {'deliver_hormones': ['GnRH']},
            10: {'deliver_hormones': ['GnRH']},
            11: {'set_ai_day': True, 'set_conception_rate': True}
        },
        'CoSynch 72': {
            0: {'deliver_hormones': ['GnRH']},
            7: {'deliver_hormones': ['PGF']},
            10: {'deliver_hormones': ['GnRH']},
            11: {'set_ai_day': True, 'set_conception_rate': True}
        },
        '5d CoSynch': {
            0: {'deliver_hormones': ['GnRH']},
            5: {'deliver_hormones': ['PGF']},
            6: {'deliver_hormones': ['PGF']},
            8: {'deliver_hormones': ['GnRH']},
            9: {'set_ai_day': True, 'set_conception_rate': True}
        },
    }

    @staticmethod
    def get_schedule(animal_category: Literal['heifers', 'cows'], protocol_name: str) -> dict[int, dict] | None:
        animal_category_to_protocols = {
            'heifers': HormoneDeliverySchedule.HEIFER_REPRO_PROTOCOLS,
            'cows': HormoneDeliverySchedule.COW_REPRO_PROTOCOLS
        }

        if animal_category not in animal_category_to_protocols:
            return None

        protocols = animal_category_to_protocols[animal_category]
        if protocol_name not in protocols:
            return None

        return protocols[protocol_name]
