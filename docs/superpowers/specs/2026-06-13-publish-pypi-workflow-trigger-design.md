# Publish to PyPI ワークフロートリガー修正

## 背景

`publish.yml` のトリガーは `release: types: [published]` のみ。`release.yml` は `GITHUB_TOKEN` で `gh release create` を実行していたが、GitHub の仕様により `GITHUB_TOKEN` が作成した release イベントは他ワークフローを発火しない。そのため `gh release create` は削除され、`publish.yml` を発火する手段がなくなった（Actions GUIに `workflow_dispatch` ボタンもない）。

## 要件

- `release.yml` 完了後に自動で `publish.yml` が発火する
- PAT（Personal Access Token）不要
- GitHub Releases ページに changelog（リリースノート）を公開する

## 設計

### アーキテクチャ

```
[Actions Tab] → workflow_dispatch
       ↓
  release.yml
  ├─ cz bump (or tag recovery)
  ├─ git push --follow-tags
  └─ gh release create --generate-notes
       ↓ workflow_run: completed
  publish.yml
  ├─ build
  ├─ publish-testpypi
  ├─ publish-pypi
  └─ install-test
```

`gh release create` は `GITHUB_TOKEN` で実行するため `release: types: [published]` を発火しない。`publish.yml` は `workflow_run` で `release.yml` の完了を検知して発火する。

### release.yml への変更

「Push commit and tag」ステップの後に「Create GitHub Release」ステップを追加する。

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

`permissions: contents: write` はすでに設定済みのため追加不要。

### publish.yml への変更

**トリガー**: `workflow_run` を追加し、`release: types: [published]` も残す。

```yaml
on:
  workflow_run:
    workflows: [Release]
    types: [completed]
  release:
    types: [published]
```

**build ジョブの条件**: `workflow_run` で失敗した場合は実行しない。

```yaml
jobs:
  build:
    if: ${{ github.event_name != 'workflow_run' || github.event.workflow_run.conclusion == 'success' }}
```

`release: types: [published]` のフォールバックは、手動で GitHub Release を作成した場合にも対応するために維持する。

## 変更ファイル

- `.github/workflows/release.yml` — `Create GitHub Release` ステップを追加
- `.github/workflows/publish.yml` — `workflow_run` トリガーを追加、`build` ジョブに `if` 条件を追加
