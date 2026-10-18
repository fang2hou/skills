#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Inject a report.json into the vendored renderer template.

Usage:
  build.py DIR           Reads DIR/report.json, writes DIR/index.html.

The template (assets/report-template.html) is the prebuilt single-file renderer
from fang2hou/report-kit, kept in readable form in this repository; this script
only embeds the report data (~390 KB before content, within the 1 MB budget).
Never re-minify the template's JS here: compressing an already-formatted bundle
with a second tool silently corrupts code paths. Validation is a guard rail —
the authoritative schema lives in report-kit's src/lib/schema.ts.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

BLOCK_TYPES = {
    "p",
    "ul",
    "ol",
    "steps",
    "callout",
    "card",
    "kv",
    "figures",
    "table",
    "bars",
    "compare",
    "pair",
    "details",
    "figure",
}
QUESTION_TYPES = {"choice", "verdict", "text"}
SIZE_BUDGET = 1_000_000

TEMPLATE_MARKER = '<script id="report-data" type="application/json">'
PLACEHOLDER = TEMPLATE_MARKER + "null</script>"


def fail(message: str) -> None:
    print(f"INVALID: {message}", file=sys.stderr)
    sys.exit(1)


def check(report: object, where: str = "(root)") -> None:
    if not isinstance(report, dict):
        fail(f"{where}: expected an object")
    for key in ("lang", "title", "summary", "sections"):
        if key not in report:
            fail(f"{where}: missing required field '{key}'")
    for key in ("lang", "title"):
        if not isinstance(report[key], str) or not report[key]:
            fail(f"{where}.{key}: expected a non-empty string")
    if not isinstance(report["summary"], list) or not all(
        isinstance(p, str) for p in report["summary"]
    ):
        fail(f"{where}.summary: expected an array of strings")
    sections = report["sections"]
    if not isinstance(sections, list):
        fail(f"{where}.sections: expected an array")
    for i, section in enumerate(sections):
        s = f"{where}.sections[{i}]"
        if not isinstance(section, dict) or not isinstance(section.get("heading"), str):
            fail(f"{s}: expected an object with a 'heading' string")
        blocks = section.get("blocks", [])
        if not isinstance(blocks, list):
            fail(f"{s}.blocks: expected an array")
        for j, block in enumerate(blocks):
            b = f"{s}.blocks[{j}]"
            if not isinstance(block, dict) or block.get("type") not in BLOCK_TYPES:
                fail(f"{b}: 'type' must be one of {sorted(BLOCK_TYPES)}")
    review = report.get("review")
    if review is not None:
        if not isinstance(review, dict) or not isinstance(review.get("questions"), list):
            fail(f"{where}.review: expected an object with a 'questions' array")
        for i, question in enumerate(review["questions"]):
            q = f"{where}.review.questions[{i}]"
            if not isinstance(question, dict) or question.get("type") not in QUESTION_TYPES:
                fail(f"{q}: 'type' must be one of {sorted(QUESTION_TYPES)}")
            if not isinstance(question.get("id"), str) or not question["id"].isascii():
                fail(f"{q}.id: expected an ASCII string (it becomes the form field name)")


def main() -> None:
    if len(sys.argv) != 2:
        print("usage: build.py DIR", file=sys.stderr)
        sys.exit(2)
    skill_dir = Path(__file__).resolve().parent.parent
    directory = Path(sys.argv[1])
    json_path = directory / "report.json"

    try:
        report_text = json_path.read_text(encoding="utf-8")
    except OSError as error:
        fail(f"cannot read {json_path}: {error}")
    try:
        report = json.loads(report_text)
    except json.JSONDecodeError as error:
        fail(f"{json_path}: {error.msg} at line {error.lineno} column {error.colno}")
    check(report)

    template_path = skill_dir / "assets" / "report-template.html"
    try:
        template = template_path.read_text(encoding="utf-8")
    except OSError as error:
        fail(f"cannot read template {template_path}: {error}")

    # "</" inside a JSON string would close the script tag; "\/" is valid JSON.
    payload = report_text.replace("</", "<\\/")
    tag = f"{TEMPLATE_MARKER}{payload}</script>"
    if PLACEHOLDER in template:
        template = template.replace(PLACEHOLDER, tag)
    elif "<body" in template:
        marker = template[template.index("<body") :]
        end = marker.index(">") + 1
        at = template.index("<body") + end
        template = template[:at] + tag + template[at:]
    else:
        fail("template has neither the placeholder nor a <body> tag")

    html = template
    out = directory / "index.html"
    out.write_text(html, encoding="utf-8")
    size = out.stat().st_size
    print(f"OK: {out} ({size} bytes)")
    if size > SIZE_BUDGET:
        print(
            f"WARNING: {size} bytes exceeds the 1 MB budget; shrink raster images or trim prose",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
