# epub-content-extractor

EPUBファイルのテキストと画像を抽出し、Markdownファイル群として出力するCLIツール。FastMCPによるMCPサーバとしても動作します。

## インストール

```bash
pip install epub-content-extractor
```

uvxで直接実行:

```bash
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
