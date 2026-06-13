# verify-testpypi-cover-extraction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `publish.yml` に `verify-testpypi` ジョブを追加し、TestPyPI 公開直後にカバー画像の抽出が正しく動作することを CI で自動検証する。

**Architecture:** TestPyPI 公開後に ebooklib でカバー付き EPUB をインラインで生成し、uvx で公開済みパッケージを使って抽出を実行。`images/cover.png` の存在確認が失敗すれば PyPI 公開をブロックする。

**Tech Stack:** GitHub Actions, uv/uvx, ebooklib, Python 3.13

---

### Task 1: ローカルでEPUB生成スクリプトを検証する

CIに追加する前に、EPUB生成と抽出スクリプトがローカルで正しく動作することを確認する。

**Files:**
- 確認のみ（ファイル変更なし）

- [ ] **Step 1: EPUB生成スクリプトをローカルで実行する**

```bash
cd /workspaces/epub-content-extractor
python -c "
from ebooklib import epub
_PNG = (
    b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
    b'\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00'
    b'\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18'
    b'\xd8N\x00\x00\x00\x00IEND\xaeB\x60\x82'
)
book = epub.EpubBook()
book.set_identifier('ci-cover-test')
book.set_title('CI Cover Test')
cover = epub.EpubCover(file_name='images/cover.png')
cover.media_type = 'image/png'
cover.content = _PNG
book.add_item(cover)
epub.write_epub('/tmp/test_cover.epub', book)
print('OK: /tmp/test_cover.epub generated')
"
```

期待される出力：`OK: /tmp/test_cover.epub generated`

- [ ] **Step 2: ローカル版CLIで抽出してcover.pngを確認する**

```bash
python -m epub_content_extractor /tmp/test_cover.epub /tmp/test_cover_output/
test -f /tmp/test_cover_output/images/cover.png && echo "PASS: cover.png found" || echo "FAIL: cover.png not found"
```

期待される出力：`PASS: cover.png found`

---

### Task 2: publish.yml に verify-testpypi ジョブを追加する

**Files:**
- Modify: `.github/workflows/publish.yml`

- [ ] **Step 1: verify-testpypi ジョブを publish-testpypi の直後に追加する**

`.github/workflows/publish.yml` の `publish-testpypi` ジョブの閉じ括弧の直後（`publish-pypi` ジョブの前）に以下を挿入する：

```yaml
  verify-testpypi:
    name: Verify cover extraction (TestPyPI)
    needs: [build, publish-testpypi]
    runs-on: ubuntu-latest
    steps:
      - uses: astral-sh/setup-uv@v6
        with:
          python-version: "3.13"

      - name: Generate test EPUB with cover image
        run: |
          uv run --with ebooklib python -c "
          from ebooklib import epub
          _PNG = (
              b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
              b'\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00'
              b'\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18'
              b'\xd8N\x00\x00\x00\x00IEND\xaeB\x60\x82'
          )
          book = epub.EpubBook()
          book.set_identifier('ci-cover-test')
          book.set_title('CI Cover Test')
          cover = epub.EpubCover(file_name='images/cover.png')
          cover.media_type = 'image/png'
          cover.content = _PNG
          book.add_item(cover)
          epub.write_epub('test.epub', book)
          "

      - name: Extract with uvx (version-pinned, no cache)
        run: |
          uvx --upgrade \
            --from "epub-content-extractor==${{ needs.build.outputs.version }}" \
            --index "https://test.pypi.org/simple/" \
            --extra-index-url "https://pypi.org/simple/" \
            --index-strategy unsafe-best-match \
            epub-extract test.epub output/

      - name: Verify cover image was extracted
        run: test -f output/images/cover.png
```

- [ ] **Step 2: publish-pypi の needs を更新する**

`.github/workflows/publish.yml` の `publish-pypi` ジョブの `needs` を変更する：

変更前：
```yaml
  publish-pypi:
    name: Publish to PyPI
    needs: publish-testpypi
```

変更後：
```yaml
  publish-pypi:
    name: Publish to PyPI
    needs: [publish-testpypi, verify-testpypi]
```

- [ ] **Step 3: 変更後のファイル全体を確認する**

変更後の `.github/workflows/publish.yml` が以下の構造になっていることを確認する：

```
jobs:
  build:        needs: なし
  publish-testpypi: needs: build
  verify-testpypi:  needs: [build, publish-testpypi]   ← 新規
  publish-pypi:     needs: [publish-testpypi, verify-testpypi]  ← 更新
  install-test:     needs: [build, publish-pypi]
```

- [ ] **Step 4: 全テストを実行して既存機能への影響がないことを確認する**

```bash
python -m pytest tests/ -v
```

期待される出力：`65 passed`

- [ ] **Step 5: コミットする**

```bash
git add .github/workflows/publish.yml
git commit -m "ci: add verify-testpypi job to gate PyPI publish on cover extraction"
```
