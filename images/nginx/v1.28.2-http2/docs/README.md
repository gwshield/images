# gwshield-nginx v1.28.2-http2

**Profile:** http2 — HTTP/1.1 + HTTP/2 + TLS
**Registry:** `ghcr.io/gwshield/nginx:v1.28.2-http2`
**Scan date:** 2026-03-01 — 0 HIGH / 0 CRITICAL CVEs

---

## Scan delta vs. upstream

| Metric | Upstream `nginx:1.28.2` (Debian) | gwshield-nginx:v1.28.2-http2 |
|---|---|---|
| HIGH CVEs | 2 | **0** |
| CRITICAL CVEs | 0 | **0** |
| Total H/C CVEs | **2** | **0** |
| Image base | debian/bookworm-slim | FROM scratch |
| Shell present | Yes (`/bin/bash`) | No |
| OS package tree | Debian 12 (bookworm) | None |
| HTTP/2 | Yes | Yes (`ngx_http_v2_module`) |

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

nginx v1.28.2 compiled from source with `--with-http_v2_module` added to the http profile.
Same static linking and hardening flags as the http profile. HTTP/2 Rapid Reset
(CVE-2023-44487) is fixed in nginx 1.25.3+ — not applicable to 1.28.2.

Hardening flags:

```
CFLAGS:  -O2 -fstack-protector-strong -D_FORTIFY_SOURCE=2 -Wformat -Werror=format-security
LDFLAGS: -Wl,-Bstatic -lpcre2-8 -lz -Wl,-Bdynamic -Wl,-z,relro,-z,now
```

Static linking verified: `readelf -d nginx | grep NEEDED | grep -v musl` → empty output.

### Minimal runtime (FROM scratch)

Identical to the http profile. No additional runtime files for HTTP/2.

### Non-root execution

Runs as UID/GID **65532** (`nonroot`).

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

| Dimension | Upstream (nginx:1.28.2) | gwshield-nginx:v1.28.2-http2 |
|---|---|---|
| Runtime base | Debian bookworm-slim | **scratch** |
| Shell | yes | **no** |
| Package manager | yes | **no** |
| Static libs | partial | **all static except musl loader** |
| HIGH CVEs | 2 | **0** |
| CRITICAL CVEs | 0 | **0** |
| Non-root UID | not enforced | **65532** |
| HTTP/2 | yes | **yes** (`ngx_http_v2_module`) |
| HTTP/3 | no | **no** — see `v1.28.2-http3` |
