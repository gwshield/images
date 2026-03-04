# Gatewarden Shield — Hardened Container Images

Zero-CVE, production-hardened container images. Built from source, signed with cosign, SBOM attached.

> **Source repository is private.** This registry is the public distribution endpoint.

---

## Images

| Image | Tags | Profile |
|---|---|---|
| `ghcr.io/gwshield/postgres` | `v15.17`, `v15.17-tls`, `v15.17-cli`, `v15.17-vector`, `v15.17-timescale` | PostgreSQL 15.17 |
| `ghcr.io/gwshield/redis` | `v7.4.8`, `v7.4.8-tls`, `v7.4.8-cluster`, `v7.4.8-cli` | Redis 7.4.8 |
| `ghcr.io/gwshield/nginx` | `v1.28.2`, `v1.28.2-http2`, `v1.28.2-http3` | nginx 1.28.2 |
| `ghcr.io/gwshield/traefik` | `v3.6.9` | Traefik 3.6.9 |

---

## Hardening principles

- Built from upstream source tarballs with SHA-256 verification
- Multi-stage builds — `FROM scratch` or `gcr.io/distroless/cc-debian12` runtime
- No shell, no package manager, no `curl`/`wget` in the runtime layer
- Non-root execution: UID/GID `65532` (nonroot)
- Hardened compiler flags: `-fstack-protector-strong`, `-D_FORTIFY_SOURCE=2`, RELRO, NOW
- Trivy CVE scan gate — 0 unfixed HIGH/CRITICAL at release time
- cosign keyless signed (Sigstore / OIDC) — no key management required
- SBOM attached to OCI manifest (CycloneDX + SPDX)

---

## Verify an image

```bash
# Pull by digest (immutable)
docker pull ghcr.io/gwshield/postgres:v15.17

# Verify cosign signature
cosign verify \
  --certificate-identity-regexp="https://github.com/RelicFrog/gwshield-images.*" \
  --certificate-oidc-issuer="https://token.actions.githubusercontent.com" \
  ghcr.io/gwshield/postgres:v15.17

# Inspect attached SBOM
cosign download sbom ghcr.io/gwshield/postgres:v15.17
```

---

## License

Apache-2.0 — © Gatewarden / RelicFrog Foundation
