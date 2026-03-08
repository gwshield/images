#!/usr/bin/env python3
# =============================================================================
# update-registry.py — registry.json processing engine
# =============================================================================
# Single source of truth for all public image metadata.
# Called by promote.yml (upsert image entry) and scan.yml (update CVE status).
#
# Usage:
#   # After a promote:
#   python3 scripts/update-registry.py promote \
#     --name postgres \
#     --version v15.17 \
#     --base-version v15.17 \
#     --profile "" \
#     --digest sha256:abc123 \
#     --tags "ghcr.io/gwshield/postgres:v15.17 ghcr.io/gwshield/postgres:latest" \
#     --cosign-identity "https://github.com/gwshield/images/.github/workflows/promote.yml@refs/heads/main" \
#     --promoted-at "2026-03-08T12:00:00Z"
#
#   # After a scan:
#   python3 scripts/update-registry.py scan \
#     --name postgres \
#     --version v15.17 \
#     --cve-total 0 \
#     --cve-critical 0 \
#     --cve-high 0 \
#     --scanner trivy \
#     --scanned-at "2026-03-08T12:00:00Z"
#
# registry.json schema (top level):
#   {
#     "schema_version": "1",
#     "last_updated": "<ISO8601>",
#     "images": {
#       "<name>:<version>": { ...entry... }
#     }
#   }
#
# Entry schema:
#   {
#     "name":             "postgres",
#     "version":          "v15.17",
#     "base_version":     "v15.17",
#     "profile":          "",
#     "category":         "runtime",        # runtime | builder
#     "public_image":     "ghcr.io/gwshield/postgres",
#     "tags":             ["ghcr.io/gwshield/postgres:v15.17", ...],
#     "digest":           "sha256:...",
#     "cosign_identity":  "https://github.com/gwshield/images/...",
#     "promoted_at":      "2026-03-08T12:00:00Z",
#     "scan": {
#       "status":         "clean",        # clean | findings | unknown
#       "total":          0,
#       "critical":       0,
#       "high":           0,
#       "scanner":        "trivy",
#       "scanned_at":     "2026-03-08T12:00:00Z"
#     }
#   }
# =============================================================================

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from datetime import datetime, timezone

REGISTRY_FILE = pathlib.Path("registry.json")
SCHEMA_VERSION = "1"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_registry() -> dict:
    if REGISTRY_FILE.exists():
        try:
            data = json.loads(REGISTRY_FILE.read_text())
            # Migrate older schema if needed
            if "images" not in data:
                data["images"] = {}
            if "schema_version" not in data:
                data["schema_version"] = SCHEMA_VERSION
            return data
        except json.JSONDecodeError as exc:
            print(f"WARNING: registry.json is invalid JSON ({exc}) — starting fresh", file=sys.stderr)
    return {
        "schema_version": SCHEMA_VERSION,
        "last_updated": now_utc(),
        "images": {},
    }


def save_registry(data: dict) -> None:
    data["last_updated"] = now_utc()
    REGISTRY_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"registry.json updated ({len(data['images'])} entries)")


def image_key(name: str, version: str) -> str:
    return f"{name}:{version}"


def parse_tags(tags_str: str) -> list[str]:
    """Accept space- or comma-separated tag list."""
    if not tags_str:
        return []
    tags_str = tags_str.replace(",", " ")
    return [t.strip() for t in tags_str.split() if t.strip()]


# ---------------------------------------------------------------------------
# Subcommand: promote
# ---------------------------------------------------------------------------

def cmd_promote(args: argparse.Namespace) -> None:
    registry = load_registry()
    key = image_key(args.name, args.version)
    tags = parse_tags(args.tags)

    existing = registry["images"].get(key, {})

    entry: dict = {
        "name":            args.name,
        "version":         args.version,
        "base_version":    args.base_version or args.version.split("-")[0],
        "profile":         args.profile or "",
        "category":        args.category or "runtime",
        "public_image":    f"ghcr.io/gwshield/{args.name}",
        "tags":            tags,
        "digest":          args.digest,
        "cosign_identity": args.cosign_identity or "",
        "promoted_at":     args.promoted_at or now_utc(),
        # Preserve existing scan data if not overwritten
        "scan":            existing.get("scan", {
            "status":     "unknown",
            "total":      None,
            "critical":   None,
            "high":       None,
            "scanner":    None,
            "scanned_at": None,
        }),
    }

    registry["images"][key] = entry
    save_registry(registry)
    print(f"promote: upserted {key} (digest: {args.digest})")


# ---------------------------------------------------------------------------
# Subcommand: scan
# ---------------------------------------------------------------------------

def cmd_scan(args: argparse.Namespace) -> None:
    registry = load_registry()
    key = image_key(args.name, args.version)

    if key not in registry["images"]:
        # Create a minimal skeleton if the image was never promoted
        # (e.g. scan runs before first promote — unlikely but safe)
        registry["images"][key] = {
            "name":            args.name,
            "version":         args.version,
            "base_version":    args.version.split("-")[0],
            "profile":         "",
            "public_image":    f"ghcr.io/gwshield/{args.name}",
            "tags":            [],
            "digest":          "",
            "cosign_identity": "",
            "promoted_at":     None,
            "scan":            {},
        }

    total    = int(args.cve_total)
    critical = int(args.cve_critical)
    high     = int(args.cve_high)

    if total == 0:
        status = "clean"
    else:
        status = "findings"

    registry["images"][key]["scan"] = {
        "status":     status,
        "total":      total,
        "critical":   critical,
        "high":       high,
        "scanner":    args.scanner or "trivy",
        "scanned_at": args.scanned_at or now_utc(),
    }

    save_registry(registry)
    print(f"scan: updated {key} → status={status}, total={total}, critical={critical}, high={high}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="registry.json processing engine — single source of truth for gwshield image metadata",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # --- promote ---
    p = sub.add_parser("promote", help="Upsert an image entry after a successful promote")
    p.add_argument("--name",             required=True,  help="Image name (e.g. postgres)")
    p.add_argument("--version",          required=True,  help="Full version tag (e.g. v15.17-tls)")
    p.add_argument("--base-version",     default="",     help="Base version without profile suffix (e.g. v15.17)")
    p.add_argument("--profile",          default="",     help="Profile suffix (e.g. tls, cluster, '')")
    p.add_argument("--category",         default="runtime", help="Image category: runtime | builder")
    p.add_argument("--digest",           required=True,  help="OCI digest of the pushed image (sha256:...)")
    p.add_argument("--tags",             default="",     help="Space- or comma-separated list of public tags")
    p.add_argument("--cosign-identity",  default="",     help="cosign OIDC identity URL")
    p.add_argument("--promoted-at",      default="",     help="ISO8601 timestamp (default: now)")

    # --- scan ---
    s = sub.add_parser("scan", help="Update CVE scan status for an image entry")
    s.add_argument("--name",         required=True,  help="Image name (e.g. postgres)")
    s.add_argument("--version",      required=True,  help="Full version tag (e.g. v15.17)")
    s.add_argument("--cve-total",    required=True,  help="Total findings after false-positive filter")
    s.add_argument("--cve-critical", default="0",    help="CRITICAL findings count")
    s.add_argument("--cve-high",     default="0",    help="HIGH findings count")
    s.add_argument("--scanner",      default="trivy", help="Scanner name")
    s.add_argument("--scanned-at",   default="",     help="ISO8601 timestamp (default: now)")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "promote":
        cmd_promote(args)
    elif args.command == "scan":
        cmd_scan(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
