from __future__ import annotations

from typing import Literal

from RUFAS.routines.animal.life_cycle.repro_protocol_enums import HeiferReproProtocolEnum, CowReproProtocolEnum


class HormoneDeliverySchedule:
    """
    This class contains the hormone delivery schedule for the reproduction protocols that involves hormone delivery.

    Notes
    -----
    The schedule is a dictionary of offset days to a dictionary of events that should
    happen on that day. The events are:

    - deliver_hormones: a list of hormones to deliver on that day. The supported hormones are: GnRH, PGF, CIDR.

    - set_ai_day: a boolean indicating whether to set the AI day to that day

    - set_conception_rate: a boolean indicating whether to set the conception rate to that day

    The schedule is static and is not meant to be instantiated. It is based on the following protocols and their
    subprotocols:

    - Heifer reproduction protocols and subprotocols:
        - TAI
            - 5dCG2P
            - 5dCGP
        - SynchED
            - 2P
            - CP
    - Cow reproduction protocols and subprotocols:
        - TAI
            - OvSynch 48
            - OvSynch 56
            - CoSynch 72
            - 5d CoSynch
    """

    HEIFER_REPRO_PROTOCOLS = {
        HeiferReproProtocolEnum.TAI_5dCG2P.value: {
            0: {'deliver_hormones': ['CIDR']},
            5: {'deliver_hormones': ['PGF']},
            6: {'deliver_hormones': ['PGF']},
            8: {'deliver_hormones': ['GnRH']},
            9: {'set_ai_day': True, 'set_conception_rate': True}
        },
        HeiferReproProtocolEnum.TAI_5dCGP.value: {
            0: {'deliver_hormones': ['CIDR']},
            5: {'deliver_hormones': ['PGF']},
            8: {'deliver_hormones': ['GnRH']},
            9: {'set_ai_day': True, 'set_conception_rate': True}
        },
        HeiferReproProtocolEnum.SynchED_2P.value: {
            0: {'deliver_hormones': ['PGF']},
            14: {'deliver_hormones': ['PGF']},
        },
        HeiferReproProtocolEnum.SynchED_CP.value: {
            0: {'deliver_hormones': ['CIDR']},
            7: {'deliver_hormones': ['PGF']},
        }
    }

    COW_REPRO_PROTOCOLS = {
        CowReproProtocolEnum.PreSynch_PreSynch.value: {
            0: {'deliver_hormones': ['PGF']},
            14: {'deliver_hormones': ['PGF']},
            # 26: End day, start of TAI
        },

        CowReproProtocolEnum.PreSynch_DoubleOvSynch.value: {
            0: {'deliver_hormones': ['GnRH']},
            7: {'deliver_hormones': ['PGF']},
            10: {'deliver_hormones': ['GnRH']},
            # 17: End day, start of TAI
        },

        CowReproProtocolEnum.PreSynch_G6G.value: {
            0: {'deliver_hormones': ['PGF']},
            2: {'deliver_hormones': ['GnRH']},
            # 9: End day, start of TAI
        },

        CowReproProtocolEnum.TAI_OvSynch_48.value: {
            0: {'deliver_hormones': ['GnRH']},
            7: {'deliver_hormones': ['PGF']},
            9: {'deliver_hormones': ['GnRH']},
            10: {'deliver_hormones': ['GnRH']},
            11: {'set_ai_day': True, 'set_conception_rate': True}
        },
        CowReproProtocolEnum.TAI_OvSynch_56.value: {
            0: {'deliver_hormones': ['GnRH']},
            7: {'deliver_hormones': ['PGF']},
            9: {'deliver_hormones': ['GnRH']},
            10: {'deliver_hormones': ['GnRH']},
            11: {'set_ai_day': True, 'set_conception_rate': True}
        },
        CowReproProtocolEnum.TAI_CoSynch_72.value: {
            0: {'deliver_hormones': ['GnRH']},
            7: {'deliver_hormones': ['PGF']},
            10: {'deliver_hormones': ['GnRH']},
            11: {'set_ai_day': True, 'set_conception_rate': True}
        },
        CowReproProtocolEnum.TAI_5d_CoSynch.value: {
            0: {'deliver_hormones': ['GnRH']},
            5: {'deliver_hormones': ['PGF']},
            6: {'deliver_hormones': ['PGF']},
            8: {'deliver_hormones': ['GnRH']},
            9: {'set_ai_day': True, 'set_conception_rate': True}
        },
    }

    @staticmethod
    def get_schedule(animal_category: Literal['heifers', 'cows'], protocol_name: str) -> dict[int, dict] | None:
        """
        Get the hormone delivery schedule for the given animal category and protocol name.

        Parameters
        ----------
        animal_category : Literal['heifers', 'cows']
            The animal category to get the schedule for. Must be either 'heifers' or 'cows'.
        protocol_name : str
            The name of the protocol to get the schedule for. Must be one of the protocols defined in
            HEIFER_REPRO_PROTOCOLS or COW_REPRO_PROTOCOLS.

        Returns
        -------
        dict[int, dict] | None
            The hormone delivery schedule for the given animal category and protocol name. None if the
            animal category or protocol name is invalid.
        """

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

    @staticmethod
    def get_adjusted_schedule(animal_category: Literal['heifers', 'cows'],
                              protocol_name: str,
                              start_day: int) -> dict[int, dict] | None:
        """
        Get the hormone delivery schedule for the given animal category and protocol name, adjusted to start
        on the given start day.

        Parameters
        ----------
        animal_category : Literal['heifers', 'cows']
            The animal category to get the schedule for. Must be either 'heifers' or 'cows'.
        protocol_name : str
            The name of the protocol to get the schedule for. Must be one of the protocols defined in
            HEIFER_REPRO_PROTOCOLS or COW_REPRO_PROTOCOLS.
        start_day : int
            The day to start the schedule on.

        Returns
        -------
        dict[int, dict] | None
            The hormone delivery schedule for the given animal category and protocol name, adjusted to start
            on the given start day. None if the animal category or protocol name is invalid.
        """

        schedule = HormoneDeliverySchedule.get_schedule(animal_category, protocol_name)
        if schedule is None:
            return None
        adjusted_schedule = {}
        for offset_days in schedule:
            adjusted_schedule[start_day + offset_days] = schedule[offset_days]
        return adjusted_schedule
