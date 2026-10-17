#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pyyaml>=6.0.2",
# ]
# ///
"""Deterministic validator, contextual symptom scanner, and fact-preservation checker for natural-writing.

Modes:
  validate   (default) Validate skill structure, schemas, cross-references, sources, and JSONL datasets.
  scan       Scan text or a file for Layer 3 symptom review candidates (always action=review_only).
  fact-check Compare original and rewritten text to detect dropped numbers, code spans, or terms.

Exit codes:
  0  Success / all checks passed.
  2  Validation error, fact-check drift, or invalid CLI usage.
  3  Missing input file.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

# Keep default scan output bounded so agent harnesses never ingest unbounded match dumps.
DEFAULT_SCAN_LIMIT = 50
# Agent Skills specification limits for SKILL.md frontmatter and body.
MAX_DESCRIPTION_CHARS = 1024
RECOMMENDED_DESCRIPTION_CHARS = 250
RECOMMENDED_BODY_LINES = 500

EXIT_OK = 0
EXIT_VALIDATION_ERROR = 2
EXIT_MISSING_INPUT = 3

SKILL_ROOT = Path(__file__).resolve().parent.parent


def log_err(message: str) -> None:
    """Write human-readable diagnostics to stderr so stdout remains pure JSON."""
    sys.stderr.write(f"{message}\n")


def _safe_load_yaml(content: str) -> Any:
    try:
        import yaml
    except ModuleNotFoundError as exc:
        raise ValueError(
            "PyYAML is required for YAML validation/scan modes; run via `uv run skills/natural-writing/scripts/validate.py`."
        ) from exc
    return yaml.safe_load(content)


def load_yaml_file(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Missing YAML file: {path.relative_to(SKILL_ROOT)}")
    data = _safe_load_yaml(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected top-level mapping in {path.relative_to(SKILL_ROOT)}")
    return data

def load_jsonl_file(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise FileNotFoundError(f"Missing JSONL file: {path.relative_to(SKILL_ROOT)}")
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line_no, raw in enumerate(fh, start=1):
            stripped = raw.strip()
            if not stripped:
                continue
            try:
                obj = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Malformed JSON in {path.relative_to(SKILL_ROOT)}:{line_no}: {exc}"
                ) from exc
            if not isinstance(obj, dict):
                raise ValueError(
                    f"Expected JSON object in {path.relative_to(SKILL_ROOT)}:{line_no}"
                )
            records.append(obj)
    return records


def extract_source_ids(sources_md: Path) -> set[str]:
    r"""Extract all `### \`source_id\`` headings from references/sources.md."""
    text = sources_md.read_text(encoding="utf-8")
    return set(re.findall(r"^### `([a-z0-9-]+)`\s*$", text, flags=re.MULTILINE))


def validate_markdown_links(md_path: Path) -> list[str]:
    """Check that every relative Markdown link resolves and enforce 1-level depth (AP-27)."""
    errors: list[str] = []
    rel_md = md_path.relative_to(SKILL_ROOT)
    is_nested_doc = rel_md.parts[0] in ("references", "evals")
    text = md_path.read_text(encoding="utf-8")
    for match in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", text):
        target = match.group(1).strip()
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        clean_target = target.split("#", 1)[0]
        if not clean_target:
            continue
        if is_nested_doc:
            errors.append(
                f"{rel_md}: nested relative link '{target}' violates one-level reference depth (link from SKILL.md instead)"
            )
            continue
        resolved = (md_path.parent / clean_target).resolve()
        if not resolved.exists():
            errors.append(f"{rel_md}: broken link target '{target}'")
        elif resolved.is_file() and resolved.stat().st_size == 0:
            errors.append(f"{rel_md}: link target '{target}' is empty")
    return errors


def validate_skill_package() -> tuple[bool, dict[str, Any]]:
    errors: list[str] = []
    warnings: list[str] = []

    required_files = [
        "SKILL.md",
        "README.md",
        "patterns/schema.json",
        "patterns/symptoms.yaml",
        "rules/core.yaml",
        "rules/zh-CN.yaml",
        "rules/en.yaml",
        "rules/ja.yaml",
        "references/foundations.md",
        "references/sources.md",
        "references/principles.md",
        "references/pragmatics.md",
        "references/chinese.md",
        "references/english.md",
        "references/japanese.md",
        "examples/zh-CN.jsonl",
        "examples/en.jsonl",
        "examples/ja.jsonl",
        "evals/cases.jsonl",
        "evals/rubric.md",
        "evals/ablation.md",
    ]

    for rel in required_files:
        p = SKILL_ROOT / rel
        if not p.is_file():
            errors.append(f"Missing required file: {rel}")
        elif p.stat().st_size == 0:
            errors.append(f"Empty required file: {rel}")

    if errors:
        return False, {"status": "error", "errors": errors, "warnings": warnings}

    # 1. Validate SKILL.md frontmatter and links
    skill_md = SKILL_ROOT / "SKILL.md"
    skill_text = skill_md.read_text(encoding="utf-8")
    fm_match = re.match(r"^---\n(.*?)\n---\n(.*)$", skill_text, flags=re.DOTALL)
    if not fm_match:
        errors.append("SKILL.md: missing valid YAML frontmatter delimiters")
        body_lines = 0
        desc_len = 0
    else:
        fm_data = _safe_load_yaml(fm_match.group(1)) or {}
        body_text = fm_match.group(2)
        body_lines = len(body_text.splitlines())
        name = str(fm_data.get("name", ""))
        desc = str(fm_data.get("description", "")).strip()
        desc_len = len(desc)
        if name != SKILL_ROOT.name:
            errors.append(
                f"SKILL.md: name '{name}' does not match directory '{SKILL_ROOT.name}'"
            )
        if not desc:
            errors.append("SKILL.md: description is empty")
        elif desc_len > MAX_DESCRIPTION_CHARS:
            errors.append(
                f"SKILL.md: description length {desc_len} exceeds {MAX_DESCRIPTION_CHARS}"
            )
        elif desc_len > RECOMMENDED_DESCRIPTION_CHARS:
            warnings.append(
                f"SKILL.md: description length {desc_len} exceeds recommended {RECOMMENDED_DESCRIPTION_CHARS}"
            )
        if body_lines > RECOMMENDED_BODY_LINES:
            warnings.append(
                f"SKILL.md: body has {body_lines} lines (recommended <= {RECOMMENDED_BODY_LINES})"
            )

    for md_rel in [
        "SKILL.md",
        "README.md",
        "references/foundations.md",
        "references/sources.md",
        "references/principles.md",
        "references/pragmatics.md",
        "references/chinese.md",
        "references/english.md",
        "references/japanese.md",
        "evals/rubric.md",
        "evals/ablation.md",
    ]:
        errors.extend(validate_markdown_links(SKILL_ROOT / md_rel))

    # 2. Extract valid source IDs from references/sources.md
    source_ids = extract_source_ids(SKILL_ROOT / "references/sources.md")
    if len(source_ids) < 15:
        errors.append(
            f"references/sources.md: expected at least 15 indexed sources, found {len(source_ids)}"
        )

    # 3. Validate Layer 1 and Layer 2 rule files
    rule_files = [
        ("core", "rules/core.yaml"),
        ("language", "rules/zh-CN.yaml"),
        ("language", "rules/en.yaml"),
        ("language", "rules/ja.yaml"),
    ]
    all_rule_ids: set[str] = set()
    core_rule_ids: set[str] = set()
    rule_counts: dict[str, int] = {}

    required_rule_keys = {
        "id",
        "layer",
        "language",
        "category",
        "severity",
        "version",
        "updated_at",
        "principle",
        "problem",
        "triggers",
        "detection",
        "revision_strategy",
        "exceptions",
        "sources",
        "examples",
    }

    for expected_layer, rel_path in rule_files:
        data = load_yaml_file(SKILL_ROOT / rel_path)
        rules = data.get("rules", [])
        if not isinstance(rules, list) or not rules:
            errors.append(f"{rel_path}: 'rules' must be a non-empty list")
            continue
        rule_counts[rel_path] = len(rules)
        for rule in rules:
            rid = rule.get("id", "<missing>")
            missing = required_rule_keys - set(rule.keys())
            if missing:
                errors.append(f"{rel_path} [{rid}]: missing keys {sorted(missing)}")
            if rid in all_rule_ids:
                errors.append(f"{rel_path}: duplicate rule id '{rid}'")
            all_rule_ids.add(rid)
            if expected_layer == "core":
                core_rule_ids.add(rid)
            else:
                parent = rule.get("parent_principle")
                if not parent:
                    errors.append(
                        f"{rel_path} [{rid}]: Layer 2 rule missing 'parent_principle'"
                    )
                elif parent not in core_rule_ids:
                    errors.append(
                        f"{rel_path} [{rid}]: parent_principle '{parent}' not found in rules/core.yaml"
                    )
            for src in rule.get("sources", []):
                if src not in source_ids:
                    errors.append(
                        f"{rel_path} [{rid}]: source '{src}' not found in references/sources.md"
                    )
            examples = rule.get("examples", [])
            verdicts = {ex.get("verdict") for ex in examples if isinstance(ex, dict)}
            if "rewrite" not in verdicts or "keep" not in verdicts:
                errors.append(
                    f"{rel_path} [{rid}]: must include both 'rewrite' and 'keep' examples"
                )

    # 4. Validate Layer 3 symptoms.yaml
    symptoms_data = load_yaml_file(SKILL_ROOT / "patterns/symptoms.yaml")
    symptoms = symptoms_data.get("symptoms", [])
    symptom_ids: set[str] = set()
    status_counts: dict[str, int] = {"active": 0, "monitoring": 0, "deprecated": 0}
    required_symptom_keys = {
        "id",
        "layer",
        "version",
        "status",
        "action_on_match",
        "observed_since",
        "last_reviewed",
        "affected_models",
        "languages",
        "category",
        "severity",
        "linked_rules",
        "surface_patterns",
        "why_it_occurs",
        "contextual_test",
        "valid_contexts",
        "revision_guidance",
        "examples",
    }

    for sym in symptoms:
        sid = sym.get("id", "<missing>")
        missing = required_symptom_keys - set(sym.keys())
        if missing:
            errors.append(
                f"patterns/symptoms.yaml [{sid}]: missing keys {sorted(missing)}"
            )
        if sid in symptom_ids:
            errors.append(f"patterns/symptoms.yaml: duplicate symptom id '{sid}'")
        symptom_ids.add(sid)

        if sym.get("action_on_match") != "review_only":
            errors.append(
                f"patterns/symptoms.yaml [{sid}]: action_on_match must be 'review_only'"
            )
        status = sym.get("status")
        if status in status_counts:
            status_counts[status] += 1
        else:
            errors.append(
                f"patterns/symptoms.yaml [{sid}]: invalid status '{status}'"
            )
        for lr in sym.get("linked_rules", []):
            if lr not in all_rule_ids:
                errors.append(
                    f"patterns/symptoms.yaml [{sid}]: unknown linked_rule '{lr}'"
                )
        ex_verdicts = {
            ex.get("verdict") for ex in sym.get("examples", []) if isinstance(ex, dict)
        }
        if "rewrite" not in ex_verdicts or "keep" not in ex_verdicts:
            errors.append(
                f"patterns/symptoms.yaml [{sid}]: must include both 'rewrite' and 'keep' examples"
            )

    # 5. Validate examples/*.jsonl
    example_counts: dict[str, int] = {}
    for ex_rel in ["examples/zh-CN.jsonl", "examples/en.jsonl", "examples/ja.jsonl"]:
        records = load_jsonl_file(SKILL_ROOT / ex_rel)
        example_counts[ex_rel] = len(records)
        verdicts = set()
        for rec in records:
            eid = rec.get("id", "<missing>")
            verdicts.add(rec.get("verdict"))
            for tr in rec.get("triggered_rules", []):
                if tr not in all_rule_ids:
                    errors.append(f"{ex_rel} [{eid}]: unknown triggered_rule '{tr}'")
            for ts in rec.get("triggered_symptoms", []):
                if ts not in symptom_ids:
                    errors.append(f"{ex_rel} [{eid}]: unknown triggered_symptom '{ts}'")
        if "rewrite" not in verdicts or "keep" not in verdicts:
            errors.append(f"{ex_rel}: must contain both 'rewrite' and 'keep' records")

    # 6. Validate evals/cases.jsonl
    eval_cases = load_jsonl_file(SKILL_ROOT / "evals/cases.jsonl")
    eval_langs = {c.get("language") for c in eval_cases}
    eval_categories = {c.get("category") for c in eval_cases}
    for req_lang in ("zh-CN", "en", "ja"):
        if req_lang not in eval_langs:
            errors.append(f"evals/cases.jsonl: missing language '{req_lang}'")
    required_eval_categories = {
        "context_sensitive_metaphor",
        "valid_contrast_preservation",
        "false_contrast_removal",
        "anti_colloquial_overcorrection",
        "literary_metaphor_preservation",
        "technical_term_preservation",
        "information_density_and_fidelity",
        "register_and_keigo_calibration",
    }
    missing_cats = required_eval_categories - eval_categories
    if missing_cats:
        errors.append(
            f"evals/cases.jsonl: missing required categories {sorted(missing_cats)}"
        )
    # 7. Bidirectional n-gram anti-leakage check (CJK 4-grams & Latin 3-word windows)
    corpus_files = [
        "SKILL.md",
        "README.md",
        "rules/core.yaml",
        "rules/zh-CN.yaml",
        "rules/en.yaml",
        "rules/ja.yaml",
        "patterns/symptoms.yaml",
        "examples/zh-CN.jsonl",
        "examples/en.jsonl",
        "examples/ja.jsonl",
        "references/foundations.md",
        "references/sources.md",
        "references/principles.md",
        "references/pragmatics.md",
        "references/chinese.md",
        "references/english.md",
        "references/japanese.md",
    ]
    combined_corpus = "\n".join(
        (SKILL_ROOT / cf).read_text(encoding="utf-8") for cf in corpus_files
    )
    combined_corpus_lower = combined_corpus.lower()
    # Only bare grammatical/symptom inflections tested across the suite are masked
    # before CJK 4-gram extraction; all scenario nouns, calques, and rewrites are checked.
    cjk_grammar_mask = (
        "稳稳地接住",
        "彻底闭环",
        "而是一场",
        "而是一次",
        "といったような",
        "かと思われます",
        "の実施を行うことが可能であり",
        "という形になります",
        "させていただきます",
        "れていた",
        "いたします",
        "のご担当者様がおっしゃっていた",
        "おっしゃっていた",
        "しました",
        "できます",
        "されます",
        "なかった",
        "ったと推",
    )
    cjk_run_re = re.compile(r"[\u4e00-\u9fff\u3040-\u30ff]{4,}")
    latin_word_re = re.compile(r"[A-Za-z0-9_.-]+")
    for case in eval_cases:
        cid = case.get("id", "<missing>")
        for label in ("input_text", "reference_output"):
            raw_span = str(case.get(label, "")).strip()
            if raw_span and raw_span in combined_corpus:
                errors.append(
                    f"evals/cases.jsonl [{cid}]: {label} leaks verbatim into skill corpus"
                )
            span = re.sub(r"(?:core|zh|en|ja|symptom)\.[a-z0-9_.]+", "", raw_span)
            # Check Latin 3-word windows (zero overlap permitted across all 17 files)
            words = [w.lower() for w in latin_word_re.findall(span)]
            for idx in range(len(words) - 2):
                w3 = " ".join(words[idx : idx + 3])
                if re.search(r"\b" + re.escape(w3) + r"\b", combined_corpus_lower):
                    errors.append(
                        f"evals/cases.jsonl [{cid}]: {label} Latin 3-word window '{w3}' leaks into skill corpus"
                    )
                    break
            # Check CJK 4-grams across all 17 files
            masked_span = span
            for gm in cjk_grammar_mask:
                masked_span = masked_span.replace(gm, " ")
            leaked_cjk = None
            for m in cjk_run_re.finditer(masked_span):
                run = m.group(0)
                for idx in range(len(run) - 3):
                    g4 = run[idx : idx + 4]
                    if g4 in combined_corpus:
                        leaked_cjk = g4
                        break
                if leaked_cjk:
                    break
            if leaked_cjk:
                errors.append(
                    f"evals/cases.jsonl [{cid}]: {label} CJK 4-gram '{leaked_cjk}' leaks into skill corpus"
                )
    ok = len(errors) == 0
    summary = {
        "status": "ok" if ok else "error",
        "skill_name": SKILL_ROOT.name,
        "skill_md_body_lines": body_lines,
        "skill_md_description_chars": desc_len,
        "indexed_sources": len(source_ids),
        "rule_counts": rule_counts,
        "total_rules": len(all_rule_ids),
        "symptom_counts": status_counts,
        "total_symptoms": len(symptom_ids),
        "example_counts": example_counts,
        "eval_case_count": len(eval_cases),
        "warnings": warnings,
        "errors": errors,
    }
    return ok, summary


def scan_text_for_symptoms(
    text: str, lang: str | None, limit: int
) -> dict[str, Any]:
    """Scan text against active/monitoring Layer 3 symptoms as review_only signals."""
    symptoms_data = load_yaml_file(SKILL_ROOT / "patterns/symptoms.yaml")
    matches: list[dict[str, Any]] = []

    for sym in symptoms_data.get("symptoms", []):
        if sym.get("status") == "deprecated":
            continue
        sym_langs = sym.get("languages", [])
        if lang and lang not in sym_langs:
            continue
        hit_patterns: list[str] = []
        for pat in sym.get("surface_patterns", []):
            # Support '...' or '……' wildcard spans in surface patterns
            regex_pat = re.escape(pat).replace(r"\.\.\.", r".{1,40}?").replace("……", r".{1,30}?")
            if re.search(regex_pat, text, flags=re.IGNORECASE):
                hit_patterns.append(pat)
        if hit_patterns:
            matches.append(
                {
                    "symptom_id": sym["id"],
                    "status": sym["status"],
                    "action": sym["action_on_match"],
                    "severity": sym["severity"],
                    "matched_patterns": hit_patterns,
                    "linked_rules": sym["linked_rules"],
                    "contextual_test": sym["contextual_test"],
                    "valid_contexts": sym["valid_contexts"],
                    "revision_guidance": sym["revision_guidance"],
                }
            )
            if len(matches) >= limit:
                break

    return {
        "status": "ok",
        "note": "Symptom matches are review_only signals. Evaluate each hit against its contextual_test and valid_contexts before editing.",
        "match_count": len(matches),
        "limit": limit,
        "matches": matches,
    }


_UNIT_MAP = {
    "seconds": "s",
    "second": "s",
    "sec": "s",
    "secs": "s",
    "milliseconds": "ms",
    "millisecond": "ms",
    "minutes": "min",
    "minute": "min",
    "hours": "h",
    "hour": "h",
}

_NUMBER_TOKEN_RE = re.compile(
    r"(?<![a-zA-Z0-9_./-])"
    r"-?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?"
    r"(?:(?:\s|-)?(?:%|ms|s|sec(?:ond)?s?|min(?:ute)?s?|hours?|KB|MB|GB|TB|PB|KiB|MiB|GiB|Hz|req/s|RPC/s|FPS)(?![a-zA-Z])"
    r"|(?:\s|-)?(?:秒|分|時間|小时|点|件|回|次|行|個|个|月|日|万))?"
)


def _strip_structural_numbering(text: str) -> str:
    """Remove Markdown heading numbers, list markers, and section labels before extracting factual numbers."""
    cleaned = re.sub(
        r"(?m)^(\s*#{1,6}\s+(?:(?:Section|Decision|Step|Phase|Part|第)\s*)?)\d+(?:\.\d+)*[.):、．]?\s+",
        r"\1",
        text,
    )
    cleaned = re.sub(
        r"(?m)^(\s*(?:[-*]\s+)?(?:\*\*)?[（(]?)\d+(?:\.\d+)*[)）.、:](\*\*)?\s+",
        r"\1\2 ",
        cleaned,
    )
    cleaned = re.sub(
        r"\b(?:Section|Decision|Step|Phase|Part)\s+\d+(?:\.\d+)*\b",
        " ",
        cleaned,
        flags=re.IGNORECASE,
    )
    # CJK section counters: 第-prefixed forms are always structural; a bare
 # "N 節/章/…" is stripped only as a cross-reference (e.g. "5 節のとおり"),
 # never when the counter builds a quantity noun ("8 节点" keeps its "8").
    cleaned = re.sub(r"第\s*\d+\s*(?:节|節|章|篇|步|歩)", " ", cleaned)
    cleaned = re.sub(
        r"\d+\s*(?:节|節|章|篇)(?=(?:の|で|に|は|と|及び|とおり|、|。|，|：|\s|$))",
        " ",
        cleaned,
    )
    return cleaned


def _normalize_numeric_token(token: str) -> str:
    """Normalize commas, spaces, hyphens, and English unit spellings for equivalence comparison."""
    s = token.strip().replace(",", "")
    m = re.match(r"^(-?\d+(?:\.\d+)?)(?:[\s-]*(.+))?$", s)
    if not m:
        return s
    num, unit = m.group(1), (m.group(2) or "").strip()
    unit = _UNIT_MAP.get(unit.lower(), unit)
    return f"{num}{unit}"


def extract_invariants(text: str, extra_terms: list[str]) -> dict[str, list[str]]:
    """Extract numeric tokens, version strings, inline code spans, URLs, and custom terms."""
    prose_text = _strip_structural_numbering(text)
    numbers = sorted(set(_NUMBER_TOKEN_RE.findall(prose_text)))
    versions = sorted(set(re.findall(r"\bv\d+(?:\.\d+)+\b", text)))
    code_spans = sorted(set(re.findall(r"`([^`]+)`", text)))
    urls = sorted(set(re.findall(r"https?://[^\s)>\]\"']+", text)))
    present_terms = sorted(t for t in extra_terms if t and t in text)
    return {
        "numbers": numbers,
        "versions": versions,
        "code_spans": code_spans,
        "urls": urls,
        "protected_terms": present_terms,
    }

def run_fact_check(
    original: str, rewritten: str, extra_terms: list[str]
) -> tuple[bool, dict[str, Any]]:
    orig_inv = extract_invariants(original, extra_terms)
    rew_inv = extract_invariants(rewritten, extra_terms)
    orig_norm_text = original.replace(",", "")
    rew_norm_text = rewritten.replace(",", "")

    missing: dict[str, list[str]] = {}
    unverified_additions: dict[str, list[str]] = {}

    for key in ("numbers", "versions", "code_spans", "urls", "protected_terms"):
        if key == "numbers":
            orig_norm_map = {_normalize_numeric_token(x): x.strip() for x in orig_inv[key]}
            rew_norm_map = {_normalize_numeric_token(x): x.strip() for x in rew_inv[key]}
            dropped = sorted(
                raw
                for norm, raw in orig_norm_map.items()
                if norm not in rew_norm_map and raw not in rewritten and norm not in rew_norm_text
            )
            added = sorted(
                raw
                for norm, raw in rew_norm_map.items()
                if norm not in orig_norm_map and raw not in original and norm not in orig_norm_text
            )
        else:
            orig_set = {item.strip() for item in orig_inv[key]}
            rew_set = {item.strip() for item in rew_inv[key]}
            dropped = sorted(d for d in (orig_set - rew_set) if d not in rewritten)
            added = sorted(a for a in (rew_set - orig_set) if a not in original)
        if dropped:
            missing[key] = dropped
        if added and key in ("numbers", "versions", "urls"):
            unverified_additions[key] = added

    passed = len(missing) == 0 and len(unverified_additions) == 0
    return passed, {
        "status": "pass" if passed else "fail",
        "missing_from_rewrite": missing,
        "unverified_additions_in_rewrite": unverified_additions,
        "original_invariants": orig_inv,
    }


def read_text_or_file(value: str) -> str:
    candidate = Path(value)
    if candidate.is_file():
        return candidate.read_text(encoding="utf-8")
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="validate.py",
        description="Validate the natural-writing skill package, scan prose for contextual review signals, or check fact preservation.",
        epilog=(
            "Exit codes: 0 success; 2 validation error, fact-check drift, or invalid usage; "
            "3 missing input file. JSON results go to stdout, diagnostics to stderr."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--mode",
        choices=("validate", "scan", "fact-check"),
        default="validate",
        help="Operation mode (default: validate).",
    )
    parser.add_argument(
        "--file",
        help="Path to input file for --mode scan.",
    )
    parser.add_argument(
        "--text",
        help="Inline text string for --mode scan.",
    )
    parser.add_argument(
        "--lang",
        choices=("zh-CN", "en", "ja"),
        help="Optional language filter for --mode scan.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_SCAN_LIMIT,
        help=f"Maximum symptom matches to return in scan mode (default: {DEFAULT_SCAN_LIMIT}).",
    )
    parser.add_argument(
        "--original",
        help="Original text or file path for --mode fact-check.",
    )
    parser.add_argument(
        "--rewritten",
        help="Rewritten text or file path for --mode fact-check.",
    )
    parser.add_argument(
        "--terms",
        default="",
        help="Comma-separated protected terms for --mode fact-check.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.mode == "validate":
        try:
            ok, report = validate_skill_package()
        except FileNotFoundError as exc:
            log_err(f"Error: {exc}")
            return EXIT_MISSING_INPUT
        except ValueError as exc:
            log_err(f"Validation error: {exc}")
            return EXIT_VALIDATION_ERROR

        sys.stdout.write(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
        if ok:
            log_err(
                f"PASS: natural-writing validated ({report['total_rules']} rules, "
                f"{report['total_symptoms']} symptoms, {report['eval_case_count']} eval cases)."
            )
            return EXIT_OK
        for err in report["errors"]:
            log_err(f"FAIL: {err}")
        return EXIT_VALIDATION_ERROR

    if args.mode == "scan":
        if args.file == "-":
            content = sys.stdin.read()
        elif args.file:
            fpath = Path(args.file)
            if not fpath.is_file():
                log_err(
                    f"Error: --file '{args.file}' does not exist. Provide an existing file path, '-', or use --text."
                )
                return EXIT_MISSING_INPUT
            content = fpath.read_text(encoding="utf-8")
        elif args.text:
            content = args.text
        else:
            log_err(
                "Error: --mode scan requires --file <path|-> or --text <string>."
            )
            return EXIT_VALIDATION_ERROR
        result = scan_text_for_symptoms(content, args.lang, max(1, args.limit))
        sys.stdout.write(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
        log_err(
            f"Scanned text: {result['match_count']} review_only symptom signal(s) found."
        )
        return EXIT_OK

    if args.mode == "fact-check":
        if not args.original or not args.rewritten:
            log_err(
                "Error: --mode fact-check requires both --original <path|text> and --rewritten <path|text>."
            )
            return EXIT_VALIDATION_ERROR
        orig_text = read_text_or_file(args.original)
        rew_text = read_text_or_file(args.rewritten)
        terms = [t.strip() for t in args.terms.split(",") if t.strip()]
        passed, report = run_fact_check(orig_text, rew_text, terms)
        sys.stdout.write(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
        if passed:
            log_err("PASS: fact-check verified zero dropped or fabricated invariants.")
            return EXIT_OK
        log_err("FAIL: fact-check detected invariant drift between original and rewrite.")
        return EXIT_VALIDATION_ERROR

    return EXIT_VALIDATION_ERROR


if __name__ == "__main__":
    sys.exit(main())
