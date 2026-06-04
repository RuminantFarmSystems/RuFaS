from pathlib import Path
from typing import Callable, Iterable, Any

import pandas as pd
import tabulate # required for pd._to_markdown
from IPython.display import Markdown, display
from pandas import DataFrame


def read_tbl(path: str | Path, **kwargs) -> pd.DataFrame:
    """
    Imports a table as a pandas.DataFrame


    Parameters
    ----------
    path: str | Path
        the path to a file containing tabular data. The file extension is used to determine which reader function
        to use: ``pandas.read_csv`` (.csv), ``pandas.read_excel`` (.xlsx or .xls),
        or ``pandas.read_table`` (all others).
    kwargs:
        additional arguments passed to the reader function. See documentation for those functions in "See Also" to
        for the available arguments and their effects (e.g., ``help(pandas.read_csv)``).

    See Also:
    ---------
    display_md_tbl: display a data frame as a Markdown Table
    import_tbl: to read and then display a Markdown table
    pandas.read_csv: read csv files
    pandas.read_excel: read excel files
    pandas.read_table: read text tables


    Returns
    -------
    a ``pandas.DataFrame`` containing the table data

    Examples
    --------
    read_tbl("resources/table_data/example-table.csv")
    """
    path = Path(path)

    # Set some default keyword arguments
    if "keep_default_na" not in kwargs and "na_values" not in kwargs:
        # Ensure that missing values are printed they are typed into the files (i.e., not replaced with NaN)
        kwargs["keep_default_na"] = False

    # Determine which reader function to call
    reader: Callable
    if path.suffix == ".csv" :
        reader = pd.read_csv
    elif path.suffix in {".xlsx", ".xls"}:
        reader = pd.read_excel
    else:
        reader = pd.read_table

    # Try to use the read the table into a data frame
    try:
        return reader(path, **kwargs)
    except Exception as e :
        print(f"error reading table with '{reader.__module__}.{reader.__name__}':", e)
        raise


def display_md_tbl(tbl: pd.DataFrame, sep_lines_after: Iterable[int] | None = None, **kwargs) -> None:
    """
    Display a ``pandas.DataFrame`` as a Markdown table

    Parameters
    ----------
    tbl: pandas.DataFrame
        the tabular data to display
    sep_lines_after:
        a list of rows after which separating lines should be added.
    kwargs:
        additional arguments passed to ``pandas.DataFrame.to_markdown`` (and ``tabulate.tabulate``, by extension)

    Notes
    -----
    Useful ``**kwargs`` include:

        ``maxcolwidths``: an iterable of maximum widths (characters) of each column. For example,
            ``maxcolwidths = [None, None, 32, None]`` sets the 3rd column (of 4 total) to be no wider than 32
            characters. If elements in this column are longer, they will be automatically wrapped by adding line breaks
            between words when possible.

        ``colalign``: an iterable of alignments of each column. Options are "left", "right", "center", or "decimal".
            For example ``colalign = ["left", "left", "right", "decimal"]`` sets the first two columns to be
            left-aligned, the third column to be right-aligned, and the last column to be aligned at the decimal
            if possible.

    ``pandas.DataFrame.to_markdown`` passes arguments to ``tabulate.tabulate``, which ``to_markdown`` uses
    internally. So, for a full list of accepted arguments, you should see the ``tabulate`` documentation.

    Returns
    -------
    A display of the Markdown table will be created using ``IPython.display.display``, which
    properly displays the tables in notebooks and Quarto documents.

    See Also
    --------
    read_tbl: to read a table from a file to a data frame
    import_tbl: to read and then display a Markdown table
    pandas.DataFrame.to_markdown: convert a data frame into a Markdown table
    tabulate.tabulate: create a generic Markdown table
    """
    # Ensure correct type
    if not isinstance(tbl, pd.DataFrame):
        raise TypeError("tbl must be a pandas.DataFrame")

    # Set some default keyword arguments, if not provided
    if "index" not in kwargs:
        # don't print row numbers
        kwargs["index"] = False

    if "tablefmt" not in kwargs:
        # default to using the grid tables (with column alignment enabled)
        kwargs["tablefmt"] = "colon_grid"

    tbl = _insert_lines(tbl, sep_lines_after)

    # Get the Markdown table
    md_tbl = tbl.to_markdown(**kwargs)

    # Return a display of the table
    display(Markdown(md_tbl))


def _insert_lines(tbl: pd.DataFrame, lines_after: Iterable[int] | None) -> DataFrame | Any:
    """
    Add lines after specific rows in a table. Useful for displaying row-merged tables in markdown

    Parameters
    ----------
    tbl: pandas.DataFrame
        the table to insert lines into
    lines_after: Iterable[int]
        a list of the rows after which blank lines should be inserted


    Returns
    -------
    The original pandas.DataFrame with blank lines (``tabulate.SEPARATING_LINE``) inserted.
    """
    if lines_after is not None:
        start_split = 0
        tbl_slices = []
        blank_row = [tabulate.SEPARATING_LINE for i in range(tbl.shape[1])]
        blank_row = pd.DataFrame([blank_row], columns=tbl.columns)
        for split in lines_after:
            this_slice = tbl[start_split:split + 1]
            tbl_slices.append(this_slice)
            start_split = split + 1
        tbl_slices.append(tbl[start_split:])

        new_tbl = tbl_slices[0]
        for i in range(len(tbl_slices) - 1):
            this_slice = pd.concat([blank_row, tbl_slices[i + 1]]).reset_index(drop=True)
            new_tbl = pd.concat([new_tbl, this_slice]).reset_index(drop=True)
        tbl = new_tbl
    return tbl


def import_table(path: str | Path, read_opts: dict | None = None, **display_opts):
    """
    Import a table (from csv, excel, or other file) into a Markdown (e.g., quarto) display

    Notes
    -----
    This function is a convenience wrapper for ``read_tbl`` and ``display_md_tbl``. It tries to use
    sensible defaults to reduce the amount of code needed to make nice figures in quarto documents.

    Useful arguments to control the alignment and width of columns are ``colalign`` and ``maxcolwidths``.

    Parameters
    ----------
    path: str | Path
        the path to a file containing tabular data
    read_opts: dict | None
        a dictionary of named options for reading the file, passed to the ``**kwargs`` argument of
        ``read_tbl``.
    display_opts:
        Options for how to display the table, that are passed to ``display_md_tbl``.

    See Also
    -------
    read_tbl: to read a table from a file to a data frame
    display_md_tbl: display a data frame as a Markdown Table

    Examples
    --------
    # The following examples are expected to be called from within a qmd file or Jupyter notebook:

    ## use default settings
    import_table("resources/table_data/example-table.csv")

    ## align the columns and set the 2nd column to be no longer than 30 characters
    import_table(
        "resources/table_data/example-table.csv",
        colalign = ["left", "left", "right"],
        maxcolwidths = [None, 30, None]
    )
    """

    # Convert read_args into empty dictionary if None
    read_opts = {} if read_opts is None else read_opts

    # Read the table, passing the read_args
    tbl = read_tbl(path, **read_opts)

    # display the table
    display_md_tbl(tbl, **display_opts)

    
def display_mdtab(tab: pd.DataFrame, **kwargs) -> None:
    """
    display a markdown table (deprecated: use display_md_tbl instead)
    """
    tab = tab.fillna("")
    tab = tab.map(
        lambda x: str(x).replace("\n", "<br>") if pd.notna(x) else ""
    )

    print(tab.to_markdown(index=False, **kwargs))
