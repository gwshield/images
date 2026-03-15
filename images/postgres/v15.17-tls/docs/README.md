# gwshield-postgres v15.17-tls

**Profile:** tls — single-node server, TCP + TLS (OpenSSL statically linked)
**Registry:** `ghcr.io/gwshield/postgres:v15.17-tls`
**Scan date:** 2026-03-02 — 0 HIGH / 0 CRITICAL CVEs

---

## Scan delta vs. upstream

| Metric | Upstream `postgres:15.17` (Debian 13) | gwshield-postgres:v15.17-tls |
|---|---|---|
| Total H/C CVEs | **76** | **0** |
| Image base | debian 13.0 (trixie) | distroless/cc-debian12 |
| Shell present | Yes | No |
| gosu binary | Yes (41 CVEs) | No |
| TLS | snakeoil key (baked in) | Operator-supplied cert at runtime |
| snakeoil key | Yes | **No** |

Same upstream CVE elimination as the standard profile — see `v15.17` for the full table.

---

## What was done

### Source compilation with TLS

PostgreSQL v15.17 compiled with `--with-openssl`. OpenSSL is statically linked —
`libssl` and `libcrypto` are compiled into the `postgres` binary. No separate
`libssl.so` in the runtime layer.

All `--without-*` flags from the standard profile apply here as well
(`--without-readline`, `--without-icu`, `--disable-rpath`).

### TLS configuration

- `ssl = on` — TLS required for client connections
- `ssl_min_protocol_version = 'TLSv1.2'` — TLS 1.0/1.1 disabled
- Certificate and key mounted at runtime via `/tls` volume — not baked into the image
- mTLS: set `ssl_ca_file` and `clientcert=verify-full` in `pg_hba.conf` (operator opt-in)

### Non-root execution

Runs as UID/GID **65532** (`nonroot`).

---

## Source pins

| Component | Version | SHA256 / Digest |
|---|---|---|
| PostgreSQL source | 15.17 | `f7fc926ea77ffc52e9d6fd58276427e3fe14d35fd9ff3ccf724ca88a28bcb4df` |
| debian:12-slim (builder) | 12-slim | `sha256:74d56e3931e0d5a1dd51f8c8a2466d21de84a271cd3b5a733b803aa91abf4421` |
| distroless/cc-debian12 | — | `sha256:329e54034ce498f9c6b345044e8f530c6691f99e94a92446f68c0adf9baa8464` |
| Build date | 2026-03-02 | — |

---

## Delta summary

| Dimension | Upstream (postgres:15.17) | gwshield-postgres:v15.17-tls |
|---|---|---|
| Runtime base | Debian 13 (trixie) | **distroless/cc-debian12** |
| Shell | yes | **no** |
| TLS cert | snakeoil (baked in) | **operator-supplied (runtime mount)** |
| HIGH CVEs | 31+ | **0** |
| CRITICAL CVEs | 45+ | **0** |
| Non-root UID | not enforced | **65532** |
