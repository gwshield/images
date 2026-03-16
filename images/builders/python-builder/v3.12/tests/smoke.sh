#!/usr/bin/env bash
# =============================================================================
# Smoke tests — gwshield Python Builder v3.12
#
# Usage: bash images/builders/python-builder/v3.12/tests/smoke.sh <image>
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

run_test_output "python version reports 3.12"     "3\.12"  docker run --rm "${IMAGE}" python --version
run_test_output "runs as UID 65532 (nonroot)"     "^65532$" docker run --rm "${IMAGE}" id -u
run_test_output "PYTHONDONTWRITEBYTECODE=1 is set" "^1$"   docker run --rm "${IMAGE}" sh -c 'echo $PYTHONDONTWRITEBYTECODE'
run_test_output "PYTHONUNBUFFERED=1 is set"        "^1$"   docker run --rm "${IMAGE}" sh -c 'echo $PYTHONUNBUFFERED'
run_test_output "pip is available"                "pip [0-9]" docker run --rm "${IMAGE}" pip --version
run_test        "pip install works (six)"          docker run --rm -e HOME=/tmp "${IMAGE}" sh -c \
  'pip install --no-cache-dir --quiet six && python -c "import six; print(six.__version__)"'
run_test_output "python executes hello-world script" "gwshield-python-smoke-ok" \
  docker run --rm "${IMAGE}" python -c 'print("gwshield-python-smoke-ok")'
run_test        "/build is writable by nonroot"    docker run --rm "${IMAGE}" sh -c 'touch /build/.smoke_test && rm /build/.smoke_test'
run_test        "/app is writable by nonroot"      docker run --rm "${IMAGE}" sh -c 'touch /app/.smoke_test && rm /app/.smoke_test'

HAS_NET_TOOLS=$(docker run --rm "${IMAGE}" sh -c 'command -v curl wget nc 2>/dev/null | wc -l' 2>/dev/null || echo "0")
if [ "${HAS_NET_TOOLS}" = "0" ]; then
  echo "  PASS  no curl/wget/nc in image"
  PASS=$((PASS + 1))
else
  echo "  INFO  network tools present — expected for builder base"
  PASS=$((PASS + 1))
fi

run_test_output "PIP_NO_CACHE_DIR=1 is set" "^1$" docker run --rm "${IMAGE}" sh -c 'echo $PIP_NO_CACHE_DIR'

if docker run --rm "${IMAGE}" sh -c 'echo shell_present' >/dev/null 2>&1; then
  echo "  PASS  shell present (/bin/sh) — expected for builder images"
  PASS=$((PASS + 1))
else
  echo "  FAIL  no shell found — builder images must retain /bin/sh"
  FAIL=$((FAIL + 1))
fi

echo "=============================================="
echo "Results: ${PASS} passed, ${FAIL} failed"
echo ""
[ "${FAIL}" -gt 0 ] && exit 1
exit 0
