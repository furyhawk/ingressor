"""
Marker PDF/Document to Markdown Converter - Reflex Framework Implementation

This app converts PDFs, images, and documents to Markdown, HTML, JSON, or chunks.
"""

import base64
import io
import mimetypes
import os
import re
import tempfile
from typing import Any, Dict

import reflex as rx
from marker.config.parser import ConfigParser
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered
from marker.settings import settings
from PIL import Image
import pypdfium2


# Environment setup
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
os.environ["IN_STREAMLIT"] = "true"


# ============================================================================
# State Management
# ============================================================================

class MarkerState(rx.State):
    """State management for the Marker PDF converter application."""
    
    # File handling
    uploaded_file_data: bytes | None = None
    uploaded_file_name: str = ""
    uploaded_file_type: str = ""
    
    # PDF navigation
    page_number: int = 0
    total_pages: int = 0
    current_page_image: str = ""  # base64 encoded image
    
    # Processing options
    page_range: str = "0-0"
    output_format: str = "markdown"
    mode: str = "auto"
    use_llm: bool = False
    force_ocr: bool = False
    disable_ocr: bool = False
    strip_existing_ocr: bool = False
    keep_headers_footers: bool = False
    debug: bool = False
    
    # Processing state
    is_processing: bool = False
    processing_message: str = ""
    
    # Results
    conversion_result: str = ""
    result_format: str = ""
    debug_pdf_image: str = ""  # base64 encoded
    debug_layout_image: str = ""  # base64 encoded
    error_message: str = ""
    
    # Models loaded flag
    models_loaded: bool = False
    model_dict: Dict[str, Any] = {}

    async def handle_file_upload(self, files: list[rx.UploadFile]):
        """Handle file upload."""
        if not files:
            self.error_message = "No file selected"
            return
        
        file = files[0]
        self.uploaded_file_name = file.name
        self.uploaded_file_type = mimetypes.guess_type(file.name)[0] or ""
        
        # Read file content
        try:
            self.uploaded_file_data = await file.read()
            self.current_page_image = ""
            self.debug_pdf_image = ""
            self.debug_layout_image = ""
            self._update_page_info()
            self.error_message = ""
        except Exception as e:
            self.error_message = f"Error reading file: {str(e)}"

    def _update_page_info(self):
        """Update page count and display first page."""
        if not self.uploaded_file_data:
            return
        
        try:
            if "pdf" in self.uploaded_file_type:
                stream = io.BytesIO(self.uploaded_file_data)
                doc = pypdfium2.PdfDocument(stream)
                self.total_pages = len(doc) - 1
            else:
                self.total_pages = 0
            
            self.page_number = 0
            self.page_range = f"0-0"
            self._load_page_image()
        except Exception as e:
            self.error_message = f"Error processing file: {str(e)}"

    def _load_page_image(self):
        """Load and display the current page as an image."""
        if not self.uploaded_file_data:
            return
        
        try:
            if "pdf" in self.uploaded_file_type:
                stream = io.BytesIO(self.uploaded_file_data)
                doc = pypdfium2.PdfDocument(stream)
                if self.page_number < len(doc):
                    page = doc[self.page_number]
                    png_image = page.render(scale=96 / 72).to_pil().convert("RGB")
                else:
                    self.error_message = "Invalid page number"
                    return
            else:
                png_image = Image.open(io.BytesIO(self.uploaded_file_data)).convert("RGB")
            
            # Convert to base64
            img_bytes = io.BytesIO()
            png_image.save(img_bytes, format="PNG")
            img_bytes = img_bytes.getvalue()
            encoded = base64.b64encode(img_bytes).decode()
            self.current_page_image = f"data:image/png;base64,{encoded}"
        except Exception as e:
            self.error_message = f"Error loading page image: {str(e)}"

    def set_page_number(self, value: str):
        """Set page number and update display."""
        try:
            page_num = int(value)
            if 0 <= page_num <= self.total_pages:
                self.page_number = page_num
                self.page_range = f"{page_num}-{page_num}"
                self._load_page_image()
            else:
                self.error_message = f"Page number must be between 0 and {self.total_pages}"
        except ValueError:
            self.error_message = "Invalid page number"

    def set_page_range(self, value: str):
        """Update page range for processing."""
        self.page_range = value

    def set_output_format(self, value: str):
        """Set output format."""
        self.output_format = value

    def set_mode(self, value: str):
        """Set processing mode."""
        self.mode = value

    def toggle_use_llm(self):
        """Toggle LLM usage."""
        self.use_llm = not self.use_llm

    def toggle_force_ocr(self):
        """Toggle force OCR."""
        self.force_ocr = not self.force_ocr

    def toggle_disable_ocr(self):
        """Toggle disable OCR."""
        self.disable_ocr = not self.disable_ocr

    def toggle_strip_existing_ocr(self):
        """Toggle strip existing OCR."""
        self.strip_existing_ocr = not self.strip_existing_ocr

    def toggle_keep_headers_footers(self):
        """Toggle keep headers/footers."""
        self.keep_headers_footers = not self.keep_headers_footers

    def toggle_debug(self):
        """Toggle debug mode."""
        self.debug = not self.debug

    async def run_conversion(self):
        """Run the PDF conversion."""
        if not self.uploaded_file_data:
            self.error_message = "No file uploaded"
            return
        
        self.is_processing = True
        self.processing_message = "Processing file..."
        self.error_message = ""
        
        try:
            # Load models if not already loaded
            if not self.models_loaded:
                self.processing_message = "Loading models (this may take a moment)..."
                self.model_dict = create_model_dict()
                self.models_loaded = True
            
            # Convert to PDF if needed
            with tempfile.TemporaryDirectory() as tmp_dir:
                temp_file_path = os.path.join(tmp_dir, "temp.pdf")
                with open(temp_file_path, "wb") as f:
                    f.write(self.uploaded_file_data)
                
                self.processing_message = "Converting document..."
                
                # Parse CLI options
                cli_options = self._build_cli_options()
                config_parser = ConfigParser(cli_options)
                
                # Run conversion
                rendered = self._convert_pdf(temp_file_path, config_parser)
                
                # Extract results
                text, ext, images = text_from_rendered(rendered)
                self.result_format = self.output_format
                
                # Format output based on type
                if self.output_format == "markdown":
                    text = self._markdown_insert_images(text, images)
                
                self.conversion_result = text if isinstance(text, str) else str(text)
                
                # Handle debug images
                if self.debug:
                    self.processing_message = "Loading debug information..."
                    debug_data_path = rendered.metadata.get("debug_data_path")
                    if debug_data_path:
                        page_range = config_parser.generate_config_dict()["page_range"]
                        first_page = page_range[0] if page_range else 0
                        
                        pdf_image_path = os.path.join(debug_data_path, f"pdf_page_{first_page}.png")
                        if os.path.exists(pdf_image_path):
                            self.debug_pdf_image = self._image_to_base64(pdf_image_path)
                        
                        layout_image_path = os.path.join(debug_data_path, f"layout_page_{first_page}.png")
                        if os.path.exists(layout_image_path):
                            self.debug_layout_image = self._image_to_base64(layout_image_path)
            
            self.processing_message = "Done!"
        
        except Exception as e:
            self.error_message = f"Conversion error: {str(e)}"
            self.conversion_result = ""
        
        finally:
            self.is_processing = False

    def _build_cli_options(self) -> Dict[str, Any]:
        """Build CLI options for the converter."""
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

    def _convert_pdf(self, fname: str, config_parser: ConfigParser):
        """Convert PDF file."""
        config_dict = config_parser.generate_config_dict()
        config_dict["pdftext_workers"] = 1
        converter = PdfConverter(
            config=config_dict,
            artifact_dict=self.model_dict,
            processor_list=config_parser.get_processors(),
            renderer=config_parser.get_renderer(),
            llm_service=config_parser.get_llm_service(),
        )
        return converter(fname)

    @staticmethod
    def _markdown_insert_images(markdown: str, images: Dict[str, Any]) -> str:
        """Insert images into markdown as base64 encoded HTML."""
        image_tags = re.findall(
            r'(!\[(?P<image_title>[^\]]*)\]\((?P<image_path>[^\)"\s]+)\s*([^\)]*)\))',
            markdown,
        )
        
        for image in image_tags:
            image_markdown = image[0]
            image_alt = image[1]
            image_path = image[2]
            if image_path in images:
                img = images[image_path]
                img_bytes = io.BytesIO()
                img.save(img_bytes, format=settings.OUTPUT_IMAGE_FORMAT)
                img_bytes = img_bytes.getvalue()
                encoded = base64.b64encode(img_bytes).decode()
                img_html = f'<img src="data:image/{settings.OUTPUT_IMAGE_FORMAT.lower()};base64,{encoded}" alt="{image_alt}" style="max-width: 100%;">'
                markdown = markdown.replace(image_markdown, img_html)
        
        return markdown

    @staticmethod
    def _image_to_base64(image_path: str) -> str:
        """Convert image file to base64 data URL."""
        try:
            with Image.open(image_path) as img:
                img_bytes = io.BytesIO()
                img.save(img_bytes, format="PNG")
                img_bytes = img_bytes.getvalue()
                encoded = base64.b64encode(img_bytes).decode()
                return f"data:image/png;base64,{encoded}"
        except Exception:
            return ""


# ============================================================================
# UI Components
# ============================================================================

def render_sidebar() -> rx.Component:
    """Render the sidebar with upload and controls."""
    return rx.vstack(
        rx.heading("Marker PDF Converter", size="4"),
        rx.divider(),
        
        # File upload
        rx.vstack(
            rx.text("Upload File", weight="bold"),
            rx.upload(
                rx.button("📁 Choose File", color_scheme="blue"),
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
                    rx.text(f"📄 {MarkerState.uploaded_file_name}", size="2", color="green"),
                    padding="0.5em",
                    border_radius="0.25em",
                    background_color="rgba(0, 255, 0, 0.1)",
                )
            ),
            spacing="4",
        ),
        
        rx.divider(),
        
        # Page navigation (only for PDFs)
        rx.cond(
            MarkerState.total_pages > 0,
            rx.vstack(
                rx.text("Page Navigation", weight="bold"),
                rx.hstack(
                    rx.input(
                        value=rx.cond(
                            MarkerState.total_pages > 0,
                            MarkerState.page_number.to_string(),
                            "0"
                        ),
                        on_change=MarkerState.set_page_number,
                        type_="number",
                        width="100%",
                    ),
                    rx.text(f"/ {MarkerState.total_pages}", size="2"),
                    width="100%",
                ),
                spacing="2",
            ),
        ),
        
        rx.divider(),
        
        # Output options
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
        ),
        
        rx.divider(),
        
        # Processing options
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
        ),
        
        rx.divider(),
        
        # Convert button
        rx.button(
            "🚀 Run Conversion",
            on_click=MarkerState.run_conversion,
            width="100%",
            is_loading=MarkerState.is_processing,
            color_scheme="green",
            size="4",
        ),
        
        # Status message
        rx.cond(
            MarkerState.processing_message != "",
            rx.box(
                rx.text(MarkerState.processing_message, size="2"),
                padding="1em",
                border_radius="0.5em",
                background_color="rgba(100, 150, 255, 0.1)",
            )
        ),
        
        # Error message
        rx.cond(
            MarkerState.error_message != "",
            rx.box(
                rx.text(MarkerState.error_message, size="2", color="red"),
                padding="1em",
                border_radius="0.5em",
                background_color="rgba(255, 0, 0, 0.1)",
            )
        ),
        
        spacing="5",
        padding="1.5em",
        width="100%",
        height="100vh",
        overflow_y="auto",
        background_color="rgba(240, 240, 240, 0.5)",
    )


def render_preview() -> rx.Component:
    """Render the left preview column with page image."""
    return rx.vstack(
        rx.heading("Document Preview", size="4"),
        rx.cond(
            MarkerState.current_page_image != "",
            rx.image(src=MarkerState.current_page_image, width="100%"),
            rx.box(
                rx.text("Upload a file to see preview", color="gray"),
                padding="2em",
                text_align="center",
            ),
        ),
        
        # Debug images
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
        
        spacing="5",
        padding="1.5em",
        width="100%",
        height="100vh",
        overflow_y="auto",
    )


def render_results() -> rx.Component:
    """Render the right results column."""
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
                                "text"
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


# ============================================================================
# Main Layout
# ============================================================================

def index() -> rx.Component:
    """Main page layout."""
    return rx.hstack(
        # Sidebar
        rx.box(
            render_sidebar(),
            width="25%",
            border_right="1px solid #e0e0e0",
            height="100vh",
            overflow_y="auto",
        ),
        
        # Main content area
        rx.hstack(
            # Left column - Preview
            rx.box(
                render_preview(),
                width="37.5%",
                border_right="1px solid #e0e0e0",
            ),
            
            # Right column - Results
            rx.box(
                render_results(),
                width="37.5%",
            ),
            
            width="75%",
            spacing="0",
        ),
        
        width="100%",
        height="100vh",
        spacing="0",
    )


# ============================================================================
# App Configuration
# ============================================================================

# Create the app
app = rx.App()

# Add index page
app.add_page(index, title="Marker PDF Converter")
