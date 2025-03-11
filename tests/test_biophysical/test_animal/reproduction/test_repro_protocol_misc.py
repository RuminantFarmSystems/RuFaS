from RUFAS.biophysical.animal.data_types.repro_protocol_enums import (
    HeiferReproductionProtocol,
    HeiferSynchEDSubProtocol,
    HeiferTAISubProtocol,
)
from RUFAS.biophysical.animal.reproduction.repro_protocol_misc import InternalReproSettings


def test_internal_repro_settings() -> None:
    """
    Test the HEIFER_REPRO_PROTOCOLS dictionary in InternalReproSettings.

    This test ensures that the default sub-protocols and properties are correctly defined
    for each reproduction protocol in HEIFER_REPRO_PROTOCOLS.
    """
    expected_protocols = {
        HeiferReproductionProtocol.TAI.value: {
            "default_sub_protocol": HeiferTAISubProtocol.TAI_5dCG2P,
            "default_sub_properties": {"conception_rate": 0.5},
        },
        HeiferReproductionProtocol.SynchED.value: {
            "default_sub_protocol": HeiferSynchEDSubProtocol.SynchED_2P,
            "default_sub_properties": {"estrus_detection_rate": 0.7},
        },
        HeiferSynchEDSubProtocol.SynchED_2P.value: {
            "when_estrus_not_detected": {
                "repro_protocol": HeiferReproductionProtocol.TAI,
                "repro_sub_protocol": HeiferTAISubProtocol.TAI_5dCG2P,
                "repro_sub_properties": {"conception_rate": 0.5},
            }
        },
        HeiferSynchEDSubProtocol.SynchED_CP.value: {
            "when_estrus_not_detected": {
                "repro_protocol": HeiferReproductionProtocol.TAI,
                "repro_sub_protocol": HeiferTAISubProtocol.TAI_5dCG2P,
                "repro_sub_properties": {"conception_rate": 0.5},
            }
        },
    }

    for protocol, expected_values in expected_protocols.items():
        assert InternalReproSettings.HEIFER_REPRO_PROTOCOLS[protocol] == expected_values
