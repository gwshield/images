#!/usr/bin/env bash
# =============================================================================
# Smoke test — gwshield-otelcol v0.147.0 (contrib)
# =============================================================================
#
# Validates the built image before promotion:
#   1.  gwshield-init banner present (otelcol in --gws-version output)
#   2.  otelcol-contrib binary present at /usr/bin/otelcol-contrib
#   3.  gwshield-init binary present at /usr/local/bin/gwshield-init
#   4.  --gws-version reports correct version (0.147) and service name
#   5.  No shell in runtime layer (/bin/sh absent)
#   6.  Non-root UID 65532
#   7.  Config skeleton present (/etc/otelcol/config.yaml)
#   8.  Static binary — zero NEEDED entries
#   9.  Config validates cleanly (otelcol-contrib validate)
#   10. Collector starts and health endpoint responds on :13133
#
# Usage: ./tests/smoke.sh <image_tag>
# =============================================================================
set -euo pipefail

IMAGE="${1:-gwshield-otelcol:v0.147.0}"
PASS=0
FAIL=0
CID_LIST=()

_pass() { echo "  [PASS] $*"; ((PASS++)) || true; }
_fail() { echo "  [FAIL] $*"; ((FAIL++)) || true; }

_file_in_image() {
  local img="$1" path="$2" cid
  cid=$(docker create --platform linux/amd64 "$img" 2>/dev/null)
  CID_LIST+=("$cid")
  docker cp "${cid}:${path}" - >/dev/null 2>&1
  local rc=$?
  docker rm -f "$cid" >/dev/null 2>&1
  CID_LIST=("${CID_LIST[@]/$cid}")
  return $rc
}

cleanup() {
  for cid in "${CID_LIST[@]:-}"; do
    [ -n "$cid" ] && docker rm -f "$cid" >/dev/null 2>&1 || true
  done
  docker rm -f "otelcol-smoke-$$" >/dev/null 2>&1 || true
}
trap cleanup EXIT

echo "=== Smoke: ${IMAGE} ==="

# ---------------------------------------------------------------------------
# 1. gwshield-init banner present
# ---------------------------------------------------------------------------
VERSION_OUT=$(docker run --rm --platform linux/amd64 "$IMAGE" --gws-version 2>&1 || true)
if grep -qi 'otelcol' <<< "$VERSION_OUT"; then
  _pass "banner present: $(echo "$VERSION_OUT" | head -1)"
else
  _fail "banner missing or wrong service: $VERSION_OUT"
fi

# ---------------------------------------------------------------------------
# 2. otelcol-contrib binary present
# ---------------------------------------------------------------------------
if _file_in_image "$IMAGE" /usr/bin/otelcol-contrib; then
  _pass "otelcol-contrib binary present at /usr/bin/otelcol-contrib"
else
  _fail "otelcol-contrib binary missing"
fi

# ---------------------------------------------------------------------------
# 3. gwshield-init binary present
# ---------------------------------------------------------------------------
if _file_in_image "$IMAGE" /usr/local/bin/gwshield-init; then
  _pass "gwshield-init binary present"
else
  _fail "gwshield-init binary missing"
fi

# ---------------------------------------------------------------------------
# 4. --gws-version reports 0.147 and service name otelcol
# ---------------------------------------------------------------------------
if grep -q '0\.147' <<< "$VERSION_OUT" && grep -qi 'otelcol' <<< "$VERSION_OUT"; then
  _pass "version correct: $(echo "$VERSION_OUT" | head -1)"
else
  _fail "version check failed: $VERSION_OUT"
fi

# ---------------------------------------------------------------------------
# 5. No shell in runtime layer
# ---------------------------------------------------------------------------
SHELL_RC=0
docker run --rm --platform linux/amd64 --entrypoint /bin/sh "$IMAGE" -c "echo ok" \
  >/dev/null 2>&1 || SHELL_RC=$?
if [ "$SHELL_RC" -ne 0 ]; then
  _pass "no shell in runtime layer"
else
  _fail "shell found in runtime layer (security violation)"
fi

# ---------------------------------------------------------------------------
# 6. Non-root UID 65532
# ---------------------------------------------------------------------------
CID=$(docker create --platform linux/amd64 "$IMAGE" 2>/dev/null)
UID_OUT=$(docker inspect --format='{{.Config.User}}' "$CID" 2>/dev/null || echo "unknown")
docker rm -f "$CID" >/dev/null 2>&1
if [ "$UID_OUT" = "65532:65532" ]; then
  _pass "non-root user: $UID_OUT"
else
  _fail "unexpected user: $UID_OUT (expected 65532:65532)"
fi

# ---------------------------------------------------------------------------
# 7. Config skeleton present
# ---------------------------------------------------------------------------
if _file_in_image "$IMAGE" /etc/otelcol/config.yaml; then
  _pass "config skeleton present at /etc/otelcol/config.yaml"
else
  _fail "config skeleton missing"
fi

# ---------------------------------------------------------------------------
# 8. Static binary — zero NEEDED entries
# ---------------------------------------------------------------------------
CID=$(docker create --platform linux/amd64 "$IMAGE" 2>/dev/null)
docker cp "${CID}:/usr/bin/otelcol-contrib" /tmp/smoke-otelcol-bin >/dev/null 2>&1
docker rm -f "$CID" >/dev/null 2>&1
NEEDED=$(readelf -d /tmp/smoke-otelcol-bin 2>/dev/null | grep NEEDED || true)
rm -f /tmp/smoke-otelcol-bin
if [ -z "$NEEDED" ]; then
  _pass "static binary — zero NEEDED entries"
else
  _fail "dynamic deps found: $NEEDED"
fi

# ---------------------------------------------------------------------------
# 9. Config validates cleanly
# ---------------------------------------------------------------------------
VALIDATE_OUT=$(docker run --rm --platform linux/amd64 \
  --entrypoint /usr/bin/otelcol-contrib "$IMAGE" \
  validate --config /etc/otelcol/config.yaml 2>&1 || true)
if echo "$VALIDATE_OUT" | grep -qi 'error\|invalid\|fail'; then
  _fail "config validation failed: $VALIDATE_OUT"
else
  _pass "config validates cleanly"
fi

# ---------------------------------------------------------------------------
# 10. Collector starts and health endpoint responds on :13133
# ---------------------------------------------------------------------------
docker network create "otelcol-smoke-net-$$" >/dev/null 2>&1 || true
docker run --rm -d --platform linux/amd64 \
  --name "otelcol-smoke-$$" \
  --network "otelcol-smoke-net-$$" \
  "$IMAGE" 2>/dev/null
sleep 4
HEALTH_RC=0
docker run --rm --network "otelcol-smoke-net-$$" \
  alpine/curl:latest curl -sf "http://otelcol-smoke-$$:13133/" >/dev/null 2>/dev/null || HEALTH_RC=$?
docker rm -f "otelcol-smoke-$$" >/dev/null 2>&1 || true
docker network rm "otelcol-smoke-net-$$" >/dev/null 2>&1 || true
if [ "$HEALTH_RC" -eq 0 ]; then
  _pass "health_check extension responds on :13133"
else
  _fail "health_check endpoint did not respond (rc=${HEALTH_RC})"
fi

# ---------------------------------------------------------------------------
# Result
# ---------------------------------------------------------------------------
echo ""
echo "=== Result: ${PASS} passed, ${FAIL} failed ==="
[ "$FAIL" -eq 0 ]
