# gwshield go-builder v1.24-dev

**Profile:** dev (compile + lint + format + vuln scan)
**Registry:** `ghcr.io/gwshield/go-builder:v1.24-dev`
**Scan date:** 2026-03-08 — 0 HIGH / 0 CRITICAL CVEs

> **Builder image** — use as `FROM ghcr.io/gwshield/go-builder:v1.24-dev AS ci`
> in CI pipelines. Not deployed as a runtime container.

---

## Overview

Extends `gwshield/go-builder:v1.24` with the full Go CI toolchain.

| Tool | Version |
|---|---|
| Base image | `ghcr.io/gwshield/go-builder:v1.24` |
| golangci-lint | v2.11.2 |
| gofumpt | v0.9.2 |
| goimports | v0.42.0 |
| govulncheck | v1.1.4 |
| staticcheck | 2025.1.1 |

All tools are compiled with `CGO_ENABLED=0` — fully static binaries.

**Tool version compatibility note:** `goimports v0.43.0` requires Go >= 1.25
(`golang.org/x/tools v0.43.0` bumped its `go` directive). This image pins
`goimports v0.42.0` — the last Go 1.24-compatible release. Similarly,
`staticcheck 2026.1` requires Go >= 1.25; this image uses `2025.1.1`.
Use `go-builder:v1.25-dev` for these newer tool versions.

---

## CVE baseline

Inherits 0 HIGH / 0 CRITICAL from `go-builder:v1.24`. Dev tools are not
present in downstream runtime images and do not expand the CVE surface.

---

## Source pins

| Component | Version | Digest |
|---|---|---|
| Base image | `ghcr.io/gwshield/go-builder:v1.24` | `sha256:3d90a0589ad0a6daaf285ff6809891175eee7537511e3fcf34b7517a2cd8708a` |
| golangci-lint | v2.11.2 | — |
| gofumpt | v0.9.2 | — |
| goimports | v0.42.0 | — |
| govulncheck | v1.1.4 | — |
| staticcheck | 2025.1.1 | — |
| Build date | 2026-03-08 | — |

---

## Rebuild trigger

- New Go 1.24.x patch release
- New `golangci-lint` / `govulncheck` / `staticcheck` release with security fixes
- Alpine 3.22 update in the base image
- Tool version bumps tracked in `build/versions.env`
