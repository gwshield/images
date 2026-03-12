# Changelog

All notable changes to **Gatewarden Shield** are documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
Commits follow [Conventional Commits](https://www.conventionalcommits.org/).

---

## [Unreleased]

### Planned
- PHP hardened image (FPM profile — target version TBD)
- Go builder v1.26 (compile-only + dev variants)
- OCI provenance attestation (SLSA Level 3)
- Hub → pipeline request promotion workflow (vote threshold definition + issue template)
- MCP server exposing container hardening patterns to AI tools
- `check-stage` and `check-prod` devbox run scripts (still stubs)

---

## [v0.2.1-alpha] — 2026-03-12

### Added

#### Supabase `version` tag + `supabase_ingress.py` unit tests (`feat(supabase)`, `test(supabase)`)

- **`version` image tag** written on every promote run — `tag_key='version'`, `tag_value` derived from
  `base_version` via `derive_version_group()`:
  - `major >= 10` → major only (e.g. `v15.17` → `"15"`, `v17.9` → `"17"`)
  - `major < 10`  → `major.minor` (e.g. `v3.12.4` → `"3.12"`, `v1.28.2` → `"1.28"`)
  - Written as delete-first + insert (UNIQUE constraint includes `tag_value` — safe version bump)
  - Wrapped in try/except — Supabase outage never blocks a promote
- **Hub use**: `tag_key='version'` drives sub-grouping in the Hub catalog list view;
  `extractVersionGroup()` in `images-catalog-view.tsx` replaced by direct tag lookup.
- **`scripts/tests/test_supabase_ingress.py`** — new unit test suite for all pure helpers in
  `supabase_ingress.py`; 99 tests, stdlib `unittest` only (no external deps):
  - `TestDeriveVersionGroup` — 18 cases covering all image families + boundary (major 9/10) + no-v-prefix
  - `TestDeriveSlug` — 35 cases covering all slug derivations incl. python-builder dispatch shapes
  - `TestDeriveImageType` / `TestResolveImageType` — 15 cases
  - `TestDeriveOsTag` — 10 cases
  - `TestExtractFindingsFromTrivy` — 6 cases (empty results, None vulns, fixed/unfixed, truncation, PURL)
  - `TestComponentType` — 10 cases
  - `TestMainEnvGuard` — env-var guard exit-code check
- **`promote.yml` pre-flight test step** — `python3 scripts/tests/test_supabase_ingress.py` runs
  immediately after `Set up Python`, before any DB or registry write; no `continue-on-error` — test
  failure hard-stops the promote.

### Fixed

#### `supabase_ingress.py` — python-builder slug derivation (`fix(supabase)`)

Two slug bugs uncovered by the new tests and confirmed in the DB:

1. **`python-builder` canonical profile**: `release-public.yml` dispatches `python-builder:v3.12`
   with `profile=""` (directory name `v3.12` → `base_version=v3.12`, profile stripped to `""`).
   `derive_slug("python-builder", "")` previously returned `"python-builder"` — wrong Hub slug.
   **Fix**: when `profile=""` for `python-builder`, fall back to `base_version` for slug construction:
   `python-builder / "" / v3.12` → `python-builder-v312`.

2. **`python-builder` dev profile**: `release-public.yml` dispatches `python-builder:v3.12-dev`
   with `profile="dev"` (suffix after `base_version` strip). `derive_slug("python-builder", "dev")`
   previously returned `"python-builder-dev"` — missing version segment.
   **Fix**: slug always built from `base_version + optional suffix`:
   `python-builder / "dev" / v3.12` → `python-builder-v312-dev`.

   New derivation logic for python-builder:
   - Normalise `base_version` → `bv_norm` (e.g. `v3.12` → `v312`)
   - Strip any version prefix from `profile` to get pure suffix (`"dev"` stays `"dev"`, `"v3.12"` → `""`)
   - Combine: `python-builder-{bv_norm}` or `python-builder-{bv_norm}-{suffix}`

#### Supabase phantom row cleanup (`fix(supabase)`)

Two phantom image rows accumulated in Supabase from pre-fix promote runs:
- `slug=python-builder` (UUID `a7179fed`) — held versions `v3.12` + `v3.13`, 78 snapshots
- `slug=python-builder-dev` (UUID `2456bdd6`) — held versions `v3.12-dev` + `v3.13-dev`, 79 snapshots

Both rows cascade-deleted (174 rows total across `images`, `image_versions`,
`image_metadata_snapshots`, `image_tags`). The actual OCI images in `ghcr.io/gwshield` are
unaffected — only DB metadata was removed. Final state: 34 active images, 34 version-tags, 0 missing.

---

## [v0.2.0-alpha] — 2026-03-12

### Changed

#### CI pipeline — full stabilisation sprint (`fix(ci)`, `refactor(ci)`, `docs(ci)`)

This release closes the multi-sprint CI stabilisation effort. All 36 images are green, all runners
correctly assigned, no flapping jobs.

**Sprint 1 — Bug fixes (`aa4842a`)**
- `scan.yml` concurrency guard to prevent parallel scan + registry-update races.
- `useblacksmith/*` Actions removed from reusable workflows — replaced with SHA-pinned
  `docker/setup-buildx-action` + `docker/build-push-action` (root cause: Blacksmith runner token
  rejected by GitHub Action-download endpoint for third-party Action tarballs).
- Trivy version pinned; SARIF upload path corrected; `find images -name Dockerfile` depth fixed to
  `-mindepth 3 -maxdepth 4` (was silently dropping all builder images at depth 4).

**Sprint 2+3 — Refactoring (`b79c348`)**
- `ubuntu-latest` → `blacksmith-2vcpu-ubuntu-2404` for 3 additional jobs.
- `scripts/ci/parse-trivy.py` extracted from inline workflow YAML.
- `scripts/ci/discover-targets.sh` extracted from inline workflow YAML.
- `_functional-job.yml` reusable workflow created; `functional.yml` consolidated from per-family
  duplicated jobs to a single parameterised matrix.

**Bugfix sprint — Stability (`d9a9db0` → `81f56fc`)**
- `_functional-job.yml`: `timeout-minutes` hardcoded (expression interpolation not supported at job
  level in reusable workflows); `docker/login-action` SHA-pinned.
- `_functional-job.yml` moved from `.github/workflows/reusable/` to top-level `.github/workflows/`
  — GitHub Actions does not support reusable `workflow_call` files in subdirectories.
- `functional.yml` push-trigger guard job added — GitHub generates a push run when any workflow file
  changes; without an unconditional job the run fails as "0 jobs / workflow file issue".
- `haproxy.sh` + `haproxy-ssl.sh`: SIGPIPE fix — `echo "$VAR" | grep -q` under `set -euo pipefail`
  causes broken-pipe; replaced with herestring `grep -q "pattern" <<< "$VAR"`.
- `haproxy-ssl/configs/haproxy.cfg`: `maxconn` reduced from 50000 → 4096 (50000×2 FDs exceeds CI
  runner FD limit of 65536).
- AGENTS.md + CLAUDE.md updated with 4 new CI discoveries (subdirectory constraint,
  `timeout-minutes` interpolation, push-trigger guard pattern, herestring vs pipe).
- Pipeline architecture docs (`.vault/claude/PIPELINE_ARCHITECTURE.md` + `_EN.md`) fully rewritten
  across 17 sections.

**Runner policy (final state)**
- `blacksmith-8vcpu-ubuntu-2404`: all Docker build jobs.
- `blacksmith-2vcpu-ubuntu-2404`: all other jobs in `RelicFrog/gwshield-images`.
- `ubuntu-latest`: `discover-ci` / `discover-scan-targets` (lightweight, no Docker) + all jobs in
  `gwshield/images` (Blacksmith not installed in that org — permanent documented exception).

---

## [v0.1.9-alpha] — 2026-03-12

### Added

#### Supabase `image_type` propagation — insert-only semantics (`feat(supabase)`)
- **Hub migration 0033** — `images.image_type TEXT NOT NULL DEFAULT 'service' CHECK (image_type IN
  ('service','builder','tooling'))` — partial indexes on `builder` and `tooling` variants.
- **`supabase_ingress.py`** — `--image-type` CLI parameter on `promote` subcommand (default `'service'`,
  allowed: `service|builder|tooling`, exits non-zero on invalid value).
  - `_VALID_IMAGE_TYPES` constant — matches DB CHECK constraint.
  - `derive_image_type(name, profile)` — auto-detects type from image name/profile.
  - `resolve_image_type(cli_arg, name, profile)` — CLI arg takes priority over auto-detect.
  - `upsert_image()` — SELECT-first, then INSERT (with `image_type`) or UPDATE (without `image_type`);
    admin Hub override survives every subsequent promote run.
- **`release-public.yml`** — `emit_entry()` shell function derives `image_type` from path + profile:
  `images/builders/**` → `builder`; profile `cli` → `tooling`; else → `service`; field added to
  dispatch payload.
- **`promote.yml`** (gwshield/images) — `--image-type "${{ github.event.client_payload.image_type }}"`
  passed to `supabase_ingress.py`.
- **Hub migration 0032** (`images.title_override`, `images.featured_promo_text`) — admin-only fields;
  pipeline never sets or overwrites these.
- Full re-promote of all 36 images triggered to backfill `image_type` in Supabase (2026-03-12).

### Fixed

#### CI pipeline stability — promote.yml (`fix(ci)`)
- **`sigstore/cosign-installer@v3` replaced** with direct `curl` download of cosign v3.0.5 binary
  (SHA256-verified). The `sigstore/cosign-installer` Action caused intermittent `401 Unauthorized`
  during `Set up job` phase on Blacksmith runners — same root cause as the `useblacksmith/*`
  failures fixed in v0.1.8-alpha.
- **`cosign attest` — `continue-on-error: true`** added to SBOM attestation step. Root cause:
  cosign v3 `--replace` reads all existing attestation bundles from the registry before writing;
  bundles created by an earlier cosign version are not valid JSON for cosign v3's envelope parser,
  causing `invalid attestation: decoding json`. On re-promotes (same digest), the SBOM already
  exists and the error is non-fatal. `--replace` flag removed to avoid the fetch.

#### CI pipeline stability — build.yml (`fix(ci)`)
- **`useblacksmith/setup-docker-builder@v1` + `useblacksmith/build-push-action@v2` replaced** with
  SHA-pinned `docker/setup-buildx-action@4d04d5d` (v4.0.0) + `docker/build-push-action@10e90e36`
  (v6.19.2). Root cause: Blacksmith runner token is rejected by GitHub's Action-download endpoint
  for third-party Action tarballs, causing intermittent `401 Unauthorized` on `Set up job`.
  Blacksmith _runners_ are still used — only the Action steps changed.

#### Functional test fixes — haproxy (`fix(tests)`)
- **`haproxy.cfg` `maxconn 50000`** reduced to `4096` — HAProxy requires `maxconn×2` FDs;
  50000 × 2 = 100031 exceeds the CI runner FD limit of 65536, causing immediate container exit.
- **`haproxy.sh` broken pipe** — `$(echo "$METRICS" | head -3)` under `set -o pipefail` causes
  broken-pipe error; fixed by capturing output first, then `{ head -n 3 || true; }`.
- **`haproxy-ssl.sh` broken pipe + HSTS pipe** — same pattern applied; HSTS curl piped to grep
  also fixed.

### Changed

#### Supabase service role key rotation (`chore(infra)`)
- `SUPABASE_SERVICE_ROLE_KEY` rotated from JWT format (`eyJ...`) to `sb_secret_...` format
  in both `RelicFrog/gwshield-images` and `gwshield/images`.

---

## [v0.1.8-alpha] — 2026-03-12

### Added

#### Go builder v1.25 + v1.25-dev (`feat(builders)`)
- **`images/builders/go-builder/v1.25/Dockerfile`** — hardened compile-only builder image
  on `golang:1.25.8-alpine3.22` (digest-pinned). `CGO_ENABLED=0`, `GOFLAGS=-trimpath`,
  `HISTFILE=/dev/null`, nonroot UID/GID 65532. Identical structure to v1.24.
- **`images/builders/go-builder/v1.25-dev/Dockerfile`** — dev profile extending v1.25 with:
  - `golangci-lint v2.11.3` (updated from v2.11.2 in v1.24-dev)
  - `gofumpt v0.9.2`
  - `goimports` (latest from golang.org/x/tools)
  - `govulncheck v1.1.4`
  - `staticcheck 2026.1` (updated from 2025.1.1 — **requires Go >= 1.25**)
- **Smoke tests**: 7 tests (compile-only) / 12 tests (dev) — same pattern as v1.24
- **Functional tests**: reuse `go-builder.sh` + `go-builder-dev.sh` with v1.25 image tags
- **`functional.yml`**: 2 new matrix entries (`go-builder:v1.25`, `go-builder:v1.25-dev`)
- **CVE scan**: 0 CRITICAL, 0 HIGH — promoted to `ghcr.io/gwshield`

> **Note:** `v1.25-dev` builds after `v1.25` is promoted — the `BASE_DIGEST` in the
> Dockerfile is updated to the live digest after the first promote run.

---

## [v0.1.7-alpha] — 2026-03-11

### Added

#### Caddy v2.11.2 — 5 plugin profiles (`feat(caddy)`)
- **`images/caddy/v2.11.2-cloudflare/Dockerfile`** — xcaddy v0.4.5 build with
  `caddy-dns/cloudflare@v0.2.3` (DNS-01 ACME for wildcard certs behind Cloudflare).
  `CF_API_TOKEN` env var required at runtime.
- **`images/caddy/v2.11.2-crowdsec/Dockerfile`** — xcaddy build with
  `caddy-crowdsec-bouncer/http@v0.10.0` + `/layer4@v0.10.0` (CrowdSec IP bouncer;
  both sub-packages required for full HTTP + Layer-4 coverage).
- **`images/caddy/v2.11.2-security/Dockerfile`** — xcaddy build with
  `caddy-security@v1.1.45` (OIDC/JWT/OAuth2 auth middleware; ~120 transitive deps —
  re-scan on every plugin version bump).
- **`images/caddy/v2.11.2-ratelimit/Dockerfile`** — xcaddy build with
  `caddy-ratelimit@v0.1.0` (native in-process rate limiting).
- **`images/caddy/v2.11.2-l4/Dockerfile`** — xcaddy build with `caddy-l4@master`
  (Layer-4 / gRPC routing; no versioned releases — pinned to `master`, use commit SHA
  in production).
- All profiles: 4-stage Dockerfile (`deps` → `banner` → `builder` → `scratch`),
  `gwshield-init` banner, 11-test `smoke.sh`, 7-test functional test, 0 CVEs.
- All plugin binaries: `CGO_ENABLED=0` → fully static (zero `NEEDED` entries verified
  via `readelf -d`).
- **xcaddy SHA-512 verified** (`linux_amd64` + `linux_arm64` per `TARGETARCH`) — arch-aware
  download prevents "Invalid ELF image" failure on arm64 QEMU cross-builds.
- **`tests/functional/`** — `caddy-cloudflare.sh`, `caddy-crowdsec.sh`,
  `caddy-security.sh`, `caddy-ratelimit.sh`, `caddy-l4.sh` added (7 tests each).
- **`functional.yml`** — 5 new jobs; `image_group` filter extended.
- **CVE scan**: all 5 profiles — 0 CRITICAL, 0 HIGH; promoted to `ghcr.io/gwshield`.

### Fixed

#### Caddy plugin profiles — xcaddy arm64 cross-build (`fix(caddy)`)
- xcaddy is a host-native tool binary. Downloading `linux_amd64` and running it under
  QEMU on an `arm64` builder stage fails with "Invalid ELF image for this architecture".
  Fixed by using `ARG TARGETARCH` + `case` statement to select the correct
  `linux_amd64` / `linux_arm64` tarball and its SHA-512 checksum in all 5 plugin
  Dockerfiles.

---

## [v0.1.6-alpha] — 2026-03-11

### Added

#### Caddy v2.11.2 — standard profile (`feat(caddy)`)
- **`images/caddy/v2.11.2/Dockerfile`** — multi-stage build: `golang:1.26.1-alpine3.22` builder
  → `FROM scratch` runtime. `CGO_ENABLED=0` produces a fully static binary with zero dynamic
  dependencies (verified via `readelf -d`).
- **CVE mitigation**: upstream `caddy:2-alpine` (Go 1.26.0) carried 1 CRITICAL (`zlib
  CVE-2026-22184`) and 3 HIGH Go stdlib CVEs (`CVE-2026-25679`, `CVE-2026-27137`,
  `CVE-2026-27142`). Rebuilding with Go 1.26.1 on `FROM scratch` eliminates all four.
- **`configs/Caddyfile`** — automatic HTTPS disabled; HTTP listener on `:8080`; `/healthz`
  returns 200 OK; admin API on `localhost:2019` (healthcheck only, not externally exposed).
- `/data` (`XDG_DATA_HOME`) and `/config` (`XDG_CONFIG_HOME`) pre-created with UID 65532
  ownership for ACME certificate storage and config cache.
- **`tests/smoke.sh`** — 10 tests: binary, version, config validate, non-root, no-shell, fully
  static (zero NEEDED), CA certs, Caddyfile, /data, /config.
- **`tests/functional/caddy.sh`** — 7 functional tests via Docker network + alpine/curl: /healthz
  200, body OK, 404 for unknown paths, non-root, no version leak in Server header, version string.
- **`functional.yml`** — `functional-caddy` job added; `caddy` image_group filter added.
- **CVE scan**: 0 CRITICAL, 0 HIGH — hard gate passes; image promoted to `ghcr.io/gwshield/caddy:v2.11.2`.

---

## [v0.1.5-alpha] — 2026-03-11

### Added

#### HAProxy v3.1.16 — standard profile (`feat(haproxy)`)
- **`images/haproxy/v3.1.16/Dockerfile`** — Alpine 3.22 builder → FROM scratch runtime;
  static OpenSSL, PCRE2 (JIT), zlib; `USE_PROMEX=1` (Prometheus `/metrics` on `:9101`);
  no Lua (reduced attack surface); only musl libc as shared dependency.
- **musl dynamic loader** copied from builder to `/lib/` in scratch runtime (same pattern
  as Redis/nginx); required for HAProxy binary execution.
- **`configs/haproxy.cfg`** — minimal HTTP frontend (:8080), `/healthz` ACL, stats socket,
  Prometheus metrics frontend (:9101); HAProxy 3.x quirks handled:
  `nbthread` omitted (auto-detect), `master-worker` in CLI (`-W`), `ulimit-n` removed (nonroot).
- **`tests/smoke.sh`** — 8 tests; config syntax check uses exit-code (not string grep —
  HAProxy 3.x no longer prints "Configuration file is valid").
- **`tests/functional/haproxy.sh`** — 7 functional tests via Docker network + alpine/curl sidecar.
- **`functional.yml`** — haproxy job added; `image_group` filter updated.
- **CVE scan**: 0 CRITICAL, 0 HIGH — hard gate passes; image promoted to `ghcr.io/gwshield/haproxy:v3.1.16`.

#### HAProxy v3.1.16-ssl — TLS profile (`feat(haproxy)`)
- **`images/haproxy/v3.1.16-ssl/Dockerfile`** — identical binary to standard; SSL activated at
  config level. `bind *:8443 ssl crt /etc/haproxy/certs/server.pem alpn h2,http/1.1`.
- **`configs/haproxy.cfg`** — HTTP :8080 redirects to HTTPS (301), `/healthz` bypasses redirect;
  HTTPS :8443 terminates TLS; HSTS `max-age=63072000; includeSubDomains; preload`;
  `ssl-min-ver TLSv1.2`; ECDHE+AEAD cipher suites; no deprecated `no-sslv3`/`no-tlsv1x` options.
- `maxconn 32000` — within default container FD limit (65536).
- **`tests/smoke.sh`** — 10 tests; self-signed cert generated for TLS startup test and config check.
- **`tests/functional/haproxy-ssl.sh`** — 7 tests (HTTPS 200, HTTP→HTTPS 301, HSTS, Prometheus, UID).
- **`functional.yml`** — haproxy-ssl job added; `haproxy-ssl` image_group filter added.
- **CVE scan**: 0 CRITICAL, 0 HIGH; promoted to `ghcr.io/gwshield/haproxy:v3.1.16-ssl`.

### Fixed
- `fix(haproxy)`: Dockerfile `COPY configs/haproxy.cfg` path corrected to repo-root-relative
  `images/haproxy/v3.1.16/configs/haproxy.cfg` (build context is repo root).

---

## [v0.1.4-alpha] — 2026-03-11

### Added

#### Structured CVE findings persistence (`feat(supabase)`)
- **`cve_findings` table** (hub migration 0029) — stores per-CVE findings per `image_version_id`;
  unique on `(image_version_id, cve_id)`; fields: `cve_id`, `severity`, `package_name`,
  `package_version`, `fixed_version`, `description`, `layer`, `component`, `mitigation_type`,
  `mitigation_detail`; RLS: public read for public images, service role write.
- **`supabase_ingress.py` — `findings` subcommand** (new, stdlib-only) — parses raw Trivy JSON;
  DiffID-based layer classification (`base_image` | `builder_stage`); component taxonomy
  (`alpine-pkg`, `debian-pkg`, `rust-crate`, `go-module`, `python-pkg`, `npm-pkg`, `other`);
  `mitigation_type` derived from `FixedVersion` presence (`pkg_upgrade` / `not_applicable`);
  upsert on `(image_version_id, cve_id)` — fully idempotent.
- **`promote.yml`** (gwshield/images) — new "Write CVE findings to Supabase" step after
  `registry.json` update; passes Trivy output as `--findings-json`; `continue-on-error: true`.
- **`scan.yml`** (RelicFrog/gwshield-images) — `update-public-registry` job extended to pass
  `--findings-json @trivy-scan.json` on every weekly re-scan; findings stay current.
- **`cve-rescan-origin.yml`** (RelicFrog/gwshield-images) — new backfill + weekly rescan
  pipeline; reads `registry.json` from `gwshield/images`, pulls each image by digest, runs
  Trivy at full severity (`CRITICAL,HIGH,MEDIUM,LOW`), writes structured findings; `max-parallel: 4`;
  `continue-on-error: true` per job; weekly schedule Sunday 05:00 UTC; manual dispatch with
  `image_filter` input.
- **Backfill complete** (2026-03-11): 27/27 images rescanned → **132 rows** written to
  `cve_findings`; breakdown: HIGH 12, MEDIUM 23, LOW 97; all `layer=base_image`; 0 CRITICAL
  (hard gate holds); `debian-pkg` dominant (120/132) from distroless PostgreSQL base.

#### gwshield-hub — community catalog live (`feat(hub)`)
- **`hub.gwshield.io`** launched — Next.js 16 + Supabase + GitHub OAuth + Netlify; Phases A–D
  complete as of 2026-03-10. Companion repo: `520-app-gwshield-hub-public`.
- All 23 pipeline images visible in the public catalog (`/images`); data sourced via
  `supabase_ingress.py` after every promote and scan run.
- **Image request system** live at `/requests` — community can submit, vote, and comment on
  image targets; admin moderation queue at `/admin/requests`; `priority_score` Postgres trigger.
- **Changelog page** (`/changelog`) — promotion timeline sourced from `promotion_runs` table.
- **Admin area** — request moderation, featured-image toggle, immutable audit log;
  role-gated by `app_metadata.role` in Supabase Auth JWT.
- **Supabase schema** — migrations 0001–0029 applied; pipeline-relevant additions:
  `cosign_identity`, `base_version`, `profile` on `image_versions`; `scan_status`, `scanner`
  on `image_metadata_snapshots`; `cve_findings` table (migration 0029).

#### Supabase writeback — fully operational (`feat(supabase)`)
- `supabase_ingress.py` (stdlib-only) in `gwshield/images/scripts/` — `promote`, `scan`, and
  `findings` subcommands; idempotent upsert; slug derivation matches hub seed catalog.
- All 23 image/version/snapshot/findings records confirmed written.

#### Pipeline hardening (`fix(ci)`)
- `release-public.yml` — dispatch-verify step polls 4×15s for confirmed `promote` run start;
  fails after 60s if no run detected (catches silent `gwshield-builder` App permission gaps).
- `ci.yml` — workflow YAML syntax validation via `yaml.safe_load()` on all `*.yml` files.
- `functional.yml` — 3× retry with 10s backoff on all `docker pull` steps.
- `gwshield-builder` App — `actions:write` permission added (required for
  `repository_dispatch` to trigger workflows in `gwshield/images`).

#### Runner migration — all workflows on Blacksmith (`ci(workflows)`)
- **`ubuntu-latest` eliminated** from all 6 workflows in `RelicFrog/gwshield-images`.
- GitHub Free minutes no longer consumed by any CI run.

#### Functional test fixes (`fix(tests)`)
- `nginx.sh` — `fastcgi_temp_path` directive removed from test nginx config.
- `python-builder-dev.sh` — `setuptools.build_meta` backend; `EXPECTED_MINOR` unused var removed.
- `go-builder-dev.sh` — golangci-lint assertion corrected (no false positive on file:line:col).
- `postgres.sh` — `max-parallel` reduced to 2 (OOM guard for initdb in constrained CI).

#### Rust builder images (`feat(builders)`)
- **Rust builder v1.87 (compile-only)** (`images/builders/rust-builder/v1.87/`) —
  based on `rust:1.87.0-alpine3.22` (digest-pinned), nonroot UID 65532, `CARGO_HOME` owned
  by nonroot, `x86_64-unknown-linux-musl` target pre-installed alongside the default
  `aarch64-unknown-linux-musl`, `RUSTFLAGS="-C target-feature=+crt-static"` produces fully
  static musl binaries; 0 CVEs (after targeted `apk upgrade`); smoke tested; published to
  `ghcr.io/gwshield/rust-builder:v1.87`.
- **Rust builder v1.87-dev** (`images/builders/rust-builder/v1.87-dev/`) — extends v1.87 with
  `clippy` and `rustfmt` (rustup components) plus `cargo-audit v0.21.2` and `cargo-deny v0.18.2`
  (compiled from source via `cargo install --locked`); 0 CVEs; smoke tested; published to
  `ghcr.io/gwshield/rust-builder:v1.87-dev`.
- **Rust functional tests** — `tests/functional/rust-builder.sh` and `rust-builder-dev.sh` covering
  static binary compilation, musl target verification, clippy, rustfmt, cargo-audit, cargo-deny;
  `tests/functional/fixtures/rust-app/` (Cargo.toml + deny.toml + src/main.rs + src/lib.rs);
  `functional.yml` matrix entries added for the `rust` image group.

### Fixed

#### CVE remediation — Rust v1.87 base (`fix(builders)`)
- `rust:1.87.0-alpine3.22` shipped with outdated Alpine packages containing 8 HIGH/CRITICAL CVEs:
  - `binutils 2.44-r0` → `2.44-r3`: CVE-2025-5244, CVE-2025-5245 (HIGH)
  - `libcrypto3`/`libssl3 3.5.0-r0` → `3.5.5-r0`: CVE-2025-15467 (CRITICAL),
    CVE-2025-69419, CVE-2025-69421 (HIGH)
- Fixed via targeted `apk upgrade --no-cache binutils libssl3 libcrypto3` in the builder stage.
  Allowlist entries document the remediation; to be removed when upstream Rust base image ships
  the fixed packages.

#### Smoke test — v1.87 cargo build test (`fix(tests)`)
- Replaced `docker create` + `docker start` + `docker cp` pattern with a single `docker run --rm`
  that performs the full build, binary execution, and `readelf` static check inside the container.
  The original approach failed because `RUSTFLAGS` inside a quoted `sh -c` string was not seen
  by cargo; moving to `-e RUSTFLAGS=...` env var and eliminating the docker cp step resolved the
  failure. Pattern now mirrors the working `v1.87-dev` smoke test approach.

---

## [v0.1.3-alpha] — 2026-03-08

### Added

#### Builder images — Go + Python (`feat(builders)`)
- **Go builder v1.24 (compile-only)** (`images/builders/go-builder/v1.24/`) — Alpine 3.22 base,
  `CGO_ENABLED=0`, `-trimpath`, `GOFLAGS`, nonroot UID 65532; smoke tested; 0 CVEs; published
  to `ghcr.io/gwshield/go-builder:v1.24`.
- **Go builder v1.24-dev** (`images/builders/go-builder/v1.24-dev/`) — extends v1.24 with full
  dev tooling: golangci-lint v2.11.2, gofumpt v0.9.2, goimports, govulncheck v1.1.4,
  staticcheck 2025.1.1; installed via official binary releases / `go install`; smoke tested;
  0 CVEs; published to `ghcr.io/gwshield/go-builder:v1.24-dev`.
- **Python builder v3.12 + v3.13 (compile-only)** (`images/builders/python-builder/v3.12/`,
  `v3.13/`) — Alpine base, UV + pip, nonroot UID 65532; smoke tested; 0 CVEs.
- **Python builder v3.12-dev + v3.13-dev** — extends compile-only with: ruff, mypy, pytest,
  pip-audit, black, isort; smoke tested; 0 CVEs; published to `ghcr.io/gwshield`.

#### PostgreSQL v17.9 — full profile stack (`feat(images)`)
- **PostgreSQL v17.9 (standard, tls, cli, vector, timescale)** (`images/postgres/v17.9*/`) —
  full port of the v15.17 profile stack to PostgreSQL 17.9. New build requirements for PG17:
  `bison`, `flex`, and `perl` (for `Gen_fmgrtab.pl`, `gen_node_support.pl`, `genbki.pl`);
  SHA-256 verified source tarball; distroless/cc-debian12 runtime; 0 CVEs on all 5 profiles.
  Extensions: pg_partman v5.4.3, pg_cron v1.6.7, pgvector v0.8.2, TimescaleDB v2.25.2.
  All 5 profiles published to `ghcr.io/gwshield/postgres:v17.9[-profile]`.

#### Functional test suite (`feat(tests)`)
- **`tests/functional/`** — Level 1 functional tests for every image group; test real
  operational behaviour beyond the existing smoke tests (container lifecycle + minimal function):
  - `go-builder.sh` — multi-package compile, `go test`, static binary extraction + `file(1)` check
  - `go-builder-dev.sh` — golangci-lint, gofumpt, govulncheck, staticcheck, goimports on fixture
  - `python-builder.sh` — `pip install`, module execution, output verification
  - `python-builder-dev.sh` — ruff, mypy, pytest, black, pip-audit on fixture
  - `postgres.sh` — initdb, `pg_isready`, `CREATE TABLE` + `INSERT` + `SELECT` round-trip,
    extension-load check (profile-specific: vector, timescale, cli)
  - `redis.sh` — PING, `SET`/`GET`, TTL, `INFO server`, cluster-enabled check
  - `nginx.sh` — HTTP 200 on `/healthz`, static file content, `server_tokens off` header check
  - `traefik.sh` — `/ping` 200, API `/api/rawdata`, web entrypoint, `/api/version` JSON
- **`tests/functional/fixtures/`** — shared Go (`go-app/`) and Python (`python-app/`) fixture
  packages used by builder functional tests.
- **`.github/workflows/functional.yml`** — daily cron at 03:00 UTC against published
  `ghcr.io/gwshield` images; manual dispatch with `image_group` filter
  (`all | builders | postgres | redis | nginx | traefik`); `fail-fast: false` matrix.

#### Public README improvements (`feat(readme)`)
- **Version column** added to all image tables in `gwshield/images` README (rendered by
  `generate-readme.py`); makes the software version explicit alongside the full image tag.
- **WIP / early-access banner** added to the header section — announces alpha status,
  upcoming gwshield.io landing page, MCP server, and extended tooling.

### Fixed

#### CI lint (`fix(images)`)
- `go-builder/v1.24-dev/Dockerfile` — `# hadolint ignore=DL3002` before `USER 0` in
  `tool-installer` stage; `# hadolint ignore=DL3062` before `RUN` block that uses
  `go install goimports@latest` (no standalone release tag for `golang.org/x/tools`).
- `python-builder/v3.12-dev/Dockerfile` and `python-builder/v3.13-dev/Dockerfile` —
  `# hadolint ignore=DL3002` before `USER 0` in `tool-installer` stage.

#### Smoke tests — distroless-safe `.so` checks (`fix(images)`)
- `images/postgres/v17.9-vector/tests/smoke.sh` — replaced `docker run --entrypoint /bin/ls`
  (unavailable in distroless) with `_file_in_image` helper (`docker create` + `cp`);
  added Tests 6 + 7 for `pg_partman.control` and `pg_cron.so` presence (aligned with v15.17-vector).
- `images/postgres/v17.9-timescale/tests/smoke.sh` — same fix + added `_file_pattern_in_image`
  helper for `timescaledb-tsl` versioned filename; aligned 11-test suite with v15.17-timescale.

---

## [v0.1.2-alpha] — 2026-03-08

### Added

#### Cross-org public promotion pipeline (`feat(ci)`)
- **`release-public.yml`** refactored from direct promote to `repository_dispatch` fan-out:
  dispatches per-image promote events to `gwshield/images`; no credentials flow in the payload;
  `gwshield/images` generates its own tokens per job.
- **`gwshield/images` promote workflow** (`gwshield/images/.github/workflows/promote.yml`):
  receives `promote-image` dispatch; runs skopeo copy, cosign keyless sign, syft SBOM attestation;
  writes `registry.json` entry; triggers `readme-update` dispatch.
- **GitHub App `gwshield-builder`** (App ID `3032134`): installed in both `relicfrog` and
  `gwshield` orgs; permissions: `packages:write`, `contents:write`, `members:read`, `metadata:read`;
  used for cross-org dispatch auth only — src/dst image operations use `GITHUB_TOKEN` and
  `RELICFROG_READ_PAT` respectively.
- **`RELICFROG_READ_PAT`** (classic PAT, `read:packages` only): stored in `gwshield/images`;
  sole mechanism that works for cross-org GHCR src pull — fine-grained PATs and App tokens are
  denied by GHCR for org-owned packages. Expires ~2027-03, calendar reminder set.
- **`ghcr-cleanup.yml`** — weekly orphaned manifest pruning (Sunday 03:00 UTC); auto-discovery
  of all gwshield GHCR packages; dry-run mode; no extra PAT needed.

#### registry.json processing engine (`feat(registry)`)
- **`gwshield/images/scripts/update-registry.py`** — single source of truth for all public image
  metadata; `promote` subcommand (upsert after each promote), `scan` subcommand (CVE status update
  after each trivy run); idempotent upsert keyed by `name:version`; schema version `"1"`.
- **`registry.json`** (in `gwshield/images`) — auto-generated, never edited manually; fields per
  image entry: `name`, `version`, `base_version`, `profile`, `public_image`, `tags`, `digest`,
  `cosign_identity`, `promoted_at`, `scan.{status,total,critical,high,scanner,scanned_at}`.
- **`gwshield/images/scripts/generate-readme.py`** — renders `README.md` from `registry.json`;
  groups images by service; per-image table with tag, profile, short digest, CVE status, promote
  date; `cosign verify` section per image; graceful placeholder if `registry.json` missing.
- **`gwshield/images/.github/workflows/readme-update.yml`** — triggered by `registry-updated`
  repository_dispatch (from promote and scan jobs) and manual dispatch; pulls latest commits after
  checkout (race-condition guard); regenerates README; commits `[skip ci]`; concurrency-queued
  (never drops updates).

#### scan.yml — public registry CVE status sync (`feat(ci)`)
- New `update-public-registry` matrix job after `trivy-scan`: downloads per-image scan artifact,
  parses CVE counts (total, critical, high), dispatches `registry-updated` event to
  `gwshield/images` with CVE payload; uses App token for gwshield dispatch auth.

#### PostgreSQL v15.17 — two new flavor profiles (`feat(postgres)`)
- **vector** (`images/postgres/v15.17-vector/`) — PostgreSQL 15.17 + pgvector v0.8.2 +
  pg_partman v5.4.2 + pg_cron v1.6.7; pgvector compiled via `USE_PGXS=1`, produces `vector.so`;
  activated per-DB via `CREATE EXTENSION vector;` (no `shared_preload_libraries` entry needed);
  adds VECTOR data type, IVFFlat and HNSW index types; same distroless/cc-debian12 runtime.
- **timescale** (`images/postgres/v15.17-timescale/`) — PostgreSQL 15.17 + TimescaleDB v2.25.1 +
  pg_partman v5.4.2 + pg_cron v1.6.7; TimescaleDB built via CMake (`-DCMAKE_BUILD_TYPE=Release`,
  `-DREGRESS_CHECKS=OFF`); installs `timescaledb.so` + `timescaledb-tsl.so`; MUST be first in
  `shared_preload_libraries`; `timescaledb.telemetry_level = off`; TSL license noted in
  `docs/risk-statement.md`.
- Both profiles inherit pg_partman + pg_cron from standard profile.

### Changed

#### PostgreSQL v15.17 standard profile — extensions added (`feat(postgres)`)
- Added pg_partman v5.4.2 and pg_cron v1.6.7 to the v15.17 standard profile; two new builder
  stages (`ext-partman`, `ext-cron`); `shared_preload_libraries = 'pg_cron,pg_partman_bgw'`.

#### PostgreSQL v15.13 → v15.17 patch update (`chore(postgres)`)
- Bumped source tarball from 15.13 to 15.17; updated SHA256 pin; renamed image directories.

### Removed

#### `release.yml` retired (`chore(ci)`)
- Removed `.github/workflows/release.yml` — traefik-only, old naming convention, superseded by
  the cross-org `release-public.yml` + `gwshield/images/promote.yml` architecture.

### Security

#### App visibility review (`docs(security)`)
- `gwshield-builder` App cannot be set private (GitHub constraint: app installed on multiple orgs).
- Confirmed non-issue: installation tokens are scoped per-org — external installations have zero
  access to `relicfrog` or `gwshield` resources.
- Documented in `.vault/claude/CROSS_ORG_CI_ARCHITECTURE.md`.

---

## [v0.1.1-alpha] — 2026-03-01

### Added

#### Redis v7.4.8 — three hardened profiles (`feat(redis)`)
- **standard** (`images/redis/v7.4.8/`) — Redis built from source with `DISABLE_SCRIPTING=yes`;
  `libm` statically linked via `LDFLAGS="-Wl,-Bstatic -lm -Wl,-Bdynamic"`; FROM scratch runtime;
  dangerous commands renamed in `redis.conf`; `protected-mode no` for container deployments.
- **TLS** (`images/redis/v7.4.8-tls/`) — OpenSSL statically linked via `LIBSSL_LIBS` and
  `LIBCRYPTO_LIBS` make variables (not `LDFLAGS`); TLS-only listener on port 6380; plain port
  disabled; self-signed cert and key included for smoke tests.
- **cluster-mode** (`images/redis/v7.4.8-cluster/`) — same binary as standard; cluster mode
  is a config-level feature enabled via `cluster-enabled yes` and
  `cluster-config-file /data/nodes.conf`; smoke test verifies `redis_mode:cluster` via
  `INFO server`.
- All three profiles: FROM scratch runtime, UID/GID 65532, musl loader verification step in
  builder, docker-network smoke tests, `scan/allowlist.yaml`, `docs/` risk statement and
  mitigation summary.

#### nginx v1.28.2 — three hardened profiles (`feat(nginx)`)
- **http** (`images/nginx/v1.28.2/`) — nginx built from source; pcre2, zlib statically linked;
  FROM scratch runtime; stripped modules list.
- **http2** (`images/nginx/v1.28.2-http2/`) — same as http with `--with-http_v2_module`.
- **http3 / QUIC** (`images/nginx/v1.28.2-http3/`) — built against
  **QuicTLS** (`openssl-3.3.0-quic1`), which is the correct OpenSSL fork for QUIC (BoringSSL
  is incompatible with nginx's `--with-openssl=<path>` pattern); pcre2 and zlib statically
  linked via `--with-ld-opt="-Wl,-Bstatic -lpcre2-8 -lz -Wl,-Bdynamic"`.

#### Shared C/autoconf builder snippet (`feat(shared)`)
- `shared/builders/c-autoconf/Dockerfile.builder` — reusable builder stage template for
  images that compile C sources via autoconf/make.
- `shared/builders/c-autoconf/versions.env.template` — version-pin template for C/autoconf targets.

### Fixed

#### CI — push-event target discovery (`fix(ci)`)
- `build.yml` and `ci.yml`: switched from `origin/main...HEAD` to `HEAD~1..HEAD` for diff-based
  auto-discovery of changed image directories on push events. Prevents missing targets when
  history is shallow-cloned.
- Guard `grep` against exit code 1 when diff produces no image changes (empty matrix).

#### nginx — static linking corrections (`fix(nginx)`)
- Switched http3 from BoringSSL to QuicTLS — BoringSSL has no `./config` script and is
  incompatible with nginx's `--with-openssl=<path>` argument.
- Corrected `--with-ld-opt` for pcre2+zlib static linking — without these flags the FROM scratch
  runtime has no `.so` files and the binary fails to start.
- Resolved `SC2034` shellcheck warnings (unused variables `uid`, `i`) in `smoke.sh`.
- Replaced `cd + clone` pattern with direct `git clone` into `WORKDIR` to satisfy `DL3003`.

#### Build performance — BuildKit cache mounts (`perf(build)`)
- Added `--mount=type=cache,target=/var/cache/apk,id=apk-<name>-<profile>-<stage>` to all
  Alpine `apk add` steps across all images — enables Blacksmith sticky disk cache reuse.

### Changed
- Version bump: `v0.1.0-alpha` → `v0.1.1-alpha`.
- Digest verification dates updated to 2026-03-01 for all targets.
- musl loader grep filter standardised to `'musl'` (matches both `ld-musl-*.so.1` and
  `libc.musl-*.so.1`) across all images.

---

## [v0.1.0-alpha] — 2026-02-28

### Added

#### Traefik v3.6.9 — initial hardened image (`feat(traefik)`)
- Multi-stage Dockerfile: deps stage (Alpine 3.23), builder stage (Go 1.25.7-alpine3.23),
  runtime stage (FROM scratch).
- Binary rebuilt from source with `CGO_ENABLED=0`; verified statically linked via
  `readelf -d`.
- Non-root runtime: UID/GID 65532 (`nonroot`).
- `scan/allowlist.yaml` — confirmed false positive documented (CVE-2026-24051,
  Darwin-only code path, not compiled on linux/amd64).
- `docs/risk-statement.md` and `docs/mitigation-summary.md`.
- Smoke tests: startup, `--help`, non-root assertion, no-shell assertion, `/ping` endpoint.

#### Mono-repo MVP architecture (`feat(arch)`)
- `images/<name>/<version>/` layout — self-contained per image target.
- `shared/base-layers/` — reference Dockerfile patterns (nonroot user, ca-certs, tzdata).
- `.github/workflows/build.yml` — matrix build + push to GHCR + CVE scan + smoke; uses
  Blacksmith (`useblacksmith/setup-docker-builder@v1`, `useblacksmith/build-push-action@v2`);
  auto-discovery via `find images -name Dockerfile`.
- `.github/workflows/ci.yml` — PR/branch lint (hadolint, shellcheck, YAML schema) + local
  build + smoke; auto-discovery via changed file diff.
- `.github/workflows/scan.yml` — weekly scheduled re-scan (Trivy + Grype); opens GitHub
  issue on new findings.
- `.github/workflows/release.yml` — semver tag gate: scan must pass → cosign sign →
  GitHub Release.
- `renovate.json` — automated PRs for Go toolchain, Alpine base image, and service version bumps.
- `Makefile` — local dev shortcuts: `build`, `scan`, `smoke`, `all`, `list`, `pipeline-debug`.

#### Documentation
- `README.md` — project overview, image catalogue, quickstart, security model, CI/CD overview.
- `CONTRIBUTING.md` — per-image contract, Dockerfile conventions, PR checklist.
- `SECURITY.md` — vulnerability reporting policy.
- `STRUCTURE.md` — repository layout and pipeline flow.
- `AGENTS.md` — agent roles, conventions, guardrails.
- `CLAUDE.md` — problem statement, work tracks, non-negotiables.

### Fixed
- SARIF upload removed — requires GitHub Advanced Security licence (not available for private
  repo without licence).
- Lowercase registry org (`relicfrog`) hardcoded — `github.repository_owner` returns
  mixed-case on GHCR pushes.
- `hadolint DL4006` warning resolved in Traefik Dockerfile.
- `shellcheck SC2034` and `SC2155` warnings resolved across smoke scripts.

---

[Unreleased]: https://github.com/RelicFrog/gwshield-images/compare/v0.1.9-alpha...HEAD
[v0.1.9-alpha]: https://github.com/RelicFrog/gwshield-images/compare/v0.1.8-alpha...v0.1.9-alpha
[v0.1.8-alpha]: https://github.com/RelicFrog/gwshield-images/compare/v0.1.7-alpha...v0.1.8-alpha
[v0.1.7-alpha]: https://github.com/RelicFrog/gwshield-images/compare/v0.1.6-alpha...v0.1.7-alpha
[v0.1.6-alpha]: https://github.com/RelicFrog/gwshield-images/compare/v0.1.5-alpha...v0.1.6-alpha
[v0.1.5-alpha]: https://github.com/RelicFrog/gwshield-images/compare/v0.1.4-alpha...v0.1.5-alpha
[v0.1.4-alpha]: https://github.com/RelicFrog/gwshield-images/compare/v0.1.3-alpha...v0.1.4-alpha
[v0.1.3-alpha]: https://github.com/RelicFrog/gwshield-images/compare/v0.1.2-alpha...v0.1.3-alpha
[v0.1.2-alpha]: https://github.com/RelicFrog/gwshield-images/compare/v0.1.1-alpha...v0.1.2-alpha
[v0.1.1-alpha]: https://github.com/RelicFrog/gwshield-images/compare/v0.1.0-alpha...v0.1.1-alpha
[v0.1.0-alpha]: https://github.com/RelicFrog/gwshield-images/releases/tag/v0.1.0-alpha
