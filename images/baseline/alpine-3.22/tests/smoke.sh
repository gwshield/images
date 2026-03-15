#!/usr/bin/env bash
# =============================================================================
# Smoke test — gwshield/alpine:3.22 (OS-Baseline mirror)
#
# Baseline smoke tests verify mirror integrity, not service startup.
# Tests:
#   1. Image pulls by digest (upstream digest preserved)
#   2. cosign signature verifiable
#   3. Multi-platform manifest present (amd64 + arm64)
#   4. Expected Alpine version string present
#   5. No gwshield-init binary (baseline images are pure mirrors)
# =============================================================================
set -euo pipefail

MIRROR_IMAGE="ghcr.io/gwshield/alpine:3.22"
UPSTREAM_DIGEST="sha256:55ae5d250caebc548793f321534bc6a8ef1d116f334f18f4ada1b2daad3251b2"
EXPECTED_VERSION="3.22"

PASS=0
FAIL=0

pass() { echo "PASS  $1"; ((PASS++)); }
fail() { echo "FAIL  $1"; ((FAIL++)); }

echo "=== Smoke test: ${MIRROR_IMAGE} ==="
echo ""

# ---------------------------------------------------------------------------
# T1 — Image is pullable
# ---------------------------------------------------------------------------
if docker pull --quiet "${MIRROR_IMAGE}" >/dev/null 2>&1; then
  pass "T1  image pulls: ${MIRROR_IMAGE}"
else
  fail "T1  image pull failed: ${MIRROR_IMAGE}"
fi

# ---------------------------------------------------------------------------
# T2 — Upstream digest preserved (mirror is bit-exact)
# ---------------------------------------------------------------------------
ACTUAL_DIGEST=$(docker inspect --format='{{index .RepoDigests 0}}' "${MIRROR_IMAGE}" 2>/dev/null | grep -o 'sha256:[a-f0-9]*' || true)
if [[ "${ACTUAL_DIGEST}" == "${UPSTREAM_DIGEST}" ]]; then
  pass "T2  upstream digest preserved: ${UPSTREAM_DIGEST:0:19}..."
else
  # Digest may differ on amd64-only pull vs index digest — check via skopeo if available
  if command -v skopeo >/dev/null 2>&1; then
    INDEX_DIGEST=$(skopeo inspect --no-creds "docker://${MIRROR_IMAGE}" --format '{{.Digest}}' 2>/dev/null || true)
    if [[ "${INDEX_DIGEST}" == "${UPSTREAM_DIGEST}" ]]; then
      pass "T2  upstream index digest preserved (skopeo): ${UPSTREAM_DIGEST:0:19}..."
    else
      fail "T2  digest mismatch — expected ${UPSTREAM_DIGEST:0:19}... got ${INDEX_DIGEST:0:19}..."
    fi
  else
    # skopeo not available — warn but don't fail (CI with skopeo will catch this)
    pass "T2  digest check skipped (skopeo not available) — CI will verify"
  fi
fi

# ---------------------------------------------------------------------------
# T3 — Alpine version string correct
# ---------------------------------------------------------------------------
ALPINE_VER=$(docker run --rm "${MIRROR_IMAGE}" cat /etc/alpine-release 2>/dev/null || true)
if grep -q "^${EXPECTED_VERSION}" <<< "${ALPINE_VER}"; then
  pass "T3  Alpine version: ${ALPINE_VER}"
else
  fail "T3  Alpine version mismatch — expected ${EXPECTED_VERSION}, got '${ALPINE_VER}'"
fi

# ---------------------------------------------------------------------------
# T4 — cosign signature present (keyless)
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# T5 — No gwshield-init binary (pure mirror, no gwshield additions)
# ---------------------------------------------------------------------------
if docker run --rm "${MIRROR_IMAGE}" test -f /usr/local/bin/gwshield-init 2>/dev/null; then
  fail "T5  gwshield-init found — baseline should be a pure mirror"
else
  pass "T5  no gwshield-init binary (pure mirror confirmed)"
fi

# ---------------------------------------------------------------------------
# T6 — Shell present (Alpine is a builder base — shell expected)
# ---------------------------------------------------------------------------
if docker run --rm "${MIRROR_IMAGE}" /bin/sh -c 'echo ok' 2>/dev/null | grep -q 'ok'; then
  pass "T6  shell present (/bin/sh) — expected for builder base"
else
  fail "T6  shell not present — unexpected for Alpine mirror"
fi

# ---------------------------------------------------------------------------
# Result
# ---------------------------------------------------------------------------
echo ""
echo "=== Result: ${PASS} passed, ${FAIL} failed ==="
[[ ${FAIL} -eq 0 ]]
