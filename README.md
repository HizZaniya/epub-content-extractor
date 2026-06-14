# epub-content-extractor

EPUBファイルのテキストと画像を抽出し、Markdownファイル群として出力するCLIツール。FastMCPによるMCPサーバとしても動作します。

## 必要なもの

- **uv** — パッケージマネージャ。[公式インストール手順](https://docs.astral.sh/uv/getting-started/installation/)に従ってインストールしてください。

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

## 対応EPUBレイアウト

- **リフロー型**: HTML構造から自然な読み順でテキスト抽出
- **フィックス型**: `position: absolute` CSS座標によるソート（RTL/LTR対応）
- **AHL型**: スパインアイテムごとにフィックス型/リフロー型を判定

## TestPyPI での動作確認

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

## 開発

```bash
uv sync --group dev
uv run pytest tests/ -v
uv run ruff check .
```
