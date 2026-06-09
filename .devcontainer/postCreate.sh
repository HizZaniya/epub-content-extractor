#!/usr/bin/env bash
set -euo pipefail

# Python/Node バージョンをインストール
mise trust
mise install

# Python 依存関係をインストール
uv sync --dev
uv tool install ty

# pre-commit フックをインストール
uv run pre-commit install

# Claude Code プラグインをインストール
# settings.json の enabledPlugins で有効化されているが、
# インストール自体は明示的に行う必要がある
claude plugin install superpowers@claude-plugins-official
claude plugin install pyright-lsp@claude-plugins-official
claude plugin install context7@claude-plugins-official
claude plugin install bash-language-server@claude-code-lsps
claude plugin install criticalthink@criticalthink
