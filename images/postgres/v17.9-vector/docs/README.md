# gwshield-postgres v17.9-vector

**Profile:** vector — standard + pgvector + pg_partman + pg_cron
**Registry:** `ghcr.io/gwshield/postgres:v17.9-vector`
**Scan date:** 2026-03-08 — 0 unfixed HIGH / 0 CRITICAL CVEs

---

## Scan delta vs. upstream

Same upstream CVE elimination as `v17.9` standard. Extension surface
(pgvector v0.8.2, pg_cron v1.6.7, pg_partman v5.4.3) scanned clean at 2026-03-08.

| Metric | Upstream `postgres:17` | gwshield-postgres:v17.9-vector |
|---|---|---|
| Image base | Debian bookworm (full) | distroless/cc-debian12 |
| Shell present | Yes | No |
| pgvector | No | Yes (v0.8.2) |
| HIGH CVEs (unfixed) | many | **0** (1 accepted — glibc) |

### Accepted finding

**CVE-2026-0861** (HIGH, glibc/libc6) — same justification as standard profile.
The vulnerable `iconv()` code path is not reachable with `--without-icu`/`locale=C`.
Review date: **2026-09-08**.

---

## What was done

Extends the standard profile with:

| Extension | Version | Activation |
|---|---|---|
| pgvector | 0.8.2 | `CREATE EXTENSION vector;` per database |
| pg_partman | 5.4.3 | SQL + optional BGW |
| pg_cron | 1.6.7 | `shared_preload_libraries` |

pgvector adds the `VECTOR` data type and IVFFlat / HNSW index types.
Activated per-database — no network exposure beyond standard PostgreSQL.

### Non-root execution

Runs as UID/GID **65532** (`nonroot`).

---

## Source pins

| Component | Version | SHA256 / Digest |
|---|---|---|
| PostgreSQL source | 17.9 | `70eaebacf5344a0951075a666369d95d25ae4485ad0d6d3df652065277f4943c` |
| pgvector | 0.8.2 | — |
| pg_partman | 5.4.3 | — |
| pg_cron | 1.6.7 | — |
| debian:12-slim (builder) | 12-slim | `sha256:74d56e3931e0d5a1dd51f8c8a2466d21de84a271cd3b5a733b803aa91abf4421` |
| distroless/cc-debian12 | — | `sha256:329e54034ce498f9c6b345044e8f530c6691f99e94a92446f68c0adf9baa8464` |
| Build date | 2026-03-08 | — |
