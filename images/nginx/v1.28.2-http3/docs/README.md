# gwshield-nginx v1.28.2-http3

**Profile:** http3 — HTTP/1.1 + HTTP/2 + HTTP/3 / QUIC (QuicTLS)
**Registry:** `ghcr.io/gwshield/nginx:v1.28.2-http3`
**Scan date:** 2026-03-01 — 0 HIGH / 0 CRITICAL CVEs

---

## Scan delta vs. upstream

| Metric | Upstream `nginx:1.28.2` (Debian) | gwshield-nginx:v1.28.2-http3 |
|---|---|---|
| HIGH CVEs | 2 | **0** |
| CRITICAL CVEs | 0 | **0** |
| Total H/C CVEs | **2** | **0** |
| Image base | debian/bookworm-slim | FROM scratch |
| Shell present | Yes (`/bin/bash`) | No |
| OS package tree | Debian 12 (bookworm) | None |
| HTTP/3 / QUIC | No | Yes (QuicTLS `openssl-3.3.0-quic1`) |
| musl loader | No | Yes (required for QuicTLS linkage) |

### CVEs eliminated

| CVE | Severity | Component | Upstream status | Fix |
|---|---|---|---|---|
| CVE-2026-0861 | HIGH | glibc (libc6) | affected, no fix | Eliminated — musl/scratch, no glibc |
| CVE-2024-0553 | HIGH | libgcc-s1 | will_not_fix | Eliminated — no libgcc in scratch |

> **Note on `-` scan results:** `FROM scratch` images have no OS package tree.
> Trivy and Grype show `-` — correct and expected. nginx binary scanned separately; 0 findings.

---

## What was done

### Source compilation

nginx v1.28.2 compiled with HTTP/3 support using QuicTLS (`openssl-3.3.0-quic1`) built
from source via `--with-openssl=<path>`. QuicTLS is statically compiled into the nginx
binary — no separate `.so` in the runtime layer.

**Why QuicTLS, not BoringSSL:** nginx's `--with-openssl=<path>` build mode requires an
OpenSSL-compatible `./config` script. BoringSSL does not ship one and is incompatible
with this build path. QuicTLS is an OpenSSL 3.x fork that adds QUIC transport support
while remaining fully compatible with nginx's build system.

Hardening flags:

```
CFLAGS:  -O2 -fstack-protector-strong -D_FORTIFY_SOURCE=2 -Wformat -Werror=format-security
LDFLAGS: -Wl,-Bstatic -lpcre2-8 -lz -Wl,-Bdynamic -Wl,-z,relro,-z,now
```

Static linking verified: `readelf -d nginx | grep NEEDED | grep -v musl` → empty output
(only musl loader permitted).

### Minimal runtime (FROM scratch)

- `/usr/sbin/nginx` — compiled binary (with QuicTLS statically linked in)
- `/lib/ld-musl-x86_64.so.1` — musl dynamic loader (only shared dep)
- `/etc/ssl/certs/ca-certificates.crt`, `/usr/share/zoneinfo`, `/etc/passwd`, `/etc/group`

`EXPOSE 8443/udp` is declared for QUIC transport.

### Non-root execution

Runs as UID/GID **65532** (`nonroot`).

### QuicTLS monitoring

QuicTLS is not tracked as a named package by Trivy or Grype — CVEs will not appear in
automated scans. Monitor upstream manually:
`https://github.com/quictls/openssl/releases`

---

## Source pins

| Component | Version | Source |
|---|---|---|
| nginx source | 1.28.2 | PGP-verified (key `13C82A63B603576156E30A4EA0EA981B66B0D967`) |
| QuicTLS | `openssl-3.3.0-quic1` | `https://github.com/quictls/openssl` |
| Alpine base | 3.23 | `sha256:25109184c71bdad752c8312a8623239686a9a2071e8825f20acb8f2198c3f659` |
| pcre2 | Alpine 3.23 package | statically linked |
| zlib | Alpine 3.23 package | statically linked |
| Build date | 2026-03-01 | — |

---

## Delta summary

| Dimension | Upstream (nginx:1.28.2) | gwshield-nginx:v1.28.2-http3 |
|---|---|---|
| Runtime base | Debian bookworm-slim | **scratch** |
| Shell | yes | **no** |
| Package manager | yes | **no** |
| TLS backend | OpenSSL (system) | **QuicTLS (statically compiled in)** |
| HIGH CVEs | 2 | **0** |
| CRITICAL CVEs | 0 | **0** |
| Non-root UID | not enforced | **65532** |
| HTTP/3 / QUIC | no | **yes** (`:8443/udp`) |
| QuicTLS CVE scanning | automatic | **manual monitoring required** |
