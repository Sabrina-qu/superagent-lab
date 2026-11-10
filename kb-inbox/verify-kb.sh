#!/bin/bash
# kb-inbox/verify-kb.sh — kb 收料→切分→质检门禁（Phase 2）
# Usage: bash verify-kb.sh <kb-dir>
set -uo pipefail
DIR="${1:-.}"
cd "$DIR" || exit 1
FAIL=0
echo "=== kb-verify: $(basename "$DIR") ==="

# 1. 格式：每条含标题+正文+标签（只检查产出条目，不检查 raw/ 和元文件）
echo "--- format ---"
for f in $(find . -name '*.md' -not -path './vocab.md' -not -path './index.md' -not -path './README.md' -not -path './ISSUE-TEMPLATE.md' -not -path './raw/*' -not -path './samples/*' 2>/dev/null | head -20); do
  if ! grep -q '^# ' "$f" || ! grep -qi '标签\|tag' "$f"; then
    echo "FORMAT-FAIL $f (missing heading or tag section)"
    FAIL=1
  fi
done
[ $FAIL -eq 0 ] && echo "OK format"

# 2. 词表：所有标签 ∈ 受控词表 kb/vocab.md
echo "--- vocab ---"
if [ -f vocab.md ]; then
  VOCAB=$(grep -oE '^\- [a-z0-9_-]+' vocab.md | sed 's/^- //' | sort -u)
  BAD=0
  for f in $(find . -name '*.md' -not -path './vocab.md' -not -path './index.md' -not -path './README.md' -not -path './ISSUE-TEMPLATE.md' -not -path './raw/*' -not -path './samples/*' 2>/dev/null | head -20); do
    TAGS=$(grep -oiE '标签[：:]\s*[^\n]+' "$f" | sed 's/.*[：:]//' | tr ',' '\n' | tr ' ' '\n' | sed '/^$/d' | head -10)
    for t in $TAGS; do
      if ! echo "$VOCAB" | grep -qx "$t"; then
        echo "VOCAB-FAIL $f tag=$t not in vocab"
        BAD=1
      fi
    done
  done
  [ $BAD -eq 0 ] && echo "OK vocab"
else
  echo "MISSING vocab.md"
  FAIL=1
fi

# 3. 完整性：无重复条目
echo "--- completeness ---"
if [ -f index.md ]; then
  DUPES=$(grep -oE '\[[^]]+\]' index.md | sort | uniq -d | head -5)
  if [ -n "$DUPES" ]; then echo "DUPES in index.md: $DUPES"; FAIL=1; else echo "OK no dupes"; fi
else
  echo "MISSING index.md"
  FAIL=1
fi

echo "=== kb-verify result: $([ $FAIL -eq 0 ] && echo PASS || echo FAIL) ==="
exit $FAIL
