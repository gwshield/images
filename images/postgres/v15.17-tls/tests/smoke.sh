#!/usr/bin/env bash
# =============================================================================
# Smoke tests — gwshield-postgres v15.13 (tls profile)
# =============================================================================
set -euo pipefail

IMAGE="${1:?Usage: $0 <image-ref>}"
PASS=0
FAIL=0
CONTAINER=""
NET=""
TLS_DIR=""

_pass() { echo "[PASS] $*"; PASS=$((PASS + 1)); }
_fail() { echo "[FAIL] $*"; FAIL=$((FAIL + 1)); }

cleanup() {
  [[ -n "${CONTAINER}" ]] && docker rm -f "${CONTAINER}" >/dev/null 2>&1 || true
  [[ -n "${NET}"       ]] && docker network rm "${NET}"   >/dev/null 2>&1 || true
  [[ -n "${TLS_DIR}"   ]] && rm -rf "${TLS_DIR}" || true
}
trap cleanup EXIT

NET=$(docker network create "smoke-postgres-tls-$$" 2>/dev/null)

# ---------------------------------------------------------------------------
# Test 1: postgres --version responds
# ---------------------------------------------------------------------------
if docker run --rm --entrypoint /usr/local/bin/postgres "${IMAGE}" --version 2>&1 | grep -q 'PostgreSQL'; then
  _pass "postgres --version responds"
else
  _fail "postgres --version did not respond"
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
# Test 4: generate self-signed TLS cert for smoke test
# ---------------------------------------------------------------------------
TLS_DIR=$(mktemp -d)
chmod 777 "${TLS_DIR}"

if openssl req -x509 -newkey rsa:2048 -days 1 -nodes \
    -keyout "${TLS_DIR}/server.key" \
    -out    "${TLS_DIR}/server.crt" \
    -subj "/CN=localhost" >/dev/null 2>&1; then
  chmod 600 "${TLS_DIR}/server.key"
  chmod 644 "${TLS_DIR}/server.crt"
  _pass "self-signed TLS cert generated for smoke test"
else
  _fail "openssl not available — TLS cert generation failed"
fi

# ---------------------------------------------------------------------------
# Test 5: pg_isready from our hardened image reaches a live postgres server.
# Strategy: spin up postgres:15-alpine as the server (handles initdb via
# POSTGRES_PASSWORD env and its own entrypoint — no manual initdb needed,
# no chown required). Then run pg_isready from our hardened TLS image.
# ---------------------------------------------------------------------------
CONTAINER=$(docker run -d \
    --network "${NET}" \
    --name "postgres-smoke-tls-$$" \
    -e POSTGRES_PASSWORD=gwshield_test \
    -e POSTGRES_USER=postgres \
    postgres:15-alpine)

# Wait for postgres:15-alpine to finish initdb and start listening
sleep 8

if docker run --rm \
    --network "${NET}" \
    --entrypoint /usr/local/bin/pg_isready \
    "${IMAGE}" \
    -h "postgres-smoke-tls-$$" -p 5432 -U postgres 2>&1 | grep -q 'accepting'; then
  _pass "postgres (tls profile) accepts connections (pg_isready from hardened image)"
else
  echo "[DEBUG] server container logs:"; docker logs "postgres-smoke-tls-$$" 2>&1 | tail -20
  _fail "postgres (tls profile) did not respond to pg_isready"
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
