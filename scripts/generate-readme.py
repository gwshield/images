#!/usr/bin/env python3
# =============================================================================
# generate-readme.py — render CATALOG.md from registry.json
# =============================================================================
# Reads registry.json (single source of truth) and writes CATALOG.md.
# Run by the readme-update workflow after every promote or scan event.
#
# Images are split into two sections:
#   Runtime images  — production service images (traefik, nginx, redis, postgres, …)
#   Builder images  — secure build baseline images (go-builder, python-builder, …)
#
# This script renders only dynamic content (image tables, CVE status, cosign
# table, timestamp footer). Static content (intro, build philosophy, hardening
# principles) lives in README.md and is never touched by this script.
#
# Usage:
#   python3 scripts/generate-readme.py \
#     --registry registry.json \
#     --output CATALOG.md
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

PROFILE_LABEL = {
    "":             "standard",
    "tls":          "TLS",
    "http2":        "HTTP/2",
    "http3":        "HTTP/3 / QUIC",
    "cluster":      "cluster mode",
    "cli":          "client only",
    "vector":       "pgvector",
    "timescale":    "TimescaleDB",
    "compile-only": "compile-only",
    "dev":          "compile + test + lint",
}

RUNTIME_DESCRIPTION = {
    "caddy":     "Caddy — modern web server / reverse proxy",
    "haproxy":   "HAProxy — high-performance TCP/HTTP load balancer",
    "nats":      "NATS — cloud-native messaging and event streaming",
    "nginx":     "nginx — HTTP server / reverse proxy",
    "otelcol":   "OpenTelemetry Collector — observability pipeline",
    "pomerium":  "Pomerium — identity-aware access proxy",
    "postgres":  "PostgreSQL — relational database",
    "redis":     "Redis — in-memory data store",
    "traefik":   "Traefik — cloud-native edge router",
    "valkey":    "Valkey — open-source Redis fork",
}

BUILDER_DESCRIPTION = {
    "go-builder":     "Go — reproducible static builds (CGO_ENABLED=0)",
    "python-builder": "Python — reproducible wheel builds",
    "rust-builder":   "Rust — reproducible static musl builds",
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
        return digest[7:19]
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
        return f"{total} findings ({critical} critical, {high} high)"
    return "not scanned"


def group_by_name(entries: list[dict]) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = {}
    for entry in entries:
        name = entry.get("name", "unknown")
        groups.setdefault(name, []).append(entry)
    for name in groups:
        groups[name].sort(key=lambda e: e.get("version", ""))
    return dict(sorted(groups.items()))


def split_by_category(images: dict) -> tuple[list[dict], list[dict]]:
    """Return (runtime_entries, builder_entries) sorted by name+version."""
    runtime, builder = [], []
    for entry in images.values():
        cat = entry.get("category", "runtime")
        if cat == "builder":
            builder.append(entry)
        else:
            runtime.append(entry)
    runtime.sort(key=lambda e: (e.get("name", ""), e.get("version", "")))
    builder.sort(key=lambda e: (e.get("name", ""), e.get("version", "")))
    return runtime, builder


# ---------------------------------------------------------------------------
# Sections
# ---------------------------------------------------------------------------

def render_header(last_updated: str) -> str:
    updated = fmt_date(last_updated) if last_updated else "—"
    return f"""\
# Gatewarden Shield — Image Catalog

> **This file is auto-generated from `registry.json` after every promote and scan run.**
> Do not edit manually — changes will be overwritten.
> Static content and documentation live in [README.md](README.md).

*Last updated: {updated}*

---
"""


def render_runtime_section(entries: list[dict]) -> str:
    if not entries:
        return ""
    lines: list[str] = []
    lines.append("## Runtime images\n")
    lines.append(
        "Production-hardened service images. Each image is compiled from upstream source "
        "with a patched toolchain, runs from a minimal `scratch` or distroless base, and "
        "ships with a cosign signature and SBOM.\n"
    )

    for name, group in group_by_name(entries).items():
        desc = RUNTIME_DESCRIPTION.get(name, name)
        lines.append(f"### {desc}\n")
        lines.append("| Tag | Version | Profile | Digest | CVE status | Promoted |")
        lines.append("|---|---|---|---|---|---|")
        for e in group:
            tag = e.get("version", "—")
            full_ref = f"`ghcr.io/gwshield/{name}:{tag}`"
            version = tag
            profile = profile_label(e.get("profile", ""))
            digest = short_digest(e.get("digest", ""))
            cve = scan_cell(e.get("scan") or {})
            promoted = fmt_date(e.get("promoted_at"))
            lines.append(f"| {full_ref} | `{version}` | {profile} | `{digest}` | {cve} | {promoted} |")
        lines.append("")

    lines.append("---\n")
    return "\n".join(lines)


def render_builder_section(entries: list[dict]) -> str:
    if not entries:
        return ""
    lines: list[str] = []
    lines.append("## Builder images\n")
    lines.append(
        "Secure build baseline images — published to enable reproducible, CVE-free builds "
        "in downstream multi-stage Dockerfiles. Builder images are **not** deployed as "
        "runtime containers.\n"
    )
    lines.append("```dockerfile")
    lines.append("# Example downstream usage")
    lines.append("FROM ghcr.io/gwshield/go-builder:v1.25 AS builder")
    lines.append("COPY . /build/myapp")
    lines.append("RUN go build -o /build/myapp .")
    lines.append("")
    lines.append("FROM scratch")
    lines.append("COPY --from=builder /build/myapp /myapp")
    lines.append("USER 65532:65532")
    lines.append('ENTRYPOINT ["/myapp"]')
    lines.append("```\n")

    for name, group in group_by_name(entries).items():
        desc = BUILDER_DESCRIPTION.get(name, name)
        lines.append(f"### {desc}\n")
        lines.append("| Tag | Version | Profile | Digest | CVE status | Promoted |")
        lines.append("|---|---|---|---|---|---|")
        for e in group:
            tag = e.get("version", "—")
            full_ref = f"`ghcr.io/gwshield/{name}:{tag}`"
            version = tag
            profile = profile_label(e.get("profile", ""))
            digest = short_digest(e.get("digest", ""))
            cve = scan_cell(e.get("scan") or {})
            promoted = fmt_date(e.get("promoted_at"))
            lines.append(f"| {full_ref} | `{version}` | {profile} | `{digest}` | {cve} | {promoted} |")
        lines.append("")

    lines.append("---\n")
    return "\n".join(lines)


def render_verify(runtime: list[dict], builder: list[dict]) -> str:
    ex_rt = runtime[0] if runtime else None
    ex_bl = builder[0] if builder else None

    lines: list[str] = ["## Verify an image\n", "```bash"]

    if ex_rt:
        n, v = ex_rt.get("name", "postgres"), ex_rt.get("version", "v15.17")
        d = ex_rt.get("digest", "sha256:<digest>")
        lines += [
            "# Runtime image — pull and verify",
            f"docker pull ghcr.io/gwshield/{n}:{v}",
            f"docker pull ghcr.io/gwshield/{n}@{d}",
            "",
            "cosign verify \\",
            "  --certificate-identity-regexp='https://github.com/gwshield/images.*' \\",
            "  --certificate-oidc-issuer='https://token.actions.githubusercontent.com' \\",
            f"  ghcr.io/gwshield/{n}:{v}",
            "",
        ]

    if ex_bl:
        n, v = ex_bl.get("name", "go-builder"), ex_bl.get("version", "v1.25")
        lines += [
            "# Builder image — pull and verify",
            f"docker pull ghcr.io/gwshield/{n}:{v}",
            "",
            "cosign verify \\",
            "  --certificate-identity-regexp='https://github.com/gwshield/images.*' \\",
            "  --certificate-oidc-issuer='https://token.actions.githubusercontent.com' \\",
            f"  ghcr.io/gwshield/{n}:{v}",
            "",
        ]

    if ex_rt:
        n, v = ex_rt.get("name", "postgres"), ex_rt.get("version", "v15.17")
        lines.append("# Inspect attached SBOM")
        lines.append(f"cosign download sbom ghcr.io/gwshield/{n}:{v}")

    lines += ["```\n", "---\n"]
    return "\n".join(lines)


def render_cosign_table(runtime: list[dict], builder: list[dict]) -> str:
    lines: list[str] = []
    lines.append("## Cosign verify — all images\n")
    lines.append("| Category | Image | Tag | Verify command |")
    lines.append("|---|---|---|---|")

    def cosign_row(category: str, entry: dict) -> str:
        name = entry.get("name", "—")
        tag = entry.get("version", "—")
        ref = f"ghcr.io/gwshield/{name}:{tag}"
        cmd = (
            f'`cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*"'
            f' --certificate-oidc-issuer="https://token.actions.githubusercontent.com" {ref}`'
        )
        return f"| {category} | `ghcr.io/gwshield/{name}` | `{tag}` | {cmd} |"

    for e in sorted(runtime, key=lambda x: (x.get("name", ""), x.get("version", ""))):
        lines.append(cosign_row("runtime", e))
    for e in sorted(builder, key=lambda x: (x.get("name", ""), x.get("version", ""))):
        lines.append(cosign_row("builder", e))

    lines.append("")
    lines.append("---\n")
    return "\n".join(lines)


def render_footer() -> str:
    return "Apache-2.0 — Gatewarden / RelicFrog Foundation\n"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def generate(
    registry_path: pathlib.Path,
    output_path: pathlib.Path,
) -> None:
    if not registry_path.exists():
        print(f"WARNING: {registry_path} not found — writing placeholder CATALOG", file=sys.stderr)
        output_path.write_text(
            "# Gatewarden Shield — Image Catalog\n\n"
            "Registry initializing — image metadata will appear after the first promote run.\n"
        )
        print(f"Placeholder CATALOG written to {output_path}")
        return

    data = json.loads(registry_path.read_text())
    images = data.get("images", {})
    last_updated = data.get("last_updated", "")

    if not images:
        print("WARNING: registry.json has no image entries — CATALOG will be sparse", file=sys.stderr)

    runtime, builder = split_by_category(images)

    sections = [
        render_header(last_updated),
        render_runtime_section(runtime),
        render_builder_section(builder),
        render_verify(runtime, builder),
        render_cosign_table(runtime, builder),
        render_footer(),
    ]

    catalog = "\n".join(s for s in sections if s)
    output_path.write_text(catalog)
    print(
        f"{output_path.name} written "
        f"({len(runtime)} runtime + {len(builder)} builder images, "
        f"{output_path.stat().st_size} bytes)"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate CATALOG.md from registry.json")
    parser.add_argument("--registry", default="registry.json")
    parser.add_argument("--output",   default="CATALOG.md")
    args = parser.parse_args()
    generate(pathlib.Path(args.registry), pathlib.Path(args.output))


if __name__ == "__main__":
    main()
