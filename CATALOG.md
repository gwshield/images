# Gatewarden Shield — Image Catalog

> **This file is auto-generated from `registry.json` after every promote and scan run.**
> Do not edit manually — changes will be overwritten.
> Static content and documentation live in [README.md](README.md).

*Last updated: 2026-03-16*

---

## Runtime images

Production-hardened service images. Each image is compiled from upstream source with a patched toolchain, runs from a minimal `scratch` or distroless base, and ships with a cosign signature and SBOM.

### Caddy — modern web server / reverse proxy

| Tag | Version | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|---|
| `ghcr.io/gwshield/caddy:v2.11.2` | `v2.11.2` | standard | `77fc66732d32` | 0 CVEs | 2026-03-16 |
| `ghcr.io/gwshield/caddy:v2.11.2-cloudflare` | `v2.11.2-cloudflare` | cloudflare | `8be0a07e723e` | 0 CVEs | 2026-03-16 |
| `ghcr.io/gwshield/caddy:v2.11.2-crowdsec` | `v2.11.2-crowdsec` | crowdsec | `d7ae956e9ea7` | 0 CVEs | 2026-03-16 |
| `ghcr.io/gwshield/caddy:v2.11.2-l4` | `v2.11.2-l4` | l4 | `1804e19d684c` | 0 CVEs | 2026-03-16 |
| `ghcr.io/gwshield/caddy:v2.11.2-ratelimit` | `v2.11.2-ratelimit` | ratelimit | `a04a3bae5a29` | 0 CVEs | 2026-03-16 |
| `ghcr.io/gwshield/caddy:v2.11.2-security` | `v2.11.2-security` | security | `df49a22516ad` | 0 CVEs | 2026-03-15 |

### HAProxy — high-performance TCP/HTTP load balancer

| Tag | Version | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|---|
| `ghcr.io/gwshield/haproxy:v3.1.16` | `v3.1.16` | standard | `9a9750c810dc` | 0 CVEs | 2026-03-16 |
| `ghcr.io/gwshield/haproxy:v3.1.16-ssl` | `v3.1.16-ssl` | ssl | `5a5e00ee00ca` | 0 CVEs | 2026-03-16 |

### NATS — cloud-native messaging and event streaming

| Tag | Version | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|---|
| `ghcr.io/gwshield/nats:v2.12.5` | `v2.12.5` | standard | `0adef0e21bfb` | 0 CVEs | 2026-03-16 |

### nginx — HTTP server / reverse proxy

| Tag | Version | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|---|
| `ghcr.io/gwshield/nginx:v1.28.2` | `v1.28.2` | standard | `61abfa19bf89` | 0 CVEs | 2026-03-16 |
| `ghcr.io/gwshield/nginx:v1.28.2-http2` | `v1.28.2-http2` | HTTP/2 | `a06eea3e695a` | 0 CVEs | 2026-03-16 |
| `ghcr.io/gwshield/nginx:v1.28.2-http3` | `v1.28.2-http3` | HTTP/3 / QUIC | `1456ae4905ea` | 0 CVEs | 2026-03-16 |

### OpenTelemetry Collector — observability pipeline

| Tag | Version | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|---|
| `ghcr.io/gwshield/otelcol:v0.147.0` | `v0.147.0` | standard | `4f6aef8d90e9` | 0 CVEs | 2026-03-16 |

### Pomerium — identity-aware access proxy

| Tag | Version | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|---|
| `ghcr.io/gwshield/pomerium:v0.32.2` | `v0.32.2` | standard | `8c43d150b6b0` | 0 CVEs | 2026-03-16 |

### PostgreSQL — relational database

| Tag | Version | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|---|
| `ghcr.io/gwshield/postgres:v15.17` | `v15.17` | standard | `3e0251304f00` | 0 CVEs | 2026-03-16 |
| `ghcr.io/gwshield/postgres:v15.17-cli` | `v15.17-cli` | client only | `c41994ff665d` | 0 CVEs | 2026-03-16 |
| `ghcr.io/gwshield/postgres:v15.17-timescale` | `v15.17-timescale` | TimescaleDB | `d29e835dc04a` | 0 CVEs | 2026-03-16 |
| `ghcr.io/gwshield/postgres:v15.17-tls` | `v15.17-tls` | TLS | `bbc90e9e3a9f` | 0 CVEs | 2026-03-16 |
| `ghcr.io/gwshield/postgres:v15.17-vector` | `v15.17-vector` | pgvector | `2870e464d932` | 0 CVEs | 2026-03-16 |
| `ghcr.io/gwshield/postgres:v17.9` | `v17.9` | standard | `89714cb73fed` | 0 CVEs | 2026-03-16 |
| `ghcr.io/gwshield/postgres:v17.9-cli` | `v17.9-cli` | client only | `18a83227c66d` | 0 CVEs | 2026-03-16 |
| `ghcr.io/gwshield/postgres:v17.9-timescale` | `v17.9-timescale` | TimescaleDB | `33ffdceb05f6` | 0 CVEs | 2026-03-16 |
| `ghcr.io/gwshield/postgres:v17.9-tls` | `v17.9-tls` | TLS | `e26f728ad7be` | 0 CVEs | 2026-03-16 |
| `ghcr.io/gwshield/postgres:v17.9-vector` | `v17.9-vector` | pgvector | `10ffb6c4bf1d` | 0 CVEs | 2026-03-16 |

### Redis — in-memory data store

| Tag | Version | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|---|
| `ghcr.io/gwshield/redis:v7.4.8` | `v7.4.8` | standard | `3962a7bc6e90` | 0 CVEs | 2026-03-16 |
| `ghcr.io/gwshield/redis:v7.4.8-cli` | `v7.4.8-cli` | client only | `3367ce7f3849` | 0 CVEs | 2026-03-16 |
| `ghcr.io/gwshield/redis:v7.4.8-cluster` | `v7.4.8-cluster` | cluster mode | `05d0fd9314b6` | 0 CVEs | 2026-03-16 |
| `ghcr.io/gwshield/redis:v7.4.8-tls` | `v7.4.8-tls` | TLS | `9e59c095981f` | 0 CVEs | 2026-03-16 |

### Traefik — cloud-native edge router

| Tag | Version | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|---|
| `ghcr.io/gwshield/traefik:v3.6.9` | `v3.6.9` | standard | `df8d4c9d13ae` | 0 CVEs | 2026-03-16 |

### Valkey — open-source Redis fork

| Tag | Version | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|---|
| `ghcr.io/gwshield/valkey:v8.1.6` | `v8.1.6` | standard | `609028421b92` | 0 CVEs | 2026-03-16 |
| `ghcr.io/gwshield/valkey:v8.1.6-cli` | `v8.1.6-cli` | client only | `bb1dd3435278` | 0 CVEs | 2026-03-16 |
| `ghcr.io/gwshield/valkey:v8.1.6-cluster` | `v8.1.6-cluster` | cluster mode | `5cdf92fc5d25` | 0 CVEs | 2026-03-16 |
| `ghcr.io/gwshield/valkey:v8.1.6-tls` | `v8.1.6-tls` | TLS | `2f6e3033bd3d` | 0 CVEs | 2026-03-16 |

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
| `ghcr.io/gwshield/go-builder:v1.24` | `v1.24` | standard | `07046af7bf43` | 0 CVEs | 2026-03-16 |
| `ghcr.io/gwshield/go-builder:v1.24-dev` | `v1.24-dev` | compile + test + lint | `283fbd8ba5e6` | 0 CVEs | 2026-03-16 |
| `ghcr.io/gwshield/go-builder:v1.25` | `v1.25` | standard | `edb035c7622c` | 0 CVEs | 2026-03-16 |
| `ghcr.io/gwshield/go-builder:v1.25-dev` | `v1.25-dev` | compile + test + lint | `405c28e80cb7` | 0 CVEs | 2026-03-16 |

### Python — reproducible wheel builds

| Tag | Version | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|---|
| `ghcr.io/gwshield/python-builder:v3.12` | `v3.12` | standard | `840ddf52c21f` | 0 CVEs | 2026-03-16 |
| `ghcr.io/gwshield/python-builder:v3.12-dev` | `v3.12-dev` | compile + test + lint | `7e0ee72ca1a4` | 0 CVEs | 2026-03-16 |
| `ghcr.io/gwshield/python-builder:v3.13` | `v3.13` | standard | `5f0b96670d84` | 0 CVEs | 2026-03-16 |
| `ghcr.io/gwshield/python-builder:v3.13-dev` | `v3.13-dev` | compile + test + lint | `f9b7e34203df` | 0 CVEs | 2026-03-16 |

### Rust — reproducible static musl builds

| Tag | Version | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|---|
| `ghcr.io/gwshield/rust-builder:v1.87` | `v1.87` | standard | `18339a151d75` | 0 CVEs | 2026-03-16 |
| `ghcr.io/gwshield/rust-builder:v1.87-dev` | `v1.87-dev` | compile + test + lint | `5990df4053f8` | 0 CVEs | 2026-03-16 |

---

## Verify an image

```bash
# Runtime image — pull and verify
docker pull ghcr.io/gwshield/caddy:v2.11.2
docker pull ghcr.io/gwshield/caddy@sha256:77fc66732d32724e1831b5f16173228865f8c9d08af3a465c4017f06700ddd10

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
