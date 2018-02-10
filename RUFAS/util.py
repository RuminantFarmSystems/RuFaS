import sys
from pathlib import Path

def get_base_dir():
    
    # frozen
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).resolve().parent
    
    # unfrozen
    else:
        return Path(__file__).resolve().parents[1]