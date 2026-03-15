# gwshield go-builder v1.25

**Profile:** compile-only (`CGO_ENABLED=0`)
**Registry:** `ghcr.io/gwshield/go-builder:v1.25`
**Scan date:** 2026-03-12 — 0 HIGH / 0 CRITICAL CVEs

> **Builder image** — use as `FROM ghcr.io/gwshield/go-builder:v1.25 AS builder`
> in downstream multi-stage Dockerfiles. Not deployed as a runtime container.

---

## Overview

| Field | Value |
|---|---|
| Go version | 1.25.8 |
| Base image | `golang:1.25.8-alpine3.22` |
| Non-root UID | 65532 |
| CGO | disabled (`CGO_ENABLED=0`) |
| GOFLAGS | `-trimpath` |
| Shell | retained (`/bin/sh`) — required for downstream `RUN` steps |

---

## CVE baseline

Go 1.25.8 resolves all stdlib CVEs present in Go 1.24.x at the time of build.
Alpine 3.22 ships OpenSSL 3.3.6+ resolving all Alpine 3.21 OpenSSL findings.

**Result:** 0 HIGH / 0 CRITICAL CVEs.

---

## Source pins

| Component | Version | SHA256 / Digest |
|---|---|---|
| Go toolchain | `golang:1.25.8-alpine3.22` | `sha256:6b7607461f105ccaa0615b6f7932dfd5b36c5d827a0770b5578e565107cc3adb` |
| Alpine base | 3.22 | `sha256:55ae5d250caebc548793f321534bc6a8ef1d116f334f18f4ada1b2daad3251b2` |
| Build date | 2026-03-12 | — |

---

## Rebuild trigger

- New Go 1.25.x patch release
- Alpine 3.22 package update for a HIGH/CRITICAL CVE
- Upstream digest change for `golang:1.25.8-alpine3.22`
