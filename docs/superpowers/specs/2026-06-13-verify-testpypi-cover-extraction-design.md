# TestPyPI カバー画像抽出機能テスト追加 設計書

**日付**: 2026-06-13
**対象**: `.github/workflows/publish.yml`

---

## 背景・問題

- v0.2.2 は `ITEM_COVER` 型カバー画像を抽出できないバグを含んだまま TestPyPI に公開された
- PR #12 でコード修正後に v0.2.3 を公開したが、`uvx` コマンドが `--upgrade` なしだったためキャッシュされた v0.2.2 を使い続け、修正が効いていないように見えた
- 現在の `install-test` ジョブは import と `--help` しか確認しておらず、実際の抽出動作を検証していない

---

## 目的

TestPyPI への公開直後に「カバー画像が正しく抽出できること」を CI で自動検証し、壊れたバージョンが PyPI に昇格しないよう gate として機能させる。

---

## アーキテクチャ

### 変更前

```
build → publish-testpypi → publish-pypi → install-test
```

### 変更後

```
build → publish-testpypi → verify-testpypi → publish-pypi → install-test
```

`verify-testpypi` が失敗すると `publish-pypi` はブロックされる。

---

## 実装詳細

### 新規ジョブ: `verify-testpypi`

| 項目 | 値 |
|---|---|
| `needs` | `[build, publish-testpypi]` |
| `runs-on` | `ubuntu-latest` |

**ステップ**:

1. **`astral-sh/setup-uv@v6`** — Python 3.13 をセットアップ
2. **Generate test EPUB** — `uv run --with ebooklib` でインライン Python スクリプトを実行し、`EpubCover` アイテムを持つ最小 EPUB (`test.epub`) を生成
   - バイナリファイルをリポジトリに含めない
   - 著作権問題なし（プログラム生成）
   - PNG は `conftest.py` の `_MINIMAL_PNG` と同一の 1×1 ピクセル最小 PNG
3. **Extract with uvx** — `--upgrade` + バージョン固定 (`epub-content-extractor==$version`) + TestPyPI インデックスで epub-extract を実行
   - `--upgrade` によりキャッシュを無視して必ず公開済みバージョンを取得
4. **Verify** — `test -f output/images/cover.png` でカバー画像の存在を確認

### `publish-pypi` の `needs` 変更

```yaml
# 変更前
needs: publish-testpypi

# 変更後
needs: [publish-testpypi, verify-testpypi]
```

---

## 成功・失敗基準

| 状態 | 結果 |
|---|---|
| `output/images/cover.png` が存在する | ✅ ジョブ成功 → `publish-pypi` 実行 |
| `output/images/cover.png` が存在しない | ❌ ジョブ失敗 → `publish-pypi` ブロック |
| uvx インストール失敗 | ❌ ジョブ失敗 → `publish-pypi` ブロック |

---

## スコープ外

- README への `--upgrade` 追加（アプローチ A）は今回は行わない
- PyPI 向けの同等検証は既存 `install-test` ジョブに委ねる
