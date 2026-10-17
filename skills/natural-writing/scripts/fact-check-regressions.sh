#!/usr/bin/env bash
# Regression fixtures for validate.py --mode fact-check (real files; run from anywhere).
set -u
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
V="python3 $ROOT/skills/natural-writing/scripts/validate.py"
dir=$(mktemp -d /tmp/nw-regression.XXXXXX)
pass=0; fail=0

check() { # name expected(0|2) orig_file rew_file
  local name=$1 want=$2 o=$3 r=$4 got
  $V --mode fact-check --original "$o" --rewritten "$r" >/dev/null 2>&1
  got=$?
  if [ "$got" -eq "$want" ]; then
    echo "PASS $name (exit=$got as expected)"; pass=$((pass+1))
  else
    echo "FAIL $name (exit=$got, want=$want)"; fail=$((fail+1))
    $V --mode fact-check --original "$o" --rewritten "$r" 2>/dev/null | head -20
  fi
}

# t1: unit swap ms -> s MUST fail (Hard Rule 1: unit drift is fact drift)
printf 'The tail latency was 240 ms at peak load.\n' > "$dir/t1o"
printf 'The tail latency was 240 s at peak load.\n' > "$dir/t1r"
check t1_unit_swap_ms_to_s 2 "$dir/t1o" "$dir/t1r"

# t2: unit swap GB -> MB MUST fail
printf 'Cache grew to 5 GB.\n' > "$dir/t2o"
printf 'Cache grew to 5 MB.\n' > "$dir/t2r"
check t2_unit_swap_gb_to_mb 2 "$dir/t2o" "$dir/t2r"

# t3: CJK digit spacing 2点 vs 2 点 MUST pass
printf '以下の2点を適用した。\n' > "$dir/t3o"
printf '以下の 2 点を適用した。\n' > "$dir/t3r"
check t3_cjk_spacing_equivalent 0 "$dir/t3o" "$dir/t3r"

# t4: heading/section numbering added in rewrite MUST pass (structural, not factual)
printf '障害は14:22に発生し、47件のエラーを記録した。\n' > "$dir/t4o"
cat > "$dir/t4r" <<'EOF'
## 1. 概要

### 3.1 影響

### Decision 1: 記録

障害は 14:22 に発生し、47 件のエラーを記録した。
EOF
check t4_heading_numbers_structural 0 "$dir/t4o" "$dir/t4r"

# t5: p99.9 must not yield a phantom "9 s" token; identical figures MUST pass
printf 'p99.9 latency spikes reached 240 ms under load.\n' > "$dir/t5o"
printf 'p99.9 spikes reached 240 ms under load.\n' > "$dir/t5r"
check t5_p999_no_phantom_unit 0 "$dir/t5o" "$dir/t5r"

# t6: thousands separators 50,000 vs 50000 and 1,840 vs 1840 MUST pass
printf '50,000 rows and 1,840 queued requests.\n' > "$dir/t6o"
printf '50000 rows and 1840 queued requests.\n' > "$dir/t6r"
check t6_thousands_separator_equivalent 0 "$dir/t6o" "$dir/t6r"

# t7: dropped node count 8 节点 -> 多个节点 MUST fail (counter is a quantity, not a section)
printf 'クラスタは 8 节点で構成される。\n' > "$dir/t7o"
printf 'クラスタは多个节点で構成される。\n' > "$dir/t7r"
check t7_dropped_node_count 2 "$dir/t7o" "$dir/t7r"

# t8: section self-reference 5 節のとおり added in rewrite MUST pass (structural)
printf 'ヘッダ設定と crossorigin 属性付与を確認する。\n' > "$dir/t8o"
printf '5 節のとおり、ヘッダ設定と crossorigin 属性付与を確認する。\n' > "$dir/t8r"
check t8_section_reference_structural 0 "$dir/t8o" "$dir/t8r"

# t9: literal \n inside code spans survives; figures unchanged MUST pass
printf '設定ファイルに `line1\\nline2` を書き、3 回再試行する。\n' > "$dir/t9o"
printf '設定ファイルに `line1\\nline2` を書き、3 回再試行する。\n' > "$dir/t9r"
check t9_literal_backslash_n_code_span 0 "$dir/t9o" "$dir/t9r"

# t10: 第-prefixed chapter counter replaced by 前章 MUST pass (structural)
printf '第 3 章で説明した 3 段階の手法を適用する。\n' > "$dir/t10o"
printf '前章で説明した 3 段階の手法を適用する。\n' > "$dir/t10r"
check t10_chapter_reference_structural 0 "$dir/t10o" "$dir/t10r"

echo "----------------------------------------"
echo "SUMMARY: $pass passed, $fail failed"
rm -rf "$dir"
[ "$fail" -eq 0 ]
