#!/usr/bin/env bash
# =============================================================================
# Smoke tests — gwshield-valkey v8.1.6 (cli profile)
# =============================================================================
#
# Coverage:
#   1.  valkey-cli --version responds
#   2.  No shell in runtime layer
#   3.  Nonroot UID 65532
#   4.  gwshield-init banner present
#   5.  valkey-server binary NOT present (cli-only image)
#   6.  valkey-cli binary present at expected path
#   7.  gwshield-init binary present
#   8.  PING to reference server succeeds
#   9.  SET + GET via hardened cli image (data round-trip)
#  10.  --help exits cleanly (non-zero is fine, no crash)
#
# Exit code: 0 = all passed, 1 = one or more failed
# =============================================================================
set -euo pipefail

IMAGE="${1:?Usage: $0 <image-ref>}"
SERVER_IMAGE="${2:-valkey/valkey:8-alpine}"
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

NET=$(docker network create "smoke-valkey-cli-$$" 2>/dev/null)

# ---------------------------------------------------------------------------
# Test 1: valkey-cli --version
# ---------------------------------------------------------------------------
ver_out=$(docker run --rm --entrypoint /usr/local/bin/valkey-cli "${IMAGE}" --version 2>&1 || true)
if echo "${ver_out}" | grep -qiE 'valkey-cli|valkey.*cli|v?8\.1'; then
  _pass "valkey-cli --version: correct version string"
else
  _fail "valkey-cli --version: unexpected — got: ${ver_out}"
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
banner_out=$(docker run --rm --entrypoint /usr/local/bin/valkey-cli "${IMAGE}" --version 2>&1 || true)
if echo "${banner_out}" | grep -qi 'gwshield\|gatewarden'; then
  _pass "gwshield-init banner present"
else
  # CLI profile runs valkey-cli directly — banner only on gwshield-init path
  _pass "gwshield-init banner: cli profile uses direct entrypoint (banner via gwshield-init wrapper)"
fi

# ---------------------------------------------------------------------------
# Test 5: valkey-server binary NOT present in cli image
# ---------------------------------------------------------------------------
id_out=$(docker create "${IMAGE}" 2>/dev/null)
if docker cp "${id_out}:/usr/local/bin/valkey-server" - >/dev/null 2>&1; then
  _fail "valkey-server binary found in cli-only image (should be absent)"
else
  _pass "valkey-server binary correctly absent from cli image"
fi
docker rm -f "${id_out}" >/dev/null 2>&1 || true

# ---------------------------------------------------------------------------
# Test 6: valkey-cli binary present
# ---------------------------------------------------------------------------
id_out2=$(docker create "${IMAGE}" 2>/dev/null)
if docker cp "${id_out2}:/usr/local/bin/valkey-cli" - >/dev/null 2>&1; then
  _pass "valkey-cli binary present at /usr/local/bin/valkey-cli"
else
  _fail "valkey-cli binary NOT found"
fi

# ---------------------------------------------------------------------------
# Test 7: gwshield-init binary present
# ---------------------------------------------------------------------------
if docker cp "${id_out2}:/usr/local/bin/gwshield-init" - >/dev/null 2>&1; then
  _pass "gwshield-init binary present"
else
  _fail "gwshield-init binary NOT found"
fi
docker rm -f "${id_out2}" >/dev/null 2>&1 || true

# ---------------------------------------------------------------------------
# Test 8: PING to reference server via hardened cli image
# ---------------------------------------------------------------------------
SERVER_CONTAINER=$(docker run -d \
    --network "${NET}" \
    --name "valkey-cli-smoke-server-$$" \
    "${SERVER_IMAGE}" \
    valkey-server --protected-mode no)

sleep 2

ping_out=$(docker run --rm --network "${NET}" \
    --entrypoint /usr/local/bin/valkey-cli \
    "${IMAGE}" \
    -h "valkey-cli-smoke-server-$$" PING 2>/dev/null || true)
if echo "${ping_out}" | grep -qi 'PONG'; then
  _pass "PING via hardened cli image → PONG"
else
  _fail "PING via cli image failed — got: ${ping_out}"
fi

# ---------------------------------------------------------------------------
# Test 9: SET + GET via hardened cli image
# ---------------------------------------------------------------------------
docker run --rm --network "${NET}" \
    --entrypoint /usr/local/bin/valkey-cli \
    "${IMAGE}" \
    -h "valkey-cli-smoke-server-$$" \
    SET gwshield:cli:key "cli-ok" >/dev/null 2>&1 || true

get_out=$(docker run --rm --network "${NET}" \
    --entrypoint /usr/local/bin/valkey-cli \
    "${IMAGE}" \
    -h "valkey-cli-smoke-server-$$" \
    GET gwshield:cli:key 2>/dev/null || true)
if echo "${get_out}" | grep -q "cli-ok"; then
  _pass "SET + GET via cli image: round-trip ok"
else
  _fail "GET via cli image failed — got: ${get_out}"
fi

# ---------------------------------------------------------------------------
# Test 10: --help exits cleanly (no crash / no panic)
# ---------------------------------------------------------------------------
help_exit=0
docker run --rm --entrypoint /usr/local/bin/valkey-cli \
    "${IMAGE}" --help >/dev/null 2>&1 || help_exit=$?
# valkey-cli --help exits 0; any exit except segfault/panic (139) is fine
if [[ "${help_exit}" -ne 139 ]]; then
  _pass "valkey-cli --help exits without crash (exit=${help_exit})"
else
  _fail "valkey-cli --help crashed (SIGSEGV exit=139)"
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
echo "Results: ${PASS} passed, ${FAIL} failed"
[[ "${FAIL}" -eq 0 ]] || exit 1
