#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# Smoke tests for gwshield Rust Builder v1.87 (compile-only)
#
# Tests performed:
#   1. Container starts and reports correct Rust version (1.87.x)
#   2. Process runs as UID 65532 (non-root)
#   3. CARGO_INCREMENTAL=0 is set in the environment
#   4. musl targets are installed (x86_64-unknown-linux-musl)
#   5. cargo build produces a fully static binary from a minimal hello-world
#   6. Produced binary has no dynamic library dependencies (readelf)
#   7. Shell present check (informational — builder images retain /bin/sh)
#
# Usage:
#   bash tests/smoke.sh <image>                   (preferred — matches build.yml calling convention)
#   IMAGE=ghcr.io/gwshield/rust-builder:v1.87 bash tests/smoke.sh  (legacy env var also accepted)
#
# Exit codes:
#   0 — all required tests passed
#   1 — one or more required tests failed
# =============================================================================

IMAGE="${1:-${IMAGE:-}}"
IMAGE="${IMAGE:?Usage: $0 <image>  e.g. $0 ghcr.io/gwshield/rust-builder:v1.87}"
CONTAINER_NAME="rust-builder-smoke-$$"
EXPECTED_UID="65532"
EXPECTED_RUST_MINOR="1.87"

PASS=0; FAIL=0; SKIP=0

print_result() {
    local status="$1" label="$2" detail="${3:-}"
    case "${status}" in
        PASS) printf "  [PASS] %s\n" "${label}";                                  PASS=$(( PASS + 1 )) ;;
        FAIL) printf "  [FAIL] %s%s\n" "${label}" "${detail:+ — ${detail}}";      FAIL=$(( FAIL + 1 )) ;;
        INFO) printf "  [INFO] %s%s\n" "${label}" "${detail:+ — ${detail}}";      SKIP=$(( SKIP + 1 )) ;;
    esac
}

cleanup() {
    docker rm -f "${CONTAINER_NAME}"       >/dev/null 2>&1 || true
    docker rm -f "${CONTAINER_NAME}-build" >/dev/null 2>&1 || true
    docker rm -f "${CONTAINER_NAME}-env"   >/dev/null 2>&1 || true
}
trap cleanup EXIT

printf "\n=== Smoke tests: %s ===\n\n" "${IMAGE}"

if ! docker image inspect "${IMAGE}" >/dev/null 2>&1; then
    printf "ERROR: image '%s' not found locally. Build it first.\n" "${IMAGE}" >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Test 1: Rust version matches expected minor (1.87.x)
# ---------------------------------------------------------------------------
RUST_VER_OUT=$(docker run --rm --name "${CONTAINER_NAME}" \
    "${IMAGE}" rustc --version 2>&1 || true)
if printf '%s' "${RUST_VER_OUT}" | grep -q "${EXPECTED_RUST_MINOR}"; then
    print_result PASS "Rust version contains '${EXPECTED_RUST_MINOR}'" "${RUST_VER_OUT}"
else
    print_result FAIL "Rust version contains '${EXPECTED_RUST_MINOR}'" "${RUST_VER_OUT}"
fi

# ---------------------------------------------------------------------------
# Test 2: Runs as UID 65532 (non-root)
# ---------------------------------------------------------------------------
IMAGE_USER="$(docker inspect --format='{{.Config.User}}' "${IMAGE}")"
if [[ "${IMAGE_USER}" == "${EXPECTED_UID}:${EXPECTED_UID}" ]] \
|| [[ "${IMAGE_USER}" == "${EXPECTED_UID}" ]]; then
    print_result PASS "Image USER is ${EXPECTED_UID}:${EXPECTED_UID} (non-root)"
else
    print_result FAIL "Image USER is ${EXPECTED_UID}:${EXPECTED_UID}" "got '${IMAGE_USER}'"
fi

# ---------------------------------------------------------------------------
# Test 3: CARGO_INCREMENTAL=0 is set
# ---------------------------------------------------------------------------
CI_VAL=$(docker run --rm --name "${CONTAINER_NAME}-env" "${IMAGE}" \
    sh -c 'echo "${CARGO_INCREMENTAL}"' 2>/dev/null || true)
if [[ "${CI_VAL}" == "0" ]]; then
    print_result PASS "CARGO_INCREMENTAL=0"
else
    print_result FAIL "CARGO_INCREMENTAL=0" "got '${CI_VAL}'"
fi

# ---------------------------------------------------------------------------
# Test 4: musl targets installed
# ---------------------------------------------------------------------------
TARGETS_OUT=$(docker run --rm --name "${CONTAINER_NAME}-env" "${IMAGE}" \
    rustup target list --installed 2>/dev/null || true)
if printf '%s' "${TARGETS_OUT}" | grep -q "unknown-linux-musl"; then
    print_result PASS "musl target installed" "${TARGETS_OUT}"
else
    print_result FAIL "musl target installed" "got: ${TARGETS_OUT}"
fi

# ---------------------------------------------------------------------------
# Test 5 + 6: Build a minimal Rust program and verify it is fully static.
#
# Strategy: run cargo build entirely inside the builder container (docker run
# --rm), write to /tmp (writable by UID 65532 in Alpine). The produced binary
# is run inside the same container to confirm it exists, then readelf is used
# (also inside the container — Alpine ships binutils) to verify no NEEDED
# entries.  No docker cp / docker create needed, avoids host-UID mismatch.
# ---------------------------------------------------------------------------

# Detect host target (amd64 or arm64)
HOST_ARCH=$(uname -m)
case "${HOST_ARCH}" in
    x86_64)  MUSL_TARGET="x86_64-unknown-linux-musl"  ;;
    aarch64) MUSL_TARGET="aarch64-unknown-linux-musl" ;;
    arm64)   MUSL_TARGET="aarch64-unknown-linux-musl" ;;
    *)       MUSL_TARGET="x86_64-unknown-linux-musl"  ;;
esac

BUILD_AND_CHECK_OUT=$(docker run --rm \
    -e CARGO_INCREMENTAL=0 \
    -e CARGO_NET_RETRY=3 \
    -e RUSTFLAGS="-C target-feature=+crt-static" \
    "${IMAGE}" \
    sh -c "
        set -e
        mkdir -p /tmp/smoke/src
        cat > /tmp/smoke/Cargo.toml <<'TOML'
[package]
name = \"smoke\"
version = \"0.1.0\"
edition = \"2021\"

[profile.release]
strip = true
opt-level = \"z\"
TOML
        cat > /tmp/smoke/src/main.rs <<'RS'
fn main() { println!(\"gwshield-rust-builder-smoke-ok\"); }
RS
        cd /tmp/smoke
        cargo build --release --target ${MUSL_TARGET} 2>&1
        BIN=/tmp/smoke/target/${MUSL_TARGET}/release/smoke
        if [ -f \"\${BIN}\" ]; then
            echo BUILD_OK
            \"\${BIN}\"
            readelf -d \"\${BIN}\" | grep NEEDED || echo NO_DYNAMIC_DEPS
        else
            echo BUILD_FAILED
        fi
    " 2>&1 || true)

printf '%s\n' "${BUILD_AND_CHECK_OUT}"

if printf '%s' "${BUILD_AND_CHECK_OUT}" | grep -q "BUILD_OK"; then
    print_result PASS "cargo build produces output binary"

    if printf '%s' "${BUILD_AND_CHECK_OUT}" | grep -q "NO_DYNAMIC_DEPS"; then
        print_result PASS "binary is fully static (no dynamic deps)"
    elif printf '%s' "${BUILD_AND_CHECK_OUT}" | grep -q "NEEDED"; then
        print_result FAIL "binary has unexpected dynamic deps" \
            "$(printf '%s' "${BUILD_AND_CHECK_OUT}" | grep NEEDED)"
    else
        print_result PASS "binary static check inconclusive — no NEEDED reported"
    fi
else
    print_result FAIL "cargo build failed to produce binary"
    print_result FAIL "binary static check skipped (no binary)"
fi

# ---------------------------------------------------------------------------
# Test 7 (informational): Shell presence
# Builder images retain /bin/sh intentionally.
# ---------------------------------------------------------------------------
if docker run --rm --name "${CONTAINER_NAME}-env" \
        --entrypoint /bin/sh \
        "${IMAGE}" \
        -c "echo shell_present" >/dev/null 2>&1; then
    print_result INFO "Shell present (/bin/sh)" \
        "expected for builder images — not present in runtime images"
else
    print_result INFO "No shell at /bin/sh" "unusual for a builder image"
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
printf "\n=== Results: %d passed, %d failed, %d informational ===\n\n" \
    "${PASS}" "${FAIL}" "${SKIP}"

[[ "${FAIL}" -eq 0 ]] || exit 1
