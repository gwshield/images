# Gatewarden Shield — Hardened Container Images

Zero-CVE, production-hardened container images and secure build baselines.
Built from source, signed with cosign, SBOM attached.

All runtime images run as non-root (UID 65532) with no shell, no package
manager, and no network utilities in the runtime layer.

> **This registry is currently in early access (alpha).** We are actively
> expanding the image catalogue and working on a dedicated landing page at
> **gwshield.io** — featuring an interactive image database, CVE delta
> comparisons, and a request form for new zero-CVE image targets.
>
> Coming soon to this repository:
> - **MCP server** — a Model Context Protocol server for querying and
>   consuming hardened image metadata directly from AI-assisted workflows
> - **Extended tooling** — signing verification helpers, SBOM diffing,
>   and policy-as-code examples
>
> Until the landing page launches, watch this repository or follow
> [@RelicFrog](https://github.com/RelicFrog) for updates.

> The source build pipeline is private. This registry is the public distribution
> endpoint. Every image is built from upstream source with SHA-256 verification,
> scanned with Trivy and Grype before promotion, and cosign-signed with a
> keyless Sigstore OIDC identity.

---

## Runtime images

Production-hardened service images. Each image is compiled from upstream source with a patched toolchain, runs from a minimal `scratch` or distroless base, and ships with a cosign signature and SBOM.

### nginx — HTTP server / reverse proxy

| Tag | Version | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|---|
| `ghcr.io/gwshield/nginx:v1.28.2` | `v1.28.2` | standard | `3bafd9e03053` | 0 CVEs | 2026-03-09 |
| `ghcr.io/gwshield/nginx:v1.28.2-http2` | `v1.28.2-http2` | HTTP/2 | `05ad1b49c5cf` | 0 CVEs | 2026-03-09 |
| `ghcr.io/gwshield/nginx:v1.28.2-http3` | `v1.28.2-http3` | HTTP/3 / QUIC | `b225f6e15c60` | 0 CVEs | 2026-03-09 |

### PostgreSQL — relational database

| Tag | Version | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|---|
| `ghcr.io/gwshield/postgres:v15.17` | `v15.17` | standard | `74ec19a9fb41` | 0 CVEs | 2026-03-09 |
| `ghcr.io/gwshield/postgres:v15.17-cli` | `v15.17-cli` | client only | `818e8af501b0` | 0 CVEs | 2026-03-09 |
| `ghcr.io/gwshield/postgres:v15.17-timescale` | `v15.17-timescale` | TimescaleDB | `699b5fc00339` | 0 CVEs | 2026-03-09 |
| `ghcr.io/gwshield/postgres:v15.17-tls` | `v15.17-tls` | TLS | `6ab602ca4ed7` | 0 CVEs | 2026-03-09 |
| `ghcr.io/gwshield/postgres:v15.17-vector` | `v15.17-vector` | pgvector | `1546a4aebcd4` | 0 CVEs | 2026-03-09 |
| `ghcr.io/gwshield/postgres:v17.9` | `v17.9` | standard | `aa97c82909d8` | 0 CVEs | 2026-03-09 |
| `ghcr.io/gwshield/postgres:v17.9-cli` | `v17.9-cli` | client only | `3ba14eaec711` | 0 CVEs | 2026-03-09 |
| `ghcr.io/gwshield/postgres:v17.9-timescale` | `v17.9-timescale` | TimescaleDB | `870a667a2a69` | 0 CVEs | 2026-03-09 |
| `ghcr.io/gwshield/postgres:v17.9-tls` | `v17.9-tls` | TLS | `1d865c97285a` | 0 CVEs | 2026-03-09 |
| `ghcr.io/gwshield/postgres:v17.9-vector` | `v17.9-vector` | pgvector | `ddfec19bc167` | 0 CVEs | 2026-03-09 |

### Redis — in-memory data store

| Tag | Version | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|---|
| `ghcr.io/gwshield/redis:v7.4.8` | `v7.4.8` | standard | `fa0246094eac` | 0 CVEs | 2026-03-09 |
| `ghcr.io/gwshield/redis:v7.4.8-cli` | `v7.4.8-cli` | client only | `12eff00273c4` | 0 CVEs | 2026-03-09 |
| `ghcr.io/gwshield/redis:v7.4.8-cluster` | `v7.4.8-cluster` | cluster mode | `00558bebcf98` | 0 CVEs | 2026-03-09 |
| `ghcr.io/gwshield/redis:v7.4.8-tls` | `v7.4.8-tls` | TLS | `56d8f5ce427d` | 0 CVEs | 2026-03-09 |

### Traefik — cloud-native edge router

| Tag | Version | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|---|
| `ghcr.io/gwshield/traefik:v3.6.9` | `v3.6.9` | standard | `5e4a68394b13` | 0 CVEs | 2026-03-09 |

---

## Builder images

Secure build baseline images — published to enable reproducible, CVE-free builds in downstream multi-stage Dockerfiles. Builder images are **not** deployed as runtime containers.

```dockerfile
# Example downstream usage
FROM ghcr.io/gwshield/go-builder:1.24 AS builder
COPY . /build/myapp
RUN go build -o /build/myapp .

FROM scratch
COPY --from=builder /build/myapp /myapp
USER 65532:65532
ENTRYPOINT ["/myapp"]
```

### Go — reproducible static builds (CGO_ENABLED=0)

| Tag | Version | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|---|
| `ghcr.io/gwshield/go-builder:v1.24` | `v1.24` | standard | `d8afeace81b7` | 0 CVEs | 2026-03-09 |
| `ghcr.io/gwshield/go-builder:v1.24-dev` | `v1.24-dev` | compile + test + lint | `c9c40de1bac8` | 0 CVEs | 2026-03-09 |

### Python — reproducible wheel builds

| Tag | Version | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|---|
| `ghcr.io/gwshield/python-builder:v3.12` | `v3.12` | standard | `4076d56bfcf1` | 0 CVEs | 2026-03-09 |
| `ghcr.io/gwshield/python-builder:v3.12-dev` | `v3.12-dev` | compile + test + lint | `85e5213c24ad` | 0 CVEs | 2026-03-09 |
| `ghcr.io/gwshield/python-builder:v3.13` | `v3.13` | standard | `12d462e5aa8a` | 0 CVEs | 2026-03-09 |
| `ghcr.io/gwshield/python-builder:v3.13-dev` | `v3.13-dev` | compile + test + lint | `b8aa19c21e07` | 0 CVEs | 2026-03-09 |

### rust-builder

| Tag | Version | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|---|
| `ghcr.io/gwshield/rust-builder:v1.87` | `v1.87` | standard | `f36d5bb4a703` | 0 CVEs | 2026-03-11 |

---

## Hardening principles

**Runtime images**
- Compiled from upstream source tarballs with SHA-256 verification
- Multi-stage builds — `FROM scratch` or distroless runtime layer
- No shell, no package manager, no `curl`/`wget` in the runtime layer
- Non-root execution: UID/GID 65532
- Hardened compiler flags: `-fstack-protector-strong`, `-D_FORTIFY_SOURCE=2`, RELRO, NOW

**Builder images**
- Digest-pinned toolchain base (golang:alpine, python:alpine, ...)
- `CGO_ENABLED=0` and `-trimpath` set by default
- Non-root execution: UID/GID 65532
- No test runners or linters in compile-only profiles
- Shell retained intentionally for downstream `RUN` steps

**All images**
- Trivy + Grype CVE scan gate — 0 unfixed HIGH/CRITICAL at release time
- cosign keyless signed (Sigstore / OIDC) — no long-lived key material
- SBOM attached to OCI manifest (CycloneDX + SPDX)

---

## Verify an image

```bash
# Runtime image — pull and verify
docker pull ghcr.io/gwshield/nginx:v1.28.2
docker pull ghcr.io/gwshield/nginx@sha256:3bafd9e03053bbcc5be2e96ed0858f25e5153dbf6a8b5a42474fe42cddd8f52f

cosign verify \
  --certificate-identity-regexp='https://github.com/gwshield/images.*' \
  --certificate-oidc-issuer='https://token.actions.githubusercontent.com' \
  ghcr.io/gwshield/nginx:v1.28.2

# Builder image — pull and verify
docker pull ghcr.io/gwshield/go-builder:v1.24

cosign verify \
  --certificate-identity-regexp='https://github.com/gwshield/images.*' \
  --certificate-oidc-issuer='https://token.actions.githubusercontent.com' \
  ghcr.io/gwshield/go-builder:v1.24

# Inspect attached SBOM
cosign download sbom ghcr.io/gwshield/nginx:v1.28.2
```

---

## Cosign verify — all images

| Category | Image | Tag | Verify command |
|---|---|---|---|
| runtime | `ghcr.io/gwshield/nginx` | `v1.28.2` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/nginx:v1.28.2` |
| runtime | `ghcr.io/gwshield/nginx` | `v1.28.2-http2` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/nginx:v1.28.2-http2` |
| runtime | `ghcr.io/gwshield/nginx` | `v1.28.2-http3` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/nginx:v1.28.2-http3` |
| runtime | `ghcr.io/gwshield/postgres` | `v15.17` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/postgres:v15.17` |
| runtime | `ghcr.io/gwshield/postgres` | `v15.17-cli` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/postgres:v15.17-cli` |
| runtime | `ghcr.io/gwshield/postgres` | `v15.17-timescale` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/postgres:v15.17-timescale` |
| runtime | `ghcr.io/gwshield/postgres` | `v15.17-tls` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/postgres:v15.17-tls` |
| runtime | `ghcr.io/gwshield/postgres` | `v15.17-vector` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/postgres:v15.17-vector` |
| runtime | `ghcr.io/gwshield/postgres` | `v17.9` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/postgres:v17.9` |
| runtime | `ghcr.io/gwshield/postgres` | `v17.9-cli` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/postgres:v17.9-cli` |
| runtime | `ghcr.io/gwshield/postgres` | `v17.9-timescale` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/postgres:v17.9-timescale` |
| runtime | `ghcr.io/gwshield/postgres` | `v17.9-tls` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/postgres:v17.9-tls` |
| runtime | `ghcr.io/gwshield/postgres` | `v17.9-vector` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/postgres:v17.9-vector` |
| runtime | `ghcr.io/gwshield/redis` | `v7.4.8` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/redis:v7.4.8` |
| runtime | `ghcr.io/gwshield/redis` | `v7.4.8-cli` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/redis:v7.4.8-cli` |
| runtime | `ghcr.io/gwshield/redis` | `v7.4.8-cluster` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/redis:v7.4.8-cluster` |
| runtime | `ghcr.io/gwshield/redis` | `v7.4.8-tls` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/redis:v7.4.8-tls` |
| runtime | `ghcr.io/gwshield/traefik` | `v3.6.9` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/traefik:v3.6.9` |
| builder | `ghcr.io/gwshield/go-builder` | `v1.24` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/go-builder:v1.24` |
| builder | `ghcr.io/gwshield/go-builder` | `v1.24-dev` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/go-builder:v1.24-dev` |
| builder | `ghcr.io/gwshield/python-builder` | `v3.12` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/python-builder:v3.12` |
| builder | `ghcr.io/gwshield/python-builder` | `v3.12-dev` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/python-builder:v3.12-dev` |
| builder | `ghcr.io/gwshield/python-builder` | `v3.13` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/python-builder:v3.13` |
| builder | `ghcr.io/gwshield/python-builder` | `v3.13-dev` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/python-builder:v3.13-dev` |
| builder | `ghcr.io/gwshield/rust-builder` | `v1.87` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/rust-builder:v1.87` |

---

## License

Apache-2.0 — Gatewarden / RelicFrog Foundation

---

*Registry last updated: 2026-03-11. This file is auto-generated — do not edit manually.*
