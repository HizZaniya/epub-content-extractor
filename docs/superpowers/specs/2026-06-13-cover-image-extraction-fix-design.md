# Design: cover.jpg 抽出漏れ修正

Date: 2026-06-13

## 問題

`epub/` ディレクトリでの CLI 動作確認において、`cover.jpg` が `images/` ディレクトリに抽出されないことが判明した。

### 根本原因

ebooklib は EPUB の cover 画像を `ITEM_COVER`（type=10）として扱う。現在の `extract_images()` は `get_items_of_type(ebooklib.ITEM_IMAGE)`（type=1）のみを走査するため、`ITEM_COVER` アイテムが漏れる。

**確認事項:**
- `cover.jpg` のアイテムタイプ: `ITEM_COVER`（type=10）
- `chapter_001.md` には `![](image/cover.jpg)` の参照は正しく生成されている
- `images/cover.jpg` ファイルが存在しないため、マークダウンの画像参照がリンク切れになっている

## 設計方針

アイテムタイプによるフィルタリングをメディアタイプベースに切り替える。

### 変更ファイル

`src/epub_content_extractor/image_extractor.py` のみ。

### 変更内容

**Before:**
```python
for item in book.get_items_of_type(ebooklib.ITEM_IMAGE):
```

**After:**
```python
for item in book.get_items():
    if not (item.media_type and item.media_type.startswith("image/")):
        continue
```

`ebooklib` のアイテム型定数（`ITEM_IMAGE`, `ITEM_COVER` 等）に依存せず、MIME 標準の `image/*` で判定することで、現在・将来の全画像アイテムを確実に取得する。

### エッジケース

| ケース | 対応 |
|---|---|
| `media_type` が `None` のアイテム | `and` 短絡評価でスキップ |
| 異なるパスに同名ファイル | 既存の `Path(item.file_name).name` フラット化を維持（現行動と同じ） |
| SVG 等の非 JPEG/PNG 画像 | `image/` プレフィックス一致で自動対応 |

## テスト戦略（TDD）

### 新規フィクスチャ（`tests/conftest.py`）

`epub_with_cover`: `epub.EpubCover` を使って `ITEM_COVER` の画像を含む EPUB を生成する。

### 新規テスト（`tests/test_image_extractor.py`）

- `test_extract_images_includes_cover_type`: `ITEM_COVER` アイテムが `images/` に保存されること
- `test_extract_images_cover_in_mapping`: `image_mapping` に cover 画像のキーが含まれること

### 既存テストへの影響

なし。`epub_with_image` フィクスチャは変更しない。

## 完了条件

1. `images/cover.jpg` が抽出されること
2. 新規テスト2件が Green であること
3. 既存テスト全件が Green であること
