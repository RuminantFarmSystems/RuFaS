from RUFAS.biophysical.animal.data_types.repro_protocol_enums import (
    CowPreSynchSubProtocol,
    CowTAISubProtocol,
    HeiferSynchEDSubProtocol,
    HeiferTAISubProtocol,
)
from RUFAS.biophysical.animal.reproduction.hormone_delivery_schedule import HormoneDeliverySchedule


def test_heifer_repro_protocols() -> None:
    """Test for heifer reproduction protocol mappings."""
    expected_protocols = {
        HeiferTAISubProtocol.TAI_5dCG2P.value: {
            0: {"deliver_hormones": ["CIDR"]},
            5: {"deliver_hormones": ["PGF"]},
            6: {"deliver_hormones": ["PGF"]},
            8: {"deliver_hormones": ["GnRH"]},
            9: {"set_ai_day": True, "set_conception_rate": True},
        },
        HeiferTAISubProtocol.TAI_5dCGP.value: {
            0: {"deliver_hormones": ["CIDR"]},
            5: {"deliver_hormones": ["PGF"]},
            8: {"deliver_hormones": ["GnRH"]},
            9: {"set_ai_day": True, "set_conception_rate": True},
        },
        HeiferSynchEDSubProtocol.SynchED_2P.value: {
            0: {"deliver_hormones": ["PGF"]},
            14: {"deliver_hormones": ["PGF"]},
        },
        HeiferSynchEDSubProtocol.SynchED_CP.value: {
            0: {"deliver_hormones": ["CIDR"]},
            7: {"deliver_hormones": ["PGF"]},
        },
    }

    for protocol, expected_schedule in expected_protocols.items():
        assert HormoneDeliverySchedule.HEIFER_REPRO_PROTOCOLS[protocol] == expected_schedule


def test_cow_repro_protocols() -> None:
    """Test for cow reproduction protocol mappings."""
    expected_protocols = {
        CowPreSynchSubProtocol.Presynch_PreSynch.value: {
            0: {"deliver_hormones": ["PGF"]},
            14: {"deliver_hormones": ["PGF"]},
            25: {"set_presynch_end": True},
        },
        CowPreSynchSubProtocol.Presynch_DoubleOvSynch.value: {
            0: {"deliver_hormones": ["GnRH"]},
            7: {"deliver_hormones": ["PGF"]},
            10: {"deliver_hormones": ["GnRH"]},
            16: {"set_presynch_end": True},
        },
        CowPreSynchSubProtocol.Presynch_G6G.value: {
            0: {"deliver_hormones": ["PGF"]},
            2: {"deliver_hormones": ["GnRH"]},
            8: {"set_presynch_end": True},
        },
        CowTAISubProtocol.TAI_OvSynch_48.value: {
            0: {"deliver_hormones": ["GnRH"]},
            7: {"deliver_hormones": ["PGF"]},
            9: {"deliver_hormones": ["GnRH"]},
            10: {"set_ai_day": True, "set_conception_rate": True, "set_ovsynch_end": True},
        },
        CowTAISubProtocol.TAI_OvSynch_56.value: {
            0: {"deliver_hormones": ["GnRH"]},
            7: {"deliver_hormones": ["PGF"]},
            9: {"deliver_hormones": ["GnRH"]},
            10: {"set_ai_day": True, "set_conception_rate": True, "set_ovsynch_end": True},
        },
        CowTAISubProtocol.TAI_CoSynch_72.value: {
            0: {"deliver_hormones": ["GnRH"]},
            7: {"deliver_hormones": ["PGF"]},
            10: {
                "deliver_hormones": ["GnRH"],
                "set_ai_day": True,
                "set_conception_rate": True,
                "set_ovsynch_end": True,
            },
        },
        CowTAISubProtocol.TAI_5d_CoSynch.value: {
            0: {"deliver_hormones": ["GnRH"]},
            5: {"deliver_hormones": ["PGF"]},
            6: {"deliver_hormones": ["PGF"]},
            8: {"deliver_hormones": ["GnRH"], "set_ai_day": True, "set_conception_rate": True, "set_ovsynch_end": True},
        },
    }

    for protocol, expected_schedule in expected_protocols.items():
        assert HormoneDeliverySchedule.COW_REPRO_PROTOCOLS[protocol] == expected_schedule


def test_get_schedule() -> None:
    """Test for getting hormone delivery schedule for a given category and protocol."""
    heifer_schedule = HormoneDeliverySchedule.get_schedule("heifers", HeiferTAISubProtocol.TAI_5dCG2P.value)
    expected_heifer_schedule = {
        0: {"deliver_hormones": ["CIDR"]},
        5: {"deliver_hormones": ["PGF"]},
        6: {"deliver_hormones": ["PGF"]},
        8: {"deliver_hormones": ["GnRH"]},
        9: {"set_ai_day": True, "set_conception_rate": True},
    }
    assert heifer_schedule == expected_heifer_schedule

    cow_schedule = HormoneDeliverySchedule.get_schedule("cows", CowTAISubProtocol.TAI_OvSynch_48.value)
    expected_cow_schedule = {
        0: {"deliver_hormones": ["GnRH"]},
        7: {"deliver_hormones": ["PGF"]},
        9: {"deliver_hormones": ["GnRH"]},
        10: {"set_ai_day": True, "set_conception_rate": True, "set_ovsynch_end": True},
    }
    assert cow_schedule == expected_cow_schedule
    assert HormoneDeliverySchedule.get_schedule("invalid_category", "some_protocol") is None  # type: ignore
    assert HormoneDeliverySchedule.get_schedule("heifers", "invalid_protocol") is None


def test_get_adjusted_schedule() -> None:
    """Test for getting adjusted hormone delivery schedule for a given category and protocol."""
    start_day = 3
    adjusted_heifer_schedule = HormoneDeliverySchedule.get_adjusted_schedule(
        "heifers", HeiferTAISubProtocol.TAI_5dCG2P.value, start_day
    )
    expected_adjusted_heifer_schedule = {
        3: {"deliver_hormones": ["CIDR"]},
        8: {"deliver_hormones": ["PGF"]},
        9: {"deliver_hormones": ["PGF"]},
        11: {"deliver_hormones": ["GnRH"]},
        12: {"set_ai_day": True, "set_conception_rate": True},
    }
    assert adjusted_heifer_schedule == expected_adjusted_heifer_schedule

    adjusted_cow_schedule = HormoneDeliverySchedule.get_adjusted_schedule(
        "cows", CowTAISubProtocol.TAI_OvSynch_48.value, start_day
    )
    expected_adjusted_cow_schedule = {
        3: {"deliver_hormones": ["GnRH"]},
        10: {"deliver_hormones": ["PGF"]},
        12: {"deliver_hormones": ["GnRH"]},
        13: {"set_ai_day": True, "set_conception_rate": True, "set_ovsynch_end": True},
    }
    assert adjusted_cow_schedule == expected_adjusted_cow_schedule
    assert (
        HormoneDeliverySchedule.get_adjusted_schedule("invalid_category", "some_protocol", start_day) is None
    )  # type: ignore
    assert HormoneDeliverySchedule.get_adjusted_schedule("heifers", "invalid_protocol", start_day) is None
