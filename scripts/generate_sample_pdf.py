#!/usr/bin/env python3
"""Generate a rich sample PDF for PDF conversion testing."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image as ReportLabImage
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "samples"
IMAGE_DIR = OUTPUT_DIR / "images"
OUTPUT_PATH = OUTPUT_DIR / "sample-pdf-with-images-tables.pdf"


def make_line_chart(path: Path) -> None:
    width, height = 720, 300
    image = Image.new("RGB", (width, height), "white")
    drawer = ImageDraw.Draw(image)

    pad_left, pad_top, pad_right, pad_bottom = 60, 42, 42, 52
    plot_left = pad_left
    plot_top = pad_top
    plot_right = width - pad_right
    plot_bottom = height - pad_bottom

    drawer.rectangle(
        (pad_left, pad_top, width - pad_right, height - pad_bottom),
        fill=(245, 248, 252),
        outline=(204, 214, 224),
        width=1,
    )

    axes = [
        (plot_left, plot_bottom, plot_right, plot_bottom),
        (plot_left, plot_top, plot_left, plot_bottom),
    ]
    for x1, y1, x2, y2 in axes:
        drawer.line((x1, y1, x2, y2), fill=(80, 92, 110), width=2)

    x_points = [plot_left + 50, plot_left + 150, plot_left + 250, plot_left + 350, plot_left + 450, plot_left + 550]
    y_points = [plot_bottom - 30, plot_bottom - 80, plot_bottom - 140, plot_bottom - 100, plot_bottom - 180, plot_bottom - 220]
    for i in range(len(x_points)):
        drawer.text((x_points[i] - 15, plot_bottom + 12), str(i + 1), fill=(60, 72, 90))

    for y in range(1, 5):
        y_val = plot_bottom - (y * 40)
        drawer.line((plot_left, y_val, plot_right, y_val), fill=(220, 226, 235), width=1)

    for idx in range(len(x_points) - 1):
        x1, y1 = x_points[idx], y_points[idx]
        x2, y2 = x_points[idx + 1], y_points[idx + 1]
        drawer.line((x1, y1, x2, y2), fill=(51, 102, 204), width=4)
        drawer.ellipse((x1 - 5, y1 - 5, x1 + 5, y1 + 5), fill=(51, 102, 204))
        if idx == 2:
            drawer.ellipse((x2 - 7, y2 - 7, x2 + 7, y2 + 7), fill=(245, 166, 35), outline=(180, 120, 20), width=2)

    drawer.text((plot_left, 10), "Traffic and engagement trend", fill=(40, 44, 52), anchor="la")
    drawer.text((plot_left, plot_bottom + 28), "Weeks", fill=(60, 72, 90))
    drawer.text((10, plot_top + 12), "Visits", fill=(60, 72, 90))
    image.save(path)


def make_bar_chart(path: Path) -> None:
    width, height = 720, 300
    image = Image.new("RGB", (width, height), "white")
    drawer = ImageDraw.Draw(image)

    pad_left, pad_top, pad_right, pad_bottom = 60, 48, 42, 54
    plot_left = pad_left
    plot_top = pad_top
    plot_right = width - pad_right
    plot_bottom = height - pad_bottom
    chart_height = plot_bottom - plot_top
    drawer.rectangle((plot_left, plot_top, plot_right, plot_bottom), fill=(248, 250, 252), outline=(210, 216, 225), width=1)

    bars = [180, 220, 260, 210, 290, 240]
    bar_width = 52
    categories = ["A", "B", "C", "D", "E", "F"]
    max_bar = max(bars)

    for i, val in enumerate(bars):
        x0 = plot_left + 40 + i * 86
        y0 = plot_bottom - (val / max_bar) * (chart_height - 20)
        drawer.rounded_rectangle((x0, y0, x0 + bar_width, plot_bottom), radius=8, fill=(91, 146, 229), outline=(68, 112, 186), width=2)
        drawer.text((x0 + 18, plot_bottom + 10), categories[i], fill=(60, 72, 90))

    for y in range(1, 6):
        tick = plot_bottom - y * (chart_height / 5)
        drawer.line((plot_left, tick, plot_right, tick), fill=(220, 226, 235), width=1)

    drawer.text((plot_left, 12), "Regional performance", fill=(40, 44, 52))
    drawer.text((plot_left, plot_bottom + 28), "Region", fill=(60, 72, 90))
    drawer.text((8, plot_top + 30), "Score", fill=(60, 72, 90))
    image.save(path)


def draw_arrow(drawer: ImageDraw.ImageDraw, x1: int, y1: int, x2: int, y2: int, color: tuple[int, int, int], width: int = 3) -> None:
    drawer.line((x1, y1, x2, y2), fill=color, width=width)
    angle = (y2 - y1, x2 - x1)
    if angle[1] == 0:
        return
    dx = x2 - x1
    dy = y2 - y1
    length = (dx * dx + dy * dy) ** 0.5
    if length == 0:
        return
    ux = dx / length
    uy = dy / length
    px = x2 - ux * 12
    py = y2 - uy * 12
    left_x = px - uy * 8
    left_y = py + ux * 8
    right_x = px + uy * 8
    right_y = py - ux * 8
    drawer.polygon([(x2, y2), (left_x, left_y), (right_x, right_y)], fill=color)


def make_process_diagram(path: Path) -> None:
    width, height = 720, 300
    image = Image.new("RGB", (width, height), "white")
    drawer = ImageDraw.Draw(image)

    drawer.text((32, 18), "Workflow overview", fill=(42, 52, 64))
    box_specs = [
        (40, 70, 180, 160, "Ingest"),
        (220, 70, 360, 160, "Normalize"),
        (400, 70, 540, 160, "Analyze"),
        (580, 70, 680, 160, "Export"),
    ]
    for index, (left, top, right, bottom, label) in enumerate(box_specs):
        drawer.rounded_rectangle((left, top, right, bottom), radius=18, fill=(240, 246, 255), outline=(100, 146, 235), width=2)
        drawer.text(((left + right) / 2, (top + bottom) / 2), label, fill=(32, 52, 90), anchor="mm")
        if index < len(box_specs) - 1:
            next_left = box_specs[index + 1][0]
            draw_arrow(drawer, right, (top + bottom) / 2, next_left, (top + bottom) / 2, (90, 130, 180), 3)

    drawer.text((50, 220), "Input", fill=(65, 80, 95))
    drawer.text((560, 220), "Output", fill=(65, 80, 95))
    image.save(path)


def create_images() -> dict[str, Path]:
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    file_paths = {
        "traffic": IMAGE_DIR / "traffic_chart.png",
        "regional": IMAGE_DIR / "regional_chart.png",
        "workflow": IMAGE_DIR / "workflow_diagram.png",
    }
    make_line_chart(file_paths["traffic"])
    make_bar_chart(file_paths["regional"])
    make_process_diagram(file_paths["workflow"])
    return file_paths


def build_story(images: dict[str, Path]):
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "SampleTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        alignment=1,
        spaceAfter=18,
    )
    body_style = ParagraphStyle(
        "BodyText",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=15,
        spaceAfter=12,
        textColor=colors.HexColor("#1F2937"),
    )
    caption_style = ParagraphStyle(
        "Caption",
        parent=styles["BodyText"],
        fontName="Helvetica-Oblique",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#4B5563"),
        alignment=1,
        spaceAfter=14,
    )

    story = [
        Paragraph("Sample PDF for Testing", title_style),
        Paragraph(
            "This document exists to validate PDF extraction, layout handling, and OCR coverage in documents containing both narrative text and structured elements. It includes a title, paragraphs, tables, captioned images, and a footer so it can be used to test conversion quality across multiple page layouts.",
            body_style,
        ),
        Paragraph(
            "The goal is to exercise common ingestion behaviors such as text flow across columns, page headers and footers, figure captions, and table recognition. These sample elements are intentionally varied so that a converter can be checked for alignment, ordering, and readability under realistic conditions.",
            body_style,
        ),
        Paragraph(
            "In practical deployments, PDF files often mix narrative content with charts, summary tables, and callouts. This sample is designed to reflect that mix while remaining compact enough for quick testing and iteration.",
            body_style,
        ),
    ]

    for label, path in [("Figure 1. Monthly engagement trend.", images["traffic"]), ("Figure 2. Regional performance profile.", images["regional"]), ("Figure 3. Workflow overview and extraction pipeline.", images["workflow"])]:
        story.append(Spacer(1, 8))
        story.append(ReportLabImage(str(path), width=5.8 * inch, height=2.4 * inch, kind="proportional"))
        story.append(Paragraph(label, caption_style))

    story.extend([
        Paragraph("The first table summarizes the core project milestones for the current testing cycle. It is intentionally small enough to confirm column detection without overwhelming the page layout.", body_style),
        Table(
            [
                ["Phase", "Owner", "Status", "Due"],
                ["Discovery", "Alex", "Complete", "2026-01-09"],
                ["Prototype", "Jamie", "Complete", "2026-01-23"],
                ["Validation", "Priya", "In Progress", "2026-02-05"],
                ["Launch", "Morgan", "Pending", "2026-02-18"],
            ],
            colWidths=[1.8 * inch, 1.4 * inch, 1.5 * inch, 1.5 * inch],
        ),
    ])
    story[-1].setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F5FA8")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.8, colors.HexColor("#CBD5E1")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#F8FAFC"), colors.white]),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(Spacer(1, 12))
    story.append(
        Paragraph(
            "The second table records a compact view of weekly totals and resource allocation. It is useful for testing whether a converter preserves header structure, row grouping, and the ordering of numeric data.",
            body_style,
        )
    )
    story.append(
        Table(
            [
                ["Week", "Documents", "Avg. Review Time", "Success Rate"],
                ["W1", "320", "4.2h", "98%"],
                ["W2", "410", "3.9h", "99%"],
                ["W3", "470", "3.5h", "99%"],
                ["W4", "540", "3.1h", "100%"],
            ],
            colWidths=[1.1 * inch, 1.5 * inch, 2.0 * inch, 1.5 * inch],
        )
    )
    story[-1].setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F766E")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.8, colors.HexColor("#D1FAE5")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#F0FDF4"), colors.white]),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.extend([
        Spacer(1, 10),
        Paragraph(
            "This sample also tests text wrapping near images and tables so the page composition can be evaluated on document ingestion pipelines. Footers and page numbers should remain legible and stable regardless of page count.",
            body_style,
        ),
        Paragraph(
            "Use this PDF as a compact benchmark for verifying that new extraction or conversion logic preserves captions, table structure, and document readability in a single pass.",
            body_style,
        ),
    ])
    return story


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#CBD5E1"))
    canvas.line(54, 54, 540, 54)
    canvas.setFillColor(colors.HexColor("#475569"))
    canvas.setFont("Helvetica", 9)
    canvas.drawString(54, 36, "Sample PDF for testing")
    canvas.drawRightString(540, 36, f"Page {canvas.getPageNumber()}")
    canvas.restoreState()


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    images = create_images()
    doc = SimpleDocTemplate(
        str(OUTPUT_PATH),
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=72,
        title="Sample PDF for Testing",
        author="Copilot",
    )
    doc.build(build_story(images), onFirstPage=footer, onLaterPages=footer)
    print(f"Created sample PDF: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
