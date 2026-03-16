#!/usr/bin/env bash
# =============================================================================
# Smoke test — haproxy:v3.1.16-ssl
# =============================================================================
set -euo pipefail

IMAGE="${1:-ghcr.io/gwshield/haproxy:v3.1.16-ssl}"
PASS=0
FAIL=0
CERT_DIR=$(mktemp -d)
trap 'rm -rf "$CERT_DIR"' EXIT

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

# Generate a self-signed cert for smoke testing TLS startup
openssl req -x509 -newkey rsa:2048 -nodes \
  -keyout "${CERT_DIR}/server.key" \
  -out    "${CERT_DIR}/server.crt" \
  -days 1 -subj "/CN=smoke-test" 2>/dev/null
cat "${CERT_DIR}/server.crt" "${CERT_DIR}/server.key" > "${CERT_DIR}/server.pem"

echo "=== Smoke: ${IMAGE} ==="

# ---------------------------------------------------------------------------
# Test 1: binary exists
# ---------------------------------------------------------------------------
if _file_in_image "$IMAGE" /usr/local/bin/haproxy; then
  _pass "haproxy binary present"
else
  _fail "haproxy binary missing"
fi

# ---------------------------------------------------------------------------
# Test 2: version string (requires musl loader in /lib/)
# ---------------------------------------------------------------------------
VERSION_OUT=$(docker run --rm --platform linux/amd64 "$IMAGE" -v 2>&1) && VERSION_RC=0 || VERSION_RC=$?
if [ "$VERSION_RC" -eq 0 ] && echo "$VERSION_OUT" | grep -q "HAProxy version 3.1"; then
  _pass "version string: $(echo "$VERSION_OUT" | head -1)"
else
  _fail "version string not found (rc=${VERSION_RC}): ${VERSION_OUT}"
fi

# ---------------------------------------------------------------------------
# Test 3: config syntax check (exit-code based — HAProxy 3.x)
# HAProxy -c also stat()s the cert file, so we must mount the self-signed PEM.
# ---------------------------------------------------------------------------
SYNTAX_OUT=$(docker run --rm --platform linux/amd64 \
  -v "${CERT_DIR}/server.pem:/etc/haproxy/certs/server.pem:ro" \
  "$IMAGE" -c -f /etc/haproxy/haproxy.cfg 2>&1) && SYNTAX_RC=0 || SYNTAX_RC=$?
if [ "$SYNTAX_RC" -eq 0 ]; then
  _pass "config syntax valid (with cert mounted)"
else
  _fail "config syntax check failed (rc=${SYNTAX_RC}): ${SYNTAX_OUT}"
fi

# ---------------------------------------------------------------------------
# Test 4: non-root execution
# ---------------------------------------------------------------------------
USER_OUT=$(docker inspect --format='{{.Config.User}}' \
  "$(docker create "$IMAGE" 2>/dev/null | tee /tmp/smoke-haproxy-ssl-uid-cid-$$)")
docker rm -f "$(cat /tmp/smoke-haproxy-ssl-uid-cid-$$)" >/dev/null 2>&1
rm -f /tmp/smoke-haproxy-ssl-uid-cid-$$
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
# Test 6: only musl as dynamic dependency
# ---------------------------------------------------------------------------
CID=$(docker create "$IMAGE" 2>/dev/null)
docker cp "${CID}:/usr/local/bin/haproxy" /tmp/haproxy-ssl-smoke-bin-$$ 2>/dev/null
docker rm -f "$CID" >/dev/null 2>&1
NEEDED=$(docker run --rm -v "/tmp/haproxy-ssl-smoke-bin-$$:/bin/haproxy:ro" \
  alpine:3.22 sh -c 'apk add -q binutils && readelf -d /bin/haproxy | grep NEEDED' 2>/dev/null || true)
rm -f /tmp/haproxy-ssl-smoke-bin-$$

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
# Test 8: default config present
# ---------------------------------------------------------------------------
if _file_in_image "$IMAGE" /etc/haproxy/haproxy.cfg; then
  _pass "default config present"
else
  _fail "default config missing"
fi

# ---------------------------------------------------------------------------
# Test 9: certs directory present (TLS cert mount point)
# ---------------------------------------------------------------------------
if _file_in_image "$IMAGE" /etc/haproxy/certs; then
  _pass "certs directory present"
else
  _fail "certs directory missing"
fi

# ---------------------------------------------------------------------------
# Test 10: TLS startup with self-signed cert
# Mounts the generated PEM, starts HAProxy, checks /healthz on :8080
# (the HTTP redirect frontend — no TLS needed for health probe)
# ---------------------------------------------------------------------------
NET="smoke-haproxy-ssl-$$"
CTR_NAME="haproxy-ssl-srv-$$"
docker network create "$NET" >/dev/null 2>&1
docker run -d \
  --name "$CTR_NAME" \
  --network "$NET" \
  --platform linux/amd64 \
  -v "${CERT_DIR}/server.pem:/etc/haproxy/certs/server.pem:ro" \
  "$IMAGE" \
  -W -f /etc/haproxy/haproxy.cfg \
  >/dev/null 2>&1

sleep 4

HTTP_STATUS=$(docker run --rm --network "$NET" \
  alpine/curl:latest -sf -o /dev/null -w '%{http_code}' \
  "http://${CTR_NAME}:8080/healthz" 2>/dev/null || echo "000")

if [ "$HTTP_STATUS" = "200" ]; then
  _pass "health endpoint responds HTTP 200 (with TLS cert mounted)"
else
  # Dump container logs to help diagnose
  echo "    --- container logs ---"
  docker logs "$CTR_NAME" 2>&1 | tail -10 || true
  _fail "health endpoint returned: ${HTTP_STATUS}"
fi

docker rm -f "$CTR_NAME" >/dev/null 2>&1 || true
docker network rm "$NET" >/dev/null 2>&1 || true

# ---------------------------------------------------------------------------
# Test 11: gwshield-init banner appears in startup output
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
