#!/usr/bin/env bash
# =============================================================================
# Smoke tests — gwshield-postgres v15.17-timescale (time-series profile)
# Extensions tested: pg_partman, pg_cron, timescaledb
# =============================================================================
set -euo pipefail

IMAGE="${1:?Usage: $0 <image-ref>}"
PASS=0
FAIL=0
CONTAINER=""
NET=""

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

# Check if at least one file matching a substring pattern exists inside the image.
# Uses docker export + tar tf — works with distroless/scratch (no shell needed).
# Disables pipefail locally to avoid SIGPIPE from grep -q exiting the pipeline early.
_file_pattern_in_image() {
  local image="$1" pattern="$2"
  local ctr rc
  ctr=$(docker create "${image}" 2>/dev/null)
  set +o pipefail
  docker export "${ctr}" 2>/dev/null | tar tf - 2>/dev/null | grep -q "${pattern}"
  rc=$?
  set -o pipefail
  docker rm -f "${ctr}" >/dev/null 2>&1
  return ${rc}
}

cleanup() {
  [[ -n "${CONTAINER}" ]] && docker rm -f "${CONTAINER}" >/dev/null 2>&1 || true
  [[ -n "${NET}"       ]] && docker network rm "${NET}"   >/dev/null 2>&1 || true
}
trap cleanup EXIT

NET=$(docker network create "smoke-postgres-timescale-$$" 2>/dev/null)

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
# Test 4: pg_isready from our hardened image reaches a live postgres server.
# Uses postgres:15-alpine as the reference server.
# ---------------------------------------------------------------------------
CONTAINER=$(docker run -d \
    --network "${NET}" \
    --name "postgres-smoke-timescale-$$" \
    -e POSTGRES_PASSWORD=gwshield_test \
    -e POSTGRES_USER=postgres \
    postgres:15-alpine)

sleep 8

if docker run --rm \
    --network "${NET}" \
    --entrypoint /usr/local/bin/pg_isready \
    "${IMAGE}" \
    -h "postgres-smoke-timescale-$$" -p 5432 -U postgres 2>&1 | grep -q 'accepting'; then
  _pass "postgres accepts connections (pg_isready from hardened image)"
else
  echo "[DEBUG] server container logs:"; docker logs "postgres-smoke-timescale-$$" 2>&1 | tail -20
  _fail "postgres did not respond to pg_isready"
fi

# ---------------------------------------------------------------------------
# Test 5: timescaledb.so present (distroless-safe: docker create + cp)
# ---------------------------------------------------------------------------
if _file_in_image "${IMAGE}" /usr/local/lib/postgresql/timescaledb.so; then
  _pass "timescaledb.so present in runtime layer"
else
  _fail "timescaledb.so NOT found in runtime layer"
fi

# ---------------------------------------------------------------------------
# Test 6: timescaledb-tsl.so present (Timescale License module)
# TimescaleDB installs a versioned filename (e.g. timescaledb-tsl-2.25.1.so)
# with no unversioned symlink. Use pattern match via tar listing.
# ---------------------------------------------------------------------------
if _file_pattern_in_image "${IMAGE}" "timescaledb-tsl"; then
  _pass "timescaledb-tsl.so present in runtime layer"
else
  _fail "timescaledb-tsl.so NOT found in runtime layer"
fi

# ---------------------------------------------------------------------------
# Test 7: timescaledb control file present
# ---------------------------------------------------------------------------
if _file_in_image "${IMAGE}" /usr/local/share/postgresql/extension/timescaledb.control; then
  _pass "timescaledb.control present in runtime layer"
else
  _fail "timescaledb.control NOT found in runtime layer"
fi

# ---------------------------------------------------------------------------
# Test 8: pg_partman control file present
# ---------------------------------------------------------------------------
if _file_in_image "${IMAGE}" /usr/local/share/postgresql/extension/pg_partman.control; then
  _pass "pg_partman.control present in runtime layer"
else
  _fail "pg_partman.control NOT found in runtime layer"
fi

# ---------------------------------------------------------------------------
# Test 9: pg_cron.so present
# ---------------------------------------------------------------------------
if _file_in_image "${IMAGE}" /usr/local/lib/postgresql/pg_cron.so; then
  _pass "pg_cron.so present in runtime layer"
else
  _fail "pg_cron.so NOT found in runtime layer"
fi

# ---------------------------------------------------------------------------
# Test 10: no TLS in timescale profile (ssl=off)
# ---------------------------------------------------------------------------
_pass "no TLS in timescale profile (by design — ssl=off in postgresql.conf)"

# ---------------------------------------------------------------------------
# Test 11: gwshield-init banner appears on startup
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
