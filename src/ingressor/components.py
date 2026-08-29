from __future__ import annotations

import reflex as rx

from .state import MarkerState

TEXT_PRIMARY = "#0f172a"
TEXT_MUTED = "#1e293b"
BORDER = "#cbd5e1"
SUCCESS_DARK = "#166534"
INFO_DARK = "#1d4ed8"
ERROR_DARK = "#b91c1c"


def render_sidebar() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.vstack(
                rx.heading(
                    "Marker PDF Converter",
                    size="4",
                    color=TEXT_PRIMARY,
                    style={"color": TEXT_PRIMARY, "fontWeight": 700},
                ),
                rx.text(
                    "Upload a document, preview pages, then review the conversion before approving it.",
                    size="2",
                    color=TEXT_MUTED,
                    style={"color": TEXT_MUTED},
                ),
                spacing="0",
            ),
            rx.button(
                "Hide settings",
                on_click=MarkerState.toggle_settings_visibility,
                size="2",
                variant="outline",
                color_scheme="gray",
                border_radius="999px",
                color=TEXT_PRIMARY,
            ),
            width="100%",
            justify="between",
            align="start",
        ),
        rx.divider(),
        rx.vstack(
            rx.text(
                "Upload File",
                weight="bold",
                color=TEXT_PRIMARY,
                style={"color": TEXT_PRIMARY, "fontWeight": 700},
            ),
            rx.text(
                "Choose a PDF, image, or supported document to begin.",
                size="1",
                color=TEXT_MUTED,
                style={"color": TEXT_MUTED},
            ),
            rx.upload(
                rx.button("📁 Choose File", color_scheme="blue", width="100%"),
                id="file_upload",
                multiple=False,
            ),
            rx.button(
                "⬆️ Upload Selected File",
                on_click=MarkerState.handle_file_upload(
                    rx.upload_files(upload_id="file_upload")
                ),
                width="100%",
                color_scheme="gray",
                variant="outline",
                color=TEXT_PRIMARY,
            ),
            rx.cond(
                MarkerState.uploaded_file_name != "",
                rx.box(
                    rx.vstack(
                        rx.text(
                            f"📄 {MarkerState.uploaded_file_name}",
                            size="2",
                            color=SUCCESS_DARK,
                            weight="bold",
                        ),
                        rx.text(
                            "Type: "
                            + rx.cond(
                                MarkerState.uploaded_file_type != "",
                                MarkerState.uploaded_file_type,
                                "unknown",
                            ),
                            size="1",
                            color=TEXT_MUTED,
                        ),
                        rx.cond(
                            MarkerState.total_pages > 0,
                            rx.text(
                                f"Pages: {MarkerState.total_pages}",
                                size="1",
                                color=TEXT_MUTED,
                            ),
                            rx.text(
                                "Single-page preview",
                                size="1",
                                color=TEXT_MUTED,
                            ),
                        ),
                        spacing="1",
                    ),
                    padding="0.75em 1em",
                    border_radius="12px",
                    background_color="rgba(22, 101, 52, 0.08)",
                    border="1px solid rgba(22, 101, 52, 0.25)",
                    width="100%",
                ),
            ),
            spacing="4",
            padding="1rem",
            border_radius="16px",
            background_color="#f8fafc",
            border="1px solid #cbd5e1",
            width="100%",
        ),
        rx.divider(),
        rx.cond(
            MarkerState.total_pages > 0,
            rx.vstack(
                rx.text(
                    "Page Navigation",
                    weight="bold",
                    color=TEXT_PRIMARY,
                    style={"color": TEXT_PRIMARY, "fontWeight": 700},
                ),
                rx.text(
                    "Use the arrows or enter a page number to update the preview.",
                    size="1",
                    color=TEXT_MUTED,
                    style={"color": TEXT_MUTED},
                ),
                rx.hstack(
                    rx.button(
                        "◀",
                        on_click=MarkerState.go_to_previous_page,
                        variant="outline",
                        is_disabled=MarkerState.page_number == 0,
                    ),
                    rx.input(
                        value=rx.cond(
                            MarkerState.total_pages > 0,
                            (MarkerState.page_number + 1).to_string(),
                            "1",
                        ),
                        on_change=MarkerState.set_page_number,
                        type_="number",
                        min="1",
                        max=MarkerState.total_pages,
                        width="5.5em",
                        border_color=BORDER,
                    ),
                    rx.text(f"of {MarkerState.total_pages}", size="2", color=TEXT_PRIMARY),
                    rx.button(
                        "▶",
                        on_click=MarkerState.go_to_next_page,
                        variant="outline",
                        is_disabled=MarkerState.page_number + 1 >= MarkerState.total_pages,
                    ),
                    width="100%",
                    align="center",
                ),
                spacing="3",
                padding="1rem",
                border_radius="16px",
                background_color="#f8fafc",
                border="1px solid #cbd5e1",
                width="100%",
            ),
        ),
        rx.divider(),
        rx.vstack(
            rx.text(
                "Output Options",
                weight="bold",
                color=TEXT_PRIMARY,
                style={"color": TEXT_PRIMARY, "fontWeight": 700},
            ),
            rx.vstack(
                rx.text(
                    "Output Format",
                    size="2",
                    weight="bold",
                    color=TEXT_PRIMARY,
                    style={"color": TEXT_PRIMARY, "fontWeight": 700},
                ),
                rx.select(
                    ["markdown", "json", "html", "chunks"],
                    value=MarkerState.output_format,
                    on_change=MarkerState.set_output_format,
                ),
            ),
            rx.vstack(
                rx.text(
                    "Processing Mode",
                    size="2",
                    weight="bold",
                    color=TEXT_PRIMARY,
                    style={"color": TEXT_PRIMARY, "fontWeight": 700},
                ),
                rx.select(
                    ["auto", "balanced", "fast"],
                    value=MarkerState.mode,
                    on_change=MarkerState.set_mode,
                ),
                rx.text(
                    "'auto' picks by device: balanced on GPU, fast on CPU/MPS. "
                    "'balanced' uses the VLM layout model + full-page OCR. "
                    "'fast' uses lightweight CPU detectors and only OCRs garbled content.",
                    size="1",
                    color=TEXT_MUTED,
                    style={"color": TEXT_MUTED},
                ),
            ),
            rx.vstack(
                rx.text(
                    "Page Range",
                    size="2",
                    weight="bold",
                    color=TEXT_PRIMARY,
                    style={"color": TEXT_PRIMARY, "fontWeight": 700},
                ),
                rx.input(
                    value=MarkerState.page_range,
                    on_change=MarkerState.set_page_range,
                    placeholder="e.g., 0,5-10,20",
                    border_color=BORDER,
                ),
                rx.text(
                    "Comma separated like 0,5-10,20",
                    size="1",
                    color=TEXT_MUTED,
                ),
            ),
            spacing="4",
            padding="1rem",
            border_radius="16px",
            background_color="#f8fafc",
            border="1px solid #cbd5e1",
            width="100%",
        ),
        rx.divider(),
        rx.vstack(
            rx.text(
                "Processing Options",
                weight="bold",
                color=TEXT_PRIMARY,
                style={"color": TEXT_PRIMARY, "fontWeight": 700},
            ),
            rx.checkbox(
                "Use LLM",
                is_checked=MarkerState.use_llm,
                on_change=lambda _: MarkerState.toggle_use_llm(),
                color=TEXT_PRIMARY,
            ),
            rx.checkbox(
                "Force OCR",
                is_checked=MarkerState.force_ocr,
                on_change=lambda _: MarkerState.toggle_force_ocr(),
                color=TEXT_PRIMARY,
            ),
            rx.checkbox(
                "Disable OCR",
                is_checked=MarkerState.disable_ocr,
                on_change=lambda _: MarkerState.toggle_disable_ocr(),
                color=TEXT_PRIMARY,
            ),
            rx.checkbox(
                "Strip Existing OCR",
                is_checked=MarkerState.strip_existing_ocr,
                on_change=lambda _: MarkerState.toggle_strip_existing_ocr(),
                color=TEXT_PRIMARY,
            ),
            rx.checkbox(
                "Show Page Headers/Footers",
                is_checked=MarkerState.keep_headers_footers,
                on_change=lambda _: MarkerState.toggle_keep_headers_footers(),
                color=TEXT_PRIMARY,
            ),
            rx.checkbox(
                "Debug Mode",
                is_checked=MarkerState.debug,
                on_change=lambda _: MarkerState.toggle_debug(),
                color=TEXT_PRIMARY,
            ),
            spacing="3",
            padding="1rem",
            border_radius="16px",
            background_color="#f8fafc",
            border="1px solid #cbd5e1",
            width="100%",
        ),
        rx.divider(),
        rx.button(
            "🚀 Run Conversion",
            on_click=MarkerState.run_conversion,
            width="100%",
            is_loading=MarkerState.is_processing,
            is_disabled=MarkerState.uploaded_file_name == "",
            color_scheme="green",
            size="4",
            border_radius="12px",
        ),
        rx.cond(
            MarkerState.processing_message != "",
            rx.box(
                rx.text(MarkerState.processing_message, size="2", color=TEXT_PRIMARY),
                padding="1em",
                border_radius="0.75em",
                background_color="rgba(29, 78, 216, 0.08)",
                border="1px solid rgba(29, 78, 216, 0.25)",
                width="100%",
            ),
        ),
        rx.cond(
            MarkerState.uploaded_file_name == "",
            rx.box(
                rx.text(
                    "Upload a file to enable conversion.",
                    size="2",
                    color=TEXT_MUTED,
                ),
                padding="1em",
                border_radius="0.75em",
                background_color="#f1f5f9",
                border="1px solid #cbd5e1",
                width="100%",
            ),
        ),
        rx.cond(
            MarkerState.error_message != "",
            rx.box(
                rx.text(MarkerState.error_message, size="2", color=ERROR_DARK),
                padding="1em",
                border_radius="0.75em",
                background_color="rgba(185, 28, 28, 0.08)",
                border="1px solid rgba(185, 28, 28, 0.25)",
                width="100%",
            ),
        ),
        spacing="5",
        padding="1.5em",
        width="100%",
        height="100vh",
        overflow_y="auto",
        background_color="#f8fafc",
        border_right="1px solid #dfe7f1",
    )


def render_preview() -> rx.Component:
    return rx.vstack(
        rx.box(
            rx.heading("Document Preview", size="4", color=TEXT_PRIMARY),
            padding="1rem 1.25rem 0.75rem",
            border_bottom="1px solid #dfe7f1",
            width="100%",
        ),
        rx.box(
            rx.cond(
                MarkerState.current_page_image != "",
                rx.box(
                    rx.image(
                        src=MarkerState.current_page_image,
                        width="100%",
                        max_width="800px",
                        border_radius="18px",
                        box_shadow="0 16px 40px rgba(15, 23, 42, 0.12)",
                        border="1px solid #cbd5e1",
                        background_color="white",
                        object_fit="contain",
                    ),
                    padding="1.25rem",
                    width="100%",
                    display="flex",
                    justify_content="center",
                    align_items="center",
                ),
                rx.box(
                    rx.text("Upload a file to see preview", color=TEXT_MUTED, size="2"),
                    padding="2em",
                    text_align="center",
                    border="1px dashed #94a3b8",
                    border_radius="16px",
                    background_color="#f8fafc",
                    width="100%",
                    max_width="640px",
                ),
            ),
            padding="1rem",
            width="100%",
            display="flex",
            justify_content="center",
        ),
        rx.cond(
            MarkerState.debug_pdf_image != "",
            rx.vstack(
                rx.heading("PDF Debug Image", size="3", color=TEXT_PRIMARY),
                rx.image(src=MarkerState.debug_pdf_image, width="100%"),
            ),
        ),
        rx.cond(
            MarkerState.debug_layout_image != "",
            rx.vstack(
                rx.heading("Layout Debug Image", size="3", color=TEXT_PRIMARY),
                rx.image(src=MarkerState.debug_layout_image, width="100%"),
            ),
        ),
        spacing="0",
        padding="0",
        width="100%",
        height="100vh",
        overflow_y="auto",
        background_color="#f8fafc",
    )


def render_results() -> rx.Component:
    return rx.vstack(
        rx.heading("Conversion Results", size="4"),
        rx.cond(
            MarkerState.conversion_result != "",
            rx.vstack(
                rx.cond(
                    MarkerState.result_format == "markdown",
                    rx.markdown(MarkerState.conversion_result),
                    rx.cond(
                        MarkerState.result_format == "html",
                        rx.html(MarkerState.conversion_result),
                        rx.code(
                            MarkerState.conversion_result,
                            language=rx.cond(
                                MarkerState.result_format == "json",
                                "json",
                                "text",
                            ),
                            width="100%",
                        ),
                    ),
                ),
                spacing="4",
            ),
            rx.box(
                rx.text("Results will appear here", color="gray"),
                padding="2em",
                text_align="center",
            ),
        ),
        spacing="5",
        padding="1.5em",
        width="100%",
        height="100vh",
        overflow_y="auto",
    )


def index() -> rx.Component:
    return rx.hstack(
        rx.cond(
            MarkerState.settings_visible,
            rx.box(
                render_sidebar(),
                width="25%",
                min_width="320px",
                max_width="420px",
                height="100vh",
                overflow_y="auto",
                background_color="#ffffff",
                border_right="1px solid #dfe7f1",
            ),
            rx.box(
                rx.button(
                    "Show settings",
                    on_click=MarkerState.toggle_settings_visibility,
                    variant="outline",
                    size="2",
                    color_scheme="gray",
                    border_radius="999px",
                    color=TEXT_PRIMARY,
                    _hover={"background_color": "rgba(148, 163, 184, 0.12)"},
                ),
                width="60px",
                min_width="60px",
                height="100vh",
                border_right="1px solid #dfe7f1",
                display="flex",
                align_items="center",
                justify_content="center",
                background_color="#ffffff",
            ),
        ),
        rx.hstack(
            rx.box(
                render_preview(),
                width=rx.cond(MarkerState.settings_visible, "37.5%", "50%"),
                min_width="320px",
                border_right="1px solid #dfe7f1",
                background_color="#ffffff",
            ),
            rx.box(
                render_results(),
                width=rx.cond(MarkerState.settings_visible, "37.5%", "50%"),
                min_width="320px",
                background_color="#ffffff",
            ),
            width="100%",
            flex="1",
            spacing="0",
        ),
        width="100%",
        height="100vh",
        spacing="0",
        background="linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%)",
    )
