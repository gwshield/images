# gwshield-postgres v15.17-vector

**Profile:** vector — standard + pgvector + pg_partman + pg_cron
**Registry:** `ghcr.io/gwshield/postgres:v15.17-vector`
**Scan date:** 2026-03-03 — 0 HIGH / 0 CRITICAL CVEs

---

## Scan delta vs. upstream

Same upstream CVE elimination as the standard profile — see `v15.17` for the full table.
Extension dependency surface (pgvector v0.8.2, pg_cron v1.6.7, pg_partman v5.4.2)
scanned clean at 2026-03-03.

| Metric | Upstream `postgres:15.17` | gwshield-postgres:v15.17-vector |
|---|---|---|
| Total H/C CVEs | **76** | **0** |
| Image base | debian 13.0 (trixie) | distroless/cc-debian12 |
| Shell present | Yes | No |
| pgvector | No | Yes (v0.8.2) |

---

## What was done

Extends the standard profile with:

| Extension | Version | Activation |
|---|---|---|
| pgvector | 0.8.2 | `CREATE EXTENSION vector;` per database |
| pg_partman | 5.4.2 | SQL + optional BGW; `shared_preload_libraries` |
| pg_cron | 1.6.7 | `shared_preload_libraries` |

**pgvector** adds the `VECTOR` data type and IVFFlat / HNSW index types for similarity
search. Activated per-database — no network exposure beyond standard PostgreSQL.

### Accepted finding

**CVE-2026-0861** (HIGH, glibc/libc6) — no upstream fix available. glibc is a transitive
dependency of `distroless/cc-debian12`. PostgreSQL in this profile uses `--without-icu`
and `locale=C`; the vulnerable `iconv()` code path is not reachable from network-facing
input. Compensating controls: non-root UID 65532, no shell, scram-sha-256 auth.
Review date: **2026-06-03**.

---

## Source pins

| Component | Version | SHA256 / Digest |
|---|---|---|
| PostgreSQL source | 15.17 | `f7fc926ea77ffc52e9d6fd58276427e3fe14d35fd9ff3ccf724ca88a28bcb4df` |
| pgvector | 0.8.2 | — |
| pg_partman | 5.4.2 | — |
| pg_cron | 1.6.7 | — |
| debian:12-slim (builder) | 12-slim | `sha256:74d56e3931e0d5a1dd51f8c8a2466d21de84a271cd3b5a733b803aa91abf4421` |
| distroless/cc-debian12 | — | `sha256:329e54034ce498f9c6b345044e8f530c6691f99e94a92446f68c0adf9baa8464` |
| Build date | 2026-03-03 | — |
