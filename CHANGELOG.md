# Changelog

All notable changes to **Gatewarden Shield** are documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- PHP hardened image (FPM profile — target version TBD)
- OCI provenance attestation (SLSA Level 3)
- Hub CVE detail page — per-image upstream CVE history visible in `hub.gwshield.io`
- Image request → pipeline promotion workflow (vote threshold + issue template)
- MCP server exposing container hardening patterns to AI tools

---

## [v0.1.4-alpha] — 2026-03-11

### Added

#### Rust builder images
- **Rust builder v1.87 (compile-only)** — based on `rust:1.87.0-alpine3.22`; musl static
  linking via `RUSTFLAGS="-C target-feature=+crt-static"`; `x86_64-unknown-linux-musl` and
  `aarch64-unknown-linux-musl` targets pre-installed; nonroot UID 65532; 0 CVEs; published to
  `ghcr.io/gwshield/rust-builder:v1.87`.
- **Rust builder v1.87-dev** — extends v1.87 with `clippy` and `rustfmt` (rustup components),
  `cargo-audit v0.21.2`, `cargo-deny v0.18.2` (compiled from source via `cargo install --locked`);
  0 CVEs; published to `ghcr.io/gwshield/rust-builder:v1.87-dev`.
- **Rust functional tests** — `rust-builder.sh` and `rust-builder-dev.sh` covering static binary
  compilation, musl target verification, clippy, rustfmt, cargo-audit, cargo-deny;
  `tests/functional/fixtures/rust-app/` fixture; daily CI matrix entry.

#### Structured CVE findings
- **Per-CVE findings now stored** in `hub.gwshield.io` — each promoted image's upstream CVE
  history (pre-hardening) is captured with severity, affected package, fixed version, and
  layer classification. All 23 images backfilled (132 findings total); 0 CRITICAL across all
  images confirms the hard CVE gate is working.

#### gwshield-hub community catalog
- **`hub.gwshield.io`** launched — full image catalog, changelog, image request system, admin
  area; all 23 images visible with CVE status sourced from the pipeline after every promote
  and scan run.

### Fixed

#### CVE remediation — Rust v1.87 base
- `rust:1.87.0-alpine3.22` shipped with 8 HIGH/CRITICAL CVEs in `binutils` and `libssl3`/`libcrypto3`.
  Fixed via targeted `apk upgrade --no-cache binutils libssl3 libcrypto3` in the builder stage.
  Post-fix scan: 0 CVEs. Historical pre-fix findings documented in hub for reference.

---

## [v0.1.3-alpha] — 2026-03-08

### Added

#### Builder images — Go + Python
- **Go builder v1.24 (compile-only)** — Alpine 3.22 base, `CGO_ENABLED=0`, `-trimpath`,
  nonroot UID 65532; 0 CVEs; published to `ghcr.io/gwshield/go-builder:v1.24`.
- **Go builder v1.24-dev** — extends v1.24 with full dev tooling: golangci-lint v2.11.2,
  gofumpt v0.9.2, goimports, govulncheck v1.1.4, staticcheck 2025.1.1; 0 CVEs;
  published to `ghcr.io/gwshield/go-builder:v1.24-dev`.
- **Python builder v3.12 + v3.13 (compile-only)** — Alpine base, UV + pip, nonroot UID 65532;
  0 CVEs.
- **Python builder v3.12-dev + v3.13-dev** — extends compile-only with: ruff, mypy, pytest,
  pip-audit, black, isort; 0 CVEs; published to `ghcr.io/gwshield`.

#### PostgreSQL v17.9 — full profile stack
- **PostgreSQL v17.9 (standard, TLS, cli, vector, timescale)** — full port of the v15.17
  profile stack to PostgreSQL 17.9. Extensions: pg_partman v5.4.3, pg_cron v1.6.7,
  pgvector v0.8.2, TimescaleDB v2.25.2. distroless/cc-debian12 runtime; 0 CVEs on all
  5 profiles. All 5 profiles published to `ghcr.io/gwshield/postgres:v17.9[-profile]`.

#### Functional test suite
- Level 1 functional tests for every image group; daily CI cron at 03:00 UTC against
  published `ghcr.io/gwshield` images; manual dispatch with `image_group` filter.

#### Public README improvements
- Version column added to all image tables; WIP / early-access banner.

---

## [v0.1.2-alpha] — 2026-03-08

### Added

#### Public registry + supply chain
- **cosign keyless signing** — Sigstore OIDC, Rekor transparency log.
- **SBOM attestation** — CycloneDX + SPDX via syft, attached to OCI manifest.
- **Public GHCR registry** at `ghcr.io/gwshield` — no login required; 13 images at launch.
- **registry.json** — machine-readable metadata; auto-updated after every promote and scan.
- **Auto-generated README** — rendered from `registry.json`; updated on every promote / scan.

#### PostgreSQL v15.17 — vector + timescale profiles
- **vector** — pgvector v0.8.2 + pg_partman + pg_cron; 0 CVEs.
- **timescale** — TimescaleDB v2.25.1 + pg_partman + pg_cron; 0 CVEs.

---

## [v0.1.1-alpha] — 2026-03-01

### Added

#### nginx v1.28.2 — three hardened profiles
- **http** — built from source, pcre2+zlib static, FROM scratch, 0 CVEs.
- **http2** — same as http with `--with-http_v2_module`, 0 CVEs.
- **http3/QUIC** — QuicTLS (`openssl-3.3.0-quic1`), pcre2+zlib static, 0 CVEs.

#### Redis v7.4.8 — four hardened profiles
- **standard** — source build, libm static, DISABLE_SCRIPTING, FROM scratch, 0 CVEs.
- **TLS** — OpenSSL statically linked, TLS-only listener, 0 CVEs.
- **cluster-mode** — `cluster-enabled yes`, 0 CVEs.
- **cli** — redis-cli only, no server binary, FROM scratch.

#### PostgreSQL v15.17 — three hardened profiles
- **standard** — distroless/cc-debian12, pg_partman + pg_cron, 0 CVEs.
- **TLS** — OpenSSL static, 0 CVEs.
- **cli** — psql-only, no server binary, 0 CVEs.

---

## [v0.1.0-alpha] — 2026-02-28

### Added

#### Traefik v3.6.9 — initial hardened image
- Multi-stage Dockerfile; binary rebuilt from source with `CGO_ENABLED=0`; FROM scratch runtime;
  non-root UID 65532; 0 CVEs; smoke tested.

#### Mono-repo architecture
- `images/<name>/<version>/` self-contained layout; auto-discovery CI matrix;
  Renovate integration; weekly scheduled re-scan (Trivy + Grype); Makefile.

---

[Unreleased]: https://github.com/gwshield/images/compare/v0.1.4-alpha...HEAD
[v0.1.4-alpha]: https://github.com/gwshield/images/compare/v0.1.3-alpha...v0.1.4-alpha
[v0.1.3-alpha]: https://github.com/gwshield/images/compare/v0.1.2-alpha...v0.1.3-alpha
[v0.1.2-alpha]: https://github.com/gwshield/images/compare/v0.1.1-alpha...v0.1.2-alpha
[v0.1.1-alpha]: https://github.com/gwshield/images/compare/v0.1.0-alpha...v0.1.1-alpha
[v0.1.0-alpha]: https://github.com/gwshield/images/releases/tag/v0.1.0-alpha
