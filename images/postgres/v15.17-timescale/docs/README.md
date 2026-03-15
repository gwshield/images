# gwshield-postgres v15.17-timescale

**Profile:** timescale — standard + TimescaleDB + pg_partman + pg_cron
**Registry:** `ghcr.io/gwshield/postgres:v15.17-timescale`
**Scan date:** 2026-03-03 — 0 HIGH / 0 CRITICAL CVEs

---

## Scan delta vs. upstream

Same upstream CVE elimination as the standard profile — see `v15.17` for the full table.
Extension surface (TimescaleDB v2.25.1, pg_cron v1.6.7, pg_partman v5.4.2) scanned clean
at 2026-03-03.

| Metric | Upstream `postgres:15.17` | gwshield-postgres:v15.17-timescale |
|---|---|---|
| Total H/C CVEs | **76** | **0** |
| Image base | debian 13.0 (trixie) | distroless/cc-debian12 |
| Shell present | Yes | No |
| TimescaleDB | No | Yes (v2.25.1) |

---

## What was done

Extends the standard profile with:

| Extension | Version | Activation |
|---|---|---|
| TimescaleDB | 2.25.1 | `shared_preload_libraries` (mandatory) + `CREATE EXTENSION timescaledb;` |
| pg_partman | 5.4.2 | SQL + optional BGW |
| pg_cron | 1.6.7 | `shared_preload_libraries` |

**TimescaleDB** installs hooks into the PostgreSQL query planner and executor.
It **must** appear first in `shared_preload_libraries`:
`timescaledb,pg_partman_bgw,pg_cron`

**License note:** `timescaledb-tsl.so` (Timescale License) provides compression and
continuous aggregates. TSL is source-available but not OSI-approved open source.
Review the license before production deployment in commercial contexts.

### Accepted finding

**CVE-2026-0861** (HIGH, glibc/libc6) — same as vector profile. No upstream fix; not
reachable from PG network code with `--without-icu`/`locale=C`.
Review date: **2026-06-03**.

---

## Source pins

| Component | Version | SHA256 / Digest |
|---|---|---|
| PostgreSQL source | 15.17 | `f7fc926ea77ffc52e9d6fd58276427e3fe14d35fd9ff3ccf724ca88a28bcb4df` |
| TimescaleDB | 2.25.1 | — |
| pg_partman | 5.4.2 | — |
| pg_cron | 1.6.7 | — |
| debian:12-slim (builder) | 12-slim | `sha256:74d56e3931e0d5a1dd51f8c8a2466d21de84a271cd3b5a733b803aa91abf4421` |
| distroless/cc-debian12 | — | `sha256:329e54034ce498f9c6b345044e8f530c6691f99e94a92446f68c0adf9baa8464` |
| Build date | 2026-03-03 | — |
