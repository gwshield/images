# Gatewarden Shield — Hardened Container Images

Zero-CVE, production-hardened container images and secure build baselines.
Built from source, signed with cosign, SBOM attached.

All runtime images run as non-root (UID 65532) with no shell, no package
manager, and no network utilities in the runtime layer.

> The source build pipeline is private. This registry is the public distribution
> endpoint. Every image is built from upstream source with SHA-256 verification,
> scanned with Trivy and Grype before promotion, and cosign-signed with a
> keyless Sigstore OIDC identity.

---

## Runtime images

Production-hardened service images. Each image is compiled from upstream source with a patched toolchain, runs from a minimal `scratch` or distroless base, and ships with a cosign signature and SBOM.

### nginx — HTTP server / reverse proxy

| Tag | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|
| `ghcr.io/gwshield/nginx:v1.28.2` | standard | `98dae4d2fa5a` | 0 CVEs | 2026-03-08 |
| `ghcr.io/gwshield/nginx:v1.28.2-http2` | HTTP/2 | `81d45bb45c45` | 0 CVEs | 2026-03-08 |
| `ghcr.io/gwshield/nginx:v1.28.2-http3` | HTTP/3 / QUIC | `81feb797cc56` | 0 CVEs | 2026-03-08 |

### PostgreSQL — relational database

| Tag | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|
| `ghcr.io/gwshield/postgres:v15.17` | standard | `03f0a0643d20` | 0 CVEs | 2026-03-08 |
| `ghcr.io/gwshield/postgres:v15.17-cli` | client only | `ed61bf148637` | 0 CVEs | 2026-03-08 |
| `ghcr.io/gwshield/postgres:v15.17-timescale` | TimescaleDB | `f857ec6b3fd2` | 0 CVEs | 2026-03-08 |
| `ghcr.io/gwshield/postgres:v15.17-tls` | TLS | `27feb7118bba` | 0 CVEs | 2026-03-08 |
| `ghcr.io/gwshield/postgres:v15.17-vector` | pgvector | `734b817d53e7` | 0 CVEs | 2026-03-08 |
| `ghcr.io/gwshield/postgres:v17.9` | standard | `46da2a762797` | 0 CVEs | 2026-03-08 |
| `ghcr.io/gwshield/postgres:v17.9-cli` | client only | `1ffaf8181e32` | 0 CVEs | 2026-03-08 |
| `ghcr.io/gwshield/postgres:v17.9-timescale` | TimescaleDB | `7e808ac27833` | 0 CVEs | 2026-03-08 |
| `ghcr.io/gwshield/postgres:v17.9-tls` | TLS | `54f9bf1fbeea` | 0 CVEs | 2026-03-08 |
| `ghcr.io/gwshield/postgres:v17.9-vector` | pgvector | `d6ae1257294e` | 0 CVEs | 2026-03-08 |

### Redis — in-memory data store

| Tag | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|
| `ghcr.io/gwshield/redis:v7.4.8` | standard | `9288563afa14` | 0 CVEs | 2026-03-08 |
| `ghcr.io/gwshield/redis:v7.4.8-cli` | client only | `e1d70087c9ee` | 0 CVEs | 2026-03-08 |
| `ghcr.io/gwshield/redis:v7.4.8-cluster` | cluster mode | `6707ab218e0e` | 0 CVEs | 2026-03-08 |
| `ghcr.io/gwshield/redis:v7.4.8-tls` | TLS | `c10721015f5d` | 0 CVEs | 2026-03-08 |

### Traefik — cloud-native edge router

| Tag | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|
| `ghcr.io/gwshield/traefik:v3.6.9` | standard | `8d9c28ded370` | 0 CVEs | 2026-03-08 |

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

| Tag | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|
| `ghcr.io/gwshield/go-builder:v1.24` | standard | `3d90a0589ad0` | 0 CVEs | 2026-03-08 |
| `ghcr.io/gwshield/go-builder:v1.24-dev` | compile + test + lint | `4c17f7b9b9b9` | 0 CVEs | 2026-03-08 |

### Python — reproducible wheel builds

| Tag | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|
| `ghcr.io/gwshield/python-builder:v3.12` | standard | `180d4bf1d3ac` | 0 CVEs | 2026-03-08 |
| `ghcr.io/gwshield/python-builder:v3.12-dev` | compile + test + lint | `d3ad286b6bb1` | 0 CVEs | 2026-03-08 |
| `ghcr.io/gwshield/python-builder:v3.13` | standard | `f99463ba595f` | 0 CVEs | 2026-03-08 |
| `ghcr.io/gwshield/python-builder:v3.13-dev` | compile + test + lint | `714780de371d` | 0 CVEs | 2026-03-08 |

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
docker pull ghcr.io/gwshield/nginx@sha256:98dae4d2fa5afaa227143d9273b1614b669d10e9d439da1ca90e74219edfeca0

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

---

## License

Apache-2.0 — Gatewarden / RelicFrog Foundation

---

*Registry last updated: 2026-03-08. This file is auto-generated — do not edit manually.*
