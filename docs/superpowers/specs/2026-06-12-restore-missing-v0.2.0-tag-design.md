# 設計: 欠損 v0.2.0 タグの復元

## 背景

リリースワークフロー（`.github/workflows/release.yml`）を手動実行すると `cz bump --yes` が以下のエラーで失敗する。

```
No tag found to do an incremental changelog
Error: Process completed with exit code 16.
```

## 根本原因

PR #5 以前のリリースワークフローには `git push origin --tags` が存在しなかった。そのため v0.2.0 のバンプコミット（`1b57f71 bump: version 0.1.0 → 0.2.0`）は作成・push されたが、`v0.2.0` タグはリモートに push されなかった。

次回 `cz bump` 実行時、インクリメンタル CHANGELOG 生成のために直前タグ（`v0.2.0`）を探すが、ローカル・リモートともに存在しないため exit code 16 で終了する。

PR #5 のワークフロー修正は今後の実行を保護するが、欠損タグ自体は復元していない。

## 修正方針

### 変更対象

ワークフローファイルへの変更なし。欠損タグをリポジトリへ追加するのみ。

### 手順

1. バンプコミット `1b57f71` に `v0.2.0` タグを作成する
2. `git push origin v0.2.0` でリモートへ push する

### 事後状態

```
1b57f71  bump: version 0.1.0 → 0.2.0  ← v0.2.0 タグが付く（ローカル・リモート）
```

次回 `cz bump --yes` 実行時:
- `v0.2.0` タグが検出される
- v0.2.0 以降のコミット差分から CHANGELOG が生成される
- `v0.3.0` タグが作成され、ワークフローが `git push origin --tags` で push する

## テスト基準

- `git ls-remote --tags origin` に `refs/tags/v0.2.0` が表示される
- リリースワークフローを手動実行して exit code 0 で完了する（推奨確認）

## スコープ外

- ワークフローの追加修正（PR #5 で対応済み）
- v0.1.0 タグの有無の確認（v0.2.0 タグのみが直接の問題）
