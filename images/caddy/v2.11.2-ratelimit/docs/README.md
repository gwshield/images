# gwshield-caddy v2.11.2-ratelimit

**Profile:** ratelimit — native rate limiting via `caddy-ratelimit v0.1.0`
**Registry:** `ghcr.io/gwshield/caddy:v2.11.2-ratelimit`
**Scan date:** 2026-03-11 — 0 HIGH / 0 CRITICAL CVEs

---

## Scan delta vs. upstream

| Metric | Upstream `caddy:2-alpine` (Go 1.26.0) | gwshield-caddy:v2.11.2-ratelimit |
|---|---|---|
| CRITICAL CVEs | 1 | **0** |
| HIGH CVEs | 3 | **0** |
| Total H/C CVEs | **4** | **0** |
| Image base | Alpine 3.x (full) | FROM scratch |
| Shell present | Yes | No |
| Binary deps | dynamic | **fully static (0 NEEDED)** |
| Go toolchain | 1.26.0 | 1.26.1 (stdlib CVEs patched) |

All 4 upstream CVEs eliminated. Plugin dependency tree clean at 2026-03-11.

---

## What was done

Built with `xcaddy v0.4.5` (SHA-512 verified) including `caddy-ratelimit v0.1.0` (mholt).
`CGO_ENABLED=0` enforced — fully static binary (0 NEEDED entries).

### Rate limiting capabilities

| Algorithm | Use case |
|---|---|
| Sliding window | Smoothed per-IP throttling |
| Token bucket | Burst-tolerant per-route limits |
| Fixed window | Simple per-interval counters |

Configure via `rate_limit { zone ... }` directive in Caddyfile.
Rate limit state is **in-memory only** — resets on container restart. For distributed rate
limiting an external coordinated store is required.

---

## Source pins

| Component | Version | SHA256 / Digest |
|---|---|---|
| Caddy source | 2.11.2 | `ee12f7b5f97308708de5067deebb3d3322fc24f6d54f906a47a0a4e8db799122` |
| xcaddy | 0.4.5 (SHA-512) | `edea47d552fd9ac0a533386a72acaa95733ce734f347c11e5513469b5dc0eec0a62a6e21cfa93a83ab00b2dad72e0ee0b9bdf267a9654235f70d4c934739a15b` |
| Plugin caddy-ratelimit | v0.1.0 | — |
| Go toolchain | `golang:1.26.1-alpine3.22` | `sha256:07e91d24f6330432729082bb580983181809e0a48f0f38ecde26868d4568c6ac` |
| Alpine base | 3.22 | `sha256:55ae5d250caebc548793f321534bc6a8ef1d116f334f18f4ada1b2daad3251b2` |
| Build date | 2026-03-11 | — |

---

## Delta summary

| Dimension | Upstream (caddy:2-alpine) | gwshield-caddy:v2.11.2-ratelimit |
|---|---|---|
| Go toolchain | 1.26.0 | **1.26.1** |
| Runtime base | Alpine 3.x | **scratch** |
| Shell | yes | **no** |
| Binary deps | dynamic | **fully static (0 NEEDED)** |
| CRITICAL CVEs | 1 | **0** |
| HIGH CVEs | 3 | **0** |
| Rate limiting | none | **native (sliding / token / fixed-window)** |
| Distributed state | n/a | **not supported (in-memory only)** |
| Non-root UID | not enforced | **65532** |
