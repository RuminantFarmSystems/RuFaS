from enum import Enum


class HeiferReproProtocolEnum(Enum):
    """
    This enum class lists the options for different heifer reproduction protocols.

    Notes
    -----
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


class CowReproProtocolEnum(Enum):
    """
    This enum class lists the options for different cow reproduction protocols.

    Notes
    -----
    This list includes both the protocols and their sub-protocols if they have any. The names of
    the sub-protocols are prefixed with the name of the protocol they belong to.

    Attributes
    ----------
    ED : str
        The estrus detection reproduction protocol.
    TAI : str
        The timed artificial insemination reproduction protocol.
    ED_TAI : str
        The estrus detection followed by timed artificial insemination reproduction protocol.
    TAI_OvSynch_48 : str
        The OvSynch 48 sub-protocol of the TAI protocol.
    TAI_OvSynch_56 : str
        The OvSynch 56 sub-protocol of the TAI protocol.
    TAI_CoSynch_72 : str
        The CoSynch 72 sub-protocol of the TAI protocol.
    TAI_5d_CoSynch : str
        The 5d CoSynch sub-protocol of the TAI protocol.
    """

    ED = 'ED'
    TAI = 'TAI'
    ED_TAI = 'ED-TAI'

    Presynch_Presynch = 'Presynch'
    Presynch_DoubleOvSynch = 'Double OvSynch'
    Presynch_G6G = 'G6G'

    TAI_OvSynch_48 = 'OvSynch 48'
    TAI_OvSynch_56 = 'OvSynch 56'
    TAI_CoSynch_72 = 'CoSynch 72'
    TAI_5d_CoSynch = '5d CoSynch'

    Resynch_TAIbeforePD = 'TAIbeforePD'
    Resynch_TAIafterPD = 'TAIafterPD'
    Resynch_PGFatPD = 'PGFatPD'


class CowReproStateEnum(Enum):
    """
    This enum class lists the options for different cow reproduction states.
    """

    WAITING = 'waiting'
    IN_PRESYNCH = 'in presynch'
    IN_TAI = 'in TAI'
    IN_ED = 'in estrus detection'
    ESTRUS_DETECTED = 'estrus detected'
