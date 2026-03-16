#!/usr/bin/env bash
# =============================================================================
# Smoke test — pomerium:v0.32.2 (standard)
# =============================================================================
#
# Reference implementation using shared/smoke-lib.sh — distroless/cc-debian12 pattern.
# Check metadata (labels, categories, descriptions) lives in smoke.manifest.json.
# This script contains only the test logic — what to run and how to interpret it.
#
# Usage:  ./tests/smoke.sh <image_tag>
#
# Output:
#   Console:                  [PASS]/[FAIL]/[SKIP] lines + coloured summary
#   tests/smoke-result.json:  structured JSON written by smoke_end — fed directly
#                             to Supabase via supabase_ingress.py smoke (no parsing)
# =============================================================================
set -euo pipefail

IMAGE="${1:?Usage: smoke.sh <image_tag>}"
MANIFEST="$(dirname "$0")/smoke.manifest.json"

# shellcheck source=../../../../shared/smoke-lib.sh
source "$(dirname "$0")/../../../../shared/smoke-lib.sh"

smoke_begin "$IMAGE" "$MANIFEST"

cleanup() { true; }
trap cleanup EXIT

# ---------------------------------------------------------------------------
# banner — --gws-version must mention pomerium
# ---------------------------------------------------------------------------
VERSION_OUT=$(_gws_version_out "$IMAGE")
smoke_check_detail "banner" \
  "$(grep -qi 'pomerium' <<< "$VERSION_OUT" && echo true || echo false)" \
  "$(echo "$VERSION_OUT" | head -1)"

# ---------------------------------------------------------------------------
# binary_present — /bin/pomerium
# ---------------------------------------------------------------------------
smoke_check_detail "binary_present" \
  "$(_file_in_image "$IMAGE" /bin/pomerium && echo true || echo false)" \
  "/bin/pomerium"

# ---------------------------------------------------------------------------
# gwshield_init_present — /usr/local/bin/gwshield-init
# ---------------------------------------------------------------------------
smoke_check_detail "gwshield_init_present" \
  "$(_file_in_image "$IMAGE" /usr/local/bin/gwshield-init && echo true || echo false)" \
  "/usr/local/bin/gwshield-init"

# ---------------------------------------------------------------------------
# version_string — must contain 0.32 and service name pomerium
# ---------------------------------------------------------------------------
VERSION_PASS=false
grep -q '0\.32' <<< "$VERSION_OUT" && grep -qi 'pomerium' <<< "$VERSION_OUT" && VERSION_PASS=true
smoke_check_detail "version_string" "$VERSION_PASS" "$(echo "$VERSION_OUT" | head -1)"

# ---------------------------------------------------------------------------
# no_shell — distroless/cc — /bin/sh must be absent
# ---------------------------------------------------------------------------
smoke_check_detail "no_shell" \
  "$(_shell_absent "$IMAGE" && echo true || echo false)" \
  "entrypoint /bin/sh blocked"

# ---------------------------------------------------------------------------
# nonroot — 65532:65532
# ---------------------------------------------------------------------------
UID_OUT=$(_uid_of_image "$IMAGE")
smoke_check_detail "nonroot" \
  "$([[ "$UID_OUT" == "65532:65532" ]] && echo true || echo false)" \
  "$UID_OUT"

# ---------------------------------------------------------------------------
# ca_bundle — required for OIDC token validation
# ---------------------------------------------------------------------------
smoke_check_detail "ca_bundle" \
  "$(_file_in_image "$IMAGE" /etc/ssl/certs/ca-certificates.crt && echo true || echo false)" \
  "/etc/ssl/certs/ca-certificates.crt"

# ---------------------------------------------------------------------------
# config_present — /pomerium/config.yaml skeleton
# ---------------------------------------------------------------------------
smoke_check_detail "config_present" \
  "$(_file_in_image "$IMAGE" /pomerium/config.yaml && echo true || echo false)" \
  "/pomerium/config.yaml"

# ---------------------------------------------------------------------------
# data_dir_present — /data/autocert (certmagic) + /tmp (Envoy extraction)
# ---------------------------------------------------------------------------
AUTOCERT_OK=$(_file_in_image "$IMAGE" /data/autocert && echo true || echo false)
TMP_OK=$(     _file_in_image "$IMAGE" /tmp           && echo true || echo false)
smoke_check_detail "data_dir_present" \
  "$([[ "$AUTOCERT_OK" == "true" && "$TMP_OK" == "true" ]] && echo true || echo false)" \
  "/data/autocert=$AUTOCERT_OK  /tmp=$TMP_OK (Envoy extraction target)"

# ---------------------------------------------------------------------------
# static_binary — CGO_ENABLED=0, zero NEEDED entries
# ---------------------------------------------------------------------------
NEEDED=$(_readelf_needed "$IMAGE" /bin/pomerium)
smoke_check_detail "static_binary" \
  "$([[ -z "$NEEDED" ]] && echo true || echo false)" \
  "${NEEDED:-zero NEEDED entries (CGO_ENABLED=0 confirmed)}"

# ---------------------------------------------------------------------------
smoke_end
