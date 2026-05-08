from __future__ import annotations

import argparse
import math
import textwrap
from pathlib import Path
from typing import Iterable

import pandas as pd


def normalize_cell(value: object) -> str:
    """Convert cell values to clean strings for table output."""
    if pd.isna(value):
        return ""
    text = str(value).replace("\r\n", "\n").replace("\r", "\n").strip()
    return text


def wrap_cell(text: str, width: int) -> list[str]:
    """
    Wrap a cell to a fixed width while preserving paragraph breaks.
    Empty text becomes a single blank line.
    """
    if not text:
        return [""]

    paragraphs = text.split("\n")
    wrapped_lines: list[str] = []

    for para in paragraphs:
        para = para.strip()
        if not para:
            wrapped_lines.append("")
            continue

        lines = textwrap.wrap(
            para,
            width=width,
            break_long_words=True,
            break_on_hyphens=False,
        )
        wrapped_lines.extend(lines if lines else [""])

    return wrapped_lines or [""]


def format_row(cells: list[str], widths: list[int]) -> list[str]:
    """
    Convert a logical row into one or more physical table lines.
    """
    wrapped_columns = [wrap_cell(cell, width) for cell, width in zip(cells, widths)]
    row_height = max(len(col) for col in wrapped_columns)

    padded_columns: list[list[str]] = []
    for col, width in zip(wrapped_columns, widths):
        padded = col + [""] * (row_height - len(col))
        padded_columns.append([line.ljust(width) for line in padded])

    rendered_lines = []
    for i in range(row_height):
        parts = [f" {padded_columns[col_idx][i]} " for col_idx in range(len(widths))]
        rendered_lines.append("|" + "|".join(parts) + "|")

    return rendered_lines


def make_border(widths: list[int], char: str = "-") -> str:
    return "+" + "+".join(char * (w + 2) for w in widths) + "+"


def dataframe_to_grid_table(
    df: pd.DataFrame,
    caption: str | None = None,
    label: str | None = None,
    widths: list[int] | None = None,
) -> str:
    """
    Convert a DataFrame into a Pandoc grid table for Quarto.
    """
    headers = [str(col) for col in df.columns]

    if widths is None:
        # Sensible defaults based on content length, capped for readability.
        widths = []
        for col in df.columns:
            max_len = max(
                [len(str(col))]
                + [len(normalize_cell(v)) for v in df[col].tolist()]
            )
            widths.append(min(max(max_len, 8), 40))

    if len(widths) != len(headers):
        raise ValueError("Number of widths must match number of columns.")

    lines: list[str] = []

    lines.append(make_border(widths, "-"))
    lines.extend(format_row(headers, widths))
    lines.append(make_border(widths, "="))

    for _, row in df.iterrows():
        cells = [normalize_cell(v) for v in row.tolist()]
        lines.extend(format_row(cells, widths))
        lines.append(make_border(widths, "-"))

    if caption:
        if label:
            lines.append("")
            lines.append(f": {caption} {{#{label}}}")
        else:
            lines.append("")
            lines.append(f": {caption}")

    return "\n".join(lines)


def parse_widths(raw: str | None, ncols: int) -> list[int] | None:
    if raw is None:
        return None
    widths = [int(x.strip()) for x in raw.split(",")]
    if len(widths) != ncols:
        raise ValueError(
            f"Expected {ncols} widths, but got {len(widths)}: {widths}"
        )
    return widths


def load_table(path: Path, sheet_name: str | None = None) -> pd.DataFrame:
    suffix = path.suffix.lower()

    if suffix == ".csv":
        try:
            return pd.read_csv(
                path,
                dtype=str,
                keep_default_na=False,
                encoding="utf-8",
            )
        except UnicodeDecodeError:
            return pd.read_csv(
                path,
                dtype=str,
                keep_default_na=False,
                encoding="cp1252",
            )

    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(
            path,
            sheet_name=sheet_name or 0,
            dtype=str,
        ).fillna("")

    raise ValueError("Input must be a .csv, .xlsx, or .xls file.")

def make_markdown_table(
    input_file: str,
    sheet: str | None = None,
    colalign: tuple[str, ...] | None = None,
    maxcolwidths: list[int | None] | None = None,
) -> str:
    """
    Load a CSV/Excel file and return a markdown table string.
    Designed for use inside Quarto Python chunks.
    """
    df = load_table(Path(input_file), sheet_name=sheet)

    df = df.fillna("")
    df = df.map(lambda x: "" if pd.isna(x) else str(x).replace("\n", " "))

    return df.to_markdown(
        index=False,
        colalign=colalign,
        maxcolwidths=maxcolwidths,
    )

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a Quarto/Pandoc grid table from CSV or Excel."
    )
    parser.add_argument("input_file", help="Path to CSV or Excel file")
    parser.add_argument(
        "--sheet",
        help="Excel sheet name (optional)",
        default=None,
    )
    parser.add_argument(
        "--widths",
        help="Comma-separated column widths, e.g. 30,42,10,6,12",
        default=None,
    )
    parser.add_argument(
        "--caption",
        help="Optional table caption",
        default=None,
    )
    parser.add_argument(
        "--label",
        help="Optional table label without braces, e.g. tbl-animal-grp-inputs",
        default=None,
    )
    parser.add_argument(
        "--output",
        help="Optional output text file path",
        default=None,
    )

    args = parser.parse_args()

    input_path = Path(args.input_file)
    df = load_table(input_path, sheet_name=args.sheet)

    widths = parse_widths(args.widths, len(df.columns))
    grid_table = dataframe_to_grid_table(
        df,
        caption=args.caption,
        label=args.label,
        widths=widths,
    )

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(grid_table, encoding="utf-8")
        print(f"Wrote grid table to: {output_path}")
    else:
        print(grid_table)


if __name__ == "__main__":
    main()