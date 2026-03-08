# Gatewarden Shield — Hardened Container Images

Zero-CVE, production-hardened container images. Built from source, signed with
cosign, SBOM attached. All images run as non-root (UID 65532) with no shell,
no package manager, and no network utilities in the runtime layer.

> The source build pipeline is private. This registry is the public distribution
> endpoint. Every image is built from upstream source tarballs with SHA-256
> verification, scanned with Trivy and Grype before promotion, and cosign-signed
> with a keyless Sigstore OIDC identity.

---

## Available images

### nginx — HTTP server / reverse proxy

| Tag | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|
| `ghcr.io/gwshield/nginx:v1.28.2` | standard | `98dae4d2fa5a` | not scanned | 2026-03-08 |
| `ghcr.io/gwshield/nginx:v1.28.2-http2` | HTTP/2 | `81d45bb45c45` | not scanned | 2026-03-08 |
| `ghcr.io/gwshield/nginx:v1.28.2-http3` | HTTP/3 / QUIC | `81feb797cc56` | not scanned | 2026-03-08 |

### PostgreSQL — relational database

| Tag | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|
| `ghcr.io/gwshield/postgres:v15.17` | standard | `03f0a0643d20` | not scanned | 2026-03-08 |
| `ghcr.io/gwshield/postgres:v15.17-cli` | client only | `ed61bf148637` | not scanned | 2026-03-08 |
| `ghcr.io/gwshield/postgres:v15.17-timescale` | TimescaleDB | `f857ec6b3fd2` | not scanned | 2026-03-08 |
| `ghcr.io/gwshield/postgres:v15.17-tls` | TLS | `27feb7118bba` | not scanned | 2026-03-08 |
| `ghcr.io/gwshield/postgres:v15.17-vector` | pgvector | `734b817d53e7` | not scanned | 2026-03-08 |

### Redis — in-memory data store

| Tag | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|
| `ghcr.io/gwshield/redis:v7.4.8` | standard | `9288563afa14` | not scanned | 2026-03-08 |
| `ghcr.io/gwshield/redis:v7.4.8-cli` | client only | `e1d70087c9ee` | not scanned | 2026-03-08 |
| `ghcr.io/gwshield/redis:v7.4.8-cluster` | cluster mode | `6707ab218e0e` | not scanned | 2026-03-08 |
| `ghcr.io/gwshield/redis:v7.4.8-tls` | TLS | `c10721015f5d` | not scanned | 2026-03-08 |

### Traefik — cloud-native edge router

| Tag | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|
| `ghcr.io/gwshield/traefik:v3.6.9` | standard | `8d9c28ded370` | not scanned | 2026-03-08 |

## Hardening principles

- Built from upstream source tarballs with SHA-256 verification
- Multi-stage builds — `FROM scratch` or distroless runtime layer
- No shell, no package manager, no `curl`/`wget` in the runtime layer
- Non-root execution: UID/GID 65532
- Hardened compiler flags: `-fstack-protector-strong`, `-D_FORTIFY_SOURCE=2`, RELRO, NOW
- Trivy + Grype CVE scan gate — 0 unfixed HIGH/CRITICAL findings at release time
- cosign keyless signed (Sigstore / OIDC) — no long-lived key material
- SBOM attached to OCI manifest (CycloneDX + SPDX)

---

## Verify an image

```bash
# Pull by tag
docker pull ghcr.io/gwshield/nginx:v1.28.2

# Pull by immutable digest
docker pull ghcr.io/gwshield/nginx@sha256:98dae4d2fa5afaa227143d9273b1614b669d10e9d439da1ca90e74219edfeca0

# Verify cosign signature
cosign verify \
  --certificate-identity-regexp='https://github.com/gwshield/images.*' \
  --certificate-oidc-issuer='https://token.actions.githubusercontent.com' \
  ghcr.io/gwshield/nginx:v1.28.2

# Inspect attached SBOM
cosign download sbom ghcr.io/gwshield/nginx:v1.28.2
```

---

## Cosign verify — all images

| Image | Tag | Verify command |
|---|---|---|
| `ghcr.io/gwshield/nginx` | `v1.28.2` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/nginx:v1.28.2` |
| `ghcr.io/gwshield/nginx` | `v1.28.2-http2` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/nginx:v1.28.2-http2` |
| `ghcr.io/gwshield/nginx` | `v1.28.2-http3` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/nginx:v1.28.2-http3` |
| `ghcr.io/gwshield/postgres` | `v15.17` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/postgres:v15.17` |
| `ghcr.io/gwshield/postgres` | `v15.17-cli` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/postgres:v15.17-cli` |
| `ghcr.io/gwshield/postgres` | `v15.17-timescale` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/postgres:v15.17-timescale` |
| `ghcr.io/gwshield/postgres` | `v15.17-tls` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/postgres:v15.17-tls` |
| `ghcr.io/gwshield/postgres` | `v15.17-vector` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/postgres:v15.17-vector` |
| `ghcr.io/gwshield/redis` | `v7.4.8` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/redis:v7.4.8` |
| `ghcr.io/gwshield/redis` | `v7.4.8-cli` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/redis:v7.4.8-cli` |
| `ghcr.io/gwshield/redis` | `v7.4.8-cluster` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/redis:v7.4.8-cluster` |
| `ghcr.io/gwshield/redis` | `v7.4.8-tls` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/redis:v7.4.8-tls` |
| `ghcr.io/gwshield/traefik` | `v3.6.9` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/traefik:v3.6.9` |

---

## License

Apache-2.0 — Gatewarden / RelicFrog Foundation

---

*Registry last updated: 2026-03-08. This file is auto-generated — do not edit manually.*
