---
title: TestPyPI 伝播待機をリトライループに置き換え
date: 2026-06-13
status: approved
---

## 問題

`publish.yml` の `verify-testpypi` ジョブで以下のエラーが発生する。

```
× No solution found when resolving tool dependencies:
╰─▶ Because there is no version of epub-content-extractor==0.2.4 and
    you require epub-content-extractor==0.2.4, we can conclude that your
    requirements are unsatisfiable.
```

## 根本原因

1. **TestPyPI の伝播時間が不定**: `sleep 30`（30秒固定）では不十分なことがある。
2. **`uvx --upgrade` が無効**: 新しいバージョンの uv では `--upgrade` は `uvx` に対して無効なフラグとなり、警告を出力して無視される。キャッシュバイパスの意図を果たしていない。

## 解決策

固定 `sleep 30` ステップと現行の `uvx --upgrade` コマンドを、リトライループに置き換える。

- 最大 **10回** リトライ、間隔 **30秒**（最大約5分待機）
- 成功したらすぐ次のステップへ進む
- `--upgrade` フラグを除去

## 変更後のステップ

```yaml
- name: Extract with uvx (version-pinned, retry until available)
  run: |
    VERSION="${{ needs.build.outputs.version }}"
    for i in $(seq 1 10); do
      echo "Attempt ${i}/10: installing epub-content-extractor==${VERSION} from TestPyPI..."
      if uvx \
        --from "epub-content-extractor==${VERSION}" \
        --index "https://test.pypi.org/simple/" \
        --extra-index-url "https://pypi.org/simple/" \
        --index-strategy unsafe-best-match \
        epub-extract test.epub output/; then
        echo "Success on attempt ${i}"
        exit 0
      fi
      [ ${i} -lt 10 ] && sleep 30
    done
    echo "Package not available after 10 attempts (~5 minutes)"
    exit 1
```

## 変更対象

- `.github/workflows/publish.yml`
  - `verify-testpypi` ジョブの "Wait for TestPyPI propagation" ステップを削除
  - "Extract with uvx" ステップをリトライループに置き換え

## 変更しないもの

- `publish-testpypi` ジョブの設定（`skip_existing: true` は維持）
- 他のジョブ（`build`, `publish-pypi`, `install-test`）
