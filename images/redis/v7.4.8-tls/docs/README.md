# gwshield-redis v7.4.8-tls

**Profile:** tls — server with native TLS termination (OpenSSL statically linked)
**Registry:** `ghcr.io/gwshield/redis:v7.4.8-tls`
**Scan date:** 2026-03-01 — 0 HIGH / 0 CRITICAL CVEs

---

## Scan delta vs. upstream

| Metric | Upstream `redis:7.4.8` (Debian) | gwshield-redis:v7.4.8-tls |
|---|---|---|
| HIGH CVEs | 3 | **0** |
| CRITICAL CVEs | 41 | **0** |
| Total H/C CVEs | **44** | **0** |
| Image base | debian/bookworm-slim | FROM scratch |
| Shell present | Yes (`/bin/bash`) | No |
| gosu binary | Yes (Go 1.18.2 — 41 CVEs) | No |
| TLS support | No (requires stunnel) | Yes (native `BUILD_TLS=yes`) |
| OpenSSL | System Debian 12 | Statically linked from Alpine 3.23 |
| Listening ports | 6379 (plain) | 6380 (TLS) |

### CVEs eliminated

| CVE | Severity | Component | Upstream status | Fix |
|---|---|---|---|---|
| CVE-2026-0861 | HIGH | glibc (libc6) | affected, no fix | Eliminated — musl/scratch |
| CVE-2023-45853 | CRITICAL | zlib1g | will_not_fix | Eliminated — statically linked patched zlib |
| 41 CVEs in gosu | HIGH/CRITICAL | gosu (Go 1.18.2 stdlib) | will_not_fix | Eliminated — gosu not included |

> **Note on `-` scan results:** `FROM scratch` images have no OS package tree.
> Trivy and Grype show `-` — correct and expected. The redis-server binary is scanned
> separately as a C binary; 0 findings.

---

## What was done

### Source compilation with TLS

Redis v7.4.8 compiled with `BUILD_TLS=yes`. OpenSSL is linked via the Redis
`LIBSSL_LIBS` and `LIBCRYPTO_LIBS` make variables — Redis resolves these via
pkg-config and appends them to `FINAL_LIBS`, resulting in a fully static TLS build.

Hardening flags: `-fstack-protector-strong`, `-D_FORTIFY_SOURCE=2`, `-fPIE -pie`,
`-Wl,-z,relro,-z,now`

Static linking verified: `readelf -d redis-server | grep NEEDED | grep -v musl` → empty
(libssl and libcrypto fully compiled in; only musl loader dynamic).

### TLS configuration

- Port `6380` (TLS); plain port `6379` not exposed in this profile
- Certificate and key must be mounted at runtime
- mTLS (`tls-auth-clients yes`) optional — configure in `redis.conf`
- OpenSSL version follows Alpine 3.23 — rebuild picks up OpenSSL patches via digest bump

### gosu eliminated

Non-root execution via `USER 65532:65532`.

### Scripting disabled

`DISABLE_SCRIPTING=yes` at compile time.

---

## Source pins

| Component | Version | Digest |
|---|---|---|
| Redis source | 7.4.8 | `https://download.redis.io/releases/` (PGP-verified) |
| Alpine base | 3.23 | `sha256:25109184c71bdad752c8312a8623239686a9a2071e8825f20acb8f2198c3f659` |
| OpenSSL | Alpine 3.23 package | statically linked |
| Build date | 2026-03-01 | — |

---

## Delta summary

| Dimension | Upstream (redis:7.4.8) | gwshield-redis:v7.4.8-tls |
|---|---|---|
| Runtime base | Debian bookworm-slim | **scratch** |
| Shell | yes | **no** |
| gosu | yes (41 CVEs) | **no** |
| TLS | no | **yes (native, port 6380)** |
| OpenSSL | system (dynamic) | **statically linked (Alpine 3.23)** |
| CRITICAL CVEs | 41 | **0** |
| HIGH CVEs | 3 | **0** |
| Non-root UID | not enforced | **65532** |
