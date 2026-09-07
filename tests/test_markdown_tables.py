"""Unit tests for src/ingressor/markdown_tables.py

Run with:  python -m unittest discover -s tests -v
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from ingressor.markdown_tables import (  # noqa: E402
    clean_text,
    extract_tables,
    export_tables_to_excel,
    has_part_number,
    is_part_number_token,
)


SAMPLE = """\
# Machine manual

## 1) Cooler assembly

Some intro text.

| Item # | Part Number | Désignation           | Description            | Qty |
|--------|-------------|------------------------|------------------------|-----|
| 1      | A08-0007W   | Refroidisseur hydraul. | Hydraulic cooler       | 1   |
| 2      | A04-0007T   | Valve de freinage      | Brake control valve    |     |
|        |             |                        | (with brake pedal)     | 1   |
|        | A09014Q     | Kit de joints          | Seal kit               |     |
| 3      | 510000108714| Affichage couleur      | color display          | 1   |

Note: the valve part above has no part number and must be dropped.

## 2) Driver station panel

| Item # 1 2 | Part Number 410001183677 410001183678 | Désignation Console panel A Console panel B | Description Panel A Panel B | Qty 1 1 |
|------------|---------------------------------------|---------------------------------------------|-----------------------------|---------|
| 3          | 510000108714                          | Display                                    | color display               | 1       |
"""


class TokenTests(unittest.TestCase):
    def test_real_part_numbers(self):
        for pn in (
            "410001183677",
            "058773M",
            "A02-0003K",
            "A01092Y",
            "P04-0008H",
            "T15004-SGP00702",
            "487327J",
            "003088V",
            "X22124F",
            "A09082N/00",
        ):
            self.assertTrue(is_part_number_token(pn), pn)

    def test_not_part_numbers(self):
        for token in ("1", "14", "397", "10000", "3.5m", "X22124F/00.......", "Oil", "250 h"):
            self.assertFalse(is_part_number_token(token), token)


class CleanTests(unittest.TestCase):
    def test_strips_tags_and_emphasis(self):
        self.assertEqual(clean_text("<b>Engine</b> **swap**  part"), "Engine swap part")


class ExtractTests(unittest.TestCase):
    def setUp(self):
        self.tables = extract_tables(SAMPLE, source_file="sample.md")

    def test_tables_found(self):
        self.assertEqual(len(self.tables), 2)

    def test_component_heading(self):
        self.assertEqual(self.tables[0].component, "1) Cooler assembly")
        self.assertEqual(self.tables[1].component, "2) Driver station panel")

    def test_pn_column_detected(self):
        self.assertIsNotNone(self.tables[0].pn_col)
        self.assertEqual(self.tables[0].headers[self.tables[0].pn_col], "Part Number")

    def test_wrapped_rows_merged_and_no_pn_rows_dropped(self):
        t = self.tables[0]
        rows = {row[t.pn_col]: row for row in t.rows}
        # wrapped description + qty recovered on the A04-0007T part
        valve = rows.get("A04-0007T")
        self.assertIsNotNone(valve)
        desc = " ".join(valve).lower()
        self.assertIn("with brake pedal", desc)
        # the "Seal kit" part and the display part are separate rows
        self.assertIn("A09014Q", rows)
        self.assertIn("510000108714", rows)
        # a row with no part number must not be exported
        self.assertEqual(len(t.rows), 4)  # 1,2(+merge), seal kit, display... actually count below
        self.assertFalse(any("no part number" in c.lower() for r in t.rows for c in r))

    def test_fused_header_expanded(self):
        t = self.tables[1]
        self.assertEqual(t.pn_col, 1)
        pns = [row[1] for row in t.rows]
        self.assertEqual(pns[:2], ["410001183677", "410001183678"])
        self.assertEqual(len(t.rows), 3)  # items 1,2 + item 3

    def test_plain_table_without_pn_column_is_not_parts_table(self):
        md = "# T\n\n| System | 250 h | 500 h |\n|---|---|---|\n| Engine | oil | filter |\n"
        t = extract_tables(md, source_file="x")[0]
        self.assertIsNone(t.pn_col)
        self.assertFalse(t.is_parts_table)
        self.assertFalse(t.is_locator_table)


LOCATOR_SAMPLE = """\
# 1 DESCRIPTION

## 1.2 General illustration

| Landmark | Description      | Landmark | Description      |
|----------|------------------|----------|------------------|
| 1        | Corner beacon x4 |          |                  |
|          |                  | 9        | Rubber buffer x2 |
| 2        | Antenna          | 10       | Lashing hook     |
| 3        | Bodywork         |          |                  |

## 1.8 Electrical cabinet

| Landmark | Type     | Description | Function                      |
|----------|----------|-------------|-------------------------------|
| 1        | Electric | Fuse        | 400Hz detection fuse          |
| 2        | Electric | sensor      | Aircraft connector plug cases |

## 1.9 Plain reference table

| GPU Situation | Dysfunction      |
|---------------|------------------|
| OFF           | nothing happens  |
"""


class LocatorExtractTests(unittest.TestCase):
    def setUp(self):
        self.tables = extract_tables(LOCATOR_SAMPLE, source_file="locator.md")

    def test_two_panel_flattened(self):
        t = next(t for t in self.tables if t.component == "1.2 General illustration")
        self.assertIsNone(t.pn_col)
        self.assertTrue(t.is_locator_table)
        self.assertEqual(t.headers, ["Landmark", "Description"])
        # flattened and sorted numerically (1, 2, 3, 9, 10)
        self.assertEqual([r[0] for r in t.rows], ["1", "2", "3", "9", "10"])
        self.assertEqual(t.rows[3], ["9", "Rubber buffer x2"])

    def test_single_landmark_column_kept(self):
        t = next(t for t in self.tables if t.component == "1.8 Electrical cabinet")
        self.assertTrue(t.is_locator_table)
        self.assertEqual(len(t.rows), 2)
        self.assertEqual(t.headers, ["Landmark", "Type", "Description", "Function"])

    def test_plain_table_is_other(self):
        t = next(t for t in self.tables if t.component == "1.9 Plain reference table")
        self.assertFalse(t.is_parts_table)
        self.assertFalse(t.is_locator_table)
        self.assertNotIn(t, [x for x in self.tables if x.is_component_table])

    def test_landmark_rows_only(self):
        # a landmark table with a blank / wrapped row keeps only real landmarks
        md = "# C\n\n## Legend\n\n| Landmark | Description |\n|---|---|\n| 1 | A |\n|   | continuation |\n| 2 | B |\n"
        t = extract_tables(md, source_file="x")[0]
        self.assertTrue(t.is_locator_table)
        self.assertEqual([r[0] for r in t.rows], ["1", "2"])
        self.assertEqual(t.rows[0][1], "A continuation")


LEGEND_SAMPLE = """\
# 1 ENGINE

#### TCD2013L06-4V engine

(left view)

1\\_Air filter 2\\_Oil filter cap 3\\_Exhaust manifold 4\\_Fuel supply pump

#### TCD2013L06-4V engine + radiator (right view)

1\\_Expansion tank cap 2\\_Radiator 3\\_Air cooler

Some ordinary prose mentioning 1_foo 2_bar is not a legend.

#### 3 Reference

| GPU Situation | Dysfunction      |
|---------------|------------------|
| OFF           | nothing happens  |
"""


class LegendExtractTests(unittest.TestCase):
    def test_inline_legend_under_subtitle(self):
        tables = extract_tables(LEGEND_SAMPLE, source_file="legend.md")
        legends = [t for t in tables if t.kind == "locator" and t.source_file]
        engine = next(t for t in legends if t.component.startswith("TCD2013L06-4V engine (left"))
        # component = subtitle heading + "(left view)" qualifier
        self.assertEqual(engine.component, "TCD2013L06-4V engine (left view)")
        self.assertTrue(engine.is_locator_table)
        self.assertEqual([r[0] for r in engine.rows], ["1", "2", "3", "4"])
        self.assertEqual(engine.rows[1][1], "Oil filter cap")
        self.assertEqual(engine.headers, ["Landmark", "Description"])

    def test_legend_with_three_markers(self):
        tables = extract_tables(LEGEND_SAMPLE, source_file="legend.md")
        rad = next(t for t in tables if "radiator" in t.component.lower())
        self.assertEqual(rad.component, "TCD2013L06-4V engine + radiator (right view)")
        self.assertEqual([r[0] for r in rad.rows], ["1", "2", "3"])

    def test_prose_with_few_markers_is_not_legend(self):
        tables = extract_tables(LEGEND_SAMPLE, source_file="legend.md")
        # only the two real legends + the reference table are extracted
        legends = [t for t in tables if t.is_locator_table]
        self.assertEqual(len(legends), 2)
        others = [t for t in tables if not t.is_component_table]
        self.assertTrue(any("3 Reference" == t.component for t in others))


class ExportTests(unittest.TestCase):
    def test_export_writes_workbook(self):
        from openpyxl import load_workbook

        tables = extract_tables(SAMPLE, source_file="sample.md")
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "parts.xlsx"
            summary = export_tables_to_excel(tables, out)
            self.assertTrue(out.exists())
            wb = load_workbook(out)
            # Index + 2 part tables
            self.assertEqual(len(wb.sheetnames), 3)
            # first row of each part sheet = component heading
            ws = wb[summary["path"] and "2) Driver station panel"]
            self.assertEqual(ws.cell(row=1, column=1).value, "2) Driver station panel")
            self.assertIsNotNone(ws.freeze_panes)

    def test_export_includes_locator_tables_by_default(self):
        from openpyxl import load_workbook

        tables = extract_tables(LOCATOR_SAMPLE, source_file="locator.md")
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "loc.xlsx"
            summary = export_tables_to_excel(tables, out)
            wb = load_workbook(out)
            # Index + 2 landmark tables (the "plain reference table" is skipped)
            self.assertEqual(len(wb.sheetnames), 3)
            self.assertEqual(summary["locator_tables"], 2)
            self.assertEqual(summary["other_tables"], 1)
            # landmark rows are exported (5 flattened + 2 single-column)
            self.assertEqual(summary["locator_rows"], 7)


class RealFixtureTests(unittest.TestCase):
    """End-to-end smoke test against the real servicing manual if present."""

    FIXTURE = Path(__file__).resolve().parent.parent / (
        "conversion_results/1. Servicing Manual TAM 7002.pdf 01072026/"
        "1. Servicing Manual TAM 7002.pdf 01072026.md"
    )

    def test_real_manual_extracts_parts(self):
        if not self.FIXTURE.exists():
            self.skipTest("fixture markdown not available")
        tables = extract_tables(self.FIXTURE.read_text(encoding="utf-8"), str(self.FIXTURE))
        parts = [t for t in tables if t.is_parts_table]
        self.assertGreater(len(parts), 40)
        self.assertGreater(sum(len(t.rows) for t in parts), 300)


if __name__ == "__main__":
    unittest.main()
