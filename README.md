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
| `ghcr.io/gwshield/nginx:v1.28.2` | standard | `d3253cbe4107` | not scanned | 2026-03-08 |

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
docker pull ghcr.io/gwshield/nginx@sha256:d3253cbe41078a9601044ac7b138f45a779e1fc4366e3cd833269896ebd8c8ca

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

---

## License

Apache-2.0 — Gatewarden / RelicFrog Foundation

---

*Registry last updated: 2026-03-08. This file is auto-generated — do not edit manually.*
