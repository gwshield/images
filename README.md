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
| `ghcr.io/gwshield/nginx:v1.28.2` | standard | `5348bb0d37c9` | not scanned | 2026-03-08 |
| `ghcr.io/gwshield/nginx:v1.28.2-http2` | HTTP/2 | `dec0436b96d9` | not scanned | 2026-03-08 |
| `ghcr.io/gwshield/nginx:v1.28.2-http3` | HTTP/3 / QUIC | `f870ede3e51a` | not scanned | 2026-03-08 |

### PostgreSQL — relational database

| Tag | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|
| `ghcr.io/gwshield/postgres:v15.17` | standard | `eefe314ee341` | not scanned | 2026-03-08 |
| `ghcr.io/gwshield/postgres:v15.17-cli` | client only | `3823337deeab` | not scanned | 2026-03-08 |
| `ghcr.io/gwshield/postgres:v15.17-timescale` | TimescaleDB | `b3132a4c71e1` | not scanned | 2026-03-08 |
| `ghcr.io/gwshield/postgres:v15.17-tls` | TLS | `55a4a8d91d4e` | not scanned | 2026-03-08 |
| `ghcr.io/gwshield/postgres:v15.17-vector` | pgvector | `aa8d023a7a18` | not scanned | 2026-03-08 |

### Redis — in-memory data store

| Tag | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|
| `ghcr.io/gwshield/redis:v7.4.8` | standard | `87fd4702bb10` | not scanned | 2026-03-08 |
| `ghcr.io/gwshield/redis:v7.4.8-cli` | client only | `406d976cdca7` | not scanned | 2026-03-08 |
| `ghcr.io/gwshield/redis:v7.4.8-cluster` | cluster mode | `422db1a57bc4` | not scanned | 2026-03-08 |
| `ghcr.io/gwshield/redis:v7.4.8-tls` | TLS | `851fe82125d9` | not scanned | 2026-03-08 |

### Traefik — cloud-native edge router

| Tag | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|
| `ghcr.io/gwshield/traefik:v3.6.9` | standard | `1324e3991c42` | not scanned | 2026-03-08 |

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
docker pull ghcr.io/gwshield/nginx@sha256:5348bb0d37c990a2fa4ae30c2a245b2709281cb31a5cbf711638da3c64b4314a

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
