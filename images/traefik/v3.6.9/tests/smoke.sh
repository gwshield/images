#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# Smoke tests for the hardened Traefik v3.6.9 image
#
# Tests performed:
#   1. Container starts and exits cleanly with --help
#   2. Process runs as UID 65532 (non-root)
#   3. No shell present in the runtime layer
#   4. Ping endpoint responds (minimal config mounted)
#   5. Binary reports the expected version string
#
# Usage:
#   ./images/traefik/v3.6.9/tests/smoke.sh <image>
#
# Example:
#   ./images/traefik/v3.6.9/tests/smoke.sh gatewarden/traefik:v3.6.9-hardened
#
# Exit codes:
#   0 — all tests passed
#   1 — one or more tests failed
# =============================================================================

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
IMAGE="${1:?Usage: $0 <image>}"
CONTAINER_NAME="traefik-smoke-$$"
EXPECTED_UID="65532"
PING_PORT="18080"
PING_TIMEOUT=15
CONFIG_FILE="$(cd "$(dirname "$0")/../configs" && pwd)/traefik-minimal.yml"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
PASS=0
FAIL=0

print_result() {
    local status="$1"
    local label="$2"
    local detail="${3:-}"
    if [[ "${status}" == "PASS" ]]; then
        printf "  [PASS] %s\n" "${label}"
        PASS=$(( PASS + 1 ))
    else
        printf "  [FAIL] %s%s\n" "${label}" "${detail:+ — ${detail}}"
        FAIL=$(( FAIL + 1 ))
    fi
}

cleanup() {
    docker rm -f "${CONTAINER_NAME}" >/dev/null 2>&1 || true
    docker rm -f "${CONTAINER_NAME}-run" >/dev/null 2>&1 || true
    docker rm -f "${CONTAINER_NAME}-ping" >/dev/null 2>&1 || true
}
trap cleanup EXIT

# ---------------------------------------------------------------------------
# Pre-flight: image must exist locally
# ---------------------------------------------------------------------------
printf "\n=== Smoke tests: %s ===\n\n" "${IMAGE}"

if ! docker image inspect "${IMAGE}" >/dev/null 2>&1; then
    printf "ERROR: image '%s' not found locally. Build it first.\n" "${IMAGE}" >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Test 1: Container starts and exits cleanly with --help
# ---------------------------------------------------------------------------
if docker run --rm --name "${CONTAINER_NAME}" "${IMAGE}" --help >/dev/null 2>&1; then
    print_result PASS "Container starts and exits cleanly (--help)"
else
    print_result FAIL "Container starts and exits cleanly (--help)"
fi

# ---------------------------------------------------------------------------
# Test 2: Process runs as UID 65532 (non-root)
# ---------------------------------------------------------------------------
# Use a small static tool to check UID — /traefik itself cannot exec id
# Instead we inspect the image USER metadata
IMAGE_USER="$(docker inspect --format='{{.Config.User}}' "${IMAGE}")"
if [[ "${IMAGE_USER}" == "${EXPECTED_UID}:${EXPECTED_UID}" ]] \
|| [[ "${IMAGE_USER}" == "${EXPECTED_UID}" ]]; then
    print_result PASS "Image USER is ${EXPECTED_UID}:${EXPECTED_UID} (non-root)"
else
    print_result FAIL "Image USER is ${EXPECTED_UID}:${EXPECTED_UID}" \
        "got '${IMAGE_USER}'"
fi

# ---------------------------------------------------------------------------
# Test 3: No shell in the runtime layer
# ---------------------------------------------------------------------------
if docker run --rm --name "${CONTAINER_NAME}-run" \
        --entrypoint /bin/sh \
        "${IMAGE}" \
        -c "echo shell_present" >/dev/null 2>&1; then
    print_result FAIL "No shell in runtime layer" "shell found at /bin/sh"
else
    print_result PASS "No shell in runtime layer (/bin/sh absent)"
fi

if docker run --rm --name "${CONTAINER_NAME}-run" \
        --entrypoint /bin/ash \
        "${IMAGE}" \
        -c "echo shell_present" >/dev/null 2>&1; then
    print_result FAIL "No shell in runtime layer" "shell found at /bin/ash"
else
    print_result PASS "No shell in runtime layer (/bin/ash absent)"
fi

# ---------------------------------------------------------------------------
# Test 4: Ping endpoint responds
# ---------------------------------------------------------------------------
if [[ ! -f "${CONFIG_FILE}" ]]; then
    print_result FAIL "Ping endpoint" "config file not found: ${CONFIG_FILE}"
else
    docker run -d \
        --name "${CONTAINER_NAME}-ping" \
        -p "${PING_PORT}:8080" \
        -v "${CONFIG_FILE}:/etc/traefik/traefik.yml:ro" \
        "${IMAGE}" \
        >/dev/null 2>&1

    PING_OK=0
    for _ in $(seq 1 "${PING_TIMEOUT}"); do
        if curl -sf "http://localhost:${PING_PORT}/ping" >/dev/null 2>&1; then
            PING_OK=1
            break
        fi
        sleep 1
    done

    docker stop "${CONTAINER_NAME}-ping" >/dev/null 2>&1 || true

    if [[ "${PING_OK}" -eq 1 ]]; then
        print_result PASS "Ping endpoint responds (http://localhost:${PING_PORT}/ping)"
    else
        print_result FAIL "Ping endpoint" \
            "no response after ${PING_TIMEOUT}s on port ${PING_PORT}"
    fi
fi

# ---------------------------------------------------------------------------
# Test 5: Binary reports expected version string
# ---------------------------------------------------------------------------
VERSION_OUTPUT="$(docker run --rm --name "${CONTAINER_NAME}-run" \
    "${IMAGE}" version 2>&1 || true)"

if echo "${VERSION_OUTPUT}" | grep -q "3.6.9"; then
    print_result PASS "Binary version contains '3.6.9'"
else
    print_result FAIL "Binary version contains '3.6.9'" \
        "output: $(echo "${VERSION_OUTPUT}" | head -3)"
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
printf "\n=== Results: %d passed, %d failed ===\n\n" "${PASS}" "${FAIL}"

if [[ "${FAIL}" -gt 0 ]]; then
    exit 1
fi
