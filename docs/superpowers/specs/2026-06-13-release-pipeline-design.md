# Release Pipeline 再設計

## 背景

既存の `release.yml` は `gh release create` を `GITHUB_TOKEN` で実行していたが、GitHub Actions の仕様により GITHUB_TOKEN が作成した release イベントは他ワークフローを発火しない。そのため `publish.yml` が連鎖起動しなかった。

参照リポジトリ（ndlocr-lite-mcp）の調査で、Release ワークフローは一度も成功しておらず、PyPI リリースは GitHub UI での手動操作で達成されていた。

## 要件

- 全自動は不要
- 参照リポジトリと同等の運用フローを実現する
- Release ワークフローはバージョン管理のみを担う

## 設計

### 運用フロー

```
1. Actions タブ → Release → Run workflow（workflow_dispatch）
2. GitHub の Releases ページでリリースを作成・Publish（手動）
3. Publish to PyPI ワークフローが自動発火
```

### release.yml

**役割**: バージョンバンプとタグ push のみ。

ステップ構成:
1. checkout（fetch-depth: 0）
2. setup-uv（Python 3.13）
3. commitizen インストール
4. git config（github-actions[bot]）
5. `cz bump --yes`
6. `git push origin main --follow-tags`

`gh release create` は含めない。

### publish.yml

**役割**: GitHub Release が published になったら PyPI へ公開する。

トリガー: `on: release: types: [published]`

ジョブ構成:
```
build → publish-testpypi → publish-pypi → install-test
```

参照リポジトリに合わせて `verify-testpypi`（TestPyPI からのインストール確認）ジョブを削除する。

## 変更ファイル

- `.github/workflows/release.yml` — `Create GitHub Release` ステップを削除
- `.github/workflows/publish.yml` — `verify-testpypi` ジョブを削除、`publish-pypi` の `needs` を `publish-testpypi` に変更
