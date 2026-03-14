# Roadmap

This document tracks the planned and completed milestones for **Gatewarden Shield**.
It is maintained alongside the [CHANGELOG.md](CHANGELOG.md) and updated as work progresses.

The project has two audiences with overlapping interests — see
`meta/docs/internal/` for the full contributor and enterprise pitch documents.

---

## Active

### v0.3.2-alpha — Next targets

- [ ] **PHP hardened image** (FPM profile — version TBD)
- [ ] **Go builder v1.26** — compile-only + dev variants
- [ ] **OCI provenance attestation** — SLSA Level 3 for all images

---

## Completed

### v0.3.1-alpha — Hub metadata: image size display (2026-03-14) ✓

- [x] **Image size field** — `image_size_bytes` (compressed OCI layer sum) correctly
  populated and displayed on the hub detail page for all 43 images
- [x] **Runnable size field** — hidden when not available; OCI registry API does not
  expose uncompressed layer sizes without a full image pull

### v0.3.0-alpha — OTel Collector Contrib + NATS Server (2026-03-14) ✓

- [x] **OTel Collector Contrib v0.147.0** — contrib profile, 0 CVEs, distroless/static,
  all receivers/exporters, OTLP gRPC+HTTP, health_check extension
- [x] **NATS Server v2.12.5 (standard)** — JetStream enabled, 0 CVEs, distroless/static,
  monitoring `/healthz`, no shell in runtime image

### v0.1.0-alpha — Initial release

- [x] **Traefik v3.6.9** — hardened, 0 CVEs, multi-arch (amd64 + arm64), smoke tested
- [x] **Mono-repo architecture** — `images/<name>/<version>/` self-contained layout
- [x] **Auto-discovery CI matrix** — `find images -name Dockerfile`; no manual entries
- [x] **Renovate integration** — automated PRs for Go toolchain, Alpine base image, service versions
- [x] **Weekly scheduled re-scan** — Trivy + Grype; GitHub issue opened on new findings
- [x] **Makefile** — local dev shortcuts (`build`, `scan`, `smoke`, `all`, `list`)
- [x] **Shared base-layers** — reusable Dockerfile patterns for nonroot user, ca-certs, tzdata
- [x] **Shared C/autoconf builder** — `shared/builders/c-autoconf/` snippet for C/make targets

### v0.1.1-alpha — nginx + Redis + PostgreSQL feature-sets

- [x] **nginx v1.28.2 (http)** — built from source, pcre2+zlib static, FROM scratch, 0 CVEs
- [x] **nginx v1.28.2 (http2)** — same as http with `--with-http_v2_module`, 0 CVEs
- [x] **nginx v1.28.2 (http3/QUIC)** — QuicTLS (`openssl-3.3.0-quic1`), pcre2+zlib static, 0 CVEs
- [x] **Redis v7.4.8 (standard)** — source build, libm static, DISABLE_SCRIPTING, FROM scratch, 0 CVEs
- [x] **Redis v7.4.8 (TLS)** — OpenSSL statically linked via LIBSSL_LIBS/LIBCRYPTO_LIBS, 0 CVEs
- [x] **Redis v7.4.8 (cluster-mode)** — config-level feature, cluster-enabled yes, 0 CVEs
- [x] **Redis v7.4.8 (cli)** — redis-cli only, no server binary, FROM scratch, standalone ops tool
- [x] **PostgreSQL v15.17 (standard)** — distroless/cc-debian12, pg_partman + pg_cron, 0 CVEs
- [x] **PostgreSQL v15.17 (TLS)** — OpenSSL static, 0 CVEs
- [x] **PostgreSQL v15.17 (cli)** — psql-only, no server binary, 0 CVEs
- [x] **BuildKit cache mounts** — Blacksmith sticky disk enabled for all apk stages
- [x] **CI push-event diff fix** — `HEAD~1..HEAD` for correct changed-file discovery

### v0.1.2-alpha — Public registry + supply chain + auto-docs (2026-03-08)

- [x] **PostgreSQL v15.17 (vector)** — pgvector v0.8.2 + pg_partman + pg_cron, 0 CVEs
- [x] **PostgreSQL v15.17 (timescale)** — TimescaleDB v2.25.1 + pg_partman + pg_cron, 0 CVEs
- [x] **cosign keyless signing** — Sigstore OIDC, Rekor transparency log; identity anchored to
      `gwshield/images` workflow (not the private build repo)
- [x] **SBOM attestation** — CycloneDX + SPDX via syft, attached to OCI manifest via `cosign attest`
- [x] **Public GHCR registry** at `ghcr.io/gwshield` — no login required; 13 images promoted
- [x] **Cross-org CI architecture** — private build in `RelicFrog/gwshield-images`,
      public promotion via `repository_dispatch` to `gwshield/images`; clean credential boundary
- [x] **GitHub App `gwshield-builder`** — cross-org dispatch auth; no long-lived PATs in hot paths
- [x] **GHCR cleanup workflow** — weekly orphaned manifest pruning, auto-discovery, dry-run mode
- [x] **registry.json processing engine** — `update-registry.py` single source of truth;
      `promote` + `scan` subcommands; idempotent upsert
- [x] **Auto-generated README** for `gwshield/images` — `generate-readme.py` renders from
      `registry.json`; triggered after every promote and every scan run
- [x] **scan → registry sync** — `update-public-registry` job dispatches CVE counts to
      `gwshield/images` after every Trivy run; CVE status column stays current in public README

### v0.1.3-alpha — Builder images + PostgreSQL v17.x + Functional tests (2026-03-08)

- [x] **Go builder v1.24 (compile-only)** — static CGO_ENABLED=0 baseline, 0 CVEs, published to `ghcr.io/gwshield`
- [x] **Go builder v1.24-dev** — adds golangci-lint, gofumpt, goimports, govulncheck, staticcheck, 0 CVEs
- [x] **Python builder v3.12 + v3.13 (compile-only)** — reproducible wheel builds, 0 CVEs
- [x] **Python builder v3.12-dev + v3.13-dev** — adds ruff, mypy, pytest, pip-audit, black, isort
- [x] **PostgreSQL v17.9 (standard)** — full port of v15.17 stack to PG17, 0 CVEs
- [x] **PostgreSQL v17.9 (TLS, cli, vector, timescale)** — all 5 profiles, 0 CVEs
- [x] **Functional test suite** — Level 1 functional tests for all image groups:
      `tests/functional/` scripts + daily CI cron (`functional.yml`)
- [x] **Public README improvements** — Version column in image tables; WIP / landing-page
      banner; MCP server and extended tooling announcement
- [x] **Hadolint CI fixes** — DL3002/DL3062 suppress directives in builder dev Dockerfiles

### v0.1.4-alpha — Rust builder images + CVE findings persistence + hub catalog (2026-03-11)

- [x] **Rust builder v1.87 (compile-only)** — `rust:1.87.0-alpine3.22`, musl static linking,
      `RUSTFLAGS="-C target-feature=+crt-static"`, x86_64-unknown-linux-musl + aarch64 targets
      pre-installed; nonroot UID 65532; 0 CVEs; published to `ghcr.io/gwshield/rust-builder:v1.87`.
- [x] **Rust builder v1.87-dev** — extends v1.87 with: `clippy`, `rustfmt` (rustup components),
      `cargo-audit v0.21.2`, `cargo-deny v0.18.2`; 0 CVEs; published to `ghcr.io/gwshield/rust-builder:v1.87-dev`.
- [x] **Rust functional tests** — `tests/functional/rust-builder.sh` + `rust-builder-dev.sh`;
      `tests/functional/fixtures/rust-app/`; `functional.yml` matrix entries added.
- [x] **Structured CVE findings persistence** — `cve_findings` Supabase table (migration 0029);
      `supabase_ingress.py findings` subcommand with Trivy parser + DiffID layer classification;
      `promote.yml` and `scan.yml` extended; `cve-rescan-origin.yml` backfill pipeline;
      132 rows written across all 23 images on 2026-03-11.
- [x] **gwshield-hub community catalog** — `hub.gwshield.io` launched (Next.js + Supabase +
      Netlify); image request system; admin area; 23 images in catalog.
- [x] **Pipeline hardening** — dispatch-verify step in `release-public.yml`; YAML lint in
      `ci.yml`; docker pull retries in `functional.yml`; `gwshield-builder` App `actions:write`.
- [x] **Runner migration** — all 6 workflows on `blacksmith-2vcpu-ubuntu-2404`; no GitHub
      Free minutes consumed.

### v0.1.5-alpha — HAProxy + Caddy standard (2026-03-11)

- [x] **HAProxy v3.1.16 (standard)** — static OpenSSL+PCRE2+zlib, `USE_PROMEX=1`, FROM scratch,
      musl loader, nonroot UID 65532; 0 CVEs; published to `ghcr.io/gwshield/haproxy:v3.1.16`.
- [x] **HAProxy v3.1.16-ssl** — TLS termination, TLSv1.2+, ECDHE+AEAD, HSTS, HTTP→HTTPS redirect;
      0 CVEs; published to `ghcr.io/gwshield/haproxy:v3.1.16-ssl`.
- [x] **Caddy v2.11.2 (standard)** — CGO_ENABLED=0 FROM scratch, auto-https off, gwshield-init
      banner, 0 CVEs; published to `ghcr.io/gwshield/caddy:v2.11.2`.

### v0.1.6-alpha — Caddy plugin profiles (2026-03-11)

- [x] **Caddy v2.11.2-cloudflare** — xcaddy + caddy-dns/cloudflare, DNS-01 ACME; 0 CVEs.
- [x] **Caddy v2.11.2-crowdsec** — xcaddy + caddy-crowdsec-bouncer (http + layer4); 0 CVEs.
- [x] **Caddy v2.11.2-security** — xcaddy + caddy-security (OIDC/JWT/OAuth2); 0 CVEs.
- [x] **Caddy v2.11.2-ratelimit** — xcaddy + caddy-ratelimit; 0 CVEs.
- [x] **Caddy v2.11.2-l4** — xcaddy + caddy-l4 (Layer-4/gRPC routing, commit-SHA pinned); 0 CVEs.
- [x] **xcaddy arch-aware download** — `ARG TARGETARCH` + `case` for amd64/arm64 SHA-512 verification;
      prevents "Invalid ELF image" failure on arm64 QEMU cross-builds.

### v0.1.7-alpha — Go builder v1.25 (2026-03-12)

- [x] **Go builder v1.25 (compile-only)** — `golang:1.25.8-alpine3.22`, CGO_ENABLED=0; 0 CVEs;
      published to `ghcr.io/gwshield/go-builder:v1.25`.
- [x] **Go builder v1.25-dev** — golangci-lint v2.11.3, gofumpt, govulncheck, staticcheck 2026.1
      (requires Go >= 1.25); 0 CVEs; published to `ghcr.io/gwshield/go-builder:v1.25-dev`.

### v0.1.8-alpha — Supabase image_type + pipeline stability (2026-03-12)

- [x] **Supabase `image_type` (migration 0033)** — insert-only field; `supabase_ingress.py`
      `--image-type` param + `upsert_image()` SELECT-first pattern; `release-public.yml`
      derives type from path; `promote.yml` passes it through; 36 images re-promoted.
- [x] **`useblacksmith/*` replaced in `build.yml`** — SHA-pinned `docker/*` Actions; Blacksmith
      runners kept; intermittent `401 Unauthorized` on Set up job eliminated.
- [x] **`sigstore/cosign-installer@v3` replaced in `promote.yml`** — direct cosign v3.0.5 binary
      download (SHA256-verified); same 401 root cause fixed.
- [x] **cosign attest `continue-on-error: true`** — absorbs cosign v3 bundle-fetch crash on
      re-promotes with legacy attestation bundles.
- [x] **HAProxy CI fixes** — `maxconn 4096`, broken pipe fixes in `haproxy.sh` + `haproxy-ssl.sh`.
- [x] **Supabase service role key rotated** — `sb_secret_...` format in both repos.

### v0.2.0-alpha — CI pipeline full stabilisation (2026-03-12)

- [x] **Sprint 1** — `scan.yml` concurrency guard; `useblacksmith/*` removed; Trivy version pinned;
      SARIF upload path fixed; `find` depth fixed to `-mindepth 3 -maxdepth 4`.
- [x] **Sprint 2+3** — `ubuntu-latest` → Blacksmith for 3 jobs; `parse-trivy.py` + `discover-targets.sh`
      extracted from inline YAML; `_functional-job.yml` reusable workflow created; `functional.yml`
      consolidated to single parameterised matrix.
- [x] **Bugfix sprint** — `timeout-minutes` hardcoded in reusable workflow (expression interpolation
      unsupported at job level); `docker/login-action` SHA-pinned; `_functional-job.yml` moved to
      top-level (GitHub Actions subdirectory constraint); `functional.yml` push-trigger guard job
      added; HAProxy SIGPIPE + `maxconn` fixes; AGENTS.md + CLAUDE.md updated; architecture docs
      rewritten (17 sections, DE + EN).

---

## Active / Next

### v0.2.2-alpha — Hub primary-row fix: nginx + go-builder profile tags (2026-03-13)

- [x] **`derive_profile_tag()` helper in `supabase_ingress.py`** — maps canonical pipeline
      profiles to Hub-facing `"standard"` tag value so `isPrimaryProfile()` renders correct
      parent rows without any Hub-side code change.
      Mappings: `nginx:""|"http"→standard`, `go-builder/rust-builder:""|"compile"→standard`;
      all other profiles pass through unchanged.
- [x] **DB patched: `nginx-http` `profile=http` → `standard`** — Hub now renders nginx family
      with a primary parent row (standard) and two variants (http2, http3).
- [x] **DB patched: `go-builder` `profile=compile` → `standard`** — v1.25 version group now
      renders with a primary parent row; v1.24 group (go-builder-dev) remains a variant.
- [x] **`TestDeriveProfileTag` test class** — 17 cases added to
      `scripts/tests/test_supabase_ingress.py`; total test count: 116 (was 99).

### v0.2.1-alpha — Supabase version tags + test suite + slug fixes (2026-03-12) ✓

- [x] **`version` image tag on every promote** — `derive_version_group(base_version)` →
      `major >= 10` = major only; `major < 10` = `major.minor`; delete-first write pattern;
      Hub catalog sub-grouping now driven by DB tag instead of client-side name parsing.
- [x] **`supabase_ingress.py` unit test suite** — 99 stdlib-only tests in
      `scripts/tests/test_supabase_ingress.py`; covers all pure helpers; pre-flight step in
      `promote.yml` before any DB write; hard-stops on failure (no `continue-on-error`).
- [x] **python-builder slug fix (canonical)** — `profile=""` dispatch shape falls back to
      `base_version` for slug construction; `python-builder / "" / v3.12` → `python-builder-v312`.
- [x] **python-builder slug fix (dev)** — `profile="dev"` dispatch shape combines `bv_norm` +
      suffix; `python-builder / "dev" / v3.12` → `python-builder-v312-dev`.
- [x] **Phantom row cleanup** — `python-builder` + `python-builder-dev` rows cascade-deleted
      from Supabase (174 rows); real images in `ghcr.io/gwshield` unaffected; final state:
      34 active images, 34 version-tags, 0 missing.

### Next targets (after v0.2.2-alpha)

- [ ] **PHP** — hardened FPM image, target version TBD; strip unused extensions; profiles: FPM + CLI
- [ ] **OCI provenance attestation** — SLSA Level 3 (`cosign attest --type slsaprovenance`)
- [ ] **Hub CVE detail page** — image detail page renders per-CVE history from `cve_findings` table
- [ ] **Hub → pipeline request workflow** — formal threshold + issue template
- [ ] **`check-stage` and `check-prod` devbox run scripts** — currently stubs

---

## Planned (committed, not scheduled)

These items are derived from the contributor and enterprise pitch documents
(`meta/docs/internal/`) and represent the agreed-upon direction for the project.

### Public presence

- [x] **gwshield-hub community catalog** — `hub.gwshield.io` launched (Next.js + Supabase +
      Netlify); full image catalog, changelog, requests, admin area; replaces the originally
      planned static Netlify landing page from `registry.json`
- [ ] **gwshield.io apex domain** — redirect or dedicated landing page at the apex; currently
      `hub.gwshield.io` serves the full catalog

### Community and contributor tooling

- [x] **Image request system** — live at `hub.gwshield.io/requests`; community can submit,
      vote, and comment on image requests; admin moderation queue at `/admin/requests`;
      requests feed directly into the pipeline target backlog
- [ ] **Hub → pipeline request promotion workflow** — formal threshold + issue template for
      converting a hub community request into a pipeline PR (vote threshold TBD; issue template
      to be created in `RelicFrog/gwshield-images`)
- [ ] **Contributor onboarding guide** — step-by-step: pick a target, build locally,
      open PR; includes pre-checked Dockerfile template
- [ ] **MCP server** — exposes container hardening patterns, CVE allowlist queries,
      and image metadata to AI coding tools (Claude Code, Copilot, etc.)

### Enterprise features

- [ ] **Compliance-ready build notes** — per-image PDF/Markdown export of scan evidence,
      SBOM, and risk decisions; suitable for SOC 2 / ISO 27001 artifact packages
- [ ] **Private hardened image pipeline** — self-hosted version of the build stack
      for organizations with air-gapped or regulated environments
- [ ] **Supply-chain verification tooling** — CLI helper to `cosign verify` + SBOM inspect
      any gwshield image in one command

### Scan and monitoring improvements

- [ ] **Multi-vendor scan comparison** — Trivy vs Grype vs Snyk side-by-side in CI summary
- [ ] **Dependabot / Renovate PR auto-merge gate** — scan must pass before auto-merge
- [ ] **CVE digest pinning** — weekly scan annotates affected digest in GitHub issue;
      links to the fixed promote run when resolved

---

## Long-term ideas (not committed)

- Hardened JVM image (GraalVM native — eliminates JDK from runtime layer)
- Hardened Rust service image template (zero-dep static binary baseline)
- Container signing verification step inside smoke tests (`cosign verify` as CI gate)
- `gwshield` CLI tool — pull, verify, and inspect hardened images in a single workflow

---

## How to propose a new target

Open a GitHub issue with:
1. Image name and target version
2. Upstream source repo and build method (Go / C/make / other)
3. Known CVE surface (check upstream trivy report)
4. Desired profiles (standard / TLS / cluster / etc.)

The [CONTRIBUTING.md](CONTRIBUTING.md) documents the per-image contract every new target must satisfy.
