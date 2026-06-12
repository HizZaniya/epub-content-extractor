# Release CI 承認ゲート実装計画

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `publish.yml` に TestPyPI 検証ジョブを追加し、PyPI 公開前に人間の承認を必須とするフローを実装する。

**Architecture:** `verify-testpypi` ジョブを `publish-testpypi` と `publish-pypi` の間に挿入する。承認ゲートは既存の `environment: pypi` に GitHub Settings で Required Reviewers を設定することで実現する。YAML の変更は `publish.yml` 1ファイルのみ。

**Tech Stack:** GitHub Actions, `pypa/gh-action-pypi-publish`, `actions/setup-python@v5`

---

### Task 1: `verify-testpypi` ジョブを `publish.yml` に追加する

**Files:**
- Modify: `.github/workflows/publish.yml`

このタスクは YAML ファイルの変更であり、Python のユニットテストは存在しない。変更後は Python の `yaml` モジュールで構文を検証する。

- [ ] **Step 1: `publish-pypi` ジョブの `needs` を変更する**

`.github/workflows/publish.yml` の `publish-pypi` ジョブを以下のように変更する:

```yaml
  publish-pypi:
    name: Publish to PyPI
    needs: verify-testpypi   # ← publish-testpypi から変更
    runs-on: ubuntu-latest
    environment: pypi
```

- [ ] **Step 2: `verify-testpypi` ジョブを `publish-testpypi` の直後に追加する**

`publish-testpypi` ジョブと `publish-pypi` ジョブの間に以下を挿入する:

```yaml
  verify-testpypi:
    name: Verify TestPyPI install
    needs: [build, publish-testpypi]
    runs-on: ubuntu-latest
    steps:
      - name: Wait for TestPyPI propagation
        run: sleep 30

      - uses: actions/setup-python@v5
        with:
          python-version: "3.13"

      - name: Install from TestPyPI
        run: |
          pip install \
            --index-url https://test.pypi.org/simple/ \
            --extra-index-url https://pypi.org/simple/ \
            "epub-content-extractor==${{ needs.build.outputs.version }}"

      - name: Test import
        run: python -c "import epub_content_extractor; print('Import OK')"

      - name: Test CLI entry point
        run: epub-extract --help
```

`needs` に `build` を含める理由: `needs.build.outputs.version` でバージョン文字列を参照するため。

- [ ] **Step 3: YAML 構文をバリデーションする**

```bash
python3 -c "
import yaml
with open('.github/workflows/publish.yml') as f:
    yaml.safe_load(f)
print('YAML syntax OK')
"
```

期待される出力:
```
YAML syntax OK
```

- [ ] **Step 4: ジョブの依存関係が正しいことを目視確認する**

変更後の `publish.yml` を読み、以下の依存チェーンが正しく成立していることを確認する:

```
build
  └─► publish-testpypi
          └─► verify-testpypi  (needs: [build, publish-testpypi])
                  └─► publish-pypi  (needs: verify-testpypi)
                          └─► install-test  (needs: [build, publish-pypi])
```

- [ ] **Step 5: コミットする**

```bash
git add .github/workflows/publish.yml
git commit -m "feat: add TestPyPI verification and approval gate before PyPI publish"
```

---

### Task 2: GitHub Settings で承認ゲートを設定する（YAML外作業）

**Files:** なし（GitHub の Web UI での設定）

このタスクは GitHub リポジトリの Settings を変更する手動作業であり、コードの変更は伴わない。

- [ ] **Step 1: `pypi` Environment に Required Reviewers を追加する**

1. `https://github.com/<owner>/epub-content-extractor/settings/environments` を開く
2. `pypi` をクリック
3. "Protection rules" セクションで "Required reviewers" を有効化
4. 承認者（リポジトリオーナーまたは指定ユーザー）を追加
5. "Save protection rules" をクリック

設定後の動作:
- `verify-testpypi` が成功すると GitHub が承認者にメールで通知する
- 承認者は GitHub Actions の該当ワークフロー画面で "Review deployments" → "Approve" をクリック
- 承認後に `publish-pypi` が実行される
- 拒否した場合はワークフローがそこで停止し、PyPI には何もアップロードされない

- [ ] **Step 2: `testpypi` Environment の設定を確認する（任意）**

`testpypi` Environment は承認不要のまま維持する。Required Reviewers を追加しないこと（TestPyPI は自動で実行されてよい）。
