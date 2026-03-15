# gwshield-postgres v15.17

**Profile:** standard — single-node server, pg_partman + pg_cron
**Registry:** `ghcr.io/gwshield/postgres:v15.17`
**Scan date:** 2026-03-02 — 0 HIGH / 0 CRITICAL CVEs

---

## Scan delta vs. upstream

| Metric | Upstream `postgres:15.17` (Debian 13) | gwshield-postgres:v15.17 |
|---|---|---|
| HIGH CVEs (OS) | 31 | **0** |
| CRITICAL CVEs (OS) | 4 | **0** |
| HIGH/CRITICAL (gosu) | 41 | **0** |
| Secret findings | 1 (snakeoil key) | **0** |
| Total H/C CVEs | **76** | **0** |
| Image base | debian 13.0 (trixie) | distroless/cc-debian12 |
| Shell present | Yes (`/bin/bash`) | No |
| gosu binary | Yes (Go 1.18.2 — 41 CVEs) | No |
| GnuPG stack | Yes (31+ CVEs) | No |
| perl stack | Yes (multiple CVEs) | No |
| snakeoil key | Yes (baked in) | No |

### Key CVEs eliminated

| CVE / Finding | Severity | Component | Fix |
|---|---|---|---|
| CVE-2025-68973 | HIGH | GnuPG (dirmngr, gnupg, gpg*) | Eliminated — GnuPG not present |
| CVE-2026-24882 | HIGH | GnuPG tpm2daemon | Eliminated — GnuPG not present |
| multiple HIGH | HIGH | perl / libperl | Eliminated — perl not present |
| multiple HIGH | HIGH | curl / libcurl | Eliminated — curl not present |
| multiple HIGH | HIGH | gnutls / libgnutls | Eliminated — gnutls not present |
| 41 CVEs in gosu | HIGH/CRITICAL | gosu (Go 1.18.2 stdlib) | Eliminated — gosu not included |
| snakeoil.key | SECRET | `/etc/ssl/private/` | Eliminated — distroless base |

---

## What was done

### Source compilation

PostgreSQL v15.17 compiled from the PGDG source tarball with hardened flags.
Unnecessary components stripped at compile time:

- `--without-readline` — no libreadline/libedit (no interactive psql in server image)
- `--without-icu` — no ICU locale library; `--locale=C` at `initdb` time
- `--without-openssl` — no TLS in standard profile (see `v15.17-tls`)
- `--disable-rpath` — no embedded rpath in binaries
- `zlib` statically linked: `-Wl,-Bstatic -lz -Wl,-Bdynamic`

### Extensions

| Extension | Version | Purpose |
|---|---|---|
| pg_partman | 5.4.2 | Partition management (pure SQL + optional BGW) |
| pg_cron | 1.6.7 | In-database job scheduler (preloaded) |

### Runtime base: distroless/cc-debian12

`gcr.io/distroless/cc-debian12` — glibc + libgcc only. No shell, no package manager,
no snakeoil key.

### gosu eliminated

Non-root execution via `USER 65532:65532`.

### Non-root execution

Runs as UID/GID **65532** (`nonroot`).

---

## Source pins

| Component | Version | SHA256 / Digest |
|---|---|---|
| PostgreSQL source | 15.17 | `f7fc926ea77ffc52e9d6fd58276427e3fe14d35fd9ff3ccf724ca88a28bcb4df` |
| pg_partman | 5.4.2 | — |
| pg_cron | 1.6.7 | — |
| debian:12-slim (builder) | 12-slim | `sha256:74d56e3931e0d5a1dd51f8c8a2466d21de84a271cd3b5a733b803aa91abf4421` |
| distroless/cc-debian12 | — | `sha256:329e54034ce498f9c6b345044e8f530c6691f99e94a92446f68c0adf9baa8464` |
| Build date | 2026-03-02 | — |

---

## Delta summary

| Dimension | Upstream (postgres:15.17) | gwshield-postgres:v15.17 |
|---|---|---|
| Runtime base | Debian 13 (trixie) | **distroless/cc-debian12** |
| Shell | yes | **no** |
| gosu | yes (41 CVEs) | **no** |
| GnuPG / perl / curl | yes | **no** |
| snakeoil key | yes (baked in) | **no** |
| HIGH CVEs | 31 | **0** |
| CRITICAL CVEs | 45 | **0** |
| Non-root UID | not enforced | **65532** |
| TLS | snakeoil (baked) | **no TLS** (see v15.17-tls) |
