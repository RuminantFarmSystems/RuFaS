from __future__ import annotations

from typing import Any

import pytest

from RUFAS.routines.animal.life_cycle.hormone_delivery_schedule import HormoneDeliverySchedule
from RUFAS.routines.animal.life_cycle.repro_protocol_enums import HeiferReproProtocolEnum, CowReproProtocolEnum
from RUFAS.routines.animal.life_cycle.repro_protocol_misc import InternalReproSettings


@pytest.mark.parametrize("animal_category, protocol_name, expected", [
    # Valid heifer protocols
    ('heifers', HeiferReproProtocolEnum.TAI_5dCG2P.value, {
        0: {'deliver_hormones': ['CIDR']},
        5: {'deliver_hormones': ['PGF']},
        6: {'deliver_hormones': ['PGF']},
        8: {'deliver_hormones': ['GnRH']},
        9: {'set_ai_day': True, 'set_conception_rate': True}
    }),
    ('heifers', HeiferReproProtocolEnum.TAI_5dCGP.value, {
        0: {'deliver_hormones': ['CIDR']},
        5: {'deliver_hormones': ['PGF']},
        8: {'deliver_hormones': ['GnRH']},
        9: {'set_ai_day': True, 'set_conception_rate': True}
    }),

    # Valid cow protocols
    ('cows', CowReproProtocolEnum.TAI_OvSynch_48.value, {
        0: {'deliver_hormones': ['GnRH']},
        7: {'deliver_hormones': ['PGF']},
        9: {'deliver_hormones': ['GnRH']},
        10: {'deliver_hormones': ['GnRH']},
        11: {
            'set_ai_day': True,
            'set_conception_rate': True,
            'set_tai_end': True
        }
    }),
    ('cows', CowReproProtocolEnum.TAI_OvSynch_56.value, {
        0: {'deliver_hormones': ['GnRH']},
        7: {'deliver_hormones': ['PGF']},
        9: {'deliver_hormones': ['GnRH']},
        10: {'deliver_hormones': ['GnRH']},
        11: {
            'set_ai_day': True,
            'set_conception_rate': True,
            'set_tai_end': True
        }
    }),
    ('cows', CowReproProtocolEnum.TAI_CoSynch_72.value, {
        0: {'deliver_hormones': ['GnRH']},
        7: {'deliver_hormones': ['PGF']},
        10: {'deliver_hormones': ['GnRH']},
        11: {
            'set_ai_day': True,
            'set_conception_rate': True,
            'set_tai_end': True
        }
    }),
    ('cows', CowReproProtocolEnum.TAI_5d_CoSynch.value, {
        0: {'deliver_hormones': ['GnRH']},
        5: {'deliver_hormones': ['PGF']},
        6: {'deliver_hormones': ['PGF']},
        8: {'deliver_hormones': ['GnRH']},
        9: {
            'set_ai_day': True,
            'set_conception_rate': True,
            'set_tai_end': True
        }
    }),

    # Invalid cases
    ('invalid_category', HeiferReproProtocolEnum.TAI_5dCG2P.value, None),
    ('heifers', 'invalid_protocol', None),
    ('cows', 'invalid_protocol', None),
])
def test_get_schedule(animal_category: str, protocol_name: str, expected: dict | None) -> None:
    """
    Unit test for the get_schedule() method of the HormoneDeliverySchedule class in
    hormone_delivery_schedule.py.
    """

    assert HormoneDeliverySchedule.get_schedule(
        animal_category, protocol_name) == expected  # type: ignore


@pytest.mark.parametrize("animal_category, protocol_name, start_day, expected", [
    # Valid heifer protocol adjusted schedules
    ('heifers', HeiferReproProtocolEnum.TAI_5dCG2P.value, 3, {
        3: {'deliver_hormones': ['CIDR']},
        8: {'deliver_hormones': ['PGF']},
        9: {'deliver_hormones': ['PGF']},
        11: {'deliver_hormones': ['GnRH']},
        12: {'set_ai_day': True, 'set_conception_rate': True}
    }),
    ('heifers', HeiferReproProtocolEnum.TAI_5dCGP.value, 3, {
        3: {'deliver_hormones': ['CIDR']},
        8: {'deliver_hormones': ['PGF']},
        11: {'deliver_hormones': ['GnRH']},
        12: {'set_ai_day': True, 'set_conception_rate': True}
    }),

    # Valid cow protocol adjusted schedules
    ('cows', CowReproProtocolEnum.TAI_OvSynch_48.value, 2, {
        2: {'deliver_hormones': ['GnRH']},
        9: {'deliver_hormones': ['PGF']},
        11: {'deliver_hormones': ['GnRH']},
        12: {'deliver_hormones': ['GnRH']},
        13: {'set_ai_day': True, 'set_conception_rate': True, 'set_tai_end': True}
    }),
    ('cows', CowReproProtocolEnum.TAI_OvSynch_56.value, 2, {
        2: {'deliver_hormones': ['GnRH']},
        9: {'deliver_hormones': ['PGF']},
        11: {'deliver_hormones': ['GnRH']},
        12: {'deliver_hormones': ['GnRH']},
        13: {'set_ai_day': True, 'set_conception_rate': True, 'set_tai_end': True}
    }),
    ('cows', CowReproProtocolEnum.TAI_CoSynch_72.value, 2, {
        2: {'deliver_hormones': ['GnRH']},
        9: {'deliver_hormones': ['PGF']},
        12: {'deliver_hormones': ['GnRH']},
        13: {'set_ai_day': True, 'set_conception_rate': True, 'set_tai_end': True}
    }),
    ('cows', CowReproProtocolEnum.TAI_5d_CoSynch.value, 2, {
        2: {'deliver_hormones': ['GnRH']},
        7: {'deliver_hormones': ['PGF']},
        8: {'deliver_hormones': ['PGF']},
        10: {'deliver_hormones': ['GnRH']},
        11: {'set_ai_day': True, 'set_conception_rate': True, 'set_tai_end': True}
    }),

    # Invalid cases
    ('invalid_category', HeiferReproProtocolEnum.TAI_5dCG2P.value, 3, None),
    ('heifers', 'invalid_protocol', 3, None),
    ('cows', 'invalid_protocol', 2, None),
])
def test_get_adjusted_schedule(animal_category: str, protocol_name: str, start_day: int, expected: dict | None) -> None:
    """
    Unit test for the get_adjusted_schedule() method of the HormoneDeliverySchedule class in
    hormone_delivery_schedule.py.
    """

    assert HormoneDeliverySchedule.get_adjusted_schedule(
        animal_category, protocol_name, start_day) == expected  # type: ignore


@pytest.mark.parametrize(
    "protocol, expected_result",
    [
        (HeiferReproProtocolEnum.TAI.value, {
            'default_sub_protocol': HeiferReproProtocolEnum.TAI_5dCG2P.value,
            'default_sub_properties': {
                'conception_rate': 0.5
            }
        }),
        (HeiferReproProtocolEnum.SynchED.value, {
            'default_sub_protocol': HeiferReproProtocolEnum.SynchED_2P.value,
            'default_sub_properties': {
                'estrus_detection_rate': 0.7
            }
        })
    ]
)
def test_heifer_repro_protocols_default_values(protocol: str, expected_result: dict[str, Any]) -> None:
    """
    Unit test for the default sub-protocol and properties of the TAI and SynchED protocols
    in the HEIFER_REPRO_PROTOCOLS attribute of the InternalReproSettings class.
    """

    # Act and assert
    assert InternalReproSettings.HEIFER_REPRO_PROTOCOLS[protocol] == expected_result


@pytest.mark.parametrize(
    "sub_protocol, expected_result", [
        (HeiferReproProtocolEnum.SynchED_2P.value, {
            'repro_protocol': HeiferReproProtocolEnum.TAI.value,
            'repro_sub_protocol': HeiferReproProtocolEnum.TAI_5dCG2P.value,
            'repro_sub_properties': {
                'conception_rate': 0.5
            }
        }),

        (HeiferReproProtocolEnum.SynchED_CP.value, {
            'repro_protocol': HeiferReproProtocolEnum.TAI.value,
            'repro_sub_protocol': HeiferReproProtocolEnum.TAI_5dCG2P.value,
            'repro_sub_properties': {
                'conception_rate': 0.5
            }
        })
    ])
def test_heifer_synch_ed_sub_protocols_when_estrus_not_detected(sub_protocol: str,
                                                                expected_result: dict[str, Any]) -> None:
    """
    Unit test for the sub-attributes of the HEIFER_REPRO_PROTOCOLS attribute of
    the InternalReproSettings class when estrus is not detected.
    """

    # Act and assert
    assert InternalReproSettings.HEIFER_REPRO_PROTOCOLS[sub_protocol]['when_estrus_not_detected'] \
           == expected_result


@pytest.mark.parametrize(
    "protocol_name, expected_value", [
        # Normal cases
        ('ED', 'ED'),
        ('TAI', 'TAI'),
        ('SynchED', 'SynchED'),
        ('TAI_5dCG2P', '5dCG2P'),
        ('TAI_5dCGP', '5dCGP'),
        ('SynchED_CP', 'CP'),
        ('SynchED_2P', '2P')
    ])
def test_heifer_repro_protocol_enum_values(protocol_name: str, expected_value: str) -> None:
    """
    Unit test for the values of the HeiferReproProtocolEnum class.
    """

    # Act and assert
    assert HeiferReproProtocolEnum[protocol_name].value == expected_value
