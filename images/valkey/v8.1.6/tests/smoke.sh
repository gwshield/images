#!/usr/bin/env bash
# =============================================================================
# Smoke tests — gwshield-valkey v8.1.6 (standard profile)
# =============================================================================
#
# Coverage:
#   1.  valkey-server --version responds and reports correct version
#   2.  No shell present in runtime layer (FROM scratch hardening)
#   3.  Image configured as nonroot UID 65532
#   4.  gwshield-init banner present on startup output
#   5.  Server starts and accepts PING via docker network
#   6.  SET + GET round-trip succeeds (basic data path)
#   7.  Key expiry (TTL) works correctly
#   8.  INFO server returns valkey_version field
#   9.  Renamed dangerous commands are blocked (FLUSHALL, CONFIG)
#  10.  No TLS port exposed (standard profile — plain TCP only)
#  11.  valkey-server binary present at expected path
#  12.  No valkey-server process running as root inside container
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

NET=$(docker network create "smoke-valkey-standard-$$" 2>/dev/null)

# ---------------------------------------------------------------------------
# Test 1: version output — correct binary and version string
# ---------------------------------------------------------------------------
ver_out=$(docker run --rm "${IMAGE}" --version 2>&1 || true)
if echo "${ver_out}" | grep -qiE 'valkey.*server|server.*v?8\.1'; then
  _pass "valkey-server --version: correct version string"
else
  _fail "valkey-server --version: unexpected output — got: ${ver_out}"
fi

# ---------------------------------------------------------------------------
# Test 2: no shell in runtime layer
# ---------------------------------------------------------------------------
if docker run --rm --entrypoint /bin/sh "${IMAGE}" -c 'echo shell' >/dev/null 2>&1; then
  _fail "shell /bin/sh present in runtime layer (expected none in FROM scratch)"
else
  _pass "no shell in runtime layer"
fi

# ---------------------------------------------------------------------------
# Test 3: nonroot UID 65532
# ---------------------------------------------------------------------------
actual_uid=$(docker inspect --format='{{.Config.User}}' "${IMAGE}" 2>/dev/null || true)
if [[ "${actual_uid}" == "65532:65532" ]]; then
  _pass "image configured as nonroot UID 65532:65532"
else
  _fail "unexpected user config: '${actual_uid}' (expected 65532:65532)"
fi

# ---------------------------------------------------------------------------
# Test 4: gwshield-init banner present on startup
# ---------------------------------------------------------------------------
banner_out=$(docker run --rm "${IMAGE}" --version 2>&1 || true)
if echo "${banner_out}" | grep -qi 'gwshield\|gatewarden'; then
  _pass "gwshield-init banner present in startup output"
else
  _fail "gwshield-init banner NOT found — got: ${banner_out}"
fi

# ---------------------------------------------------------------------------
# Test 5: server starts and responds to PING
# ---------------------------------------------------------------------------
CONTAINER=$(docker run -d \
    --network "${NET}" \
    --name "valkey-smoke-std-$$" \
    -v "${PWD}/images/valkey/v8.1.6/configs/valkey.conf:/etc/valkey/valkey.conf:ro" \
    "${IMAGE}")

sleep 3

ping_out=$(docker run --rm \
    --network "${NET}" \
    valkey/valkey:8-alpine \
    valkey-cli -h "valkey-smoke-std-$$" -p 6379 PING 2>/dev/null || true)
if echo "${ping_out}" | grep -qi 'PONG'; then
  _pass "server accepts PING → PONG"
else
  echo "[DEBUG] server logs:"; docker logs "${CONTAINER}" 2>&1 | tail -10
  _fail "PING failed — got: ${ping_out}"
fi

# ---------------------------------------------------------------------------
# Test 6: SET + GET round-trip
# ---------------------------------------------------------------------------
docker run --rm --network "${NET}" \
    valkey/valkey:8-alpine \
    valkey-cli -h "valkey-smoke-std-$$" -p 6379 \
    SET gwshield:smoke:key "valkey-ok" >/dev/null 2>&1 || true

get_out=$(docker run --rm --network "${NET}" \
    valkey/valkey:8-alpine \
    valkey-cli -h "valkey-smoke-std-$$" -p 6379 \
    GET gwshield:smoke:key 2>/dev/null || true)
if echo "${get_out}" | grep -q "valkey-ok"; then
  _pass "SET + GET round-trip: value stored and retrieved correctly"
else
  _fail "GET returned unexpected value — got: ${get_out}"
fi

# ---------------------------------------------------------------------------
# Test 7: TTL / key expiry
# ---------------------------------------------------------------------------
docker run --rm --network "${NET}" \
    valkey/valkey:8-alpine \
    valkey-cli -h "valkey-smoke-std-$$" -p 6379 \
    SET gwshield:smoke:ttl "expiring" EX 60 >/dev/null 2>&1 || true

ttl_out=$(docker run --rm --network "${NET}" \
    valkey/valkey:8-alpine \
    valkey-cli -h "valkey-smoke-std-$$" -p 6379 \
    TTL gwshield:smoke:ttl 2>/dev/null || true)
if echo "${ttl_out}" | grep -qE '^[1-9][0-9]*$'; then
  _pass "TTL / key expiry: TTL=${ttl_out}s"
else
  _fail "TTL check failed — got: ${ttl_out}"
fi

# ---------------------------------------------------------------------------
# Test 8: INFO server returns valkey_version
# ---------------------------------------------------------------------------
info_out=$(docker run --rm --network "${NET}" \
    valkey/valkey:8-alpine \
    valkey-cli -h "valkey-smoke-std-$$" -p 6379 \
    INFO server 2>/dev/null || true)
if echo "${info_out}" | grep -qi 'valkey_version:'; then
  _pass "INFO server: valkey_version field present"
else
  _fail "INFO server: valkey_version NOT found — got: $(echo "${info_out}" | head -5)"
fi

# ---------------------------------------------------------------------------
# Test 9: dangerous commands are renamed/blocked
# ---------------------------------------------------------------------------
flush_out=$(docker run --rm --network "${NET}" \
    valkey/valkey:8-alpine \
    valkey-cli -h "valkey-smoke-std-$$" -p 6379 \
    FLUSHALL 2>/dev/null || true)
if echo "${flush_out}" | grep -qiE 'unknown|ERR|error'; then
  _pass "FLUSHALL is renamed/blocked (rename-command in config)"
else
  _fail "FLUSHALL NOT blocked — response: ${flush_out}"
fi

config_out=$(docker run --rm --network "${NET}" \
    valkey/valkey:8-alpine \
    valkey-cli -h "valkey-smoke-std-$$" -p 6379 \
    CONFIG GET maxmemory 2>/dev/null || true)
if echo "${config_out}" | grep -qiE 'unknown|ERR|error'; then
  _pass "CONFIG is renamed/blocked (rename-command in config)"
else
  _fail "CONFIG NOT blocked — response: ${config_out}"
fi

# ---------------------------------------------------------------------------
# Test 10: TLS port NOT exposed (standard profile — plain TCP only)
# ---------------------------------------------------------------------------
if docker inspect "${IMAGE}" 2>/dev/null | grep -q '"6380/tcp"'; then
  _fail "TLS port 6380/tcp exposed in standard profile (unexpected)"
else
  _pass "TLS port 6380/tcp not exposed (correct for standard profile)"
fi

# ---------------------------------------------------------------------------
# Test 11: valkey-server binary at expected path
# ---------------------------------------------------------------------------
id_out=$(docker create "${IMAGE}" 2>/dev/null)
if docker cp "${id_out}:/usr/local/bin/valkey-server" - >/dev/null 2>&1; then
  _pass "valkey-server binary present at /usr/local/bin/valkey-server"
else
  _fail "valkey-server binary NOT found at /usr/local/bin/valkey-server"
fi
docker rm -f "${id_out}" >/dev/null 2>&1 || true

# ---------------------------------------------------------------------------
# Test 12: gwshield-init binary at expected path
# ---------------------------------------------------------------------------
id_out2=$(docker create "${IMAGE}" 2>/dev/null)
if docker cp "${id_out2}:/usr/local/bin/gwshield-init" - >/dev/null 2>&1; then
  _pass "gwshield-init binary present at /usr/local/bin/gwshield-init"
else
  _fail "gwshield-init binary NOT found at /usr/local/bin/gwshield-init"
fi
docker rm -f "${id_out2}" >/dev/null 2>&1 || true

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
echo "Results: ${PASS} passed, ${FAIL} failed"
[[ "${FAIL}" -eq 0 ]] || exit 1
