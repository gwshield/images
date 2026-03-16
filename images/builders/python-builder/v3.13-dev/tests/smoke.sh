#!/usr/bin/env bash
# =============================================================================
# Smoke tests — gwshield Python Builder v3.13-dev
#
# Usage:
#   bash images/builders/python-builder/v3.13-dev/tests/smoke.sh <image>
#
# Runs against the local image tag passed as $1.
# Exit code 0 = all tests passed.
# Exit code 1 = one or more tests failed.
# =============================================================================
set -euo pipefail

IMAGE="${1:?Usage: $0 <image>}"
PASS=0
FAIL=0

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
run_test() {
  local desc="$1"; shift
  local out rc
  out=$("$@" 2>&1) && rc=0 || rc=$?
  if [ "${rc}" -eq 0 ]; then
    echo "  PASS  ${desc}"
    PASS=$((PASS + 1))
  else
    echo "  FAIL  ${desc}"
    echo "        output: ${out}"
    FAIL=$((FAIL + 1))
  fi
}

run_test_output() {
  local desc="$1"; local pattern="$2"; shift 2
  local out
  out=$("$@" 2>&1) || true
  if echo "${out}" | grep -qE "${pattern}"; then
    echo "  PASS  ${desc}"
    PASS=$((PASS + 1))
  else
    echo "  FAIL  ${desc} (expected pattern: ${pattern})"
    echo "        output: ${out}"
    FAIL=$((FAIL + 1))
  fi
}

echo ""
echo "Smoke tests: ${IMAGE}"
echo "=============================================="

# ---------------------------------------------------------------------------
# 1. Python version reports 3.13
# ---------------------------------------------------------------------------
run_test_output \
  "python version reports 3.13" \
  "3\.13" \
  docker run --rm "${IMAGE}" python --version

# ---------------------------------------------------------------------------
# 2. Non-root execution (UID 65532)
# ---------------------------------------------------------------------------
run_test_output \
  "runs as UID 65532 (nonroot)" \
  "^65532$" \
  docker run --rm "${IMAGE}" id -u

# ---------------------------------------------------------------------------
# 3. PYTHONDONTWRITEBYTECODE=1
# ---------------------------------------------------------------------------
run_test_output \
  "PYTHONDONTWRITEBYTECODE=1 is set" \
  "^1$" \
  docker run --rm "${IMAGE}" sh -c 'echo $PYTHONDONTWRITEBYTECODE'

# ---------------------------------------------------------------------------
# 4. PYTHONUNBUFFERED=1
# ---------------------------------------------------------------------------
run_test_output \
  "PYTHONUNBUFFERED=1 is set" \
  "^1$" \
  docker run --rm "${IMAGE}" sh -c 'echo $PYTHONUNBUFFERED'

# ---------------------------------------------------------------------------
# 5. ruff present and version matches
# ---------------------------------------------------------------------------
run_test_output \
  "ruff 0.15.5 present" \
  "0\.15\.5" \
  docker run --rm "${IMAGE}" ruff --version

# ---------------------------------------------------------------------------
# 6. mypy present and version matches
# ---------------------------------------------------------------------------
run_test_output \
  "mypy 1.19.1 present" \
  "1\.19\.1" \
  docker run --rm "${IMAGE}" mypy --version

# ---------------------------------------------------------------------------
# 7. pytest present and version matches
# ---------------------------------------------------------------------------
run_test_output \
  "pytest 9.0.2 present" \
  "9\.0\.2" \
  docker run --rm "${IMAGE}" pytest --version

# ---------------------------------------------------------------------------
# 8. pip-audit present and version matches
# ---------------------------------------------------------------------------
run_test_output \
  "pip-audit 2.10.0 present" \
  "2\.10\.0" \
  docker run --rm "${IMAGE}" pip-audit --version

# ---------------------------------------------------------------------------
# 9. black present and version matches
# ---------------------------------------------------------------------------
run_test_output \
  "black 26.3.0 present" \
  "26\.3\.0" \
  docker run --rm "${IMAGE}" black --version

# ---------------------------------------------------------------------------
# 10. isort present and version matches
# ---------------------------------------------------------------------------
run_test_output \
  "isort 8.0.1 present" \
  "8\.0\.1" \
  docker run --rm "${IMAGE}" isort --version-number

# ---------------------------------------------------------------------------
# 11. ruff can lint a trivial valid Python file
# ---------------------------------------------------------------------------
run_test \
  "ruff lints valid Python without error" \
  docker run --rm -e HOME=/tmp "${IMAGE}" sh -c \
    'mkdir -p /tmp/lint && printf "def hello():\n    print(\"ok\")\n\nhello()\n" > /tmp/lint/main.py && ruff check /tmp/lint/main.py'

# ---------------------------------------------------------------------------
# 12. pytest can run a trivial test
# ---------------------------------------------------------------------------
run_test \
  "pytest runs a trivial test and passes" \
  docker run --rm -e HOME=/tmp "${IMAGE}" sh -c \
    'mkdir -p /tmp/test && printf "def test_ok():\n    assert 1 + 1 == 2\n" > /tmp/test/test_smoke.py && pytest /tmp/test/test_smoke.py -q'

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo "=============================================="
echo "Results: ${PASS} passed, ${FAIL} failed"
echo ""

if [ "${FAIL}" -gt 0 ]; then
  exit 1
fi
exit 0
