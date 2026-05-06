import pandas as pd
import tabulate
from IPython.display import Markdown, display

# TODO: This file is not finished (1 May, 2026) - revisit.

def display_mdtab(tab: pd.DataFrame, **kwargs) -> None:
    tab = tab.fillna("")
    tab = tab.map(
        lambda x: str(x).replace("\n", "<br>") if pd.notna(x) else ""
    )

    print(tab.to_markdown(index=False, **kwargs))


if __name__ == "__main__":
    from pathlib import Path

    tbl_path = Path("quarto_python_test/out.csv")

    tbl = pd.read_csv(
        tbl_path,
        dtype=str,
        keep_default_na=False
    )

    display_mdtab(
        tbl,
        colalign=("left", "left", "right")
    )