# gwshield rust-builder v1.87

**Profile:** compile-only (musl static target)
**Registry:** `ghcr.io/gwshield/rust-builder:v1.87`
**Scan date:** 2026-03-11 — 0 HIGH / 0 CRITICAL CVEs

> **Builder image** — use as `FROM ghcr.io/gwshield/rust-builder:v1.87 AS builder`
> in downstream multi-stage Dockerfiles. Not deployed as a runtime container.

---

## Overview

| Field | Value |
|---|---|
| Rust version | 1.87.0 |
| Base image | `rust:1.87.0-alpine3.22` |
| Target | `x86_64-unknown-linux-musl` (pre-installed) |
| Non-root UID | 65532 |
| `CARGO_INCREMENTAL` | `0` |
| Shell | retained (`/bin/sh`) — required for downstream `RUN` steps |

Downstream builds compiled with `RUSTFLAGS="-C target-feature=+crt-static"` produce
fully static binaries — verified via `readelf -d <binary> | grep NEEDED` → empty output.
Compatible with `FROM scratch` runtime stages.

---

## CVE baseline

`rust:1.87.0-alpine3.22` with Alpine 3.22 (OpenSSL 3.3.6+).
**Result:** 0 HIGH / 0 CRITICAL CVEs.

---

## Source pins

| Component | Version | SHA256 / Digest |
|---|---|---|
| Rust toolchain | `rust:1.87.0-alpine3.22` (index) | `sha256:126df0f2a57e675f9306fe180b833982ffb996e90a92a793bb75253cfeed5475` |
| Rust toolchain (amd64) | — | `sha256:2d5a7e008d9c1e86e54c0a3fffc00399eee945a13aa504fd5faf625e04110bf7` |
| Rust toolchain (arm64) | — | `sha256:fa3f412044d347294ad9c21eb3c9922a5e12e57b645ae53bbd27b8bc26173a7e` |
| Alpine base | 3.22 | `sha256:55ae5d250caebc548793f321534bc6a8ef1d116f334f18f4ada1b2daad3251b2` |
| Build date | 2026-03-11 | — |

---

## Rebuild trigger

- New Rust 1.87.x patch release
- Alpine 3.22 package update for a HIGH/CRITICAL CVE
- Upstream digest change for `rust:1.87.0-alpine3.22`
