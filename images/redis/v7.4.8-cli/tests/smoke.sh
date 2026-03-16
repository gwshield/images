#!/usr/bin/env bash
# =============================================================================
# Smoke tests — gwshield-redis v7.4.8 (cli profile)
# =============================================================================
# Usage: ./smoke.sh <image-ref>
#
# Tests:
#   1. redis-cli --version responds
#   2. redis-cli --help exits cleanly
#   3. No shell in runtime layer
#   4. Runs as nonroot UID 65532
#   5. Can PING a live gwshield-redis:v7.4.8 server via docker network
#   6. Can SET / GET a key against the live server
#   7. Server binary NOT present in cli image
# =============================================================================
set -euo pipefail

IMAGE="${1:?Usage: $0 <image-ref>}"
SERVER_IMAGE="${2:-ghcr.io/relicfrog/gwshield-redis:v7.4.8}"
PASS=0
FAIL=0
SERVER_CONTAINER=""
NET=""

_pass() { echo "[PASS] $*"; PASS=$((PASS + 1)); }
_fail() { echo "[FAIL] $*"; FAIL=$((FAIL + 1)); }

cleanup() {
  [[ -n "${SERVER_CONTAINER}" ]] && docker rm -f "${SERVER_CONTAINER}" >/dev/null 2>&1 || true
  [[ -n "${NET}"              ]] && docker network rm "${NET}"          >/dev/null 2>&1 || true
}
trap cleanup EXIT

NET=$(docker network create "smoke-redis-cli-$$" 2>/dev/null)

# ---------------------------------------------------------------------------
# Test 1: redis-cli --version responds
# ---------------------------------------------------------------------------
if docker run --rm "${IMAGE}" --version 2>&1 | grep -q 'Redis CLI\|redis-cli'; then
  _pass "redis-cli --version responds"
else
  _fail "redis-cli --version did not respond or unexpected output"
fi

# ---------------------------------------------------------------------------
# Test 2: redis-cli --help exits cleanly (exit 0 with usage output)
# ---------------------------------------------------------------------------
if docker run --rm "${IMAGE}" --help 2>&1 | grep -qi 'usage\|options\|host'; then
  _pass "redis-cli --help exits cleanly with usage output"
else
  _fail "redis-cli --help did not produce expected usage output"
fi

# ---------------------------------------------------------------------------
# Test 3: no shell in runtime layer
# ---------------------------------------------------------------------------
if docker run --rm --entrypoint /bin/sh "${IMAGE}" -c 'echo shell' >/dev/null 2>&1; then
  _fail "shell present in runtime layer (expected none)"
else
  _pass "no shell in runtime layer"
fi

# ---------------------------------------------------------------------------
# Test 4: image configured as nonroot UID 65532
# ---------------------------------------------------------------------------
actual_uid=$(docker inspect --format='{{.Config.User}}' "${IMAGE}" 2>/dev/null || true)
if [[ "${actual_uid}" == "65532:65532" ]]; then
  _pass "image configured as nonroot UID 65532"
else
  _fail "unexpected user config: '${actual_uid}' (expected 65532:65532)"
fi

# ---------------------------------------------------------------------------
# Test 5 + 6: start a gwshield-redis server and use the cli image to talk to it
# ---------------------------------------------------------------------------
SERVER_CONTAINER=$(docker run -d \
    --network "${NET}" \
    --name "redis-smoke-server-$$" \
    -v "${PWD}/images/redis/v7.4.8/configs/redis.conf:/etc/redis/redis.conf:ro" \
    "${SERVER_IMAGE}")

sleep 2

# PING
if docker run --rm \
    --network "${NET}" \
    "${IMAGE}" \
    -h "redis-smoke-server-$$" -p 6379 ping 2>/dev/null | grep -q 'PONG'; then
  _pass "PING via cli image returns PONG"
else
  _fail "PING via cli image did not return PONG"
fi

# SET / GET round-trip
set_out=$(docker run --rm \
    --network "${NET}" \
    "${IMAGE}" \
    -h "redis-smoke-server-$$" -p 6379 SET smoke-key smoke-value 2>/dev/null || true)
get_out=$(docker run --rm \
    --network "${NET}" \
    "${IMAGE}" \
    -h "redis-smoke-server-$$" -p 6379 GET smoke-key 2>/dev/null || true)

if echo "${set_out}" | grep -q 'OK' && echo "${get_out}" | grep -q 'smoke-value'; then
  _pass "SET/GET round-trip succeeds"
else
  _fail "SET/GET round-trip failed — SET: '${set_out}' GET: '${get_out}'"
fi

# ---------------------------------------------------------------------------
# Test 7: redis-server binary NOT present in the cli image
# ---------------------------------------------------------------------------
if docker run --rm --entrypoint /usr/local/bin/redis-server "${IMAGE}" --version >/dev/null 2>&1; then
  _fail "redis-server binary found in cli image (should not be present)"
else
  _pass "redis-server binary NOT present in cli image"
fi

# ---------------------------------------------------------------------------
# Test 8: gwshield-init banner appears on startup
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
