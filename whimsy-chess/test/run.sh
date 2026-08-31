#!/usr/bin/env bash
# End-to-end test: drive the REAL maestro.html in headless Chrome, call its own
# buildWorld(), push the result through WorldKit, and check what comes out.
#
# This is the only way to test the real producer — buildWorld() lives inside the
# page and depends on the DOM, so it can't be required from Node. The harness is
# a temporary copy of maestro.html with test/worldkit.assert.js appended; it is
# removed on exit, so nothing duplicated is ever left in the repo.
#
#   ./test/run.sh          # exits non-zero if any assertion fails
#
# By Manny Glover.
set -uo pipefail
cd "$(dirname "$0")/.."

CHROME=""
for c in google-chrome chromium chromium-browser google-chrome-stable; do
  command -v "$c" >/dev/null 2>&1 && { CHROME="$c"; break; }
done
[ -z "$CHROME" ] && { echo "SKIP: no Chrome/Chromium found — this test needs a headless browser."; exit 0; }

HARNESS="__worldkit_harness.html"
trap 'rm -f "$HARNESS"' EXIT

python3 - "$HARNESS" <<'PY'
import sys
harness = sys.argv[1]
page = open('maestro.html').read()
asserts = open('test/worldkit.assert.js').read()
inject = '<pre id="TESTOUT">pending</pre>\n<script>\n' + asserts + '\n</script>\n'
if '</body>' not in page:
    sys.exit('maestro.html has no </body> to inject into')
open(harness, 'w').write(page.replace('</body>', inject + '</body>'))
PY

timeout 120 "$CHROME" --headless=new --disable-gpu --no-sandbox \
  --virtual-time-budget=20000 --dump-dom "file://$PWD/$HARNESS" 2>/dev/null \
| python3 -c '
import sys, re, json
dom = sys.stdin.read()
m = re.search(r"@@(.*?)@@", dom, re.S)
if not m:
    print("FAIL: the harness produced no output — maestro.html may have thrown on load.")
    print(dom[:1200])
    sys.exit(1)
R = json.loads(m.group(1))
ok, fail = R.get("ok", []), R.get("fail", [])
for k in ok:   print("  ok    " + k)
for k in fail: print("  FAIL  " + k)
if "stack" in R: print("\n  " + R["stack"])
print()
for k in ("meta", "plies", "land", "water", "waterKinds", "roles", "mc", "rb", "stem"):
    if k in R: print("  " + k + ": " + json.dumps(R[k]))
print()
print(("%d passing" % len(ok)) + (", %d FAILING" % len(fail) if fail else ""))
sys.exit(1 if fail else 0)
'
