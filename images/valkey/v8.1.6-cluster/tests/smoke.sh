#!/usr/bin/env bash
# =============================================================================
# Smoke tests — gwshield-valkey v8.1.6 (cluster profile)
# =============================================================================
#
# Coverage:
#   1.  valkey-server --version responds
#   2.  No shell in runtime layer
#   3.  Nonroot UID 65532
#   4.  gwshield-init banner present
#   5.  Cluster bus port 16379/tcp exposed in image metadata
#   6.  Server starts (single-node, waits for CLUSTER MEET)
#   7.  PING succeeds on single-node cluster startup
#   8.  CLUSTER INFO reports cluster_enabled:1
#   9.  cluster-enabled=yes confirmed via CLUSTER INFO
#  10.  Dangerous commands blocked
#  11.  valkey-server binary present at expected path
#  12.  gwshield-init binary present at expected path
#
# Exit code: 0 = all passed, 1 = one or more failed
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

NET=$(docker network create "smoke-valkey-cluster-$$" 2>/dev/null)

# ---------------------------------------------------------------------------
# Test 1: version output
# ---------------------------------------------------------------------------
ver_out=$(docker run --rm "${IMAGE}" --version 2>&1 || true)
if echo "${ver_out}" | grep -qiE 'valkey.*server|server.*v?8\.1'; then
  _pass "valkey-server --version: correct version string"
else
  _fail "valkey-server --version: unexpected — got: ${ver_out}"
fi

# ---------------------------------------------------------------------------
# Test 2: no shell
# ---------------------------------------------------------------------------
if docker run --rm --entrypoint /bin/sh "${IMAGE}" -c 'echo shell' >/dev/null 2>&1; then
  _fail "shell present in runtime layer"
else
  _pass "no shell in runtime layer"
fi

# ---------------------------------------------------------------------------
# Test 3: nonroot
# ---------------------------------------------------------------------------
actual_uid=$(docker inspect --format='{{.Config.User}}' "${IMAGE}" 2>/dev/null || true)
if [[ "${actual_uid}" == "65532:65532" ]]; then
  _pass "image configured as nonroot UID 65532:65532"
else
  _fail "unexpected user: '${actual_uid}'"
fi

# ---------------------------------------------------------------------------
# Test 4: gwshield-init banner
# ---------------------------------------------------------------------------
banner_out=$(docker run --rm "${IMAGE}" --version 2>&1 || true)
if echo "${banner_out}" | grep -qi 'gwshield\|gatewarden'; then
  _pass "gwshield-init banner present"
else
  _fail "gwshield-init banner NOT found"
fi

# ---------------------------------------------------------------------------
# Test 5: cluster bus port 16379 exposed in image metadata
# ---------------------------------------------------------------------------
if docker inspect "${IMAGE}" 2>/dev/null | grep -q '"16379/tcp"'; then
  _pass "cluster bus port 16379/tcp exposed in image metadata"
else
  _fail "cluster bus port 16379/tcp NOT exposed"
fi

# ---------------------------------------------------------------------------
# Test 6 + 7: single-node cluster starts and responds to PING
# ---------------------------------------------------------------------------
CONTAINER=$(docker run -d \
    --network "${NET}" \
    --name "valkey-smoke-cluster-$$" \
    -v "${PWD}/images/valkey/v8.1.6-cluster/configs/valkey.conf:/etc/valkey/valkey.conf:ro" \
    "${IMAGE}")

sleep 3

ping_out=$(docker run --rm --network "${NET}" \
    valkey/valkey:8-alpine \
    valkey-cli -h "valkey-smoke-cluster-$$" -p 6379 \
    PING 2>/dev/null || true)
if echo "${ping_out}" | grep -qi 'PONG'; then
  _pass "single-node cluster starts and accepts PING → PONG"
else
  echo "[DEBUG] server logs:"; docker logs "${CONTAINER}" 2>&1 | tail -10
  _fail "PING failed on single-node cluster — got: ${ping_out}"
fi

# ---------------------------------------------------------------------------
# Test 8 + 9: INFO cluster confirms cluster mode is enabled
# (CONFIG is renamed/blocked; INFO cluster is always available and returns
#  cluster_enabled:1 on any node running with cluster-enabled yes)
# ---------------------------------------------------------------------------
info_cluster=$(docker run --rm --network "${NET}" \
    valkey/valkey:8-alpine \
    valkey-cli -h "valkey-smoke-cluster-$$" -p 6379 \
    INFO cluster 2>/dev/null || true)
if grep -q 'cluster_enabled:1' <<< "${info_cluster}"; then
  _pass "INFO cluster reports cluster_enabled:1"
else
  _fail "INFO cluster does NOT report cluster_enabled:1 — got: ${info_cluster}"
fi
cluster_info=$(docker run --rm --network "${NET}" \
    valkey/valkey:8-alpine \
    valkey-cli -h "valkey-smoke-cluster-$$" -p 6379 \
    CLUSTER INFO 2>/dev/null || true)
if grep -qiE 'cluster_state:(ok|fail)' <<< "${cluster_info}"; then
  _pass "CLUSTER INFO reports cluster_state present (single-node fail expected)"
else
  _fail "CLUSTER INFO cluster_state missing — got: ${cluster_info}"
fi

# ---------------------------------------------------------------------------
# Test 10: dangerous commands blocked
# ---------------------------------------------------------------------------
flush_out=$(docker run --rm --network "${NET}" \
    valkey/valkey:8-alpine \
    valkey-cli -h "valkey-smoke-cluster-$$" -p 6379 \
    FLUSHALL 2>/dev/null || true)
if echo "${flush_out}" | grep -qiE 'unknown|ERR|error'; then
  _pass "FLUSHALL is renamed/blocked"
else
  _fail "FLUSHALL NOT blocked — response: ${flush_out}"
fi

# ---------------------------------------------------------------------------
# Test 11 + 12: binary presence via docker cp
# ---------------------------------------------------------------------------
id_out=$(docker create "${IMAGE}" 2>/dev/null)
if docker cp "${id_out}:/usr/local/bin/valkey-server" - >/dev/null 2>&1; then
  _pass "valkey-server binary present at /usr/local/bin/valkey-server"
else
  _fail "valkey-server binary NOT found"
fi
if docker cp "${id_out}:/usr/local/bin/gwshield-init" - >/dev/null 2>&1; then
  _pass "gwshield-init binary present at /usr/local/bin/gwshield-init"
else
  _fail "gwshield-init binary NOT found"
fi
docker rm -f "${id_out}" >/dev/null 2>&1 || true

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
echo "Results: ${PASS} passed, ${FAIL} failed"
[[ "${FAIL}" -eq 0 ]] || exit 1
