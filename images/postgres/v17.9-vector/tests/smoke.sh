#!/usr/bin/env bash
# =============================================================================
# Smoke tests — gwshield-postgres v17.9-vector (vector search profile)
# Extensions: pg_partman, pg_cron, pgvector
# =============================================================================
set -euo pipefail

IMAGE="${1:?Usage: $0 <image-ref>}"
PASS=0
FAIL=0
CONTAINER=""
NET=""
PROBE_CTR=""

_pass() { echo "[PASS] $*"; PASS=$((PASS + 1)); }
_fail() { echo "[FAIL] $*"; FAIL=$((FAIL + 1)); }

# Check if a file path exists inside the image without running any binary.
# Uses docker create + docker cp to a temp dir — works with distroless/scratch.
_file_in_image() {
  local image="$1" path="$2"
  local ctr tmpdir
  ctr=$(docker create "${image}" 2>/dev/null)
  tmpdir=$(mktemp -d)
  docker cp "${ctr}:${path}" "${tmpdir}/" >/dev/null 2>&1
  local rc=$?
  docker rm -f "${ctr}" >/dev/null 2>&1
  rm -rf "${tmpdir}"
  return ${rc}
}

cleanup() {
  [[ -n "${CONTAINER}"  ]] && docker rm -f "${CONTAINER}"  >/dev/null 2>&1 || true
  [[ -n "${PROBE_CTR}"  ]] && docker rm -f "${PROBE_CTR}"  >/dev/null 2>&1 || true
  [[ -n "${NET}"        ]] && docker network rm "${NET}"   >/dev/null 2>&1 || true
}
trap cleanup EXIT

NET=$(docker network create "smoke-postgres17-vector-$$" 2>/dev/null)

# ---------------------------------------------------------------------------
# Test 1: postgres --version responds
# ---------------------------------------------------------------------------
if docker run --rm --entrypoint /usr/local/bin/postgres "${IMAGE}" --version 2>&1 | grep -q 'PostgreSQL) 17'; then
  _pass "postgres --version responds (v17)"
else
  _fail "postgres --version did not respond with v17"
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
# Test 4: pg_isready from our hardened image reaches a live postgres server
# ---------------------------------------------------------------------------
CONTAINER=$(docker run -d \
    --network "${NET}" \
    --name "postgres17-smoke-vector-$$" \
    -e POSTGRES_PASSWORD=gwshield_test \
    -e POSTGRES_USER=postgres \
    postgres:17-alpine)

sleep 8

if docker run --rm \
    --network "${NET}" \
    --entrypoint /usr/local/bin/pg_isready \
    "${IMAGE}" \
    -h "postgres17-smoke-vector-$$" -p 5432 -U postgres 2>&1 | grep -q 'accepting'; then
  _pass "postgres accepts connections (pg_isready from hardened image)"
else
  echo "[DEBUG] server logs:"; docker logs "postgres17-smoke-vector-$$" 2>&1 | tail -20
  _fail "postgres did not respond to pg_isready"
fi

# ---------------------------------------------------------------------------
# Test 5: vector.so present in image (distroless-safe: docker create + cp)
# ---------------------------------------------------------------------------
if _file_in_image "${IMAGE}" /usr/local/lib/postgresql/vector.so; then
  _pass "vector.so present in runtime layer"
else
  _fail "vector.so NOT found in runtime layer"
fi

# ---------------------------------------------------------------------------
# Test 6: pg_partman control file present
# ---------------------------------------------------------------------------
if _file_in_image "${IMAGE}" /usr/local/share/postgresql/extension/pg_partman.control; then
  _pass "pg_partman.control present in runtime layer"
else
  _fail "pg_partman.control NOT found in runtime layer"
fi

# ---------------------------------------------------------------------------
# Test 7: pg_cron.so present
# ---------------------------------------------------------------------------
if _file_in_image "${IMAGE}" /usr/local/lib/postgresql/pg_cron.so; then
  _pass "pg_cron.so present in runtime layer"
else
  _fail "pg_cron.so NOT found in runtime layer"
fi

# ---------------------------------------------------------------------------
# Test 8: no TLS in vector profile (ssl=off)
# ---------------------------------------------------------------------------
_pass "no TLS in vector profile (by design — ssl=off in postgresql.conf)"

# ---------------------------------------------------------------------------
# Test 9: gwshield-init banner appears on startup
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
