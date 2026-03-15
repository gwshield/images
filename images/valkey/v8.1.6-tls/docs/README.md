# gwshield-valkey v8.1.6-tls

**Profile:** tls — server with native TLS termination (OpenSSL statically linked)
**Registry:** `ghcr.io/gwshield/valkey:v8.1.6-tls`
**Scan date:** 2026-03-13 — 0 HIGH / 0 CRITICAL CVEs

---

## Scan delta vs. upstream

| Metric | Upstream `valkey/valkey:8-alpine` | gwshield-valkey:v8.1.6-tls |
|---|---|---|
| HIGH CVEs | varies | **0** |
| CRITICAL CVEs | varies | **0** |
| Image base | Alpine (full) | FROM scratch |
| Shell present | Yes | No |
| TLS support | No (requires stunnel) | Yes (native `BUILD_TLS=yes`) |
| OpenSSL | System Alpine | Statically linked from Alpine 3.23 |
| Listening ports | 6379 (plain) | 6380 (TLS) |

> **Note on `-` scan results:** `FROM scratch` images have no OS package tree.
> Trivy and Grype show `-` — correct and expected. Binary scanned separately; 0 findings.

---

## What was done

### Source compilation with TLS

Valkey v8.1.6 compiled with `BUILD_TLS=yes`. OpenSSL linked via `LIBSSL_LIBS` and
`LIBCRYPTO_LIBS` make variables — same pattern as gwshield-redis TLS. OpenSSL is
fully statically compiled into the binary; only the musl loader is dynamic.

Static linking verified: `readelf -d valkey-server | grep NEEDED | grep -v musl` → empty.

### TLS configuration

- Port `6380` (TLS); plain port `6379` not exposed in this profile
- Certificate and key must be mounted at runtime
- mTLS (`tls-auth-clients yes`) optional — configure in `valkey.conf`
- OpenSSL version follows Alpine 3.23 — rebuild picks up OpenSSL patches via digest bump

### Non-root execution

Runs as UID/GID **65532** (`nonroot`).

---

## Source pins

| Component | Version | Digest |
|---|---|---|
| Valkey source | 8.1.6 | `https://github.com/valkey-io/valkey/archive/refs/tags/8.1.6.tar.gz` |
| Alpine base | 3.23 | `sha256:25109184c71bdad752c8312a8623239686a9a2071e8825f20acb8f2198c3f659` |
| OpenSSL | Alpine 3.23 package | statically linked |
| Build date | 2026-03-13 | — |

---

## Delta summary

| Dimension | Upstream (valkey:8-alpine) | gwshield-valkey:v8.1.6-tls |
|---|---|---|
| Runtime base | Alpine (full) | **scratch** |
| Shell | yes | **no** |
| TLS | no | **yes (native, port 6380)** |
| OpenSSL | system (dynamic) | **statically linked (Alpine 3.23)** |
| CRITICAL CVEs | varies | **0** |
| HIGH CVEs | varies | **0** |
| Non-root UID | not enforced | **65532** |
