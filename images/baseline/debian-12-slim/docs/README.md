# gwshield/debian:12-slim — Verified Mirror

**Type:** OS-Baseline — verified upstream mirror
**Registry:** `ghcr.io/gwshield/debian:12-slim`
**Upstream:** `docker.io/library/debian:12-slim`
**Sync:** Weekly (Monday 04:00 UTC) · cosign-signed · Trivy-scanned

> **This is not a production-hardened gwshield image.**
> It is a bit-exact, cosign-signed mirror of the upstream Debian 12-slim
> (bookworm-slim) image, published to eliminate Docker Hub rate limits in
> gwshield CI pipelines.
>
> The gwshield PostgreSQL images use `gcr.io/distroless/cc-debian12` as
> their **runtime** base — not this image. This image is the **builder**
> stage base only.

---

## Purpose

`ghcr.io/gwshield/debian:12-slim` is used as the **builder stage** base for
all PostgreSQL images (v15.17 and v17.9, all profiles) and Pomerium v0.32.2.
The glibc toolchain in Debian 12-slim is required to compile PostgreSQL and
its extensions (pg_cron, pgvector, TimescaleDB).

The **runtime** stage of these images uses `gcr.io/distroless/cc-debian12` —
a separate, minimal image that is not a mirror of this one.

### Used by (gwshield images that use this as builder stage)

`postgres:v15.17` (all 5 profiles), `postgres:v17.9` (all 5 profiles),
`pomerium:v0.32.2`

---

## What "verified mirror" means

| Property | Value |
|---|---|
| Content | Bit-exact copy of `docker.io/library/debian:12-slim` (no modifications) |
| Upstream digest preserved | Yes — `skopeo copy --all` retains original manifest digest |
| Platforms | `linux/amd64`, `linux/arm64` |
| cosign signature | Yes — keyless Sigstore OIDC, Rekor transparency log |
| SBOM attestation | Yes — syft SPDX |
| Trivy scan | Weekly CRITICAL gate |
| Supabase CVE record | Yes |

---

## What this is NOT

- Not a runtime base for production containers
- Not the same as `gcr.io/distroless/cc-debian12` (the PostgreSQL runtime base)
- Not hardened — Debian 12-slim includes apt, shell, and a full package manager

---

## Verify

```bash
cosign verify \
  --certificate-identity-regexp='https://github.com/gwshield/images.*' \
  --certificate-oidc-issuer='https://token.actions.githubusercontent.com' \
  ghcr.io/gwshield/debian:12-slim
```

---

## Source pins

| Field | Value |
|---|---|
| Upstream image | `docker.io/library/debian:12-slim` |
| Upstream digest | `sha256:74d56e3931e0d5a1dd51f8c8a2466d21de84a271cd3b5a733b803aa91abf4421` |
| Mirror target | `ghcr.io/gwshield/debian:12-slim` |
| Sync cadence | Weekly Monday 04:00 UTC |
