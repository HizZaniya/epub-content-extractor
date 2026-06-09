---
name: epub-content-extractor-design
description: EPUBコンテンツ抽出ツールの全体設計（CLIツール + MCPサーバ）
metadata:
  type: project
---

# epub-content-extractor 設計ドキュメント

## 概要

EPUBファイルのパスを入力すると、テキストと画像を抽出してMarkdownファイル群として出力するCLIツール。
FastMCPを使ったMCPサーバとしても動作する。PyPIで公開予定。

- パッケージ名: `epub-content-extractor`
- CLIコマンド: `epub-extract`
- MCPサーバコマンド: `epub-content-extractor`

## 対応EPUBレイアウト

- リフロー型: HTMLの構造から自然な読み順でテキスト抽出
- フィックス型: 座標ベースのソートで読み順を推定。**画像を順番通りに抽出することが主目的**（外部OCR/生成AIへの橋渡し）
- AHL型（Advanced Hybrid Layout）: スパインアイテムごとにフィックス型/リフロー型を判定して処理

## アーキテクチャ

### モジュール構成

```
src/epub_content_extractor/
├── __init__.py
├── __main__.py          # CLIかMCPサーバかをサブコマンドで切り替え
├── cli.py               # typer によるCLIエントリーポイント
├── server.py            # FastMCP サーバ（MCP tools定義）
├── extractor.py         # オーケストレーション: EPUB path + output dir → ファイル群
├── epub_reader.py       # ebooklib ラッパー: OPF/スパイン/マニフェスト/メタデータ解析
├── content_converter.py # BeautifulSoup4: HTML → 構造化ブロック列（レイアウト対応）
├── markdown_writer.py   # 構造化ブロック列 → Markdown + YAML Front Matter
└── image_extractor.py   # EPUB内画像 → 出力ディレクトリへのファイル保存
```

### データの流れ

```
EPUB file
  └─ epub_reader.py      → EpubMetadata + SpineItem[]
  └─ content_converter.py → ContentBlock[] (per spine item)
  └─ image_extractor.py  → 画像ファイル保存 + パスマッピング
  └─ markdown_writer.py  → .md ファイル書き出し
       ↑ extractor.py が全体をオーケストレーション
```

`server.py` と `cli.py` はどちらも `extractor.py` の公開関数を呼ぶだけ。MCP層にEPUB解析ロジックを持たない（ndlocr-lite-mcpと同じ層分離方針）。

## 内部データ構造

```python
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
    href: str          # EPUB内の相対パス
    title: str | None  # ToC由来のタイトル
    order: int         # スパイン順の連番

@dataclass
class ContentBlock:
    type: Literal["heading", "paragraph", "image", "table"]
    content: str       # テキスト or 出力先の画像相対パス
    level: int | None  # heading の場合 1〜6
```

## 出力フォーマット

### ファイル構成

```
{output_dir}/
├── chapter_001.md
├── chapter_002.md
└── images/
    ├── chapter_001_001.png
    └── chapter_001_002.jpg
```

出力先のデフォルト: EPUBファイルと同じディレクトリに `{epub_stem}/` を作成。

### Markdown YAML Front Matter（各ファイル冒頭）

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

### 画像参照

- 画像はファイルとして保存し、Markdownから相対パスで参照
- `![](images/chapter_001_001.png)`
- Base64インライン埋め込みは行わない

## 座標ソートロジック（フィックス型・AHL型）

- `page_progression_direction: rtl`（日本語縦書き等）→ X座標の降順でカラム区切り、各カラム内はY座標昇順
- `page_progression_direction: ltr` → X座標昇順でカラム区切り、各カラム内はY座標昇順
- テキスト要素は `position: absolute` のCSS座標をBeautifulSoup4 + style属性パースで取得
- 画像要素は座標ソート後の位置に `![]()` として挿入

## CLIインターフェース

```
epub-extract INPUT [OUTPUT_DIR]
```

- `INPUT`: EPUBファイルパス（必須）
- `OUTPUT_DIR`: 出力先ディレクトリ（省略時は `{epub_dir}/{epub_stem}/`）

## MCPツール（FastMCP）

```python
@mcp.tool()
def extract_epub(source: str, output_dir: str | None = None) -> dict:
    """EPUBの全コンテンツをMarkdownファイルとして抽出する"""

@mcp.tool()
def get_epub_metadata(source: str) -> dict:
    """EPUBのメタデータを取得する（抽出は行わない）"""

@mcp.tool()
def list_epub_spine(source: str) -> dict:
    """EPUBのスパインアイテム（章）を読み順で一覧する"""
```

## 主要依存ライブラリ

```toml
dependencies = [
    "fastmcp>=3.3.1",
    "ebooklib>=0.18",
    "beautifulsoup4>=4.12",
    "lxml>=5.0",
    "typer>=0.12",
    "pillow>=11.0",
]
```

## 参考

ndlocr-lite-mcp の構成を基本とし、開発環境・CI/CD・リリースプロセスを踏襲する。
