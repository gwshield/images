# Roadmap

This document tracks the planned and completed milestones for **Gatewarden Shield** —
a collection of hardened, zero-CVE OCI images built from source and published to
[ghcr.io/gwshield](https://github.com/orgs/gwshield/packages).

---

## Completed

### v0.1.0-alpha — Initial release

- [x] **Traefik v3.6.9** — hardened, 0 CVEs, rebuilt from source (Go), smoke tested
- [x] **Mono-repo architecture** — `images/<name>/<version>/` self-contained layout
- [x] **Auto-discovery CI matrix** — `find images -name Dockerfile`; no manual entries
- [x] **Renovate integration** — automated PRs for Go toolchain, Alpine base image, service versions
- [x] **Weekly scheduled re-scan** — Trivy + Grype; GitHub issue opened on new findings

### v0.1.1-alpha — nginx + Redis + PostgreSQL

- [x] **nginx v1.28.2 (http)** — built from source, pcre2+zlib static, FROM scratch, 0 CVEs
- [x] **nginx v1.28.2 (http2)** — same as http with `--with-http_v2_module`, 0 CVEs
- [x] **nginx v1.28.2 (http3/QUIC)** — QuicTLS (`openssl-3.3.0-quic1`), pcre2+zlib static, 0 CVEs
- [x] **Redis v7.4.8 (standard)** — source build, libm static, DISABLE_SCRIPTING, FROM scratch, 0 CVEs
- [x] **Redis v7.4.8 (TLS)** — OpenSSL statically linked, TLS-only listener, 0 CVEs
- [x] **Redis v7.4.8 (cluster-mode)** — cluster-enabled yes, 0 CVEs
- [x] **Redis v7.4.8 (cli)** — redis-cli only, no server binary, FROM scratch
- [x] **PostgreSQL v15.17 (standard)** — distroless/cc-debian12, pg_partman + pg_cron, 0 CVEs
- [x] **PostgreSQL v15.17 (TLS)** — OpenSSL static, 0 CVEs
- [x] **PostgreSQL v15.17 (cli)** — psql-only, no server binary, 0 CVEs

### v0.1.2-alpha — Public registry + supply chain + auto-docs (2026-03-08)

- [x] **PostgreSQL v15.17 (vector)** — pgvector v0.8.2 + pg_partman + pg_cron, 0 CVEs
- [x] **PostgreSQL v15.17 (timescale)** — TimescaleDB v2.25.1 + pg_partman + pg_cron, 0 CVEs
- [x] **cosign keyless signing** — Sigstore OIDC, Rekor transparency log
- [x] **SBOM attestation** — CycloneDX + SPDX via syft, attached to OCI manifest
- [x] **Public GHCR registry** at `ghcr.io/gwshield` — no login required; 13 images at launch
- [x] **registry.json processing engine** — single source of truth for all public image metadata
- [x] **Auto-generated README** — rendered from `registry.json`; updated after every promote and scan

### v0.1.3-alpha — Builder images + PostgreSQL v17.x + Functional tests (2026-03-08)

- [x] **Go builder v1.24 (compile-only)** — static `CGO_ENABLED=0` baseline, 0 CVEs
- [x] **Go builder v1.24-dev** — adds golangci-lint, gofumpt, goimports, govulncheck, staticcheck
- [x] **Python builder v3.12 + v3.13 (compile-only)** — reproducible wheel builds, 0 CVEs
- [x] **Python builder v3.12-dev + v3.13-dev** — adds ruff, mypy, pytest, pip-audit, black, isort
- [x] **PostgreSQL v17.9 (standard, TLS, cli, vector, timescale)** — full 5-profile stack, 0 CVEs
- [x] **Functional test suite** — Level 1 functional tests for all image groups; daily CI cron
- [x] **Public README improvements** — Version column; WIP / landing-page banner

### v0.1.4-alpha — Rust builder images + CVE findings + hub catalog (2026-03-11)

- [x] **Rust builder v1.87 (compile-only)** — `rust:1.87.0-alpine3.22`, musl static linking,
      nonroot UID 65532; 0 CVEs; published to `ghcr.io/gwshield/rust-builder:v1.87`
- [x] **Rust builder v1.87-dev** — extends v1.87 with `clippy`, `rustfmt`, `cargo-audit`,
      `cargo-deny`; 0 CVEs; published to `ghcr.io/gwshield/rust-builder:v1.87-dev`
- [x] **Rust functional tests** — static binary, musl target, clippy, rustfmt, cargo-audit,
      cargo-deny; fixture in `tests/functional/fixtures/rust-app/`
- [x] **Structured CVE findings** — per-CVE upstream history stored in hub for all 23 images;
      132 findings backfilled; 0 CRITICAL across all images
- [x] **gwshield-hub community catalog** — `hub.gwshield.io` launched; image request system;
      all 23 images in catalog with live CVE status

---

## Active / Next

### v0.1.5-alpha — Supply chain + PHP + hub CVE detail page

- [ ] **PHP** — hardened FPM image (target version TBD); strip unused extensions from runtime
- [ ] **OCI provenance attestation** — SLSA Level 3 (`cosign attest --type slsaprovenance`)
- [ ] **Hub CVE detail page** — per-image upstream CVE history rendered from structured findings;
      data already available (132 rows from backfill)
- [ ] **Hub → pipeline request workflow** — vote threshold definition + issue template

---

## Planned (committed, not scheduled)

### Public presence

- [ ] **gwshield.io apex domain** — redirect or dedicated landing page at the apex

### Community and contributor tooling

- [ ] **Hub → pipeline request promotion workflow** — formal threshold + issue template for
      converting a hub community request into a pipeline PR
- [ ] **Contributor onboarding guide** — step-by-step: pick a target, build locally, open PR;
      includes pre-checked Dockerfile template
- [ ] **MCP server** — exposes container hardening patterns, CVE allowlist queries, and image
      metadata to AI coding tools (Claude Code, Copilot, etc.)

### Enterprise features

- [ ] **Compliance-ready build notes** — per-image PDF/Markdown export of scan evidence,
      SBOM, and risk decisions; suitable for SOC 2 / ISO 27001 artifact packages
- [ ] **Supply-chain verification tooling** — CLI helper to `cosign verify` + SBOM inspect
      any gwshield image in one command

### Scan and monitoring improvements

- [ ] **Multi-vendor scan comparison** — Trivy vs Grype vs Snyk side-by-side in CI summary
- [ ] **CVE digest pinning** — weekly scan annotates affected digest in GitHub issue;
      links to the fixed promote run when resolved

---

## Long-term ideas (not committed)

- Hardened JVM image (GraalVM native — eliminates JDK from runtime layer)
- Container signing verification step inside smoke tests (`cosign verify` as CI gate)
- `gwshield` CLI tool — pull, verify, and inspect hardened images in a single workflow

---

## How to propose a new target

Open an image request at [hub.gwshield.io/requests](https://hub.gwshield.io/requests) or
open a GitHub issue with:
1. Image name and target version
2. Upstream source repo and build method
3. Known CVE surface (check upstream trivy report)
4. Desired profiles (standard / TLS / cluster / etc.)
