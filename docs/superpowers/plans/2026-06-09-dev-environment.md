# epub-content-extractor 開発環境構築 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** epub-content-extractor プロジェクトの開発環境を一式構築する（アプリケーションコードは含まない）

**Architecture:** ndlocr-lite-mcp の構成を踏襲し、hatchling + uv + mise + FastMCP + ruff + ty + commitizen + pre-commit + GitHub Actions の組み合わせで構成する。Dev Container 内で完結する開発体験を提供し、Claude Code のプラグインも自動インストールされる。

**Tech Stack:** Python 3.13, uv, mise, hatchling, FastMCP, ruff, ty, commitizen, pytest, pre-commit, Docker (Debian bookworm-slim), GitHub Actions

---

## ファイルマップ

| ファイル | 役割 |
|---------|------|
| `pyproject.toml` | パッケージ設定・依存関係・ツール設定一元管理 |
| `pyrightconfig.json` | Pyright LSP 設定（IDE補完用） |
| `.mise.toml` | Python/Node バージョン管理 |
| `src/epub_content_extractor/__init__.py` | パッケージ宣言（空） |
| `src/epub_content_extractor/__main__.py` | エントリーポイントスタブ |
| `tests/__init__.py` | テストパッケージ宣言（空） |
| `tests/test_package.py` | パッケージインポート確認テスト |
| `.pre-commit-config.yaml` | pre-commit フック設定 |
| `.gitignore` | Git 除外設定 |
| `.devcontainer/Dockerfile` | 開発コンテナイメージ定義 |
| `.devcontainer/devcontainer.json` | VS Code Dev Container 設定 |
| `.claude/settings.json` | Claude Code プロジェクト設定 |
| `.claude/rules/development.md` | 開発原則（TDD/YAGNI/SOLID/DRY） |
| `.claude/scripts/check-pr-template.sh` | PRテンプレート検証 PostToolUse フック |
| `.claude/statusline.sh` | Claude Code ステータスライン表示スクリプト |
| `.github/pull_request_template.md` | PR テンプレート |
| `.github/LABELS.yml` | GitHub ラベル定義 |
| `.github/FUNDING.yml` | Ko-fi スポンサー設定 |
| `.github/workflows/ci.yml` | CI（lint / format / type-check / test） |
| `.github/workflows/pr-template-check.yml` | PR テンプレート必須セクション検証 |
| `.github/workflows/publish.yml` | TestPyPI → PyPI publish |
| `.github/workflows/release.yml` | commitizen バージョンバンプ + GitHub Release |
| `LICENSE` | MIT ライセンス |
| `CHANGELOG.md` | 変更履歴（雛形） |
| `.mcp.json.example` | MCP サーバ設定例 |

---

## Task 1: pyproject.toml・パッケージスタブ・テストスタブを作成する

**Files:**
- Create: `pyproject.toml`
- Create: `pyrightconfig.json`
- Create: `src/epub_content_extractor/__init__.py`
- Create: `src/epub_content_extractor/__main__.py`
- Create: `tests/__init__.py`
- Create: `tests/test_package.py`

- [ ] **Step 1: 失敗するテストを書く**

`tests/test_package.py` を作成する（この時点では `src/` が存在しないので `ImportError` で失敗するはず）:

```python
from epub_content_extractor import __version__


def test_package_importable() -> None:
    assert __version__ is not None


def test_version_is_string() -> None:
    assert isinstance(__version__, str)
```

- [ ] **Step 2: テストが失敗することを確認する**

```bash
uv run pytest tests/test_package.py -v
```

期待される出力: `ModuleNotFoundError: No module named 'epub_content_extractor'`

- [ ] **Step 3: pyproject.toml を作成する**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "epub-content-extractor"
version = "0.1.0"
description = "Extract text and images from EPUB files and reconstruct as Markdown"
readme = "README.md"
requires-python = ">=3.13"
license = { file = "LICENSE" }
authors = [
    { name = "HizZaniya" },
]
keywords = ["epub", "markdown", "mcp", "extraction", "ebook"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.13",
    "Topic :: Text Processing :: Markup",
    "Topic :: Utilities",
]
dependencies = [
    "fastmcp>=3.3.1",
    "ebooklib>=0.18",
    "beautifulsoup4>=4.12",
    "lxml>=5.0",
    "typer>=0.12",
    "pillow>=11.0",
]

[project.urls]
Homepage = "https://github.com/HizZaniya/epub-content-extractor"
Repository = "https://github.com/HizZaniya/epub-content-extractor"
"Bug Tracker" = "https://github.com/HizZaniya/epub-content-extractor/issues"

[project.scripts]
epub-extract = "epub_content_extractor.__main__:main"

[tool.hatch.build.targets.wheel]
packages = ["src/epub_content_extractor"]

[tool.ruff]
target-version = "py313"
line-length = 100

[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "UP", "RUF"]
ignore = ["B008"]

[tool.ruff.lint.isort]
known-first-party = ["epub_content_extractor"]

[tool.ruff.format]
quote-style = "double"

[tool.pyright]
include = ["src", "tests"]
extraPaths = ["src"]
venvPath = "."
venv = ".venv"

[tool.ty.environment]
python-version = "3.13"

[tool.commitizen]
name = "cz_conventional_commits"
tag_format = "v$version"
version_scheme = "pep440"
version_provider = "pep621"
update_changelog_on_bump = true

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"

[dependency-groups]
dev = [
    "commitizen>=4.0",
    "pytest>=8.0",
    "pytest-asyncio>=0.24.0",
    "pytest-mock>=3.14",
    "pre-commit>=4.0",
    "ty>=0.0.38",
    "ruff>=0.15.14",
]
```

- [ ] **Step 4: pyrightconfig.json を作成する**

```json
{
  "include": ["src", "tests"],
  "extraPaths": ["src"],
  "venvPath": ".",
  "venv": ".venv"
}
```

- [ ] **Step 5: パッケージスタブを作成する**

`src/epub_content_extractor/__init__.py`:

```python
__version__ = "0.1.0"
```

`src/epub_content_extractor/__main__.py`:

```python
def main() -> None:
    raise NotImplementedError


if __name__ == "__main__":
    main()
```

`tests/__init__.py`: 空ファイルを作成（0バイト）。

- [ ] **Step 6: 依存関係をインストールする**

```bash
uv sync --dev
```

期待される出力: `uv.lock` が生成され、全依存ライブラリがインストールされる。

- [ ] **Step 7: テストが通ることを確認する**

```bash
uv run pytest tests/test_package.py -v
```

期待される出力:
```
tests/test_package.py::test_package_importable PASSED
tests/test_package.py::test_version_is_string PASSED
```

- [ ] **Step 8: ruff・ty が通ることを確認する**

```bash
uv run ruff check . && uv run ruff format --check . && uv run ty check
```

期待される出力: エラーなし（全て通過）。

- [ ] **Step 9: コミットする**

```bash
git add pyproject.toml pyrightconfig.json src/ tests/ uv.lock
git commit -m "chore: パッケージ雛形・依存関係・ツール設定を追加"
```

---

## Task 2: miseによる環境管理を設定する

**Files:**
- Create: `.mise.toml`

- [ ] **Step 1: .mise.toml を作成する**

```toml
[tools]
python = "3.13"
node = "22"
```

- [ ] **Step 2: mise が認識することを確認する**

```bash
mise ls
```

期待される出力: python 3.13 と node 22 が一覧に表示される。

- [ ] **Step 3: コミットする**

```bash
git add .mise.toml
git commit -m "chore: miseによるPython/Nodeバージョン管理を追加"
```

---

## Task 3: pre-commit を設定する

**Files:**
- Create: `.pre-commit-config.yaml`

- [ ] **Step 1: .pre-commit-config.yaml を作成する**

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.15.14
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: local
    hooks:
      - id: ty
        name: ty type check
        entry: uv run ty check
        language: system
        types: [python]
        pass_filenames: false

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-toml
```

- [ ] **Step 2: pre-commit フックをインストールする**

```bash
uv run pre-commit install
```

期待される出力: `pre-commit installed at .git/hooks/pre-commit`

- [ ] **Step 3: 全ファイルに対して実行して問題がないことを確認する**

```bash
uv run pre-commit run --all-files
```

期待される出力: 全フック PASSED（または Skipped）。

- [ ] **Step 4: コミットする**

```bash
git add .pre-commit-config.yaml
git commit -m "chore: pre-commitフック設定を追加"
```

---

## Task 4: .gitignore を作成する

**Files:**
- Create: `.gitignore`

- [ ] **Step 1: .gitignore を作成する**

```gitignore
# Claude Code
.claude/settings.local.json

# Serena
.serena/

# Python
__pycache__/
*.py[cod]
*.pyo
.venv/
*.egg-info/
dist/
build/

# Tools cache
.ruff_cache/
.pytest_cache/
.mypy_cache/

# Environment
.env
.env.*
!.env.example
```

- [ ] **Step 2: コミットする**

```bash
git add .gitignore
git commit -m "chore: .gitignoreを追加"
```

---

## Task 5: 開発コンテナを設定する

**Files:**
- Create: `.devcontainer/Dockerfile`
- Create: `.devcontainer/devcontainer.json`

- [ ] **Step 1: Dockerfile を作成する**

```dockerfile
FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl git ca-certificates gnupg jq shellcheck \
    libjpeg-dev libpng-dev libxml2-dev libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

# GitHub CLI (gh)
RUN install -d -m 0755 /etc/apt/keyrings \
    && curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
       -o /etc/apt/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
       > /etc/apt/sources.list.d/github-cli.list \
    && apt-get update && apt-get install -y --no-install-recommends gh \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --gid 1000 vscode \
    && useradd --uid 1000 --gid 1000 --create-home --shell /bin/bash vscode
USER vscode

# mise (Python + Node.js version management)
ENV PATH="/home/vscode/.local/share/mise/shims:/home/vscode/.local/bin:$PATH"
RUN curl https://mise.run | sh && mise use --global python@3.13 node@22

# uv (Python package manager)
RUN curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=/home/vscode/.local/bin sh

# bash-language-server (consumed by the claude-code-lsps bash plugin)
RUN npm install -g bash-language-server pyright

# Claude Code (native install, stable channel)
RUN curl -fsSL https://claude.ai/install.sh | bash -s stable
```

libjpeg-dev / libpng-dev は Pillow のビルド依存、libxml2-dev / libxslt1-dev は lxml のビルド依存。

- [ ] **Step 2: devcontainer.json を作成する**

```json
{
    "name": "epub-content-extractor",
    "build": {
        "dockerfile": "Dockerfile",
        "context": ".."
    },
    "customizations": {
        "vscode": {
            "extensions": [
                "astral-sh.ty",
                "charliermarsh.ruff",
                "ms-python.python",
                "tamasfe.even-better-toml",
                "anthropic.claude-code"
            ],
            "settings": {
                "python.defaultInterpreterPath": "${containerWorkspaceFolder}/.venv/bin/python",
                "python.analysis.typeCheckingMode": "off",
                "ty.enable": true,
                "editor.formatOnSave": true,
                "editor.defaultFormatter": "charliermarsh.ruff",
                "[python]": {
                    "editor.defaultFormatter": "charliermarsh.ruff",
                    "editor.codeActionsOnSave": {
                        "source.organizeImports": "explicit"
                    }
                },
                "ruff.nativeServer": "on"
            }
        }
    },
    "postCreateCommand": "mise trust && mise install && uv sync --dev && uv tool install ty && uv run pre-commit install",
    "remoteUser": "vscode"
}
```

- [ ] **Step 3: コミットする**

```bash
git add .devcontainer/
git commit -m "chore: 開発コンテナ設定を追加"
```

---

## Task 6: Claude Code 設定を追加する

**Files:**
- Create: `.claude/settings.json`
- Create: `.claude/rules/development.md`
- Create: `.claude/scripts/check-pr-template.sh`
- Create: `.claude/statusline.sh`

- [ ] **Step 1: .claude/settings.json を作成する**

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "language": "japanese",
  "model": "claude-sonnet-4-6",
  "attribution": {
    "commit": "",
    "pr": ""
  },
  "enabledMcpjsonServers": [
    "plugin_serena_serena"
  ],
  "statusLine": {
    "type": "command",
    "command": ".claude/statusline.sh"
  },
  "enabledPlugins": {
    "superpowers@claude-plugins-official": true,
    "pyright-lsp@claude-plugins-official": true,
    "context7@claude-plugins-official": true,
    "bash-language-server@claude-code-lsps": true,
    "criticalthink@criticalthink": true
  },
  "extraKnownMarketplaces": {
    "claude-code-lsps": {
      "source": {
        "source": "github",
        "repo": "boostvolt/claude-code-lsps"
      }
    },
    "criticalthink": {
      "source": {
        "source": "github",
        "repo": "abagames/slash-criticalthink"
      }
    }
  },
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/scripts/check-pr-template.sh"
          }
        ]
      }
    ]
  }
}
```

- [ ] **Step 2: .claude/rules/development.md を作成する**

```markdown
# 開発原則

このプロジェクトではt-wada式TDD・YAGNI・SOLID・DRYの原則を厳密に守ります。

## TDD（t-wada 式）

- **Red → Green → Refactor** の順を必ず守る
- コードより先にテストを書く
- テストが通る最小限の実装のみ書く（Greenフェーズ）
- リファクタは全テストがGreenの状態でのみ行う
- テストなしでコード変更を行わない

## YAGNI（You Aren't Gonna Need It）

- 現在の要件に明示されていない機能は実装しない
- 将来の拡張を見越した抽象化・インタフェース追加は行わない
- 不要なオプション引数・設定値・フラグは作らない
- 「あると便利かもしれない」という理由だけでコードを書かない

## SOLID

- **S (Single Responsibility)**: 各モジュールは1つの責務のみ持つ
  - `server.py` = MCP プロトコル層のみ
  - `extractor.py` = EPUB抽出オーケストレーション層のみ
- **O (Open/Closed)**: 変更にはテストを書いてから着手する
- **I (Interface Segregation)**: インタフェースはクライアントが必要とするメソッドのみ定義する
- **D (Dependency Inversion)**: 上位レイヤーは下位レイヤーの具体型に依存しない

## DRY（Don't Repeat Yourself）

- 重複するロジックは共通ヘルパーに集約する
- テストの共通セットアップは conftest.py フィクスチャに集約する
- エラー変換パターンは1か所に集める
- コピペコードを避ける

## コメント

- デフォルトはコメント不要
- WHYが非自明な場合のみコメントを書く
- 「何をしているか」は良い命名で表現する
```

- [ ] **Step 3: .claude/scripts/check-pr-template.sh を作成する**

```bash
#!/usr/bin/env bash
# PostToolUse hook: gh pr create 後にPRテンプレート必須セクションを検証する

set -euo pipefail

input=$(cat)

# Bash ツールの gh pr create コマンドか確認
command=$(echo "$input" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('tool_input', {}).get('command', ''))
except Exception:
    print('')
" 2>/dev/null || true)

if ! echo "$command" | grep -qE 'gh pr create'; then
    exit 0
fi

# ツール出力から PR URL を抽出
output=$(echo "$input" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    resp = d.get('tool_response', '')
    if isinstance(resp, str):
        print(resp)
    elif isinstance(resp, dict):
        print(resp.get('output', '') or resp.get('stdout', ''))
    else:
        print('')
except Exception:
    print('')
" 2>/dev/null || true)

pr_url=$(echo "$output" | grep -oE 'https://github\.com/[^[:space:]]+/pull/[0-9]+' | head -1 || true)

if [ -z "$pr_url" ]; then
    exit 0
fi

# PR 本文を取得
body=$(gh pr view "$pr_url" --json body --jq '.body' 2>/dev/null || echo "")

if [ -z "$body" ]; then
    exit 0
fi

# 必須セクションチェック
required_sections=(
    "## 概要"
    "## ラベル"
    "## 完了条件"
    "## パフォーマンス影響"
    "## レビュアーへの案内"
)

missing=()
for section in "${required_sections[@]}"; do
    if ! echo "$body" | grep -qF "$section"; then
        missing+=("$section")
    fi
done

# ラベルのチェックボックス確認（- [x] が1つ以上）
if ! echo "$body" | grep -qE '\- \[x\]'; then
    missing+=("ラベルのチェック（## ラベル セクションで - [x] を1つ選択）")
fi

if [ ${#missing[@]} -gt 0 ]; then
    echo "⚠️  PRテンプレート検証失敗: 以下が不足または未入力です"
    for m in "${missing[@]}"; do
        echo "  • $m"
    done
    echo ""
    echo "以下のコマンドでPR本文を修正してください:"
    echo "  gh pr edit $pr_url"
fi

exit 0
```

作成後に実行権限を付与する:

```bash
chmod +x .claude/scripts/check-pr-template.sh
```

- [ ] **Step 4: .claude/statusline.sh を作成する**

```bash
#!/usr/bin/env bash
set -u

input=$(cat)
MODEL=$(printf '%s' "$input" | jq -r '.model.display_name // "unknown"')
PCT=$(printf '%s' "$input" | jq -r '.context_window.used_percentage // 0' | cut -d. -f1)

if BRANCH=$(git branch --show-current 2>/dev/null) && [ -n "$BRANCH" ]; then
    echo "${MODEL} | ${PCT}% | ${BRANCH}"
else
    echo "${MODEL} | ${PCT}%"
fi
```

作成後に実行権限を付与する:

```bash
chmod +x .claude/statusline.sh
```

- [ ] **Step 5: コミットする**

```bash
git add .claude/settings.json .claude/rules/ .claude/scripts/ .claude/statusline.sh
git commit -m "chore: Claude Code設定・開発ルール・フックスクリプトを追加"
```

---

## Task 7: GitHub設定ファイルを追加する

**Files:**
- Create: `.github/pull_request_template.md`
- Create: `.github/LABELS.yml`
- Create: `.github/FUNDING.yml`

- [ ] **Step 1: .github/pull_request_template.md を作成する**

```markdown
<!-- PRタイトルの形式：type(scope): 命令形の説明（日本語可）

  例：
    feat(extractor): EPUBリフロー型テキスト抽出を実装
    fix(content-converter): 座標ソートの降順ロジックを修正
    refactor(markdown-writer): YAML Front Matter生成を共通化
    chore: ebooklib を最新版にアップデート
    ci: pytest CIジョブを追加
-->

## 概要

<!-- 必須。2〜4文で「何を・なぜ」変更するか記述すること。
     ユーザー（CLIまたはMCPクライアント）への影響またはエンジニアリング上の理由に焦点を当てる。
     関連Issueがある場合はリンクを記載：「Closes #123」または「Ref #456」 -->

## ラベル

<!-- 必ず1つだけチェックし、GitHub UI（右サイドバー > Labels）でも同じラベルを付与すること。
     ラベルは `gh release create --generate-notes` のカテゴリ分類に使われる。 -->

- [ ] `breaking-change` — CLIの引数・戻り値・動作など、利用者対応が必要な変更（0.y.zフェーズではMINORバンプ）
- [ ] `feature`         — 新しいCLIオプションまたはMCPツールの追加
- [ ] `enhancement`     — 既存機能の改善
- [ ] `bug`             — ユーザー影響のあるリグレッション
- [ ] `fix`             — リグレッションでない不具合修正
- [ ] `mcp`             — FastMCP サーバ層の変更（`server.py`）
- [ ] `extractor`       — EPUB抽出コア層の変更（`extractor.py` 等）
- [ ] `devcontainer`    — Dev Container / Dockerfile の変更
- [ ] `performance`     — 計測可能な速度・メモリ改善（ベンチマーク結果必須）
- [ ] `docs`            — ドキュメントのみ（README、インラインコメント、ガイド）
- [ ] `ci`              — GitHub Actionsワークフローの変更
- [ ] `build`           — pyproject.toml・uv・ツールチェーンの設定変更
- [ ] `dependencies`    — 依存関係のバージョン更新
- [ ] `skip-changelog`  — リリースノートから意図的に除外するもの

## 完了条件（Definition of Done）

> **マージ前に全項目をチェックすること。未チェック項目があるPRはマージ不可。**
> 適用外の項目は理由をコメントで明記した上でチェックすること。

### CI/CD（自動チェック）

- [ ] `test` ジョブがグリーン（`uv run pytest tests/ -v`）
- [ ] `lint` ジョブがグリーン（`uv run ruff check .`）
- [ ] `format` ジョブがグリーン（`uv run ruff format --check .`）
- [ ] `type-check` ジョブがグリーン（`uv run ty check`）

### コード品質（手動確認）

- [ ] `uv run ruff check .` がローカルで警告ゼロで通過する
- [ ] `uv run ruff format --check .` がローカルで通過する
- [ ] `uv run ty check` がローカルでエラーゼロで通過する
- [ ] デバッグ用 `print()` がプロダクションコードに残っていない
- [ ] ハードコードされたAPIキー・パスワードが含まれていない

### テスト（手動確認）

- [ ] TDDサイクル（Red → Green → Refactor）を完了した
- [ ] 新規プロダクションロジックに対応するテストが書かれている
- [ ] `uv run pytest tests/ -v` が全件グリーン

### アーキテクチャ（レイヤー分離）

- [ ] `server.py` にEPUB解析ロジックがない（`extractor.py` 経由のみ）
- [ ] `extractor.py` に FastMCP／MCP プロトコルの依存がない
- [ ] 新規MCPツールのエラーは `ToolError` として上位へ伝播している

## テスト証跡

<!-- CI設定・ドキュメントのみの変更はこのセクションを削除すること -->

### 追加・変更したテスト

| テストファイル | 追加・変更したテストケース名 |
|--------------|--------------------------|
| <!-- 例: tests/test_extractor.py --> | <!-- 例: test_extract_epub_returns_markdown_files --> |

### 手動確認手順

<!-- ローカルで実施したハッピーパスと異常系を記載する。手順が自明な場合は省略可 -->

1.
2.

## セキュリティチェック

<!-- 新規MCPツールを追加した場合のみ記入すること。
     既存ツールの修正・ドキュメント変更ではセクションごと削除すること。 -->

- [ ] ユーザー入力がバリデーションされている（Pydantic型 + ロジックレベル）
- [ ] ファイルパスのディレクトリトラバーサル対策がある（`../` 等の不正パスを拒否）
- [ ] エラーレスポンスに機密情報が含まれていない（絶対パス等）

## パフォーマンス影響

- [ ] パフォーマンスへの影響を確認した

**影響の有無と理由：**
<!-- `performance` ラベル：ベンチマーク結果（before / after）を以下に貼り付けること -->
<!-- その他のラベル：「影響なし。〇〇のみの変更のため」と一行で記載 -->

## 破壊的変更

<!-- `breaking-change` ラベルの場合のみ記入すること。
     それ以外のPRではセクションごと削除すること。
     0.y.z開発フェーズでは、破壊的変更はMAJORではなくMINORをバンプする。 -->

### 変更前後の動作

**変更前：** <!-- 旧動作を説明 -->

**変更後：** <!-- 新動作を説明 -->

### 移行手順

<!-- CLIユーザーや `.mcp.json` の設定変更が必要な場合、手順を記載する。 -->

### バージョンバンプ確認

- [ ] `pyproject.toml` の `version` を同一コミットで更新済み
- [ ] MINORバージョンをバンプした（0.y.zフェーズでの破壊的変更）

## レビュアーへの案内

### 重点的にレビューしてほしい部分

<!-- どこを特に見てほしいか、その理由とともに記載する -->

-

### テストが難しかった部分・未テストの部分

<!-- テストを書かなかった・書けなかった部分とその理由を明記する。なければ「なし」と記載 -->

-

### 設計上の判断とトレードオフ

<!-- 他の実装アプローチを検討した場合、なぜこの設計を選んだかを説明する。自明な場合は「なし」と記載 -->

-
```

- [ ] **Step 2: .github/LABELS.yml を作成する**

```yaml
breaking-change:
  color: "D93F0B"
  description: "CLI/MCP tool signature or behavior change requiring user action"

feature:
  color: "0075CA"
  description: "New CLI option or MCP tool"

enhancement:
  color: "A2EEEF"
  description: "Improvement to existing feature or behavior"

bug:
  color: "D73A4A"
  description: "Regression: something that used to work now doesn't"

fix:
  color: "E4E669"
  description: "Non-regression defect fix"

mcp:
  color: "BFD4F2"
  description: "FastMCP server layer changes (server.py)"

extractor:
  color: "C5DEF5"
  description: "EPUB extraction core layer changes"

devcontainer:
  color: "F9D0C4"
  description: "Dev Container / Dockerfile changes"

performance:
  color: "1D76DB"
  description: "Measurable speed or memory improvement (benchmarks required)"

docs:
  color: "0075CA"
  description: "Documentation only (README, comments, guides)"

ci:
  color: "FBCA04"
  description: "GitHub Actions workflow changes"

build:
  color: "FBCA04"
  description: "pyproject.toml, uv, or toolchain configuration"

dependencies:
  color: "0366D6"
  description: "Dependency version bumps"

skip-changelog:
  color: "EEEEEE"
  description: "Intentionally excluded from release notes"
```

- [ ] **Step 3: .github/FUNDING.yml を作成する**

```yaml
ko_fi: hizzaniya
```

- [ ] **Step 4: コミットする**

```bash
git add .github/pull_request_template.md .github/LABELS.yml .github/FUNDING.yml
git commit -m "chore: GitHub PRテンプレート・ラベル・スポンサー設定を追加"
```

---

## Task 8: GitHub Actions CI ワークフローを追加する

**Files:**
- Create: `.github/workflows/ci.yml`
- Create: `.github/workflows/pr-template-check.yml`

- [ ] **Step 1: .github/workflows/ci.yml を作成する**

```yaml
name: CI

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

jobs:
  lint:
    name: Lint (ruff check)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: astral-sh/setup-uv@v6
        with:
          python-version: "3.13"
          enable-cache: true
          cache-dependency-glob: "uv.lock"

      - run: uv sync --frozen --group dev

      - run: uv run ruff check .

  format:
    name: Format (ruff format --check)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: astral-sh/setup-uv@v6
        with:
          python-version: "3.13"
          enable-cache: true
          cache-dependency-glob: "uv.lock"

      - run: uv sync --frozen --group dev

      - run: uv run ruff format --check .

  type-check:
    name: Type Check (ty)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: astral-sh/setup-uv@v6
        with:
          python-version: "3.13"
          enable-cache: true
          cache-dependency-glob: "uv.lock"

      - run: uv sync --frozen --group dev

      - run: uv run ty check

  test:
    name: Test (pytest)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: astral-sh/setup-uv@v6
        with:
          python-version: "3.13"
          enable-cache: true
          cache-dependency-glob: "uv.lock"

      - run: uv sync --frozen --group dev

      - run: uv run pytest tests/ -v
```

- [ ] **Step 2: .github/workflows/pr-template-check.yml を作成する**

```yaml
name: PR Template Check

on:
  pull_request:
    types: [opened, edited, reopened, synchronize]
    branches: [main]

jobs:
  validate-template:
    name: PR Template Validation
    runs-on: ubuntu-latest
    steps:
      - name: Validate required sections and label
        uses: actions/github-script@v7
        with:
          script: |
            const body = context.payload.pull_request.body ?? '';

            const required = [
              '## 概要',
              '## ラベル',
              '## 完了条件',
              '## パフォーマンス影響',
              '## レビュアーへの案内',
            ];

            const missing = required.filter(s => !body.includes(s));
            const hasLabel = /- \[x\]/i.test(body);

            const errors = [];
            if (missing.length > 0) {
              errors.push(`必須セクションが不足しています:\n${missing.map(s => `  • ${s}`).join('\n')}`);
            }
            if (!hasLabel) {
              errors.push('ラベルが未選択です（## ラベル セクションで `- [x]` を1つチェックしてください）');
            }

            if (errors.length > 0) {
              core.setFailed(errors.join('\n\n'));
            }
```

- [ ] **Step 3: コミットする**

```bash
git add .github/workflows/ci.yml .github/workflows/pr-template-check.yml
git commit -m "ci: lint/format/type-check/test CIジョブおよびPRテンプレート検証を追加"
```

---

## Task 9: GitHub Actions publish/release ワークフローを追加する

**Files:**
- Create: `.github/workflows/publish.yml`
- Create: `.github/workflows/release.yml`

- [ ] **Step 1: .github/workflows/publish.yml を作成する**

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

permissions:
  contents: read

jobs:
  build:
    name: Build distribution
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.get_version.outputs.version }}
    steps:
      - uses: actions/checkout@v4

      - uses: astral-sh/setup-uv@v6
        with:
          python-version: "3.13"

      - run: uv build

      - name: Get version
        id: get_version
        run: |
          VERSION=$(grep '^version' pyproject.toml | head -1 | sed 's/.*"\(.*\)"/\1/')
          echo "version=${VERSION}" >> $GITHUB_OUTPUT

      - uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/

  publish-testpypi:
    name: Publish to TestPyPI
    needs: build
    runs-on: ubuntu-latest
    environment: testpypi
    permissions:
      id-token: write
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: dist
          path: dist/

      - uses: pypa/gh-action-pypi-publish@release/v1
        with:
          repository-url: https://test.pypi.org/legacy/

  publish-pypi:
    name: Publish to PyPI
    needs: publish-testpypi
    runs-on: ubuntu-latest
    environment: pypi
    permissions:
      id-token: write
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: dist
          path: dist/

      - uses: pypa/gh-action-pypi-publish@release/v1

  install-test:
    name: Install test from PyPI
    needs: [build, publish-pypi]
    runs-on: ubuntu-latest
    steps:
      - name: Wait for PyPI propagation
        run: sleep 60

      - uses: actions/setup-python@v5
        with:
          python-version: "3.13"

      - name: Install from PyPI
        run: pip install "epub-content-extractor==${{ needs.build.outputs.version }}"

      - name: Test import
        run: python -c "import epub_content_extractor; print('Import OK')"

      - name: Test CLI entry point
        run: epub-extract --help
```

- [ ] **Step 2: .github/workflows/release.yml を作成する**

```yaml
name: Release

on:
  workflow_dispatch:

permissions:
  contents: write

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: astral-sh/setup-uv@v6
        with:
          python-version: "3.13"
          enable-cache: true

      - name: Install commitizen
        run: uv tool install commitizen

      - name: Configure git
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"

      - name: Bump version and generate CHANGELOG
        run: cz bump --yes

      - name: Push commit and tag
        run: git push origin main --follow-tags

      - name: Create GitHub Release
        run: |
          VERSION=$(grep '^version' pyproject.toml | head -1 | sed 's/.*"\(.*\)"/\1/')
          gh release create "v${VERSION}" --title "v${VERSION}" --generate-notes
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

- [ ] **Step 3: コミットする**

```bash
git add .github/workflows/publish.yml .github/workflows/release.yml
git commit -m "ci: PyPI publishおよびreleaseワークフローを追加"
```

---

## Task 10: LICENSE・CHANGELOG・.mcp.json.example を追加する

**Files:**
- Create: `LICENSE`
- Create: `CHANGELOG.md`
- Create: `.mcp.json.example`

- [ ] **Step 1: LICENSE を作成する**

```
MIT License

Copyright (c) 2026 HizZaniya

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

- [ ] **Step 2: CHANGELOG.md を作成する**

```markdown
# Changelog
```

- [ ] **Step 3: .mcp.json.example を作成する**

```json
{
    "mcpServers": {
        "epub-content-extractor": {
            "command": "uvx",
            "args": [
                "--from",
                "/path/to/epub-content-extractor",
                "epub-extract"
            ]
        }
    }
}
```

- [ ] **Step 4: コミットする**

```bash
git add LICENSE CHANGELOG.md .mcp.json.example
git commit -m "chore: MITライセンス・CHANGELOG雛形・MCP設定例を追加"
```

---

## Task 11: 最終確認

- [ ] **Step 1: 全テストが通ることを確認する**

```bash
uv run pytest tests/ -v
```

期待される出力:
```
tests/test_package.py::test_package_importable PASSED
tests/test_package.py::test_version_is_string PASSED
```

- [ ] **Step 2: lint・format・type-check が全て通ることを確認する**

```bash
uv run ruff check . && uv run ruff format --check . && uv run ty check
```

期待される出力: エラー・警告なし。

- [ ] **Step 3: pre-commit が全ファイルで通ることを確認する**

```bash
uv run pre-commit run --all-files
```

期待される出力: 全フック PASSED（または Skipped）。

- [ ] **Step 4: ディレクトリ構造を確認する**

```bash
find . -not -path './.git/*' -not -path './.venv/*' -not -path './.ruff_cache/*' -not -path './.pytest_cache/*' | sort
```

以下のファイルが全て存在すること:
- `pyproject.toml`, `pyrightconfig.json`, `uv.lock`
- `.mise.toml`
- `.pre-commit-config.yaml`
- `.gitignore`
- `src/epub_content_extractor/__init__.py`
- `src/epub_content_extractor/__main__.py`
- `tests/__init__.py`, `tests/test_package.py`
- `.devcontainer/Dockerfile`, `.devcontainer/devcontainer.json`
- `.claude/settings.json`, `.claude/rules/development.md`
- `.claude/scripts/check-pr-template.sh`, `.claude/statusline.sh`
- `.github/pull_request_template.md`, `.github/LABELS.yml`, `.github/FUNDING.yml`
- `.github/workflows/ci.yml`, `.github/workflows/pr-template-check.yml`
- `.github/workflows/publish.yml`, `.github/workflows/release.yml`
- `LICENSE`, `CHANGELOG.md`, `.mcp.json.example`
