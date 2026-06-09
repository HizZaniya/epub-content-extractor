from pathlib import Path
from typing import Literal

import ebooklib
from ebooklib import epub

from epub_content_extractor.content_converter import convert_html
from epub_content_extractor.epub_reader import read_epub, read_epub_book
from epub_content_extractor.image_extractor import extract_images
from epub_content_extractor.markdown_writer import write_chapter
from epub_content_extractor.models import ContentBlock


def extract_epub(epub_path: Path, output_dir: Path | None) -> dict:
    epub_path = Path(epub_path)
    if output_dir is None:
        output_dir = epub_path.parent / epub_path.stem
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not epub_path.exists():
        raise FileNotFoundError(f"EPUB file not found: {epub_path}")
    book = epub.read_epub(str(epub_path), {"ignore_ncx": True})
    metadata, spine_items = read_epub_book(book)

    image_mapping = extract_images(book, output_dir)

    written_files: list[str] = []
    for spine_item in spine_items:
        item = book.get_item_with_href(spine_item.href)
        if item is None:
            item = book.get_item_with_id(spine_item.id)
        if item is None or item.get_type() != ebooklib.ITEM_DOCUMENT:
            continue

        item_layout = _get_item_layout(book, spine_item.id, metadata.layout)
        blocks = convert_html(
            item.content,
            layout=item_layout,
            ppd=metadata.page_progression_direction,
            spine_href=spine_item.href,
        )
        blocks = _resolve_image_paths(blocks, image_mapping, output_dir)

        md_path = write_chapter(blocks, metadata, spine_item, output_dir)
        written_files.append(str(md_path))

    return {
        "output_dir": str(output_dir),
        "files": written_files,
        "chapters": len(written_files),
    }


def _get_item_layout(
    book: epub.EpubBook, item_id: str, global_layout: str
) -> Literal["reflowable", "fixed-layout"]:
    item = book.get_item_with_id(item_id)
    if item is None:
        return "fixed-layout" if global_layout == "fixed-layout" else "reflowable"
    props = getattr(item, "properties", []) or []
    if isinstance(props, str):
        props = props.split()
    if "rendition:layout-pre-paginated" in props:
        return "fixed-layout"
    if "rendition:layout-reflowable" in props:
        return "reflowable"
    return "fixed-layout" if global_layout == "fixed-layout" else "reflowable"


def _resolve_image_paths(
    blocks: list[ContentBlock],
    image_mapping: dict[str, Path],
    output_dir: Path,
) -> list[ContentBlock]:
    resolved: list[ContentBlock] = []
    for block in blocks:
        if block.type == "image" and block.content in image_mapping:
            rel = image_mapping[block.content].relative_to(output_dir)
            resolved.append(ContentBlock(type="image", content=str(rel)))
        else:
            resolved.append(block)
    return resolved


def get_epub_metadata(epub_path: Path) -> dict:
    metadata, _ = read_epub(Path(epub_path))
    return {
        "title": metadata.title,
        "authors": metadata.authors,
        "language": metadata.language,
        "layout": metadata.layout,
        "page_progression_direction": metadata.page_progression_direction,
        "publisher": metadata.publisher,
        "identifier": metadata.identifier,
    }


def list_epub_spine(epub_path: Path) -> dict:
    _, spine_items = read_epub(Path(epub_path))
    return {
        "spine": [
            {
                "id": item.id,
                "href": item.href,
                "title": item.title,
                "order": item.order,
            }
            for item in spine_items
        ]
    }
