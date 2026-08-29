from __future__ import annotations

import base64
import html
import io
import os
import re
from dataclasses import dataclass
from typing import Any

from marker.config.parser import ConfigParser
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict, shutdown_models
from marker.output import text_from_rendered
from marker.settings import settings
from PIL import Image

os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")

_MODEL_DICT: dict[str, Any] | None = None


@dataclass(slots=True)
class ConversionResult:
    text: str
    images: dict[str, Any]
    metadata: dict[str, Any]


def get_model_dict() -> dict[str, Any]:
    global _MODEL_DICT
    if _MODEL_DICT is None:
        _MODEL_DICT = create_model_dict()
    return _MODEL_DICT


def shutdown_model_dict() -> None:
    global _MODEL_DICT
    if _MODEL_DICT is not None:
        shutdown_models(_MODEL_DICT)
        _MODEL_DICT = None


def convert_pdf(filepath: str, options: dict[str, Any]) -> ConversionResult:
    config_parser = ConfigParser(options)
    config_dict = config_parser.generate_config_dict()
    config_dict["pdftext_workers"] = 1
    converter = PdfConverter(
        config=config_dict,
        artifact_dict=get_model_dict(),
        processor_list=config_parser.get_processors(),
        renderer=config_parser.get_renderer(),
        llm_service=config_parser.get_llm_service(),
    )
    rendered = converter(filepath)
    text, _, images = text_from_rendered(rendered)
    return ConversionResult(text=text, images=images, metadata=rendered.metadata)


def encode_image(image: Image.Image) -> str:
    img_bytes = io.BytesIO()
    image.save(img_bytes, format=settings.OUTPUT_IMAGE_FORMAT)
    encoded = base64.b64encode(img_bytes.getvalue()).decode(settings.OUTPUT_ENCODING)
    return (
        f"data:image/{settings.OUTPUT_IMAGE_FORMAT.lower()};base64,{encoded}"
    )


def image_file_to_base64(image_path: str) -> str:
    try:
        with Image.open(image_path) as img:
            return encode_image(img)
    except OSError:
        return ""


def markdown_insert_images(markdown: str, images: dict[str, Any]) -> str:
    image_tags = re.findall(
        r"(!\[(?P<image_title>[^\]]*)\]\((?P<image_path>[^\)\"\s]+)\s*([^\)]*)\))",
        markdown,
    )

    for image_markdown, image_alt, image_path, _ in image_tags:
        if image_path not in images:
            continue

        markdown = markdown.replace(
            image_markdown,
            _image_to_html(images[image_path], image_alt),
        )

    return markdown


def _image_to_html(image: Any, image_alt: str) -> str:
    img_bytes = io.BytesIO()
    image.save(img_bytes, format=settings.OUTPUT_IMAGE_FORMAT)
    encoded = base64.b64encode(img_bytes.getvalue()).decode(settings.OUTPUT_ENCODING)
    escaped_alt = html.escape(image_alt, quote=True)
    return (
        f'<img src="data:image/{settings.OUTPUT_IMAGE_FORMAT.lower()};base64,'
        f'{encoded}" alt="{escaped_alt}" style="max-width: 100%;">'
    )
