#!/usr/bin/env python3
import sys

from main import run_rufas
from pathlib import Path

# Helper functions and classes for evaluation
## TODO

# Run the script code
if __name__ == "__main__":

    # Pre processing
    ## TODO

    print(sys.argv[1:])

    # Run the RuFaS model within the eval_CS folder.
    run_rufas(
        metapath = Path("eval_CS/inputs/metadata.json"),
        out_dir = Path("eval_CS/outputs/"),
        log_dir = Path("eval_CS/logs/")
    )

    # Post-processing
    ## TODO
