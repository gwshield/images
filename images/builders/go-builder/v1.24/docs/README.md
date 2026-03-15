# gwshield go-builder v1.24

**Profile:** compile-only (`CGO_ENABLED=0`)
**Registry:** `ghcr.io/gwshield/go-builder:v1.24`
**Scan date:** 2026-03-08 — 0 HIGH / 0 CRITICAL CVEs

> **Builder image** — use as `FROM ghcr.io/gwshield/go-builder:v1.24 AS builder`
> in downstream multi-stage Dockerfiles. Not deployed as a runtime container.

---

## Overview

| Field | Value |
|---|---|
| Go version | 1.24.13 |
| Base image | `golang:1.24.13-alpine3.22` |
| Non-root UID | 65532 |
| CGO | disabled (`CGO_ENABLED=0`) |
| GOFLAGS | `-trimpath` |
| Shell | retained (`/bin/sh`) — required for downstream `RUN` steps |

---

## CVE baseline

### Go standard library

Go 1.24.13 is the current latest patch in the 1.24.x line. The initial baseline
(Go 1.24.2) carried 7 HIGH/CRITICAL stdlib CVEs — all resolved by upgrading to 1.24.13:

| CVE | Severity | Package | Fixed in |
|---|---|---|---|
| CVE-2025-68121 | CRITICAL | crypto/tls | 1.24.13 |
| CVE-2025-22874 | HIGH | crypto/x509 | 1.24.4 |
| CVE-2025-47907 | HIGH | database/sql | 1.24.6 |
| CVE-2025-58183 | HIGH | archive/tar | 1.24.8 |
| CVE-2025-61726 | HIGH | net/url | 1.24.12 |
| CVE-2025-61728 | HIGH | archive/zip | 1.24.12 |
| CVE-2025-61729 | HIGH | crypto/x509 | 1.24.11 |

### Alpine 3.22 packages

Alpine 3.22 ships OpenSSL 3.3.6+, resolving all OpenSSL findings from the
Alpine 3.21 baseline:

| CVE | Severity | Package | Fixed in Alpine |
|---|---|---|---|
| CVE-2025-15467 | CRITICAL | libssl3 | 3.22 (OpenSSL 3.3.6-r0) |
| CVE-2025-69419 | HIGH | libssl3 | 3.22 (OpenSSL 3.3.6-r0) |
| CVE-2025-69421 | HIGH | libssl3 | 3.22 (OpenSSL 3.3.6-r0) |

**Result: 0 HIGH / 0 CRITICAL CVEs.**

---

## Hardening applied

| Control | Detail |
|---|---|
| Digest-pinned base | `golang:1.24.13-alpine3.22` pinned by SHA256 |
| Non-root identity | UID/GID 65532 (`nonroot`) — all downstream builds run as nonroot |
| CGO disabled | `CGO_ENABLED=0` — enforces static linking for all downstream builds |
| `-trimpath` | Set in `GOFLAGS` — strips host paths from binaries |
| HISTFILE=/dev/null | Shell history disabled |
| Writable paths scoped | `/go/pkg/mod`, `/go/cache`, `/build` only |
| No extra tooling | No curl, wget, nc, linters, or test runners |

Shell (`/bin/sh`) is **retained intentionally** — required for downstream `RUN` steps.
Shell absence is only enforced in runtime images (scratch/distroless), not builder images.

---

## Source pins

| Component | Version | Digest |
|---|---|---|
| Go toolchain | `golang:1.24.13-alpine3.22` | `sha256:3641e0d9b931dc4f2f185dcd669c4679670e9277c8166a838ddb98a2d4389cb5` |
| Alpine base | 3.22 | `sha256:55ae5d250caebc548793f321534bc6a8ef1d116f334f18f4ada1b2daad3251b2` |
| Build date | 2026-03-08 | — |

---

## Rebuild trigger

- New Go 1.24.x patch release (stdlib CVE fix or security advisory)
- Alpine 3.22 package update for a HIGH/CRITICAL CVE
- Upstream digest change for `golang:1.24.13-alpine3.22`

**Tool version compatibility note:** `goimports v0.43.0` and `staticcheck 2026.1`
require Go >= 1.25 and cannot be installed on this image. Use `go-builder:v1.25-dev`
for those tools.
