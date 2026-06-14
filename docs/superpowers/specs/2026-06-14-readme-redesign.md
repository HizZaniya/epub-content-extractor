# README リデザイン設計

**日付**: 2026-06-14
**ステータス**: 承認済み

---

## 目的

現在の README を以下の方針で改善する：

- MCP クライアント別の設定方法（設定ファイルの書き方）を明示する
- CLI を uvx 経由で直接実行する正しい方法を示す
- pip インストール記述を削除する
- MCP ツール関数のリファレンスを設ける
- ユーザ向けと開発者向けのセクションを分ける

参考スタイル: <https://github.com/HizZaniya/ndlocr-lite-mcp>

---

## 削除する内容

- `pip install epub-content-extractor`（古い記述）
- `uvx epub-content-extractor --help`（誤解を招く記述 — 実際はMCPサーバーが起動するだけ）

---

## README 全体構成

```
# epub-content-extractor
## 必要なもの
## MCPクライアント別の設定
  ### Claude Code
  ### Cursor
  ### VS Code (GitHub Copilot)
## CLIとして直接使う（uvx経由）
## ツールリファレンス
  ### extract_epub
  ### get_epub_metadata
  ### list_epub_spine
## 対応EPUBレイアウト
---（水平線で区切り）
## 開発者向け
  ### 開発環境のセットアップ
  ### テスト・Lint
  ### TestPyPI での動作確認
```

---

## セクション詳細

### 必要なもの

- **uv** のみ。公式インストール手順へのリンクを示す。
- pip への言及はしない。

### MCPクライアント別の設定

対象クライアント: **Claude Code**・**Cursor**・**VS Code (GitHub Copilot)**

各クライアントごとに「設定ファイルの場所」→「記述する JSON」の2ステップで構成する。

#### Claude Code

`claude mcp add` コマンド方式と `.claude/mcp.json` 手書き方式の両方を示す。

```bash
claude mcp add epub-content-extractor uvx epub-content-extractor
```

または `.claude/mcp.json`（プロジェクトローカル）:

```json
{
  "mcpServers": {
    "epub-content-extractor": {
      "command": "uvx",
      "args": ["epub-content-extractor"]
    }
  }
}
```

#### Cursor

`.cursor/mcp.json`（プロジェクト）または `~/.cursor/mcp.json`（グローバル）:

```json
{
  "mcpServers": {
    "epub-content-extractor": {
      "command": "uvx",
      "args": ["epub-content-extractor"]
    }
  }
}
```

#### VS Code (GitHub Copilot)

`.vscode/mcp.json`:

```json
{
  "servers": {
    "epub-content-extractor": {
      "command": "uvx",
      "args": ["epub-content-extractor"]
    }
  }
}
```

### CLIとして直接使う（uvx経由）

**重要**: `uvx epub-content-extractor` は MCP サーバーを起動するコマンドであり、ヘルプは表示されない。
CLI ツールのエントリポイントは `epub-extract` であり、uvx 経由では `--from` フラグで指定する。

```bash
uvx --from epub-content-extractor epub-extract INPUT.epub [OUTPUT_DIR]
```

出力例（ディレクトリ構造・YAML Front Matter）は現行 README の内容を維持する。

### ツールリファレンス

#### `extract_epub`

EPUBの全コンテンツをMarkdownファイルとして出力する。

パラメータ:

| パラメータ | 型 | デフォルト | 説明 |
|---|---|---|---|
| `source` | string | 必須 | EPUBファイルの絶対パスまたは相対パス |
| `output_dir` | string | null | 出力先ディレクトリ（省略時は `{epub_dir}/{epub_stem}/`）|

レスポンス:

```json
{
  "output_dir": "/path/to/output",
  "files": [
    "/path/to/output/chapter_001.md",
    "/path/to/output/chapter_002.md"
  ],
  "chapters": 2
}
```

#### `get_epub_metadata`

EPUBのメタデータを取得する（ファイル出力なし）。

パラメータ:

| パラメータ | 型 | デフォルト | 説明 |
|---|---|---|---|
| `source` | string | 必須 | EPUBファイルの絶対パスまたは相対パス |

レスポンス:

```json
{
  "title": "書籍タイトル",
  "authors": ["著者名"],
  "language": "ja",
  "layout": "fixed-layout",
  "page_progression_direction": "rtl",
  "publisher": "出版社",
  "identifier": "urn:isbn:..."
}
```

#### `list_epub_spine`

スパインアイテム（章）を読み順で一覧表示する（ファイル出力なし）。

パラメータ:

| パラメータ | 型 | デフォルト | 説明 |
|---|---|---|---|
| `source` | string | 必須 | EPUBファイルの絶対パスまたは相対パス |

レスポンス:

```json
{
  "spine": [
    {
      "id": "chapter01",
      "href": "OEBPS/chapter01.xhtml",
      "title": "第1章",
      "order": 1
    }
  ]
}
```

### 対応EPUBレイアウト

現行 README の内容を維持する（リフロー型・フィックス型・AHL型）。

### 開発者向けセクション（水平線で区切り）

#### 開発環境のセットアップ

```bash
uv sync --group dev
```

#### テスト・Lint

```bash
uv run pytest tests/ -v
uv run ruff check .
```

#### TestPyPI での動作確認

現行 README の TestPyPI セクションの内容をそのまま移動する。

---

## 実装上の注意

- `uvx epub-content-extractor --help` が MCP サーバー起動になる旨を CLI セクションの冒頭で明記すること
- VS Code の JSON キーは `"servers"` であり、他クライアントの `"mcpServers"` と異なる点に注意
- Claude Code の `claude mcp add` コマンドが正しく動作するか実装時に確認すること
