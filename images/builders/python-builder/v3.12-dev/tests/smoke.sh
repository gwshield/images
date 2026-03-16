#!/usr/bin/env bash
# =============================================================================
# Smoke tests — gwshield Python Builder v3.12-dev
#
# Usage: bash images/builders/python-builder/v3.12-dev/tests/smoke.sh <image>
# Exit code 0 = all tests passed, 1 = one or more failed.
# =============================================================================
set -euo pipefail

IMAGE="${1:?Usage: $0 <image>}"
PASS=0
FAIL=0

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

run_test_output "python version reports 3.12"      "3\.12"   docker run --rm "${IMAGE}" python --version
run_test_output "runs as UID 65532 (nonroot)"      "^65532$" docker run --rm "${IMAGE}" id -u
run_test_output "PYTHONDONTWRITEBYTECODE=1 is set"  "^1$"    docker run --rm "${IMAGE}" sh -c 'echo $PYTHONDONTWRITEBYTECODE'
run_test_output "PYTHONUNBUFFERED=1 is set"         "^1$"    docker run --rm "${IMAGE}" sh -c 'echo $PYTHONUNBUFFERED'
run_test_output "ruff 0.15.5 present"              "0\.15\.5"  docker run --rm "${IMAGE}" ruff --version
run_test_output "mypy 1.19.1 present"              "1\.19\.1"  docker run --rm "${IMAGE}" mypy --version
run_test_output "pytest 9.0.2 present"             "9\.0\.2"   docker run --rm "${IMAGE}" pytest --version
run_test_output "pip-audit 2.10.0 present"         "2\.10\.0"  docker run --rm "${IMAGE}" pip-audit --version
run_test_output "black 26.3.0 present"             "26\.3\.0"  docker run --rm "${IMAGE}" black --version
run_test_output "isort 8.0.1 present"              "8\.0\.1"   docker run --rm "${IMAGE}" isort --version-number

run_test "ruff lints valid Python without error" \
  docker run --rm -e HOME=/tmp "${IMAGE}" sh -c \
    'mkdir -p /tmp/lint && printf "def hello():\n    print(\"ok\")\n\nhello()\n" > /tmp/lint/main.py && ruff check /tmp/lint/main.py'

run_test "pytest runs a trivial test and passes" \
  docker run --rm -e HOME=/tmp "${IMAGE}" sh -c \
    'mkdir -p /tmp/test && printf "def test_ok():\n    assert 1 + 1 == 2\n" > /tmp/test/test_smoke.py && pytest /tmp/test/test_smoke.py -q'

echo "=============================================="
echo "Results: ${PASS} passed, ${FAIL} failed"
echo ""
[ "${FAIL}" -gt 0 ] && exit 1
exit 0
