#!/usr/bin/env bash
set -euo pipefail
experiment=$(cd -- "$(dirname -- "$0")" && pwd)
project=$(cd -- "$experiment/../.." && pwd)
build="${CONVERGENCE_BUILD_DIR:-$project/build-convergence}"
cmake -S "$project" -B "$build" -DCMAKE_BUILD_TYPE=Release
cmake --build "$build" --target convergence_benchmark convergence_tests -j 2
ctest --test-dir "$build" -R '^convergence_checks$' --output-on-failure
python3 - "$build" "$experiment" <<'PYMETA'
import datetime, pathlib, platform, subprocess, sys
build, experiment = map(pathlib.Path, sys.argv[1:])
cache = dict(line.split('=', 1) for line in (build/'CMakeCache.txt').read_text().splitlines() if '=' in line and not line.startswith('//'))
compiler = cache['CMAKE_CXX_COMPILER:FILEPATH']
text = f"Captured: {datetime.datetime.now().astimezone().isoformat()}\n{platform.platform()}\n"
text += subprocess.check_output([compiler, '--version'], text=True)
text += '\nRelease flags: '+cache.get('CMAKE_CXX_FLAGS_RELEASE:STRING', 'unknown')
text += '\nSingle-threaded solvers; steady_clock microseconds; one warmup, 21 timed repetitions.\n'
text += 'No CPU affinity/frequency pinning or exclusive CPU reservation.\n'
(experiment/'environment.txt').write_text(text)
PYMETA
"$build/convergence_benchmark" "$experiment"
python3 "$experiment/plot.py"
python3 "$experiment/make_page.py"
