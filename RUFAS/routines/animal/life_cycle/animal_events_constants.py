"""
RUFAS: Ruminant Farm Systems Model
File name: animal_events_constants.py
Author(s): Militsa Sotirova, militsasotirova@gmail.com
Description: These constants are all of the event descriptions for the animal
    classes.
"""
# calf
WEAN_DAY = "wean day"
STILL_BIRTH = "still birth"


# reproduction
INSEMINATED_W_BASE = "inseminated with "

BREEDING_START = "breeding started"
DO_NOT_BREED = "do not breed"

ESTRUS_DETECTED = "estrus detected"
BASIC_ESTRUS_NOTE = "estrus"
ESTRUS_AFTER_AI_NOTE = "estrus after AI"
ESTRUS_AFTER_ABORTION_NOTE = "estrus after abortion"
FIRST_ESTRUS_NOTE = "first estrus"
ESTRUS_AFTER_CALVING_NOTE = "1st estrus after calving"
ESTRUS_BEFORE_VWP_NOTE = "estrus occurred before vwp"
ESTRUS_AFTER_PGF_NOTE = "estrus after PGF"

INJECT_GNRH = "inject GnRH"
INJECT_PGF = "inject PGF"
ESTRUS_OCCURRED = "estrus occurred"
INJECT_CIDR = "inject CIDR"

PRESYNCH_END = "presynch ended"
DOUBLE_OVSYNCH_END = "double OvSynch ended"
C6G_END = "G6G ended"


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
MATURE_BODY_WEIGHT_EARLY = "mature body weight reached prior to grow end day"
MATURE_BODY_WEIGHT_REGULAR = "mature body reached"
HEIFERII_TO_III = "heiferII moving to heiferIII"
NEW_BIRTH = "new birth, start milking"
DRY = "dry"


# culling
CULL_REASON_BASE = "culled for "
HEIFER_REPRO_CULL = "culled for heifer reproduction problem"
LOW_PROD_CULL = "culled for low production"


# potentially will be deleted (referenced only in commented code)
COW_REPRO_CULL = "cull for cow reproduction problem"
