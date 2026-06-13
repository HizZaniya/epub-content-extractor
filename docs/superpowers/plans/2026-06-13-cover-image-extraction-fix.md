# cover.jpg 抽出漏れ修正 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `ITEM_COVER`（type=10）タイプの画像アイテムを `extract_images()` が抽出できるようにする。

**Architecture:** `extract_images()` のフィルタリングを `get_items_of_type(ITEM_IMAGE)` から `book.get_items()` + `media_type.startswith("image/")` チェックへ切り替える。変更ファイルは `image_extractor.py` のみ。テストはフィクスチャを `conftest.py` に追加し、`test_image_extractor.py` に2件追加する。フィクスチャは EPUB ファイルを書き出さずに `epub.EpubBook` オブジェクトを直接返すことで、ITEM_COVER タイプが write/read ラウンドトリップで失われないことを保証する。

**Tech Stack:** Python, ebooklib, pytest

---

## File Structure

| ファイル | 変更内容 |
|---|---|
| `tests/conftest.py` | `book_with_cover_item` フィクスチャを追加 |
| `tests/test_image_extractor.py` | テスト2件追加 |
| `src/epub_content_extractor/image_extractor.py` | `get_items_of_type(ITEM_IMAGE)` → media_type チェックへ変更、`import ebooklib` 削除 |

---

### Task 1: ITEM_COVER に対して失敗するテストを追加する

**Files:**
- Modify: `tests/conftest.py`
- Modify: `tests/test_image_extractor.py`

- [ ] **Step 1: `book_with_cover_item` フィクスチャを `conftest.py` に追加する**

`tests/conftest.py` の末尾（`epub_with_image` フィクスチャの後）に追加する:

```python
@pytest.fixture
def book_with_cover_item() -> epub.EpubBook:
    """ITEM_COVER タイプのアイテムを含む EpubBook を返す（ファイルI/O不要）。"""
    png_bytes = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
        b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00"
        b"\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18"
        b"\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    book = epub.EpubBook()
    book.set_identifier("test-cover-unit")
    cover = epub.EpubCover(file_name="images/cover.png")
    cover.media_type = "image/png"
    cover.content = png_bytes
    book.add_item(cover)
    return book
```

- [ ] **Step 2: 失敗するテストを `test_image_extractor.py` の末尾に追加する**

```python
def test_extract_images_includes_cover_type(
    book_with_cover_item: epub.EpubBook, tmp_path: Path
) -> None:
    output_dir = tmp_path / "output"
    extract_images(book_with_cover_item, output_dir)
    assert (output_dir / "images" / "cover.png").exists()


def test_extract_images_cover_in_mapping(
    book_with_cover_item: epub.EpubBook, tmp_path: Path
) -> None:
    output_dir = tmp_path / "output"
    mapping = extract_images(book_with_cover_item, output_dir)
    assert any("cover.png" in k for k in mapping.keys())
```

- [ ] **Step 3: テストを実行して Red を確認する**

```bash
uv run pytest tests/test_image_extractor.py::test_extract_images_includes_cover_type tests/test_image_extractor.py::test_extract_images_cover_in_mapping -v
```

Expected output（2件とも FAIL）:
```
FAILED tests/test_image_extractor.py::test_extract_images_includes_cover_type
FAILED tests/test_image_extractor.py::test_extract_images_cover_in_mapping
```

---

### Task 2: `extract_images` を media_type ベースに修正して Green にする

**Files:**
- Modify: `src/epub_content_extractor/image_extractor.py`

- [ ] **Step 1: `image_extractor.py` を以下の内容に置き換える**

```python
from pathlib import Path

from ebooklib import epub


def extract_images(book: epub.EpubBook, output_dir: Path) -> dict[str, Path]:
    mapping: dict[str, Path] = {}
    images_dir = output_dir / "images"

    for item in book.get_items():
        if not (item.media_type and item.media_type.startswith("image/")):
            continue
        images_dir.mkdir(parents=True, exist_ok=True)
        filename = Path(item.file_name).name
        dest = images_dir / filename
        dest.write_bytes(item.content)
        mapping[item.file_name] = dest

    return mapping
```

変更点:
- `import ebooklib` を削除（`ITEM_IMAGE` 定数が不要になった）
- `book.get_items_of_type(ebooklib.ITEM_IMAGE)` → `book.get_items()` + `media_type` チェック
- docstring を削除（WHAT は関数名と型アノテーションで自明）

- [ ] **Step 2: 新テストが Green になることを確認する**

```bash
uv run pytest tests/test_image_extractor.py -v
```

Expected output（7件すべて PASS）:
```
PASSED tests/test_image_extractor.py::test_extract_images_creates_directory
PASSED tests/test_image_extractor.py::test_extract_images_saves_file
PASSED tests/test_image_extractor.py::test_extract_images_returns_mapping
PASSED tests/test_image_extractor.py::test_extract_images_filename
PASSED tests/test_image_extractor.py::test_no_images_returns_empty
PASSED tests/test_image_extractor.py::test_extract_images_includes_cover_type
PASSED tests/test_image_extractor.py::test_extract_images_cover_in_mapping
```

- [ ] **Step 3: テストスイート全体が Green であることを確認する**

```bash
uv run pytest -v
```

Expected: all tests PASSED、既存テストに影響がないこと

- [ ] **Step 4: コミットする**

```bash
git add tests/conftest.py tests/test_image_extractor.py src/epub_content_extractor/image_extractor.py
git commit -m "fix: extract cover images by media_type instead of ITEM_IMAGE type"
```
