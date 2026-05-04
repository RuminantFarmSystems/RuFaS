import pandas as pd
import tabulate
from IPython.display import Markdown, display

# TODO: This file is not finished (1 May, 2026) - revisit.

def display_mdtab(tab: pd.DataFrame, **kwargs) -> None:
    print(tab.to_markdown(index = False, **kwargs))

if __name__ == '__main__':
    from pathlib import Path

    tbl_path = Path("quarto_python_test/out.csv")
    tbl = pd.read_csv(tbl_path)

    display_mdtab(tbl, colalign = ("left", "left", "right"), maxcolwidths = [None, 40, None])
