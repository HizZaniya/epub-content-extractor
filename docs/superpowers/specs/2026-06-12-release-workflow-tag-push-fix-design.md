---
name: release-workflow-tag-push-fix
description: release.yml の --follow-tags でタグが push されないバグの修正設計
metadata:
  type: project
---

## 問題

`release.yml` の `git push origin main --follow-tags` ステップが commit を push するが、commitizen が作成した lightweight タグを push しない。`--follow-tags` は annotated タグのみ対象とするため、lightweight タグはリモートに届かない。結果として `gh release create` が "tag exists locally but has not been pushed" エラーで失敗する。

## 修正

`.github/workflows/release.yml` の "Push commit and tag" ステップを変更する。

**変更前:**
```yaml
- name: Push commit and tag
  run: git push origin main --follow-tags
```

**変更後:**
```yaml
- name: Push commit and tag
  run: |
    git push origin main
    git push origin --tags
```

commit と全タグを明示的に分けて push することで、lightweight タグも確実にリモートへ届く。

## 影響範囲

- `.github/workflows/release.yml` の1ステップのみ変更
- `publish.yml`、`ci.yml` は変更なし
- commitizen の設定変更なし
