#!/usr/bin/env bash
# =============================================================================
# Smoke tests — gwshield-postgres v17.9 (cli profile)
# =============================================================================
set -euo pipefail

IMAGE="${1:?Usage: $0 <image-ref>}"
PASS=0
FAIL=0
CONTAINER=""
NET=""

_pass() { echo "[PASS] $*"; PASS=$((PASS + 1)); }
_fail() { echo "[FAIL] $*"; FAIL=$((FAIL + 1)); }

cleanup() {
  [[ -n "${CONTAINER}" ]] && docker rm -f "${CONTAINER}" >/dev/null 2>&1 || true
  [[ -n "${NET}"       ]] && docker network rm "${NET}"   >/dev/null 2>&1 || true
}
trap cleanup EXIT

NET=$(docker network create "smoke-postgres17-cli-$$" 2>/dev/null)

# ---------------------------------------------------------------------------
# Test 1: psql --version responds
# ---------------------------------------------------------------------------
if docker run --rm --entrypoint /usr/local/bin/psql "${IMAGE}" --version 2>&1 | grep -q 'psql.*17'; then
  _pass "psql --version responds (v17)"
else
  _fail "psql --version did not respond with v17"
fi

# ---------------------------------------------------------------------------
# Test 2: no shell in runtime layer
# ---------------------------------------------------------------------------
if docker run --rm --entrypoint /bin/sh "${IMAGE}" -c 'echo shell' >/dev/null 2>&1; then
  _fail "shell present in runtime layer (expected none)"
else
  _pass "no shell in runtime layer"
fi

# ---------------------------------------------------------------------------
# Test 3: runs as nonroot (UID 65532)
# ---------------------------------------------------------------------------
actual_uid=$(docker inspect --format='{{.Config.User}}' "${IMAGE}" 2>/dev/null || true)
if [[ "${actual_uid}" == "65532:65532" ]]; then
  _pass "image configured as nonroot UID 65532"
else
  _fail "unexpected user config: '${actual_uid}' (expected 65532:65532)"
fi

# ---------------------------------------------------------------------------
# Test 4: psql connects to a live postgres:17-alpine server
# ---------------------------------------------------------------------------
CONTAINER=$(docker run -d \
    --network "${NET}" \
    --name "postgres17-smoke-cli-$$" \
    -e POSTGRES_PASSWORD=gwshield_test \
    -e POSTGRES_USER=postgres \
    postgres:17-alpine)

sleep 8

if docker run --rm \
    --network "${NET}" \
    --entrypoint /usr/local/bin/psql \
    -e PGPASSWORD=gwshield_test \
    "${IMAGE}" \
    -h "postgres17-smoke-cli-$$" -p 5432 -U postgres -d postgres \
    -c 'SELECT version();' 2>&1 | grep -q 'PostgreSQL 17'; then
  _pass "psql connects and queries server (v17)"
else
  echo "[DEBUG] server logs:"; docker logs "postgres17-smoke-cli-$$" 2>&1 | tail -20
  _fail "psql could not connect or query server"
fi

# ---------------------------------------------------------------------------
# Test 5: no server binary in cli image
# ---------------------------------------------------------------------------
if docker run --rm --entrypoint /usr/local/bin/postgres "${IMAGE}" --version >/dev/null 2>&1; then
  _fail "postgres server binary present in cli image (expected none)"
else
  _pass "no postgres server binary in cli image"
fi

# ---------------------------------------------------------------------------
# Test 6: gwshield-init banner appears on startup
# ---------------------------------------------------------------------------
banner_out=$(docker run --rm "${IMAGE}" --version 2>&1 || true)
if echo "${banner_out}" | grep -qi 'gwshield\|gatewarden'; then
  _pass "gwshield-init banner present on startup"
else
  _fail "gwshield-init banner NOT found in startup output"
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
echo "Results: ${PASS} passed, ${FAIL} failed"
[[ "${FAIL}" -eq 0 ]] || exit 1
