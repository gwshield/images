#!/usr/bin/env bash
# =============================================================================
# Smoke tests — gwshield-postgres v15.13 (cli profile)
# =============================================================================
set -euo pipefail

IMAGE="${1:?Usage: $0 <image-ref>}"
PASS=0
FAIL=0
NET=""
SERVER_CONTAINER=""

_pass() { echo "[PASS] $*"; PASS=$((PASS + 1)); }
_fail() { echo "[FAIL] $*"; FAIL=$((FAIL + 1)); }

cleanup() {
  [[ -n "${SERVER_CONTAINER}" ]] && docker rm -f "${SERVER_CONTAINER}" >/dev/null 2>&1 || true
  [[ -n "${NET}"              ]] && docker network rm "${NET}"          >/dev/null 2>&1 || true
}
trap cleanup EXIT

# ---------------------------------------------------------------------------
# Test 1: psql --version responds (bypass gwshield-init wrapper)
# ---------------------------------------------------------------------------
if docker run --rm --entrypoint /usr/local/bin/psql "${IMAGE}" --version 2>&1 | grep -q 'psql'; then
  _pass "psql --version responds"
else
  _fail "psql --version did not respond"
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
# Test 4: no server binary in runtime layer
# ---------------------------------------------------------------------------
if docker run --rm --entrypoint /usr/local/bin/postgres "${IMAGE}" --version >/dev/null 2>&1; then
  _fail "postgres server binary found in cli image (expected absent)"
else
  _pass "no postgres server binary in cli runtime layer"
fi

# ---------------------------------------------------------------------------
# Test 5: no initdb in runtime layer
# ---------------------------------------------------------------------------
if docker run --rm --entrypoint /usr/local/bin/initdb "${IMAGE}" --version >/dev/null 2>&1; then
  _fail "initdb found in cli image (expected absent)"
else
  _pass "no initdb in cli runtime layer"
fi

# ---------------------------------------------------------------------------
# Test 6: psql connects to a live postgres server.
# Spin up postgres:15-alpine as server (handles initdb internally via
# POSTGRES_PASSWORD env). Then connect with psql from our hardened cli image.
# ---------------------------------------------------------------------------
NET=$(docker network create "smoke-postgres-cli-$$" 2>/dev/null)

SERVER_CONTAINER=$(docker run -d \
    --network "${NET}" \
    --name "postgres-cli-server-$$" \
    -e POSTGRES_PASSWORD=gwshield_test \
    -e POSTGRES_USER=postgres \
    postgres:15-alpine)

# Wait for postgres:15-alpine to finish initdb and start listening
sleep 8

if docker run --rm \
    --network "${NET}" \
    --entrypoint /usr/local/bin/psql \
    -e PGPASSWORD=gwshield_test \
    "${IMAGE}" \
    -h "postgres-cli-server-$$" -U postgres -d postgres -c 'SELECT version();' 2>&1 \
    | grep -q 'PostgreSQL'; then
  _pass "psql connects to postgres server and queries successfully"
else
  echo "[DEBUG] server container logs:"; docker logs "postgres-cli-server-$$" 2>&1 | tail -20
  _fail "psql could not connect to postgres server"
fi

# ---------------------------------------------------------------------------
# Test 7: gwshield-init banner appears on startup
# gwshield-init is the ENTRYPOINT — call with no --entrypoint override.
# It prints banner then exec's psql --help (CMD default).
# ---------------------------------------------------------------------------
banner_out=$(docker run --rm "${IMAGE}" 2>&1 || true)
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
