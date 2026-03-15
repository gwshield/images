# gwshield-nginx v1.28.2

**Profile:** http — HTTP/1.1 + TLS reverse proxy
**Registry:** `ghcr.io/gwshield/nginx:v1.28.2`
**Scan date:** 2026-03-01 — 0 HIGH / 0 CRITICAL CVEs

---

## Scan delta vs. upstream

| Metric | Upstream `nginx:1.28.2` (Debian) | gwshield-nginx:v1.28.2 |
|---|---|---|
| HIGH CVEs | 2 | **0** |
| CRITICAL CVEs | 0 | **0** |
| Total H/C CVEs | **2** | **0** |
| Image base | debian/bookworm-slim | FROM scratch |
| Shell present | Yes (`/bin/bash`) | No |
| OS package tree | Debian 12 (bookworm) | None |
| HTTP/2 | Yes (always-on) | No (stripped) |
| Modules | Full upstream set | Minimal |

### CVEs eliminated

| CVE | Severity | Component | Upstream status | Fix |
|---|---|---|---|---|
| CVE-2026-0861 | HIGH | glibc (libc6) | affected, no fix | Eliminated — musl/scratch, no glibc |
| CVE-2024-0553 | HIGH | libgcc-s1 | will_not_fix | Eliminated — no libgcc in scratch |

> **Note on `-` scan results:** `FROM scratch` images have no OS package tree.
> Trivy and Grype show `-` — correct and expected. The nginx binary is scanned separately as a C binary; 0 findings.

---

## What was done

### Source compilation

nginx v1.28.2 compiled from source with statically linked OpenSSL, pcre2, and zlib.
No shared library dependencies except the musl libc loader — verified via
`readelf -d nginx | grep NEEDED | grep -v musl` → empty output.

Hardening flags:

```
CFLAGS:  -O2 -fstack-protector-strong -D_FORTIFY_SOURCE=2 -Wformat -Werror=format-security
LDFLAGS: -Wl,-Bstatic -lpcre2-8 -lz -Wl,-Bdynamic -Wl,-z,relro,-z,now
```

### Modules stripped

The following modules are excluded at compile time to reduce attack surface:
`autoindex`, `ssi`, `geo`, `split_clients`, `fastcgi`, `uwsgi`, `scgi`, `grpc`,
`memcached`, `mail_pop3`, `mail_imap`, `mail_smtp`

### Minimal runtime (FROM scratch)

- `/usr/sbin/nginx` — compiled binary
- `/lib/ld-musl-x86_64.so.1` — musl dynamic loader (only shared dep)
- `/etc/ssl/certs/ca-certificates.crt` — TLS certificate validation
- `/usr/share/zoneinfo` — timezone data
- `/etc/passwd` and `/etc/group` — non-root user entries

No shell, no package manager, no curl, wget, or nc.

### Non-root execution

Runs as UID/GID **65532** (`nonroot`).

---

## Known limitations

- HTTP/2 not available in this profile — use `v1.28.2-http2` or `v1.28.2-http3`
- OpenSSL CVEs may affect the binary until rebuilt — no runtime patch path

---

## Source pins

| Component | Version | Digest |
|---|---|---|
| nginx source | 1.28.2 | PGP-verified (key `13C82A63B603576156E30A4EA0EA981B66B0D967`) |
| Alpine base | 3.23 | `sha256:25109184c71bdad752c8312a8623239686a9a2071e8825f20acb8f2198c3f659` |
| OpenSSL | Alpine 3.23 package | statically linked |
| pcre2 | Alpine 3.23 package | statically linked |
| zlib | Alpine 3.23 package | statically linked |
| Build date | 2026-03-01 | — |

---

## Delta summary

| Dimension | Upstream (nginx:1.28.2) | gwshield-nginx:v1.28.2 |
|---|---|---|
| Runtime base | Debian bookworm-slim | **scratch** |
| Shell | yes | **no** |
| Package manager | yes | **no** |
| Static libs | partial | **all static except musl loader** |
| HIGH CVEs | 2 | **0** |
| CRITICAL CVEs | 0 | **0** |
| Non-root UID | not enforced | **65532** |
| HTTP/2 | yes | **no** (stripped) |
