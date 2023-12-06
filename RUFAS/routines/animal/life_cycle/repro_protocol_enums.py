from enum import Enum


class HeiferReproProtocolEnum(Enum):
    """
    This enum class lists the heifer reproduction protocols.

    This list includes both the protocols and their sub-protocols if they have any. The names of
    the sub-protocols are prefixed with the name of the protocol they belong to.

    Attributes
    ----------
    ED : str
        The estrus detection reproduction protocol.
    TAI : str
        The timed artificial insemination reproduction protocol.
    SynchED : str
        The synchronized estrus detection reproduction protocol.
    TAI_5dCG2P : str
        The 5dCG2P sub-protocol of the TAI protocol.
    TAI_5dCGP : str
        The 5dCGP sub-protocol of the TAI protocol.
    SynchED_CP : str
        The CP sub-protocol of the SynchED protocol.
    SynchED_2P : str
        The 2P sub-protocol of the SynchED protocol.
    """

    ED = 'ED'
    TAI = 'TAI'
    SynchED = 'SynchED'
    TAI_5dCG2P = '5dCG2P'
    TAI_5dCGP = '5dCGP'
    SynchED_CP = 'CP'
    SynchED_2P = '2P'
