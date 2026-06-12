# 欠損 v0.2.0 タグの復元 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** リポジトリに欠損している `v0.2.0` タグを作成・push し、リリースワークフローの `cz bump --yes` が正常に動作するようにする。

**Architecture:** バンプコミット `1b57f71` に `v0.2.0` タグをローカルで作成し、リモート（origin）へ push する。ワークフローファイルへの変更は不要。

**Tech Stack:** Git

---

### Task 1: v0.2.0 タグを作成して push する

**Files:**
- 変更なし（git タグ操作のみ）

- [x] **Step 1: 現在のタグ状態を確認する**

```bash
git tag -l
git ls-remote --tags origin
```

期待出力: どちらも空（タグが存在しないこと）

- [x] **Step 2: バンプコミットに v0.2.0 タグを作成する**

```bash
git tag v0.2.0 1b57f71
```

期待出力: エラーなし（出力なし）

- [x] **Step 3: ローカルにタグが作成されたことを確認する**

```bash
git tag -l
```

期待出力:
```
v0.2.0
```

- [x] **Step 4: タグをリモートへ push する**

```bash
git push origin v0.2.0
```

期待出力（例）:
```
Total 0 (delta 0), reused 0 (delta 0), pack-reused 0
To https://github.com/HizZaniya/epub-content-extractor.git
 * [new tag]         v0.2.0 -> v0.2.0
```

- [x] **Step 5: リモートにタグが反映されたことを確認する**

```bash
git ls-remote --tags origin
```

期待出力（`refs/tags/v0.2.0` が含まれること）:
```
<sha>	refs/tags/v0.2.0
```

これで実装完了。コミットは不要（タグ操作のみ）。
