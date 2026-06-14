# README リデザイン 実装計画

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** README.md をユーザ向け（MCP設定・CLI・ツールリファレンス）と開発者向けに再編し、pip 記述削除・uvx 正確な使い方・クライアント別設定・ツールリファレンスを追加する。

**Architecture:** README.md 1ファイルのみを書き換える。テストコードの変更はなし。セクション順は「必要なもの → MCP設定 → CLI → ツールリファレンス → 対応レイアウト → 開発者向け」とする。

**Tech Stack:** Markdown、git

---

## ファイルマップ

| 操作 | ファイル |
|---|---|
| Modify | `README.md` |

---

### Task 1: 前提条件セクションの書き換え

pip install を削除し、uv のみを前提条件として明示する。

**Files:**
- Modify: `README.md`（冒頭〜インストールセクション）

- [ ] **Step 1: README.md の冒頭〜インストールセクションを以下に置き換える**

  現在の `## インストール` セクション全体（pip + uvx --help の記述）を削除し、以下に差し替える：

  ```markdown
  ## 必要なもの

  - **uv** — パッケージマネージャ。[公式インストール手順](https://docs.astral.sh/uv/getting-started/installation/)に従ってインストールしてください。
  ```

- [ ] **Step 2: 変更を確認する**

  `README.md` を開き、`pip install` の記述が消えていること、`## 必要なもの` セクションが追加されていることを目視確認する。

- [ ] **Step 3: コミット**

  ```bash
  git add README.md
  git commit -m "docs: remove pip install, add uv prerequisite section"
  ```

---

### Task 2: MCPクライアント別設定セクションの追加

Claude Code・Cursor・VS Code の3クライアント分の設定方法を追加する。

**Files:**
- Modify: `README.md`（`## MCPサーバとして使う` セクションを置き換え）

- [ ] **Step 1: 既存の `## MCPサーバとして使う` セクションを以下に置き換える**

  ```markdown
  ## MCPクライアント別の設定

  ### Claude Code

  1. 以下のコマンドを実行します。

     ```bash
     claude mcp add epub-content-extractor uvx epub-content-extractor
     ```

     または `.claude/mcp.json`（プロジェクトローカル）に以下を記述します。

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

  2. Claude Code を再起動します。

  ---

  ### Cursor

  1. プロジェクトルートに `.cursor/mcp.json` を作成します（グローバル設定の場合は `~/.cursor/mcp.json`）。
  2. 以下の内容を記述します。

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

  3. Cursor を再起動します。

  ---

  ### VS Code (GitHub Copilot)

  1. プロジェクトルートに `.vscode/mcp.json` を作成します。
  2. 以下の内容を記述します。

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

  3. VS Code を再起動し、Copilot Chat から MCP ツールが利用可能になっていることを確認します。
  ```

  > **注意**: VS Code のキーは `"servers"` であり、他クライアントの `"mcpServers"` とは異なる。

- [ ] **Step 2: 変更を確認する**

  `README.md` に `### Claude Code`・`### Cursor`・`### VS Code (GitHub Copilot)` の3セクションが存在することを確認する。

- [ ] **Step 3: コミット**

  ```bash
  git add README.md
  git commit -m "docs: add per-client MCP configuration section"
  ```

---

### Task 3: CLIセクションの修正

`uvx epub-content-extractor --help` が MCP サーバー起動である旨を注記し、正しい uvx CLI 実行方法を示す。

**Files:**
- Modify: `README.md`（`## CLIの使い方` セクション）

- [ ] **Step 1: `## CLIの使い方` セクションの見出しと冒頭を以下に書き換える**

  見出しを `## CLIとして直接使う（uvx経由）` に変更し、以下の注記とコマンド例を冒頭に追加する：

  ```markdown
  ## CLIとして直接使う（uvx経由）

  > **注意**: `uvx epub-content-extractor` は MCP サーバーを起動するコマンドです。ヘルプは表示されません。
  > CLI ツールのエントリポイントは `epub-extract` です。uvx 経由では `--from` フラグを使って以下のように実行します。

  ```bash
  uvx --from epub-content-extractor epub-extract INPUT.epub [OUTPUT_DIR]
  ```

  - `INPUT.epub`: 入力EPUBファイルのパス（必須）
  - `OUTPUT_DIR`: 出力先ディレクトリ（省略時は `{epub_dir}/{epub_stem}/`）
  ```

  その後ろの `### 出力例` セクション（ディレクトリ構造・YAML Front Matter）はそのまま維持する。

- [ ] **Step 2: 変更を確認する**

  - 見出しが `## CLIとして直接使う（uvx経由）` になっていること
  - `uvx --from epub-content-extractor epub-extract` のコマンドが存在すること
  - `uvx epub-content-extractor --help` の記述が消えていること

- [ ] **Step 3: コミット**

  ```bash
  git add README.md
  git commit -m "docs: fix uvx CLI usage and add note about MCP server entry point"
  ```

---

### Task 4: ツールリファレンスセクションの追加

既存の簡易ツール表を削除し、各ツールにパラメータ表とレスポンス例を追加した詳細リファレンスに置き換える。

**Files:**
- Modify: `README.md`（`### MCPツール` の簡易表を削除し、`## ツールリファレンス` セクションを新設）

- [ ] **Step 1: 既存の `### MCPツール` 簡易表を削除し、CLIセクションの後ろに以下を追加する**

  ```markdown
  ## ツールリファレンス

  ### `extract_epub`

  EPUBの全コンテンツをMarkdownファイルとして出力します。

  #### パラメータ

  | パラメータ | 型 | デフォルト | 説明 |
  |---|---|---|---|
  | `source` | string | 必須 | EPUBファイルの絶対パスまたは相対パス |
  | `output_dir` | string | null | 出力先ディレクトリ（省略時は `{epub_dir}/{epub_stem}/`）|

  #### レスポンス

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

  ---

  ### `get_epub_metadata`

  EPUBのメタデータを取得します（ファイル出力なし）。

  #### パラメータ

  | パラメータ | 型 | デフォルト | 説明 |
  |---|---|---|---|
  | `source` | string | 必須 | EPUBファイルの絶対パスまたは相対パス |

  #### レスポンス

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

  ---

  ### `list_epub_spine`

  スパインアイテム（章）を読み順で一覧表示します（ファイル出力なし）。

  #### パラメータ

  | パラメータ | 型 | デフォルト | 説明 |
  |---|---|---|---|
  | `source` | string | 必須 | EPUBファイルの絶対パスまたは相対パス |

  #### レスポンス

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
  ```

- [ ] **Step 2: 変更を確認する**

  - `### MCPツール` の簡易表が消えていること
  - `## ツールリファレンス` 配下に `extract_epub`・`get_epub_metadata`・`list_epub_spine` の3セクションが存在すること
  - 各セクションにパラメータ表とレスポンス JSON があること

- [ ] **Step 3: コミット**

  ```bash
  git add README.md
  git commit -m "docs: add detailed tool reference with parameters and response examples"
  ```

---

### Task 5: 開発者向けセクションの整理と TestPyPI 移動

水平線で区切ったうえで `## 開発者向け` セクションを新設し、TestPyPI セクションをその中に移動する。

**Files:**
- Modify: `README.md`（`## TestPyPI での動作確認` と `## 開発` セクション）

- [ ] **Step 1: `## 対応EPUBレイアウト` の後ろに水平線と開発者向けセクションを追加し、既存の `## 開発` と `## TestPyPI での動作確認` を統合する**

  `## 対応EPUBレイアウト` の後：

  ```markdown
  ---

  ## 開発者向け

  ### 開発環境のセットアップ

  ```bash
  uv sync --group dev
  ```

  ### テスト・Lint

  ```bash
  uv run pytest tests/ -v
  uv run ruff check .
  ```

  ### TestPyPI での動作確認

  リリース前に TestPyPI へアップロードされたパッケージを `uvx` で検証する。

  TestPyPI には `lxml>=5.0` が存在しないため、`--extra-index-url` で PyPI を補助インデックスとして追加し、`--index-strategy unsafe-best-match` で全インデックスから最適バージョンを選択させる必要がある。

  ```bash
  # MCP サーバーとして起動確認
  uvx --from "epub-content-extractor" \
      --index "https://test.pypi.org/simple/" \
      --extra-index-url "https://pypi.org/simple/" \
      --index-strategy unsafe-best-match \
      epub-content-extractor

  # CLI ツールとして動作確認
  uvx --from "epub-content-extractor" \
      --index "https://test.pypi.org/simple/" \
      --extra-index-url "https://pypi.org/simple/" \
      --index-strategy unsafe-best-match \
      epub-extract <EPUBファイルパス>

  # バージョンを指定する場合
  uvx --from "epub-content-extractor==0.2.2" \
      --index "https://test.pypi.org/simple/" \
      --extra-index-url "https://pypi.org/simple/" \
      --index-strategy unsafe-best-match \
      epub-content-extractor
  ```
  ```

  その後、現行の独立した `## 開発` と `## TestPyPI での動作確認` セクションを削除する。

- [ ] **Step 2: 変更を確認する**

  - `## 対応EPUBレイアウト` の直後に `---` 水平線があること
  - `## 開発者向け` セクション配下に `### 開発環境のセットアップ`・`### テスト・Lint`・`### TestPyPI での動作確認` の3セクションが存在すること
  - `## 開発` と `## TestPyPI での動作確認` のトップレベルセクションが消えていること
  - README の末尾が `## 開発者向け` セクションで終わっていること

- [ ] **Step 3: コミット**

  ```bash
  git add README.md
  git commit -m "docs: reorganize developer section and move TestPyPI under it"
  ```

---

## セルフレビュー

### Spec カバレッジ確認

| 要件 | 対応タスク |
|---|---|
| MCP設定（Claude Code・Cursor・VS Code）の設定ファイル記述を示す | Task 2 |
| uvx 経由の CLI 直接実行方法を示す | Task 3 |
| `uvx epub-content-extractor --help` が動作しない旨を説明する | Task 3 |
| pip インストール記述を削除する | Task 1 |
| MCPツール関数のリファレンスを設ける | Task 4 |
| ユーザ向けと開発者向けのセクションを分ける | Task 5 |

### プレースホルダー確認

TBD・TODO・「同様に」などのプレースホルダーなし。各ステップに実際の Markdown コンテンツを記載済み。

### 整合性確認

- `extract_epub` のパラメータ名 `source` / `output_dir` は `server.py:31-33` と一致
- `get_epub_metadata` のレスポンスフィールドは `extractor.py:88-96` と一致
- `list_epub_spine` のレスポンス構造は `extractor.py:101-111` と一致
- VS Code の JSON キー `"servers"` はリファレンスリポジトリと一致（他クライアントは `"mcpServers"`）
