#!/usr/bin/env python3
"""Extract the images embedded in a PDF -- fast, and without re-encoding.

Built for art books / portfolios / scanned magazines, where every page is one
big picture.  It walks the page content (including images nested inside form
XObjects) and writes out each image object byte-for-byte: JPEG and JPEG 2000
streams are copied verbatim, so nothing is decoded, resized or quality-lost.
Extraction of a 26-page art book takes ~0.03s and the output is bit-identical
to the source images.

Inputs may be single PDFs, whole folders (scanned recursively) or glob patterns,
so a library of art books can be converted in one command.

Images stored with simple filters (Flate/LZW/...) are decoded and re-encoded as
PNG, using the decoded pixel data directly so colors stay untouched.  Pages that
hold no extractable image at all -- vector art, tiled images -- can be rasterized
with ``--render-missing``.

Examples
--------
    # every image of an art book into "God of War..._images/"
    python scripts/pdf_images.py "ingress/God of War Ragnarök - Digital Artbook.pdf"

    # a whole folder (recursive), or a glob pattern (quote it!)
    python scripts/pdf_images.py ingress/
    python scripts/pdf_images.py --format png "artbooks/**/*.pdf"

    # that folder into one place, one sub-folder per PDF
    python scripts/pdf_images.py artbooks -o out

    # explicit output dir, only pages 1-12 and 40+, skip thumbnails/decoration
    python scripts/pdf_images.py artbook.pdf -o out --pages 1-12,40- --min-px 256

    # vector/tiled PDF: rasterize the pages that yielded no image
    python scripts/pdf_images.py artbook.pdf --render-missing --dpi 300

    # normalize everything to PNG, flattening transparency masks
    python scripts/pdf_images.py artbook.pdf --format png --flatten

    # machine-readable report of what was extracted
    python scripts/pdf_images.py artbook.pdf --manifest out/manifest.json
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import io
import json
import re
import sys
import time
import unicodedata
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterator, Sequence

try:
    import pypdfium2 as pdfium
    from PIL import Image
except ImportError as exc:  # pragma: no cover - dependency guard
    sys.exit(f"pypdfium2 and pillow are required:  pip install pypdfium2 pillow  ({exc})")

_IMAGE_OBJ = pdfium.raw.FPDF_PAGEOBJ_IMAGE

# > 8 bytes is enough to tell these apart; ordered because JPEG2000 has two forms.
_MAGIC = (
    (b"\xff\xd8\xff", "jpg"),
    (b"\x89PNG\r\n\x1a\n", "png"),
    (b"II*\x00", "tif"),
    (b"MM\x00*", "tif"),
    (b"\x00\x00\x00\x0cjP", "jp2"),
    (b"jP  \r\n\x87\n", "jp2"),
    (b"\xff\x4f\xff\x51", "jp2"),
    (b"RIFF", "webp"),
    (b"GIF8", "gif"),
    (b"BM", "bmp"),
)


@dataclass
class ImageRecord:
    """One found image, as reported in the manifest."""

    file: str
    page: int  # 1-based
    index: int
    width: int
    height: int
    size: int
    filters: list[str]
    rendered: bool = False
    duplicate_of: str | None = None


@dataclass
class Result:
    pdf: str
    out_dir: str
    pages_scanned: int = 0
    found: int = 0
    written: int = 0
    duplicates: int = 0
    skipped_small: int = 0
    skipped_existing: int = 0
    failed: int = 0
    bytes_written: int = 0
    seconds: float = 0.0
    images: list[ImageRecord] = field(default_factory=list)

    @property
    def megabytes(self) -> float:
        return self.bytes_written / 1e6


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def sanitize(name: str, limit: int = 60) -> str:
    """Make a filesystem-friendly prefix out of a PDF file name.

    The name is composed to NFC first: macOS hands back decomposed (NFD) paths,
    and the combining marks would otherwise be stripped as non-word characters.
    """
    cleaned = unicodedata.normalize("NFC", name)
    cleaned = re.sub(r"[^\w\-. ]+", "", cleaned, flags=re.UNICODE).strip(" .-")
    cleaned = re.sub(r"\s+", "_", cleaned)
    return (cleaned[:limit].rstrip(" .-_")) or "images"


def sniff_extension(data: bytes) -> str:
    """Extension of the bytes we got back, whatever pdfium decided to emit."""
    for magic, ext in _MAGIC:
        if data.startswith(magic):
            return ext
    return "png"


_GLOB_CHARS = re.compile(r"[*?\[]")


def _iter_pdfs(root: Path) -> Iterator[Path]:
    """Every non-hidden PDF below ``root``, in a stable order."""
    for path in sorted(root.rglob("*")):
        if path.suffix.lower() != ".pdf":
            continue
        if any(part.startswith(".") for part in path.relative_to(root).parts):
            continue  # .git, .Trash, AppleDouble sidecars, ...
        yield path


def expand_inputs(specs: Sequence[Path]) -> list[Path]:
    """Turn files, folders and glob patterns into a de-duplicated PDF list.

    A folder is scanned recursively; a pattern may use ``*``, ``?`` and ``**``
    (quote it so the shell does not expand it first).  Hidden files and folders
    are skipped unless named explicitly.
    """
    found: list[Path] = []
    seen: set[Path] = set()

    def add(path: Path) -> None:
        if path.suffix.lower() != ".pdf" or not path.is_file():
            return
        resolved = path.resolve()
        if resolved not in seen:
            seen.add(resolved)
            found.append(path)

    for spec in specs:
        text = str(spec)
        if _GLOB_CHARS.search(text):
            matches = [Path(m) for m in glob.glob(text, recursive=True)]
            if not matches:
                raise ValueError(
                    f"pattern matched nothing: {text}\n"
                    f"       (globs are case-sensitive: '*.PDF' != '*.pdf'; pass the "
                    f"folder instead to catch both)"
                )
            for match in sorted(matches):
                if match.is_dir():
                    for candidate in _iter_pdfs(match):
                        add(candidate)
                else:
                    add(match)  # an explicit pattern may name a hidden file
        elif spec.is_dir():
            for candidate in _iter_pdfs(spec):
                add(candidate)
        elif spec.is_file():
            add(spec)
        else:
            raise ValueError(f"no such file, folder or pattern: {text}")

    return found


def parse_pages(spec: str | None, page_count: int) -> list[int]:
    """Parse ``"1-5,8,12-"`` (1-based, inclusive) into 0-based page indices."""
    if not spec:
        return list(range(page_count))

    wanted: set[int] = set()
    for chunk in spec.replace(" ", "").split(","):
        if not chunk:
            continue
        match = re.fullmatch(r"(\d*)-(\d*)", chunk)
        if match:
            start = int(match.group(1) or 1)
            end = int(match.group(2) or page_count)
            wanted.update(range(start, end + 1))
        elif chunk.isdigit():
            wanted.add(int(chunk))
        else:
            raise ValueError(f"bad page selection: {chunk!r}")
    return sorted(n - 1 for n in wanted if 1 <= n <= page_count)


def image_objects(page: pdfium.PdfPage) -> list[pdfium.PdfImage]:
    """Image objects on a page, descending into nested form XObjects."""
    try:
        return list(page.get_objects(filter=[_IMAGE_OBJ], max_depth=15))
    except TypeError:  # older pypdfium2: no max_depth recursion
        return list(page.get_objects(filter=[_IMAGE_OBJ]))


# --------------------------------------------------------------------------- #
# extraction
# --------------------------------------------------------------------------- #
def extract_native(image: pdfium.PdfImage) -> tuple[bytes, str, list[str]]:
    """Copy the image stream out as-is (JPEG/JP2) or re-encode losslessly."""
    buffer = io.BytesIO()
    image.extract(buffer)  # no fb_format -> pdfium picks png/tiff when re-encoding
    data = buffer.getvalue()
    return data, sniff_extension(data), list(image.get_filters())


def reencode(image: pdfium.PdfImage, data: bytes, fmt: str, flatten: bool) -> tuple[bytes, str]:
    """Re-encode the image, keeping the exact source pixels where possible."""
    pil = None
    if not flatten:
        # Decoding the stream ourselves avoids pdfium's bitmap color transform
        # (which shifts RGB values by ~10 levels on ICC-tagged art).
        try:
            pil = Image.open(io.BytesIO(data))
            pil.load()
        except Exception:
            pil = None
    if pil is None:
        # transparency masks / exotic color spaces: let pdfium rasterize it
        pil = image.get_bitmap(render=flatten).to_pil()

    if fmt in {"jpg", "jpeg"}:
        if pil.mode not in {"RGB", "L"}:
            pil = pil.convert("RGB")
        ext = "jpg"
    elif fmt == "tif":
        ext = "tif"
    else:
        if pil.mode not in {"RGB", "RGBA", "L", "LA", "P"}:
            pil = pil.convert("RGB")
        ext = fmt

    buffer = io.BytesIO()
    pil.save(buffer, format={"tif": "TIFF", "jpg": "JPEG"}.get(fmt, fmt.upper()))
    return buffer.getvalue(), ext


def extract_pdf(
    pdf_path: Path,
    out_dir: Path,
    *,
    pages: str | None = None,
    fmt: str = "native",
    flatten: bool = False,
    min_px: int = 0,
    min_bytes: int = 0,
    dedupe: bool = True,
    overwrite: bool = False,
    render_missing: bool = False,
    render_all: bool = False,
    dpi: int = 200,
    prefix: str | None = None,
    verbose: bool = True,
) -> Result:
    """Extract (or rasterize) every image of one PDF into ``out_dir``."""
    result = Result(pdf=str(pdf_path), out_dir=str(out_dir))
    started = time.perf_counter()
    stem = prefix or sanitize(pdf_path.stem)
    if flatten and fmt == "native":
        fmt = "png"  # baking in a mask requires decoding and re-encoding

    doc = pdfium.PdfDocument(pdf_path)
    try:
        selected = parse_pages(pages, len(doc))
        out_dir.mkdir(parents=True, exist_ok=True)
        seen: dict[str, str] = {}

        for page_index in selected:
            page = doc[page_index]
            result.pages_scanned += 1
            images = [] if render_all else image_objects(page)

            for index, image in enumerate(images, start=1):
                result.found += 1
                width, height = image.get_px_size()
                name = f"{stem}-p{page_index + 1:04d}-{index:02d}"

                if min(width, height) < min_px:
                    result.skipped_small += 1
                    continue

                try:
                    if fmt == "native":
                        data, ext, filters = extract_native(image)
                    else:
                        raw, _, filters = extract_native(image)
                        data, ext = reencode(image, raw, fmt, flatten)
                except Exception as exc:  # malformed / unsupported image object
                    result.failed += 1
                    if verbose:
                        print(f"  ! page {page_index + 1} image {index}: {exc}", file=sys.stderr)
                    continue

                if len(data) < min_bytes:
                    result.skipped_small += 1
                    continue

                digest = hashlib.blake2b(data, digest_size=12).hexdigest()
                record = ImageRecord(
                    file="", page=page_index + 1, index=index,
                    width=width, height=height, size=len(data), filters=filters,
                )

                if dedupe and digest in seen:
                    result.duplicates += 1
                    record.duplicate_of = seen[digest]
                    result.images.append(record)
                    continue

                target = out_dir / f"{name}.{ext}"
                if target.exists() and not overwrite:
                    result.skipped_existing += 1
                    continue

                target.write_bytes(data)
                seen[digest] = target.name
                record.file = target.name
                result.images.append(record)
                result.written += 1
                result.bytes_written += len(data)
                if verbose:
                    print(f"  p{page_index + 1:04d} {index:02d} {width}x{height} "
                          f"{len(data) / 1024:7.1f} KB  {target.name}")

            # rasterize pages that hold no extractable image (or all of them)
            if render_all or (render_missing and not images):
                data, ext, width, height = _render_page(page, dpi)
                target = out_dir / f"{stem}-p{page_index + 1:04d}-page.{ext}"
                if target.exists() and not overwrite:
                    result.skipped_existing += 1
                else:
                    target.write_bytes(data)
                    result.images.append(ImageRecord(
                        file=target.name, page=page_index + 1, index=0,
                        width=width, height=height, size=len(data),
                        filters=[f"render@{dpi}dpi"], rendered=True,
                    ))
                    result.written += 1
                    result.bytes_written += len(data)
                    result.found += 1
                    if verbose:
                        print(f"  p{page_index + 1:04d} rendered {len(data) / 1024:7.1f} KB  {target.name}")
    finally:
        doc.close()

    result.seconds = time.perf_counter() - started
    return result


def _render_page(page: pdfium.PdfPage, dpi: int) -> tuple[bytes, str, int, int]:
    bitmap = page.render(scale=dpi / 72)
    pil = bitmap.to_pil()
    buffer = io.BytesIO()
    pil.save(buffer, format="PNG")
    return buffer.getvalue(), "png", pil.width, pil.height


# --------------------------------------------------------------------------- #
# cli
# --------------------------------------------------------------------------- #
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract embedded images from a PDF (fast, no re-encoding).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("Examples", 1)[1].replace("--------", "", 1).strip(),
    )
    parser.add_argument("pdf", nargs="+", type=Path, metavar="PATH",
                        help="PDF file(s), folder(s) or glob pattern(s) such as "
                             "'artbooks/**/*.pdf' (quoted)")
    parser.add_argument("-o", "--out", type=Path,
                        help="output directory; with several PDFs each gets a "
                             "sub-folder (default: <pdf>_images next to each PDF)")
    parser.add_argument("--pages", help='pages to scan, 1-based, e.g. "1-12,40-"')
    parser.add_argument("--format", default="native",
                        choices=["native", "png", "jpg", "webp", "tif"],
                        help="native keeps the original stream (default); anything else "
                             "decodes and re-encodes")
    parser.add_argument("--flatten", action="store_true",
                        help="bake in transparency masks / placement transform (implies re-encode)")
    parser.add_argument("--min-px", type=int, default=0, metavar="N",
                        help="skip images smaller than N px in either dimension")
    parser.add_argument("--min-kb", type=float, default=0, metavar="KB",
                        help="skip images smaller than KB kilobytes")
    parser.add_argument("--no-dedupe", action="store_true",
                        help="keep identical images found on several pages")
    parser.add_argument("--overwrite", action="store_true",
                        help="overwrite files that already exist in the output dir")
    parser.add_argument("--render-missing", action="store_true",
                        help="rasterize pages that contain no extractable image")
    parser.add_argument("--render-all", action="store_true",
                        help="ignore embedded images and rasterize every selected page")
    parser.add_argument("--dpi", type=int, default=200, help="DPI for rasterization (default 200)")
    parser.add_argument("--prefix", help="file name prefix (default: sanitized PDF name)")
    parser.add_argument("--manifest", type=Path, help="write a JSON manifest of extracted images")
    parser.add_argument("--json", action="store_true", help="print the result as JSON")
    parser.add_argument("-q", "--quiet", action="store_true", help="no per-image output")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    verbose = not args.quiet
    results: list[Result] = []

    try:
        inputs = expand_inputs(args.pdf)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if not inputs:
        print(f"error: no PDF found in {', '.join(str(p) for p in args.pdf)}", file=sys.stderr)
        return 2
    if verbose and len(args.pdf) < len(inputs):
        print(f"{len(inputs)} PDF(s)")
    taken: dict[Path, int] = {}

    for index, pdf_path in enumerate(inputs, start=1):
        out_dir = args.out or pdf_path.parent / f"{sanitize(pdf_path.stem)}_images"
        if args.out and len(inputs) > 1:
            # one sub-folder per PDF, disambiguated when stems repeat across folders
            base = args.out / sanitize(pdf_path.stem)
            taken[base] = taken.get(base, 0) + 1
            out_dir = base if taken[base] == 1 else base.with_name(f"{base.name}-{taken[base]}")
        if verbose:
            print(f"\n[{index}/{len(inputs)}] {pdf_path.name} -> {out_dir}")

        try:
            result = extract_pdf(
                pdf_path, out_dir,
                pages=args.pages, fmt=args.format, flatten=args.flatten,
                min_px=args.min_px, min_bytes=int(args.min_kb * 1024),
                dedupe=not args.no_dedupe, overwrite=args.overwrite,
                render_missing=args.render_missing, render_all=args.render_all,
                dpi=args.dpi, prefix=args.prefix, verbose=verbose,
            )
        except Exception as exc:
            print(f"  ! {pdf_path.name}: {exc}", file=sys.stderr)
            return 1
        results.append(result)

        if verbose:
            print(f"  {result.pages_scanned} pages, {result.found} images, "
                  f"{result.written} written ({result.megabytes:.1f} MB), "
                  f"{result.duplicates} duplicates, {result.skipped_small} filtered, "
                  f"{result.failed} failed in {result.seconds:.2f}s")
            if not result.written and not args.render_missing:
                print("  no embedded image found -- try --render-missing to "
                      "rasterize the pages instead")

    if args.manifest:
        payload = [asdict(r) for r in results]
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    if args.json:
        print(json.dumps([asdict(r) for r in results], indent=2))
    if verbose and len(results) > 1:
        print(f"\n{len(results)} PDF(s): {sum(r.written for r in results)} images, "
              f"{sum(r.bytes_written for r in results) / 1e6:.1f} MB, "
              f"{sum(r.duplicates for r in results)} duplicates, "
              f"{sum(r.failed for r in results)} failures in "
              f"{sum(r.seconds for r in results):.2f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
