# gwshield-caddy v2.11.2

**Profile:** standard — static binary, auto-https off, scratch runtime
**Registry:** `ghcr.io/gwshield/caddy:v2.11.2`
**Scan date:** 2026-03-11 — 0 HIGH / 0 CRITICAL CVEs

---

## Scan delta vs. upstream

| Metric | Upstream `caddy:2-alpine` (Go 1.26.0) | gwshield-caddy:v2.11.2 |
|---|---|---|
| CRITICAL CVEs | 1 | **0** |
| HIGH CVEs | 3 | **0** |
| Total H/C CVEs | **4** | **0** |
| Image base | Alpine 3.x (full) | FROM scratch |
| Shell present | Yes (`/bin/ash`) | No |
| Binary deps | dynamic (musl, zlib) | **fully static (0 NEEDED)** |
| Go toolchain | 1.26.0 | 1.26.1 (stdlib CVEs patched) |

### CVEs eliminated

| CVE | Severity | Component | Fix |
|---|---|---|---|
| CVE-2026-22184 | CRITICAL | Alpine zlib | Eliminated — FROM scratch, no Alpine packages |
| CVE-2026-25679 | HIGH | Go stdlib crypto/tls | Eliminated — rebuilt with Go 1.26.1 |
| CVE-2026-27137 | HIGH | Go stdlib net/http | Eliminated — rebuilt with Go 1.26.1 |
| CVE-2026-27142 | HIGH | Go stdlib archive/zip | Eliminated — rebuilt with Go 1.26.1 |

---

## What was done

### Source compilation

Caddy v2.11.2 compiled from source using Go 1.26.1 with `CGO_ENABLED=0` — producing
a fully static binary with zero shared library dependencies.

Binary verified: `readelf -d caddy | grep NEEDED` → **empty output**.

### Minimal runtime (FROM scratch)

- `/usr/bin/caddy` — compiled static binary
- `/etc/ssl/certs/ca-certificates.crt` — TLS certificate validation
- `/usr/share/zoneinfo` — timezone data
- `/etc/caddy/Caddyfile` — bundled minimal config (`auto_https off`)
- `/data/` and `/config/` — pre-created XDG directories (owned by UID 65532)

No shell, no package manager, no curl, wget, or nc.

### Auto HTTPS disabled

The bundled Caddyfile sets `auto_https off`. Enable by mounting a custom Caddyfile.

### Non-root execution

Runs as UID/GID **65532** (`nonroot`).

---

## Source pins

| Component | Version | SHA256 / Digest |
|---|---|---|
| Caddy source | 2.11.2 | `ee12f7b5f97308708de5067deebb3d3322fc24f6d54f906a47a0a4e8db799122` |
| Go toolchain | `golang:1.26.1-alpine3.22` | `sha256:07e91d24f6330432729082bb580983181809e0a48f0f38ecde26868d4568c6ac` |
| Alpine base | 3.22 | `sha256:55ae5d250caebc548793f321534bc6a8ef1d116f334f18f4ada1b2daad3251b2` |
| Build date | 2026-03-11 | — |

---

## Delta summary

| Dimension | Upstream (caddy:2-alpine) | gwshield-caddy:v2.11.2 |
|---|---|---|
| Go toolchain | 1.26.0 | **1.26.1** (3 stdlib CVEs fixed) |
| Runtime base | Alpine 3.x (full) | **scratch** |
| Shell | yes | **no** |
| Binary deps | dynamic | **fully static (0 NEEDED)** |
| CRITICAL CVEs | 1 | **0** |
| HIGH CVEs | 3 | **0** |
| Non-root UID | not enforced | **65532** |
| Auto HTTPS | enabled | **disabled** (operator opt-in) |
