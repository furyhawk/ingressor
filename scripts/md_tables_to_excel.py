#!/usr/bin/env python3
"""Extract tables from Markdown parts manuals and export them to Excel.

Two kinds of "component" tables are understood:

* **Part tables** -- a dedicated **Part Number** column exists; the heading
  above the table is kept as its **component**, and only the rows that
  actually carry a part number are exported (wrapped text and quantities that
  belong to a part are merged back into it).

* **Locator tables** -- no part number, but a **Landmark** / **Rep.** column
  is used to locate parts or components on an illustration (common in
  GUINAULT manuals, e.g. ``Landmark | Description | Landmark | Description``).
  Only the rows that carry a landmark are kept, and side-by-side two-panel
  legends are flattened into one ``Landmark | Description`` list.

The result is one Excel worksheet per component table.

Example
-------
    python scripts/md_tables_to_excel.py \
        "conversion_results/1. Servicing Manual TAM 7002.pdf 01072026/"*.md \
        -o tam7002_parts.xlsx

    python scripts/md_tables_to_excel.py \
        "conversion_results/GUINAULT - GPU GA180 - Operation and maintenance manual (1)/"*.md

    # also export the tables without Part Number / Landmark columns (e.g.
    # maintenance schedules), untouched, on their own sheets:
    python scripts/md_tables_to_excel.py manual.md --include-other-tables
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parent
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

from ingressor.markdown_tables import (  # noqa: E402
    extract_tables,
    export_tables_to_excel,
)


def collect_markdown(paths: list[str]) -> list[Path]:
    files: list[Path] = []
    for p in paths:
        path = Path(p)
        if path.is_dir():
            files.extend(sorted(path.rglob("*.md")))
        else:
            files.append(path)
    return [f for f in dict.fromkeys(files) if f.exists()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="md_tables_to_excel",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "markdown",
        nargs="+",
        help="one or more .md files (or folders scanned for .md files)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="output .xlsx path (default: <first input>.xlsx next to it)",
    )
    parser.add_argument(
        "--include-other-tables",
        action="store_true",
        help="also export the tables that have no Part Number and no "
        "Landmark/Rep. column (they are exported as-is on their own sheet)",
    )
    parser.add_argument(
        "--no-index",
        action="store_true",
        help="do not add the 'Index' overview sheet",
    )
    parser.add_argument("-q", "--quiet", action="store_true", help="only print errors")
    args = parser.parse_args(argv)

    files = collect_markdown(args.markdown)
    if not files:
        parser.error("no markdown files found")

    if args.output is None:
        first = files[0]
        output = first.with_suffix(".xlsx")
        if len(files) > 1:
            output = (first.parent / (first.stem + "_tables.xlsx")).resolve()
    else:
        output = Path(args.output)

    tables = []
    for f in files:
        try:
            text = f.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"error: cannot read {f}: {exc}", file=sys.stderr)
            return 2
        tables.extend(extract_tables(text, source_file=str(f)))

    if not tables:
        parser.error("no tables found in the given markdown file(s)")

    parts = [t for t in tables if t.is_parts_table]
    locators = [t for t in tables if t.is_locator_table]
    if not parts and not locators and not args.include_other_tables:
        print(
            "error: no table with a Part Number or Landmark column was found "
            "in the given file(s).",
            file=sys.stderr,
        )
        print(
            "hint: use --include-other-tables to export every table, or check "
            "that the markdown has a 'Part Number' / 'Part No.' / 'PN' / 'Code' "
            "or 'Landmark' / 'Rep.' header.",
            file=sys.stderr,
        )
        return 3

    summary = export_tables_to_excel(
        tables,
        output,
        include_other_tables=args.include_other_tables,
        write_index_sheet=not args.no_index,
    )

    if not args.quiet:
        print(f"Input markdown : {', '.join(str(f) for f in files)}")
        print(f"Excel workbook : {summary['path']}")
        print(f"Tables extracted: {len(tables)} "
              f"(parts: {len(parts)}, landmark: {len(locators)}, "
              f"other: {len(tables) - len(parts) - len(locators)})")
        index_count = 0 if args.no_index else 1
        if args.include_other_tables:
            print(f"Sheets written : {summary['workbook_sheets']} "
                  f"(parts: {summary['parts_tables']}, landmark: {summary['locator_tables']}, "
                  f"other: {summary['other_tables']}, index: {index_count})")
        else:
            print(f"Sheets written : {summary['workbook_sheets']} "
                  f"(parts: {summary['parts_tables']}, landmark: {summary['locator_tables']}, "
                  f"index: {index_count}; other tables skipped - use --include-other-tables to add them)")
        print(f"Part rows kept : {summary['parts_rows']}")
        print(f"Landmark rows  : {summary['locator_rows']}")

        warned = [t for t in (parts + locators) if t.warnings]
        if warned:
            print("\nTables needing a manual check (best-effort reconstruction):")
            for t in warned:
                print(f"  - {t.component}  [{t.source_file}:{t.source_line}]")
                for w in t.warnings:
                    print(f"      * {w}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
