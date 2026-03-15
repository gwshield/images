# gwshield-postgres v17.9-cli

**Profile:** cli — psql client only, no server binary
**Registry:** `ghcr.io/gwshield/postgres:v17.9-cli`
**Scan date:** 2026-03-08 — 0 unfixed HIGH / 0 CRITICAL CVEs

---

## Scan delta vs. upstream

| Metric | Upstream `postgres:17` | gwshield-postgres:v17.9-cli |
|---|---|---|
| Image base | Debian bookworm (full) | distroless/cc-debian12 |
| Shell present | Yes | No |
| Server binary | Yes | **No** |
| Listening ports | 5432 | **None** |
| HIGH CVEs (unfixed) | many | **0** (1 accepted — glibc) |

### Accepted finding

**CVE-2026-0861** (HIGH, glibc/libc6) — glibc is a transitive dep of
`distroless/cc-debian12`. No server binary, no listening ports — attack surface
is minimal. Used ephemerally. Review date: **2026-09-08**.

---

## What was done

Full PostgreSQL v17.9 source compiled; only `psql` and required shared libraries
extracted to the runtime image. Client-only — outbound connections only, no
persistent state, no inbound ports.

### Non-root execution

Runs as UID/GID **65532** (`nonroot`). No writable volumes required.

---

## Usage

```bash
docker run --rm \
  ghcr.io/gwshield/postgres:v17.9-cli \
  -h <postgres-host> -U postgres -d mydb -c 'SELECT version();'
```

---

## Source pins

| Component | Version | SHA256 / Digest |
|---|---|---|
| PostgreSQL source | 17.9 | `70eaebacf5344a0951075a666369d95d25ae4485ad0d6d3df652065277f4943c` |
| debian:12-slim (builder) | 12-slim | `sha256:74d56e3931e0d5a1dd51f8c8a2466d21de84a271cd3b5a733b803aa91abf4421` |
| distroless/cc-debian12 | — | `sha256:329e54034ce498f9c6b345044e8f530c6691f99e94a92446f68c0adf9baa8464` |
| Build date | 2026-03-08 | — |
