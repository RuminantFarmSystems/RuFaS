from enum import Enum


class HeiferReproductionProtocol(Enum):
    """
    This enum class lists the options for different heifer reproduction protocols.

    Attributes
    ----------
    ED : str
        The estrus detection reproduction protocol.
    TAI : str
        The timed artificial insemination reproduction protocol.
    SynchED : str
        The synchronized estrus detection reproduction protocol.

    """

    ED = "ED"
    TAI = "TAI"
    SynchED = "SynchED"


class HeiferTAISubProtocol(Enum):
    """
    This enum class lists the options for different heifer reproduction sub-protocols for the TAI program.

    Attributes
    ----------
    TAI_5dCG2P : str
        The 5dCG2P sub-protocol of the TAI protocol.
    TAI_5dCGP : str
        The 5dCGP sub-protocol of the TAI protocol.
    """

    TAI_5dCG2P = "5dCG2P"
    TAI_5dCGP = "5dCGP"
    SynchED_CP = "CP"
    SynchED_2P = "2P"


class HeiferSynchEDSubProtocol(Enum):
    """
    This enum class lists the options for different heifer reproduction sub-protocols for the SynchED program.

    Attributes
    ----------
    SynchED_CP : str
        The CP sub-protocol of the SynchED protocol.
    SynchED_2P : str
        The 2P sub-protocol of the SynchED protocol.

    """

    SynchED_CP = "CP"
    SynchED_2P = "2P"


class CowReproductionProtocol(Enum):
    """
    This enum class lists the options for different cow reproduction protocols.

    Notes
    -----
    This list includes both the protocols and their sub-protocols if they have any. The names of
    the sub-protocols are prefixed with the name of the protocol they belong to.

    Attributes
    ----------
    NONE : str
        The option that represents no other option has been set.
    ED : str
        The estrus detection reproduction protocol.
    TAI : str
        The timed artificial insemination reproduction protocol.
    ED_TAI : str
        The estrus detection followed by timed artificial insemination reproduction protocol.

    """

    NONE = "None"
    ED = "ED"
    TAI = "TAI"
    ED_TAI = "ED-TAI"


class CowPreSynchSubProtocol(Enum):
    """
    This enum class lists the options for different cow reproduction sub-protocols for the PreSynch program.

    Attributes
    ----------
    Presynch_PreSynch : str
        The PreSynch program of the Presynch protocol.
    Presynch_DoubleOvSynch : str
        The Double OvSynch program of the Presynch protocol.
    Presynch_G6G : str
        The G6G program of the Presynch protocol.
    NONE : str
        The option that represents no other option has been set.

    """

    Presynch_PreSynch = "PreSynch"
    Presynch_DoubleOvSynch = "Double OvSynch"
    Presynch_G6G = "G6G"
    NONE = "None"


class CowTAISubProtocol(Enum):
    """
    This enum class lists the options for different cow reproduction sub-protocols for the TAI program.

    Attributes
    ----------
    TAI_OvSynch_48 : str
        The OvSynch 48 program of the TAI protocol.
    TAI_OvSynch_56 : str
        The OvSynch 56 program of the TAI protocol.
    TAI_CoSynch_72 : str
        The CoSynch 72 program of the TAI protocol.
    TAI_5d_CoSynch : str
        The 5d CoSynch program of the TAI protocol.
    NONE : str
        The option that represents no other option has been set.

    """

    TAI_OvSynch_48 = "OvSynch 48"
    TAI_OvSynch_56 = "OvSynch 56"
    TAI_CoSynch_72 = "CoSynch 72"
    TAI_5d_CoSynch = "5d CoSynch"
    NONE = "None"


class CowReSynchSubProtocol(Enum):
    """
    This enum class lists the options for different cow reproduction sub-protocols for the ReSynch program.

    Attributes
    ----------
    Resynch_TAIbeforePD : str
        The TAIbeforePD resynch program used in TAI and ED-TAI protocols.
    Resynch_TAIafterPD : str
        The TAIafterPD resynch program used in TAI and ED-TAI protocols.
    Resynch_PGFatPD : str
        The PGFatPD resynch program used in TAI and ED-TAI protocols.
    NONE : str
        The option that represents no other option has been set.

    """

    Resynch_TAIbeforePD = "TAIbeforePD"
    Resynch_TAIafterPD = "TAIafterPD"
    Resynch_PGFatPD = "PGFatPD"
    NONE = "None"


class ReproStateEnum(Enum):
    """
    This enum class lists the options for different reproduction states.

    Attributes
    ----------
    NONE : str
        The state that represents no other state has been set.
    WAITING_FULL_ED_CYCLE : str
        The state that represents the animal is waiting for a full estrus cycle.
    WAITING_SHORT_ED_CYCLE : str
        The state that represents the animal is waiting for a short estrus cycle.
    WAITING_FULL_ED_CYCLE_BEFORE_OVSYNCH : str
        The state that represents the animal is waiting for a full estrus cycle before OvSynch, applicable to ED-TAI.
    IN_PRESYNCH : str
        The state that represents the animal is in a presynch program.
    HAS_DONE_PRESYNCH : str
        The state that represents the animal has done a presynch program.
    IN_OVSYNCH : str
        The state that represents the animal is in an OvSynch program.
    ESTRUS_DETECTED : str
        The state that represents that estrus has been detected.
    AFTER_AI : str
        The state that represents the animal has just been inseminated.
    FRESH : str
        The state that represents the animal is in the fresh state.
    PREGNANT : str
        The state that represents the animal is pregnant.
    ENTER_HERD_FROM_INIT : str
        The state that represents the animal has just entered the herd through initialization.

    """

    NONE = "none"
    WAITING_FULL_ED_CYCLE = "waiting for full estrus cycle"
    WAITING_SHORT_ED_CYCLE = "waiting for short estrus cycle"
    WAITING_FULL_ED_CYCLE_BEFORE_OVSYNCH = "waiting for full estrus cycle before OvSynch"
    IN_PRESYNCH = "in presynch"
    HAS_DONE_PRESYNCH = "has done presynch"
    IN_OVSYNCH = "in OvSynch"
    ESTRUS_DETECTED = "estrus detected"
    AFTER_AI = "after AI"
    FRESH = "fresh"
    PREGNANT = "pregnant"
    ENTER_HERD_FROM_INIT = "entered herd from init"
