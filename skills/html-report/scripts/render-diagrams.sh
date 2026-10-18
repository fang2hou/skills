#!/usr/bin/env bash
# Render <pre class="mermaid"> blocks in an HTML report to inline SVG with Pele.
# https://pele.run — Mermaid syntax in, themeable SVG out, at build time.
#
# Usage:
#   bash render-diagrams.sh <index.html>            render every block in place
#   bash render-diagrams.sh <index.html> --check    validate only, write nothing
#
# A block looks like:
#   <pre class="mermaid" data-caption="Request path">flowchart LR
#     A[Browser] --> B[Cache]</pre>
#
# data-caption adds a figcaption; data-wide adds the .wide 1080 px breakout.
#
# The rendered block becomes <figure class="diagram">…svg…<figcaption>…</figcaption></figure>.
# Exit codes: 0 ok · 1 usage or file missing · 2 node/npm missing · 3 pele install failed · 4 diagram errors.
set -euo pipefail

if [ $# -lt 1 ] || [ ! -f "$1" ]; then
  echo "usage: bash render-diagrams.sh <index.html> [--check]" >&2
  exit 1
fi
target=$(cd "$(dirname "$1")" && pwd)/$(basename "$1")
check=${2:-}

command -v node >/dev/null 2>&1 || { echo "node >= 20 is required (https://nodejs.org)" >&2; exit 2; }
node_major=$(node -p 'process.versions.node.split(".")[0]')
if [ "$node_major" -lt 20 ]; then
  echo "node >= 20 required, found $(node --version)" >&2
  exit 2
fi

# Pele is installed once into a shared cache; bare-specifier resolution needs cwd = cache.
cache="${XDG_CACHE_HOME:-$HOME/.cache}/html-report/pele"
if [ ! -f "$cache/node_modules/pele/package.json" ]; then
  command -v npm >/dev/null 2>&1 || { echo "npm is required to install pele" >&2; exit 2; }
  echo "installing pele into $cache ..." >&2
  mkdir -p "$cache"
  npm install --prefix "$cache" pele@1 --no-audit --no-fund --loglevel=error >&2 || {
    echo "npm install failed — check the network, or retry" >&2
    exit 3
  }
fi

cd "$cache"
node --input-type=module - "$target" "$check" <<'NODE'
import { readFileSync, writeFileSync } from 'node:fs';
import { PeleError, render } from 'pele';

const [file, flag] = process.argv.slice(2);
const check = flag === '--check';
const html = readFileSync(file, 'utf8');

// The pre block holds HTML text, so entities must become Mermaid source again.
const decode = (s) =>
  s
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#0?39;|&apos;/g, "'")
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/^\n+/, '')
    .replace(/\s+$/, '');

const re = /<pre class="mermaid"([^>]*)>([\s\S]*?)<\/pre>/g;
let out = '';
let last = 0;
let count = 0;
let bytes = 0;
let failed = 0;
let m;
while ((m = re.exec(html))) {
  count++;
  const attrs = m[1];
  const captionText = /data-caption="([^"]*)"/.exec(attrs)?.[1];
  const caption = captionText ? `<figcaption>${captionText}</figcaption>` : '';
  const wide = /data-wide/.test(attrs) ? ' wide' : '';
  try {
    const { svg } = render(decode(m[2]), {
      idPrefix: `d${count}`,
      maxWidth: 1040,
      padding: 4,
    });
    bytes += svg.length;
    out +=
      html.slice(last, m.index) +
      `<figure class="diagram${wide}">${svg}${caption}</figure>`;
    last = m.index + m[0].length;
  } catch (e) {
    failed++;
    console.error(`diagram ${count}:`);
    if (e instanceof PeleError) {
      const at = e.line ? ` (line ${e.line}, column ${e.column})` : '';
      console.error(`  [${e.code}] ${e.message}${at}`);
      if (e.snippet) console.error(e.snippet.split('\n').map((l) => `  | ${l}`).join('\n'));
    } else {
      console.error(`  ${e.message}`);
    }
  }
}

if (failed) {
  console.error(`${failed} of ${count} diagram(s) failed — fix the source and re-run.`);
  process.exit(4);
}
if (!count) {
  console.log('no <pre class="mermaid"> blocks found; file unchanged');
  process.exit(0);
}
if (check) {
  console.log(`${count} diagram(s) valid`);
  process.exit(0);
}
writeFileSync(file, out + html.slice(last));
console.log(`rendered ${count} diagram(s), ${(bytes / 1024).toFixed(1)} KB of inline SVG`);
NODE
