#!/usr/bin/env bash
# =============================================================================
# Smoke tests — gwshield-redis v7.4.8 (cluster profile)
# =============================================================================
set -euo pipefail

IMAGE="${1:?Usage: $0 <image-ref>}"
PASS=0
FAIL=0
CONTAINER=""

_pass() { echo "[PASS] $*"; PASS=$((PASS + 1)); }
_fail() { echo "[FAIL] $*"; FAIL=$((FAIL + 1)); }

cleanup() {
  if [[ -n "${CONTAINER}" ]]; then
    docker rm -f "${CONTAINER}" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

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
# Test 4: cluster bus port 16379 exposed in image metadata
# ---------------------------------------------------------------------------
if docker inspect "${IMAGE}" 2>/dev/null | grep -q '"16379/tcp"'; then
  _pass "cluster bus port 16379/tcp exposed in image metadata"
else
  _fail "cluster bus port 16379/tcp NOT exposed in image metadata"
fi

# ---------------------------------------------------------------------------
# Test 5: single-node cluster starts (cluster-enabled yes but no peers)
# Redis in cluster mode with no peers still starts — it waits for CLUSTER MEET.
# We check it binds and responds to PING.
# ---------------------------------------------------------------------------
CONTAINER=$(docker run -d \
    -v "${PWD}/images/redis/v7.4.8-cluster/configs/redis.conf:/etc/redis/redis.conf:ro" \
    -p 16380:6379 \
    "${IMAGE}")

sleep 2

if docker run --rm --network host redis:7-alpine redis-cli -p 16380 ping 2>/dev/null | grep -q 'PONG'; then
  _pass "redis-server (cluster) accepts PING on single-node startup"
else
  _fail "redis-server (cluster) did not respond to PING"
fi

# ---------------------------------------------------------------------------
# Test 6: cluster-enabled reported by INFO
# ---------------------------------------------------------------------------
if docker run --rm --network host redis:7-alpine redis-cli -p 16380 INFO server 2>/dev/null | grep -q 'redis_mode:cluster'; then
  _pass "INFO server reports redis_mode:cluster"
else
  _fail "INFO server does NOT report redis_mode:cluster"
fi

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
