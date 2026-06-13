# Publish to PyPI ワークフロートリガー修正 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `release.yml` 完了時に `publish.yml` が自動発火するよう `workflow_run` トリガーを追加し、`release.yml` には GitHub Release 作成ステップを復活させる。

**Architecture:** `publish.yml` に `workflow_run` トリガーを追加して `release.yml` 成功完了を検知する。`release.yml` は `gh release create` で GitHub Releases ページに changelog を公開する。PAT 不要。

**Tech Stack:** GitHub Actions YAML, `gh` CLI (`GITHUB_TOKEN` 使用)

---

## ファイルマップ

| ファイル | 変更種別 | 内容 |
|---|---|---|
| `.github/workflows/publish.yml` | 修正 | `workflow_run` トリガー追加、`build` ジョブに `if` 条件追加 |
| `.github/workflows/release.yml` | 修正 | `Create GitHub Release` ステップ追加 |

---

### Task 1: publish.yml — `workflow_run` トリガーと `if` 条件を追加

**Files:**
- Modify: `.github/workflows/publish.yml`

現在の `on:` セクション（1〜5行目）:
```yaml
on:
  release:
    types: [published]
```

変更後:
```yaml
on:
  workflow_run:
    workflows: [Release]
    types: [completed]
  release:
    types: [published]
```

現在の `build` ジョブ（11〜12行目）:
```yaml
  build:
    name: Build distribution
```

変更後:
```yaml
  build:
    name: Build distribution
    if: ${{ github.event_name != 'workflow_run' || github.event.workflow_run.conclusion == 'success' }}
```

- [ ] **Step 1: `on:` セクションを修正する**

`.github/workflows/publish.yml` の `on:` セクション（1〜5行目）を以下に置き換える:

```yaml
name: Publish to PyPI

on:
  workflow_run:
    workflows: [Release]
    types: [completed]
  release:
    types: [published]
```

- [ ] **Step 2: `build` ジョブに `if` 条件を追加する**

`.github/workflows/publish.yml` の `build:` ジョブ定義（`name: Build distribution` の次の行）に `if` 条件を追加する:

```yaml
  build:
    name: Build distribution
    if: ${{ github.event_name != 'workflow_run' || github.event.workflow_run.conclusion == 'success' }}
    runs-on: ubuntu-latest
```

- [ ] **Step 3: YAML 構文を検証する**

```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/publish.yml')); print('YAML valid')"
```

期待出力: `YAML valid`

- [ ] **Step 4: ファイル全体を目視確認する**

```bash
cat -n .github/workflows/publish.yml
```

期待する全体像:
```yaml
name: Publish to PyPI

on:
  workflow_run:
    workflows: [Release]
    types: [completed]
  release:
    types: [published]

permissions:
  contents: read

jobs:
  build:
    name: Build distribution
    if: ${{ github.event_name != 'workflow_run' || github.event.workflow_run.conclusion == 'success' }}
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.get_version.outputs.version }}
    steps:
      ...（以降は変更なし）
```

- [ ] **Step 5: コミットする**

```bash
git add .github/workflows/publish.yml
git commit -m "ci: add workflow_run trigger to publish workflow"
```

---

### Task 2: release.yml — `Create GitHub Release` ステップを追加

**Files:**
- Modify: `.github/workflows/release.yml`

現在の最後のステップ（44〜46行目）:
```yaml
      - name: Push commit and tag
        run: git push origin main --follow-tags
```

変更後（このステップの後に追加）:
```yaml
      - name: Push commit and tag
        run: git push origin main --follow-tags

      - name: Create GitHub Release
        run: |
          VERSION=$(python3 -c "
          import tomllib
          with open('pyproject.toml', 'rb') as f:
              print(tomllib.load(f)['project']['version'])
          ")
          gh release create "v${VERSION}" --title "v${VERSION}" --generate-notes
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

- [ ] **Step 1: `Create GitHub Release` ステップを追加する**

`.github/workflows/release.yml` の末尾（`git push origin main --follow-tags` の後）に以下を追加:

```yaml
      - name: Create GitHub Release
        run: |
          VERSION=$(python3 -c "
          import tomllib
          with open('pyproject.toml', 'rb') as f:
              print(tomllib.load(f)['project']['version'])
          ")
          gh release create "v${VERSION}" --title "v${VERSION}" --generate-notes
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

- [ ] **Step 2: YAML 構文を検証する**

```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/release.yml')); print('YAML valid')"
```

期待出力: `YAML valid`

- [ ] **Step 3: ファイル全体を目視確認する**

```bash
cat -n .github/workflows/release.yml
```

期待する全体像:
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

      - name: Bump version or recover missing tag
        run: |
          VERSION=$(python3 -c "
          import tomllib
          with open('pyproject.toml', 'rb') as f:
              print(tomllib.load(f)['project']['version'])
          ")
          TAG="v${VERSION}"
          if git rev-parse --verify "refs/tags/${TAG}" >/dev/null 2>&1; then
            cz bump --yes
          else
            echo "Recovery: version ${VERSION} has no tag. Creating annotated tag ${TAG}."
            git tag -a "${TAG}" -m "chore: release ${TAG}"
          fi

      - name: Push commit and tag
        run: git push origin main --follow-tags

      - name: Create GitHub Release
        run: |
          VERSION=$(python3 -c "
          import tomllib
          with open('pyproject.toml', 'rb') as f:
              print(tomllib.load(f)['project']['version'])
          ")
          gh release create "v${VERSION}" --title "v${VERSION}" --generate-notes
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

- [ ] **Step 4: コミットする**

```bash
git add .github/workflows/release.yml
git commit -m "ci: add gh release create step to release workflow"
```
