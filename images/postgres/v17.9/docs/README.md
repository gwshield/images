# gwshield-postgres v17.9

**Profile:** standard — single-node server, pg_partman + pg_cron
**Registry:** `ghcr.io/gwshield/postgres:v17.9`
**Scan date:** 2026-03-08 — 0 unfixed HIGH / 0 CRITICAL CVEs

---

## Scan delta vs. upstream

| Metric | Upstream `postgres:17` (Debian bookworm) | gwshield-postgres:v17.9 |
|---|---|---|
| HIGH CVEs (OS) | many | **0 unfixed** |
| CRITICAL CVEs | varies | **0** |
| gosu CVEs | 41 | **0** |
| Image base | debian bookworm (full) | distroless/cc-debian12 |
| Shell present | Yes (`/bin/bash`) | No |
| gosu binary | Yes (multiple CVEs) | No |
| GnuPG / perl / curl | Yes | No |
| snakeoil key | Yes (baked in) | No |

### Accepted finding

**CVE-2026-0861** (HIGH, glibc/libc6) — no Debian bookworm fix available. glibc is a
transitive dependency of `distroless/cc-debian12`. PostgreSQL in this profile uses
`--without-icu` and `locale=C`; the vulnerable code path is not reachable from
network-facing input.

Compensating controls: non-root UID 65532, no shell, scram-sha-256 auth,
read-only root filesystem. Review date: **2026-09-08**.

---

## What was done

### Source compilation

PostgreSQL v17.9 compiled from the PGDG source tarball. PG17 requires additional
build-time packages not needed for PG15: `bison`, `flex`, `perl` (used by
`Gen_fmgrtab.pl`, `gen_node_support.pl`, `genbki.pl` in the PG17 build system).

Same hardening flags and `--without-*` stripping as v15.17:
- `--without-readline`, `--without-icu`, `--without-openssl` (standard profile)
- `--disable-rpath`, `zlib` statically linked

### Extensions

| Extension | Version | Purpose |
|---|---|---|
| pg_partman | 5.4.3 | Partition management (fixes control file version bug from v5.4.2) |
| pg_cron | 1.6.7 | In-database job scheduler |

### Runtime base: distroless/cc-debian12

Same as v15.17 — glibc + libgcc only. No shell, no package manager, no snakeoil key.

### Non-root execution

Runs as UID/GID **65532** (`nonroot`).

---

## Source pins

| Component | Version | SHA256 / Digest |
|---|---|---|
| PostgreSQL source | 17.9 | `70eaebacf5344a0951075a666369d95d25ae4485ad0d6d3df652065277f4943c` |
| pg_partman | 5.4.3 | — |
| pg_cron | 1.6.7 | — |
| debian:12-slim (builder) | 12-slim | `sha256:74d56e3931e0d5a1dd51f8c8a2466d21de84a271cd3b5a733b803aa91abf4421` |
| distroless/cc-debian12 | — | `sha256:329e54034ce498f9c6b345044e8f530c6691f99e94a92446f68c0adf9baa8464` |
| Build date | 2026-03-08 | — |

---

## Delta summary

| Dimension | Upstream (postgres:17) | gwshield-postgres:v17.9 |
|---|---|---|
| Runtime base | Debian bookworm (full) | **distroless/cc-debian12** |
| Shell | yes | **no** |
| gosu | yes (multiple CVEs) | **no** |
| GnuPG / perl / curl | yes | **no** |
| snakeoil key | yes (baked in) | **no** |
| HIGH CVEs (unfixed) | many | **0** (1 accepted — glibc, not reachable) |
| CRITICAL CVEs | varies | **0** |
| Non-root UID | not enforced | **65532** |
