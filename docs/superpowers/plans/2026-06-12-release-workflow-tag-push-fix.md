# Release Workflow Tag Push Fix 実装計画

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `release.yml` の push ステップを修正し、lightweight タグがリモートに確実に push されるようにする。

**Architecture:** `git push origin main --follow-tags` は annotated タグのみを push するため、commitizen が作成する lightweight タグが push されない。コマンドを2行に分けて commit と全タグを個別に push することで解決する。

**Tech Stack:** GitHub Actions YAML

---

### Task 1: release.yml の push コマンドを修正する

**Files:**
- Modify: `.github/workflows/release.yml:34`

- [ ] **Step 1: 現在の内容を確認する**

```bash
grep -n "push" .github/workflows/release.yml
```

Expected output:
```
34:      - name: Push commit and tag
35:        run: git push origin main --follow-tags
```

- [ ] **Step 2: push コマンドを修正する**

`.github/workflows/release.yml` の "Push commit and tag" ステップを以下に変更する:

```yaml
      - name: Push commit and tag
        run: |
          git push origin main
          git push origin --tags
```

- [ ] **Step 3: YAML の文法を確認する**

```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/release.yml'))" && echo "YAML OK"
```

Expected output:
```
YAML OK
```

- [ ] **Step 4: 変更内容を確認する**

```bash
git diff .github/workflows/release.yml
```

Expected output（抜粋）:
```diff
-        run: git push origin main --follow-tags
+        run: |
+          git push origin main
+          git push origin --tags
```

- [ ] **Step 5: コミットする**

```bash
git add .github/workflows/release.yml
git commit -m "fix: push tags explicitly to fix release workflow"
```
