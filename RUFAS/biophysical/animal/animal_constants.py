# EVENTS
# calf
WEAN_DAY = "wean day"
STILL_BIRTH = "still birth happened"
NUM_CALVES_BORN_NOTE = "number of calves born so far"

# reproduction
INSEMINATED_W_BASE = "inseminated with "

BREEDING_START = "breeding start"
DO_NOT_BREED = "mark as do not breed"

ESTRUS_DETECTED_NOTE = "estrus detected"
ESTRUS_NOT_DETECTED_NOTE = "estrus not detected"
BASIC_ESTRUS_NOTE = "estrus"

# When days born == estrus day
ESTRUS_OCCURRED_NOTE = "estrus occurred"

# When simulate_estrus() is called
ESTRUS_DAY_SCHEDULED_NOTE = "estrus day scheduled"

AI_DAY_SCHEDULED_NOTE = "AI day scheduled"
AI_PERFORMED_NOTE = "AI performed"
TAI_AFTER_ESTRUS_NOT_DETECTED_IN_SYNCH_ED_NOTE = "TAI after estrus not detected in SynchED"
REBREEDING_NOTE = "rebreeding start"
SETTING_REPRO_PROGRAM_NOTE = "setting repro program"

ESTRUS_AFTER_AI_NOTE = "estrus after AI"
ESTRUS_AFTER_ABORTION_NOTE = "estrus after abortion"
FIRST_ESTRUS_NOTE = "first estrus"
ESTRUS_AFTER_CALVING_NOTE = "1st estrus after calving"
ESTRUS_BEFORE_VOLUNTARY_WAITING_PERIOD_NOTE = "estrus occurred before the end of the voluntary waiting period"
ESTRUS_AFTER_PGF_NOTE = "estrus after PGF"
SIMULATE_ESTRUS_AFTER_PGF_NOTE = "simulating estrus after PGF"
ESTRUS_NOT_DETECTED_BETWEEN_VWP_AND_OVSYNCH_START_DAY_NOTE = "estrus not detected between VWP and OvSynch start day"
NO_ED_INSTITUTED_BEFORE_OVSYNCH_IN_ED_TAI_NOTE = "No ED instituted before OvSynch in ED-TAI"
CANCEL_ESTRUS_DETECTION_NOTE = "canceled estrus detection"

# TAI injections
INJECT_GNRH = "inject GnRH"
INJECT_PGF = "inject PGF"

# heifer repro
INJECT_CIDR = "inject CIDR"

# presynch protocols
PRESYNCH_PERIOD_START = "Presynch period started"
PRESYNCH_PERIOD_END = "Presynch period ended"
PRESYNCH_END = "Presynch ended"
DOUBLE_OVSYNCH_END = "Double OvSynch ended"
C6G_END = "G6G ended"
OVSYNCH_PERIOD_START_NOTE = "OvSynch period started"
OVSYNCH_PERIOD_END_NOTE = "OvSynch period ended"

# ReSynch protocols
SETTING_UP_OVSYNCH_PROGRAM_IN_ADVANCE_NOTE = "setting up OvSynch program in advance"
DISCONTINUE_OVSYNCH_PROGRAM_IN_TAI_BEFORE_PD_NOTE = "discontinued OvSynch program"
DECREASE_CONCEPTION_RATE = "decrease OvSynch program conception rate"

# Conception outcomes
SUCCESSFUL_CONCEPTION = "successful conception"
FAILED_CONCEPTION = "failed conception"

# pregnancy
HEIFER_PREG = "heifer pregnant"
HEIFER_NOT_PREG = "heifer not pregnant"
COW_PREG = "cow pregnant"
COW_NOT_PREG = "cow not pregnant"

PREG_CHECK_1_PREG = "pregnancy check 1: confirmed"
PREG_LOSS_BEFORE_1 = "pregnancy loss happened before 1st pregnancy check"
PREG_CHECK_1_NOT_PREG = "pregnancy check 1: not pregnant"
PREG_CHECK_2_PREG = "pregnancy check 2: confirmed"
PREG_LOSS_BTWN_1_AND_2 = "pregnancy loss happened between 1st and 2nd pregnancy check"
PREG_CHECK_3_PREG = "pregnancy check 3: confirmed"
PREG_LOSS_BTWN_2_AND_3 = "pregnancy loss happened between 2nd and 3rd pregnancy check"

# life cycle
INIT_HERD = "entered herd through initialization"
ENTER_HERD = "entered herd"
MATURE_BODY_WEIGHT_REGULAR = "mature body reached"
HEIFERII_TO_III = "heiferII moving to heiferIII"
NEW_BIRTH = "new birth, start milking"
DRY = "dry"

# culling
HEIFER_REPRO_CULL = "culled for heifer reproductive problem"
LOW_PROD_CULL = "culled for low production"
DEATH_CULL = "culled for death"
LAMENESS_CULL = "culled for lameness"
INJURY_CULL = "culled for injury"
MASTITIS_CULL = "culled for mastitis"
DISEASE_CULL = "culled for disease"
UDDER_CULL = "culled for udder"
UNKNOWN_CULL = "culled for unknown"

# STATS
STDI = 2

# DEFAULTS
# The number of days to start a TAI program before the first preg check, used in TAIbeforePD resynch protocol
DAYS_BEFORE_FIRST_PREG_CHECK_TO_START_TAI = 6

# Maximum estrus cycle length when a PGF injection is given after a failed preg check, used in PGFatPD resynch protocol
MAX_ESTRUS_CYCLE_LENGTH_PGF_AT_PREG_CHECK = 7

# The number of days during the herd generation process before we start saving heiferIIIs to replacement herd.
DAYS_TO_START_REPLACEMENT_HERD = 3000

# The buying and selling threshold of for herd-size maintenance
BUYING_THRESHOLD = 1.01
SELLING_THRESHOLD = 1.03

MITS_PARAMETER_A = 45.98
"""
The parameter 'a' in the Mitscherlich Model 3 (Mills et al., 2003).
"""

MITS_PARAMETER_B = 0
"""
The parameter 'b' in the Mitscherlich Model 3 (Mills et al., 2003).
"""
