from __future__ import annotations

import asyncio
import base64
import io
import mimetypes
import os
import tempfile
from pathlib import Path

import pypdfium2
import reflex as rx
from marker.config.parser import ConfigParser
from marker.settings import settings
from PIL import Image, UnidentifiedImageError

from .marker import (
    convert_pdf,
    image_file_to_base64,
    markdown_insert_images,
)


class MarkerState(rx.State):
    uploaded_file_data: bytes | None = None
    uploaded_file_name: str = ""
    uploaded_file_type: str = ""

    page_number: int = 0
    total_pages: int = 0
    current_page_image: str = ""

    page_range: str = "0-0"
    output_format: str = "markdown"
    mode: str = "auto"
    use_llm: bool = False
    force_ocr: bool = False
    disable_ocr: bool = False
    strip_existing_ocr: bool = False
    keep_headers_footers: bool = False
    debug: bool = False

    is_processing: bool = False
    processing_message: str = ""

    conversion_result: str = ""
    original_conversion: str = ""
    review_text: str = ""
    review_status: str = "pending"
    result_format: str = ""
    debug_pdf_image: str = ""
    debug_layout_image: str = ""
    error_message: str = ""

    async def handle_file_upload(self, files: list[rx.UploadFile]):
        if not files:
            self.error_message = "No file selected"
            return

        file = files[0]

        try:
            file_data = await file.read()
            self.uploaded_file_name = file.name
            self.uploaded_file_type = mimetypes.guess_type(file.name)[0] or ""
            self.uploaded_file_data = file_data
            self.conversion_result = ""
            self.original_conversion = ""
            self.review_text = ""
            self.review_status = "pending"
            self.current_page_image = ""
            self.debug_pdf_image = ""
            self.debug_layout_image = ""
            self.error_message = ""
            self._update_page_info()
            if not self.error_message:
                self.processing_message = (
                    f"Loaded {file.name}. Configure options, then run conversion."
                )
            else:
                self.processing_message = ""
        except (OSError, ValueError) as exc:
            self.uploaded_file_data = None
            self.uploaded_file_name = ""
            self.uploaded_file_type = ""
            self.total_pages = 0
            self.page_number = 0
            self.page_range = "0-0"
            self.current_page_image = ""
            self.conversion_result = ""
            self.original_conversion = ""
            self.review_text = ""
            self.review_status = "pending"
            self.processing_message = ""
            self.error_message = f"Error reading file: {exc}"

    def _update_page_info(self) -> None:
        if not self.uploaded_file_data:
            return

        try:
            if "pdf" in self.uploaded_file_type:
                stream = io.BytesIO(self.uploaded_file_data)
                doc = pypdfium2.PdfDocument(stream)
                self.total_pages = len(doc)
                self.page_number = 0
                self.page_range = "0-0"
                self._load_page_image()
            else:
                self.total_pages = 0
                self.page_number = 0
                self.page_range = "0-0"
                self._load_page_image()
        except (OSError, ValueError, pypdfium2.PdfiumError) as exc:
            self.error_message = f"Error processing file: {exc}"

    def _load_page_image(self) -> None:
        if not self.uploaded_file_data:
            return

        try:
            if "pdf" in self.uploaded_file_type:
                stream = io.BytesIO(self.uploaded_file_data)
                doc = pypdfium2.PdfDocument(stream)
                if self.page_number >= len(doc):
                    self.error_message = "Invalid page number"
                    return
                page = doc[self.page_number]
                png_image = page.render(scale=96 / 72).to_pil().convert("RGB")
            else:
                png_image = Image.open(io.BytesIO(self.uploaded_file_data)).convert(
                    "RGB"
                )

            img_bytes = io.BytesIO()
            png_image.save(img_bytes, format="PNG")
            encoded = img_bytes.getvalue()
            self.current_page_image = (
                "data:image/png;base64," + base64.b64encode(encoded).decode()
            )
        except (
            OSError,
            ValueError,
            UnidentifiedImageError,
            pypdfium2.PdfiumError,
        ) as exc:
            self.error_message = f"Error loading page image: {exc}"

    def set_page_number(self, value: str):
        try:
            page_num = int(value)
            if self.total_pages == 0:
                self.error_message = "Upload a PDF to navigate pages"
                return

            if 1 <= page_num <= self.total_pages:
                self.page_number = page_num - 1
                self.page_range = f"{self.page_number}-{self.page_number}"
                self.error_message = ""
                self._load_page_image()
            else:
                self.error_message = f"Page number must be between 1 and {self.total_pages}"
        except ValueError:
            self.error_message = "Invalid page number"

    def set_page_range(self, value: str):
        self.page_range = value

    def go_to_previous_page(self):
        if self.total_pages == 0:
            self.error_message = "Upload a PDF to navigate pages"
            return
        if self.page_number == 0:
            self.error_message = "Already on the first page"
            return

        self.page_number -= 1
        self.page_range = f"{self.page_number}-{self.page_number}"
        self.error_message = ""
        self._load_page_image()

    def go_to_next_page(self):
        if self.total_pages == 0:
            self.error_message = "Upload a PDF to navigate pages"
            return
        if self.page_number >= self.total_pages - 1:
            self.error_message = "Already on the last page"
            return

        self.page_number += 1
        self.page_range = f"{self.page_number}-{self.page_number}"
        self.error_message = ""
        self._load_page_image()

    def set_review_text(self, value: str):
        self.review_text = value
        self.review_status = "pending"

    def set_output_format(self, value: str):
        self.output_format = value

    def set_mode(self, value: str):
        self.mode = value

    def approve_conversion(self):
        if not self.review_text:
            return
        self.conversion_result = self.review_text
        self.review_status = "approved"
        self.processing_message = "Conversion approved and ready to use."

    def reset_review(self):
        self.review_text = self.original_conversion
        self.review_status = "pending"
        self.processing_message = "Review reset to the original conversion."

    def toggle_use_llm(self):
        self.use_llm = not self.use_llm

    def toggle_force_ocr(self):
        self.force_ocr = not self.force_ocr

    def toggle_disable_ocr(self):
        self.disable_ocr = not self.disable_ocr

    def toggle_strip_existing_ocr(self):
        self.strip_existing_ocr = not self.strip_existing_ocr

    def toggle_keep_headers_footers(self):
        self.keep_headers_footers = not self.keep_headers_footers

    def toggle_debug(self):
        self.debug = not self.debug

    def _build_cli_options(self) -> dict[str, object]:
        return {
            "output_format": self.output_format,
            "page_range": self.page_range,
            "force_ocr": self.force_ocr,
            "disable_ocr": self.disable_ocr,
            "debug": self.debug,
            "output_dir": settings.DEBUG_DATA_FOLDER if self.debug else None,
            "use_llm": self.use_llm,
            "strip_existing_ocr": self.strip_existing_ocr,
            "keep_pageheader_in_output": self.keep_headers_footers,
            "keep_pagefooter_in_output": self.keep_headers_footers,
            "mode": None if self.mode == "auto" else self.mode,
        }

    async def run_conversion(self):
        if not self.uploaded_file_data:
            self.error_message = "No file uploaded"
            return

        self.is_processing = True
        self.processing_message = "Processing file and preparing the review result..."
        self.error_message = ""

        try:
            with tempfile.TemporaryDirectory() as tmp_dir:
                temp_file_path = os.path.join(tmp_dir, "temp.pdf")
                await asyncio.to_thread(
                    Path(temp_file_path).write_bytes, self.uploaded_file_data
                )

                self.processing_message = "Converting document..."
                cli_options = self._build_cli_options()
                rendered = convert_pdf(temp_file_path, cli_options)

                text = rendered.text
                if self.output_format == "markdown":
                    text = markdown_insert_images(text, rendered.images)

                self.result_format = self.output_format
                self.conversion_result = text if isinstance(text, str) else str(text)
                self.original_conversion = self.conversion_result
                self.review_text = self.conversion_result
                self.review_status = "pending"

                if self.debug:
                    self.processing_message = "Loading debug information..."
                    debug_data_path = rendered.metadata.get("debug_data_path")
                    if debug_data_path:
                        page_range = ConfigParser(cli_options).generate_config_dict()[
                            "page_range"
                        ]
                        first_page = page_range[0] if page_range else 0

                        pdf_image_path = os.path.join(
                            debug_data_path, f"pdf_page_{first_page}.png"
                        )
                        if os.path.exists(pdf_image_path):
                            self.debug_pdf_image = image_file_to_base64(
                                pdf_image_path
                            )

                        layout_image_path = os.path.join(
                            debug_data_path, f"layout_page_{first_page}.png"
                        )
                        if os.path.exists(layout_image_path):
                            self.debug_layout_image = image_file_to_base64(
                                layout_image_path
                            )

                self.processing_message = "Conversion complete. Review and approve the result below."
        except (OSError, ValueError, RuntimeError, pypdfium2.PdfiumError) as exc:
            self.error_message = f"Conversion error: {exc}"
            self.conversion_result = ""
            self.original_conversion = ""
            self.review_text = ""
            self.review_status = "pending"
        finally:
            self.is_processing = False
