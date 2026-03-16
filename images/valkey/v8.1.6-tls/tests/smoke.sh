#!/usr/bin/env bash
# =============================================================================
# Smoke tests — gwshield-valkey v8.1.6 (tls profile)
# =============================================================================
#
# Coverage:
#   1.  valkey-server --version responds
#   2.  No shell in runtime layer
#   3.  Nonroot UID 65532
#   4.  gwshield-init banner present
#   5.  TLS port 6380 exposed in image metadata
#   6.  Plain TCP port 6379 NOT exposed (tls-only profile)
#   7.  Server starts and accepts PING over TLS with self-signed cert
#   8.  SET + GET round-trip over TLS
#   9.  Dangerous commands blocked
#  10.  valkey-server binary present at expected path
#  11.  gwshield-init binary present at expected path
#
# Exit code: 0 = all passed, 1 = one or more failed
# =============================================================================
set -euo pipefail

IMAGE="${1:?Usage: $0 <image-ref>}"
PASS=0
FAIL=0
CONTAINER=""
NET=""
CERT_DIR=""

_pass() { echo "[PASS] $*"; PASS=$((PASS + 1)); }
_fail() { echo "[FAIL] $*"; FAIL=$((FAIL + 1)); }

cleanup() {
  [[ -n "${CONTAINER}" ]] && docker rm -f "${CONTAINER}" >/dev/null 2>&1 || true
  [[ -n "${NET}"       ]] && docker network rm "${NET}"   >/dev/null 2>&1 || true
  [[ -n "${CERT_DIR}"  ]] && rm -rf "${CERT_DIR}"
}
trap cleanup EXIT

NET=$(docker network create "smoke-valkey-tls-$$" 2>/dev/null)

# ---------------------------------------------------------------------------
# Test 1: version output
# ---------------------------------------------------------------------------
ver_out=$(docker run --rm "${IMAGE}" --version 2>&1 || true)
if echo "${ver_out}" | grep -qiE 'valkey.*server|server.*v?8\.1'; then
  _pass "valkey-server --version: correct version string"
else
  _fail "valkey-server --version: unexpected output — got: ${ver_out}"
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
  _fail "gwshield-init banner NOT found — got: ${banner_out}"
fi

# ---------------------------------------------------------------------------
# Test 5: TLS port 6380 exposed in image metadata
# ---------------------------------------------------------------------------
if docker inspect "${IMAGE}" 2>/dev/null | grep -q '"6380/tcp"'; then
  _pass "TLS port 6380/tcp exposed in image metadata"
else
  _fail "TLS port 6380/tcp NOT exposed in image metadata"
fi

# ---------------------------------------------------------------------------
# Test 6: plain port 6379 NOT exposed
# ---------------------------------------------------------------------------
if docker inspect "${IMAGE}" 2>/dev/null | grep -q '"6379/tcp"'; then
  _fail "plain port 6379/tcp exposed in tls-only profile (unexpected)"
else
  _pass "plain port 6379/tcp not in image metadata (correct for tls profile)"
fi

# ---------------------------------------------------------------------------
# Test 7: server starts + PING over TLS (self-signed cert)
# ---------------------------------------------------------------------------
CERT_DIR=$(mktemp -d)
openssl req -x509 -newkey rsa:2048 -nodes \
    -keyout "${CERT_DIR}/server.key" \
    -out    "${CERT_DIR}/server.crt" \
    -days 1 -subj "/CN=valkey-tls-smoke" 2>/dev/null
# For client auth disabled (tls-auth-clients no), ca.crt can be the server cert itself
cp "${CERT_DIR}/server.crt" "${CERT_DIR}/ca.crt"
# Ensure nonroot UID 65532 inside the container can traverse the dir and read the certs.
# mktemp -d produces a 700 directory; the container user cannot enter it unless we open it.
chmod 755 "${CERT_DIR}"
chmod 644 "${CERT_DIR}/server.key" "${CERT_DIR}/server.crt" "${CERT_DIR}/ca.crt"

CONTAINER=$(docker run -d \
    --network "${NET}" \
    --name "valkey-smoke-tls-$$" \
    -v "${CERT_DIR}:/tls:ro" \
    -v "${PWD}/images/valkey/v8.1.6-tls/configs/valkey.conf:/etc/valkey/valkey.conf:ro" \
    "${IMAGE}")

sleep 5

ping_out=$(docker run --rm \
    --network "${NET}" \
    -v "${CERT_DIR}:/tls:ro" \
    valkey/valkey:8-alpine \
    valkey-cli \
      --tls --cacert /tls/ca.crt \
      -h "valkey-smoke-tls-$$" -p 6380 \
    PING 2>/dev/null || true)
if echo "${ping_out}" | grep -qi 'PONG'; then
  _pass "TLS PING → PONG (self-signed cert, tls-auth-clients no)"
else
  echo "[DEBUG] server logs:"; docker logs "${CONTAINER}" 2>&1 | tail -10
  _fail "TLS PING failed — got: ${ping_out}"
fi

# ---------------------------------------------------------------------------
# Test 8: SET + GET over TLS
# ---------------------------------------------------------------------------
docker run --rm --network "${NET}" \
    -v "${CERT_DIR}:/tls:ro" \
    valkey/valkey:8-alpine \
    valkey-cli --tls --cacert /tls/ca.crt \
      -h "valkey-smoke-tls-$$" -p 6380 \
    SET gwshield:tls:key "tls-ok" >/dev/null 2>&1 || true

get_out=$(docker run --rm --network "${NET}" \
    -v "${CERT_DIR}:/tls:ro" \
    valkey/valkey:8-alpine \
    valkey-cli --tls --cacert /tls/ca.crt \
      -h "valkey-smoke-tls-$$" -p 6380 \
    GET gwshield:tls:key 2>/dev/null || true)
if echo "${get_out}" | grep -q "tls-ok"; then
  _pass "SET + GET over TLS: round-trip ok"
else
  _fail "TLS GET failed — got: ${get_out}"
fi

# ---------------------------------------------------------------------------
# Test 9: dangerous commands blocked
# ---------------------------------------------------------------------------
flush_out=$(docker run --rm --network "${NET}" \
    -v "${CERT_DIR}:/tls:ro" \
    valkey/valkey:8-alpine \
    valkey-cli --tls --cacert /tls/ca.crt \
      -h "valkey-smoke-tls-$$" -p 6380 \
    FLUSHALL 2>/dev/null || true)
if echo "${flush_out}" | grep -qiE 'unknown|ERR|error'; then
  _pass "FLUSHALL is renamed/blocked"
else
  _fail "FLUSHALL NOT blocked — response: ${flush_out}"
fi

# ---------------------------------------------------------------------------
# Test 10 + 11: binary presence via docker cp
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
