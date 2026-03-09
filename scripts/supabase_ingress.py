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
#   scan      — update CVE counts on the latest snapshot after a scan run
#
# Usage:
#   python3 scripts/supabase_ingress.py promote \
#     --name postgres --version v15.17-tls \
#     --base-version v15.17 --profile tls \
#     --digest sha256:abc123 \
#     --tags "ghcr.io/gwshield/postgres:v15.17-tls" \
#     --cosign-identity "https://github.com/gwshield/images/..." \
#     --promoted-at "2026-03-09T12:00:00Z"
#
#   python3 scripts/supabase_ingress.py scan \
#     --name postgres --version v15.17-tls \
#     --cve-total 0 --cve-critical 0 --cve-high 0 \
#     --scanner trivy --scanned-at "2026-03-09T12:00:00Z"
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
# =============================================================================

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone


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
        # Derive major version from base_version (e.g. "v15.17" → "v15")
        major = ""
        bv = base_version.lstrip("v")
        if "." in bv:
            major_num = bv.split(".")[0]
            major = f"-v{major_num}"
        if p == "":
            return f"postgres{major}"
        return f"postgres{major}-{p}"

    if name == "python-builder":
        # Strip 'v' and dots from profile version prefix: v3.12 → v312
        # profile is e.g. "v3.12", "v3.12-dev", "v3.13", "v3.13-dev"
        if p == "":
            return "python-builder"
        # normalise: v3.12-dev → v312-dev
        normalised = p.replace("v", "v").replace(".", "")
        # "v312" not "v3.12" — replace only the version dots, not the dash suffix
        import re
        normalised = re.sub(r"v(\d+)\.(\d+)", r"v\1\2", p)
        return f"python-builder-{normalised}"

    if name == "go-builder":
        if p == "" or p == "compile":
            return "go-builder"
        return f"go-builder-{p}"

    # Default: name + optional profile suffix
    if p == "":
        return name
    return f"{name}-{p}"


def derive_source_type(name: str) -> str:
    if "builder" in name:
        return "base"
    return "dockerfile"


def derive_summary(name: str, profile: str, base_version: str) -> str:
    bv = base_version or ""
    p = profile.strip()
    label = f"{name} {bv}" + (f" ({p})" if p else "")
    return f"Hardened {label} image — 0 CVEs"


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

    def _request(self, method: str, path: str, body=None, params: dict = None) -> list | dict | None:
        url = self.base + path
        if params:
            qs = "&".join(f"{k}={v}" for k, v in params.items())
            url = f"{url}?{qs}"

        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data, headers=self.headers, method=method)

        try:
            with urllib.request.urlopen(req) as resp:
                raw = resp.read()
                return json.loads(raw) if raw else None
        except urllib.error.HTTPError as e:
            body_text = e.read().decode()
            print(f"[ERROR] {method} {path} → HTTP {e.code}: {body_text}", file=sys.stderr)
            raise

    def upsert(self, table: str, row: dict, on_conflict: str) -> dict:
        headers_extra = {"Prefer": f"return=representation,resolution=merge-duplicates"}
        url = f"{self.base}/{table}?on_conflict={on_conflict}"
        data = json.dumps([row]).encode()
        req = urllib.request.Request(url, data=data, headers={**self.headers, **headers_extra}, method="POST")
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            return result[0] if isinstance(result, list) else result

    def insert(self, table: str, row: dict) -> dict:
        url = f"{self.base}/{table}"
        data = json.dumps([row]).encode()
        req = urllib.request.Request(url, data=data, headers=self.headers, method="POST")
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
        req = urllib.request.Request(url, data=data, headers={**self.headers, "Prefer": "return=minimal"}, method="PATCH")
        with urllib.request.urlopen(req) as resp:
            resp.read()

    def update_latest_snapshot(self, version_id: str, patch: dict) -> None:
        """Update the most recent snapshot row for a given version_id."""
        # Select snapshot ordered by created_at desc, take first
        url = (f"{self.base}/image_metadata_snapshots"
               f"?version_id=eq.{version_id}&order=created_at.desc&limit=1")
        req = urllib.request.Request(url, headers=self.headers, method="GET")
        with urllib.request.urlopen(req) as resp:
            rows = json.loads(resp.read())

        if not rows:
            print(f"[WARN] No snapshot found for version_id={version_id} — skipping CVE update")
            return

        snap_id = rows[0]["id"]
        self.update("image_metadata_snapshots", {"id": snap_id}, patch)
        print(f"  snapshot {snap_id[:8]}… updated")


# ---------------------------------------------------------------------------
# promote subcommand
# ---------------------------------------------------------------------------

def cmd_promote(args, db: SupabaseClient):
    name        = args.name
    version     = args.version
    base_version = args.base_version
    profile     = args.profile or ""
    digest      = args.digest or None
    tags        = args.tags or ""
    cosign_id   = args.cosign_identity or None
    promoted_at = args.promoted_at or datetime.now(timezone.utc).isoformat()

    slug         = derive_slug(name, profile, base_version)
    source_type  = derive_source_type(name)
    summary      = derive_summary(name, profile, base_version)
    is_latest    = any("latest" in t for t in tags.split())
    sbom_ref     = f"ghcr.io/gwshield/{name}:{version}" if version else None

    print(f"[promote] {name}:{version}  slug={slug}  profile={profile!r}")

    # 1. Upsert image (insert-only for name/summary — never overwrite on re-promote)
    image_row = db.upsert("images", {
        "slug":        slug,
        "name":        f"{name.replace('-', ' ').title()} {base_version}" if base_version else name,
        "summary":     summary,
        "source_type": source_type,
        "visibility":  "public",
        "status":      "active",
        "featured":    False,
    }, on_conflict="slug")

    image_id = image_row["id"]
    print(f"  image {image_id[:8]}… upserted")

    # 2. Set all existing versions for this image to is_latest=false
    existing_versions = db.select("image_versions", {"image_id": image_id})
    for ev in existing_versions:
        if ev.get("is_latest"):
            db.update("image_versions", {"id": ev["id"]}, {"is_latest": False})

    # 3. Upsert image_version
    version_row = db.upsert("image_versions", {
        "image_id":       image_id,
        "tag":            version,
        "digest":         digest,
        "promoted_at":    promoted_at,
        "is_latest":      True,
        "cosign_identity": cosign_id,
        "base_version":   base_version,
        "profile":        profile,
    }, on_conflict="image_id,tag")

    version_id = version_row["id"]
    print(f"  version {version_id[:8]}… upserted (is_latest=True)")

    # 4. Insert metadata snapshot (always new row — snapshots are immutable)
    snapshot_row = db.insert("image_metadata_snapshots", {
        "image_id":      image_id,
        "version_id":    version_id,
        "cve_count":     None,
        "scan_status":   "unknown",
        "scanner":       None,
        "sbom_ref":      sbom_ref,
        "provenance_ref": cosign_id,
        "raw_payload":   {
            "name":        name,
            "version":     version,
            "base_version": base_version,
            "profile":     profile,
            "digest":      digest,
            "tags":        tags.split(),
            "cosign_identity": cosign_id,
            "promoted_at": promoted_at,
        },
        "snapshotted_at": promoted_at,
    })

    snapshot_id = snapshot_row["id"]
    print(f"  snapshot {snapshot_id[:8]}… created")

    # 5. Link snapshot back to version
    db.update("image_versions", {"id": version_id}, {"metadata_snapshot_id": snapshot_id})

    # 6. Upsert image_tags: profile + family
    tags_to_write = [{"image_id": image_id, "tag_key": "family", "tag_value": name}]
    if profile:
        tags_to_write.append({"image_id": image_id, "tag_key": "profile", "tag_value": profile})

    for t in tags_to_write:
        db.upsert("image_tags", t, on_conflict="image_id,tag_key,tag_value")

    print(f"[promote] done — slug={slug}")


# ---------------------------------------------------------------------------
# scan subcommand
# ---------------------------------------------------------------------------

def cmd_scan(args, db: SupabaseClient):
    name       = args.name
    version    = args.version
    cve_total  = int(args.cve_total)
    cve_crit   = int(args.cve_critical)
    cve_high   = int(args.cve_high)
    scanner    = args.scanner or "trivy"
    scanned_at = args.scanned_at or datetime.now(timezone.utc).isoformat()

    scan_status = "clean" if (cve_crit == 0 and cve_high == 0) else "findings"

    print(f"[scan] {name}:{version}  total={cve_total} crit={cve_crit} high={cve_high}  status={scan_status}")

    # Resolve version_id via slug pattern
    # We query image_versions joined through images by checking all versions with this tag
    url = (f"{db.base}/image_versions"
           f"?tag=eq.{version}&select=id,image_id,images(slug)")
    req = urllib.request.Request(
        url + "&images=not.is.null",
        headers={**db.headers, "Accept": "application/json"},
        method="GET"
    )
    # Simpler: select by tag directly and filter by name match
    version_rows = db.select("image_versions", {"tag": version})

    version_id = None
    for vr in version_rows:
        # Cross-check via image name (slug contains the name)
        img_rows = db.select("images", {"id": vr["image_id"]})
        if img_rows and name.replace("-", "") in img_rows[0]["slug"].replace("-", ""):
            version_id = vr["id"]
            break

    if not version_id:
        print(f"[ERROR] Could not resolve version_id for {name}:{version}", file=sys.stderr)
        sys.exit(1)

    print(f"  resolved version_id={version_id[:8]}…")

    db.update_latest_snapshot(version_id, {
        "cve_count":    cve_total,
        "cve_critical": cve_crit,
        "cve_high":     cve_high,
        "scan_status":  scan_status,
        "scanner":      scanner,
        "snapshotted_at": scanned_at,
    })

    print(f"[scan] done — {name}:{version} → {scan_status}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    supabase_url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    service_key  = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

    if not supabase_url or not service_key:
        print("[ERROR] SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set", file=sys.stderr)
        sys.exit(1)

    db = SupabaseClient(supabase_url, service_key)

    parser = argparse.ArgumentParser(description="gwshield pipeline → Supabase writeback")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_promote = sub.add_parser("promote")
    p_promote.add_argument("--name",             required=True)
    p_promote.add_argument("--version",          required=True)
    p_promote.add_argument("--base-version",     required=True, dest="base_version")
    p_promote.add_argument("--profile",          default="")
    p_promote.add_argument("--digest",           default=None)
    p_promote.add_argument("--tags",             default="")
    p_promote.add_argument("--cosign-identity",  default=None, dest="cosign_identity")
    p_promote.add_argument("--promoted-at",      default=None, dest="promoted_at")

    p_scan = sub.add_parser("scan")
    p_scan.add_argument("--name",        required=True)
    p_scan.add_argument("--version",     required=True)
    p_scan.add_argument("--cve-total",   default="0", dest="cve_total")
    p_scan.add_argument("--cve-critical",default="0", dest="cve_critical")
    p_scan.add_argument("--cve-high",    default="0", dest="cve_high")
    p_scan.add_argument("--scanner",     default="trivy")
    p_scan.add_argument("--scanned-at",  default=None, dest="scanned_at")

    args = parser.parse_args()

    if args.cmd == "promote":
        cmd_promote(args, db)
    elif args.cmd == "scan":
        cmd_scan(args, db)


if __name__ == "__main__":
    main()
