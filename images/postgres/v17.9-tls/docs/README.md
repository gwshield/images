# gwshield-postgres v17.9-tls

**Profile:** tls — single-node server, TCP + TLS (OpenSSL statically linked)
**Registry:** `ghcr.io/gwshield/postgres:v17.9-tls`
**Scan date:** 2026-03-08 — 0 unfixed HIGH / 0 CRITICAL CVEs

---

## Scan delta vs. upstream

Same upstream CVE elimination as `v17.9` standard — see that profile for the full table.

| Metric | Upstream `postgres:17` | gwshield-postgres:v17.9-tls |
|---|---|---|
| Image base | Debian bookworm (full) | distroless/cc-debian12 |
| Shell present | Yes | No |
| TLS cert | snakeoil (baked in) | Operator-supplied at runtime |
| HIGH CVEs (unfixed) | many | **0** (1 accepted — glibc) |

### Accepted finding

**CVE-2026-0861** (HIGH, glibc/libc6) — same justification as standard profile.
OpenSSL is statically linked so `libssl` CVEs do not affect the runtime layer.
Review date: **2026-09-08**.

---

## What was done

PostgreSQL v17.9 compiled with `--with-openssl`. OpenSSL statically linked into
the `postgres` binary — no `libssl.so` in the runtime layer.

Same `--without-*` flags as standard profile. TLS configuration:
- `ssl = on`, `ssl_min_protocol_version = 'TLSv1.2'`
- Certificate and key mounted at `/tls` at runtime — not baked into the image

### Non-root execution

Runs as UID/GID **65532** (`nonroot`).

---

## Source pins

| Component | Version | SHA256 / Digest |
|---|---|---|
| PostgreSQL source | 17.9 | `70eaebacf5344a0951075a666369d95d25ae4485ad0d6d3df652065277f4943c` |
| debian:12-slim (builder) | 12-slim | `sha256:74d56e3931e0d5a1dd51f8c8a2466d21de84a271cd3b5a733b803aa91abf4421` |
| distroless/cc-debian12 | — | `sha256:329e54034ce498f9c6b345044e8f530c6691f99e94a92446f68c0adf9baa8464` |
| Build date | 2026-03-08 | — |
