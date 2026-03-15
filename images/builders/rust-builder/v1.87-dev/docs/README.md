# gwshield rust-builder v1.87-dev

**Profile:** dev (compile + clippy + rustfmt + cargo-audit + cargo-deny)
**Registry:** `ghcr.io/gwshield/rust-builder:v1.87-dev`
**Scan date:** 2026-03-11 — 0 HIGH / 0 CRITICAL CVEs

> **Builder image** — use as `FROM ghcr.io/gwshield/rust-builder:v1.87-dev AS ci`
> in CI pipelines. Not deployed as a runtime container.

---

## Overview

Extends `gwshield/rust-builder:v1.87` with the full Rust CI toolchain.

| Tool | Version | Install method |
|---|---|---|
| Base image | `ghcr.io/gwshield/rust-builder:v1.87` | — |
| clippy | 1.87.0 (toolchain) | `rustup component add` |
| rustfmt | 1.87.0 (toolchain) | `rustup component add` |
| cargo-audit | 0.21.2 | `cargo install --locked` |
| cargo-deny | 0.18.2 | `cargo install --locked` |

`cargo-audit` and `cargo-deny` are installed with `--locked` for reproducible builds.

`cargo-audit` downloads the RustSec advisory DB at runtime during CI (network call).
Handle unavailability gracefully in CI pipelines.

---

## CVE baseline

Inherits 0 HIGH / 0 CRITICAL from `rust-builder:v1.87`. Dev tools are not in
downstream runtime images.

---

## Source pins

| Component | Version | Digest |
|---|---|---|
| Base image | `ghcr.io/gwshield/rust-builder:v1.87` | `sha256:f36d5bb4a70303f4e97583635af6ab9a6c6c7918898bd5905bf86324bb25495f` |
| cargo-audit | 0.21.2 | — |
| cargo-deny | 0.18.2 | — |
| Build date | 2026-03-11 | — |

---

## Rebuild trigger

- New Rust 1.87.x patch release
- New `cargo-audit` / `cargo-deny` release with security fixes
- Alpine 3.22 update in the base builder image
