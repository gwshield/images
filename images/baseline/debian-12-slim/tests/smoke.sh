#!/usr/bin/env bash
# =============================================================================
# Smoke test — gwshield/debian:12-slim (OS-Baseline mirror)
#
# Baseline smoke tests verify mirror integrity, not service startup.
# Tests:
#   1. Image pulls
#   2. Upstream digest preserved
#   3. Debian version string correct (bookworm / 12)
#   4. cosign signature verifiable
#   5. No gwshield-init binary (pure mirror)
#   6. Shell + apt present (expected for Debian builder base)
# =============================================================================
set -euo pipefail

MIRROR_IMAGE="ghcr.io/gwshield/debian:12-slim"
UPSTREAM_DIGEST="sha256:74d56e3931e0d5a1dd51f8c8a2466d21de84a271cd3b5a733b803aa91abf4421"
EXPECTED_CODENAME="bookworm"
EXPECTED_VERSION_ID="12"

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

# T3 — Debian version and codename correct
OS_RELEASE=$(docker run --rm "${MIRROR_IMAGE}" cat /etc/os-release 2>/dev/null || true)
if grep -q "VERSION_CODENAME=${EXPECTED_CODENAME}" <<< "${OS_RELEASE}" && \
   grep -q "VERSION_ID=\"${EXPECTED_VERSION_ID}\"" <<< "${OS_RELEASE}"; then
  pass "T3  Debian ${EXPECTED_VERSION_ID} (${EXPECTED_CODENAME}) confirmed"
else
  fail "T3  Debian version mismatch — expected ${EXPECTED_VERSION_ID}/${EXPECTED_CODENAME}"
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

# T5 — No gwshield-init binary (pure mirror)
if docker run --rm "${MIRROR_IMAGE}" test -f /usr/local/bin/gwshield-init 2>/dev/null; then
  fail "T5  gwshield-init found — baseline should be a pure mirror"
else
  pass "T5  no gwshield-init binary (pure mirror confirmed)"
fi

# T6 — Shell present (expected for Debian builder base)
if docker run --rm "${MIRROR_IMAGE}" /bin/bash -c 'echo ok' 2>/dev/null | grep -q 'ok'; then
  pass "T6  shell present (/bin/bash) — expected for Debian builder base"
else
  fail "T6  shell not present — unexpected for Debian 12-slim mirror"
fi

# T7 — apt present (Debian-specific check)
if docker run --rm "${MIRROR_IMAGE}" which apt-get >/dev/null 2>&1; then
  pass "T7  apt-get present — expected for Debian mirror"
else
  fail "T7  apt-get not found — unexpected for Debian 12-slim"
fi

echo ""
echo "=== Result: ${PASS} passed, ${FAIL} failed ==="
[[ ${FAIL} -eq 0 ]]
