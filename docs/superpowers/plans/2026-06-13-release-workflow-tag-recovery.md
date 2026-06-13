# Release Workflow Tag Recovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `release.yml` の Bump ステップを修正し、`pyproject.toml` のバージョンに対応するタグが存在しない場合（タグ欠損状態）でもリリースを完遂できるようにする。

**Architecture:** `cz bump --yes` の前に現在バージョンのタグ存在を確認する。タグが存在しない場合は注釈付きタグを作成してバンプをスキップ。タグが存在する場合は通常通り `cz bump --yes` を実行する。

**Tech Stack:** GitHub Actions, bash, commitizen, git

---

### Task 1: ローカルでタグ欠損状態を確認する

**Files:**
- 確認のみ（変更なし）

- [ ] **Step 1: 現在のタグ状態を確認する**

```bash
git tag --list
git rev-parse v0.2.1 2>&1 || echo "v0.2.1 tag does not exist"
```

期待出力:
```
v0.2.0
fatal: ambiguous argument 'v0.2.1': unknown revision ...
v0.2.1 tag does not exist
```

- [ ] **Step 2: pyproject.toml のバージョンを確認する**

```bash
python3 -c "import tomllib; d=tomllib.load(open('pyproject.toml','rb')); print(d['project']['version'])"
```

期待出力:
```
0.2.1
```

これで「バージョン 0.2.1 のタグが存在しない」状態が確認できる。

---

### Task 2: ローカルでリカバリスクリプトを手動検証する

**Files:**
- 確認のみ（変更なし）

- [ ] **Step 1: リカバリロジックをドライランで確認する**

以下のコマンドをローカルで実行し、タグが正しく作成されることを確認する（`git push` はしない）：

```bash
VERSION=$(python3 -c "import tomllib; d=tomllib.load(open('pyproject.toml','rb')); print(d['project']['version'])")
TAG="v${VERSION}"
echo "VERSION=${VERSION}, TAG=${TAG}"
if git rev-parse "${TAG}" >/dev/null 2>&1; then
  echo "Tag ${TAG} exists -> would run: cz bump --yes"
else
  echo "Recovery: version ${VERSION} has no tag. Creating annotated tag ${TAG}."
  git tag -a "${TAG}" -m "chore: release ${TAG}"
fi
```

期待出力:
```
VERSION=0.2.1, TAG=v0.2.1
Recovery: version 0.2.1 has no tag. Creating annotated tag v0.2.1.
```

- [ ] **Step 2: 注釈付きタグが作成されたことを確認する**

```bash
git tag -v v0.2.1
```

期待出力（抜粋）：
```
object ...
type commit
tag v0.2.1
tagger ...
chore: release v0.2.1
```

- [ ] **Step 3: 検証後にローカルタグを削除する（CI での動作確認のため残さない）**

```bash
git tag -d v0.2.1
```

期待出力:
```
Deleted tag 'v0.2.1' (was ...)
```

---

### Task 3: `release.yml` を修正する

**Files:**
- Modify: `.github/workflows/release.yml`

- [ ] **Step 1: 現在のステップを確認する**

`.github/workflows/release.yml` の `Bump version and generate CHANGELOG` ステップ（30〜31行目）を確認する：

```yaml
      - name: Bump version and generate CHANGELOG
        run: cz bump --yes
```

- [ ] **Step 2: ステップを置き換える**

上記のステップを以下に置き換える：

```yaml
      - name: Bump version or recover missing tag
        run: |
          VERSION=$(python3 -c "import tomllib; d=tomllib.load(open('pyproject.toml','rb')); print(d['project']['version'])")
          TAG="v${VERSION}"
          if git rev-parse "${TAG}" >/dev/null 2>&1; then
            cz bump --yes
          else
            echo "Recovery: version ${VERSION} has no tag. Creating annotated tag ${TAG}."
            git tag -a "${TAG}" -m "chore: release ${TAG}"
          fi
```

変更後の `release.yml` 全体：

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
          VERSION=$(python3 -c "import tomllib; d=tomllib.load(open('pyproject.toml','rb')); print(d['project']['version'])")
          TAG="v${VERSION}"
          if git rev-parse "${TAG}" >/dev/null 2>&1; then
            cz bump --yes
          else
            echo "Recovery: version ${VERSION} has no tag. Creating annotated tag ${TAG}."
            git tag -a "${TAG}" -m "chore: release ${TAG}"
          fi

      - name: Push commit and tag
        run: git push origin main --follow-tags
```

- [ ] **Step 3: YAML の構文を確認する**

```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/release.yml'))" && echo "YAML valid"
```

期待出力:
```
YAML valid
```

- [ ] **Step 4: コミットする**

```bash
git add .github/workflows/release.yml
git commit -m "fix: handle missing tag in release workflow"
```
