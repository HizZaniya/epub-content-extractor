#!/usr/bin/env bash
# PostToolUse hook: gh pr create 後にPRテンプレート必須セクションを検証する

set -euo pipefail

input=$(cat)

# Bash ツールの gh pr create コマンドか確認
command=$(echo "$input" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('tool_input', {}).get('command', ''))
except Exception:
    print('')
" 2>/dev/null || true)

if ! echo "$command" | grep -qE 'gh pr create'; then
    exit 0
fi

# ツール出力から PR URL を抽出
output=$(echo "$input" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    resp = d.get('tool_response', '')
    if isinstance(resp, str):
        print(resp)
    elif isinstance(resp, dict):
        print(resp.get('output', '') or resp.get('stdout', ''))
    else:
        print('')
except Exception:
    print('')
" 2>/dev/null || true)

pr_url=$(echo "$output" | grep -oE 'https://github\.com/[^[:space:]]+/pull/[0-9]+' | head -1 || true)

if [ -z "$pr_url" ]; then
    exit 0
fi

# PR 本文を取得
body=$(gh pr view "$pr_url" --json body --jq '.body' 2>/dev/null || echo "")

if [ -z "$body" ]; then
    exit 0
fi

# 必須セクションチェック
required_sections=(
    "## 概要"
    "## ラベル"
    "## 完了条件"
    "## パフォーマンス影響"
    "## レビュアーへの案内"
)

missing=()
for section in "${required_sections[@]}"; do
    if ! echo "$body" | grep -qF "$section"; then
        missing+=("$section")
    fi
done

# ラベルのチェックボックス確認（- [x] が1つ以上）
if ! echo "$body" | grep -qE '\- \[x\]'; then
    missing+=("ラベルのチェック（## ラベル セクションで - [x] を1つ選択）")
fi

if [ ${#missing[@]} -gt 0 ]; then
    echo "⚠️  PRテンプレート検証失敗: 以下が不足または未入力です"
    for m in "${missing[@]}"; do
        echo "  • $m"
    done
    echo ""
    echo "以下のコマンドでPR本文を修正してください:"
    echo "  gh pr edit $pr_url"
    exit 2
fi

exit 0
