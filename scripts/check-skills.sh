#!/usr/bin/env bash
set -u
set -o pipefail

root=${1:-skills}

if [[ ! -d "$root" ]]; then
  printf 'Skills root does not exist: %s\n' "$root" >&2
  printf 'SUMMARY: 0 passed, 0 warnings, 1 failed\n'
  exit 1
fi

shopt -s nullglob
directories=("$root"/*/)
if ((${#directories[@]} == 0)); then
  printf 'No skill directories found under: %s\n' "$root" >&2
  printf 'SUMMARY: 0 passed, 0 warnings, 1 failed\n'
  exit 1
fi

passed=0
warned=0
failed=0

for skill_dir in "${directories[@]}"; do
  skill_dir=${skill_dir%/}
  file="$skill_dir/SKILL.md"
  expected_name=${skill_dir##*/}
  errors=()
  warnings=()
  frontmatter_end=''
  name=''
  description=''

  if [[ ! -f "$file" ]]; then
    errors+=("SKILL.md is missing")
  else
    first_line=$(sed -n '1p' "$file")
  if [[ "$first_line" != "---" ]]; then
    errors+=("does not start with YAML frontmatter delimiter ---")
  else
    if frontmatter_end=$(awk '
      NR > 1 && $0 == "---" { print NR; found = 1; exit }
      END { if (!found) exit 1 }
    ' "$file"); then
      if name=$(awk -v end="$frontmatter_end" '
        NR >= 2 && NR < end && $0 ~ /^name:[[:space:]]*/ {
          value = substr($0, index($0, ":") + 1)
          sub(/^[[:space:]]+/, "", value)
          print value
          found = 1
          exit
        }
        END { if (!found) exit 1 }
      ' "$file"); then
        if [[ -z "$name" ]]; then
          errors+=("name is empty")
        elif [[ ! "$name" =~ ^[a-z0-9-]{1,64}$ ]]; then
          errors+=("name must be 1-64 characters using only lowercase letters, numbers, and hyphens")
        elif [[ "$name" == -* || "$name" == *- ]]; then
          errors+=("name must not start or end with a hyphen")
        elif [[ "$name" == *--* ]]; then
          errors+=("name must not contain consecutive hyphens")
        fi
        if [[ "$name" != "$expected_name" ]]; then
          errors+=("name '$name' does not match parent directory '$expected_name'")
        fi
      else
        errors+=("name is missing from frontmatter")
      fi

      if description=$(awk -v end="$frontmatter_end" '
        NR >= 2 && NR < end {
          if (!collecting && $0 ~ /^description:[[:space:]]*/) {
            value = substr($0, index($0, ":") + 1)
            sub(/^[[:space:]]+/, "", value)
            found = 1
            if (value ~ /^>[+-]?[[:space:]]*$/ || value ~ /^\|[+-]?[[:space:]]*$/) {
              value = ""
              collecting = 1
              next
            }
            print value
            emitted = 1
            exit
          }
          if (collecting) {
            if ($0 == "" || $0 ~ /^[[:space:]]/) {
              continuation = $0
              sub(/^[[:space:]]+/, "", continuation)
              if (value != "") value = value " "
              value = value continuation
              next
            }
            print value
            emitted = 1
            exit
          }
        }
        END {
          if (collecting && !emitted) print value
          if (!found) exit 1
        }
      ' "$file"); then
        if [[ -z "${description//[[:space:]]/}" ]]; then
          errors+=("description is empty")
        else
          description_chars=$(printf '%s' "$description" | wc -m)
          if ((description_chars > 1024)); then
            errors+=("description is $description_chars characters; maximum is 1024")
          elif ((description_chars > 250)); then
            warnings+=("description is $description_chars characters; recommended maximum is 250")
          fi
        fi
      else
        errors+=("description is missing from frontmatter")
      fi

      body_lines=$(awk -v end="$frontmatter_end" 'NR > end { count++ } END { print count + 0 }' "$file")
      if ((body_lines > 500)); then
        warnings+=("body is $body_lines lines; recommended maximum is 500")
      fi
    else
      errors+=("frontmatter is not closed by a second --- delimiter")
    fi
  fi
  fi

  if ((${#errors[@]} > 0)); then
    printf 'FAIL %s\n' "$file"
    for reason in "${errors[@]}"; do
      printf '%s: %s\n' "$file" "$reason" >&2
    done
    ((failed += 1))
  elif ((${#warnings[@]} > 0)); then
    printf 'WARN %s (%s)\n' "$file" "$(IFS='; '; printf '%s' "${warnings[*]}")"
    ((warned += 1))
  else
    printf 'PASS %s\n' "$file"
    ((passed += 1))
  fi
done

printf 'SUMMARY: %d passed, %d warnings, %d failed\n' "$passed" "$warned" "$failed"
if ((failed > 0)); then
  exit 1
fi
