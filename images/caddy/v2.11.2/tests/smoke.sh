#!/usr/bin/env bash
# =============================================================================
# Smoke test — caddy:v2.11.2 (standard)
# =============================================================================
#
# Reference implementation using shared/smoke-lib.sh.
# Check metadata (labels, categories, descriptions) lives in smoke.manifest.json.
# This script contains only the test logic — what to run and how to interpret it.
#
# Usage:
#   ./tests/smoke.sh <image_tag>
#
# Output:
#   Console:                  [PASS]/[FAIL]/[SKIP] lines + coloured summary
#   tests/smoke-result.json:  structured JSON written by smoke_end — fed directly
#                             to Supabase via supabase_ingress.py smoke (no parsing)
# =============================================================================
set -euo pipefail

IMAGE="${1:?Usage: smoke.sh <image_tag>}"
MANIFEST="$(dirname "$0")/smoke.manifest.json"

# Load shared library — provides smoke_begin/check_detail/skip/end + helpers
# shellcheck source=../../../../shared/smoke-lib.sh
source "$(dirname "$0")/../../../../shared/smoke-lib.sh"

smoke_begin "$IMAGE" "$MANIFEST"

cleanup() { true; }
trap cleanup EXIT

# ---------------------------------------------------------------------------
# binary_present — caddy binary at /usr/bin/caddy
# ---------------------------------------------------------------------------
smoke_check_detail "binary_present" \
  "$(_file_in_image "$IMAGE" /usr/bin/caddy && echo true || echo false)" \
  "/usr/bin/caddy"

# ---------------------------------------------------------------------------
# version_string — must contain v2.11
# ---------------------------------------------------------------------------
VERSION_OUT=$(docker run --rm --platform linux/amd64 "$IMAGE" version 2>&1 || true)
if echo "$VERSION_OUT" | grep -q "v2\.11"; then
  smoke_check_detail "version_string" true "$(echo "$VERSION_OUT" | head -1)"
else
  smoke_check_detail "version_string" false "$VERSION_OUT"
fi

# ---------------------------------------------------------------------------
# config_validate — caddy validate exits 0 on valid config
# ---------------------------------------------------------------------------
VALIDATE_OUT=$(docker run --rm --platform linux/amd64 "$IMAGE" \
  validate --config /etc/caddy/Caddyfile --adapter caddyfile 2>&1) && VALIDATE_RC=0 || VALIDATE_RC=$?
smoke_check_detail "config_validate" \
  "$([[ $VALIDATE_RC -eq 0 ]] && echo true || echo false)" \
  "${VALIDATE_OUT:-exit 0}"

# ---------------------------------------------------------------------------
# nonroot — must run as 65532:65532
# ---------------------------------------------------------------------------
UID_OUT=$(_uid_of_image "$IMAGE")
smoke_check_detail "nonroot" \
  "$([[ "$UID_OUT" == "65532:65532" ]] && echo true || echo false)" \
  "$UID_OUT"

# ---------------------------------------------------------------------------
# no_shell — /bin/sh must not be executable (FROM scratch)
# ---------------------------------------------------------------------------
smoke_check_detail "no_shell" \
  "$(_shell_absent "$IMAGE" && echo true || echo false)" \
  "entrypoint /bin/sh blocked"

# ---------------------------------------------------------------------------
# static_binary — zero NEEDED entries (CGO_ENABLED=0)
# ---------------------------------------------------------------------------
NEEDED=$(_readelf_needed "$IMAGE" /usr/bin/caddy)
smoke_check_detail "static_binary" \
  "$([[ -z "$NEEDED" ]] && echo true || echo false)" \
  "${NEEDED:-zero NEEDED entries}"

# ---------------------------------------------------------------------------
# ca_bundle — /etc/ssl/certs/ca-certificates.crt
# ---------------------------------------------------------------------------
smoke_check_detail "ca_bundle" \
  "$(_file_in_image "$IMAGE" /etc/ssl/certs/ca-certificates.crt && echo true || echo false)" \
  "/etc/ssl/certs/ca-certificates.crt"

# ---------------------------------------------------------------------------
# config_present — bundled Caddyfile
# ---------------------------------------------------------------------------
smoke_check_detail "config_present" \
  "$(_file_in_image "$IMAGE" /etc/caddy/Caddyfile && echo true || echo false)" \
  "/etc/caddy/Caddyfile"

# ---------------------------------------------------------------------------
# data_dir_present — /data (XDG_DATA_HOME) and /config (XDG_CONFIG_HOME)
# ---------------------------------------------------------------------------
DATA_OK=$(_file_in_image "$IMAGE" /data   && echo true || echo false)
CFG_OK=$( _file_in_image "$IMAGE" /config && echo true || echo false)
smoke_check_detail "data_dir_present" \
  "$([[ "$DATA_OK" == "true" && "$CFG_OK" == "true" ]] && echo true || echo false)" \
  "/data present=$DATA_OK  /config present=$CFG_OK"

# ---------------------------------------------------------------------------
# banner — gwshield-init banner in startup output
# caddy writes banner to stdout via gwshield-init before exec()ing caddy.
# 'caddy version' passes through gwshield-init which prints the banner first.
# ---------------------------------------------------------------------------
BANNER_OUT=$(docker run --rm --platform linux/amd64 "$IMAGE" version 2>&1 || true)
smoke_check_detail "banner" \
  "$(echo "$BANNER_OUT" | grep -qi 'gwshield\|gatewarden' && echo true || echo false)" \
  "$(echo "$BANNER_OUT" | grep -i 'gwshield\|gatewarden' | head -1)"

# ---------------------------------------------------------------------------
smoke_end
