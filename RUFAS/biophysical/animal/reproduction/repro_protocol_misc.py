from typing import Any

from RUFAS.biophysical.animal.data_types.repro_protocol_enums import (
    HeiferReproductionProtocol,
    HeiferTAISubProtocol,
    HeiferSynchEDSubProtocol,
)


class InternalReproSettings:
    """
    This class contains the internal reproduction settings that are not explicitly defined by the user.

    Attributes
    ----------
    HEIFER_REPRO_PROTOCOLS : dict[str, dict]
        The reproduction protocols for heifers.
        - TAI
            - default_sub_protocol : Literal['5dCG2P']
                The default sub-protocol for TAI.
            - default_sub_properties : dict[str, Any]
                The properties of the default sub-protocol.
                - conception_rate : float
                    The conception rate of the default sub-protocol.
        - SynchED
            - default_sub_protocol : Literal['2P']
                The default sub-protocol for SynchED.
            - default_sub_properties : dict[str, Any]
                The properties of the default sub-protocol.
                - estrus_detection_rate : float
                    The estrus detection rate of the default sub-protocol.
        - SynchED 2P
            - when_estrus_not_detected
                When estrus is not detected in SynchED 2P, the reproduction protocol is switched to TAI.
                - repro_protocol : Literal['TAI']
                    The TAI reproduction protocol will be used next. If estrus is still not detected, then
                    the reproduction protocol will be switched to ED as the last resort.
                - repro_sub_protocol : Literal['5dCG2P', '5dCG2P']
                    The TAI sub-protocol that will be used next.
                - repro_sub_properties : dict[str, Any]
                    The properties of the TAI sub-protocol.
                    - conception_rate : float
                        The conception rate of the TAI sub-protocol.
        - SynchED CP
            - when_estrus_not_detected
                When estrus is not detected in SynchED CP, the reproduction protocol is switched to TAI.
                - repro_protocol : Literal['TAI']
                    The TAI reproduction protocol will be used next. If estrus is still not detected, then
                    the reproduction protocol will be switched to ED as the last resort.
                - repro_sub_protocol : Literal['5dCG2P', '5dCG2P']
                    The TAI sub-protocol that will be used next.
                - repro_sub_properties : dict[str, Any]
                    The properties of the TAI sub-protocol.
                    - conception_rate : float
                        The conception rate of the TAI sub-protocol.
    """

    HEIFER_REPRO_PROTOCOLS: dict[str, dict[str, Any]] = {
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

    COW_REPRO_PROTOCOLS: dict[str, dict[str, Any]] = {}
