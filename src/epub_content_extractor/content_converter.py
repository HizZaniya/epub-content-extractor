from pathlib import PurePosixPath
from typing import Literal

from bs4 import BeautifulSoup, Tag

from epub_content_extractor.models import ContentBlock


def convert_html(
    html: bytes,
    layout: Literal["reflowable", "fixed-layout", "ahl"],
    ppd: Literal["ltr", "rtl"],
    spine_href: str,
) -> list[ContentBlock]:
    soup = BeautifulSoup(html, "lxml")
    body = soup.find("body")
    if body is None:
        return []

    if layout == "fixed-layout":
        return _convert_fixed(body, ppd, spine_href)
    return _convert_reflowable(body, spine_href)


def _convert_reflowable(body: Tag, spine_href: str) -> list[ContentBlock]:
    blocks: list[ContentBlock] = []
    for tag in body.descendants:
        if not isinstance(tag, Tag):
            continue
        if tag.name in ("h1", "h2", "h3", "h4", "h5", "h6"):
            text = tag.get_text(strip=True)
            if text:
                blocks.append(ContentBlock(type="heading", content=text, level=int(tag.name[1])))
        elif tag.name == "p":
            text = tag.get_text(strip=True)
            if text:
                blocks.append(ContentBlock(type="paragraph", content=text))
        elif tag.name == "img":
            src = tag.get("src", "")
            resolved = _resolve_href(spine_href, str(src))
            blocks.append(ContentBlock(type="image", content=resolved))
        elif tag.name == "table":
            text = _table_to_text(tag)
            blocks.append(ContentBlock(type="table", content=text))
    return blocks


def _resolve_href(spine_href: str, img_src: str) -> str:
    base = PurePosixPath(spine_href).parent
    resolved = base / img_src
    parts: list[str] = []
    for part in resolved.parts:
        if part == "..":
            if parts:
                parts.pop()
        elif part != ".":
            parts.append(part)
    return "/".join(parts)


def _table_to_text(table: Tag) -> str:
    rows: list[str] = []
    for tr in table.find_all("tr"):
        cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
        rows.append("| " + " | ".join(cells) + " |")
    return "\n".join(rows)


def _convert_fixed(body: Tag, ppd: Literal["ltr", "rtl"], spine_href: str) -> list[ContentBlock]:
    elements: list[tuple[float, float, Tag]] = []
    for tag in body.find_all(True):
        if not isinstance(tag, Tag):
            continue
        style = tag.get("style", "")
        if "position" not in str(style) or "absolute" not in str(style):
            continue
        x, y = _parse_xy(str(style))
        elements.append((x, y, tag))

    sorted_elements = _sort_fixed_elements(elements, ppd)
    blocks: list[ContentBlock] = []
    for _, _, tag in sorted_elements:
        if tag.name == "img":
            src = tag.get("src", "")
            resolved = _resolve_href(spine_href, str(src))
            blocks.append(ContentBlock(type="image", content=resolved))
        else:
            text = tag.get_text(strip=True)
            if text:
                blocks.append(ContentBlock(type="paragraph", content=text))
    return blocks


def _parse_xy(style: str) -> tuple[float, float]:
    x = y = 0.0
    for part in style.split(";"):
        part = part.strip()
        if part.startswith("left:"):
            x = _parse_px(part.split(":", 1)[1])
        elif part.startswith("top:"):
            y = _parse_px(part.split(":", 1)[1])
    return x, y


def _parse_px(value: str) -> float:
    return float(value.strip().replace("px", "").strip() or "0")


_COLUMN_TOLERANCE = 50.0


def _sort_fixed_elements(
    elements: list[tuple[float, float, Tag]], ppd: Literal["ltr", "rtl"]
) -> list[tuple[float, float, Tag]]:
    if not elements:
        return []

    sorted_by_x = sorted(elements, key=lambda e: e[0], reverse=(ppd == "rtl"))
    columns: list[list[tuple[float, float, Tag]]] = []
    current_col: list[tuple[float, float, Tag]] = [sorted_by_x[0]]

    for el in sorted_by_x[1:]:
        if abs(el[0] - current_col[0][0]) <= _COLUMN_TOLERANCE:
            current_col.append(el)
        else:
            columns.append(sorted(current_col, key=lambda e: e[1]))
            current_col = [el]
    columns.append(sorted(current_col, key=lambda e: e[1]))

    result: list[tuple[float, float, Tag]] = []
    for col in columns:
        result.extend(col)
    return result
