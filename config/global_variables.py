import os
ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))

SUPPRESS_GRAPHICS = False  # optional global flag to suppress graphics
# TODO: "producing graphics" message and directory structure still generated when SUPPRESS_GRAPHICS = True

PRINT_STATUS_MESSAGES = True  # optional flag to print status messages - TODO: unimplemented

OUT_DIR = os.path.join(ROOT_DIR, "output")  # where should output files go? - TODO: unimplemented
