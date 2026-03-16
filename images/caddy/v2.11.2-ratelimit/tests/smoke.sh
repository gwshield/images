#!/usr/bin/env bash
# =============================================================================
# Smoke test — caddy:v2.11.2-ratelimit
# =============================================================================
set -euo pipefail

IMAGE="${1:-ghcr.io/gwshield/caddy:v2.11.2-ratelimit}"
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

if _file_in_image "$IMAGE" /usr/bin/caddy; then
  _pass "caddy binary present"
else
  _fail "caddy binary missing"
fi

VERSION_OUT=$(docker run --rm --platform linux/amd64 "$IMAGE" version 2>&1 || true)
if echo "$VERSION_OUT" | grep -q "v2\.11"; then
  _pass "version string: $(echo "$VERSION_OUT" | grep -v 'gwshield\|gatewarden' | head -1)"
else
  _fail "version string not found: $VERSION_OUT"
fi

VALIDATE_OUT=$(docker run --rm --platform linux/amd64 "$IMAGE" \
  validate --config /etc/caddy/Caddyfile --adapter caddyfile 2>&1) && VALIDATE_RC=0 || VALIDATE_RC=$?
if [ "$VALIDATE_RC" -eq 0 ]; then
  _pass "config validate passed"
else
  _fail "config validate failed (rc=${VALIDATE_RC}): ${VALIDATE_OUT}"
fi

CID=$(docker create --platform linux/amd64 "$IMAGE" 2>/dev/null)
USER_OUT=$(docker inspect --format='{{.Config.User}}' "$CID")
docker rm -f "$CID" >/dev/null 2>&1
if [ "$USER_OUT" = "65532:65532" ]; then
  _pass "non-root user: $USER_OUT"
else
  _fail "unexpected user: $USER_OUT (expected 65532:65532)"
fi

if docker run --rm --entrypoint /bin/sh "$IMAGE" -c 'echo alive' 2>&1 | grep -q "alive"; then
  _fail "shell found in runtime image"
else
  _pass "no shell in runtime image"
fi

CID=$(docker create --platform linux/amd64 "$IMAGE" 2>/dev/null)
docker cp "${CID}:/usr/bin/caddy" /tmp/caddy-smoke-bin-$$ 2>/dev/null
docker rm -f "$CID" >/dev/null 2>&1
NEEDED=$(docker run --rm -v "/tmp/caddy-smoke-bin-$$:/bin/caddy:ro" \
  alpine:3.22 sh -c 'apk add -q binutils && readelf -d /bin/caddy | grep NEEDED' 2>/dev/null || true)
rm -f /tmp/caddy-smoke-bin-$$
if [ -z "$NEEDED" ]; then
  _pass "static binary verified — zero dynamic dependencies"
else
  _fail "unexpected dynamic deps: $NEEDED"
fi

if _file_in_image "$IMAGE" /etc/ssl/certs/ca-certificates.crt; then
  _pass "CA certificates present"
else
  _fail "CA certificates missing"
fi

if _file_in_image "$IMAGE" /etc/caddy/Caddyfile; then
  _pass "default Caddyfile present"
else
  _fail "default Caddyfile missing"
fi

if _file_in_image "$IMAGE" /data; then
  _pass "/data directory present"
else
  _fail "/data directory missing"
fi

if _file_in_image "$IMAGE" /config; then
  _pass "/config directory present"
else
  _fail "/config directory missing"
fi

BANNER_OUT=$(docker run --rm --platform linux/amd64 "$IMAGE" version 2>&1 || true)
if echo "$BANNER_OUT" | grep -qi 'gwshield\|gatewarden'; then
  _pass "gwshield-init banner present in startup output"
else
  _fail "gwshield-init banner NOT found in startup output"
fi

echo ""
echo "=== Result: ${PASS} passed, ${FAIL} failed ==="
[ "$FAIL" -eq 0 ]
