# gwshield/alpine:3.22 — Verified Mirror

**Type:** OS-Baseline — verified upstream mirror
**Registry:** `ghcr.io/gwshield/alpine:3.22`
**Upstream:** `docker.io/library/alpine:3.22`
**Sync:** Weekly (Monday 04:00 UTC) · cosign-signed · Trivy-scanned

> **This is not a production-hardened gwshield image.**
> It is a bit-exact, cosign-signed mirror of the upstream Alpine 3.22 image,
> published to eliminate Docker Hub rate limits in gwshield CI pipelines.
>
> For production builds use `ghcr.io/gwshield/go-builder:v1.25` or the
> appropriate gwshield builder image.

---

## Purpose

`ghcr.io/gwshield/alpine:3.22` is used as the build foundation for 18 gwshield
images including all Caddy profiles, HAProxy, OTel Collector, NATS Server,
and all Go/Python/Rust builder images. By mirroring Alpine into our own registry,
CI never touches Docker Hub and is not subject to pull rate limits.

### Used by (gwshield images built from this baseline)

`go-builder:v1.24`, `go-builder:v1.25`, `python-builder:v3.12`, `python-builder:v3.12-dev`,
`python-builder:v3.13`, `python-builder:v3.13-dev`, `rust-builder:v1.87`,
`caddy:v2.11.2` (all profiles), `haproxy:v3.1.16` (both profiles),
`nats:v2.12.5`, `otelcol:v0.147.0`, `pomerium:v0.32.2`

---

## What "verified mirror" means

| Property | Value |
|---|---|
| Content | Bit-exact copy of `docker.io/library/alpine:3.22` (no modifications) |
| Upstream digest preserved | Yes — `skopeo copy --all` retains original manifest digest |
| Platforms | `linux/amd64`, `linux/arm64` |
| cosign signature | Yes — keyless Sigstore OIDC, Rekor transparency log |
| SBOM attestation | Yes — syft SPDX |
| Trivy scan | Weekly CRITICAL gate — sync blocked if new CRITICAL found |
| Supabase CVE record | Yes — scan results visible in Hub |

---

## What this is NOT

- Not rebuilt from source
- Not hardened (runs as root, has shell, has apk)
- Not suitable as a production container base without additional hardening
- Not a replacement for `ghcr.io/gwshield/go-builder:v1.25` or similar

---

## Verify

```bash
cosign verify \
  --certificate-identity-regexp='https://github.com/gwshield/images.*' \
  --certificate-oidc-issuer='https://token.actions.githubusercontent.com' \
  ghcr.io/gwshield/alpine:3.22
```

---

## Source pins

| Field | Value |
|---|---|
| Upstream image | `docker.io/library/alpine:3.22` |
| Upstream digest | `sha256:55ae5d250caebc548793f321534bc6a8ef1d116f334f18f4ada1b2daad3251b2` |
| Mirror target | `ghcr.io/gwshield/alpine:3.22` |
| Sync cadence | Weekly Monday 04:00 UTC |
