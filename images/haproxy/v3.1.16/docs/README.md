# gwshield-haproxy v3.1.16 (standard)

**Profile:** standard — TCP/HTTP proxy, Prometheus metrics, no TLS frontend
**Registry:** `ghcr.io/gwshield/haproxy:v3.1.16`
**Scan date:** 2026-03-11 — 0 HIGH / 0 CRITICAL CVEs

---

## Scan delta vs. upstream

| Metric | Upstream `haproxy:3.1-alpine` | gwshield-haproxy:v3.1.16 |
|---|---|---|
| HIGH CVEs | 0 | **0** |
| CRITICAL CVEs | 0 | **0** |
| Total H/C CVEs | **0** | **0** |
| Image base | Alpine 3.x (full) | FROM scratch |
| Shell present | Yes (`/bin/ash`) | No |
| Package manager | Yes (`apk`) | No |
| Network tools | Yes | No |
| Listening ports | 80, 443, 8080 | 8080 (HTTP), 9101 (metrics) |

> **Note on `-` scan results:** Trivy and Grype show `-` (not scanned / no result) for
> `FROM scratch` images. This is **correct and expected behaviour** — a scratch image has
> no OS package database, no package manager, and no package tree for the scanner to
> traverse. The HAProxy binary (C) is scanned separately; no findings reported.

---

## What was done

### Source rebuild

HAProxy v3.1.16 compiled from the official source tarball with statically linked
OpenSSL, PCRE2 (JIT), and zlib. No shared library dependencies except the musl
libc dynamic loader (`ld-musl-x86_64.so.1`) — verified via `readelf -d`.

| Make variable | Value | Purpose |
|---|---|---|
| `TARGET` | `linux-musl` | musl libc target |
| `USE_OPENSSL=1` | static | TLS backend; no `libssl.so` in runtime |
| `USE_STATIC_PCRE2=1` | yes | No `libpcre2-8.so` in runtime layer |
| `USE_PCRE2_JIT=1` | yes | PCRE2 JIT compiler for ACL performance |
| `USE_ZLIB=1` | static | HTTP compression; no `libz.so` in runtime |
| `USE_SLZ=0` | disabled | Use external zlib |
| `USE_PROMEX=1` | yes | Prometheus exporter built-in; metrics on `:9101` |
| `USE_LUA` | not set | Lua excluded — reduces attack surface |
| `USE_THREAD=1` | yes | Multi-threading |

Static linking verified: `readelf -d haproxy | grep NEEDED | grep -v musl` → empty output.

### Minimal runtime (FROM scratch)

- `/lib/ld-musl-x86_64.so.1` — musl dynamic loader (only shared dep)
- `/usr/local/sbin/haproxy` — compiled binary
- `/etc/passwd` and `/etc/group` — non-root user entries
- `/etc/ssl/certs/ca-certificates.crt` — TLS certificate validation for backends
- `/usr/share/zoneinfo` — timezone data

No shell, no package manager, no curl, wget, or nc.

### Non-root execution

Runs as UID/GID **65532** (`nonroot`).

### Prometheus metrics

`USE_PROMEX=1` compiles the Prometheus exporter. `/metrics` is exposed on `:9101`.
No extra binary or sidecar required.

---

## Known limitations

- **Lua scripting disabled** in the standard profile. See the `v3.1.16-ssl` profile
  for TLS termination; a future `lua` profile for Lua scripting.
- **No TLS frontend** — the standard profile verifies backend TLS (via statically linked
  OpenSSL) but does not terminate TLS from clients.

---

## Source pins

| Component | Version | SHA256 |
|---|---|---|
| HAProxy source | 3.1.16 | `ef48aec8c884af4eace2669a639b57038e2bebcad22eb506d713725e9d9a445a` |
| Alpine base | 3.22 | `sha256:55ae5d250caebc548793f321534bc6a8ef1d116f334f18f4ada1b2daad3251b2` |
| Build date | 2026-03-11 | — |

---

## Delta summary

| Dimension | Upstream (haproxy:3.1-alpine) | gwshield-haproxy:v3.1.16 |
|---|---|---|
| Runtime base | Alpine 3.x (full) | scratch (minimal) |
| Shell | yes (`/bin/ash`) | **no** |
| Package manager | yes (`apk`) | **no** |
| Network tools | yes | **no** |
| Static libs | partial | **all static except musl loader** |
| CRITICAL CVEs | 0 | **0** |
| HIGH CVEs | 0 | **0** |
| Non-root UID | not enforced | **65532** |
| Prometheus metrics | no | **yes** (`:9101/metrics`) |
