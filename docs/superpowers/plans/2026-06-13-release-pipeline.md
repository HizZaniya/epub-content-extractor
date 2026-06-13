# Release Pipeline 再設計 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** release.yml をバージョン管理のみに絞り、publish.yml を参照リポジトリに合わせて簡素化する。

**Architecture:** release.yml から `gh release create` ステップを削除し、バージョンバンプ+タグ push のみにする。publish.yml から `verify-testpypi` ジョブを削除し、`build → publish-testpypi → publish-pypi → install-test` のシンプルな連鎖にする。

**Tech Stack:** GitHub Actions, uv, commitizen, pypa/gh-action-pypi-publish

---

### Task 1: release.yml を修正する

**Files:**
- Modify: `.github/workflows/release.yml`

- [ ] **Step 1: `Create GitHub Release` ステップを削除する**

`.github/workflows/release.yml` を以下の内容に置き換える：

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
```

- [ ] **Step 2: YAML 構文を確認する**

```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/release.yml'))" && echo "OK"
```

期待出力: `OK`

- [ ] **Step 3: コミット**

```bash
git add .github/workflows/release.yml
git commit -m "ci: remove gh release create from release workflow"
```

---

### Task 2: publish.yml を修正する

**Files:**
- Modify: `.github/workflows/publish.yml`

- [ ] **Step 1: `verify-testpypi` ジョブを削除し、`publish-pypi` の依存を変更する**

`.github/workflows/publish.yml` を以下の内容に置き換える：

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

- [ ] **Step 2: YAML 構文を確認する**

```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/publish.yml'))" && echo "OK"
```

期待出力: `OK`

- [ ] **Step 3: コミット**

```bash
git add .github/workflows/publish.yml
git commit -m "ci: remove verify-testpypi job from publish workflow"
```
