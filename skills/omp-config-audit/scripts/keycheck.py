#!/usr/bin/env python3
"""Key-level validation for omp config layers against the installed schema.

Usage: keycheck.py <schema.json> <layer.yaml> [<layer.yaml> ...]

Prints, per layer, the leaf keys that are absent from the schema after excluding
children of record-typed parents (dynamically named, schema-invisible), and exits
non-zero if any stale key remains. Exits 0 when every key is valid.

schema.json is `omp config list --json` output. Record-typed parents are detected
from the schema's own "type": "record" entries; unknown deep paths under a parent
that is itself unknown are reported as stale (that is a real finding).
"""

import json
import re
import sys

import yaml

RECORD_TYPES = {"record", "map", "object"}


def flatten(node, prefix=""):
    out = set()
    if isinstance(node, dict):
        if not node:
            out.add(prefix[:-1])
        for k, v in node.items():
            out |= flatten(v, f"{prefix}{k}.")
    elif isinstance(node, list):
        if prefix:
            out.add(prefix[:-1] + "[]")
    else:
        out.add(prefix[:-1])
    return out


def main(argv):
    if len(argv) < 3:
        print(__doc__, file=sys.stderr)
        return 2
    schema = json.load(open(argv[1]))
    schema_keys = set(schema.keys())

    def parent_is_dynamic(key):
        parts = key.split(".")
        for i in range(len(parts) - 1, 0, -1):
            anc = ".".join(parts[:i])
            if anc in schema:
                return schema[anc].get("type", "") in RECORD_TYPES
        return False

    def is_section_header(key):
        # A bare key with schema children (e.g. `mcp: {}` with `mcp.enableProjectConfig`
        # in schema) is a valid empty section, not a stale key.
        return any(k.startswith(key + ".") for k in schema_keys)

    stale_total = 0
    for path in argv[2:]:
        name = path.rsplit("/", 1)[-1]
        data = yaml.safe_load(open(path)) or {}
        keys = flatten(data)
        leaf = {k for k in keys if not k.endswith("[]")}
        lists = {k[:-2] for k in keys if k.endswith("[]")}
        candidates = leaf | lists
        stale = sorted(
            k
            for k in candidates
            if k not in schema_keys
            and not parent_is_dynamic(k)
            and not is_section_header(k)
        )
        stale_total += len(stale)
        print(f"[{name}] {len(candidates)} keys -> stale: {len(stale)}")
        for s in stale:
            print(f"  STALE? {s}")
    print(f"TOTAL stale: {stale_total}")
    return 1 if stale_total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
