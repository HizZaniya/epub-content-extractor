from pathlib import Path

from fastmcp import FastMCP

from epub_content_extractor.extractor import (
    extract_epub as _extract_epub,
)
from epub_content_extractor.extractor import (
    get_epub_metadata as _get_epub_metadata,
)
from epub_content_extractor.extractor import (
    list_epub_spine as _list_epub_spine,
)

mcp = FastMCP("epub-content-extractor")


def _extract_epub_impl(source: str, output_dir: str | None = None) -> dict:
    return _extract_epub(Path(source), Path(output_dir) if output_dir else None)


def _get_epub_metadata_impl(source: str) -> dict:
    return _get_epub_metadata(Path(source))


def _list_epub_spine_impl(source: str) -> dict:
    return _list_epub_spine(Path(source))


@mcp.tool()
def extract_epub(source: str, output_dir: str | None = None) -> dict:
    """Extract all EPUB content as Markdown files."""
    return _extract_epub_impl(source, output_dir)


@mcp.tool()
def get_epub_metadata(source: str) -> dict:
    """Get EPUB metadata without extraction."""
    return _get_epub_metadata_impl(source)


@mcp.tool()
def list_epub_spine(source: str) -> dict:
    """List EPUB spine items in reading order."""
    return _list_epub_spine_impl(source)


def run() -> None:
    mcp.run()
