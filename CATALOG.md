# Gatewarden Shield — Image Catalog

> **This file is auto-generated from `registry.json` after every promote and scan run.**
> Do not edit manually — changes will be overwritten.
> Static content and documentation live in [README.md](README.md).

*Last updated: 2026-04-10*

---

## Runtime images

Production-hardened service images. Each image is compiled from upstream source with a patched toolchain, runs from a minimal `scratch` or distroless base, and ships with a cosign signature and SBOM.

### Caddy — modern web server / reverse proxy

| Tag | Version | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|---|
| `ghcr.io/gwshield/caddy:v2.11.2` | `v2.11.2` | standard | `bb9e46b38cfa` | 0 CVEs | 2026-03-31 |
| `ghcr.io/gwshield/caddy:v2.11.2-cloudflare` | `v2.11.2-cloudflare` | cloudflare | `75dc0397ec0b` | 5 findings (2 critical, 3 high) | 2026-04-10 |
| `ghcr.io/gwshield/caddy:v2.11.2-crowdsec` | `v2.11.2-crowdsec` | crowdsec | `8ec053d7ec9f` | 5 findings (2 critical, 3 high) | 2026-04-10 |
| `ghcr.io/gwshield/caddy:v2.11.2-l4` | `v2.11.2-l4` | l4 | `1e4b4cc90d74` | 5 findings (2 critical, 3 high) | 2026-04-09 |
| `ghcr.io/gwshield/caddy:v2.11.2-ratelimit` | `v2.11.2-ratelimit` | ratelimit | `9d6ab1d7fc67` | 5 findings (2 critical, 3 high) | 2026-04-09 |
| `ghcr.io/gwshield/caddy:v2.11.2-security` | `v2.11.2-security` | security | `fe9848301e73` | 6 findings (2 critical, 4 high) | 2026-04-10 |

### HAProxy — high-performance TCP/HTTP load balancer

| Tag | Version | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|---|
| `ghcr.io/gwshield/haproxy:v3.1.16` | `v3.1.16` | standard | `7ba2dd484472` | 0 CVEs | 2026-04-09 |
| `ghcr.io/gwshield/haproxy:v3.1.16-ssl` | `v3.1.16-ssl` | ssl | `8e38c056647e` | 0 CVEs | 2026-04-10 |

### NATS — cloud-native messaging and event streaming

| Tag | Version | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|---|
| `ghcr.io/gwshield/nats:v2.12.5` | `v2.12.5` | standard | `2b7212ff3de4` | 4 findings (0 critical, 4 high) | 2026-04-09 |

### nginx — HTTP server / reverse proxy

| Tag | Version | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|---|
| `ghcr.io/gwshield/nginx:v1.28.2` | `v1.28.2` | standard | `cba41fb70b71` | 0 CVEs | 2026-04-10 |
| `ghcr.io/gwshield/nginx:v1.28.2-http2` | `v1.28.2-http2` | HTTP/2 | `ea8f8ca26c67` | 0 CVEs | 2026-04-10 |
| `ghcr.io/gwshield/nginx:v1.28.2-http3` | `v1.28.2-http3` | HTTP/3 / QUIC | `9eff30ef0723` | 0 CVEs | 2026-04-10 |

### openresty

| Tag | Version | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|---|
| `ghcr.io/gwshield/openresty:v1.29.2` | `v1.29.2` | standard | `68a691fe21cf` | 10 findings (1 critical, 9 high) | 2026-04-10 |
| `ghcr.io/gwshield/openresty:v1.29.2-lua` | `v1.29.2-lua` | lua | `49e102de903a` | 8 findings (1 critical, 7 high) | 2026-04-09 |

### OpenTelemetry Collector — observability pipeline

| Tag | Version | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|---|
| `ghcr.io/gwshield/otelcol:v0.147.0` | `v0.147.0` | standard | `367bc14fc9f4` | 7 findings (1 critical, 6 high) | 2026-04-09 |

### php

| Tag | Version | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|---|
| `ghcr.io/gwshield/php:v8.2-fpm` | `v8.2-fpm` | fpm | `69db162ea72e` | 49 findings (0 critical, 49 high) | 2026-04-10 |
| `ghcr.io/gwshield/php:v8.2-fpm-dev` | `v8.2-fpm-dev` | fpm-dev | `608fb10ef834` | 50 findings (0 critical, 50 high) | 2026-04-10 |
| `ghcr.io/gwshield/php:v8.3-fpm` | `v8.3-fpm` | fpm | `e4a037f6f135` | 49 findings (0 critical, 49 high) | 2026-04-10 |
| `ghcr.io/gwshield/php:v8.3-fpm-dev` | `v8.3-fpm-dev` | fpm-dev | `3ccb73a74e48` | 49 findings (0 critical, 49 high) | 2026-04-09 |
| `ghcr.io/gwshield/php:v8.4-fpm` | `v8.4-fpm` | fpm | `518417f6e325` | 48 findings (0 critical, 48 high) | 2026-04-09 |
| `ghcr.io/gwshield/php:v8.4-fpm-dev` | `v8.4-fpm-dev` | fpm-dev | `a8196fa65737` | 50 findings (0 critical, 50 high) | 2026-04-10 |

### Pomerium — identity-aware access proxy

| Tag | Version | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|---|
| `ghcr.io/gwshield/pomerium:v0.32.2` | `v0.32.2` | standard | `cbd7807c12ef` | 9 findings (1 critical, 8 high) | 2026-04-09 |

### PostgreSQL — relational database

| Tag | Version | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|---|
| `ghcr.io/gwshield/postgres:v15.17` | `v15.17` | standard | `69e2308623ac` | 1 findings (0 critical, 1 high) | 2026-03-31 |
| `ghcr.io/gwshield/postgres:v15.17-cli` | `v15.17-cli` | client only | `5e55c47156c8` | 2 findings (0 critical, 2 high) | 2026-04-10 |
| `ghcr.io/gwshield/postgres:v15.17-timescale` | `v15.17-timescale` | TimescaleDB | `bffe38b68c1b` | 2 findings (0 critical, 2 high) | 2026-04-10 |
| `ghcr.io/gwshield/postgres:v15.17-tls` | `v15.17-tls` | TLS | `645886abb042` | 1 findings (0 critical, 1 high) | 2026-03-31 |
| `ghcr.io/gwshield/postgres:v15.17-vector` | `v15.17-vector` | pgvector | `0e3643716c64` | 2 findings (0 critical, 2 high) | 2026-04-10 |
| `ghcr.io/gwshield/postgres:v17.9` | `v17.9` | standard | `3e8071710826` | 1 findings (0 critical, 1 high) | 2026-04-09 |
| `ghcr.io/gwshield/postgres:v17.9-cli` | `v17.9-cli` | client only | `b58d35f0ea25` | 1 findings (0 critical, 1 high) | 2026-04-09 |
| `ghcr.io/gwshield/postgres:v17.9-timescale` | `v17.9-timescale` | TimescaleDB | `e1fcdc087cb7` | 2 findings (0 critical, 2 high) | 2026-04-10 |
| `ghcr.io/gwshield/postgres:v17.9-tls` | `v17.9-tls` | TLS | `cbf2b3eb040a` | 1 findings (0 critical, 1 high) | 2026-04-09 |
| `ghcr.io/gwshield/postgres:v17.9-vector` | `v17.9-vector` | pgvector | `53651c78e615` | 2 findings (0 critical, 2 high) | 2026-04-10 |
| `ghcr.io/gwshield/postgres:v18.3` | `v18.3` | standard | `07218d6e0012` | 1 findings (0 critical, 1 high) | 2026-04-09 |
| `ghcr.io/gwshield/postgres:v18.3-cli` | `v18.3-cli` | client only | `db49560c39c3` | 1 findings (0 critical, 1 high) | 2026-04-09 |
| `ghcr.io/gwshield/postgres:v18.3-timescale` | `v18.3-timescale` | TimescaleDB | `e0158bf66ddc` | 1 findings (0 critical, 1 high) | 2026-04-09 |
| `ghcr.io/gwshield/postgres:v18.3-tls` | `v18.3-tls` | TLS | `28aeb3f812c3` | 2 findings (0 critical, 2 high) | 2026-04-10 |
| `ghcr.io/gwshield/postgres:v18.3-vector` | `v18.3-vector` | pgvector | `ab713c5a5e83` | 1 findings (0 critical, 1 high) | 2026-04-09 |

### Redis — in-memory data store

| Tag | Version | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|---|
| `ghcr.io/gwshield/redis:v7.4.8` | `v7.4.8` | standard | `8fe8ad8bc206` | 0 CVEs | 2026-04-10 |
| `ghcr.io/gwshield/redis:v7.4.8-cli` | `v7.4.8-cli` | client only | `b59a2c3e88a5` | 0 CVEs | 2026-04-10 |
| `ghcr.io/gwshield/redis:v7.4.8-cluster` | `v7.4.8-cluster` | cluster mode | `7c7c26ee4866` | 0 CVEs | 2026-04-10 |
| `ghcr.io/gwshield/redis:v7.4.8-tls` | `v7.4.8-tls` | TLS | `74f6a0c644b8` | 0 CVEs | 2026-04-09 |

### Traefik — cloud-native edge router

| Tag | Version | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|---|
| `ghcr.io/gwshield/traefik:v3.6.12` | `v3.6.12` | standard | `a6cc8bb2a699` | 3 findings (0 critical, 3 high) | 2026-04-10 |
| `ghcr.io/gwshield/traefik:v3.6.9` | `v3.6.9` | standard | `b1796eab8328` | 6 findings (1 critical, 5 high) | 2026-04-09 |

### Valkey — open-source Redis fork

| Tag | Version | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|---|
| `ghcr.io/gwshield/valkey:v8.1.6` | `v8.1.6` | standard | `aeee36c5a1cf` | 0 CVEs | 2026-04-09 |
| `ghcr.io/gwshield/valkey:v8.1.6-cli` | `v8.1.6-cli` | client only | `49990b44e720` | 0 CVEs | 2026-04-09 |
| `ghcr.io/gwshield/valkey:v8.1.6-cluster` | `v8.1.6-cluster` | cluster mode | `fc6aa702e39e` | 0 CVEs | 2026-04-10 |
| `ghcr.io/gwshield/valkey:v8.1.6-tls` | `v8.1.6-tls` | TLS | `2f8058bc3706` | 0 CVEs | 2026-04-10 |

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
| `ghcr.io/gwshield/go-builder:v1.24` | `v1.24` | standard | `23dbfafe6e00` | 20 findings (0 critical, 20 high) | 2026-04-10 |
| `ghcr.io/gwshield/go-builder:v1.24-dev` | `v1.24-dev` | compile + test + lint | `ef432bfb472e` | 24 findings (0 critical, 24 high) | 2026-04-10 |
| `ghcr.io/gwshield/go-builder:v1.25` | `v1.25` | standard | `e2fcb71e62a2` | 0 CVEs | 2026-04-09 |
| `ghcr.io/gwshield/go-builder:v1.25-dev` | `v1.25-dev` | compile + test + lint | `262f1c03ce0f` | 0 CVEs | 2026-04-09 |

### Python — reproducible wheel builds

| Tag | Version | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|---|
| `ghcr.io/gwshield/python-builder:v3.12` | `v3.12` | standard | `76fe6fb309f2` | 0 CVEs | 2026-04-09 |
| `ghcr.io/gwshield/python-builder:v3.12-dev` | `v3.12-dev` | compile + test + lint | `795539e3fbe4` | 0 CVEs | 2026-04-10 |
| `ghcr.io/gwshield/python-builder:v3.13` | `v3.13` | standard | `c5dbe350c845` | 0 CVEs | 2026-04-09 |
| `ghcr.io/gwshield/python-builder:v3.13-dev` | `v3.13-dev` | compile + test + lint | `52d4fec0dc4c` | 0 CVEs | 2026-04-10 |

### Rust — reproducible static musl builds

| Tag | Version | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|---|
| `ghcr.io/gwshield/rust-builder:v1.87` | `v1.87` | standard | `650d81d06f7e` | 0 CVEs | 2026-04-09 |
| `ghcr.io/gwshield/rust-builder:v1.87-dev` | `v1.87-dev` | compile + test + lint | `a6551a6d67ef` | 0 CVEs | 2026-04-09 |

---

## Verify an image

```bash
# Runtime image — pull and verify
docker pull ghcr.io/gwshield/caddy:v2.11.2
docker pull ghcr.io/gwshield/caddy@sha256:bb9e46b38cfa2819a0acf48eb0615ba4bb924b0e33707a8bb2a880976ffe49e7

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
| runtime | `ghcr.io/gwshield/openresty` | `v1.29.2` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/openresty:v1.29.2` |
| runtime | `ghcr.io/gwshield/openresty` | `v1.29.2-lua` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/openresty:v1.29.2-lua` |
| runtime | `ghcr.io/gwshield/otelcol` | `v0.147.0` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/otelcol:v0.147.0` |
| runtime | `ghcr.io/gwshield/php` | `v8.2-fpm` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/php:v8.2-fpm` |
| runtime | `ghcr.io/gwshield/php` | `v8.2-fpm-dev` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/php:v8.2-fpm-dev` |
| runtime | `ghcr.io/gwshield/php` | `v8.3-fpm` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/php:v8.3-fpm` |
| runtime | `ghcr.io/gwshield/php` | `v8.3-fpm-dev` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/php:v8.3-fpm-dev` |
| runtime | `ghcr.io/gwshield/php` | `v8.4-fpm` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/php:v8.4-fpm` |
| runtime | `ghcr.io/gwshield/php` | `v8.4-fpm-dev` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/php:v8.4-fpm-dev` |
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
| runtime | `ghcr.io/gwshield/postgres` | `v18.3` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/postgres:v18.3` |
| runtime | `ghcr.io/gwshield/postgres` | `v18.3-cli` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/postgres:v18.3-cli` |
| runtime | `ghcr.io/gwshield/postgres` | `v18.3-timescale` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/postgres:v18.3-timescale` |
| runtime | `ghcr.io/gwshield/postgres` | `v18.3-tls` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/postgres:v18.3-tls` |
| runtime | `ghcr.io/gwshield/postgres` | `v18.3-vector` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/postgres:v18.3-vector` |
| runtime | `ghcr.io/gwshield/redis` | `v7.4.8` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/redis:v7.4.8` |
| runtime | `ghcr.io/gwshield/redis` | `v7.4.8-cli` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/redis:v7.4.8-cli` |
| runtime | `ghcr.io/gwshield/redis` | `v7.4.8-cluster` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/redis:v7.4.8-cluster` |
| runtime | `ghcr.io/gwshield/redis` | `v7.4.8-tls` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/redis:v7.4.8-tls` |
| runtime | `ghcr.io/gwshield/traefik` | `v3.6.12` | `cosign verify --certificate-identity-regexp="https://github.com/gwshield/images.*" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" ghcr.io/gwshield/traefik:v3.6.12` |
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
