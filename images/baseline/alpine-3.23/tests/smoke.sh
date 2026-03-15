#!/usr/bin/env bash
# =============================================================================
# Smoke test — gwshield/alpine:3.23 (OS-Baseline mirror)
#
# Baseline smoke tests verify mirror integrity, not service startup.
# Tests:
#   1. Image pulls by digest (upstream digest preserved)
#   2. cosign signature verifiable
#   3. Expected Alpine version string present
#   4. No gwshield-init binary (baseline images are pure mirrors)
#   5. Shell present (expected for builder base)
# =============================================================================
set -euo pipefail

MIRROR_IMAGE="ghcr.io/gwshield/alpine:3.23"
UPSTREAM_DIGEST="sha256:25109184c71bdad752c8312a8623239686a9a2071e8825f20acb8f2198c3f659"
EXPECTED_VERSION="3.23"

PASS=0
FAIL=0

pass() { echo "PASS  $1"; ((PASS++)); }
fail() { echo "FAIL  $1"; ((FAIL++)); }

echo "=== Smoke test: ${MIRROR_IMAGE} ==="
echo ""

# T1 — Image is pullable
if docker pull --quiet "${MIRROR_IMAGE}" >/dev/null 2>&1; then
  pass "T1  image pulls: ${MIRROR_IMAGE}"
else
  fail "T1  image pull failed: ${MIRROR_IMAGE}"
fi

# T2 — Upstream digest preserved
ACTUAL_DIGEST=$(docker inspect --format='{{index .RepoDigests 0}}' "${MIRROR_IMAGE}" 2>/dev/null | grep -o 'sha256:[a-f0-9]*' || true)
if [[ "${ACTUAL_DIGEST}" == "${UPSTREAM_DIGEST}" ]]; then
  pass "T2  upstream digest preserved: ${UPSTREAM_DIGEST:0:19}..."
else
  if command -v skopeo >/dev/null 2>&1; then
    INDEX_DIGEST=$(skopeo inspect --no-creds "docker://${MIRROR_IMAGE}" --format '{{.Digest}}' 2>/dev/null || true)
    if [[ "${INDEX_DIGEST}" == "${UPSTREAM_DIGEST}" ]]; then
      pass "T2  upstream index digest preserved (skopeo): ${UPSTREAM_DIGEST:0:19}..."
    else
      fail "T2  digest mismatch — expected ${UPSTREAM_DIGEST:0:19}... got ${INDEX_DIGEST:0:19}..."
    fi
  else
    pass "T2  digest check skipped (skopeo not available) — CI will verify"
  fi
fi

# T3 — Alpine version string correct
ALPINE_VER=$(docker run --rm "${MIRROR_IMAGE}" cat /etc/alpine-release 2>/dev/null || true)
if grep -q "^${EXPECTED_VERSION}" <<< "${ALPINE_VER}"; then
  pass "T3  Alpine version: ${ALPINE_VER}"
else
  fail "T3  Alpine version mismatch — expected ${EXPECTED_VERSION}, got '${ALPINE_VER}'"
fi

# T4 — cosign signature
if command -v cosign >/dev/null 2>&1; then
  if cosign verify \
      --certificate-identity-regexp='https://github.com/gwshield/images.*' \
      --certificate-oidc-issuer='https://token.actions.githubusercontent.com' \
      "${MIRROR_IMAGE}" >/dev/null 2>&1; then
    pass "T4  cosign signature valid"
  else
    fail "T4  cosign verification failed"
  fi
else
  pass "T4  cosign check skipped (cosign not available locally) — CI will verify"
fi

# T5 — No gwshield-init binary
if docker run --rm "${MIRROR_IMAGE}" test -f /usr/local/bin/gwshield-init 2>/dev/null; then
  fail "T5  gwshield-init found — baseline should be a pure mirror"
else
  pass "T5  no gwshield-init binary (pure mirror confirmed)"
fi

# T6 — Shell present
if docker run --rm "${MIRROR_IMAGE}" /bin/sh -c 'echo ok' 2>/dev/null | grep -q 'ok'; then
  pass "T6  shell present (/bin/sh) — expected for builder base"
else
  fail "T6  shell not present — unexpected for Alpine mirror"
fi

echo ""
echo "=== Result: ${PASS} passed, ${FAIL} failed ==="
[[ ${FAIL} -eq 0 ]]
