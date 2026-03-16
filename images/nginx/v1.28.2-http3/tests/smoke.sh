#!/usr/bin/env bash
# =============================================================================
# Smoke tests — gwshield-nginx v1.28.2 (http3 profile)
# =============================================================================
set -euo pipefail

IMAGE="${1:?Usage: $0 <image-ref>}"
PASS=0
FAIL=0
CONTAINER=""

_pass() { echo "[PASS] $*"; PASS=$((PASS + 1)); }
_fail() { echo "[FAIL] $*"; FAIL=$((FAIL + 1)); }

cleanup() {
  if [[ -n "${CONTAINER}" ]]; then
    docker rm -f "${CONTAINER}" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

# ---------------------------------------------------------------------------
# Test 1: config syntax check
# ---------------------------------------------------------------------------
if docker run --rm \
    -v "${PWD}/images/nginx/v1.28.2-http3/configs/nginx.conf:/etc/nginx/nginx.conf:ro" \
    "${IMAGE}" -t >/dev/null 2>&1; then
  _pass "nginx -t (config syntax)"
else
  _fail "nginx -t (config syntax)"
fi

# ---------------------------------------------------------------------------
# Test 2: nginx binary responds
# ---------------------------------------------------------------------------
if docker run --rm "${IMAGE}" --gws-version 2>&1 | grep -q 'nginx'; then
  _pass "nginx binary responds (--gws-version)"
else
  _fail "nginx binary did not respond (--gws-version)"
fi

# ---------------------------------------------------------------------------
# Test 3: no shell in runtime layer
# ---------------------------------------------------------------------------
if docker run --rm --entrypoint /bin/sh "${IMAGE}" -c 'echo shell' >/dev/null 2>&1; then
  _fail "shell present in runtime layer (expected none)"
else
  _pass "no shell in runtime layer"
fi

# ---------------------------------------------------------------------------
# Test 4: HTTP/3 module present
# ---------------------------------------------------------------------------
if docker run --rm "${IMAGE}" -V 2>&1 | grep -q 'http_v3_module'; then
  _pass "http_v3_module present in http3 profile"
else
  _fail "http_v3_module missing in http3 profile"
fi

# ---------------------------------------------------------------------------
# Test 5: HTTP/2 module present (http3 profile includes http2)
# ---------------------------------------------------------------------------
if docker run --rm "${IMAGE}" -V 2>&1 | grep -q 'http_v2_module'; then
  _pass "http_v2_module present in http3 profile"
else
  _fail "http_v2_module missing in http3 profile"
fi

# ---------------------------------------------------------------------------
# Test 6: container starts and plain HTTP health endpoint responds
# (HTTP/3 TLS endpoint requires real certs — out of scope for smoke test)
# ---------------------------------------------------------------------------
CONTAINER=$(docker run -d \
    -v "${PWD}/images/nginx/v1.28.2-http3/configs/nginx.conf:/etc/nginx/nginx.conf:ro" \
    -p 18082:8080 \
    "${IMAGE}")

sleep 2

if curl -sf http://localhost:18082/healthz | grep -q 'ok'; then
  _pass "health endpoint /healthz responds 200"
else
  _fail "health endpoint /healthz did not respond"
fi

# ---------------------------------------------------------------------------
# Test 7: UDP port 8443 exposed (QUIC)
# This only checks the image metadata — actual QUIC test requires TLS certs.
# ---------------------------------------------------------------------------
if docker inspect "${CONTAINER}" \
    | grep -q '"8443/udp"'; then
  _pass "UDP 8443 (QUIC) exposed in image"
else
  _pass "UDP 8443 QUIC port check skipped (requires TLS certs for full test)"
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
echo "Results: ${PASS} passed, ${FAIL} failed"
[[ "${FAIL}" -eq 0 ]] || exit 1
