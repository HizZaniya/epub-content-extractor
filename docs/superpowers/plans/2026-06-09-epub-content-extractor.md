# epub-content-extractor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** EPUBファイルからテキストと画像を抽出しMarkdownファイル群として出力するCLIツールとMCPサーバを実装する。

**Architecture:** 7つの専門モジュールがレイヤー分離されたアーキテクチャ。`epub_reader` → `content_converter` / `image_extractor` → `markdown_writer` → `extractor`（オーケストレーション）→ `cli` / `server`（エントリーポイント）。t-wada式TDD（Red→Green→Refactor）を全タスクで厳守。

**Tech Stack:** Python 3.13, ebooklib>=0.18, BeautifulSoup4>=4.12 + lxml>=5.0, typer>=0.12, FastMCP>=3.3.1, pytest + pytest-mock

---

## ファイルマップ

| ファイル | 役割 |
|---|---|
| `src/epub_content_extractor/models.py` | 新規: 共有データクラス（EpubMetadata, SpineItem, ContentBlock） |
| `src/epub_content_extractor/epub_reader.py` | 新規: ebooklibラッパー（メタデータ・スパイン抽出） |
| `src/epub_content_extractor/content_converter.py` | 新規: HTML→ContentBlock[]変換（リフロー/フィックス/AHL対応） |
| `src/epub_content_extractor/image_extractor.py` | 新規: EPUB内画像→出力ディレクトリへの保存 |
| `src/epub_content_extractor/markdown_writer.py` | 新規: ContentBlock[]→Markdownファイル書き出し |
| `src/epub_content_extractor/extractor.py` | 新規: 全体オーケストレーション |
| `src/epub_content_extractor/cli.py` | 新規: typer CLIエントリーポイント |
| `src/epub_content_extractor/server.py` | 新規: FastMCP サーバ（3 MCPツール定義） |
| `src/epub_content_extractor/__main__.py` | 更新: `main()`をcli.appに委譲 |
| `src/epub_content_extractor/__init__.py` | 更新: 公開APIをエクスポート |
| `pyproject.toml` | 更新: `epub-content-extractor` MCPサーバエントリーポイントを追加 |
| `tests/conftest.py` | 新規: テスト用EPUBフィクスチャ |
| `tests/test_models.py` | 新規 |
| `tests/test_epub_reader.py` | 新規 |
| `tests/test_content_converter.py` | 新規 |
| `tests/test_image_extractor.py` | 新規 |
| `tests/test_markdown_writer.py` | 新規 |
| `tests/test_extractor.py` | 新規（統合テスト） |
| `tests/test_cli.py` | 新規 |
| `tests/test_server.py` | 新規 |

---

### Task 1: 共有データモデル（models.py）

**Files:**
- Create: `src/epub_content_extractor/models.py`
- Create: `tests/test_models.py`

- [ ] **Step 1: failing testを書く**

```python
# tests/test_models.py
from epub_content_extractor.models import ContentBlock, EpubMetadata, SpineItem


def test_epub_metadata_reflowable() -> None:
    meta = EpubMetadata(
        title="Test Book",
        authors=["Author A"],
        language="ja",
        layout="reflowable",
        page_progression_direction="rtl",
        publisher=None,
        identifier=None,
    )
    assert meta.title == "Test Book"
    assert meta.layout == "reflowable"
    assert meta.page_progression_direction == "rtl"
    assert meta.publisher is None


def test_epub_metadata_fixed_layout() -> None:
    meta = EpubMetadata(
        title="Fixed",
        authors=[],
        language="ja",
        layout="fixed-layout",
        page_progression_direction="rtl",
        publisher="Publisher",
        identifier="urn:isbn:9784000000000",
    )
    assert meta.layout == "fixed-layout"
    assert meta.identifier == "urn:isbn:9784000000000"


def test_spine_item_creation() -> None:
    item = SpineItem(id="ch1", href="OEBPS/chapter01.xhtml", title="Chapter 1", order=1)
    assert item.id == "ch1"
    assert item.href == "OEBPS/chapter01.xhtml"
    assert item.order == 1


def test_spine_item_no_title() -> None:
    item = SpineItem(id="ch2", href="chapter02.xhtml", title=None, order=2)
    assert item.title is None


def test_content_block_heading() -> None:
    block = ContentBlock(type="heading", content="Chapter 1", level=1)
    assert block.type == "heading"
    assert block.level == 1


def test_content_block_paragraph() -> None:
    block = ContentBlock(type="paragraph", content="Hello World", level=None)
    assert block.type == "paragraph"
    assert block.level is None


def test_content_block_image() -> None:
    block = ContentBlock(type="image", content="images/fig001.png", level=None)
    assert block.type == "image"


def test_content_block_table() -> None:
    block = ContentBlock(type="table", content="| A | B |", level=None)
    assert block.type == "table"
```

- [ ] **Step 2: testが失敗することを確認**

```bash
uv run pytest tests/test_models.py -v
```

期待出力: `ImportError: cannot import name 'ContentBlock' from 'epub_content_extractor.models'`

- [ ] **Step 3: 最小実装を書く**

```python
# src/epub_content_extractor/models.py
from dataclasses import dataclass
from typing import Literal


@dataclass
class EpubMetadata:
    title: str
    authors: list[str]
    language: str
    layout: Literal["reflowable", "fixed-layout", "ahl"]
    page_progression_direction: Literal["ltr", "rtl"]
    publisher: str | None
    identifier: str | None


@dataclass
class SpineItem:
    id: str
    href: str
    title: str | None
    order: int


@dataclass
class ContentBlock:
    type: Literal["heading", "paragraph", "image", "table"]
    content: str
    level: int | None = None
```

- [ ] **Step 4: testがpassすることを確認**

```bash
uv run pytest tests/test_models.py -v
```

期待出力: `8 passed`

- [ ] **Step 5: lintとtype checkを確認**

```bash
uv run ruff check src/epub_content_extractor/models.py tests/test_models.py
uv run ty check
```

- [ ] **Step 6: commit**

```bash
git add src/epub_content_extractor/models.py tests/test_models.py
git commit -m "feat: add shared data models (EpubMetadata, SpineItem, ContentBlock)"
```

---

### Task 2: テスト用EPUBフィクスチャ（conftest.py）

**Files:**
- Create: `tests/conftest.py`

- [ ] **Step 1: conftest.pyを書く**

```python
# tests/conftest.py
import pytest
from ebooklib import epub


@pytest.fixture
def reflowable_epub(tmp_path):
    """最小限のリフロー型EPUBを生成する。"""
    book = epub.EpubBook()
    book.set_identifier("test-reflowable-1")
    book.set_title("Reflowable Test Book")
    book.set_language("ja")
    book.add_author("Test Author")
    book.add_metadata(None, "meta", "reflowable", {"property": "rendition:layout"})
    book.add_metadata(None, "meta", "rtl", {"property": "page-progression-direction"})

    ch1 = epub.EpubHtml(title="Chapter 1", file_name="chapter01.xhtml", lang="ja")
    ch1.content = (
        b'<?xml version="1.0" encoding="UTF-8"?>'
        b"<html><body>"
        b"<h1>Chapter 1</h1>"
        b"<p>Hello World</p>"
        b"<h2>Section 1.1</h2>"
        b"<p>Paragraph text.</p>"
        b"</body></html>"
    )

    ch2 = epub.EpubHtml(title="Chapter 2", file_name="chapter02.xhtml", lang="ja")
    ch2.content = (
        b'<?xml version="1.0" encoding="UTF-8"?>'
        b"<html><body>"
        b"<h1>Chapter 2</h1>"
        b"<p>Second chapter.</p>"
        b"</body></html>"
    )

    nav = epub.EpubNav()
    book.add_item(ch1)
    book.add_item(ch2)
    book.add_item(nav)
    book.toc = [ch1, ch2]
    book.spine = ["nav", ch1, ch2]

    path = tmp_path / "reflowable.epub"
    epub.write_epub(str(path), book)
    return path


@pytest.fixture
def fixed_epub(tmp_path):
    """最小限のフィックス型EPUB（rtl）を生成する。"""
    book = epub.EpubBook()
    book.set_identifier("test-fixed-1")
    book.set_title("Fixed Layout Test Book")
    book.set_language("ja")
    book.add_author("Test Author")
    book.add_metadata(None, "meta", "pre-paginated", {"property": "rendition:layout"})
    book.add_metadata(None, "meta", "rtl", {"property": "page-progression-direction"})

    page1 = epub.EpubHtml(title="Page 1", file_name="page01.xhtml", lang="ja")
    page1.content = (
        b'<?xml version="1.0" encoding="UTF-8"?>'
        b"<html><body>"
        b'<div style="position: absolute; left: 700px; top: 100px;">Right text</div>'
        b'<div style="position: absolute; left: 100px; top: 100px;">Left text</div>'
        b'<div style="position: absolute; left: 700px; top: 200px;">Right second</div>'
        b"</body></html>"
    )

    nav = epub.EpubNav()
    book.add_item(page1)
    book.add_item(nav)
    book.toc = []
    book.spine = ["nav", page1]

    path = tmp_path / "fixed.epub"
    epub.write_epub(str(path), book)
    return path


@pytest.fixture
def epub_with_image(tmp_path):
    """画像を含むリフロー型EPUBを生成する。"""
    book = epub.EpubBook()
    book.set_identifier("test-image-1")
    book.set_title("Image Test Book")
    book.set_language("ja")
    book.add_author("Test Author")

    # 1x1の白ピクセルPNG（最小PNG）
    png_bytes = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
        b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00"
        b"\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18"
        b"\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    img = epub.EpubImage()
    img.id = "img1"
    img.file_name = "images/fig001.png"
    img.media_type = "image/png"
    img.content = png_bytes

    ch1 = epub.EpubHtml(title="Chapter 1", file_name="chapter01.xhtml", lang="ja")
    ch1.content = (
        b'<?xml version="1.0" encoding="UTF-8"?>'
        b"<html><body>"
        b"<h1>Chapter 1</h1>"
        b'<img src="../images/fig001.png" alt="Figure 1"/>'
        b"<p>Caption text.</p>"
        b"</body></html>"
    )

    nav = epub.EpubNav()
    book.add_item(img)
    book.add_item(ch1)
    book.add_item(nav)
    book.toc = [ch1]
    book.spine = ["nav", ch1]

    path = tmp_path / "with_image.epub"
    epub.write_epub(str(path), book)
    return path
```

- [ ] **Step 2: フィクスチャが使えることを確認**

```bash
uv run pytest tests/ --collect-only 2>&1 | head -20
```

期待出力: テスト収集時にエラーなし

- [ ] **Step 3: commit**

```bash
git add tests/conftest.py
git commit -m "test: add shared EPUB fixtures to conftest.py"
```

---

### Task 3: EPUB読み込み – メタデータとスパイン（epub_reader.py）

**Files:**
- Create: `src/epub_content_extractor/epub_reader.py`
- Create: `tests/test_epub_reader.py`

- [ ] **Step 1: failing testを書く**

```python
# tests/test_epub_reader.py
from pathlib import Path

import pytest

from epub_content_extractor.epub_reader import read_epub
from epub_content_extractor.models import EpubMetadata, SpineItem


def test_read_metadata_reflowable(reflowable_epub: Path) -> None:
    metadata, _ = read_epub(reflowable_epub)
    assert isinstance(metadata, EpubMetadata)
    assert metadata.title == "Reflowable Test Book"
    assert metadata.authors == ["Test Author"]
    assert metadata.language == "ja"
    assert metadata.layout == "reflowable"
    assert metadata.page_progression_direction == "rtl"


def test_read_metadata_fixed(fixed_epub: Path) -> None:
    metadata, _ = read_epub(fixed_epub)
    assert metadata.layout == "fixed-layout"
    assert metadata.page_progression_direction == "rtl"


def test_read_spine_items(reflowable_epub: Path) -> None:
    _, spine_items = read_epub(reflowable_epub)
    assert len(spine_items) == 2
    assert all(isinstance(item, SpineItem) for item in spine_items)


def test_spine_items_ordered(reflowable_epub: Path) -> None:
    _, spine_items = read_epub(reflowable_epub)
    orders = [item.order for item in spine_items]
    assert orders == sorted(orders)
    assert orders[0] == 1


def test_spine_items_have_title(reflowable_epub: Path) -> None:
    _, spine_items = read_epub(reflowable_epub)
    titles = [item.title for item in spine_items]
    assert "Chapter 1" in titles


def test_spine_items_have_href(reflowable_epub: Path) -> None:
    _, spine_items = read_epub(reflowable_epub)
    hrefs = [item.href for item in spine_items]
    assert any("chapter01.xhtml" in h for h in hrefs)


def test_epub_file_not_found() -> None:
    with pytest.raises(FileNotFoundError):
        read_epub(Path("/nonexistent/path.epub"))
```

- [ ] **Step 2: testが失敗することを確認**

```bash
uv run pytest tests/test_epub_reader.py -v
```

期待出力: `ImportError: cannot import name 'read_epub'`

- [ ] **Step 3: 最小実装を書く**

```python
# src/epub_content_extractor/epub_reader.py
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

    for value, attrs in book.get_metadata(None, "meta"):
        prop = attrs.get("property", "")
        if prop == "rendition:layout":
            if value == "pre-paginated":
                global_layout = "fixed-layout"
            else:
                global_layout = "reflowable"

    # AHL判定: スパインアイテムに個別のlayout overrideがある場合
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
    return global_layout  # type: ignore[return-value]


def _detect_page_progression(book: epub.EpubBook) -> Literal["ltr", "rtl"]:
    for value, attrs in book.get_metadata(None, "meta"):
        if attrs.get("property") == "page-progression-direction":
            if value in ("ltr", "rtl"):
                return value  # type: ignore[return-value]
    return "ltr"


def _extract_spine(book: epub.EpubBook) -> list[SpineItem]:
    toc_map = _build_toc_map(book)
    items: list[SpineItem] = []
    order = 1
    for idref, _ in book.spine:
        item = book.get_item_with_id(idref)
        if item is None or item.get_type() != ebooklib.ITEM_DOCUMENT:
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
            elif hasattr(entry, "file_name") and getattr(entry, "title", None):
                toc_map[entry.file_name] = entry.title

    traverse(book.toc)
    return toc_map
```

- [ ] **Step 4: testがpassすることを確認**

```bash
uv run pytest tests/test_epub_reader.py -v
```

期待出力: `7 passed`

- [ ] **Step 5: lintとtype checkを確認**

```bash
uv run ruff check src/epub_content_extractor/epub_reader.py tests/test_epub_reader.py
uv run ty check
```

- [ ] **Step 6: commit**

```bash
git add src/epub_content_extractor/epub_reader.py tests/test_epub_reader.py
git commit -m "feat: implement epub_reader (metadata + spine extraction)"
```

---

### Task 4: コンテンツ変換 – リフロー型（content_converter.py）

**Files:**
- Create: `src/epub_content_extractor/content_converter.py`
- Create: `tests/test_content_converter.py`

- [ ] **Step 1: failing testを書く（リフロー型）**

```python
# tests/test_content_converter.py
import pytest

from epub_content_extractor.content_converter import convert_html
from epub_content_extractor.models import ContentBlock


def test_heading_h1() -> None:
    html = b"<html><body><h1>Chapter 1</h1></body></html>"
    blocks = convert_html(html, layout="reflowable", ppd="ltr", spine_href="ch.xhtml")
    assert len(blocks) == 1
    assert blocks[0].type == "heading"
    assert blocks[0].level == 1
    assert blocks[0].content == "Chapter 1"


def test_heading_levels() -> None:
    html = b"<html><body><h2>Section</h2><h3>Subsection</h3></body></html>"
    blocks = convert_html(html, layout="reflowable", ppd="ltr", spine_href="ch.xhtml")
    assert blocks[0].level == 2
    assert blocks[1].level == 3


def test_paragraph() -> None:
    html = b"<html><body><p>Hello World</p></body></html>"
    blocks = convert_html(html, layout="reflowable", ppd="ltr", spine_href="ch.xhtml")
    assert len(blocks) == 1
    assert blocks[0].type == "paragraph"
    assert blocks[0].content == "Hello World"


def test_empty_paragraph_skipped() -> None:
    html = b"<html><body><p></p><p>Text</p></body></html>"
    blocks = convert_html(html, layout="reflowable", ppd="ltr", spine_href="ch.xhtml")
    assert len(blocks) == 1
    assert blocks[0].content == "Text"


def test_image_tag() -> None:
    html = b'<html><body><img src="../images/fig001.png" alt="fig"/></body></html>'
    blocks = convert_html(html, layout="reflowable", ppd="ltr", spine_href="OEBPS/ch.xhtml")
    assert len(blocks) == 1
    assert blocks[0].type == "image"
    assert "fig001.png" in blocks[0].content


def test_image_src_resolved() -> None:
    html = b'<html><body><img src="../images/fig001.png"/></body></html>'
    blocks = convert_html(html, layout="reflowable", ppd="ltr", spine_href="OEBPS/Text/ch.xhtml")
    # resolved: OEBPS/images/fig001.png
    assert blocks[0].content == "OEBPS/images/fig001.png"


def test_table() -> None:
    html = b"<html><body><table><tr><td>A</td><td>B</td></tr></table></body></html>"
    blocks = convert_html(html, layout="reflowable", ppd="ltr", spine_href="ch.xhtml")
    assert len(blocks) == 1
    assert blocks[0].type == "table"
    assert "A" in blocks[0].content
    assert "B" in blocks[0].content


def test_multiple_blocks_in_order() -> None:
    html = b"<html><body><h1>Title</h1><p>Para</p></body></html>"
    blocks = convert_html(html, layout="reflowable", ppd="ltr", spine_href="ch.xhtml")
    assert blocks[0].type == "heading"
    assert blocks[1].type == "paragraph"
```

- [ ] **Step 2: testが失敗することを確認**

```bash
uv run pytest tests/test_content_converter.py -v
```

期待出力: `ImportError: cannot import name 'convert_html'`

- [ ] **Step 3: リフロー型の最小実装を書く**

```python
# src/epub_content_extractor/content_converter.py
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
    """HTML bytesをContentBlock列に変換する。"""
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
    """フィックス型: position:absoluteの要素を座標ソートしてContentBlock列を返す。"""
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
```

- [ ] **Step 4: testがpassすることを確認**

```bash
uv run pytest tests/test_content_converter.py -v
```

期待出力: `8 passed`

- [ ] **Step 5: フィックス型の追加テストを書く**

```python
# tests/test_content_converter.py に追記

def test_fixed_layout_rtl_order() -> None:
    # RTL: X大きい方（右）が先
    html = (
        b"<html><body>"
        b'<div style="position: absolute; left: 700px; top: 100px;">Right</div>'
        b'<div style="position: absolute; left: 100px; top: 100px;">Left</div>'
        b"</body></html>"
    )
    blocks = convert_html(html, layout="fixed-layout", ppd="rtl", spine_href="page.xhtml")
    assert blocks[0].content == "Right"
    assert blocks[1].content == "Left"


def test_fixed_layout_ltr_order() -> None:
    # LTR: X小さい方（左）が先
    html = (
        b"<html><body>"
        b'<div style="position: absolute; left: 700px; top: 100px;">Right</div>'
        b'<div style="position: absolute; left: 100px; top: 100px;">Left</div>'
        b"</body></html>"
    )
    blocks = convert_html(html, layout="fixed-layout", ppd="ltr", spine_href="page.xhtml")
    assert blocks[0].content == "Left"
    assert blocks[1].content == "Right"


def test_fixed_layout_column_y_order() -> None:
    # 同じカラム内でY昇順
    html = (
        b"<html><body>"
        b'<div style="position: absolute; left: 700px; top: 200px;">Second</div>'
        b'<div style="position: absolute; left: 700px; top: 100px;">First</div>'
        b"</body></html>"
    )
    blocks = convert_html(html, layout="fixed-layout", ppd="rtl", spine_href="page.xhtml")
    assert blocks[0].content == "First"
    assert blocks[1].content == "Second"
```

- [ ] **Step 6: 追加testがpassすることを確認**

```bash
uv run pytest tests/test_content_converter.py -v
```

期待出力: `11 passed`

- [ ] **Step 7: commit**

```bash
git add src/epub_content_extractor/content_converter.py tests/test_content_converter.py
git commit -m "feat: implement content_converter (reflowable + fixed-layout HTML to ContentBlock)"
```

---

### Task 5: 画像抽出（image_extractor.py）

**Files:**
- Create: `src/epub_content_extractor/image_extractor.py`
- Create: `tests/test_image_extractor.py`

- [ ] **Step 1: failing testを書く**

```python
# tests/test_image_extractor.py
from pathlib import Path

import pytest
from ebooklib import epub

from epub_content_extractor.image_extractor import extract_images


def test_extract_images_creates_directory(epub_with_image: Path, tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    book = epub.read_epub(str(epub_with_image), {"ignore_ncx": True})
    mapping = extract_images(book, output_dir)
    assert (output_dir / "images").is_dir()


def test_extract_images_saves_file(epub_with_image: Path, tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    book = epub.read_epub(str(epub_with_image), {"ignore_ncx": True})
    mapping = extract_images(book, output_dir)
    assert len(mapping) == 1
    saved_path = list(mapping.values())[0]
    assert saved_path.exists()


def test_extract_images_returns_mapping(epub_with_image: Path, tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    book = epub.read_epub(str(epub_with_image), {"ignore_ncx": True})
    mapping = extract_images(book, output_dir)
    # キーはEPUB内のhref, 値はPathオブジェクト
    epub_hrefs = list(mapping.keys())
    assert any("fig001.png" in h for h in epub_hrefs)


def test_extract_images_filename(epub_with_image: Path, tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    book = epub.read_epub(str(epub_with_image), {"ignore_ncx": True})
    mapping = extract_images(book, output_dir)
    saved = list(mapping.values())[0]
    assert saved.name == "fig001.png"
    assert saved.parent.name == "images"


def test_no_images_returns_empty(reflowable_epub: Path, tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    book = epub.read_epub(str(reflowable_epub), {"ignore_ncx": True})
    mapping = extract_images(book, output_dir)
    assert mapping == {}
```

- [ ] **Step 2: testが失敗することを確認**

```bash
uv run pytest tests/test_image_extractor.py -v
```

期待出力: `ImportError: cannot import name 'extract_images'`

- [ ] **Step 3: 最小実装を書く**

```python
# src/epub_content_extractor/image_extractor.py
from pathlib import Path

import ebooklib
from ebooklib import epub


def extract_images(book: epub.EpubBook, output_dir: Path) -> dict[str, Path]:
    """EPUB内の全画像を output_dir/images/ に保存し href→Path のマッピングを返す。"""
    mapping: dict[str, Path] = {}
    images_dir = output_dir / "images"

    for item in book.get_items_of_type(ebooklib.ITEM_IMAGE):
        images_dir.mkdir(parents=True, exist_ok=True)
        filename = Path(item.file_name).name
        dest = images_dir / filename
        dest.write_bytes(item.content)
        mapping[item.file_name] = dest

    return mapping
```

- [ ] **Step 4: testがpassすることを確認**

```bash
uv run pytest tests/test_image_extractor.py -v
```

期待出力: `5 passed`

- [ ] **Step 5: commit**

```bash
git add src/epub_content_extractor/image_extractor.py tests/test_image_extractor.py
git commit -m "feat: implement image_extractor (EPUB images to output directory)"
```

---

### Task 6: Markdown出力（markdown_writer.py）

**Files:**
- Create: `src/epub_content_extractor/markdown_writer.py`
- Create: `tests/test_markdown_writer.py`

- [ ] **Step 1: failing testを書く**

```python
# tests/test_markdown_writer.py
from pathlib import Path

import pytest

from epub_content_extractor.markdown_writer import write_chapter
from epub_content_extractor.models import ContentBlock, EpubMetadata, SpineItem


@pytest.fixture
def sample_metadata() -> EpubMetadata:
    return EpubMetadata(
        title="Test Book",
        authors=["Author A"],
        language="ja",
        layout="reflowable",
        page_progression_direction="rtl",
        publisher="Test Publisher",
        identifier="urn:isbn:9784000000000",
    )


@pytest.fixture
def sample_spine_item() -> SpineItem:
    return SpineItem(id="ch1", href="chapter01.xhtml", title="Chapter 1", order=1)


def test_write_chapter_creates_file(
    tmp_path: Path, sample_metadata: EpubMetadata, sample_spine_item: SpineItem
) -> None:
    blocks = [ContentBlock(type="paragraph", content="Hello World")]
    write_chapter(blocks, sample_metadata, sample_spine_item, tmp_path)
    assert (tmp_path / "chapter_001.md").exists()


def test_write_chapter_filename_uses_order(
    tmp_path: Path, sample_metadata: EpubMetadata
) -> None:
    item = SpineItem(id="ch5", href="ch5.xhtml", title="Chapter 5", order=5)
    blocks: list[ContentBlock] = []
    write_chapter(blocks, sample_metadata, item, tmp_path)
    assert (tmp_path / "chapter_005.md").exists()


def test_yaml_front_matter(
    tmp_path: Path, sample_metadata: EpubMetadata, sample_spine_item: SpineItem
) -> None:
    blocks: list[ContentBlock] = []
    write_chapter(blocks, sample_metadata, sample_spine_item, tmp_path)
    content = (tmp_path / "chapter_001.md").read_text(encoding="utf-8")
    assert content.startswith("---\n")
    assert 'title: "Test Book"' in content
    assert "language: ja" in content
    assert 'chapter_title: "Chapter 1"' in content
    assert "spine_order: 1" in content
    assert "epub_layout: reflowable" in content
    assert "page_progression_direction: rtl" in content


def test_heading_output(
    tmp_path: Path, sample_metadata: EpubMetadata, sample_spine_item: SpineItem
) -> None:
    blocks = [ContentBlock(type="heading", content="My Heading", level=1)]
    write_chapter(blocks, sample_metadata, sample_spine_item, tmp_path)
    content = (tmp_path / "chapter_001.md").read_text(encoding="utf-8")
    assert "# My Heading" in content


def test_heading_level_2(
    tmp_path: Path, sample_metadata: EpubMetadata, sample_spine_item: SpineItem
) -> None:
    blocks = [ContentBlock(type="heading", content="Section", level=2)]
    write_chapter(blocks, sample_metadata, sample_spine_item, tmp_path)
    content = (tmp_path / "chapter_001.md").read_text(encoding="utf-8")
    assert "## Section" in content


def test_paragraph_output(
    tmp_path: Path, sample_metadata: EpubMetadata, sample_spine_item: SpineItem
) -> None:
    blocks = [ContentBlock(type="paragraph", content="Hello World")]
    write_chapter(blocks, sample_metadata, sample_spine_item, tmp_path)
    content = (tmp_path / "chapter_001.md").read_text(encoding="utf-8")
    assert "Hello World" in content


def test_image_output(
    tmp_path: Path, sample_metadata: EpubMetadata, sample_spine_item: SpineItem
) -> None:
    blocks = [ContentBlock(type="image", content="images/fig001.png")]
    write_chapter(blocks, sample_metadata, sample_spine_item, tmp_path)
    content = (tmp_path / "chapter_001.md").read_text(encoding="utf-8")
    assert "![](images/fig001.png)" in content


def test_table_output(
    tmp_path: Path, sample_metadata: EpubMetadata, sample_spine_item: SpineItem
) -> None:
    blocks = [ContentBlock(type="table", content="| A | B |")]
    write_chapter(blocks, sample_metadata, sample_spine_item, tmp_path)
    content = (tmp_path / "chapter_001.md").read_text(encoding="utf-8")
    assert "| A | B |" in content


def test_authors_in_front_matter(
    tmp_path: Path, sample_metadata: EpubMetadata, sample_spine_item: SpineItem
) -> None:
    blocks: list[ContentBlock] = []
    write_chapter(blocks, sample_metadata, sample_spine_item, tmp_path)
    content = (tmp_path / "chapter_001.md").read_text(encoding="utf-8")
    assert "- Author A" in content
```

- [ ] **Step 2: testが失敗することを確認**

```bash
uv run pytest tests/test_markdown_writer.py -v
```

期待出力: `ImportError: cannot import name 'write_chapter'`

- [ ] **Step 3: 最小実装を書く**

```python
# src/epub_content_extractor/markdown_writer.py
from pathlib import Path

from epub_content_extractor.models import ContentBlock, EpubMetadata, SpineItem


def write_chapter(
    blocks: list[ContentBlock],
    metadata: EpubMetadata,
    spine_item: SpineItem,
    output_dir: Path,
) -> Path:
    """ContentBlock列をMarkdownファイルとして output_dir に書き出す。"""
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"chapter_{spine_item.order:03d}.md"
    path = output_dir / filename

    lines: list[str] = []
    lines.append(_front_matter(metadata, spine_item))
    lines.append("")

    for block in blocks:
        lines.append(_render_block(block))
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _front_matter(metadata: EpubMetadata, spine_item: SpineItem) -> str:
    authors_yaml = "\n".join(f'  - "{a}"' for a in metadata.authors)
    publisher = f'publisher: "{metadata.publisher}"' if metadata.publisher else "publisher: null"
    identifier = (
        f'identifier: "{metadata.identifier}"' if metadata.identifier else "identifier: null"
    )
    chapter_title = (
        f'chapter_title: "{spine_item.title}"' if spine_item.title else "chapter_title: null"
    )
    return "\n".join(
        [
            "---",
            f'title: "{metadata.title}"',
            "authors:",
            authors_yaml,
            f"language: {metadata.language}",
            publisher,
            identifier,
            f"epub_layout: {metadata.layout}",
            f"page_progression_direction: {metadata.page_progression_direction}",
            chapter_title,
            f"spine_order: {spine_item.order}",
            "---",
        ]
    )


def _render_block(block: ContentBlock) -> str:
    if block.type == "heading":
        level = block.level or 1
        return "#" * level + " " + block.content
    if block.type == "paragraph":
        return block.content
    if block.type == "image":
        return f"![]({block.content})"
    if block.type == "table":
        return block.content
    return block.content
```

- [ ] **Step 4: testがpassすることを確認**

```bash
uv run pytest tests/test_markdown_writer.py -v
```

期待出力: `10 passed`

- [ ] **Step 5: commit**

```bash
git add src/epub_content_extractor/markdown_writer.py tests/test_markdown_writer.py
git commit -m "feat: implement markdown_writer (ContentBlock[] to Markdown with YAML front matter)"
```

---

### Task 7: オーケストレーション（extractor.py）

**Files:**
- Create: `src/epub_content_extractor/extractor.py`
- Create: `tests/test_extractor.py`

- [ ] **Step 1: failing testを書く（統合テスト）**

```python
# tests/test_extractor.py
from pathlib import Path

import pytest

from epub_content_extractor.extractor import extract_epub, get_epub_metadata, list_epub_spine


def test_extract_epub_creates_output_dir(reflowable_epub: Path, tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    result = extract_epub(reflowable_epub, output_dir)
    assert output_dir.is_dir()


def test_extract_epub_creates_chapter_files(reflowable_epub: Path, tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    result = extract_epub(reflowable_epub, output_dir)
    md_files = list(output_dir.glob("chapter_*.md"))
    assert len(md_files) == 2


def test_extract_epub_result_has_output_dir(reflowable_epub: Path, tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    result = extract_epub(reflowable_epub, output_dir)
    assert "output_dir" in result
    assert result["output_dir"] == str(output_dir)


def test_extract_epub_result_has_file_list(reflowable_epub: Path, tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    result = extract_epub(reflowable_epub, output_dir)
    assert "files" in result
    assert len(result["files"]) == 2


def test_extract_epub_default_output_dir(reflowable_epub: Path, tmp_path: Path) -> None:
    # OUTPUT_DIRを指定しない場合 {epub_dir}/{epub_stem}/ が使われる
    result = extract_epub(reflowable_epub, None)
    expected_dir = reflowable_epub.parent / reflowable_epub.stem
    assert result["output_dir"] == str(expected_dir)
    # クリーンアップ
    import shutil
    shutil.rmtree(expected_dir, ignore_errors=True)


def test_extract_epub_with_images(epub_with_image: Path, tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    result = extract_epub(epub_with_image, output_dir)
    images_dir = output_dir / "images"
    assert images_dir.is_dir()
    assert len(list(images_dir.glob("*"))) == 1


def test_extract_epub_image_path_in_markdown(epub_with_image: Path, tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    extract_epub(epub_with_image, output_dir)
    md_files = sorted(output_dir.glob("chapter_*.md"))
    content = md_files[0].read_text(encoding="utf-8")
    assert "![](images/fig001.png)" in content


def test_get_epub_metadata(reflowable_epub: Path) -> None:
    result = get_epub_metadata(reflowable_epub)
    assert result["title"] == "Reflowable Test Book"
    assert result["language"] == "ja"
    assert result["layout"] == "reflowable"
    assert "Test Author" in result["authors"]


def test_list_epub_spine(reflowable_epub: Path) -> None:
    result = list_epub_spine(reflowable_epub)
    assert "spine" in result
    assert len(result["spine"]) == 2
    orders = [item["order"] for item in result["spine"]]
    assert orders == [1, 2]


def test_list_epub_spine_has_title(reflowable_epub: Path) -> None:
    result = list_epub_spine(reflowable_epub)
    titles = [item["title"] for item in result["spine"]]
    assert "Chapter 1" in titles
```

- [ ] **Step 2: testが失敗することを確認**

```bash
uv run pytest tests/test_extractor.py -v
```

期待出力: `ImportError: cannot import name 'extract_epub'`

- [ ] **Step 3: 最小実装を書く**

```python
# src/epub_content_extractor/extractor.py
from pathlib import Path
from urllib.parse import urljoin

import ebooklib
from ebooklib import epub

from epub_content_extractor.content_converter import convert_html
from epub_content_extractor.epub_reader import read_epub
from epub_content_extractor.image_extractor import extract_images
from epub_content_extractor.markdown_writer import write_chapter
from epub_content_extractor.models import ContentBlock


def extract_epub(epub_path: Path, output_dir: Path | None) -> dict:
    """EPUBの全コンテンツをMarkdownファイル群として抽出する。"""
    epub_path = Path(epub_path)
    if output_dir is None:
        output_dir = epub_path.parent / epub_path.stem
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    metadata, spine_items = read_epub(epub_path)
    book = epub.read_epub(str(epub_path), {"ignore_ncx": True})

    image_mapping = extract_images(book, output_dir)

    written_files: list[str] = []
    for spine_item in spine_items:
        item = book.get_item_with_href(spine_item.href)
        if item is None or item.get_type() != ebooklib.ITEM_DOCUMENT:
            continue

        blocks = convert_html(
            item.content,
            layout=metadata.layout if metadata.layout != "ahl" else "fixed-layout",
            ppd=metadata.page_progression_direction,
            spine_href=spine_item.href,
        )

        blocks = _resolve_image_paths(blocks, spine_item.href, image_mapping, output_dir)

        md_path = write_chapter(blocks, metadata, spine_item, output_dir)
        written_files.append(str(md_path))

    return {
        "output_dir": str(output_dir),
        "files": written_files,
        "chapters": len(written_files),
    }


def _resolve_image_paths(
    blocks: list[ContentBlock],
    spine_href: str,
    image_mapping: dict[str, Path],
    output_dir: Path,
) -> list[ContentBlock]:
    resolved: list[ContentBlock] = []
    for block in blocks:
        if block.type == "image":
            epub_href = block.content
            if epub_href in image_mapping:
                rel = image_mapping[epub_href].relative_to(output_dir)
                resolved.append(ContentBlock(type="image", content=str(rel)))
            else:
                resolved.append(block)
        else:
            resolved.append(block)
    return resolved


def get_epub_metadata(epub_path: Path) -> dict:
    """EPUBのメタデータを辞書として返す（抽出は行わない）。"""
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
    """EPUBのスパインアイテム（章）を読み順で一覧する。"""
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
```

- [ ] **Step 4: testがpassすることを確認**

```bash
uv run pytest tests/test_extractor.py -v
```

期待出力: `11 passed`

- [ ] **Step 5: AHL型のスパインアイテム別レイアウト判定を追加**

`extractor.py` の `extract_epub` 内の `convert_html` 呼び出し部分を更新:

```python
# AHL型の場合、スパインアイテムごとにlayoutを判定
item_layout = _get_item_layout(book, spine_item.id, metadata.layout)

blocks = convert_html(
    item.content,
    layout=item_layout,
    ppd=metadata.page_progression_direction,
    spine_href=spine_item.href,
)
```

以下のヘルパーを `extractor.py` に追加:

```python
def _get_item_layout(
    book: epub.EpubBook, item_id: str, global_layout: str
) -> "Literal['reflowable', 'fixed-layout']":
    item = book.get_item_with_id(item_id)
    if item is None:
        return "reflowable" if global_layout == "reflowable" else "fixed-layout"  # type: ignore[return-value]
    props = getattr(item, "properties", []) or []
    if isinstance(props, str):
        props = props.split()
    if "rendition:layout-pre-paginated" in props:
        return "fixed-layout"
    if "rendition:layout-reflowable" in props:
        return "reflowable"
    return "reflowable" if global_layout in ("reflowable", "ahl") else "fixed-layout"  # type: ignore[return-value]
```

先頭の import に `Literal` を追加:

```python
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    pass
```

実際には `Literal` を直接使うよう変更:

```python
from typing import Literal
```

- [ ] **Step 6: 全テストがpassすることを確認**

```bash
uv run pytest tests/ -v
```

期待出力: 全テスト passed

- [ ] **Step 7: commit**

```bash
git add src/epub_content_extractor/extractor.py tests/test_extractor.py
git commit -m "feat: implement extractor (orchestration + AHL layout detection)"
```

---

### Task 8: CLIエントリーポイント（cli.py + __main__.py）

**Files:**
- Create: `src/epub_content_extractor/cli.py`
- Modify: `src/epub_content_extractor/__main__.py`
- Create: `tests/test_cli.py`

- [ ] **Step 1: failing testを書く**

```python
# tests/test_cli.py
from pathlib import Path

import pytest
from typer.testing import CliRunner

from epub_content_extractor.cli import app


runner = CliRunner()


def test_cli_help() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "INPUT" in result.output


def test_cli_extract_creates_output(reflowable_epub: Path, tmp_path: Path) -> None:
    output_dir = str(tmp_path / "output")
    result = runner.invoke(app, [str(reflowable_epub), output_dir])
    assert result.exit_code == 0
    assert (tmp_path / "output").is_dir()


def test_cli_extract_success_message(reflowable_epub: Path, tmp_path: Path) -> None:
    output_dir = str(tmp_path / "output")
    result = runner.invoke(app, [str(reflowable_epub), output_dir])
    assert result.exit_code == 0
    assert "chapter" in result.output.lower() or "extracted" in result.output.lower()


def test_cli_nonexistent_file(tmp_path: Path) -> None:
    result = runner.invoke(app, ["/nonexistent/path.epub"])
    assert result.exit_code != 0


def test_cli_default_output_dir(reflowable_epub: Path) -> None:
    result = runner.invoke(app, [str(reflowable_epub)])
    assert result.exit_code == 0
    expected_dir = reflowable_epub.parent / reflowable_epub.stem
    assert expected_dir.is_dir()
    import shutil
    shutil.rmtree(expected_dir, ignore_errors=True)
```

- [ ] **Step 2: testが失敗することを確認**

```bash
uv run pytest tests/test_cli.py -v
```

期待出力: `ImportError: cannot import name 'app'`

- [ ] **Step 3: cli.py を書く**

```python
# src/epub_content_extractor/cli.py
from pathlib import Path

import typer

from epub_content_extractor.extractor import extract_epub

app = typer.Typer(help="Extract text and images from EPUB files as Markdown.")


@app.command()
def main(
    input: Path = typer.Argument(..., help="Path to the EPUB file."),
    output_dir: Path | None = typer.Argument(None, help="Output directory (default: {epub_dir}/{epub_stem}/)."),
) -> None:
    """EPUBファイルからMarkdownファイル群を抽出する。"""
    if not input.exists():
        typer.echo(f"Error: File not found: {input}", err=True)
        raise typer.Exit(code=1)

    result = extract_epub(input, output_dir)
    typer.echo(f"Extracted {result['chapters']} chapter(s) to {result['output_dir']}")
    for f in result["files"]:
        typer.echo(f"  {f}")
```

- [ ] **Step 4: __main__.py を更新する**

```python
# src/epub_content_extractor/__main__.py
from epub_content_extractor.cli import app


def main() -> None:
    app()


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: testがpassすることを確認**

```bash
uv run pytest tests/test_cli.py -v
```

期待出力: `5 passed`

- [ ] **Step 6: commit**

```bash
git add src/epub_content_extractor/cli.py src/epub_content_extractor/__main__.py tests/test_cli.py
git commit -m "feat: implement CLI entry point (typer)"
```

---

### Task 9: MCPサーバ（server.py）

**Files:**
- Create: `src/epub_content_extractor/server.py`
- Create: `tests/test_server.py`
- Modify: `pyproject.toml`（エントリーポイント追加）

- [ ] **Step 1: failing testを書く**

```python
# tests/test_server.py
from pathlib import Path

import pytest

from epub_content_extractor.server import mcp


def test_server_has_extract_epub_tool() -> None:
    tool_names = [t.name for t in mcp._tool_manager.list_tools()]
    assert "extract_epub" in tool_names


def test_server_has_get_epub_metadata_tool() -> None:
    tool_names = [t.name for t in mcp._tool_manager.list_tools()]
    assert "get_epub_metadata" in tool_names


def test_server_has_list_epub_spine_tool() -> None:
    tool_names = [t.name for t in mcp._tool_manager.list_tools()]
    assert "list_epub_spine" in tool_names


def test_extract_epub_tool_result(reflowable_epub: Path, tmp_path: Path) -> None:
    from epub_content_extractor.server import _extract_epub_impl
    result = _extract_epub_impl(str(reflowable_epub), str(tmp_path / "output"))
    assert "output_dir" in result
    assert "chapters" in result


def test_get_epub_metadata_tool_result(reflowable_epub: Path) -> None:
    from epub_content_extractor.server import _get_epub_metadata_impl
    result = _get_epub_metadata_impl(str(reflowable_epub))
    assert result["title"] == "Reflowable Test Book"
    assert result["language"] == "ja"


def test_list_epub_spine_tool_result(reflowable_epub: Path) -> None:
    from epub_content_extractor.server import _list_epub_spine_impl
    result = _list_epub_spine_impl(str(reflowable_epub))
    assert "spine" in result
    assert len(result["spine"]) == 2
```

- [ ] **Step 2: testが失敗することを確認**

```bash
uv run pytest tests/test_server.py -v
```

期待出力: `ImportError: cannot import name 'mcp'`

- [ ] **Step 3: server.py を書く**

```python
# src/epub_content_extractor/server.py
from pathlib import Path

from fastmcp import FastMCP

from epub_content_extractor.extractor import (
    extract_epub as _extract_epub,
    get_epub_metadata as _get_epub_metadata,
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
    """EPUBの全コンテンツをMarkdownファイルとして抽出する。"""
    return _extract_epub_impl(source, output_dir)


@mcp.tool()
def get_epub_metadata(source: str) -> dict:
    """EPUBのメタデータを取得する（抽出は行わない）。"""
    return _get_epub_metadata_impl(source)


@mcp.tool()
def list_epub_spine(source: str) -> dict:
    """EPUBのスパインアイテム（章）を読み順で一覧する。"""
    return _list_epub_spine_impl(source)


def run() -> None:
    mcp.run()
```

- [ ] **Step 4: pyproject.toml にMCPサーバエントリーポイントを追加**

`pyproject.toml` の `[project.scripts]` セクションを以下に変更:

```toml
[project.scripts]
epub-extract = "epub_content_extractor.__main__:main"
epub-content-extractor = "epub_content_extractor.server:run"
```

- [ ] **Step 5: testがpassすることを確認**

```bash
uv run pytest tests/test_server.py -v
```

期待出力: `6 passed`

- [ ] **Step 6: 全テストがpassすることを確認**

```bash
uv run pytest tests/ -v
```

期待出力: 全テスト passed

- [ ] **Step 7: lint + type check + format**

```bash
uv run ruff check .
uv run ruff format --check .
uv run ty check
```

- [ ] **Step 8: commit**

```bash
git add src/epub_content_extractor/server.py tests/test_server.py pyproject.toml
git commit -m "feat: implement FastMCP server with extract_epub, get_epub_metadata, list_epub_spine tools"
```

---

### Task 10: __init__.py の公開APIを整理

**Files:**
- Modify: `src/epub_content_extractor/__init__.py`

- [ ] **Step 1: test_package.py が全て通ることを確認（既存テスト）**

```bash
uv run pytest tests/test_package.py -v
```

期待出力: `2 passed`

- [ ] **Step 2: __init__.py を更新して公開APIを明示**

```python
# src/epub_content_extractor/__init__.py
from epub_content_extractor.extractor import extract_epub, get_epub_metadata, list_epub_spine
from epub_content_extractor.models import ContentBlock, EpubMetadata, SpineItem

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "extract_epub",
    "get_epub_metadata",
    "list_epub_spine",
    "EpubMetadata",
    "SpineItem",
    "ContentBlock",
]
```

- [ ] **Step 3: 全テストがpassすることを確認**

```bash
uv run pytest tests/ -v
```

期待出力: 全テスト passed

- [ ] **Step 4: CI相当チェックを全て実行**

```bash
uv run ruff check .
uv run ruff format --check .
uv run ty check
uv run pytest tests/ -v
```

全て成功することを確認。

- [ ] **Step 5: commit**

```bash
git add src/epub_content_extractor/__init__.py
git commit -m "feat: export public API from __init__.py"
```

---

### Task 11: README更新

**Files:**
- Modify: `README.md`

- [ ] **Step 1: README.md を更新**

```markdown
# epub-content-extractor

EPUBファイルのテキストと画像を抽出し、Markdownファイル群として出力するCLIツール。FastMCPによるMCPサーバとしても動作します。

## インストール

```bash
pip install epub-content-extractor
# または
uvx epub-content-extractor --help
```

## CLIの使い方

```bash
epub-extract INPUT.epub [OUTPUT_DIR]
```

- `INPUT.epub`: 入力EPUBファイルのパス（必須）
- `OUTPUT_DIR`: 出力先ディレクトリ（省略時は `{epub_dir}/{epub_stem}/`）

### 出力例

```
output/
├── chapter_001.md
├── chapter_002.md
└── images/
    └── fig001.png
```

各 `.md` ファイルはYAML Front Matter付き:

```yaml
---
title: "書籍タイトル"
authors:
  - "著者名"
language: ja
publisher: "出版社"
identifier: "urn:isbn:..."
epub_layout: fixed-layout
page_progression_direction: rtl
chapter_title: "第1章"
spine_order: 1
---
```

## MCPサーバとして使う

```bash
epub-content-extractor
```

または `uvx` で直接起動:

```bash
uvx epub-content-extractor
```

### MCPツール

| ツール名 | 説明 |
|---|---|
| `extract_epub` | EPUBの全コンテンツをMarkdownとして抽出 |
| `get_epub_metadata` | EPUBのメタデータを取得（抽出なし） |
| `list_epub_spine` | スパインアイテム（章）を一覧 |

## 対応EPUBレイアウト

- **リフロー型**: HTML構造から自然な読み順でテキスト抽出
- **フィックス型**: `position: absolute` CSS座標によるソート（RTL/LTR対応）
- **AHL型**: スパインアイテムごとにフィックス型/リフロー型を判定

## 開発

```bash
uv sync --group dev
uv run pytest tests/ -v
uv run ruff check .
```
```

- [ ] **Step 2: commit**

```bash
git add README.md
git commit -m "docs: update README with CLI, MCP server usage and output format"
```

---

## セルフレビューチェックリスト

- [x] **仕様カバレッジ**: 全モジュール・全MCPツール・全レイアウト型（reflowable/fixed/AHL）・CLIをカバー
- [x] **プレースホルダーなし**: 全ステップに実際のコードあり
- [x] **型の一貫性**: `ContentBlock.level: int | None = None` はTask 1〜7で一貫
- [x] **pyproject.toml更新**: Task 9でMCPサーバエントリーポイント追加
- [x] **TDD順序**: 全タスクがRed→Green→Commit順
