#!/usr/bin/env python3
# =============================================================================
# supabase_ingress.py — Pipeline → Supabase writeback
#
# Writes promoted image metadata and CVE scan results into the gwshield-hub
# Supabase instance. Acts as the bridge between the gwshield/images promotion
# pipeline and the Supabase single source of truth.
#
# Subcommands:
#   promote   — upsert image/version/snapshot after a successful promote
#   scan      — update CVE counts + write cve_findings on the latest snapshot
#   findings  — write structured CVE findings for a specific image version
#               (used by rescan-origin pipeline and manual backfill)
#
# Multi-platform support (migration 0053):
#   The promote subcommand accepts --platforms (JSON array of OCI platform
#   strings, e.g. '["linux/amd64","linux/arm64"]') and per-platform size
#   fields (--image-size-json, --runnable-size-json, --sbom-refs-json,
#   --provenance-refs-json). When platforms are supplied, one
#   image_metadata_snapshots row is written per platform instead of a single
#   row. The image_versions.platforms column is populated with the full list.
#
#   Backward compatibility: when --platforms is omitted the script falls back
#   to the previous single-row snapshot behaviour so existing callers continue
#   to work unmodified.
#
# Suppressed CVE transparency:
#   The scan and findings subcommands accept an optional --allowlist-json
#   argument. When provided, suppressed CVE entries (produced by
#   gen-trivyignore.py --emit-findings-json) are merged with the real Trivy
#   findings before the Supabase write. Suppressed entries carry
#   is_suppressed=true and the full allowlist rationale.
#
#   The suppression_* columns (is_suppressed, suppression_reason,
#   suppression_detail, suppression_evidence, review_date) are written
#   conditionally — write_findings() probes for column existence and falls
#   back silently to the current schema if migration 0044 is not yet applied.
#   This keeps the pipeline forward-compatible with the Hub migration schedule.
#
# Usage:
#   python3 scripts/supabase_ingress.py promote \
#     --name postgres --version v15.17-tls \
#     --base-version v15.17 --profile tls \
#     --image-type service \
#     --digest sha256:abc123 \
#     --tags "ghcr.io/gwshield/postgres:v15.17-tls" \
#     --cosign-identity "https://github.com/gwshield/images/..." \
#     --promoted-at "2026-03-09T12:00:00Z" \
#     --platforms '["linux/amd64","linux/arm64"]' \
#     --image-size-json '{"linux/amd64":12345678,"linux/arm64":12100000}' \
#     --runnable-size-json '{"linux/amd64":26000000,"linux/arm64":25900000}' \
#     --sbom-refs-json '{"linux/amd64":"ghcr.io/gwshield/postgres:v15.17-tls@sha256:aaa","linux/arm64":"ghcr.io/gwshield/postgres:v15.17-tls@sha256:bbb"}'
#
#   python3 scripts/supabase_ingress.py scan \
#     --name postgres --version v15.17-tls \
#     --cve-total 0 --cve-critical 0 --cve-high 0 \
#     --scanner trivy --scanned-at "2026-03-09T12:00:00Z" \
#     --findings-json '[{"cve_id":"CVE-2025-5244","severity":"HIGH",...}]'
#
#   python3 scripts/supabase_ingress.py findings \
#     --name rust-builder --version v1.87 \
#     --findings-json /path/to/trivy-results.json \
#     --findings-format trivy
#
# Environment variables (set as GitHub Actions secrets):
#   SUPABASE_URL                https://bgxstxpcfrvdvlbzmiek.supabase.co
#   SUPABASE_SERVICE_ROLE_KEY   <service role key — never the anon key>
#
# Slug derivation (authoritative — matches gwshield-hub seed-images.ts):
#   traefik            → traefik
#   nginx / ""         → nginx-http
#   nginx / http2      → nginx-http2
#   nginx / http3      → nginx-http3
#   redis / ""         → redis
#   redis / tls        → redis-tls
#   redis / cluster    → redis-cluster
#   redis / cli        → redis-cli
#   postgres / ""      → postgres-v15 or postgres-v17 (derived from base_version)
#   postgres / tls     → postgres-v15-tls  (etc.)
#   go-builder / ""    → go-builder
#   go-builder / dev   → go-builder-dev
#   python-builder/v3.12     → python-builder-v312
#   python-builder/v3.12-dev → python-builder-v312-dev
#   python-builder/v3.13     → python-builder-v313
#   python-builder/v3.13-dev → python-builder-v313-dev
#   rust-builder / ""  → rust-builder
#   rust-builder / dev → rust-builder-dev
#   caddy / ""         → caddy
#   caddy / cloudflare → caddy-cloudflare
#   haproxy / ""       → haproxy
#   haproxy / ssl      → haproxy-ssl
#
# image_type (migration 0033) — valid values + authority:
#   'service'  — production-ready application/service images (default)
#   'builder'  — build-time base images used in multi-stage pipelines
#   'tooling'  — CLI utilities and admin/ops tooling images
#
#   Priority: --image-type CLI arg > derive_image_type() auto-detection
#   Insert-only: image_type is written ONLY on first insert. On conflict
#   (slug already exists) image_type is NEVER overwritten — admin overrides
#   in the Hub remain the authority. All other non-protected fields are
#   updated normally (name, summary, source_type, visibility, status).
# =============================================================================

import argparse
import json
import os
import pathlib
import re
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone

# Valid image_type values — must match DB CHECK constraint (migration 0033)
_VALID_IMAGE_TYPES = {"service", "builder", "tooling"}


# ---------------------------------------------------------------------------
# Slug derivation — must match gwshield-hub seed-images.ts CATALOG slugs
# ---------------------------------------------------------------------------


def derive_slug(name: str, profile: str, base_version: str) -> str:
    """
    Derive the Supabase slug from pipeline fields.
    Hub-side slugs are authoritative; this function must stay in sync with
    seed-images.ts CATALOG definitions in gwshield-hub.
    """
    p = profile.strip()

    if name == "nginx":
        if p == "" or p == "http":
            return "nginx-http"
        return f"nginx-{p}"

    if name == "postgres":
        bv = base_version.lstrip("v")
        if "." in bv:
            major_num = bv.split(".")[0]
            major = f"-v{major_num}"
        else:
            major = ""
        if p == "":
            return f"postgres{major}"
        return f"postgres{major}-{p}"

    if name == "python-builder":
        # Hub slugs for python-builder always embed the version number:
        #   python-builder-v312        python-builder-v312-dev
        #   python-builder-v313        python-builder-v313-dev
        #
        # release-public.yml dispatches one of two shapes:
        #   profile=""      base_version="v3.12"    (canonical build)
        #   profile="dev"   base_version="v3.12"    (dev build)
        #   profile="v3.12" base_version="v3.12"    (explicit, legacy)
        #   profile="v3.12-dev" base_version="v3.12" (explicit, legacy)
        #
        # Strategy: always build slug from base_version + optional non-version suffix.
        #   1. Normalise base_version → "v312"
        #   2. Strip any version-like prefix from profile to get the pure suffix
        #      (e.g. "dev" stays "dev"; "v3.12" → ""; "v3.12-dev" → "dev")
        #   3. Combine: "python-builder-v312" or "python-builder-v312-dev"
        bv_norm = (
            re.sub(r"v(\d+)\.(\d+)", r"v\1\2", base_version) if base_version else ""
        )
        # Strip version prefix from profile (handles legacy explicit profiles)
        suffix = re.sub(r"^v\d+\.\d+", "", p).lstrip("-")
        if not bv_norm:
            # No base_version at all — bare name or bare suffix
            return f"python-builder-{suffix}" if suffix else "python-builder"
        return (
            f"python-builder-{bv_norm}-{suffix}"
            if suffix
            else f"python-builder-{bv_norm}"
        )

    if name == "go-builder":
        # Hub slugs always embed the version number — same pattern as python-builder:
        #   go-builder-v124        go-builder-v124-dev
        #   go-builder-v125        go-builder-v125-dev
        # Without versioned slugs, v1.24 and v1.25 collapse onto the same DB row
        # and the Hub cannot render them as separate version groups.
        bv_norm = (
            re.sub(r"v(\d+)\.(\d+)", r"v\1\2", base_version) if base_version else ""
        )
        suffix = re.sub(r"^v\d+\.\d+", "", p).lstrip("-")
        # "compile" is the internal canonical name → no suffix in slug
        if suffix == "compile":
            suffix = ""
        if not bv_norm:
            return f"go-builder-{suffix}" if suffix else "go-builder"
        return f"go-builder-{bv_norm}-{suffix}" if suffix else f"go-builder-{bv_norm}"

    if name == "rust-builder":
        # Same versioned-slug pattern as go-builder / python-builder:
        #   rust-builder-v187        rust-builder-v187-dev
        bv_norm = (
            re.sub(r"v(\d+)\.(\d+)", r"v\1\2", base_version) if base_version else ""
        )
        suffix = re.sub(r"^v\d+\.\d+", "", p).lstrip("-")
        if suffix == "compile":
            suffix = ""
        if not bv_norm:
            return f"rust-builder-{suffix}" if suffix else "rust-builder"
        return (
            f"rust-builder-{bv_norm}-{suffix}" if suffix else f"rust-builder-{bv_norm}"
        )

    # Default: name + optional profile suffix
    if p == "":
        return name
    return f"{name}-{p}"


def derive_profile_tag(name: str, profile: str) -> str:
    """
    Map the raw pipeline profile to the Hub-facing profile tag value.

    The pipeline uses short names like "http" (nginx canonical) and "compile"
    (go-builder canonical) internally.  The Hub's isPrimaryProfile() treats
    profile=null and profile="standard" as the primary/parent row.  This
    function normalises canonical profiles to "standard" so that the Hub
    renders them correctly as parent rows without any Hub-side code changes.

    Canonical → standard mappings:
      nginx       "" or "http"    → "standard"   (HTTP is the base nginx profile)
      go-builder  "" or "compile" → "standard"   (compile is the base go-builder profile)
      rust-builder "" or "compile"→ "standard"   (compile is the base rust-builder profile)
      All others: profile passed through unchanged.

    Returns "" (falsy) when the raw profile is empty and there is no canonical
    mapping, so callers can use `if profile_tag:` to skip writing the tag.
    """
    p = profile.strip()

    if name == "nginx":
        if p == "" or p == "http":
            return "standard"
        return p

    if name in ("go-builder", "rust-builder"):
        if p == "" or p == "compile":
            return "standard"
        return p

    return p


def derive_image_type(name: str, profile: str) -> str:
    """
    Auto-detect image_type from name + profile (migration 0033 fallback).

    Used when --image-type is not passed explicitly. The CLI arg always
    takes priority over this function.

    Values (enforced by DB CHECK constraint):
      'builder'  — build-time base images used in multi-stage pipelines
      'tooling'  — CLI utilities and admin/ops tooling images
      'service'  — production-ready application/service images (default)
    """
    _BUILDER_FAMILIES = {"go-builder", "python-builder", "rust-builder"}
    if name in _BUILDER_FAMILIES:
        return "builder"

    # Tooling images — identified by 'cli' profile
    # Covers redis-cli, postgres-cli (and any future cli profile)
    if profile.strip() == "cli":
        return "tooling"

    return "service"


def resolve_image_type(cli_arg: str | None, name: str, profile: str) -> str:
    """
    Resolve the final image_type to use.

    Priority:
      1. --image-type CLI argument (explicit, validated upstream)
      2. derive_image_type() auto-detection (fallback)
    """
    if cli_arg:
        return cli_arg
    return derive_image_type(name, profile)


def derive_source_type(name: str) -> str:
    if "builder" in name:
        return "base"
    return "dockerfile"


def derive_summary(name: str, profile: str, base_version: str) -> str:
    bv = base_version or ""
    p = profile.strip()
    label = f"{name} {bv}" + (f" ({p})" if p else "")
    return f"Hardened {label} image — 0 CVEs"


def derive_os_tag(name: str) -> str:
    """
    Derive the base OS for image_tags.

    - Builder images based on golang/rust/python alpine → 'alpine'
    - Runtime images built on Alpine musl → 'alpine'
    - Distroless-based images (postgres) → 'distroless'
    - Scratch-based images (caddy, traefik) → 'scratch'
    """
    _DISTROLESS = {"postgres"}
    _SCRATCH = {"caddy", "traefik"}

    if name in _DISTROLESS:
        return "distroless"
    if name in _SCRATCH:
        return "scratch"
    return "alpine"


def derive_version_group(version_string: str) -> str:
    """
    Derive the version group tag value from a full version string.

    The version group is used as tag_key='version' in image_tags and drives
    sub-grouping in the Hub catalog list view.

    Heuristic (matches Hub's extractVersionGroup() convention):
      Major >= 10 → only Major          (e.g. postgres v15.17 → "15")
      Major <  10 → Major.Minor         (e.g. python  v3.12.4 → "3.12")

    Examples:
      'v15.17'   → '15'
      'v7.4.8'   → '7.4'
      'v3.12.4'  → '3.12'
      '1.28.2'   → '1.28'
      'v3.6.9'   → '3.6'
      'v2.11.2'  → '2.11'
      'v3.1.16'  → '3.1'
      'v1.87'    → '1.87'
    """
    s = version_string.lstrip("v")
    parts = s.split(".")
    major = int(parts[0])
    minor = int(parts[1]) if len(parts) > 1 else None
    if major >= 10:
        return str(major)
    if minor is not None:
        return f"{major}.{minor}"
    return str(major)


# ---------------------------------------------------------------------------
# Platform helpers (migration 0053)
# ---------------------------------------------------------------------------


def parse_platforms(platforms_json: str | None) -> list[str]:
    """
    Parse the --platforms JSON argument into a list of OCI platform strings.

    Accepts:
      '["linux/amd64","linux/arm64"]'  -> ["linux/amd64", "linux/arm64"]
      '"linux/amd64"'                  -> ["linux/amd64"]  (single string)
      None / ""                        -> []  (single-arch legacy mode)

    Returns an empty list when platforms_json is absent — callers treat []
    as "legacy single-row mode" and fall back to the pre-0053 path.
    """
    if not platforms_json:
        return []
    data = json.loads(platforms_json)
    if isinstance(data, str):
        return [data] if data else []
    if isinstance(data, list):
        return [str(p) for p in data if p]
    return []


def parse_size_map(size_json: str | None) -> dict[str, int]:
    """
    Parse a per-platform size JSON map.

    Accepts:
      '{"linux/amd64":12345678,"linux/arm64":12100000}'
      None / ""  -> {}

    Values are coerced to int; null values are dropped.
    """
    if not size_json:
        return {}
    data = json.loads(size_json)
    return {k: int(v) for k, v in data.items() if v is not None}


def parse_ref_map(ref_json: str | None) -> dict[str, str]:
    """
    Parse a per-platform OCI ref JSON map.

    Accepts:
      '{"linux/amd64":"ghcr.io/gwshield/redis:v7.4.8@sha256:aaa","linux/arm64":"..."}'
      None / ""  -> {}
    """
    if not ref_json:
        return {}
    data = json.loads(ref_json)
    return {k: str(v) for k, v in data.items() if v}


# ---------------------------------------------------------------------------
# CVE findings extraction from Trivy JSON output
# ---------------------------------------------------------------------------


def _build_layer_index(diff_ids: list[str], history: list) -> dict[str, str]:
    """
    Build a mapping from DiffID → 'base_image' | 'builder_stage'.

    Strategy: walk the image history in order, assigning each non-empty layer
    to a DiffID. Layers whose created_by command contains our gwshield build
    markers (GWS_SERVICE, addgroup nonroot, apk upgrade with our cache id) are
    'builder_stage'. Everything before the first gwshield marker is 'base_image'.
    """
    _GWSHIELD_MARKERS = (
        "GWS_SERVICE",
        "GWS_VERSION",
        "GWS_PROFILE",
        "addgroup",
        "nonroot",
        "apk-rust-builder",
        "apk-go-builder",
        "apk-python-builder",
        "apk-nginx",
        "apk-redis",
        "apk-postgres",
    )

    result = {}
    non_empty = [h for h in history if not h.get("empty_layer")]

    for idx, diff_id in enumerate(diff_ids):
        if idx >= len(non_empty):
            result[diff_id] = "base_image"
            continue
        cmd = non_empty[idx].get("created_by", "")
        if any(m in cmd for m in _GWSHIELD_MARKERS):
            result[diff_id] = "builder_stage"
        else:
            result[diff_id] = "base_image"

    return result


def _component_type(pkg_id: str, vuln_type: str) -> str:
    """Map trivy vuln type / pkg identifier to our component taxonomy."""
    if vuln_type in ("alpine", "apk") or "pkg:apk" in pkg_id:
        return "alpine-pkg"
    if vuln_type in ("debian", "dpkg") or "pkg:deb" in pkg_id:
        return "debian-pkg"
    if "pkg:cargo" in pkg_id or vuln_type == "cargo":
        return "rust-crate"
    if "pkg:golang" in pkg_id or vuln_type == "gomod":
        return "go-module"
    if "pkg:pypi" in pkg_id or vuln_type in ("pip", "poetry"):
        return "python-pkg"
    if "pkg:npm" in pkg_id or vuln_type in ("npm", "yarn"):
        return "npm-pkg"
    return "other"


def extract_findings_from_trivy(trivy_json: dict) -> list[dict]:
    """
    Parse a Trivy JSON report and return a list of cve_findings rows ready
    for Supabase insertion.

    Each finding captures:
      - cve_id, severity, package_name, package_version, fixed_version
      - description (Trivy Title field — concise, scanner-provided)
      - mitigation_type: 'pkg_upgrade' if FixedVersion exists, else 'not_applicable'
      - mitigation_detail: null (filled in by pipeline if known)
      - layer: 'base_image' | 'builder_stage'  (derived from DiffID index)
      - component: 'alpine-pkg' | 'rust-crate' | 'go-module' | etc.
    """
    metadata = trivy_json.get("Metadata", {})
    history = metadata.get("ImageConfig", {}).get("history", [])
    diff_ids = metadata.get("DiffIDs", [])
    layer_index = _build_layer_index(diff_ids, history)

    findings = []
    for result in trivy_json.get("Results", []):
        vuln_type = result.get("Type", "")
        for v in result.get("Vulnerabilities") or []:
            layer_info = v.get("Layer", {})
            layer_diff = layer_info.get("DiffID", "")

            layer = layer_index.get(layer_diff, "base_image")

            fixed_ver = v.get("FixedVersion") or None
            mitigation_type = "pkg_upgrade" if fixed_ver else "not_applicable"

            pkg_id = v.get("PkgID", "") or v.get("PkgIdentifier", {}).get("PURL", "")

            findings.append(
                {
                    "cve_id": v["VulnerabilityID"],
                    "severity": v.get("Severity", "UNKNOWN"),
                    "package_name": v.get("PkgName", ""),
                    "package_version": v.get("InstalledVersion", ""),
                    "fixed_version": fixed_ver,
                    "description": (v.get("Title") or v.get("Description", ""))[:500],
                    "mitigation_type": mitigation_type,
                    "mitigation_detail": None,
                    "layer": layer,
                    "component": _component_type(pkg_id, vuln_type),
                }
            )

    return findings


# ---------------------------------------------------------------------------
# Supabase REST API client (no external deps — stdlib only)
# ---------------------------------------------------------------------------


class SupabaseClient:
    def __init__(self, url: str, service_role_key: str):
        self.base = url.rstrip("/") + "/rest/v1"
        self.headers = {
            "apikey": service_role_key,
            "Authorization": f"Bearer {service_role_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }

    def _request(
        self, method: str, path: str, body=None, params: dict = None
    ) -> list | dict | None:
        url = self.base + path
        if params:
            qs = "&".join(f"{k}={v}" for k, v in params.items())
            url = f"{url}?{qs}"

        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(
            url, data=data, headers=self.headers, method=method
        )

        try:
            with urllib.request.urlopen(req) as resp:
                raw = resp.read()
                return json.loads(raw) if raw else None
        except urllib.error.HTTPError as e:
            body_text = e.read().decode()
            print(
                f"[ERROR] {method} {path} → HTTP {e.code}: {body_text}", file=sys.stderr
            )
            raise

    def upsert(self, table: str, row: dict, on_conflict: str) -> dict:
        headers_extra = {"Prefer": "return=representation,resolution=merge-duplicates"}
        url = f"{self.base}/{table}?on_conflict={on_conflict}"
        data = json.dumps([row]).encode()
        req = urllib.request.Request(
            url, data=data, headers={**self.headers, **headers_extra}, method="POST"
        )
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            return result[0] if isinstance(result, list) else result

    def insert(self, table: str, row: dict) -> dict:
        url = f"{self.base}/{table}"
        data = json.dumps([row]).encode()
        req = urllib.request.Request(
            url, data=data, headers=self.headers, method="POST"
        )
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            return result[0] if isinstance(result, list) else result

    def select(self, table: str, filters: dict) -> list:
        params = {k: f"eq.{v}" for k, v in filters.items()}
        url = f"{self.base}/{table}?" + "&".join(f"{k}={v}" for k, v in params.items())
        req = urllib.request.Request(url, headers=self.headers, method="GET")
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())

    def update(self, table: str, filters: dict, row: dict) -> None:
        params = {k: f"eq.{v}" for k, v in filters.items()}
        url = f"{self.base}/{table}?" + "&".join(f"{k}={v}" for k, v in params.items())
        data = json.dumps(row).encode()
        req = urllib.request.Request(
            url,
            data=data,
            headers={**self.headers, "Prefer": "return=minimal"},
            method="PATCH",
        )
        with urllib.request.urlopen(req) as resp:
            resp.read()

    def delete(self, table: str, filters: dict) -> None:
        params = {k: f"eq.{v}" for k, v in filters.items()}
        url = f"{self.base}/{table}?" + "&".join(f"{k}={v}" for k, v in params.items())
        req = urllib.request.Request(
            url, headers={**self.headers, "Prefer": "return=minimal"}, method="DELETE"
        )
        with urllib.request.urlopen(req) as resp:
            resp.read()

    def table_exists(self, table: str) -> bool:
        """Check if a table is accessible (migration applied)."""
        url = f"{self.base}/{table}?limit=0"
        req = urllib.request.Request(url, headers=self.headers, method="GET")
        try:
            with urllib.request.urlopen(req) as resp:
                resp.read()
                return True
        except urllib.error.HTTPError as e:
            if e.code == 404 or b"PGRST205" in e.read():
                return False
            return False
        except Exception:
            return False

    def update_latest_snapshot(self, version_id: str, patch: dict) -> str | None:
        """Update the most recent snapshot row for a given version_id.
        Returns the snapshot id, or None if not found."""
        url = (
            f"{self.base}/image_metadata_snapshots"
            f"?version_id=eq.{version_id}&order=created_at.desc&limit=1"
        )
        req = urllib.request.Request(url, headers=self.headers, method="GET")
        with urllib.request.urlopen(req) as resp:
            rows = json.loads(resp.read())

        if not rows:
            print(
                f"[WARN] No snapshot found for version_id={version_id} — skipping CVE update"
            )
            return None

        snap_id = rows[0]["id"]
        self.update("image_metadata_snapshots", {"id": snap_id}, patch)
        print(f"  snapshot {snap_id[:8]}… updated")
        return snap_id

    def resolve_version_id(self, name: str, version: str) -> str | None:
        """Resolve image_version.id from name + tag. Returns None if not found."""
        version_rows = self.select("image_versions", {"tag": version})
        for vr in version_rows:
            img_rows = self.select("images", {"id": vr["image_id"]})
            if img_rows and name.replace("-", "") in img_rows[0]["slug"].replace(
                "-", ""
            ):
                return vr["id"]
        return None

    def upsert_image(self, slug: str, insert_fields: dict, update_fields: dict) -> dict:
        """
        Insert-or-selective-update for the images table.

        On INSERT (new slug): writes both insert_fields and update_fields.
        On CONFLICT (slug exists): writes only update_fields — insert_fields
        (specifically image_type) are NEVER overwritten so admin overrides survive.

        This implements the requirement from migration 0033:
          image_type is insert-only — the Hub admin owns it after first write.

        Args:
            slug:          unique key for ON CONFLICT detection
            insert_fields: fields written only on first insert (e.g. image_type)
            update_fields: fields always written / updated (e.g. name, summary)
        """
        # Check if the row already exists
        existing = self.select("images", {"slug": slug})

        if existing:
            # Row exists — update only the non-protected fields
            row_id = existing[0]["id"]
            self.update("images", {"id": row_id}, update_fields)
            print(
                f"  image {row_id[:8]}… updated (image_type preserved: "
                f"{existing[0].get('image_type', '?')})"
            )
            return existing[0] | update_fields | {"id": row_id}
        else:
            # New row — write everything including insert_fields
            full_row = {"slug": slug, **insert_fields, **update_fields}
            result = self.insert("images", full_row)
            image_id = result["id"]
            print(
                f"  image {image_id[:8]}… inserted  "
                f"(image_type={insert_fields.get('image_type', '?')})"
            )
            return result


# ---------------------------------------------------------------------------
# CVE findings persistence
# ---------------------------------------------------------------------------

# Suppression columns added by Hub migration 0044.
# We probe for their existence once per process run and cache the result.
_suppression_columns_available: bool | None = None


def _suppression_cols_exist(db: SupabaseClient) -> bool:
    """
    Return True if the cve_findings table has the migration-0044 suppression
    columns (is_suppressed, suppression_reason, …).

    Result is cached for the lifetime of the process — one probe per run.
    Falls back to False on any error so older pipelines stay functional.
    """
    global _suppression_columns_available
    if _suppression_columns_available is not None:
        return _suppression_columns_available

    # Probe by requesting a single row and checking column keys.
    # If the table is empty we can't introspect columns this way, so we fall
    # back to a known-safe approach: attempt a dry PATCH with limit=0.
    try:
        url = db.base + "/cve_findings?select=is_suppressed&limit=1"
        import urllib.request as _ur

        req = _ur.Request(url, headers=db.headers, method="GET")
        with _ur.urlopen(req) as resp:
            resp.read()
        _suppression_columns_available = True
    except Exception:
        _suppression_columns_available = False

    status = (
        "available"
        if _suppression_columns_available
        else "not yet available (migration 0044 pending)"
    )
    print(f"  [suppress-probe] suppression columns: {status}")
    return _suppression_columns_available


def _merge_with_allowlist(
    trivy_findings: list[dict], allowlist_findings: list[dict]
) -> list[dict]:
    """
    Merge real Trivy findings with suppressed allowlist findings.

    Strategy:
    - Build a set of CVE IDs already present in the Trivy findings.
    - For each allowlist entry whose CVE ID is NOT already in the Trivy set,
      append it (it was completely suppressed by .trivyignore — Trivy never
      emitted it). These entries always have is_suppressed=True.
    - For any CVE ID that appears in BOTH lists (should not happen normally —
      would mean Trivy reported it despite being in .trivyignore), the Trivy
      finding takes precedence and the allowlist entry is skipped.

    The merge is intentionally additive-only — it never modifies the real
    Trivy findings, only appends the suppressed ones.
    """
    trivy_cve_ids = {f["cve_id"] for f in trivy_findings}
    merged = list(trivy_findings)

    skipped = 0
    appended = 0
    for entry in allowlist_findings:
        cve_id = entry.get("cve_id", "")
        if not cve_id:
            continue
        if cve_id in trivy_cve_ids:
            # Trivy reported it despite .trivyignore — real finding wins
            skipped += 1
            print(
                f"  [merge] {cve_id} — Trivy finding takes precedence over allowlist entry"
            )
            continue
        merged.append(entry)
        appended += 1

    if allowlist_findings:
        print(
            f"  [merge] +{appended} suppressed / {skipped} skipped (Trivy precedence) "
            f"/ {len(trivy_findings)} real → {len(merged)} total findings"
        )

    return merged


def write_findings(
    db: SupabaseClient, version_id: str, findings: list[dict], replace: bool = True
) -> int:
    """
    Write cve_findings rows for a given image_version_id.

    Handles both real findings (is_suppressed absent or False) and suppressed
    findings (is_suppressed=True, produced by gen-trivyignore.py
    --emit-findings-json + _merge_with_allowlist).

    Suppression columns (is_suppressed, suppression_reason, suppression_detail,
    suppression_evidence, review_date) are written only when migration 0044 is
    applied. If the columns don't exist yet the row is written without them —
    the suppressed entry is still stored, just without the rich metadata until
    the migration runs.

    If replace=True (default), deletes existing findings for this version first
    (idempotent re-runs). If the cve_findings table doesn't exist yet (migration
    pending), logs a warning and returns 0 without error.

    Returns the number of rows written.
    """
    if not findings:
        print(
            "  No CVE findings to write (clean image — no real or suppressed findings)"
        )
        return 0

    if not db.table_exists("cve_findings"):
        print(
            "[WARN] cve_findings table not found — migration pending. "
            "Findings will be written once the schema is applied.",
            file=sys.stderr,
        )
        return 0

    if replace:
        try:
            db.delete("cve_findings", {"image_version_id": version_id})
            print(f"  Cleared existing findings for version {version_id[:8]}…")
        except Exception as e:
            print(f"[WARN] Could not clear findings: {e}", file=sys.stderr)

    suppress_cols = _suppression_cols_exist(db)

    real_count = sum(1 for f in findings if not f.get("is_suppressed", False))
    supp_count = len(findings) - real_count
    print(f"  Writing {real_count} real + {supp_count} suppressed finding(s)…")

    written = 0
    for f in findings:
        # --- core columns (always present in current schema) ---
        row: dict = {
            "image_version_id": version_id,
            "cve_id": f["cve_id"],
            "severity": f["severity"],
            "package_name": f["package_name"],
            "package_version": f.get("package_version", ""),
            "fixed_version": f.get("fixed_version"),
            "description": f.get("description", ""),
            "mitigation_type": f.get("mitigation_type", "not_applicable"),
            "mitigation_detail": f.get("mitigation_detail"),
            "layer": f.get("layer", "base_image"),
            "component": f.get("component", "other"),
        }

        # --- suppression columns (migration 0044 — written only when available) ---
        if suppress_cols:
            row["is_suppressed"] = f.get("is_suppressed", False)
            row["suppression_reason"] = f.get("suppression_reason")
            row["suppression_detail"] = f.get("suppression_detail")
            row["suppression_evidence"] = f.get("suppression_evidence")
            row["review_date"] = f.get("review_date")

        db.upsert("cve_findings", row, on_conflict="image_version_id,cve_id")
        written += 1

    print(
        f"  Wrote {written} CVE finding(s) to cve_findings "
        f"(suppression metadata: {'yes' if suppress_cols else 'no — migration 0044 pending'})"
    )
    return written


# ---------------------------------------------------------------------------
# Snapshot payload builder (shared by single-row + per-platform promote)
# ---------------------------------------------------------------------------


def _build_snapshot_payload(
    image_id: str,
    version_id: str,
    sbom_ref: str | None,
    provenance: str | None,
    promoted_at: str,
    name: str,
    version: str,
    base_version: str,
    profile: str,
    digest: str | None,
    tags: str,
    cosign_id: str | None,
    image_type: str,
    # per-platform fields (migration 0053) — omitted from payload when None
    platform: str | None = None,
    arch: str | None = None,
    image_size_bytes: int | None = None,
    runnable_size_bytes: int | None = None,
) -> dict:
    """
    Build the image_metadata_snapshots insert payload.

    Columns added by migration 0053 (platform, arch, image_size_bytes,
    runnable_size_bytes) are included only when a value is provided, so the
    function is safe to call against databases where migration 0053 is not yet
    applied — the insert simply omits the new columns.
    """
    payload: dict = {
        "image_id": image_id,
        "version_id": version_id,
        "cve_count": None,
        "scan_status": "unknown",
        "scanner": None,
        "sbom_ref": sbom_ref,
        "provenance_ref": provenance,
        "raw_payload": {
            "name": name,
            "version": version,
            "base_version": base_version,
            "profile": profile,
            "digest": digest,
            "tags": tags.split(),
            "cosign_identity": cosign_id,
            "promoted_at": promoted_at,
            "image_type": image_type,
        },
        "snapshotted_at": promoted_at,
    }
    # migration 0053 columns — only written when values are provided
    if platform is not None:
        payload["platform"] = platform
    if arch is not None:
        payload["arch"] = arch
    if image_size_bytes is not None:
        payload["image_size_bytes"] = image_size_bytes
    if runnable_size_bytes is not None:
        payload["runnable_size_bytes"] = runnable_size_bytes
    return payload


# ---------------------------------------------------------------------------
# promote subcommand
# ---------------------------------------------------------------------------


def cmd_promote(args, db: SupabaseClient):
    name = args.name
    version = args.version
    base_version = args.base_version
    profile = args.profile or ""
    digest = args.digest or None
    tags = args.tags or ""
    cosign_id = args.cosign_identity or None
    promoted_at = args.promoted_at or datetime.now(timezone.utc).isoformat()

    # --- migration 0053 fields ---
    platforms = parse_platforms(getattr(args, "platforms", None))
    image_sizes = parse_size_map(getattr(args, "image_size_json", None))
    runnable_sizes = parse_size_map(getattr(args, "runnable_size_json", None))
    sbom_refs = parse_ref_map(getattr(args, "sbom_refs_json", None))
    provenance_refs = parse_ref_map(getattr(args, "provenance_refs_json", None))

    slug = derive_slug(name, profile, base_version)
    image_type = resolve_image_type(getattr(args, "image_type", None), name, profile)
    source_type = derive_source_type(name)
    summary = derive_summary(name, profile, base_version)
    default_sbom_ref = f"ghcr.io/gwshield/{name}:{version}" if version else None
    os_tag = derive_os_tag(name)

    print(
        f"[promote] {name}:{version}  slug={slug}  profile={profile!r}  "
        f"image_type={image_type}  platforms={platforms or '(legacy)'}"
    )

    # 1. Insert-or-selective-update images table
    #
    #    insert_fields  — written ONLY on first insert, never overwritten:
    #      image_type   <- admin override in Hub is authoritative after first write
    #
    #    update_fields  — always written (pipeline is authoritative for these):
    #      name, summary, source_type, visibility, status, featured
    image_row = db.upsert_image(
        slug=slug,
        insert_fields={"image_type": image_type},
        update_fields={
            "name": f"{name.replace('-', ' ').title()} {base_version}"
            if base_version
            else name,
            "summary": summary,
            "source_type": source_type,
            "visibility": "public",
            "status": "active",
            "featured": False,
        },
    )
    image_id = image_row["id"]

    # 2. Set all existing versions for this image to is_latest=false
    for ev in db.select("image_versions", {"image_id": image_id}):
        if ev.get("is_latest"):
            db.update("image_versions", {"id": ev["id"]}, {"is_latest": False})

    # 3. Upsert image_version — include platforms list (migration 0053)
    version_payload: dict = {
        "image_id": image_id,
        "tag": version,
        "digest": digest,
        "promoted_at": promoted_at,
        "is_latest": True,
        "cosign_identity": cosign_id,
        "base_version": base_version,
        "profile": profile,
    }
    if platforms:
        version_payload["platforms"] = platforms

    version_row = db.upsert(
        "image_versions", version_payload, on_conflict="image_id,tag"
    )
    version_id = version_row["id"]
    print(
        f"  version {version_id[:8]}… upserted (is_latest=True"
        + (f", platforms={platforms}" if platforms else "")
        + ")"
    )

    # 4. Insert metadata snapshot(s)
    #
    #    Migration 0053: one row per platform when --platforms is supplied.
    #    The per-platform row carries platform, arch, image_size_bytes,
    #    runnable_size_bytes, and the platform-specific sbom_ref.
    #
    #    Legacy fallback (no --platforms): single row without platform fields —
    #    identical to the pre-0053 behaviour, safe against older DB schemas.
    snapshot_ids: list[str] = []

    if platforms:
        for plat in platforms:
            arch = plat.split("/")[1] if "/" in plat else plat
            snap_payload = _build_snapshot_payload(
                image_id=image_id,
                version_id=version_id,
                sbom_ref=sbom_refs.get(plat, default_sbom_ref),
                provenance=provenance_refs.get(plat, cosign_id),
                promoted_at=promoted_at,
                name=name,
                version=version,
                base_version=base_version,
                profile=profile,
                digest=digest,
                tags=tags,
                cosign_id=cosign_id,
                image_type=image_type,
                platform=plat,
                arch=arch,
                image_size_bytes=image_sizes.get(plat) or None,
                runnable_size_bytes=runnable_sizes.get(plat) or None,
            )
            snap_row = db.insert("image_metadata_snapshots", snap_payload)
            snap_id = snap_row["id"]
            snapshot_ids.append(snap_id)
            size_info = ""
            if image_sizes.get(plat):
                size_info += f"  image_size={image_sizes[plat]}"
            if runnable_sizes.get(plat):
                size_info += f"  runnable_size={runnable_sizes[plat]}"
            print(f"  snapshot {snap_id[:8]}… created  platform={plat}{size_info}")
    else:
        snap_payload = _build_snapshot_payload(
            image_id=image_id,
            version_id=version_id,
            sbom_ref=default_sbom_ref,
            provenance=cosign_id,
            promoted_at=promoted_at,
            name=name,
            version=version,
            base_version=base_version,
            profile=profile,
            digest=digest,
            tags=tags,
            cosign_id=cosign_id,
            image_type=image_type,
        )
        snap_row = db.insert("image_metadata_snapshots", snap_payload)
        snap_id = snap_row["id"]
        snapshot_ids.append(snap_id)
        print(f"  snapshot {snap_id[:8]}… created (legacy single-row)")

    # 5. Link most-recent snapshot back to version
    db.update(
        "image_versions", {"id": version_id}, {"metadata_snapshot_id": snapshot_ids[-1]}
    )

    # 6. Upsert image_tags
    #    arch tag: reflects actual platforms when available, else legacy string
    arch_tag = ",".join(platforms) if platforms else "linux/amd64,linux/arm64"
    tags_to_write: list[dict] = [
        {"image_id": image_id, "tag_key": "family", "tag_value": name},
        {"image_id": image_id, "tag_key": "image_type", "tag_value": image_type},
        {"image_id": image_id, "tag_key": "os", "tag_value": os_tag},
        {"image_id": image_id, "tag_key": "arch", "tag_value": arch_tag},
    ]
    profile_tag = derive_profile_tag(name, profile)
    if profile_tag:
        tags_to_write.append(
            {"image_id": image_id, "tag_key": "profile", "tag_value": profile_tag}
        )
    if image_type == "tooling":
        tags_to_write.append(
            {"image_id": image_id, "tag_key": "category", "tag_value": "tooling"}
        )
    for t in tags_to_write:
        db.upsert("image_tags", t, on_conflict="image_id,tag_key,tag_value")
    print(
        f"  wrote {len(tags_to_write)} tag(s): "
        f"{', '.join(t['tag_key'] + '=' + t['tag_value'] for t in tags_to_write)}"
    )

    # 7. Write version group tag
    version_group = derive_version_group(base_version)
    try:
        db.delete("image_tags", {"image_id": image_id, "tag_key": "version"})
        db.insert(
            "image_tags",
            {"image_id": image_id, "tag_key": "version", "tag_value": version_group},
        )
        print(f"  version tag set: version={version_group}")
    except Exception as e:
        print(f"[WARN] Could not write version tag: {e}", file=sys.stderr)

    print(
        f"[promote] done — slug={slug}  image_type={image_type}  version={version_group}"
        + (f"  snapshots={len(snapshot_ids)}" if len(snapshot_ids) > 1 else "")
    )


# ---------------------------------------------------------------------------
# scan subcommand
# ---------------------------------------------------------------------------


def cmd_scan(args, db: SupabaseClient):
    name = args.name
    version = args.version
    cve_total = int(args.cve_total)
    cve_crit = int(args.cve_critical)
    cve_high = int(args.cve_high)
    scanner = args.scanner or "trivy"
    scanned_at = args.scanned_at or datetime.now(timezone.utc).isoformat()
    findings_arg = getattr(args, "findings_json", None)
    allowlist_arg = getattr(args, "allowlist_json", None)

    scan_status = "clean" if (cve_crit == 0 and cve_high == 0) else "findings"

    print(
        f"[scan] {name}:{version}  total={cve_total} crit={cve_crit} high={cve_high}  status={scan_status}"
    )

    version_id = db.resolve_version_id(name, version)
    if not version_id:
        print(
            f"[ERROR] Could not resolve version_id for {name}:{version}",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"  resolved version_id={version_id[:8]}…")

    db.update_latest_snapshot(
        version_id,
        {
            "cve_count": cve_total,
            "cve_critical": cve_crit,
            "cve_high": cve_high,
            "scan_status": scan_status,
            "scanner": scanner,
            "snapshotted_at": scanned_at,
        },
    )

    if findings_arg or allowlist_arg:
        trivy_findings = _parse_findings_arg(findings_arg) if findings_arg else []
        allowlist_entries = (
            _parse_findings_arg(allowlist_arg, fmt="findings") if allowlist_arg else []
        )
        findings = _merge_with_allowlist(trivy_findings, allowlist_entries)
        write_findings(db, version_id, findings, replace=True)

    print(f"[scan] done — {name}:{version} → {scan_status}")


# ---------------------------------------------------------------------------
# findings subcommand  (standalone — used by rescan-origin pipeline)
# ---------------------------------------------------------------------------


def cmd_findings(args, db: SupabaseClient):
    """
    Write structured CVE findings for a specific image version.

    Accepts either:
      --findings-json <inline-json-string>   — pre-parsed findings array
      --findings-json @/path/to/file.json    — path to trivy JSON report
      --findings-format trivy                — parse as raw trivy output (default)
      --findings-format findings             — parse as pre-formatted findings array

    Optionally merge with suppressed entries from allowlist.yaml:
      --allowlist-json @/path/to/allowlist-findings.json
    """
    name = args.name
    version = args.version
    fmt = getattr(args, "findings_format", "trivy")
    raw_arg = args.findings_json
    allowlist_arg = getattr(args, "allowlist_json", None)

    print(f"[findings] {name}:{version}  format={fmt}")

    version_id = db.resolve_version_id(name, version)
    if not version_id:
        print(
            f"[ERROR] Could not resolve version_id for {name}:{version}",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"  resolved version_id={version_id[:8]}…")

    trivy_findings = _parse_findings_arg(raw_arg, fmt)
    allowlist_entries = (
        _parse_findings_arg(allowlist_arg, fmt="findings") if allowlist_arg else []
    )
    findings = _merge_with_allowlist(trivy_findings, allowlist_entries)

    count = write_findings(db, version_id, findings, replace=True)
    print(f"[findings] done — {count} finding(s) written for {name}:{version}")


def _parse_findings_arg(raw_arg: str, fmt: str = "trivy") -> list[dict]:
    """
    Parse the --findings-json argument.
    Supports:
      - inline JSON string (starts with '[' or '{')
      - @/path/to/file  — load from file path
      - fmt="trivy"     — parse as raw Trivy JSON output (extract + normalise)
      - fmt="findings"  — parse as pre-formatted findings array
    """
    if not raw_arg:
        return []

    if raw_arg.startswith("@"):
        path = raw_arg[1:]
        with open(path) as f:
            content = f.read()
    else:
        content = raw_arg

    data = json.loads(content)

    if fmt == "trivy":
        if isinstance(data, dict) and "Results" in data:
            return extract_findings_from_trivy(data)
        if isinstance(data, list):
            return data
        raise ValueError(f"Unexpected trivy format: {type(data)}")

    if fmt == "findings":
        if isinstance(data, list):
            return data
        raise ValueError(f"findings format expects a JSON array, got {type(data)}")

    raise ValueError(f"Unknown findings format: {fmt}")


# ---------------------------------------------------------------------------
# smoke subcommand — writes smoke_result.json content to smoke_results table
# ---------------------------------------------------------------------------


def cmd_smoke(args, db: SupabaseClient):
    """
    Write a smoke test result for a runtime image version to smoke_results.

    Reads smoke-result.json (produced by shared/smoke-lib.sh smoke_end()) and
    inserts one row into public.smoke_results for the resolved image_version_id.

    Required: --name, --version, --base-version
    Optional: --profile, --result-file, --run-url, --runner, --trigger
    """
    name = args.name
    version = args.version
    base_version = args.base_version
    profile = args.profile or ""
    result_file = args.result_file
    run_url = getattr(args, "run_url", "") or ""
    runner = getattr(args, "runner", "") or ""
    trigger = getattr(args, "trigger", "post-build") or "post-build"

    slug = derive_slug(name, profile, base_version)
    print(
        f"[smoke] {name}:{version}  slug={slug}  profile={profile!r}  result_file={result_file}"
    )

    # Resolve image_version_id via slug → image → image_versions
    image_row = db.select("images", {"slug": slug})
    if not image_row:
        print(
            f"[smoke] WARNING: no image found for slug={slug!r} — skipping Supabase write",
            file=sys.stderr,
        )
        return
    image_id = image_row[0]["id"]

    version_rows = db.select("image_versions", {"image_id": image_id, "tag": version})
    if not version_rows:
        print(
            f"[smoke] WARNING: no image_version found for {slug}:{version} — skipping Supabase write",
            file=sys.stderr,
        )
        return
    version_id = version_rows[0]["id"]

    # Parse smoke-result.json
    if not result_file or not pathlib.Path(result_file).exists():
        print(
            f"[smoke] WARNING: result file not found: {result_file!r} — skipping Supabase write",
            file=sys.stderr,
        )
        return

    try:
        result = json.loads(pathlib.Path(result_file).read_text())
    except Exception as e:
        print(f"[smoke] ERROR reading {result_file}: {e}", file=sys.stderr)
        return

    overall_status = result.get("overall_status", "skipped")
    pass_count = int(result.get("pass_count", 0))
    fail_count = int(result.get("fail_count", 0))
    duration_ms = result.get("duration_ms")
    image_ref = result.get("image_ref", "")
    ran_at = result.get("ran_at") or datetime.now(timezone.utc).isoformat()
    checks = result.get("checks", [])

    payload = {
        "image_version_id": version_id,
        "ran_at": ran_at,
        "trigger": trigger,
        "overall_status": overall_status,
        "pass_count": pass_count,
        "fail_count": fail_count,
        "checks": checks,
    }
    if duration_ms is not None:
        payload["duration_ms"] = int(duration_ms)
    if image_ref:
        payload["image_ref"] = image_ref
    if run_url:
        payload["run_url"] = run_url
    if runner:
        payload["runner"] = runner

    db.insert("smoke_results", payload)
    print(
        f"[smoke] result written — {slug}:{version}  status={overall_status}  "
        f"pass={pass_count}  fail={fail_count}"
    )


# ---------------------------------------------------------------------------
# baseline subcommand — writes mirror sync + smoke results to Supabase
# ---------------------------------------------------------------------------


def cmd_baseline(args, db: SupabaseClient):
    """
    Write baseline image sync result (mirror + Trivy CVE + smoke test) to Supabase.

    Creates or updates:
      images                   row  (image_type='baseline')
      image_versions           row  (base_version=tag, profile='')
      baseline_sync_results    row  (sync outcome, CVE counts, smoke checks)

    Idempotent: re-syncing the same slug+digest upserts the sync result row.
    """
    slug = args.slug
    upstream_image = args.upstream_image
    upstream_tag = args.upstream_tag
    upstream_digest = args.upstream_digest
    mirror_image = args.mirror_image  # full ref incl. tag
    mirror_digest = args.mirror_digest or ""
    status = args.status  # synced | blocked_cve | skipped
    critical = int(args.critical or 0)
    high = int(args.high or 0)
    smoke_status = getattr(args, "smoke_status", "skipped") or "skipped"
    smoke_pass = int(getattr(args, "smoke_pass", 0) or 0)
    smoke_fail = int(getattr(args, "smoke_fail", 0) or 0)
    run_url = getattr(args, "run_url", "") or ""

    print(
        f"[baseline] {slug}  status={status}  crit={critical}  high={high}  smoke={smoke_status}"
    )

    # Parse smoke checks JSON — prefer --smoke-checks-file (avoids shell quoting
    # issues with { } ( ) characters in inline JSON from GITHUB_OUTPUT).
    smoke_checks_file = getattr(args, "smoke_checks_file", None)
    if smoke_checks_file:
        try:
            import pathlib

            smoke_checks = json.loads(pathlib.Path(smoke_checks_file).read_text())
        except Exception:
            smoke_checks = []
    else:
        smoke_checks_raw = getattr(args, "smoke_checks", "[]") or "[]"
        try:
            smoke_checks = (
                json.loads(smoke_checks_raw) if smoke_checks_raw.strip() else []
            )
        except Exception:
            smoke_checks = []

    # ── Upsert image (image_type='baseline') ─────────────────────────────
    # slug is the unique key (not name). Use upsert_image() which does
    # select + insert/update to preserve admin-set image_type overrides.
    display_name = f"{upstream_image.capitalize()} {upstream_tag}"  # e.g. "Alpine 3.22"
    image_row = db.upsert_image(
        slug=slug,
        insert_fields={"image_type": "baseline", "visibility": "public"},
        update_fields={"name": display_name},
    )
    image_id = image_row.get("id") if image_row else None
    if not image_id:
        raise RuntimeError(f"[baseline] could not resolve image_id for slug={slug}")

    print(f"  image_id={image_id[:8]}…")

    # ── Upsert image_version ──────────────────────────────────────────────
    # Use select+insert/update pattern (same as upsert_image) — no image_type
    # column exists on image_versions, and on_conflict multi-column upsert
    # requires an explicit DB constraint which may not exist.
    version_tag = upstream_tag  # e.g. "3.22" or "12-slim"
    version_payload = {
        "image_id": image_id,
        "tag": version_tag,
        "base_version": version_tag,
        "profile": "",
        "digest": mirror_digest or upstream_digest,
    }
    existing_versions = db.select(
        "image_versions", {"image_id": image_id, "tag": version_tag}
    )
    if existing_versions:
        version_id = existing_versions[0]["id"]
        db.update(
            "image_versions",
            {"id": version_id},
            {
                "digest": mirror_digest or upstream_digest,
            },
        )
        print(f"  version {version_id[:8]}… updated")
    else:
        version_row = db.insert("image_versions", version_payload)
        version_id = version_row.get("id") if version_row else None
        if not version_id:
            raise RuntimeError(
                f"[baseline] could not insert version for {slug}:{version_tag}"
            )
        print(f"  version {version_id[:8]}… inserted")

    print(f"  version_id={version_id[:8]}…")

    # ── Insert baseline_sync_results row ──────────────────────────────────
    # Table created by Hub migration 0055_baseline_sync_results.sql
    # If table doesn't exist yet, skip gracefully (continue-on-error in workflow)
    if not db.table_exists("baseline_sync_results"):
        print(
            f"[baseline] WARNING: baseline_sync_results table not yet created — skipping writeback"
        )
        print(f"           Apply Hub migration 0055 to enable baseline sync tracking.")
        return

    db.insert(
        "baseline_sync_results",
        {
            "image_version_id": version_id,
            "synced_at": _utcnow(),
            "trigger": "manual" if run_url else "scheduled",
            "status": status,
            "upstream_image": upstream_image,
            "upstream_tag": upstream_tag,
            "upstream_digest": upstream_digest,
            "mirror_image": mirror_image,
            "mirror_digest": mirror_digest,
            "critical_count": critical,
            "high_count": high,
            "smoke_status": smoke_status,
            "smoke_pass": smoke_pass,
            "smoke_fail": smoke_fail,
            "smoke_checks": smoke_checks,
            "run_url": run_url,
        },
    )
    print(
        f"[baseline] sync result written — {slug} {status} smoke={smoke_status} ({smoke_pass}/{smoke_pass + smoke_fail})"
    )


def _utcnow() -> str:
    """Return current UTC timestamp as ISO 8601 string."""
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _validate_image_type(value: str) -> str:
    """argparse type validator for --image-type."""
    if value not in _VALID_IMAGE_TYPES:
        raise argparse.ArgumentTypeError(
            f"invalid image_type {value!r} — must be one of: "
            + ", ".join(sorted(_VALID_IMAGE_TYPES))
        )
    return value


def main():
    supabase_url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

    if not supabase_url or not service_key:
        print(
            "[ERROR] SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set",
            file=sys.stderr,
        )
        sys.exit(1)

    db = SupabaseClient(supabase_url, service_key)

    parser = argparse.ArgumentParser(
        description="gwshield pipeline → Supabase writeback"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # --- promote ---
    p_promote = sub.add_parser("promote")
    p_promote.add_argument("--name", required=True)
    p_promote.add_argument("--version", required=True)
    p_promote.add_argument("--base-version", required=True, dest="base_version")
    p_promote.add_argument("--profile", default="")
    p_promote.add_argument(
        "--image-type",
        default=None,
        dest="image_type",
        type=_validate_image_type,
        help=(
            "Structural image classification written on first insert only. "
            "Admin overrides in the Hub are preserved on subsequent promotes. "
            f"Allowed: {', '.join(sorted(_VALID_IMAGE_TYPES))}. "
            "Default: auto-detected from --name/--profile."
        ),
    )
    p_promote.add_argument("--digest", default=None)
    p_promote.add_argument("--tags", default="")
    p_promote.add_argument("--cosign-identity", default=None, dest="cosign_identity")
    p_promote.add_argument("--promoted-at", default=None, dest="promoted_at")
    # migration 0053 — multi-platform fields
    p_promote.add_argument(
        "--platforms",
        default=None,
        help=(
            "JSON array of OCI platform strings, e.g. "
            '["linux/amd64","linux/arm64"]. '
            "When supplied, one snapshot row per platform is written "
            "and image_versions.platforms is populated. "
            "Omit for legacy single-arch images."
        ),
    )
    p_promote.add_argument(
        "--image-size-json",
        default=None,
        dest="image_size_json",
        help=(
            "JSON object platform -> compressed size bytes "
            "(skopeo inspect --raw, sum of layer sizes)."
        ),
    )
    p_promote.add_argument(
        "--runnable-size-json",
        default=None,
        dest="runnable_size_json",
        help=(
            "JSON object platform -> uncompressed on-disk size bytes "
            "(skopeo inspect without --raw, LayersData[].Size sum)."
        ),
    )
    p_promote.add_argument(
        "--sbom-refs-json",
        default=None,
        dest="sbom_refs_json",
        help=(
            "JSON object platform -> per-platform OCI SBOM ref "
            "(ghcr.io/gwshield/<name>:<tag>@sha256:<platform-digest>)."
        ),
    )
    p_promote.add_argument(
        "--provenance-refs-json",
        default=None,
        dest="provenance_refs_json",
        help=(
            "JSON object platform -> per-platform provenance ref. "
            "Defaults to cosign identity when not supplied."
        ),
    )

    # --- scan ---
    p_scan = sub.add_parser("scan")
    p_scan.add_argument("--name", required=True)
    p_scan.add_argument("--version", required=True)
    p_scan.add_argument("--cve-total", default="0", dest="cve_total")
    p_scan.add_argument("--cve-critical", default="0", dest="cve_critical")
    p_scan.add_argument("--cve-high", default="0", dest="cve_high")
    p_scan.add_argument("--scanner", default="trivy")
    p_scan.add_argument("--scanned-at", default=None, dest="scanned_at")
    p_scan.add_argument(
        "--findings-json",
        default=None,
        dest="findings_json",
        help="Inline JSON array of findings, or @/path/to/trivy.json",
    )
    p_scan.add_argument(
        "--allowlist-json",
        default=None,
        dest="allowlist_json",
        help=(
            "Pre-formatted suppressed findings from gen-trivyignore.py "
            "--emit-findings-json, or @/path/to/allowlist-findings.json. "
            "Merged with --findings-json before the Supabase write so "
            "suppressed CVEs are stored transparently with is_suppressed=true."
        ),
    )

    # --- findings ---
    p_findings = sub.add_parser("findings")
    p_findings.add_argument("--name", required=True)
    p_findings.add_argument("--version", required=True)
    p_findings.add_argument(
        "--findings-json",
        required=True,
        dest="findings_json",
        help="Inline JSON array, or @/path/to/trivy.json",
    )
    p_findings.add_argument(
        "--findings-format",
        default="trivy",
        dest="findings_format",
        choices=["trivy", "findings"],
        help="trivy = raw Trivy JSON output; findings = pre-formatted array",
    )
    p_findings.add_argument(
        "--allowlist-json",
        default=None,
        dest="allowlist_json",
        help=(
            "Pre-formatted suppressed findings from gen-trivyignore.py "
            "--emit-findings-json, or @/path/to/allowlist-findings.json. "
            "Merged with --findings-json before the Supabase write."
        ),
    )

    # smoke subcommand
    p_smoke = sub.add_parser(
        "smoke", help="Write smoke-result.json to smoke_results table in Supabase"
    )
    p_smoke.add_argument("--name", required=True)
    p_smoke.add_argument("--version", required=True)
    p_smoke.add_argument("--base-version", required=True, dest="base_version")
    p_smoke.add_argument("--profile", default="")
    p_smoke.add_argument(
        "--result-file",
        required=True,
        dest="result_file",
        help="Path to smoke-result.json produced by smoke_end()",
    )
    p_smoke.add_argument(
        "--run-url",
        default="",
        dest="run_url",
        help="Public GitHub Actions run URL (gwshield/images)",
    )
    p_smoke.add_argument(
        "--runner", default="", help="Runner label, e.g. blacksmith-2vcpu-ubuntu-2404"
    )
    p_smoke.add_argument(
        "--trigger",
        default="post-build",
        help="Trigger type: post-build | post-promote | scheduled | manual",
    )

    # baseline subcommand
    p_baseline = sub.add_parser(
        "baseline", help="Write baseline image mirror sync result to Supabase"
    )
    p_baseline.add_argument("--slug", required=True)
    p_baseline.add_argument("--upstream-image", required=True, dest="upstream_image")
    p_baseline.add_argument("--upstream-tag", required=True, dest="upstream_tag")
    p_baseline.add_argument("--upstream-digest", required=True, dest="upstream_digest")
    p_baseline.add_argument("--mirror-image", required=True, dest="mirror_image")
    p_baseline.add_argument("--mirror-digest", default="", dest="mirror_digest")
    p_baseline.add_argument("--status", default="synced")
    p_baseline.add_argument("--critical", default="0")
    p_baseline.add_argument("--high", default="0")
    p_baseline.add_argument("--smoke-status", default="skipped", dest="smoke_status")
    p_baseline.add_argument("--smoke-pass", default="0", dest="smoke_pass")
    p_baseline.add_argument("--smoke-fail", default="0", dest="smoke_fail")
    p_baseline.add_argument(
        "--smoke-checks",
        default="[]",
        dest="smoke_checks",
        help="Smoke checks JSON inline string (use --smoke-checks-file to avoid shell quoting issues)",
    )
    p_baseline.add_argument(
        "--smoke-checks-file",
        default=None,
        dest="smoke_checks_file",
        help="Path to a file containing smoke checks JSON (preferred over --smoke-checks)",
    )
    p_baseline.add_argument("--run-url", default="", dest="run_url")

    args = parser.parse_args()

    if args.cmd == "promote":
        cmd_promote(args, db)
    elif args.cmd == "scan":
        cmd_scan(args, db)
    elif args.cmd == "findings":
        cmd_findings(args, db)
    elif args.cmd == "smoke":
        cmd_smoke(args, db)
    elif args.cmd == "baseline":
        cmd_baseline(args, db)


if __name__ == "__main__":
    main()
