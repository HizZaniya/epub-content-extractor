# リリースCI: TestPyPI検証 → 承認フェーズ → PyPI アップロード 設計書

Date: 2026-06-12

## 概要

現在の `publish.yml` は TestPyPI にアップロードするが実際にそこからのインストール検証を行わず、PyPI 公開後に初めてスモークテストが走る構成になっている。本設計では TestPyPI からのインストール検証を PyPI 公開前に追加し、さらに GitHub Environment の Required Reviewers による人間の承認ゲートを挿入する。

## 変更スコープ

対象ファイル: `.github/workflows/publish.yml`（1ファイルのみ）

GitHub Settings での追加作業: `pypi` Environment に Required Reviewers を設定

## 変更前後のフロー

### 変更前

```
build → publish-testpypi → publish-pypi → install-test（PyPIから）
```

### 変更後

```
build → publish-testpypi → verify-testpypi → [承認ゲート] → publish-pypi → install-test（PyPIから）
```

## ジョブ設計

### 追加: `verify-testpypi`

| 項目 | 内容 |
|------|------|
| `needs` | `[build, publish-testpypi]` |
| `environment` | なし（承認ゲートはここに置かない） |
| 実行内容 | TestPyPI から指定バージョンをインストールし、import と CLI の `--help` を確認 |

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

`--extra-index-url https://pypi.org/simple/` を付ける理由: epub-content-extractor の依存パッケージは TestPyPI に存在しないため、PyPI からフォールバックさせる必要がある。

### 変更: `publish-pypi`

`needs` を変更する（1行のみ）:

```yaml
# 変更前
needs: publish-testpypi

# 変更後
needs: verify-testpypi
```

`environment: pypi` は維持する。この environment に Required Reviewers が設定されていることで、`verify-testpypi` 完了後に自動で一時停止し、承認者への通知が送られる。

### 変更なし: `build`, `publish-testpypi`, `install-test`

## GitHub Settings での設定（YAML外）

Settings → Environments → `pypi` → Protection rules:

- **Required reviewers**: 承認者を追加（リポジトリオーナーまたは指定ユーザー）

この設定がない場合、`publish-pypi` ジョブは承認なしで即時実行される。

## 承認フローの動作

1. `verify-testpypi` が成功すると GitHub が承認者にメールで通知する
2. 承認者は GitHub Actions の画面から「Review deployments」で承認または拒否する
3. 承認後、`publish-pypi` が実行される
4. 拒否した場合、ワークフローはそこで停止する（PyPI には何もアップロードされない）

## テスト戦略（変更なし）

TestPyPI 検証と PyPI 最終確認の両方でスモークテストのみ実施:

- `import epub_content_extractor` が成功すること
- `epub-extract --help` が exit code 0 で終了すること

より詳細な統合テストは CI の `ci.yml` で担保する。
