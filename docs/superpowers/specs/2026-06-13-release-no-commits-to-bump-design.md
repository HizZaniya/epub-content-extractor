---
title: Release Workflow — NOTHING_TO_BUMP グレースフルスキップ
date: 2026-06-13
status: approved
---

## 問題

Release ワークフローを手動トリガー (`workflow_dispatch`) した際、直前の `v0.2.2` タグ以降のコミットがすべて `docs:` / `ci:` / マージコミットのみの場合、`cz bump --yes` が exit code 21 (`NOTHING_TO_BUMP`) で終了する。`bash -e` がこれをエラーとして扱いジョブが失敗する。

## 根本原因

- `v0.2.2` タグはリモートに存在する
- タグ以降のコミット: `docs:` 2件、`ci:` 3件、マージコミット 1件 — いずれもバンプ対象外
- `cz bump --yes` → exit code 21 → `bash -e` がスクリプトを中断

## 設計方針

バンプ対象コミットが存在しない場合は、明確なメッセージを出力してジョブを**成功扱いでスキップ**する（push も GitHub Release 作成もしない）。

## 変更内容

対象ファイル: `.github/workflows/release.yml`

### 1. ステップに `id: bump` を追加

後続ステップが `steps.bump.outputs.skipped` を参照できるようにする。

### 2. `cz bump --yes` の exit code ハンドリング

```bash
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
```

recovery ブランチ（タグ未存在時）では `skipped=false` を書き出す。

### 3. 後続ステップに `if:` 条件を追加

```yaml
- name: Push commit and tag
  if: steps.bump.outputs.skipped != 'true'

- name: Create GitHub Release
  if: steps.bump.outputs.skipped != 'true'
```

## 動作フロー

| 状況 | `cz bump` exit code | 結果 |
|------|-------------------|------|
| バンプ対象コミットあり | 0 | 通常通りバンプ → push → release |
| バンプ対象コミットなし | 21 | メッセージ出力 → 後続スキップ → 成功終了 |
| その他エラー | 1〜20, 22〜 | 従来通りジョブ失敗 |
| タグ未存在（recovery） | — | タグ作成 → push → release |

## テスト観点

- `cz bump --yes` が exit 21 を返す状況でジョブが success になること
- push ステップ・GitHub Release ステップが実行されないこと
- `cz bump --yes` が exit 0 を返す場合は従来通りすべてのステップが実行されること
- その他の exit code（例: 1）ではジョブが失敗すること
