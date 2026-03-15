# gwshield-pomerium v0.32.2

**Profile:** standard — Identity-Aware Proxy, Zero-Trust, all-in-one binary
**Registry:** `ghcr.io/gwshield/pomerium:v0.32.2`
**Scan date:** 2026-03-14 — 0 HIGH / 0 CRITICAL CVEs

---

## Scan delta vs. upstream

| Metric | Upstream `pomerium/pomerium:v0.32.2` | gwshield-pomerium:v0.32.2 |
|---|---|---|
| HIGH CVEs | varies | **0** |
| CRITICAL CVEs | varies | **0** |
| Image base | ubuntu-based | distroless/cc-debian12 |
| Shell present | Yes | No |
| Package manager | Yes | No |
| Go toolchain | upstream | 1.26.1 (stdlib CVEs patched) |
| Binary deps | dynamic | **fully static (0 NEEDED)** |

---

## What was done

### Source compilation

Pomerium v0.32.2 compiled from source with `CGO_ENABLED=0` and Go 1.26.1.
The build requires a Node.js stage to compile the embedded admin UI (React/TypeScript SPA)
before the Go build — the UI assets are embedded via `go:embed`.

`-ldflags` set version strings to produce correct `pomerium --version` output.

Binary verified fully static: `readelf -d pomerium | grep NEEDED` → **empty output**.

### Embedded Envoy

Pomerium embeds `pomerium/envoy-custom v1.37.0-rc3` (statically linked C++) via `go:embed`.
Envoy is extracted to `/tmp` at startup — `/tmp` must be writable.

### Runtime base: distroless/cc-debian12

`distroless/cc-debian12` is used instead of scratch because Envoy requires a writable `/tmp`.
The `cc` variant provides glibc stubs without adding a shell or package manager.

### Architecture

| Component | Role |
|---|---|
| Proxy | Receives requests, enforces authn/authz |
| Authenticate | OIDC/OAuth2 flow, IdP redirect handling |
| Authorize | Policy evaluation |
| Databroker | Session + user data store |

### Ports

| Port | Purpose |
|---|---|
| `:443` | HTTPS proxy (clients) |
| `:5443` | gRPC internal (authorize/databroker) |
| `127.0.0.1:28080` | Health check |

### Runtime requirements

- `/tmp` must be writable (Docker `--tmpfs /tmp` or Kubernetes `emptyDir`)
- `/pomerium/config.yaml` must be mounted with valid IdP credentials
- `/data/autocert` must be writable if `autocert: true` is set

---

## Source pins

| Component | Version | SHA256 / Digest |
|---|---|---|
| Pomerium source | 0.32.2 | `66c07457aa6d60cb5dc008dd415e2d6bfc6fe2a52918b5d9cacc4cd59d9ed2f8` |
| Go toolchain | `golang:1.26.1-bookworm` | `sha256:c7a82e9e2df2fea5d8cb62a16aa6f796d2b2ed81ccad4ddd2bc9f0d22936c3f2` |
| Node (UI build) | `node:22.22.1-bookworm-slim` | `sha256:9c2c405e3ff9b9afb2873232d24bb06367d649aa3e6259cbe314da59578e81e9` |
| distroless/cc-debian12 | — | `sha256:8837fd0a981b9d3922e8d9e55dd6340525346bbf894f7f4614b125bdb62c2aa2` |
| Envoy (embedded) | v1.37.0-rc3 | amd64: `88f132d3...` · arm64: `1b6f188f...` |
| Build date | 2026-03-14 | — |

---

## Delta summary

| Dimension | Upstream pomerium | gwshield-pomerium:v0.32.2 |
|---|---|---|
| Go toolchain | upstream | **1.26.1** |
| Runtime base | ubuntu-based | **distroless/cc-debian12** |
| Shell | yes | **no** |
| Package manager | yes | **no** |
| Binary deps | dynamic | **fully static (0 NEEDED)** |
| CRITICAL CVEs | varies | **0** |
| HIGH CVEs | varies | **0** |
| Non-root UID | not enforced | **65532** |
| Zero-Trust | configurable | **enforced — all traffic requires IdP authn** |
