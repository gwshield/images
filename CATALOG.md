# Gatewarden Shield — Image Catalog

> **This file is auto-generated from `registry.json` after every promote and scan run.**
> Do not edit manually — changes will be overwritten.
> Static content and documentation live in [README.md](README.md).

*Last updated: 2026-04-27*

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
| `ghcr.io/gwshield/caddy:v2.11.2-security` | `v2.11.2-security` | security | `9317f0986645` | 6 findings (2 critical, 4 high) | 2026-04-10 |

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
| `ghcr.io/gwshield/nginx:v1.28.2-http2` | `v1.28.2-http2` | HTTP/2 | `8b8955d9db1b` | 0 CVEs | 2026-04-10 |
| `ghcr.io/gwshield/nginx:v1.28.2-http3` | `v1.28.2-http3` | HTTP/3 / QUIC | `40f98979c97e` | 0 CVEs | 2026-04-10 |

### openresty

| Tag | Version | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|---|
| `ghcr.io/gwshield/openresty:v1.29.2` | `v1.29.2` | standard | `0d4e932f1287` | 10 findings (1 critical, 9 high) | 2026-04-10 |
| `ghcr.io/gwshield/openresty:v1.29.2-lua` | `v1.29.2-lua` | lua | `c66c8c83f831` | 10 findings (1 critical, 9 high) | 2026-04-10 |

### OpenTelemetry Collector — observability pipeline

| Tag | Version | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|---|
| `ghcr.io/gwshield/otelcol:v0.147.0` | `v0.147.0` | standard | `221cd738a62f` | 7 findings (1 critical, 6 high) | 2026-04-10 |

### php

| Tag | Version | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|---|
| `ghcr.io/gwshield/php:v8.2-fpm` | `v8.2-fpm` | fpm | `69db162ea72e` | 49 findings (0 critical, 49 high) | 2026-04-10 |
| `ghcr.io/gwshield/php:v8.2-fpm-dev` | `v8.2-fpm-dev` | fpm-dev | `943e195170c7` | 50 findings (0 critical, 50 high) | 2026-04-10 |
| `ghcr.io/gwshield/php:v8.3-fpm` | `v8.3-fpm` | fpm | `b90ff8be21e5` | 49 findings (0 critical, 49 high) | 2026-04-10 |
| `ghcr.io/gwshield/php:v8.3-fpm-dev` | `v8.3-fpm-dev` | fpm-dev | `25dad794974d` | 0 CVEs | 2026-04-10 |
| `ghcr.io/gwshield/php:v8.4-fpm` | `v8.4-fpm` | fpm | `518417f6e325` | 48 findings (0 critical, 48 high) | 2026-04-09 |
| `ghcr.io/gwshield/php:v8.4-fpm-dev` | `v8.4-fpm-dev` | fpm-dev | `cc057f39e11b` | 1 findings (0 critical, 1 high) | 2026-04-10 |

### Pomerium — identity-aware access proxy

| Tag | Version | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|---|
| `ghcr.io/gwshield/pomerium:v0.32.2` | `v0.32.2` | standard | `e76a5232375f` | 10 findings (1 critical, 9 high) | 2026-04-10 |

### PostgreSQL — relational database

| Tag | Version | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|---|
| `ghcr.io/gwshield/postgres:v15.17` | `v15.17` | standard | `69e2308623ac` | 0 CVEs | 2026-03-31 |
| `ghcr.io/gwshield/postgres:v15.17-cli` | `v15.17-cli` | client only | `0bd48611a0da` | 2 findings (0 critical, 2 high) | 2026-04-10 |
| `ghcr.io/gwshield/postgres:v15.17-timescale` | `v15.17-timescale` | TimescaleDB | `bfddbcd11da8` | 2 findings (0 critical, 2 high) | 2026-04-10 |
| `ghcr.io/gwshield/postgres:v15.17-tls` | `v15.17-tls` | TLS | `bf273c3fd02e` | 2 findings (0 critical, 2 high) | 2026-04-10 |
| `ghcr.io/gwshield/postgres:v15.17-vector` | `v15.17-vector` | pgvector | `c52e7cb8ab4f` | 2 findings (0 critical, 2 high) | 2026-04-10 |
| `ghcr.io/gwshield/postgres:v17.9` | `v17.9` | standard | `3e8071710826` | 1 findings (0 critical, 1 high) | 2026-04-09 |
| `ghcr.io/gwshield/postgres:v17.9-cli` | `v17.9-cli` | client only | `b58d35f0ea25` | 1 findings (0 critical, 1 high) | 2026-04-09 |
| `ghcr.io/gwshield/postgres:v17.9-timescale` | `v17.9-timescale` | TimescaleDB | `e1fcdc087cb7` | 2 findings (0 critical, 2 high) | 2026-04-10 |
| `ghcr.io/gwshield/postgres:v17.9-tls` | `v17.9-tls` | TLS | `52c352ac3c91` | 2 findings (0 critical, 2 high) | 2026-04-10 |
| `ghcr.io/gwshield/postgres:v17.9-vector` | `v17.9-vector` | pgvector | `2534ec325899` | 2 findings (0 critical, 2 high) | 2026-04-10 |
| `ghcr.io/gwshield/postgres:v18.3` | `v18.3` | standard | `0a9cb0377fd9` | 5 findings (1 critical, 4 high) | 2026-04-10 |
| `ghcr.io/gwshield/postgres:v18.3-cli` | `v18.3-cli` | client only | `db49560c39c3` | 0 CVEs | 2026-04-09 |
| `ghcr.io/gwshield/postgres:v18.3-timescale` | `v18.3-timescale` | TimescaleDB | `e0158bf66ddc` | 1 findings (0 critical, 1 high) | 2026-04-09 |
| `ghcr.io/gwshield/postgres:v18.3-tls` | `v18.3-tls` | TLS | `28aeb3f812c3` | 2 findings (0 critical, 2 high) | 2026-04-10 |
| `ghcr.io/gwshield/postgres:v18.3-vector` | `v18.3-vector` | pgvector | `52a2cd0c5648` | 2 findings (0 critical, 2 high) | 2026-04-10 |

### Redis — in-memory data store

| Tag | Version | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|---|
| `ghcr.io/gwshield/redis:v7.4.8` | `v7.4.8` | standard | `8fe8ad8bc206` | 0 CVEs | 2026-04-10 |
| `ghcr.io/gwshield/redis:v7.4.8-cli` | `v7.4.8-cli` | client only | `60b54a2e85db` | 0 CVEs | 2026-04-10 |
| `ghcr.io/gwshield/redis:v7.4.8-cluster` | `v7.4.8-cluster` | cluster mode | `d8a804da5246` | 0 CVEs | 2026-04-10 |
| `ghcr.io/gwshield/redis:v7.4.8-tls` | `v7.4.8-tls` | TLS | `dd69e4c60872` | 0 CVEs | 2026-04-10 |

### Traefik — cloud-native edge router

| Tag | Version | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|---|
| `ghcr.io/gwshield/traefik:v3.6.12` | `v3.6.12` | standard | `a6cc8bb2a699` | 3 findings (0 critical, 3 high) | 2026-04-10 |
| `ghcr.io/gwshield/traefik:v3.6.9` | `v3.6.9` | standard | `b1796eab8328` | 6 findings (1 critical, 5 high) | 2026-04-09 |

### Valkey — open-source Redis fork

| Tag | Version | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|---|
| `ghcr.io/gwshield/valkey:v8.1.6` | `v8.1.6` | standard | `5794ea975b68` | 0 CVEs | 2026-04-10 |
| `ghcr.io/gwshield/valkey:v8.1.6-cli` | `v8.1.6-cli` | client only | `49990b44e720` | 0 CVEs | 2026-04-09 |
| `ghcr.io/gwshield/valkey:v8.1.6-cluster` | `v8.1.6-cluster` | cluster mode | `741040c6353d` | 0 CVEs | 2026-04-10 |
| `ghcr.io/gwshield/valkey:v8.1.6-tls` | `v8.1.6-tls` | TLS | `369651fd3b8a` | 0 CVEs | 2026-04-10 |

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
| `ghcr.io/gwshield/go-builder:v1.24` | `v1.24` | standard | `23dbfafe6e00` | 93 findings (2 critical, 91 high) | 2026-04-10 |
| `ghcr.io/gwshield/go-builder:v1.24-dev` | `v1.24-dev` | compile + test + lint | `1eaea9617b1c` | 113 findings (2 critical, 111 high) | 2026-04-10 |
| `ghcr.io/gwshield/go-builder:v1.25` | `v1.25` | standard | `d459aec10a4c` | 0 CVEs | 2026-04-10 |
| `ghcr.io/gwshield/go-builder:v1.25-dev` | `v1.25-dev` | compile + test + lint | `262f1c03ce0f` | 0 CVEs | 2026-04-09 |

### Python — reproducible wheel builds

| Tag | Version | Profile | Digest | CVE status | Promoted |
|---|---|---|---|---|---|
| `ghcr.io/gwshield/python-builder:v3.12` | `v3.12` | standard | `76fe6fb309f2` | 0 CVEs | 2026-04-09 |
| `ghcr.io/gwshield/python-builder:v3.12-dev` | `v3.12-dev` | compile + test + lint | `e28a42babf68` | 0 CVEs | 2026-04-10 |
| `ghcr.io/gwshield/python-builder:v3.13` | `v3.13` | standard | `dd93559c0ea2` | 0 CVEs | 2026-04-10 |
| `ghcr.io/gwshield/python-builder:v3.13-dev` | `v3.13-dev` | compile + test + lint | `ad4fd502f4f9` | 0 CVEs | 2026-04-10 |

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
