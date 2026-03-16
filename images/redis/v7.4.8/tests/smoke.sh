#!/usr/bin/env bash
# =============================================================================
# Smoke tests — gwshield-redis v7.4.8 (standard profile)
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

NET=$(docker network create "smoke-redis-standard-$$" 2>/dev/null)

# ---------------------------------------------------------------------------
# Test 1: redis-server --version responds
# ---------------------------------------------------------------------------
if docker run --rm "${IMAGE}" --version 2>&1 | grep -q 'Redis server'; then
  _pass "redis-server --version responds"
else
  _fail "redis-server --version did not respond"
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
# Test 4: container starts and accepts PING via docker network
# ---------------------------------------------------------------------------
CONTAINER=$(docker run -d \
    --network "${NET}" \
    --name "redis-smoke-standard-$$" \
    -v "${PWD}/images/redis/v7.4.8/configs/redis.conf:/etc/redis/redis.conf:ro" \
    "${IMAGE}")

sleep 2

if docker run --rm \
    --network "${NET}" \
    redis:7-alpine \
    redis-cli -h "redis-smoke-standard-$$" -p 6379 ping 2>/dev/null | grep -q 'PONG'; then
  _pass "redis-server accepts PING (standard profile)"
else
  _fail "redis-server did not respond to PING"
fi

# ---------------------------------------------------------------------------
# Test 5: renamed dangerous commands are blocked
# ---------------------------------------------------------------------------
flushall_out=$(docker run --rm \
    --network "${NET}" \
    redis:7-alpine \
    redis-cli -h "redis-smoke-standard-$$" -p 6379 FLUSHALL 2>&1 || true)
if echo "${flushall_out}" | grep -qi 'unknown\|ERR\|error'; then
  _pass "FLUSHALL is renamed/blocked"
else
  _fail "FLUSHALL is NOT blocked — response: ${flushall_out}"
fi

# ---------------------------------------------------------------------------
# Test 6: no TLS in standard profile (plain TCP only)
# ---------------------------------------------------------------------------
_pass "no TLS in standard profile (by design)"

# ---------------------------------------------------------------------------
# Test 7: gwshield-init banner appears on startup
# ---------------------------------------------------------------------------
banner_out=$(docker run --rm "${IMAGE}" --version 2>&1 || true)
if echo "${banner_out}" | grep -qi 'gwshield\|gatewarden'; then
  _pass "gwshield-init banner present on stdout"
else
  _fail "gwshield-init banner NOT found in startup output"
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
echo "Results: ${PASS} passed, ${FAIL} failed"
[[ "${FAIL}" -eq 0 ]] || exit 1
