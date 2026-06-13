# リリースワークフロー タグ欠損リカバリ設計

## 背景

`annotated_tag = true` が追加される前（PR#7 以前）のリリース実行において、`cz bump --yes` が軽量タグ（lightweight tag）を作成していた。`git push origin main --follow-tags` は注釈付きタグ（annotated tag）しかプッシュしないため、`v0.2.1` タグがリモートに存在しない状態（タグ欠損状態）になった。

この状態では `cz bump --yes` が以下の理由で失敗する：

- `pyproject.toml` のバージョン = `0.2.1`
- 最新タグ = `v0.2.0`
- `v0.2.0` 以降のコミットは `ci:` / `docs:` のみで、バンプ対象コミットなし
- `cz bump` の算出バージョン（`0.2.1`）= 現在バージョン → `NO_COMMITS_TO_BUMP`（終了コード 21）

PR#7 で `annotated_tag = true` が追加されたため**今後の再発はない**が、現在の状態を修正する必要がある。

## 目標

- `release.yml` を修正し、タグ欠損状態でもリリースを完遂できるようにする
- `pyproject.toml` のバージョンに対応するタグが存在しない場合は注釈付きタグを作成する
- 正常状態では `cz bump --yes` の挙動を変更しない

## 設計

### 変更ファイル

`.github/workflows/release.yml` のみ変更する。

### ロジック

```
pyproject.toml からバージョン読み取り
  → タグ v$VERSION が存在するか確認
      ├─ 存在しない（タグ欠損状態）
      │    → git tag -a v$VERSION -m "chore: release v$VERSION"
      └─ 存在する（正常状態）
           → cz bump --yes
```

その後の `git push origin main --follow-tags` は両ケースで共通。

### 変更後のステップ

```yaml
- name: Bump version or recover missing tag
  run: |
    VERSION=$(python3 -c "import tomllib; d=tomllib.load(open('pyproject.toml','rb')); print(d['project']['version'])")
    TAG="v${VERSION}"
    if git rev-parse "${TAG}" >/dev/null 2>&1; then
      cz bump --yes
    else
      echo "Recovery: version ${VERSION} has no tag. Creating annotated tag ${TAG}."
      git tag -a "${TAG}" -m "chore: release ${TAG}"
    fi
```

### エラーハンドリング

| ケース | 挙動 |
|---|---|
| タグなし・タグ欠損状態 | 注釈付きタグを作成 → プッシュへ |
| タグあり・通常状態 | `cz bump --yes` を実行 |
| `cz bump` が 21 以外で失敗 | そのまま exit（CI 失敗） |
| タグあり・バンプ対象コミットなし | `cz bump` が 21 で失敗 → CI 失敗（正常な失敗） |

## テスト戦略

- ローカルで `git rev-parse v0.2.1` が失敗することを確認（タグ欠損状態の再現）
- bash スクリプト部分を手動実行し、注釈付きタグが作成されることを確認（`git tag -v v0.2.1`）
- タグ作成後に `git push --follow-tags` でプッシュされることを確認
