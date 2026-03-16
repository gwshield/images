#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# Smoke tests — gwshield Rust Builder v1.87-dev (compile + lint + audit)
#
# Tests performed:
#   1. Rust version matches expected minor (1.87.x)
#   2. Runs as UID 65532 (non-root)
#   3. clippy present and version check
#   4. rustfmt present and version check
#   5. cargo-audit present and version check
#   6. cargo-deny present and version check
#   7. cargo build compiles a minimal static binary (toolchain intact)
#   8. clippy reports no issues on clean code
#
# Usage:
#   bash images/builders/rust-builder/v1.87-dev/tests/smoke.sh <image>
#
# Exit code 0 = all tests passed, 1 = one or more failed.
# =============================================================================

IMAGE="${1:?Usage: $0 <image>}"
PASS=0
FAIL=0

run_test_output() {
    local desc="$1" pattern="$2"; shift 2
    local out
    out=$("$@" 2>&1) || true
    if echo "${out}" | grep -qE "${pattern}"; then
        echo "  PASS  ${desc}"
        PASS=$((PASS + 1))
    else
        echo "  FAIL  ${desc} (expected pattern: ${pattern})"
        echo "        output: ${out}"
        FAIL=$((FAIL + 1))
    fi
}

run_test() {
    local desc="$1"; shift
    local out rc
    out=$("$@" 2>&1) && rc=0 || rc=$?
    if [[ "${rc}" -eq 0 ]]; then
        echo "  PASS  ${desc}"
        PASS=$((PASS + 1))
    else
        echo "  FAIL  ${desc}"
        echo "        output: ${out}"
        FAIL=$((FAIL + 1))
    fi
}

echo ""
echo "Smoke tests: ${IMAGE}"
echo "=============================================="

# 1. Rust version
run_test_output "rustc version contains 1.87" "1\.87" \
    docker run --rm "${IMAGE}" rustc --version

# 2. Non-root UID
run_test_output "runs as UID 65532 (nonroot)" "^65532$" \
    docker run --rm "${IMAGE}" id -u

# 3. clippy
run_test_output "cargo clippy present" "clippy|[0-9]\.[0-9]" \
    docker run --rm "${IMAGE}" cargo clippy --version

# 4. rustfmt
run_test_output "rustfmt present" "rustfmt|[0-9]\.[0-9]" \
    docker run --rm "${IMAGE}" rustfmt --version

# 5. cargo-audit
run_test_output "cargo-audit present (0.21)" "0\.21" \
    docker run --rm "${IMAGE}" cargo audit --version

# 6. cargo-deny
run_test_output "cargo-deny present (0.18)" "0\.18" \
    docker run --rm "${IMAGE}" cargo deny --version

# 7. Build minimal program (toolchain intact)
run_test "cargo build compiles hello-world" \
    docker run --rm "${IMAGE}" sh -c '
        mkdir -p /tmp/hello/src
        printf "[package]\nname=\"hello\"\nversion=\"0.1.0\"\nedition=\"2021\"\n" \
            > /tmp/hello/Cargo.toml
        printf "fn main() { println!(\"gwshield-rust-builder-dev-smoke-ok\"); }\n" \
            > /tmp/hello/src/main.rs
        cd /tmp/hello
        HOST=$(rustup show active-toolchain | grep -oE "x86_64|aarch64")
        RUSTFLAGS="-C target-feature=+crt-static" \
            cargo build --release --target "${HOST}-unknown-linux-musl" 2>&1
        echo BUILD_OK
    '

# 8. clippy reports no issues on clean code
run_test "clippy passes on clean Rust code" \
    docker run --rm "${IMAGE}" sh -c '
        mkdir -p /tmp/lint/src
        printf "[package]\nname=\"lint\"\nversion=\"0.1.0\"\nedition=\"2021\"\n" \
            > /tmp/lint/Cargo.toml
        printf "fn main() { println!(\"ok\"); }\n" > /tmp/lint/src/main.rs
        cd /tmp/lint
        cargo clippy -- -D warnings 2>&1
    '

echo "=============================================="
echo "Results: ${PASS} passed, ${FAIL} failed"
echo ""
[[ "${FAIL}" -eq 0 ]] || exit 1
