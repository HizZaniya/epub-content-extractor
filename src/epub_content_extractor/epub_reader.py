from pathlib import Path
from typing import Literal

import ebooklib
from ebooklib import epub

from epub_content_extractor.models import EpubMetadata, SpineItem


def read_epub(path: Path) -> tuple[EpubMetadata, list[SpineItem]]:
    """EPUBファイルを読み込みメタデータとスパインアイテムを返す。"""
    if not path.exists():
        raise FileNotFoundError(f"EPUB file not found: {path}")

    book = epub.read_epub(str(path), {"ignore_ncx": True})
    metadata = _extract_metadata(book)
    spine_items = _extract_spine(book)
    return metadata, spine_items


def _extract_metadata(book: epub.EpubBook) -> EpubMetadata:
    title = _get_dc(book, "title") or ""
    authors = _get_dc_list(book, "creator")
    language = _get_dc(book, "language") or "und"
    publisher = _get_dc(book, "publisher")
    identifier = _get_dc(book, "identifier")
    layout = _detect_layout(book)
    ppd = _detect_page_progression(book)
    return EpubMetadata(
        title=title,
        authors=authors,
        language=language,
        layout=layout,
        page_progression_direction=ppd,
        publisher=publisher,
        identifier=identifier,
    )


def _get_dc(book: epub.EpubBook, name: str) -> str | None:
    items = book.get_metadata("DC", name)
    if items:
        return items[0][0]
    return None


def _get_dc_list(book: epub.EpubBook, name: str) -> list[str]:
    return [v for v, _ in book.get_metadata("DC", name)]


def _detect_layout(book: epub.EpubBook) -> Literal["reflowable", "fixed-layout", "ahl"]:
    global_layout = "reflowable"
    fixed_count = 0
    reflowable_count = 0

    for value, attrs in book.get_metadata("OPF", "meta"):
        prop = attrs.get("property", "")
        if prop == "rendition:layout":
            if value == "pre-paginated":
                global_layout = "fixed-layout"
            else:
                global_layout = "reflowable"

    for idref, _ in book.spine:
        item = book.get_item_with_id(idref)
        if item is None:
            continue
        props = getattr(item, "properties", []) or []
        if isinstance(props, str):
            props = props.split()
        if "rendition:layout-pre-paginated" in props:
            fixed_count += 1
        elif "rendition:layout-reflowable" in props:
            reflowable_count += 1

    if fixed_count > 0 and reflowable_count > 0:
        return "ahl"
    if fixed_count > 0 and global_layout == "reflowable":
        return "ahl"
    if global_layout == "fixed-layout":
        return "fixed-layout"
    return "reflowable"


def _detect_page_progression(book: epub.EpubBook) -> Literal["ltr", "rtl"]:
    for value, attrs in book.get_metadata("OPF", "meta"):
        if attrs.get("property") == "page-progression-direction":
            if value == "rtl":
                return "rtl"
            if value == "ltr":
                return "ltr"
    return "ltr"


def _extract_spine(book: epub.EpubBook) -> list[SpineItem]:
    toc_map = _build_toc_map(book)
    items: list[SpineItem] = []
    order = 1
    for idref, _ in book.spine:
        item = book.get_item_with_id(idref)
        if item is None or item.get_type() != ebooklib.ITEM_DOCUMENT:
            continue
        if isinstance(item, epub.EpubNav):
            continue
        href = item.file_name
        title = toc_map.get(href) or getattr(item, "title", None)
        items.append(SpineItem(id=idref, href=href, title=title, order=order))
        order += 1
    return items


def _build_toc_map(book: epub.EpubBook) -> dict[str, str]:
    toc_map: dict[str, str] = {}

    def traverse(items: list) -> None:  # type: ignore[type-arg]
        for entry in items:
            if isinstance(entry, tuple):
                section, children = entry
                if hasattr(section, "href") and section.title:
                    toc_map[section.href.split("#")[0]] = section.title
                traverse(children)
            elif hasattr(entry, "href") and getattr(entry, "title", None):
                toc_map[entry.href.split("#")[0]] = entry.title
            elif hasattr(entry, "file_name") and getattr(entry, "title", None):
                toc_map[entry.file_name] = entry.title

    traverse(book.toc)
    return toc_map
