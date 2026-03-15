# gwshield-caddy v2.11.2-crowdsec

**Profile:** crowdsec — IP bouncer via `caddy-crowdsec-bouncer v0.10.0`
**Registry:** `ghcr.io/gwshield/caddy:v2.11.2-crowdsec`
**Scan date:** 2026-03-11 — 0 HIGH / 0 CRITICAL CVEs

---

## Scan delta vs. upstream

| Metric | Upstream `caddy:2-alpine` (Go 1.26.0) | gwshield-caddy:v2.11.2-crowdsec |
|---|---|---|
| CRITICAL CVEs | 1 | **0** |
| HIGH CVEs | 3 | **0** |
| Total H/C CVEs | **4** | **0** |
| Image base | Alpine 3.x (full) | FROM scratch |
| Shell present | Yes | No |
| Binary deps | dynamic | **fully static (0 NEEDED)** |
| Go toolchain | 1.26.0 | 1.26.1 (stdlib CVEs patched) |

All 4 upstream CVEs eliminated — see `caddy:v2.11.2` for details.
Plugin dependency tree (`caddy-crowdsec-bouncer v0.10.0` http + layer4): clean at 2026-03-11.

---

## What was done

Built with `xcaddy v0.4.5` (SHA-512 verified) including both sub-packages of
`caddy-crowdsec-bouncer v0.10.0` (`http` + `layer4`). Both sub-packages are required —
omitting either silently drops part of the bouncer functionality.

`CGO_ENABLED=0` enforced — fully static binary (0 NEEDED entries).

### CrowdSec runtime model

The bouncer queries CrowdSec LAPI on every request. IPs in the blocklist receive `403`
before reaching upstreams. No traffic content is sent to CrowdSec — only the client IP
is evaluated. LAPI unreachability causes fail-open (requests pass through).

Requires `CROWDSEC_API_URL` and `CROWDSEC_API_KEY` at runtime.

---

## Source pins

| Component | Version | SHA256 / Digest |
|---|---|---|
| Caddy source | 2.11.2 | `ee12f7b5f97308708de5067deebb3d3322fc24f6d54f906a47a0a4e8db799122` |
| xcaddy | 0.4.5 (SHA-512) | `edea47d552fd9ac0a533386a72acaa95733ce734f347c11e5513469b5dc0eec0a62a6e21cfa93a83ab00b2dad72e0ee0b9bdf267a9654235f70d4c934739a15b` |
| Plugin caddy-crowdsec-bouncer | v0.10.0 | — |
| Go toolchain | `golang:1.26.1-alpine3.22` | `sha256:07e91d24f6330432729082bb580983181809e0a48f0f38ecde26868d4568c6ac` |
| Alpine base | 3.22 | `sha256:55ae5d250caebc548793f321534bc6a8ef1d116f334f18f4ada1b2daad3251b2` |
| Build date | 2026-03-11 | — |

---

## Delta summary

| Dimension | Upstream (caddy:2-alpine) | gwshield-caddy:v2.11.2-crowdsec |
|---|---|---|
| Go toolchain | 1.26.0 | **1.26.1** |
| Runtime base | Alpine 3.x | **scratch** |
| Shell | yes | **no** |
| Binary deps | dynamic | **fully static (0 NEEDED)** |
| CRITICAL CVEs | 1 | **0** |
| HIGH CVEs | 3 | **0** |
| IP reputation enforcement | no | **yes** (CrowdSec LAPI) |
| Non-root UID | not enforced | **65532** |
