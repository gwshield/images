# gwshield go-builder v1.25-dev

**Profile:** dev (compile + lint + format + vuln scan)
**Registry:** `ghcr.io/gwshield/go-builder:v1.25-dev`
**Scan date:** 2026-03-12 — 0 HIGH / 0 CRITICAL CVEs

> **Builder image** — use as `FROM ghcr.io/gwshield/go-builder:v1.25-dev AS ci`
> in CI pipelines. Not deployed as a runtime container.

---

## Overview

Extends `gwshield/go-builder:v1.25` with the full Go CI toolchain.

| Tool | Version |
|---|---|
| Base image | `ghcr.io/gwshield/go-builder:v1.25` |
| golangci-lint | v2.11.3 |
| gofumpt | v0.9.2 |
| goimports | v0.43.0 |
| govulncheck | v1.1.4 |
| staticcheck | 2026.1 |

`staticcheck 2026.1` requires Go >= 1.25 — not available on the v1.24 builder.
`goimports v0.43.0` requires Go >= 1.25 (golang.org/x/tools v0.43.0).

---

## CVE baseline

Inherits 0 HIGH / 0 CRITICAL from `go-builder:v1.25`. Dev tools are not present in
downstream runtime images.

---

## Source pins

| Component | Version | Digest |
|---|---|---|
| Base image | `ghcr.io/gwshield/go-builder:v1.25` | `sha256:54967b6a5508ecee0b3da32631f2788741458c867364fa1e3c70cd9317d4c68f` |
| Build date | 2026-03-12 | — |

---

## Rebuild trigger

- New Go 1.25.x patch release
- New `golangci-lint` / `govulncheck` / `staticcheck` release with security fixes
- Alpine 3.22 update in the base image
