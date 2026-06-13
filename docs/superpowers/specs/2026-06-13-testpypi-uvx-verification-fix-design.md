---
title: TestPyPI uvx 検証コマンド修正
date: 2026-06-13
status: approved
---

## 問題

`uvx` で TestPyPI からパッケージをインストールすると依存解決に失敗する。

```
× No solution found when resolving tool dependencies:
╰─▶ Because only lxml==4.9.2 is available and epub-content-extractor==0.2.2
    depends on lxml>=5.0, we can conclude that epub-content-extractor==0.2.2
    cannot be used.
```

## 原因

`epub-content-extractor` は `lxml>=5.0` を要求するが、TestPyPI には `lxml==4.9.2` しか存在しない。uv のデフォルトインデックス戦略（`first-match`）は、最初のインデックスでパッケージが見つかると他のインデックスを参照しないため、PyPI の `lxml>=5.0` に辿り着けない。

## 解決策

`--extra-index-url` で PyPI を追加インデックスとして指定し、`--index-strategy unsafe-best-match` で全インデックスから最適バージョンを選択させる。

## 修正後のコマンド

```bash
# MCP サーバーとして起動確認
uvx --from "epub-content-extractor" \
    --index "https://test.pypi.org/simple/" \
    --extra-index-url "https://pypi.org/simple/" \
    --index-strategy unsafe-best-match \
    epub-content-extractor

# CLI ツールとして動作確認
uvx --from "epub-content-extractor" \
    --index "https://test.pypi.org/simple/" \
    --extra-index-url "https://pypi.org/simple/" \
    --index-strategy unsafe-best-match \
    epub-extract <EPUBファイルパス>

# バージョン指定
uvx --from "epub-content-extractor==0.2.2" \
    --index "https://test.pypi.org/simple/" \
    --extra-index-url "https://pypi.org/simple/" \
    --index-strategy unsafe-best-match \
    epub-content-extractor
```

## 変更対象

- `README.md` の TestPyPI 検証コマンドを上記に更新

## 対象外

- `pyproject.toml` の依存定義は変更しない（`lxml>=5.0` は正当な要件）
- CI/CD ワークフローは変更しない
