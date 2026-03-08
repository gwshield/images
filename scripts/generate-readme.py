#!/usr/bin/env python3
# =============================================================================
# generate-readme.py — render README.md from registry.json
# =============================================================================
# Reads registry.json (single source of truth) and writes README.md.
# Run by the readme-update workflow after every promote or scan event.
#
# Images are split into two sections:
#   Runtime images  — production service images (traefik, nginx, redis, postgres)
#   Builder images  — secure build baseline images (go-builder, python-builder)
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

PROFILE_LABEL = {
    "":            "standard",
    "tls":         "TLS",
    "http2":       "HTTP/2",
    "http3":       "HTTP/3 / QUIC",
    "cluster":     "cluster mode",
    "cli":         "client only",
    "vector":      "pgvector",
    "timescale":   "TimescaleDB",
    "compile-only": "compile-only",
    "dev":         "compile + test + lint",
}

RUNTIME_DESCRIPTION = {
    "postgres": "PostgreSQL — relational database",
    "redis":    "Redis — in-memory data store",
    "nginx":    "nginx — HTTP server / reverse proxy",
    "traefik":  "Traefik — cloud-native edge router",
}

BUILDER_DESCRIPTION = {
    "go-builder":     "Go — reproducible static builds (CGO_ENABLED=0)",
    "python-builder": "Python — reproducible wheel builds",
    "node-builder":   "Node.js — deterministic package builds",
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

def render_header() -> str:
    return """\
# Gatewarden Shield — Hardened Container Images

Zero-CVE, production-hardened container images and secure build baselines.
Built from source, signed with cosign, SBOM attached.

All runtime images run as non-root (UID 65532) with no shell, no package
manager, and no network utilities in the runtime layer.

> **This registry is currently in early access (alpha).** We are actively
> expanding the image catalogue and working on a dedicated landing page at
> **gwshield.io** — featuring an interactive image database, CVE delta
> comparisons, and a request form for new zero-CVE image targets.
>
> Coming soon to this repository:
> - **MCP server** — a Model Context Protocol server for querying and
>   consuming hardened image metadata directly from AI-assisted workflows
> - **Extended tooling** — signing verification helpers, SBOM diffing,
>   and policy-as-code examples
>
> Until the landing page launches, watch this repository or follow
> [@RelicFrog](https://github.com/RelicFrog) for updates.

> The source build pipeline is private. This registry is the public distribution
> endpoint. Every image is built from upstream source with SHA-256 verification,
> scanned with Trivy and Grype before promotion, and cosign-signed with a
> keyless Sigstore OIDC identity.

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
    lines.append("FROM ghcr.io/gwshield/go-builder:1.24 AS builder")
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


def render_hardening() -> str:
    return """\
## Hardening principles

**Runtime images**
- Compiled from upstream source tarballs with SHA-256 verification
- Multi-stage builds — `FROM scratch` or distroless runtime layer
- No shell, no package manager, no `curl`/`wget` in the runtime layer
- Non-root execution: UID/GID 65532
- Hardened compiler flags: `-fstack-protector-strong`, `-D_FORTIFY_SOURCE=2`, RELRO, NOW

**Builder images**
- Digest-pinned toolchain base (golang:alpine, python:alpine, ...)
- `CGO_ENABLED=0` and `-trimpath` set by default
- Non-root execution: UID/GID 65532
- No test runners or linters in compile-only profiles
- Shell retained intentionally for downstream `RUN` steps

**All images**
- Trivy + Grype CVE scan gate — 0 unfixed HIGH/CRITICAL at release time
- cosign keyless signed (Sigstore / OIDC) — no long-lived key material
- SBOM attached to OCI manifest (CycloneDX + SPDX)

---
"""


def render_verify(runtime: list[dict], builder: list[dict]) -> str:
    # Pick one runtime + one builder as examples if available
    ex_rt = runtime[0] if runtime else None
    ex_bl = builder[0] if builder else None

    lines: list[str] = ["## Verify an image\n", "```bash"]

    if ex_rt:
        n, v = ex_rt.get("name", "postgres"), ex_rt.get("version", "v15.17")
        d = ex_rt.get("digest", "sha256:<digest>")
        lines += [
            f"# Runtime image — pull and verify",
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
        n, v = ex_bl.get("name", "go-builder"), ex_bl.get("version", "1.24")
        lines += [
            f"# Builder image — pull and verify",
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
        lines.append(f"# Inspect attached SBOM")
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
        print(f"WARNING: {registry_path} not found — writing placeholder README", file=sys.stderr)
        output_path.write_text(
            "# Gatewarden Shield — Hardened Container Images\n\n"
            "Registry initializing — image metadata will appear after the first promote run.\n"
        )
        print(f"Placeholder README written to {output_path}")
        return

    data = json.loads(registry_path.read_text())
    images = data.get("images", {})
    last_updated = data.get("last_updated", "")

    if not images:
        print("WARNING: registry.json has no image entries — README will be sparse", file=sys.stderr)

    runtime, builder = split_by_category(images)

    sections = [
        render_header(),
        render_runtime_section(runtime),
        render_builder_section(builder),
        render_hardening(),
        render_verify(runtime, builder),
        render_cosign_table(runtime, builder),
        render_footer(last_updated),
    ]

    readme = "\n".join(sections)
    output_path.write_text(readme)
    print(
        f"README.md written "
        f"({len(runtime)} runtime + {len(builder)} builder images, "
        f"{output_path.stat().st_size} bytes)"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate README.md from registry.json")
    parser.add_argument("--registry", default="registry.json")
    parser.add_argument("--output",   default="README.md")
    args = parser.parse_args()
    generate(pathlib.Path(args.registry), pathlib.Path(args.output))


if __name__ == "__main__":
    main()
