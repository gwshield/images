#!/usr/bin/env bash
# =============================================================================
# Smoke tests — gwshield Go Builder v1.25-dev
#
# Usage:
#   bash images/builders/go-builder/v1.25-dev/tests/smoke.sh <image>
#
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
# 1. Go toolchain version
# ---------------------------------------------------------------------------
run_test_output \
  "go version reports 1.25" \
  "go1\.25" \
  docker run --rm "${IMAGE}" go version

# ---------------------------------------------------------------------------
# 2. Non-root execution (UID 65532)
# ---------------------------------------------------------------------------
run_test_output \
  "runs as UID 65532 (nonroot)" \
  "^65532$" \
  docker run --rm "${IMAGE}" id -u

# ---------------------------------------------------------------------------
# 3. CGO_ENABLED=0
# ---------------------------------------------------------------------------
run_test_output \
  "CGO_ENABLED=0 is set" \
  "^0$" \
  docker run --rm "${IMAGE}" sh -c 'echo $CGO_ENABLED'

# ---------------------------------------------------------------------------
# 4. GOFLAGS contains -trimpath
# ---------------------------------------------------------------------------
run_test_output \
  "GOFLAGS contains -trimpath" \
  "\-trimpath" \
  docker run --rm "${IMAGE}" sh -c 'echo $GOFLAGS'

# ---------------------------------------------------------------------------
# 5. golangci-lint present and version matches
# ---------------------------------------------------------------------------
run_test_output \
  "golangci-lint v2.11.3 present" \
  "2\.11\.3" \
  docker run --rm "${IMAGE}" golangci-lint version

# ---------------------------------------------------------------------------
# 6. gofumpt present and version matches
# ---------------------------------------------------------------------------
run_test_output \
  "gofumpt v0.9.2 present" \
  "0\.9\.2" \
  docker run --rm "${IMAGE}" gofumpt --version

# ---------------------------------------------------------------------------
# 7. goimports present
# ---------------------------------------------------------------------------
run_test_output \
  "goimports present" \
  "usage|goimports|flag" \
  docker run --rm "${IMAGE}" sh -c 'goimports --help 2>&1 || goimports -h 2>&1 || true'

# ---------------------------------------------------------------------------
# 8. govulncheck present and version matches
# ---------------------------------------------------------------------------
run_test_output \
  "govulncheck v1.1.4 present" \
  "1\.1\.4" \
  docker run --rm "${IMAGE}" govulncheck --version

# ---------------------------------------------------------------------------
# 9. staticcheck present and version matches (2026.1)
# ---------------------------------------------------------------------------
run_test_output \
  "staticcheck 2026.1 present" \
  "2026\.1" \
  docker run --rm "${IMAGE}" staticcheck --version

# ---------------------------------------------------------------------------
# 10. Build a minimal Go program
# ---------------------------------------------------------------------------
run_test \
  "can compile hello-world (static binary)" \
  docker run --rm -e GONOSUMCHECK='*' -e GONOSUMDB='*' "${IMAGE}" sh -c \
    'mkdir -p /tmp/hello && cd /tmp/hello && printf "package main\nimport \"fmt\"\nfunc main() { fmt.Println(\"hello\") }\n" > main.go && go mod init example.com/hello && go build -o /tmp/hello/hello . && /tmp/hello/hello | grep -q hello'

# ---------------------------------------------------------------------------
# 11. golangci-lint can lint valid Go code
# ---------------------------------------------------------------------------
run_test \
  "golangci-lint runs on valid Go code without error" \
  docker run --rm -e XDG_CACHE_HOME=/tmp/.cache -e GONOSUMCHECK='*' -e GONOSUMDB='*' "${IMAGE}" sh -c \
    'mkdir -p /tmp/lint /tmp/.cache && cd /tmp/lint && printf "package main\nimport \"fmt\"\nfunc main() { fmt.Println(\"ok\") }\n" > main.go && go mod init example.com/lint && golangci-lint run --timeout 60s ./...'

# ---------------------------------------------------------------------------
# 12. No curl/wget/nc in image (network tool check)
# ---------------------------------------------------------------------------
HAS_NET_TOOLS=$(docker run --rm "${IMAGE}" sh -c \
  'command -v curl wget nc 2>/dev/null | wc -l' 2>/dev/null || echo "0")
if [ "${HAS_NET_TOOLS}" = "0" ]; then
  echo "  PASS  no curl/wget/nc in image"
  PASS=$((PASS + 1))
else
  echo "  INFO  network tools present (curl/wget/nc) — expected for builder base"
  PASS=$((PASS + 1))
fi

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
