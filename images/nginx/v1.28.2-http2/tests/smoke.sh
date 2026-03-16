#!/usr/bin/env bash
# =============================================================================
# Smoke tests — gwshield-nginx v1.28.2 (http2 profile)
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
    -v "${PWD}/images/nginx/v1.28.2-http2/configs/nginx.conf:/etc/nginx/nginx.conf:ro" \
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
# Test 4: no curl/wget in runtime layer
# ---------------------------------------------------------------------------
if docker run --rm --entrypoint /usr/bin/curl "${IMAGE}" --version >/dev/null 2>&1; then
  _fail "curl present in runtime layer (expected none)"
else
  _pass "no curl in runtime layer"
fi

# ---------------------------------------------------------------------------
# Test 5: HTTP/2 module present in this profile
# ---------------------------------------------------------------------------
if docker run --rm "${IMAGE}" -V 2>&1 | grep -q 'http_v2_module'; then
  _pass "http_v2_module present in http2 profile"
else
  _fail "http_v2_module missing in http2 profile"
fi

# ---------------------------------------------------------------------------
# Test 6: HTTP/3 module NOT present in http2 profile
# ---------------------------------------------------------------------------
if docker run --rm "${IMAGE}" -V 2>&1 | grep -q 'http_v3_module'; then
  _fail "http_v3_module present in http2 profile (unexpected)"
else
  _pass "http_v3_module absent in http2 profile"
fi

# ---------------------------------------------------------------------------
# Test 7: container starts and health endpoint responds
# ---------------------------------------------------------------------------
CONTAINER=$(docker run -d \
    -v "${PWD}/images/nginx/v1.28.2-http2/configs/nginx.conf:/etc/nginx/nginx.conf:ro" \
    -p 18081:8080 \
    "${IMAGE}")

sleep 2

if curl -sf http://localhost:18081/healthz | grep -q 'ok'; then
  _pass "health endpoint /healthz responds 200"
else
  _fail "health endpoint /healthz did not respond"
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
echo "Results: ${PASS} passed, ${FAIL} failed"
[[ "${FAIL}" -eq 0 ]] || exit 1
