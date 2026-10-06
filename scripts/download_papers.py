#!/usr/bin/env python3
"""Download the PDFs of the papers listed in `furyhawk/AI-Papers-of-the-Week`.

The weekly issues are plain Markdown tables.  Each row starts with a number and
a bold title and carries a ``[Paper](...)`` link.  For the 2026 issues most of
those links point at ``academy.dair.ai/papers/<slug>-<arxiv-id>``, but some point
straight at ``arxiv.org/abs/<id>`` and a few at the publisher (Nature, HF, ...).

This script pulls the Markdown for a year, slices out the requested weekly
section, resolves every ``Paper`` link to an actual PDF URL, and downloads the
files.  Resolution rules:

* ``arxiv.org/abs/<id>`` and ``arxiv.org/pdf/<id>`` -> ``https://arxiv.org/pdf/<id>``
* ``academy.dair.ai/papers/<slug>-<arxiv-id>``   -> ``https://arxiv.org/pdf/<arxiv-id>``
* any URL already ending in ``.pdf``             -> used as-is
* ``huggingface.co/.../blob/...``                -> rewritten to ``/resolve/...``
* everything else (Nature, SSRN, project pages)  -> the page is fetched and its
  ``citation_pdf_url`` meta tag (or first ``.pdf`` link) is used, if present.

Downloads are resumable (an existing file with a PDF header is skipped), run in
parallel, and verified by sniffing the ``%PDF`` magic bytes so an HTML error page
never lands on disk as a "PDF".  A JSON manifest of every row is written next to
the files.

Examples
--------
    # the default test case: September 28 - October 4, 2026
    python scripts/download_papers.py --section "September 28 - October 4"

    # just show what would be downloaded, don't fetch any PDFs
    python scripts/download_papers.py --section "September 28 - October 4" --dry-run

    # every section of the 2026 page, into papers/2026/
    python scripts/download_papers.py --all --out papers

    # only the rows whose links live on arxiv
    python scripts/download_papers.py --section "September 28" --arxiv-only

    # parse a local copy of the page instead of hitting GitHub
    python scripts/download_papers.py --md years/2026.md --section "September 28"
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass, field
from pathlib import Path

RAW_URL = "https://raw.githubusercontent.com/furyhawk/AI-Papers-of-the-Week/main/years/{year}.md"
USER_AGENT = (
    "ingressor-paper-downloader/0.1 "
    "(+https://github.com/furyhawk/ingressor; contact: furyx@hotmail.com)"
)
TIMEOUT = 60
RETRIES = 3

LINK_RE = re.compile(r"\[([^\]]*)\]\(\s*([^)\s]+)\s*\)")
ROW_RE = re.compile(r"^\|\s*(\d+)\)\s*(.*)$")
# a bare arXiv identifier, optionally versioned: 2609.37725 or 2609.37725v2
ARXIV_ID_RE = re.compile(r"(?<!\d)(\d{4}\.\d{4,5})(v\d+)?$")
HTML_PDF_RE = re.compile(
    r"""<meta[^>]+(?:name|property)=["']citation_pdf_url["'][^>]+content=["']([^"']+)["']""",
    re.IGNORECASE,
)
HTML_ANY_PDF_RE = re.compile(r"""href=["']([^"']+\.pdf[^"']*)["']""", re.IGNORECASE)
BOLD_RE = re.compile(r"\*\*(.+?)\*\*", re.DOTALL)


@dataclass
class Paper:
    """One row of a weekly table, resolved to a downloadable PDF URL."""

    index: int
    title: str
    link: str
    paper_links: list[str] = field(default_factory=list)
    pdf_url: str | None = None
    status: str = "pending"
    path: str | None = None
    detail: str = ""


# --------------------------------------------------------------------------- #
# fetch helpers
# --------------------------------------------------------------------------- #
def http_get(url: str, *, want: str = "bytes") -> tuple[bytes, str]:
    """GET `url` with retries; return (body, content_type). Raises on failure."""
    last: Exception | None = None
    for attempt in range(1, RETRIES + 1):
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                body = resp.read()
                ctype = resp.headers.get("Content-Type", "")
            if want == "text":
                body = body.decode("utf-8", errors="replace")
            return body, ctype  # type: ignore[return-value]
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            last = exc
            if attempt < RETRIES:
                time.sleep(1.5 * attempt)
        except urllib.error.HTTPError as exc:
            last = exc
            # 4xx other than rate limiting won't get better on retry
            if exc.code < 500 and exc.code != 429:
                break
            if attempt < RETRIES:
                time.sleep(1.5 * attempt)
    raise RuntimeError(f"GET {url} failed: {last}")


def fetch_markdown(year: int, md: str | None) -> str:
    """Return the raw Markdown for a year, from a local file or GitHub."""
    if md:
        return Path(md).read_text(encoding="utf-8")
    url = RAW_URL.format(year=year)
    return http_get(url, want="text")[0]  # type: ignore[return-value]


# --------------------------------------------------------------------------- #
# markdown parsing
# --------------------------------------------------------------------------- #
def split_sections(md: str) -> list[tuple[str, str]]:
    """Split the page into (heading, body) pairs at level-2 headings."""
    sections: list[tuple[str, str]] = []
    heading: str | None = None
    buf: list[str] = []
    for line in md.splitlines():
        if line.startswith("## "):
            if heading is not None:
                sections.append((heading, "\n".join(buf)))
            heading = line[3:].strip()
            buf = []
        elif heading is not None:
            buf.append(line)
    if heading is not None:
        sections.append((heading, "\n".join(buf)))
    return sections


def select_sections(
    sections: list[tuple[str, str]], want: str | None, every: bool
) -> list[tuple[str, str]]:
    """Pick sections whose heading *or* body matches `want` (case-insensitive)."""
    if every:
        return sections
    if not want:
        raise SystemExit("error: pass --section DATE (e.g. 'September 28 - October 4') or --all")
    needle = want.lower()
    hits = []
    for heading, body in sections:
        # the date is usually on the line just under the heading, so scan a
        # short prefix of the body rather than the whole (huge) section.
        probe = f"{heading}\n{body[:400]}".lower()
        if needle in probe:
            hits.append((heading, body))
    if not hits:
        available = "\n  ".join(h for h, _ in sections)
        raise SystemExit(f"error: no section matched {want!r}. Available headings:\n  {available}")
    return hits


def parse_papers(body: str) -> list[Paper]:
    """Extract every numbered table row and its `Paper` link(s)."""
    papers: list[Paper] = []
    for line in body.splitlines():
        m = ROW_RE.match(line)
        if not m:
            continue
        index, rest = int(m.group(1)), m.group(2)
        links = LINK_RE.findall(rest)
        paper_links = [url for label, url in links if "paper" in label.lower()]
        if not paper_links:
            paper_links = [url for _, url in links if _looks_like_pdf_source(url)]
        title = _clean_title(rest)
        papers.append(Paper(index=index, title=title, link=paper_links[0] if paper_links else "", paper_links=paper_links))
    return papers


def _clean_title(rest: str) -> str:
    """Pull the bold paper name out of a row, falling back to its first words."""
    bold = BOLD_RE.search(rest)
    if bold:
        return re.sub(r"\s+", " ", bold.group(1)).strip()
    text = LINK_RE.sub("", rest)
    return re.sub(r"\s+", " ", text).strip().strip("|")[:80]


def _looks_like_pdf_source(url: str) -> bool:
    host = urllib.parse.urlparse(url).netloc.lower()
    return any(h in host for h in ("arxiv.org", "academy.dair.ai", "nature.com", "ssrn.com", ".pdf"))


# --------------------------------------------------------------------------- #
# PDF URL resolution
# --------------------------------------------------------------------------- #
def arxiv_id_from(url: str) -> str | None:
    """Best-effort extraction of an arXiv id from a URL or its last path part."""
    parsed = urllib.parse.urlparse(url)
    if "arxiv.org" in parsed.netloc.lower():
        tail = parsed.path.rsplit("/", 1)[-1]
        m = ARXIV_ID_RE.search(tail)
        return m.group(1) + (m.group(2) or "") if m else None
    # academy.dair.ai (and friends) end in "<slug>-<arxiv-id>"
    m = ARXIV_ID_RE.search(parsed.path)
    if m:
        return m.group(1) + (m.group(2) or "")
    return None


def resolve_pdf(url: str) -> tuple[str | None, str]:
    """Map a `Paper` link to a PDF URL. Returns (pdf_url, detail)."""
    if not url:
        return None, "no paper link"

    parsed = urllib.parse.urlparse(url)
    host = parsed.netloc.lower()

    if "huggingface.co" in host and "/blob/" in parsed.path:
        return url.replace("/blob/", "/resolve/"), "huggingface blob->resolve"

    if url.lower().endswith(".pdf"):
        return url, "direct pdf"

    aid = arxiv_id_from(url)
    if aid:
        return f"https://arxiv.org/pdf/{aid}", f"arxiv {aid}"

    if host in ("academy.dair.ai", "academy.air.ai"):
        return None, "dair page without arxiv id"

    # publisher / project page: look for a citation_pdf_url meta tag
    try:
        html, _ = http_get(url, want="text")
    except Exception as exc:  # noqa: BLE001 - report, don't crash the batch
        return None, f"page fetch failed: {exc}"
    html = html  # type: ignore[assignment]
    m = HTML_PDF_RE.search(html)  # type: ignore[arg-type]
    if m:
        return urllib.parse.urljoin(url, m.group(1)), "html citation_pdf_url"
    m = HTML_ANY_PDF_RE.search(html)  # type: ignore[arg-type]
    if m:
        return urllib.parse.urljoin(url, m.group(1)), "html first .pdf link"
    return None, "no pdf found on page"


# --------------------------------------------------------------------------- #
# filesystem
# --------------------------------------------------------------------------- #
def slugify(text: str, fallback: str = "paper") -> str:
    """Filesystem-safe slug, NFC-normalized (macOS hands back NFD paths)."""
    text = unicodedata.normalize("NFC", text)
    text = re.sub(r"[^\w.\- ]+", "", text)
    text = re.sub(r"[\s_]+", "-", text).strip("-.").lower()
    return text[:80] or fallback


def destination(out_dir: Path, paper: Paper) -> Path:
    name = f"{paper.index:02d}-{slugify(paper.title)}"
    aid = arxiv_id_from(paper.pdf_url or "") or arxiv_id_from(paper.link)
    if aid:
        name = f"{name}-{aid}"
    return out_dir / f"{name}.pdf"


def download(paper: Paper, out_dir: Path) -> Paper:
    """Fetch one paper's PDF into `out_dir`, updating `paper` in place."""
    if not paper.pdf_url:
        paper.status = "skipped"
        return paper
    dest = destination(out_dir, paper)
    paper.path = str(dest)

    if dest.exists() and dest.stat().st_size > 0:
        with dest.open("rb") as fh:
            if fh.read(5) == b"%PDF-":
                paper.status = "existing"
                return paper

    try:
        body, ctype = http_get(paper.pdf_url)
    except Exception as exc:  # noqa: BLE001
        paper.status = "failed"
        paper.detail = f"{paper.detail}; download failed: {exc}".strip("; ")
        return paper

    if not body[:5].startswith(b"%PDF-"):
        paper.status = "failed"
        paper.detail = f"{paper.detail}; not a PDF (content-type {ctype or '?'}, {len(body)} bytes)".strip("; ")
        return paper

    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(body)
    paper.status = "downloaded"
    return paper


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = p.add_argument_group("source")
    src.add_argument("--year", type=int, default=2026, help="issue year to fetch (default: 2026)")
    src.add_argument("--md", help="read this local Markdown file instead of fetching from GitHub")
    sel = p.add_argument_group("selection")
    sel.add_argument("--section", default="September 28 - October 4",
                     help="substring of the weekly heading/date to download (default: the Oct 4 2026 issue)")
    sel.add_argument("--all", action="store_true", help="download every section of the page")
    out = p.add_argument_group("output")
    out.add_argument("-o", "--out", type=Path, default=Path("papers"),
                     help="output directory (default: papers/)")
    out.add_argument("--flat", action="store_true",
                     help="write straight into --out instead of a per-section subfolder")
    out.add_argument("--arxiv-only", action="store_true", help="skip non-arXiv sources")
    out.add_argument("--dry-run", action="store_true", help="resolve URLs and print, but download nothing")
    out.add_argument("-j", "--jobs", type=int, default=4, help="parallel downloads (default: 4)")
    return p


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)

    md = fetch_markdown(args.year, args.md)
    sections = select_sections(split_sections(md), args.section, args.all)

    grand: list[Paper] = []
    for heading, body in sections:
        papers = parse_papers(body)
        if not papers:
            print(f"! {heading}: no numbered rows found", file=sys.stderr)
            continue

        out_dir = args.out if args.flat else args.out / slugify(f"{args.year}-{args.section or heading}")
        print(f"\n== {heading}: {len(papers)} papers -> {out_dir}")

        # resolve links (sequential: the HTML fallback hits the network politely)
        for paper in papers:
            if not paper.paper_links:
                paper.status, paper.detail = "skipped", "no paper link"
                continue
            pdf_url, detail = resolve_pdf(paper.paper_links[0])
            if pdf_url and args.arxiv_only and "arxiv.org" not in pdf_url:
                pdf_url, detail = None, f"{detail} (not arxiv)"
            paper.pdf_url, paper.detail = pdf_url, detail

        if args.dry_run:
            for paper in papers:
                mark = "ok " if paper.pdf_url else "-- "
                print(f"  {mark}{paper.index:2d}. {paper.title}")
                print(f"      {paper.detail} -> {paper.pdf_url or paper.paper_links[0]}")
        else:
            with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
                futures = {pool.submit(download, p, out_dir): p for p in papers}
                for fut in as_completed(futures):
                    p = fut.result()
                    icon = {"downloaded": "+", "existing": "=", "failed": "x", "skipped": "-"}.get(p.status, "?")
                    print(f"  [{icon}] {p.index:2d}. {p.title} ({p.status})")
                    if p.status == "failed":
                        print(f"      {p.detail}")

            manifest = out_dir / "manifest.json"
            manifest.parent.mkdir(parents=True, exist_ok=True)
            manifest.write_text(
                json.dumps(
                    {"year": args.year, "section": heading, "papers": [asdict(p) for p in papers]},
                    indent=2,
                ),
                encoding="utf-8",
            )
            print(f"  manifest -> {manifest}")

        grand.extend(papers)

    if grand and not args.dry_run:
        done = sum(1 for p in grand if p.status in ("downloaded", "existing"))
        print(f"\nDone: {done}/{len(grand)} PDFs available.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
