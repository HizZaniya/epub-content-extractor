# Release Workflow NOTHING_TO_BUMP グレースフルスキップ 実装プラン

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `cz bump --yes` が exit code 21 (NOTHING_TO_BUMP) を返した場合に Release ワークフローを成功扱いでスキップする

**Architecture:** `.github/workflows/release.yml` の `Bump version or recover missing tag` ステップに exit code ハンドリングを追加し、後続ステップに `if:` 条件を付与する。shell の `set +e` / `set -e` で `cz bump` の exit code を取得し、`$GITHUB_OUTPUT` 経由で後続ステップへ伝達する。

**Tech Stack:** GitHub Actions YAML, bash

---

### Task 1: `Bump version or recover missing tag` ステップを修正

**Files:**
- Modify: `.github/workflows/release.yml`

現在のステップ（`id` なし）を読んでから変更する。

- [ ] **Step 1: 現在のワークフローファイルを確認**

```bash
cat .github/workflows/release.yml
```

Expected: ステップに `id:` がなく、`cz bump --yes` が素の呼び出しになっていることを確認する。

- [ ] **Step 2: `Bump version or recover missing tag` ステップに `id` と exit code ハンドリングを追加**

`.github/workflows/release.yml` の `Bump version or recover missing tag` ステップを以下に置き換える:

```yaml
      - name: Bump version or recover missing tag
        id: bump
        run: |
          VERSION=$(python3 -c "
          import tomllib
          with open('pyproject.toml', 'rb') as f:
              print(tomllib.load(f)['project']['version'])
          ")
          TAG="v${VERSION}"
          if git rev-parse --verify "refs/tags/${TAG}" >/dev/null 2>&1; then
            set +e
            cz bump --yes
            CZ_EXIT=$?
            set -e
            if [ $CZ_EXIT -eq 21 ]; then
              echo "No eligible commits since ${TAG}. Skipping release."
              echo "skipped=true" >> $GITHUB_OUTPUT
              exit 0
            elif [ $CZ_EXIT -ne 0 ]; then
              exit $CZ_EXIT
            fi
            echo "skipped=false" >> $GITHUB_OUTPUT
          else
            echo "Recovery: version ${VERSION} has no tag. Creating annotated tag ${TAG}."
            git tag -a "${TAG}" -m "chore: release ${TAG}"
            echo "skipped=false" >> $GITHUB_OUTPUT
          fi
```

- [ ] **Step 3: `Push commit and tag` ステップに `if:` 条件を追加**

```yaml
      - name: Push commit and tag
        if: steps.bump.outputs.skipped != 'true'
        run: git push origin main --follow-tags
```

- [ ] **Step 4: `Create GitHub Release` ステップに `if:` 条件を追加**

```yaml
      - name: Create GitHub Release
        if: steps.bump.outputs.skipped != 'true'
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

- [ ] **Step 5: YAML 構文を検証**

```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/release.yml'))" && echo "YAML OK"
```

Expected:
```
YAML OK
```

- [ ] **Step 6: ワークフロー全体を目視確認**

```bash
cat .github/workflows/release.yml
```

確認ポイント:
- `Bump version or recover missing tag` ステップに `id: bump` がある
- `set +e` / `set -e` で `cz bump --yes` を囲んでいる
- exit code 21 で `skipped=true` を出力し `exit 0` している
- exit code が 21 以外の非ゼロでは `exit $CZ_EXIT` している
- 通常バンプ成功時と recovery 時に `skipped=false` を出力している
- `Push commit and tag` ステップに `if: steps.bump.outputs.skipped != 'true'` がある
- `Create GitHub Release` ステップに `if: steps.bump.outputs.skipped != 'true'` がある

- [ ] **Step 7: コミット**

```bash
git add .github/workflows/release.yml
git commit -m "ci: skip release gracefully when no commits to bump"
```

Expected:
```
[fix/release-no-commits-to-bump ...] ci: skip release gracefully when no commits to bump
 1 file changed, ...
```
