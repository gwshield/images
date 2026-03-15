# gwshield-caddy v2.11.2-security

**Profile:** security — OIDC, OAuth2, JWT, local auth via `caddy-security v1.1.45`
**Registry:** `ghcr.io/gwshield/caddy:v2.11.2-security`
**Scan date:** 2026-03-11 — 0 HIGH / 0 CRITICAL CVEs

---

## Scan delta vs. upstream

| Metric | Upstream `caddy:2-alpine` (Go 1.26.0) | gwshield-caddy:v2.11.2-security |
|---|---|---|
| CRITICAL CVEs | 1 | **0** |
| HIGH CVEs | 3 | **0** |
| Total H/C CVEs | **4** | **0** |
| Image base | Alpine 3.x (full) | FROM scratch |
| Shell present | Yes | No |
| Binary deps | dynamic | **fully static (0 NEEDED)** |
| Go toolchain | 1.26.0 | 1.26.1 (stdlib CVEs patched) |

All 4 upstream CVEs eliminated.
Plugin dependency tree (`caddy-security v1.1.45`, ~120 transitive Go deps): clean at 2026-03-11.

---

## What was done

Built with `xcaddy v0.4.5` (SHA-512 verified) including `caddy-security v1.1.45` (greenpau).
`CGO_ENABLED=0` enforced — fully static binary (0 NEEDED entries).

### Authentication capabilities

| Capability | Detail |
|---|---|
| OIDC | Authorization Code flow; configurable provider |
| OAuth2 | GitHub, Google, Facebook, generic providers |
| JWT | Bearer token validation; configurable claims |
| Local auth | Username/password portal with bcrypt hashing |
| MFA | TOTP-based second factor (optional) |

Auth state is persisted in `/data` (XDG_DATA_HOME) — mount a persistent volume for session continuity.

> **Note on dependency surface:** `caddy-security v1.1.45` has ~120 transitive Go dependencies —
> the largest of all gwshield Caddy profiles. Review the allowlist on every plugin version bump.

---

## Source pins

| Component | Version | SHA256 / Digest |
|---|---|---|
| Caddy source | 2.11.2 | `ee12f7b5f97308708de5067deebb3d3322fc24f6d54f906a47a0a4e8db799122` |
| xcaddy | 0.4.5 (SHA-512) | `edea47d552fd9ac0a533386a72acaa95733ce734f347c11e5513469b5dc0eec0a62a6e21cfa93a83ab00b2dad72e0ee0b9bdf267a9654235f70d4c934739a15b` |
| Plugin caddy-security | v1.1.45 | — |
| Go toolchain | `golang:1.26.1-alpine3.22` | `sha256:07e91d24f6330432729082bb580983181809e0a48f0f38ecde26868d4568c6ac` |
| Alpine base | 3.22 | `sha256:55ae5d250caebc548793f321534bc6a8ef1d116f334f18f4ada1b2daad3251b2` |
| Build date | 2026-03-11 | — |

---

## Delta summary

| Dimension | Upstream (caddy:2-alpine) | gwshield-caddy:v2.11.2-security |
|---|---|---|
| Go toolchain | 1.26.0 | **1.26.1** |
| Runtime base | Alpine 3.x | **scratch** |
| Shell | yes | **no** |
| Binary deps | dynamic | **fully static (0 NEEDED)** |
| CRITICAL CVEs | 1 | **0** |
| HIGH CVEs | 3 | **0** |
| Auth | none | **OIDC / OAuth2 / JWT / local** |
| Dep surface | minimal | **~120 plugin deps (scanned clean)** |
| Non-root UID | not enforced | **65532** |
