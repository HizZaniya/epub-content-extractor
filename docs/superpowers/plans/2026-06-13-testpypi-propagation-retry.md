# TestPyPI Propagation Retry Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `publish.yml` の `verify-testpypi` ジョブで固定 `sleep 30` とブロークンな `uvx --upgrade` を、リトライループに置き換えて信頼性を高める。

**Architecture:** `.github/workflows/publish.yml` の `verify-testpypi` ジョブのみを変更する。"Wait for TestPyPI propagation" ステップを削除し、"Extract with uvx" ステップを最大10回・30秒間隔のリトライループに置き換える。他のジョブは一切変更しない。

**Tech Stack:** GitHub Actions YAML、uv/uvx

---

### Task 1: publish.yml を修正する

**Files:**
- Modify: `.github/workflows/publish.yml:89-99`

- [ ] **Step 1: "Wait for TestPyPI propagation" ステップを削除する**

`.github/workflows/publish.yml` の以下の行を削除する（`verify-testpypi` ジョブ内、行89-90付近）:

```yaml
      - name: Wait for TestPyPI propagation
        run: sleep 30
```

- [ ] **Step 2: "Extract with uvx" ステップをリトライループに置き換える**

削除前:

```yaml
      - name: Extract with uvx (version-pinned, no cache)
        run: |
          uvx --upgrade \
            --from "epub-content-extractor==${{ needs.build.outputs.version }}" \
            --index "https://test.pypi.org/simple/" \
            --extra-index-url "https://pypi.org/simple/" \
            --index-strategy unsafe-best-match \
            epub-extract test.epub output/
```

置き換え後:

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

- [ ] **Step 3: YAML の構造を確認する**

`verify-testpypi` ジョブ全体が正しいインデントになっていることを確認する:

```bash
grep -n "" .github/workflows/publish.yml | head -110
```

期待値: `verify-testpypi` ジョブ内のステップが正しくインデントされている

- [ ] **Step 4: YAML の文法を検証する**

```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/publish.yml'))" && echo "YAML valid"
```

期待値: `YAML valid` と表示される

- [ ] **Step 5: コミットする**

```bash
git add .github/workflows/publish.yml
git commit -m "fix: replace fixed sleep with retry loop in verify-testpypi job"
```
