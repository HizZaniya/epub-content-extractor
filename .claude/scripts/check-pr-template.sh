#!/usr/bin/env bash
# PreToolUse hook: gh pr create 実行前にPRテンプレート必須セクションを検証する

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

# コマンドを一時ファイルに書き出し、gh を dummy 関数で置き換えて --body を抽出
tmpfile=$(mktemp /tmp/pr-check-XXXXXX.sh)
trap 'rm -f "$tmpfile"' EXIT

cat > "$tmpfile" << 'FUNC'
gh() {
    local _capture_next=0
    for _arg; do
        if [[ $_capture_next -eq 1 ]]; then
            printf '%s' "$_arg"
            return 0
        fi
        [[ "$_arg" == '--body' ]] && _capture_next=1
    done
}
FUNC

printf '%s\n' "$command" >> "$tmpfile"

body=$(bash "$tmpfile" 2>/dev/null || true)

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
    reason="PRテンプレート検証失敗: 以下が不足または未入力です"$'\n'
    for m in "${missing[@]}"; do
        reason+="  • $m"$'\n'
    done
    reason+="PR本文を修正してから再実行してください。"

    python3 -c "
import json, sys
reason = sys.argv[1]
print(json.dumps({
    'hookSpecificOutput': {
        'hookEventName': 'PreToolUse',
        'permissionDecision': 'deny',
        'permissionDecisionReason': reason
    }
}))
" "$reason"
fi

exit 0
