# Changelog

All notable changes to **Gatewarden Shield** are documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- PHP hardened image (FPM profile — target version TBD)
- OCI provenance attestation (SLSA Level 3)
- gwshield.io landing page (static site from `registry.json`, searchable catalogue)
- Image request / voting system
- MCP server exposing container hardening patterns to AI tools

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
- **`tests/functional/`** — Level 1 functional tests for every image group:
  - `go-builder.sh` — multi-package compile, `go test`, static binary check
  - `go-builder-dev.sh` — golangci-lint, gofumpt, govulncheck, staticcheck, goimports
  - `python-builder.sh` — `pip install`, module execution, output verification
  - `python-builder-dev.sh` — ruff, mypy, pytest, black, pip-audit on fixture
  - `postgres.sh` — initdb, `pg_isready`, SQL round-trip, extension-load check
  - `redis.sh` — PING, `SET`/`GET`, TTL, `INFO server`, cluster-enabled check
  - `nginx.sh` — HTTP 200 on `/healthz`, static file content, `server_tokens off` check
  - `traefik.sh` — `/ping` 200, API `/api/rawdata`, web entrypoint, `/api/version` JSON
- Daily CI cron at 03:00 UTC against published `ghcr.io/gwshield` images; manual dispatch
  with `image_group` filter.

#### Public README improvements
- **Version column** added to all image tables (makes software version explicit alongside tag).
- **WIP / early-access banner** added — announces alpha status, upcoming gwshield.io landing
  page, MCP server, and extended tooling.

---

## [v0.1.2-alpha] — 2026-03-08

### Added

#### Cross-org public promotion pipeline
- **Public GHCR registry** at `ghcr.io/gwshield` — no login required; 13 images promoted.
- **cosign keyless signing** — Sigstore OIDC, Rekor transparency log; identity anchored to
  `gwshield/images` workflow.
- **SBOM attestation** — CycloneDX + SPDX via syft, attached to OCI manifest via
  `cosign attest`.
- **GHCR cleanup workflow** — weekly orphaned manifest pruning; auto-discovery; dry-run mode.

#### registry.json processing engine
- **`scripts/update-registry.py`** — single source of truth for all public image metadata;
  `promote` subcommand (upsert after each promote), `scan` subcommand (CVE status update);
  idempotent upsert keyed by `name:version`; schema version `"1"`.
- **`registry.json`** — auto-generated, never edited manually; fields per image entry:
  `name`, `version`, `base_version`, `profile`, `public_image`, `tags`, `digest`,
  `cosign_identity`, `promoted_at`, `scan.{status,total,critical,high,scanner,scanned_at}`.
- **`scripts/generate-readme.py`** — renders `README.md` from `registry.json`; groups images
  by service; per-image table with tag, profile, short digest, CVE status, promote date;
  `cosign verify` section per image.

#### PostgreSQL v15.17 — two new flavor profiles
- **vector** — PostgreSQL 15.17 + pgvector v0.8.2 + pg_partman v5.4.2 + pg_cron v1.6.7;
  same distroless/cc-debian12 runtime; 0 CVEs.
- **timescale** — PostgreSQL 15.17 + TimescaleDB v2.25.1 + pg_partman v5.4.2 + pg_cron v1.6.7;
  TimescaleDB MUST be first in `shared_preload_libraries`; 0 CVEs.

### Changed
- PostgreSQL v15.17 standard profile — added pg_partman v5.4.2 and pg_cron v1.6.7.
- PostgreSQL v15.13 → v15.17 patch update — bumped source tarball; renamed image directories.

---

## [v0.1.1-alpha] — 2026-03-01

### Added

#### Redis v7.4.8 — three hardened profiles
- **standard** — Redis built from source; `libm` statically linked; FROM scratch runtime;
  dangerous commands renamed; 0 CVEs.
- **TLS** — OpenSSL statically linked; TLS-only listener on port 6380; 0 CVEs.
- **cluster-mode** — same binary as standard; cluster mode via config; `cluster-enabled yes`;
  0 CVEs.
- **cli** — redis-cli only; no server binary; FROM scratch; 0 CVEs.

#### nginx v1.28.2 — three hardened profiles
- **http** — nginx built from source; pcre2, zlib statically linked; FROM scratch runtime; 0 CVEs.
- **http2** — same as http with `--with-http_v2_module`; 0 CVEs.
- **http3 / QUIC** — built against **QuicTLS** (`openssl-3.3.0-quic1`); pcre2 and zlib
  statically linked; 0 CVEs.

#### PostgreSQL v15.17 baseline
- **standard** — distroless/cc-debian12; pg_partman + pg_cron; 0 CVEs.
- **TLS** — OpenSSL static; 0 CVEs.
- **cli** — psql-only; no server binary; 0 CVEs.

---

## [v0.1.0-alpha] — 2026-02-28

### Added

#### Traefik v3.6.9 — initial hardened image
- Multi-stage Dockerfile: builder stage (Go 1.25.7-alpine3.23), runtime stage (FROM scratch).
- Binary rebuilt from source with `CGO_ENABLED=0`; verified statically linked.
- Non-root runtime: UID/GID 65532 (`nonroot`).
- Smoke tests: startup, `--help`, non-root assertion, no-shell assertion, `/ping` endpoint.

#### Mono-repo MVP architecture
- `images/<name>/<version>/` layout — self-contained per image target.
- CI matrix with auto-discovery via `find images -name Dockerfile`.
- Weekly scheduled re-scan (Trivy + Grype); opens GitHub issue on new findings.
- Renovate integration for automated version bump PRs.

---

[Unreleased]: https://github.com/gwshield/images/compare/v0.1.3-alpha...HEAD
[v0.1.3-alpha]: https://github.com/gwshield/images/compare/v0.1.2-alpha...v0.1.3-alpha
[v0.1.2-alpha]: https://github.com/gwshield/images/compare/v0.1.1-alpha...v0.1.2-alpha
[v0.1.1-alpha]: https://github.com/gwshield/images/compare/v0.1.0-alpha...v0.1.1-alpha
[v0.1.0-alpha]: https://github.com/gwshield/images/releases/tag/v0.1.0-alpha
