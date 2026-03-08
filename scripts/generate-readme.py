#!/usr/bin/env python3
# =============================================================================
# generate-readme.py — render README.md from registry.json
# =============================================================================
# Reads registry.json (single source of truth) and writes README.md.
# Run by the readme-update workflow after every promote or scan event.
#
# Usage:
#   python3 scripts/generate-readme.py \
#     --registry registry.json \
#     --output README.md
# =============================================================================

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SCAN_BADGE = {
    "clean":    "0 CVEs",
    "findings": "findings",
    "unknown":  "not scanned",
    None:       "not scanned",
}

PROFILE_LABEL = {
    "":          "standard",
    "tls":       "TLS",
    "http2":     "HTTP/2",
    "http3":     "HTTP/3 / QUIC",
    "cluster":   "cluster mode",
    "cli":       "client only",
    "vector":    "pgvector",
    "timescale": "TimescaleDB",
}

IMAGE_DESCRIPTION = {
    "postgres":  "PostgreSQL — relational database",
    "redis":     "Redis — in-memory data store",
    "nginx":     "nginx — HTTP server / reverse proxy",
    "traefik":   "Traefik — cloud-native edge router",
}


def fmt_date(iso: str | None) -> str:
    if not iso:
        return "—"
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return iso[:10] if len(iso) >= 10 else iso


def short_digest(digest: str) -> str:
    if digest and digest.startswith("sha256:"):
        return digest[7:19]  # first 12 hex chars
    return digest or "—"


def profile_label(profile: str) -> str:
    return PROFILE_LABEL.get(profile, profile or "standard")


def scan_cell(scan: dict) -> str:
    status = scan.get("status") if scan else None
    total = scan.get("total") if scan else None
    if status == "clean" or total == 0:
        return "0 CVEs"
    if status == "findings" and total is not None:
        critical = scan.get("critical", 0) or 0
        high = scan.get("high", 0) or 0
        return f"{total} ({critical} CRIT / {high} HIGH)"
    return "not scanned"


def group_by_name(images: dict) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = {}
    for entry in images.values():
        name = entry.get("name", "unknown")
        groups.setdefault(name, []).append(entry)
    # Sort entries within group by version
    for name in groups:
        groups[name].sort(key=lambda e: e.get("version", ""))
    return dict(sorted(groups.items()))


# ---------------------------------------------------------------------------
# Sections
# ---------------------------------------------------------------------------

def render_header() -> str:
    return """\
# Gatewarden Shield — Hardened Container Images

Zero-CVE, production-hardened container images. Built from source, signed with
cosign, SBOM attached. All images run as non-root (UID 65532) with no shell,
no package manager, and no network utilities in the runtime layer.

> The source build pipeline is private. This registry is the public distribution
> endpoint. Every image is built from upstream source tarballs with SHA-256
> verification, scanned with Trivy and Grype before promotion, and cosign-signed
> with a keyless Sigstore OIDC identity.

---
"""


def render_image_table(groups: dict[str, list[dict]]) -> str:
    lines: list[str] = []
    lines.append("## Available images\n")

    for name, entries in groups.items():
        desc = IMAGE_DESCRIPTION.get(name, name)
        lines.append(f"### {desc}\n")
        lines.append("| Tag | Profile | Digest | CVE status | Promoted |")
        lines.append("|---|---|---|---|---|")
        for e in entries:
            tag = e.get("version", "—")
            full_ref = f"`ghcr.io/gwshield/{name}:{tag}`"
            profile = profile_label(e.get("profile", ""))
            digest = short_digest(e.get("digest", ""))
            scan = e.get("scan") or {}
            cve = scan_cell(scan)
            promoted = fmt_date(e.get("promoted_at"))
            lines.append(f"| {full_ref} | {profile} | `{digest}` | {cve} | {promoted} |")
        lines.append("")

    return "\n".join(lines)


def render_hardening() -> str:
    return """\
## Hardening principles

- Built from upstream source tarballs with SHA-256 verification
- Multi-stage builds — `FROM scratch` or distroless runtime layer
- No shell, no package manager, no `curl`/`wget` in the runtime layer
- Non-root execution: UID/GID 65532
- Hardened compiler flags: `-fstack-protector-strong`, `-D_FORTIFY_SOURCE=2`, RELRO, NOW
- Trivy + Grype CVE scan gate — 0 unfixed HIGH/CRITICAL findings at release time
- cosign keyless signed (Sigstore / OIDC) — no long-lived key material
- SBOM attached to OCI manifest (CycloneDX + SPDX)

---
"""


def render_verify(groups: dict[str, list[dict]]) -> str:
    # Use the first available image as example
    example_name = next(iter(groups), "postgres")
    example_entries = groups.get(example_name, [])
    example_entry = example_entries[0] if example_entries else {}
    example_version = example_entry.get("version", "v15.17")
    example_digest = example_entry.get("digest", "sha256:<digest>")

    lines: list[str] = []
    lines.append("## Verify an image\n")
    lines.append("```bash")
    lines.append(f"# Pull by tag")
    lines.append(f"docker pull ghcr.io/gwshield/{example_name}:{example_version}")
    lines.append("")
    lines.append(f"# Pull by immutable digest")
    lines.append(f"docker pull ghcr.io/gwshield/{example_name}@{example_digest}")
    lines.append("")
    lines.append("# Verify cosign signature")
    lines.append("cosign verify \\")
    lines.append("  --certificate-identity-regexp='https://github.com/gwshield/images.*' \\")
    lines.append("  --certificate-oidc-issuer='https://token.actions.githubusercontent.com' \\")
    lines.append(f"  ghcr.io/gwshield/{example_name}:{example_version}")
    lines.append("")
    lines.append("# Inspect attached SBOM")
    lines.append(f"cosign download sbom ghcr.io/gwshield/{example_name}:{example_version}")
    lines.append("```\n")
    lines.append("---\n")
    return "\n".join(lines)


def render_cosign_table(groups: dict[str, list[dict]]) -> str:
    lines: list[str] = []
    lines.append("## Cosign verify — all images\n")
    lines.append("| Image | Tag | Verify command |")
    lines.append("|---|---|---|")
    for name, entries in groups.items():
        for e in entries:
            tag = e.get("version", "—")
            ref = f"ghcr.io/gwshield/{name}:{tag}"
            cmd = (
                f'`cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*"'
                f' --certificate-oidc-issuer="https://token.actions.githubusercontent.com" {ref}`'
            )
            lines.append(f"| `ghcr.io/gwshield/{name}` | `{tag}` | {cmd} |")
    lines.append("")
    lines.append("---\n")
    return "\n".join(lines)


def render_footer(last_updated: str) -> str:
    updated = fmt_date(last_updated) if last_updated else "—"
    return f"""\
## License

Apache-2.0 — Gatewarden / RelicFrog Foundation

---

*Registry last updated: {updated}. This file is auto-generated — do not edit manually.*
"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def generate(registry_path: pathlib.Path, output_path: pathlib.Path) -> None:
    if not registry_path.exists():
        print(f"ERROR: {registry_path} not found", file=sys.stderr)
        sys.exit(1)

    data = json.loads(registry_path.read_text())
    images = data.get("images", {})
    last_updated = data.get("last_updated", "")

    if not images:
        print("WARNING: registry.json has no image entries — README will be sparse", file=sys.stderr)

    groups = group_by_name(images)

    sections = [
        render_header(),
        render_image_table(groups),
        render_hardening(),
        render_verify(groups),
        render_cosign_table(groups),
        render_footer(last_updated),
    ]

    readme = "\n".join(sections)
    output_path.write_text(readme)
    print(f"README.md written ({len(images)} images, {output_path.stat().st_size} bytes)")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate README.md from registry.json"
    )
    parser.add_argument(
        "--registry", default="registry.json",
        help="Path to registry.json (default: registry.json)"
    )
    parser.add_argument(
        "--output", default="README.md",
        help="Output path for README.md (default: README.md)"
    )
    args = parser.parse_args()
    generate(pathlib.Path(args.registry), pathlib.Path(args.output))


if __name__ == "__main__":
    main()
