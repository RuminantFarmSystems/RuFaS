from RUFAS.routines.animal.life_cycle.repro_protocol_enums import HeiferReproProtocolEnum


class InternalReproSettings:
    """
    This class contains the internal reproduction settings that are not explicitly defined by the user.

    Attributes
    ----------
    HEIFER_REPRO_PROTOCOLS : dict[str, dict]
        The reproduction protocols for heifers.
        - SynchED
            - 2P
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
            - CP
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

    HEIFER_REPRO_PROTOCOLS = {
        HeiferReproProtocolEnum.SynchED.value: {
            HeiferReproProtocolEnum.SynchED_2P.value: {
                'when_estrus_not_detected': {
                    'repro_protocol': HeiferReproProtocolEnum.TAI.value,
                    'repro_sub_protocol': HeiferReproProtocolEnum.TAI_5dCG2P.value,
                    'repro_sub_properties': {
                        'conception_rate': 0.5
                    }
                }
            },
            HeiferReproProtocolEnum.SynchED_CP.value: {
                'when_estrus_not_detected': {
                    'repro_protocol': HeiferReproProtocolEnum.TAI.value,
                    'repro_sub_protocol': HeiferReproProtocolEnum.TAI_5dCG2P.value,
                    'repro_sub_properties': {
                        'conception_rate': 0.5
                    }
                }
            }
        }
    }
