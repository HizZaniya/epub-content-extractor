#!/usr/bin/env bash
set -u

input=$(cat)
MODEL=$(printf '%s' "$input" | jq -r '.model.display_name // "unknown"')
PCT=$(printf '%s' "$input" | jq -r '.context_window.used_percentage // 0' | cut -d. -f1)

if BRANCH=$(git branch --show-current 2>/dev/null) && [ -n "$BRANCH" ]; then
    echo "${MODEL} | ${PCT}% | ${BRANCH}"
else
    echo "${MODEL} | ${PCT}%"
fi
