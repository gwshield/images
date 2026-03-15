# gwshield-caddy v2.11.2-l4

**Profile:** l4 — TCP/UDP Layer-4 routing, TLS SNI routing, gRPC proxying
**Registry:** `ghcr.io/gwshield/caddy:v2.11.2-l4`
**Scan date:** 2026-03-11 — 0 HIGH / 0 CRITICAL CVEs

---

## Scan delta vs. upstream

| Metric | Upstream `caddy:2-alpine` (Go 1.26.0) | gwshield-caddy:v2.11.2-l4 |
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

Built with `xcaddy v0.4.5` (SHA-512 verified) including `caddy-l4` (mholt).
`CGO_ENABLED=0` enforced — fully static binary (0 NEEDED entries).

### Layer-4 routing capabilities

| Capability | Detail |
|---|---|
| TCP/UDP routing | Raw Layer-4 proxy without HTTP parsing |
| TLS SNI routing | Route to different upstreams based on SNI — no decryption |
| Protocol detection | Auto-detect HTTP, TLS, SSH to route appropriately |
| gRPC proxying | Native HTTP/2 + gRPC routing |
| Multiplexing | HTTPS and gRPC on the same port via SNI/protocol detection |

Configure via the top-level `layer4 { }` block in Caddyfile (not inside site blocks).

### Versioning note

`caddy-l4` does not publish versioned releases. For production deployments, pin
`PLUGIN_L4_VERSION` to a specific commit SHA in your build configuration.

---

## Source pins

| Component | Version | SHA256 / Digest |
|---|---|---|
| Caddy source | 2.11.2 | `ee12f7b5f97308708de5067deebb3d3322fc24f6d54f906a47a0a4e8db799122` |
| xcaddy | 0.4.5 (SHA-512) | `edea47d552fd9ac0a533386a72acaa95733ce734f347c11e5513469b5dc0eec0a62a6e21cfa93a83ab00b2dad72e0ee0b9bdf267a9654235f70d4c934739a15b` |
| Plugin caddy-l4 | master (commit-pinned at build) | — |
| Go toolchain | `golang:1.26.1-alpine3.22` | `sha256:07e91d24f6330432729082bb580983181809e0a48f0f38ecde26868d4568c6ac` |
| Alpine base | 3.22 | `sha256:55ae5d250caebc548793f321534bc6a8ef1d116f334f18f4ada1b2daad3251b2` |
| Build date | 2026-03-11 | — |

---

## Delta summary

| Dimension | Upstream (caddy:2-alpine) | gwshield-caddy:v2.11.2-l4 |
|---|---|---|
| Go toolchain | 1.26.0 | **1.26.1** |
| Runtime base | Alpine 3.x | **scratch** |
| Shell | yes | **no** |
| Binary deps | dynamic | **fully static (0 NEEDED)** |
| CRITICAL CVEs | 1 | **0** |
| HIGH CVEs | 3 | **0** |
| Layer-4 routing | no | **yes (TCP/UDP/SNI/gRPC)** |
| Plugin versioning | n/a | **commit-SHA pinned** |
| Non-root UID | not enforced | **65532** |
