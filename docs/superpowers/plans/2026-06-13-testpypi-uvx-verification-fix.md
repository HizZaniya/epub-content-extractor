# TestPyPI uvx 検証コマンド修正 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** README.md に TestPyPI からの `uvx` 動作確認コマンドを追加し、依存解決エラーなく実行できるようにする

**Architecture:** README の「開発」セクションの前に「TestPyPI での動作確認」セクションを追加する。コード変更なし、ドキュメント変更のみ。

**Tech Stack:** Markdown, uvx (uv)

---

### Task 1: README に TestPyPI 検証セクションを追加する

**Files:**
- Modify: `README.md`（末尾の `## 開発` セクションの直前に新セクションを挿入）

- [ ] **Step 1: 現在の README を確認する**

```bash
cat -n README.md
```

Expected: `## 開発` セクションが最終セクションとして表示される（現在74行目付近）

- [ ] **Step 2: README に TestPyPI 検証セクションを追加する**

`## 開発` の直前（73行目の空行の後）に以下を挿入する：

```markdown
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

```

- [ ] **Step 3: README の構造を確認する**

```bash
grep -n "^##" README.md
```

Expected:
```
2:## インストール
17:## CLIの使い方
53:## MCPサーバとして使う
67:## 対応EPUBレイアウト
73:## TestPyPI での動作確認
XX:## 開発
```

- [ ] **Step 4: コミットする**

```bash
git add README.md
git commit -m "docs: add TestPyPI uvx verification command to README"
```

Expected: コミット成功、pre-commit フックが全て Pass する
