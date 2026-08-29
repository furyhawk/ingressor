from __future__ import annotations

import reflex as rx

from .state import MarkerState


def render_sidebar() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.vstack(
                rx.heading("Marker PDF Converter", size="4"),
                rx.text(
                    "Upload a document, preview pages, then review the conversion before approving it.",
                    size="2",
                    color="gray",
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
            ),
            width="100%",
            justify="between",
            align="start",
        ),
        rx.divider(),
        rx.vstack(
            rx.text("Upload File", weight="bold"),
            rx.text(
                "Choose a PDF, image, or supported document to begin.",
                size="1",
                color="gray",
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
            ),
            rx.cond(
                MarkerState.uploaded_file_name != "",
                rx.box(
                    rx.vstack(
                        rx.text(
                            f"📄 {MarkerState.uploaded_file_name}",
                            size="2",
                            color="green",
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
                            color="gray",
                        ),
                        rx.cond(
                            MarkerState.total_pages > 0,
                            rx.text(
                                f"Pages: {MarkerState.total_pages}",
                                size="1",
                                color="gray",
                            ),
                            rx.text(
                                "Single-page preview",
                                size="1",
                                color="gray",
                            ),
                        ),
                        spacing="1",
                    ),
                    padding="0.75em 1em",
                    border_radius="12px",
                    background_color="rgba(34, 197, 94, 0.1)",
                    border="1px solid rgba(34, 197, 94, 0.2)",
                    width="100%",
                ),
            ),
            spacing="4",
            padding="1rem",
            border_radius="16px",
            background_color="rgba(15, 23, 42, 0.02)",
            border="1px solid rgba(148, 163, 184, 0.18)",
            width="100%",
        ),
        rx.divider(),
        rx.cond(
            MarkerState.total_pages > 0,
            rx.vstack(
                rx.text("Page Navigation", weight="bold"),
                rx.text(
                    "Use the arrows or enter a page number to update the preview.",
                    size="1",
                    color="gray",
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
                    ),
                    rx.text(f"of {MarkerState.total_pages}", size="2"),
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
                background_color="rgba(15, 23, 42, 0.02)",
                border="1px solid rgba(148, 163, 184, 0.18)",
                width="100%",
            ),
        ),
        rx.divider(),
        rx.vstack(
            rx.text("Output Options", weight="bold"),
            rx.vstack(
                rx.text("Output Format", size="2", weight="bold"),
                rx.select(
                    ["markdown", "json", "html", "chunks"],
                    value=MarkerState.output_format,
                    on_change=MarkerState.set_output_format,
                ),
            ),
            rx.vstack(
                rx.text("Processing Mode", size="2", weight="bold"),
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
                    color="gray",
                ),
            ),
            rx.vstack(
                rx.text("Page Range", size="2", weight="bold"),
                rx.input(
                    value=MarkerState.page_range,
                    on_change=MarkerState.set_page_range,
                    placeholder="e.g., 0,5-10,20",
                ),
                rx.text(
                    "Comma separated like 0,5-10,20",
                    size="1",
                    color="gray",
                ),
            ),
            spacing="4",
            padding="1rem",
            border_radius="16px",
            background_color="rgba(15, 23, 42, 0.02)",
            border="1px solid rgba(148, 163, 184, 0.18)",
            width="100%",
        ),
        rx.divider(),
        rx.vstack(
            rx.text("Processing Options", weight="bold"),
            rx.checkbox(
                "Use LLM",
                is_checked=MarkerState.use_llm,
                on_change=lambda _: MarkerState.toggle_use_llm(),
            ),
            rx.checkbox(
                "Force OCR",
                is_checked=MarkerState.force_ocr,
                on_change=lambda _: MarkerState.toggle_force_ocr(),
            ),
            rx.checkbox(
                "Disable OCR",
                is_checked=MarkerState.disable_ocr,
                on_change=lambda _: MarkerState.toggle_disable_ocr(),
            ),
            rx.checkbox(
                "Strip Existing OCR",
                is_checked=MarkerState.strip_existing_ocr,
                on_change=lambda _: MarkerState.toggle_strip_existing_ocr(),
            ),
            rx.checkbox(
                "Show Page Headers/Footers",
                is_checked=MarkerState.keep_headers_footers,
                on_change=lambda _: MarkerState.toggle_keep_headers_footers(),
            ),
            rx.checkbox(
                "Debug Mode",
                is_checked=MarkerState.debug,
                on_change=lambda _: MarkerState.toggle_debug(),
            ),
            spacing="3",
            padding="1rem",
            border_radius="16px",
            background_color="rgba(15, 23, 42, 0.02)",
            border="1px solid rgba(148, 163, 184, 0.18)",
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
                rx.text(MarkerState.processing_message, size="2"),
                padding="1em",
                border_radius="0.75em",
                background_color="rgba(100, 150, 255, 0.1)",
                border="1px solid rgba(100, 150, 255, 0.18)",
                width="100%",
            ),
        ),
        rx.cond(
            MarkerState.uploaded_file_name == "",
            rx.box(
                rx.text(
                    "Upload a file to enable conversion.",
                    size="2",
                    color="gray",
                ),
                padding="1em",
                border_radius="0.75em",
                background_color="rgba(148, 163, 184, 0.08)",
                width="100%",
            ),
        ),
        rx.cond(
            MarkerState.error_message != "",
            rx.box(
                rx.text(MarkerState.error_message, size="2", color="red"),
                padding="1em",
                border_radius="0.75em",
                background_color="rgba(255, 0, 0, 0.1)",
                border="1px solid rgba(239, 68, 68, 0.2)",
                width="100%",
            ),
        ),
        spacing="5",
        padding="1.5em",
        width="100%",
        height="100vh",
        overflow_y="auto",
        background_color="rgba(248, 250, 252, 0.95)",
        border_right="1px solid rgba(148, 163, 184, 0.25)",
    )


def render_preview() -> rx.Component:
    return rx.vstack(
        rx.box(
            rx.heading("Document Preview", size="4"),
            padding="1rem 1.25rem 0.75rem",
            border_bottom="1px solid rgba(148, 163, 184, 0.18)",
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
                        border="1px solid rgba(148, 163, 184, 0.2)",
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
                    rx.text("Upload a file to see preview", color="gray", size="2"),
                    padding="2em",
                    text_align="center",
                    border="1px dashed rgba(148, 163, 184, 0.4)",
                    border_radius="16px",
                    background_color="rgba(148, 163, 184, 0.03)",
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
                rx.heading("PDF Debug Image", size="3"),
                rx.image(src=MarkerState.debug_pdf_image, width="100%"),
            ),
        ),
        rx.cond(
            MarkerState.debug_layout_image != "",
            rx.vstack(
                rx.heading("Layout Debug Image", size="3"),
                rx.image(src=MarkerState.debug_layout_image, width="100%"),
            ),
        ),
        spacing="0",
        padding="0",
        width="100%",
        height="100vh",
        overflow_y="auto",
        background_color="rgba(248, 250, 252, 0.8)",
    )


def render_results() -> rx.Component:
    return rx.vstack(
        rx.box(
            rx.hstack(
                rx.heading("Review conversion", size="4"),
                rx.cond(
                    MarkerState.review_status == "approved",
                    rx.box(
                        rx.text("Approved", size="1", weight="bold"),
                        padding="0.35rem 0.75rem",
                        border_radius="999px",
                        background_color="rgba(34, 197, 94, 0.15)",
                        color="#166534",
                    ),
                    rx.box(
                        rx.text("Review pending", size="1", weight="bold"),
                        padding="0.35rem 0.75rem",
                        border_radius="999px",
                        background_color="rgba(59, 130, 246, 0.12)",
                        color="#1d4ed8",
                    ),
                ),
                width="100%",
                justify="between",
                align="center",
            ),
            padding="1rem 1.25rem",
            border_radius="16px",
            background_color="rgba(15, 23, 42, 0.03)",
            border="1px solid rgba(148, 163, 184, 0.2)",
            width="100%",
        ),
        rx.cond(
            MarkerState.conversion_result != "",
            rx.vstack(
                rx.text(
                    "Review the conversion result below. You can edit the text if needed, then approve the conversion.",
                    size="2",
                    color="gray",
                ),
                rx.box(
                    rx.vstack(
                        rx.text(
                            "Original Conversion",
                            size="1",
                            weight="bold",
                            color="gray",
                        ),
                        rx.box(
                            rx.text(
                                MarkerState.original_conversion,
                                size="2",
                                font_family="monospace",
                                color="gray",
                            ),
                            padding="0.75rem 1rem",
                            border_radius="8px",
                            background_color="rgba(148, 163, 184, 0.08)",
                            border="1px solid rgba(148, 163, 184, 0.2)",
                            max_h="200px",
                            overflow_y="auto",
                            width="100%",
                        ),
                        spacing="2",
                        width="100%",
                    ),
                    padding="1rem",
                    border_radius="12px",
                    background_color="rgba(15, 23, 42, 0.02)",
                    width="100%",
                ),
                rx.box(
                    rx.vstack(
                        rx.text(
                            "Your Edits",
                            size="1",
                            weight="bold",
                        ),
                        rx.text_area(
                            value=MarkerState.review_text,
                            on_change=MarkerState.set_review_text,
                            min_h="300px",
                            width="100%",
                            font_family="monospace",
                            border_radius="12px",
                            border="1px solid rgba(148, 163, 184, 0.35)",
                            background_color="white",
                            resize="vertical",
                            box_shadow="inset 0 1px 2px rgba(15, 23, 42, 0.05)",
                        ),
                        spacing="2",
                        width="100%",
                    ),
                    padding="1rem",
                    border_radius="12px",
                    background_color="rgba(15, 23, 42, 0.02)",
                    width="100%",
                ),
                rx.hstack(
                    rx.button(
                        "Approve conversion",
                        on_click=MarkerState.approve_conversion,
                        color_scheme="green",
                        is_disabled=MarkerState.review_text == "",
                        border_radius="10px",
                    ),
                    rx.button(
                        "Reset to original",
                        on_click=MarkerState.reset_review,
                        color_scheme="gray",
                        variant="outline",
                        border_radius="10px",
                    ),
                    spacing="3",
                    wrap="wrap",
                ),
                rx.cond(
                    MarkerState.review_status == "approved",
                    rx.box(
                        rx.text(
                            "✓ Conversion approved and ready to export.",
                            color="green",
                            size="2",
                            weight="bold",
                        ),
                        padding="0.75rem 1rem",
                        border_radius="12px",
                        background_color="rgba(34, 197, 94, 0.12)",
                        width="100%",
                    ),
                ),
                spacing="4",
            ),
            rx.box(
                rx.text("Results will appear here", color="gray"),
                padding="2em",
                text_align="center",
                border="1px dashed rgba(148, 163, 184, 0.35)",
                border_radius="16px",
                background_color="rgba(148, 163, 184, 0.03)",
                width="100%",
            ),
        ),
        spacing="5",
        padding="1.5em",
        width="100%",
        height="100vh",
        overflow_y="auto",
        background_color="rgba(248, 250, 252, 0.8)",
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
                background_color="rgba(255, 255, 255, 0.92)",
                border_right="1px solid rgba(148, 163, 184, 0.2)",
            ),
            rx.box(
                rx.button(
                    "Show settings",
                    on_click=MarkerState.toggle_settings_visibility,
                    variant="outline",
                    size="2",
                    color_scheme="gray",
                    border_radius="999px",
                    _hover={"background_color": "rgba(148, 163, 184, 0.12)"},
                ),
                width="60px",
                min_width="60px",
                height="100vh",
                border_right="1px solid rgba(148, 163, 184, 0.2)",
                display="flex",
                align_items="center",
                justify_content="center",
                background_color="rgba(255, 255, 255, 0.9)",
            ),
        ),
        rx.hstack(
            rx.box(
                render_preview(),
                width=rx.cond(MarkerState.settings_visible, "37.5%", "50%"),
                min_width="320px",
                border_right="1px solid rgba(148, 163, 184, 0.2)",
                background_color="rgba(255, 255, 255, 0.4)",
            ),
            rx.box(
                render_results(),
                width=rx.cond(MarkerState.settings_visible, "37.5%", "50%"),
                min_width="320px",
                background_color="rgba(255, 255, 255, 0.4)",
            ),
            width="100%",
            flex="1",
            spacing="0",
        ),
        width="100%",
        height="100vh",
        spacing="0",
        background="linear-gradient(180deg, rgba(241,245,249,0.96) 0%, rgba(248,250,252,0.98) 100%)",
    )
