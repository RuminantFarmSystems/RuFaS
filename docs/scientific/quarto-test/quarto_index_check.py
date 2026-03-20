"""
NOTE:
- all labels
- duplicate labels
- references that don not point to any label
- labels that are never referenced
- a CSV you can open in Excel
"""

from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path

# --- Configure this path ---
PROJECT_ROOT = Path(__file__).resolve().parent

# --- Patterns ---
# Matches labels in attribute blocks like {#fig-animal-icon ...}
LABEL_PATTERN = re.compile(r"\{#([A-Za-z0-9_-]+)\b")

# Matches Quarto cross-references like @fig-animal-icon
REF_PATTERN = re.compile(r"@([A-Za-z0-9_-]+)\b")

# Optional: skip code fences if desired
CODE_FENCE_PATTERN = re.compile(r"```.*?```", re.DOTALL)


def infer_label_type(label: str) -> str:
    if label.startswith("fig-"):
        return "Figure"
    if label.startswith("tbl-"):
        return "Table"
    if label.startswith("eq-"):
        return "Equation"
    if label.startswith("sec-"):
        return "Section"
    return "Other"


def find_line_number(text: str, position: int) -> int:
    return text.count("\n", 0, position) + 1


def scan_qmd_files(project_root: Path) -> tuple[list[dict], list[dict]]:
    labels: list[dict] = []
    refs: list[dict] = []

    qmd_files = sorted(project_root.rglob("*.qmd"))

    for file_path in qmd_files:
        text = file_path.read_text(encoding="utf-8")

        # If you want to ignore labels/refs inside fenced code blocks, uncomment:
        # searchable_text = re.sub(CODE_FENCE_PATTERN, "", text)
        searchable_text = text

        for match in LABEL_PATTERN.finditer(searchable_text):
            label = match.group(1)
            labels.append(
                {
                    "label": label,
                    "type": infer_label_type(label),
                    "file": str(file_path.relative_to(project_root)),
                    "line": find_line_number(searchable_text, match.start()),
                }
            )

        for match in REF_PATTERN.finditer(searchable_text):
            ref = match.group(1)
            refs.append(
                {
                    "reference": ref,
                    "file": str(file_path.relative_to(project_root)),
                    "line": find_line_number(searchable_text, match.start()),
                }
            )

    return labels, refs


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    if not PROJECT_ROOT.exists():
        raise FileNotFoundError(f"Project root not found: {PROJECT_ROOT}")

    labels, refs = scan_qmd_files(PROJECT_ROOT)

    label_to_rows: dict[str, list[dict]] = defaultdict(list)
    for row in labels:
        label_to_rows[row["label"]].append(row)

    ref_to_rows: dict[str, list[dict]] = defaultdict(list)
    for row in refs:
        ref_to_rows[row["reference"]].append(row)

    all_label_names = set(label_to_rows)
    all_ref_names = set(ref_to_rows)

    duplicates: list[dict] = []
    for label, rows in label_to_rows.items():
        if len(rows) > 1:
            for row in rows:
                duplicates.append(
                    {
                        "label": label,
                        "type": row["type"],
                        "file": row["file"],
                        "line": row["line"],
                        "count": len(rows),
                    }
                )

    missing_refs: list[dict] = []
    for ref, rows in ref_to_rows.items():
        if ref not in all_label_names:
            for row in rows:
                missing_refs.append(
                    {
                        "reference": ref,
                        "file": row["file"],
                        "line": row["line"],
                    }
                )

    unused_labels: list[dict] = []
    for label, rows in label_to_rows.items():
        if label not in all_ref_names:
            for row in rows:
                unused_labels.append(
                    {
                        "label": label,
                        "type": row["type"],
                        "file": row["file"],
                        "line": row["line"],
                    }
                )

    output_dir = PROJECT_ROOT / "reference-audit"
    output_dir.mkdir(exist_ok=True)

    write_csv(
        output_dir / "all_labels.csv",
        labels,
        ["label", "type", "file", "line"],
    )
    write_csv(
        output_dir / "all_references.csv",
        refs,
        ["reference", "file", "line"],
    )
    write_csv(
        output_dir / "duplicate_labels.csv",
        duplicates,
        ["label", "type", "file", "line", "count"],
    )
    write_csv(
        output_dir / "missing_references.csv",
        missing_refs,
        ["reference", "file", "line"],
    )
    write_csv(
        output_dir / "unused_labels.csv",
        unused_labels,
        ["label", "type", "file", "line"],
    )

    print("\nQuarto reference audit complete.")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Labels found: {len(labels)}")
    print(f"References found: {len(refs)}")
    print(f"Duplicate labels: {len(duplicates)}")
    print(f"Missing references: {len(missing_refs)}")
    print(f"Unused labels: {len(unused_labels)}")
    print(f"CSV output folder: {output_dir}\n")

    if duplicates:
        print("Duplicate labels:")
        for row in duplicates[:10]:
            print(f"  {row['label']} -> {row['file']}:{row['line']}")
        if len(duplicates) > 10:
            print("  ...")

    if missing_refs:
        print("\nMissing references:")
        for row in missing_refs[:10]:
            print(f"  @{row['reference']} -> {row['file']}:{row['line']}")
        if len(missing_refs) > 10:
            print("  ...")

    if unused_labels:
        print("\nUnused labels:")
        for row in unused_labels[:10]:
            print(f"  {row['label']} -> {row['file']}:{row['line']}")
        if len(unused_labels) > 10:
            print("  ...")


if __name__ == "__main__":
    main()