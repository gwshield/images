#!/usr/bin/env bash
# =============================================================================
# Smoke test — haproxy:v3.1.16 (standard)
# =============================================================================
set -euo pipefail

IMAGE="${1:-ghcr.io/gwshield/haproxy:v3.1.16}"
PASS=0
FAIL=0

_pass() { echo "  [PASS] $*"; ((PASS++)) || true; }
_fail() { echo "  [FAIL] $*"; ((FAIL++)) || true; }

_file_in_image() {
  local img="$1" path="$2"
  local cid
  cid=$(docker create "$img" 2>/dev/null)
  docker cp "${cid}:${path}" - >/dev/null 2>&1
  local rc=$?
  docker rm -f "$cid" >/dev/null 2>&1
  return $rc
}

echo "=== Smoke: ${IMAGE} ==="

# ---------------------------------------------------------------------------
# Test 1: binary exists and is executable
# ---------------------------------------------------------------------------
if _file_in_image "$IMAGE" /usr/local/bin/haproxy; then
  _pass "haproxy binary present"
else
  _fail "haproxy binary missing"
fi

# ---------------------------------------------------------------------------
# Test 2: version string
# ---------------------------------------------------------------------------
VERSION_OUT=$(docker run --rm --platform linux/amd64 "$IMAGE" -v 2>&1 || true)
if echo "$VERSION_OUT" | grep -q "HAProxy version 3.1"; then
  _pass "version string: $(echo "$VERSION_OUT" | head -1)"
else
  _fail "version string not found: $VERSION_OUT"
fi

# ---------------------------------------------------------------------------
# Test 3: config syntax check passes (exit-code based — HAProxy 3.x)
# haproxy -c exits 0 on valid config, non-zero on error
# ---------------------------------------------------------------------------
SYNTAX_OUT=$(docker run --rm --platform linux/amd64 "$IMAGE" -c -f /etc/haproxy/haproxy.cfg 2>&1) && SYNTAX_RC=0 || SYNTAX_RC=$?
if [ "$SYNTAX_RC" -eq 0 ]; then
  _pass "config syntax valid"
else
  _fail "config syntax check failed (rc=${SYNTAX_RC}): ${SYNTAX_OUT}"
fi

# ---------------------------------------------------------------------------
# Test 4: non-root execution
# ---------------------------------------------------------------------------
USER_OUT=$(docker inspect --format='{{.Config.User}}' \
  "$(docker create "$IMAGE" 2>/dev/null | tee /tmp/smoke-haproxy-uid-cid-$$)")
docker rm -f "$(cat /tmp/smoke-haproxy-uid-cid-$$)" >/dev/null 2>&1
rm -f /tmp/smoke-haproxy-uid-cid-$$
if [ "$USER_OUT" = "65532:65532" ]; then
  _pass "non-root user: $USER_OUT"
else
  _fail "unexpected user: $USER_OUT (expected 65532:65532)"
fi

# ---------------------------------------------------------------------------
# Test 5: no shell in runtime image
# ---------------------------------------------------------------------------
if docker run --rm --entrypoint /bin/sh "$IMAGE" -c 'echo alive' 2>&1 | grep -q "alive"; then
  _fail "shell found in runtime image"
else
  _pass "no shell in runtime image"
fi

# ---------------------------------------------------------------------------
# Test 6: only musl as dynamic dependency (no libssl.so, no libpcre2.so etc.)
# ---------------------------------------------------------------------------
# Extract binary and run readelf via a helper container
CID=$(docker create "$IMAGE" 2>/dev/null)
docker cp "${CID}:/usr/local/bin/haproxy" /tmp/haproxy-smoke-bin-$$ 2>/dev/null
docker rm -f "$CID" >/dev/null 2>&1
NEEDED=$(docker run --rm -v "/tmp/haproxy-smoke-bin-$$:/bin/haproxy:ro" \
  alpine:3.22 sh -c 'apk add -q binutils && readelf -d /bin/haproxy | grep NEEDED' 2>/dev/null || true)
rm -f /tmp/haproxy-smoke-bin-$$

if echo "$NEEDED" | grep -qv 'musl' 2>/dev/null && [ -n "$(echo "$NEEDED" | grep -v 'musl')" ]; then
  _fail "unexpected dynamic deps: $NEEDED"
else
  _pass "static linking verified — only musl: $(echo "$NEEDED" | tr -d '\n')"
fi

# ---------------------------------------------------------------------------
# Test 7: CA certificates present
# ---------------------------------------------------------------------------
if _file_in_image "$IMAGE" /etc/ssl/certs/ca-certificates.crt; then
  _pass "CA certificates present"
else
  _fail "CA certificates missing"
fi

# ---------------------------------------------------------------------------
# Test 8: default config file present
# ---------------------------------------------------------------------------
if _file_in_image "$IMAGE" /etc/haproxy/haproxy.cfg; then
  _pass "default config present"
else
  _fail "default config missing"
fi

# ---------------------------------------------------------------------------
# Test 9: gwshield-init banner appears in startup output
# gwshield-init prints the Gatewarden Shield banner then exec()s haproxy.
# haproxy -v outputs the version — banner appears before it on stdout.
# ---------------------------------------------------------------------------
BANNER_OUT=$(docker run --rm --platform linux/amd64 "$IMAGE" -v 2>&1 || true)
if echo "$BANNER_OUT" | grep -qi 'gwshield\|gatewarden'; then
  _pass "gwshield-init banner present in startup output"
else
  _fail "gwshield-init banner NOT found in startup output"
fi

# ---------------------------------------------------------------------------
# Result
# ---------------------------------------------------------------------------
echo ""
echo "=== Result: ${PASS} passed, ${FAIL} failed ==="
[ "$FAIL" -eq 0 ]
