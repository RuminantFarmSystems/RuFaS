import os

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))

PRODUCE_GRAPHICS = True  # optional global flag to suppress graphics
# TODO: "producing graphics" message and directory structure still generated when PRODUCE_GRAPHICS = True - GitHub Issue # 211

PRINT_STATUS_MESSAGES = True  # optional flag to print status messages - TODO: unimplemented - GitHub Issue #211

OUT_DIR = os.path.join(ROOT_DIR, "output")  # where should output files go? - TODO: unimplemented - GitHub Issue #211
