#!/usr/bin/env bash
# =============================================================================
# Smoke test — gwshield-nats v2.12.5 (standard)
# =============================================================================
#
# Validates the built image before promotion:
#   1.  gwshield-init banner present (nats in --gws-version output)
#   2.  nats-server binary present at /usr/bin/nats-server
#   3.  gwshield-init binary present at /usr/local/bin/gwshield-init
#   4.  --gws-version reports correct version (2.12) and service name
#   5.  No shell in runtime layer (/bin/sh absent)
#   6.  Non-root UID 65532
#   7.  Config skeleton present (/etc/nats/nats.conf)
#   8.  /data/jetstream directory present
#   9.  Static binary — zero NEEDED entries
#   10. Server starts and monitoring endpoint responds on :8222/healthz
#
# Usage: ./tests/smoke.sh <image_tag>
# =============================================================================
set -euo pipefail

IMAGE="${1:-gwshield-nats:v2.12.5}"
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
  docker rm -f "nats-smoke-$$" >/dev/null 2>&1 || true
  docker network rm "nats-smoke-net-$$" >/dev/null 2>&1 || true
}
trap cleanup EXIT

echo "=== Smoke: ${IMAGE} ==="

# ---------------------------------------------------------------------------
# 1. gwshield-init banner present
# ---------------------------------------------------------------------------
VERSION_OUT=$(docker run --rm --platform linux/amd64 "$IMAGE" --gws-version 2>&1 || true)
if grep -qi 'nats' <<< "$VERSION_OUT"; then
  _pass "banner present: $(echo "$VERSION_OUT" | head -1)"
else
  _fail "banner missing or wrong service: $VERSION_OUT"
fi

# ---------------------------------------------------------------------------
# 2. nats-server binary present
# ---------------------------------------------------------------------------
if _file_in_image "$IMAGE" /usr/bin/nats-server; then
  _pass "nats-server binary present at /usr/bin/nats-server"
else
  _fail "nats-server binary missing"
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
# 4. --gws-version reports 2.12 and service name nats
# ---------------------------------------------------------------------------
if grep -q '2\.12' <<< "$VERSION_OUT" && grep -qi 'nats' <<< "$VERSION_OUT"; then
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
if _file_in_image "$IMAGE" /etc/nats/nats.conf; then
  _pass "config skeleton present at /etc/nats/nats.conf"
else
  _fail "config skeleton missing"
fi

# ---------------------------------------------------------------------------
# 8. /data/jetstream directory present
# ---------------------------------------------------------------------------
if _file_in_image "$IMAGE" /data/jetstream; then
  _pass "/data/jetstream directory present"
else
  _fail "/data/jetstream directory missing"
fi

# ---------------------------------------------------------------------------
# 9. Static binary — zero NEEDED entries
# ---------------------------------------------------------------------------
CID=$(docker create --platform linux/amd64 "$IMAGE" 2>/dev/null)
docker cp "${CID}:/usr/bin/nats-server" /tmp/smoke-nats-bin >/dev/null 2>&1
docker rm -f "$CID" >/dev/null 2>&1
NEEDED=$(readelf -d /tmp/smoke-nats-bin 2>/dev/null | grep NEEDED || true)
rm -f /tmp/smoke-nats-bin
if [ -z "$NEEDED" ]; then
  _pass "static binary — zero NEEDED entries"
else
  _fail "dynamic deps found: $NEEDED"
fi

# ---------------------------------------------------------------------------
# 10. Server starts and monitoring /healthz responds on :8222
# ---------------------------------------------------------------------------
docker network create "nats-smoke-net-$$" >/dev/null 2>&1 || true
# Note: no --rm so we can capture logs on failure; cleanup trap handles removal
docker run -d --platform linux/amd64 \
  --name "nats-smoke-$$" \
  --network "nats-smoke-net-$$" \
  --tmpfs "/data/jetstream:uid=65532,gid=65532" \
  "$IMAGE" 2>/dev/null
sleep 5
HEALTH_RC=0
HEALTH_OUT=$(docker run --rm --network "nats-smoke-net-$$" \
  alpine/curl:latest curl -sf "http://nats-smoke-$$:8222/healthz" 2>/dev/null) || HEALTH_RC=$?
if [ "$HEALTH_RC" -ne 0 ]; then
  echo "  [DEBUG] NATS server logs:"
  docker logs "nats-smoke-$$" 2>&1 | tail -20 || true
fi
docker rm -f "nats-smoke-$$" >/dev/null 2>&1 || true
docker network rm "nats-smoke-net-$$" >/dev/null 2>&1 || true
if [ "$HEALTH_RC" -eq 0 ]; then
  _pass "monitoring /healthz responds on :8222 — output: ${HEALTH_OUT}"
else
  _fail "monitoring endpoint did not respond (rc=${HEALTH_RC})"
fi

# ---------------------------------------------------------------------------
# Result
# ---------------------------------------------------------------------------
echo ""
echo "=== Result: ${PASS} passed, ${FAIL} failed ==="
[ "$FAIL" -eq 0 ]
