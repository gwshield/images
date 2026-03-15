# gwshield/alpine:3.23 — Verified Mirror

**Type:** OS-Baseline — verified upstream mirror
**Registry:** `ghcr.io/gwshield/alpine:3.23`
**Upstream:** `docker.io/library/alpine:3.23`
**Sync:** Weekly (Monday 04:00 UTC) · cosign-signed · Trivy-scanned

> **This is not a production-hardened gwshield image.**
> It is a bit-exact, cosign-signed mirror of the upstream Alpine 3.23 image,
> published to eliminate Docker Hub rate limits in gwshield CI pipelines.
>
> For production builds use the appropriate gwshield builder or runtime image.

---

## Purpose

`ghcr.io/gwshield/alpine:3.23` is used as the build foundation for all nginx,
Redis, and Valkey gwshield images. Alpine 3.23 ships OpenSSL 3.3.x and the
compiler toolchain required for these C-source builds.

### Used by (gwshield images built from this baseline)

`nginx:v1.28.2` (all profiles), `redis:v7.4.8` (all profiles),
`valkey:v8.1.6` (all profiles)

---

## What "verified mirror" means

| Property | Value |
|---|---|
| Content | Bit-exact copy of `docker.io/library/alpine:3.23` (no modifications) |
| Upstream digest preserved | Yes — `skopeo copy --all` retains original manifest digest |
| Platforms | `linux/amd64`, `linux/arm64` |
| cosign signature | Yes — keyless Sigstore OIDC, Rekor transparency log |
| SBOM attestation | Yes — syft SPDX |
| Trivy scan | Weekly CRITICAL gate |
| Supabase CVE record | Yes |

---

## What this is NOT

- Not rebuilt from source
- Not hardened (runs as root, has shell, has apk)
- Not a replacement for production-ready gwshield images

---

## Verify

```bash
cosign verify \
  --certificate-identity-regexp='https://github.com/gwshield/images.*' \
  --certificate-oidc-issuer='https://token.actions.githubusercontent.com' \
  ghcr.io/gwshield/alpine:3.23
```

---

## Source pins

| Field | Value |
|---|---|
| Upstream image | `docker.io/library/alpine:3.23` |
| Upstream digest | `sha256:25109184c71bdad752c8312a8623239686a9a2071e8825f20acb8f2198c3f659` |
| Mirror target | `ghcr.io/gwshield/alpine:3.23` |
| Sync cadence | Weekly Monday 04:00 UTC |
