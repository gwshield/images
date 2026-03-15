# Gatewarden Shield — Image Catalog

> **This file is auto-generated from `registry.json` after every promote and scan run.**
> Do not edit manually — changes will be overwritten.
> Static content and documentation live in [README.md](README.md).

*Last updated: 2026-03-15*

---

## Runtime images

Production-hardened service images. Each image is compiled from upstream source with a patched toolchain, runs from a minimal `scratch` or distroless base, and ships with a cosign signature and SBOM.

### Caddy — modern web server / reverse proxy

| Tag | Version | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|---|
| `ghcr.io/gwshield/caddy:v2.11.2` | `v2.11.2` | standard | `df49a22516ad` | 0 CVEs | 2026-03-15 |
| `ghcr.io/gwshield/caddy:v2.11.2-cloudflare` | `v2.11.2-cloudflare` | cloudflare | `df49a22516ad` | 0 CVEs | 2026-03-15 |
| `ghcr.io/gwshield/caddy:v2.11.2-crowdsec` | `v2.11.2-crowdsec` | crowdsec | `fff8b4b631e9` | 0 CVEs | 2026-03-15 |
| `ghcr.io/gwshield/caddy:v2.11.2-l4` | `v2.11.2-l4` | l4 | `b6508c5d7e64` | 0 CVEs | 2026-03-15 |
| `ghcr.io/gwshield/caddy:v2.11.2-ratelimit` | `v2.11.2-ratelimit` | ratelimit | `412ae88e2ec7` | 0 CVEs | 2026-03-15 |
| `ghcr.io/gwshield/caddy:v2.11.2-security` | `v2.11.2-security` | security | `df49a22516ad` | 0 CVEs | 2026-03-15 |

### HAProxy — high-performance TCP/HTTP load balancer

| Tag | Version | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|---|
| `ghcr.io/gwshield/haproxy:v3.1.16` | `v3.1.16` | standard | `78ddb006a52b` | 0 CVEs | 2026-03-15 |
| `ghcr.io/gwshield/haproxy:v3.1.16-ssl` | `v3.1.16-ssl` | ssl | `eec1eafc7d14` | 0 CVEs | 2026-03-15 |

### NATS — cloud-native messaging and event streaming

| Tag | Version | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|---|
| `ghcr.io/gwshield/nats:v2.12.5` | `v2.12.5` | standard | `cd70312103e5` | 0 CVEs | 2026-03-15 |

### nginx — HTTP server / reverse proxy

| Tag | Version | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|---|
| `ghcr.io/gwshield/nginx:v1.28.2` | `v1.28.2` | standard | `61abfa19bf89` | 0 CVEs | 2026-03-15 |
| `ghcr.io/gwshield/nginx:v1.28.2-http2` | `v1.28.2-http2` | HTTP/2 | `a06eea3e695a` | 0 CVEs | 2026-03-15 |
| `ghcr.io/gwshield/nginx:v1.28.2-http3` | `v1.28.2-http3` | HTTP/3 / QUIC | `1456ae4905ea` | 0 CVEs | 2026-03-15 |

### OpenTelemetry Collector — observability pipeline

| Tag | Version | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|---|
| `ghcr.io/gwshield/otelcol:v0.147.0` | `v0.147.0` | standard | `4f6aef8d90e9` | 0 CVEs | 2026-03-15 |

### Pomerium — identity-aware access proxy

| Tag | Version | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|---|
| `ghcr.io/gwshield/pomerium:v0.32.2` | `v0.32.2` | standard | `44342614f447` | 0 CVEs | 2026-03-15 |

### PostgreSQL — relational database

| Tag | Version | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|---|
| `ghcr.io/gwshield/postgres:v15.17` | `v15.17` | standard | `3e83cfac801f` | 0 CVEs | 2026-03-15 |
| `ghcr.io/gwshield/postgres:v15.17-cli` | `v15.17-cli` | client only | `3e83cfac801f` | 0 CVEs | 2026-03-15 |
| `ghcr.io/gwshield/postgres:v15.17-timescale` | `v15.17-timescale` | TimescaleDB | `3e83cfac801f` | 0 CVEs | 2026-03-15 |
| `ghcr.io/gwshield/postgres:v15.17-tls` | `v15.17-tls` | TLS | `3e83cfac801f` | 0 CVEs | 2026-03-15 |
| `ghcr.io/gwshield/postgres:v15.17-vector` | `v15.17-vector` | pgvector | `3e83cfac801f` | 0 CVEs | 2026-03-15 |
| `ghcr.io/gwshield/postgres:v17.9` | `v17.9` | standard | `3e83cfac801f` | 0 CVEs | 2026-03-15 |
| `ghcr.io/gwshield/postgres:v17.9-cli` | `v17.9-cli` | client only | `3e83cfac801f` | 0 CVEs | 2026-03-15 |
| `ghcr.io/gwshield/postgres:v17.9-timescale` | `v17.9-timescale` | TimescaleDB | `3e83cfac801f` | 0 CVEs | 2026-03-15 |
| `ghcr.io/gwshield/postgres:v17.9-tls` | `v17.9-tls` | TLS | `afc1be2f763f` | 0 CVEs | 2026-03-15 |
| `ghcr.io/gwshield/postgres:v17.9-vector` | `v17.9-vector` | pgvector | `3e83cfac801f` | 0 CVEs | 2026-03-15 |

### Redis — in-memory data store

| Tag | Version | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|---|
| `ghcr.io/gwshield/redis:v7.4.8` | `v7.4.8` | standard | `3962a7bc6e90` | 0 CVEs | 2026-03-15 |
| `ghcr.io/gwshield/redis:v7.4.8-cli` | `v7.4.8-cli` | client only | `3367ce7f3849` | 0 CVEs | 2026-03-15 |
| `ghcr.io/gwshield/redis:v7.4.8-cluster` | `v7.4.8-cluster` | cluster mode | `05d0fd9314b6` | 0 CVEs | 2026-03-15 |
| `ghcr.io/gwshield/redis:v7.4.8-tls` | `v7.4.8-tls` | TLS | `9e59c095981f` | 0 CVEs | 2026-03-15 |

### Traefik — cloud-native edge router

| Tag | Version | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|---|
| `ghcr.io/gwshield/traefik:v3.6.9` | `v3.6.9` | standard | `35f163d29af7` | 0 CVEs | 2026-03-15 |

### Valkey — open-source Redis fork

| Tag | Version | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|---|
| `ghcr.io/gwshield/valkey:v8.1.6` | `v8.1.6` | standard | `609028421b92` | 0 CVEs | 2026-03-15 |
| `ghcr.io/gwshield/valkey:v8.1.6-cli` | `v8.1.6-cli` | client only | `bb1dd3435278` | 0 CVEs | 2026-03-15 |
| `ghcr.io/gwshield/valkey:v8.1.6-cluster` | `v8.1.6-cluster` | cluster mode | `5cdf92fc5d25` | 0 CVEs | 2026-03-15 |
| `ghcr.io/gwshield/valkey:v8.1.6-tls` | `v8.1.6-tls` | TLS | `2f6e3033bd3d` | 0 CVEs | 2026-03-15 |

---

## Builder images

Secure build baseline images — published to enable reproducible, CVE-free builds in downstream multi-stage Dockerfiles. Builder images are **not** deployed as runtime containers.

```dockerfile
# Example downstream usage
FROM ghcr.io/gwshield/go-builder:v1.25 AS builder
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
| `ghcr.io/gwshield/go-builder:v1.24` | `v1.24` | standard | `5e9662410a15` | 0 CVEs | 2026-03-15 |
| `ghcr.io/gwshield/go-builder:v1.24-dev` | `v1.24-dev` | compile + test + lint | `56d6cb7f097d` | 0 CVEs | 2026-03-15 |
| `ghcr.io/gwshield/go-builder:v1.25` | `v1.25` | standard | `0840c28ffb9f` | 0 CVEs | 2026-03-15 |
| `ghcr.io/gwshield/go-builder:v1.25-dev` | `v1.25-dev` | compile + test + lint | `f07303127529` | 0 CVEs | 2026-03-15 |

### Python — reproducible wheel builds

| Tag | Version | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|---|
| `ghcr.io/gwshield/python-builder:v3.12` | `v3.12` | standard | `98f5ccda9cab` | 0 CVEs | 2026-03-15 |
| `ghcr.io/gwshield/python-builder:v3.12-dev` | `v3.12-dev` | compile + test + lint | `235c60a54f7a` | 0 CVEs | 2026-03-15 |
| `ghcr.io/gwshield/python-builder:v3.13` | `v3.13` | standard | `c3af66243f10` | 0 CVEs | 2026-03-15 |
| `ghcr.io/gwshield/python-builder:v3.13-dev` | `v3.13-dev` | compile + test + lint | `402244de375c` | 0 CVEs | 2026-03-15 |

### Rust — reproducible static musl builds

| Tag | Version | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|---|
| `ghcr.io/gwshield/rust-builder:v1.87` | `v1.87` | standard | `18339a151d75` | 0 CVEs | 2026-03-15 |
| `ghcr.io/gwshield/rust-builder:v1.87-dev` | `v1.87-dev` | compile + test + lint | `be0aff636f95` | 0 CVEs | 2026-03-15 |

---

## Verify an image

```bash
# Runtime image — pull and verify
docker pull ghcr.io/gwshield/caddy:v2.11.2
docker pull ghcr.io/gwshield/caddy@sha256:df49a22516ad6f7bb361cad3bf78a0b4d5db6ea00323232e71bbfdefd1257723

cosign verify \
  --certificate-identity-regexp='https://github.com/gwshield/images.*' \
  --certificate-oidc-issuer='https://token.actions.githubusercontent.com' \
  ghcr.io/gwshield/caddy:v2.11.2

# Builder image — pull and verify
docker pull ghcr.io/gwshield/go-builder:v1.24

cosign verify \
  --certificate-identity-regexp='https://github.com/gwshield/images.*' \
  --certificate-oidc-issuer='https://token.actions.githubusercontent.com' \
  ghcr.io/gwshield/go-builder:v1.24

# Inspect attached SBOM
cosign download sbom ghcr.io/gwshield/caddy:v2.11.2
```

---

## Cosign verify — all images

| Category | Image | Tag | Verify command |
|---|---|---|---|
| runtime | `ghcr.io/gwshield/caddy` | `v2.11.2` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/caddy:v2.11.2` |
| runtime | `ghcr.io/gwshield/caddy` | `v2.11.2-cloudflare` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/caddy:v2.11.2-cloudflare` |
| runtime | `ghcr.io/gwshield/caddy` | `v2.11.2-crowdsec` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/caddy:v2.11.2-crowdsec` |
| runtime | `ghcr.io/gwshield/caddy` | `v2.11.2-l4` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/caddy:v2.11.2-l4` |
| runtime | `ghcr.io/gwshield/caddy` | `v2.11.2-ratelimit` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/caddy:v2.11.2-ratelimit` |
| runtime | `ghcr.io/gwshield/caddy` | `v2.11.2-security` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/caddy:v2.11.2-security` |
| runtime | `ghcr.io/gwshield/haproxy` | `v3.1.16` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/haproxy:v3.1.16` |
| runtime | `ghcr.io/gwshield/haproxy` | `v3.1.16-ssl` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/haproxy:v3.1.16-ssl` |
| runtime | `ghcr.io/gwshield/nats` | `v2.12.5` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/nats:v2.12.5` |
| runtime | `ghcr.io/gwshield/nginx` | `v1.28.2` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/nginx:v1.28.2` |
| runtime | `ghcr.io/gwshield/nginx` | `v1.28.2-http2` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/nginx:v1.28.2-http2` |
| runtime | `ghcr.io/gwshield/nginx` | `v1.28.2-http3` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/nginx:v1.28.2-http3` |
| runtime | `ghcr.io/gwshield/otelcol` | `v0.147.0` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/otelcol:v0.147.0` |
| runtime | `ghcr.io/gwshield/pomerium` | `v0.32.2` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/pomerium:v0.32.2` |
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
| runtime | `ghcr.io/gwshield/valkey` | `v8.1.6` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/valkey:v8.1.6` |
| runtime | `ghcr.io/gwshield/valkey` | `v8.1.6-cli` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/valkey:v8.1.6-cli` |
| runtime | `ghcr.io/gwshield/valkey` | `v8.1.6-cluster` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/valkey:v8.1.6-cluster` |
| runtime | `ghcr.io/gwshield/valkey` | `v8.1.6-tls` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/valkey:v8.1.6-tls` |
| builder | `ghcr.io/gwshield/go-builder` | `v1.24` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/go-builder:v1.24` |
| builder | `ghcr.io/gwshield/go-builder` | `v1.24-dev` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/go-builder:v1.24-dev` |
| builder | `ghcr.io/gwshield/go-builder` | `v1.25` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/go-builder:v1.25` |
| builder | `ghcr.io/gwshield/go-builder` | `v1.25-dev` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/go-builder:v1.25-dev` |
| builder | `ghcr.io/gwshield/python-builder` | `v3.12` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/python-builder:v3.12` |
| builder | `ghcr.io/gwshield/python-builder` | `v3.12-dev` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/python-builder:v3.12-dev` |
| builder | `ghcr.io/gwshield/python-builder` | `v3.13` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/python-builder:v3.13` |
| builder | `ghcr.io/gwshield/python-builder` | `v3.13-dev` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/python-builder:v3.13-dev` |
| builder | `ghcr.io/gwshield/rust-builder` | `v1.87` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/rust-builder:v1.87` |
| builder | `ghcr.io/gwshield/rust-builder` | `v1.87-dev` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/rust-builder:v1.87-dev` |

---

Apache-2.0 — Gatewarden / RelicFrog Foundation
