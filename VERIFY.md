# Verifying GWShield Images

All GWShield container images are signed, attested with SBOMs, and carry SLSA
provenance. This document explains how to verify these trust signals.

## Prerequisites

Install [cosign](https://docs.sigstore.dev/system_config/installation/)
(**v3.0+ required** — signatures are stored in the cosign v3 bundle format
and are not visible to cosign v2):

```bash
# macOS
brew install cosign

# Linux (download binary)
curl -sL https://github.com/sigstore/cosign/releases/download/v3.0.5/cosign-linux-amd64 \
  -o /usr/local/bin/cosign
chmod +x /usr/local/bin/cosign
```

Verify your version: `cosign version` must show `GitVersion: v3.x.y`.

## Signing Identity

All images are signed using **keyless signing** (Sigstore Fulcio + Rekor).
The signing identity is the GitHub Actions OIDC token from the promote
workflow. Use a regexp match — images promoted after ADR-0007 Phase 1 are
signed by `promote-reusable.yml`, earlier images by `promote.yml`:

| Field | Value |
|---|---|
| **Certificate Identity (regexp)** | `.github/workflows/.*@refs/heads/main` |
| **OIDC Issuer** | `https://token.actions.githubusercontent.com` |

## 1. Verify Image Signature

Use the **index digest** from `registry.json` (the `digest` field):

```bash
# Replace <name> and <digest> with values from registry.json
cosign verify \
  --certificate-identity-regexp='.github/workflows/.*@refs/heads/main' \
  --certificate-oidc-issuer='https://token.actions.githubusercontent.com' \
  ghcr.io/gwshield/<name>@<digest>
```

Example (redis v7.4.8-cluster):

```bash
DIGEST=$(jq -r '.images["redis:v7.4.8-cluster"].digest' registry.json)
cosign verify \
  --certificate-identity-regexp='.github/workflows/.*@refs/heads/main' \
  --certificate-oidc-issuer='https://token.actions.githubusercontent.com' \
  "ghcr.io/gwshield/redis@${DIGEST}"
```

A successful verification prints the Sigstore certificate chain and returns
exit code 0.

## 2. Verify SBOM Attestation

Each image carries a per-platform SPDX JSON SBOM attested via cosign. Use the
**per-platform digest** from the `sbom_ref` map in `registry.json` (not the
index digest). SBOM attestations are stored without a Rekor tlog entry due to
payload size; pass `--insecure-ignore-tlog`:

```bash
# Get the per-platform ref from registry.json
SBOM_REF=$(jq -r '.images["redis:v7.4.8-cluster"].sbom_ref["linux/amd64"]' registry.json)

cosign verify-attestation \
  --type spdxjson \
  --insecure-ignore-tlog \
  --certificate-identity-regexp='.github/workflows/.*@refs/heads/main' \
  --certificate-oidc-issuer='https://token.actions.githubusercontent.com' \
  "${SBOM_REF}"
```

To extract the SBOM payload:

```bash
cosign verify-attestation \
  --type spdxjson \
  --insecure-ignore-tlog \
  --certificate-identity-regexp='.github/workflows/.*@refs/heads/main' \
  --certificate-oidc-issuer='https://token.actions.githubusercontent.com' \
  "${SBOM_REF}" \
  | jq -r '.payload' | base64 -d | jq '.predicate'
```

> **Note:** SBOM attestations use `--signing-config` to omit the Rekor tlog
> because SPDX JSON payloads (~700 KB) exceed Rekor's 128 KB limit. As a
> result, `--insecure-ignore-tlog` is required for external verification.
> The signing certificate is still issued by Fulcio and validated against the
> Sigstore root of trust.

## 3. Verify SLSA Provenance

Each image carries an SLSA v1.0 provenance attestation (recorded in Rekor).
Use the **per-platform digest** from the `provenance_ref` map in
`registry.json`:

```bash
PROV_REF=$(jq -r '.images["redis:v7.4.8-cluster"].provenance_ref["linux/amd64"]' registry.json)

cosign verify-attestation \
  --type slsaprovenance1 \
  --certificate-identity-regexp='.github/workflows/.*@refs/heads/main' \
  --certificate-oidc-issuer='https://token.actions.githubusercontent.com' \
  "${PROV_REF}"
```

The provenance predicate contains:
- **buildType**: `https://github.com/gwshield/images/build@v1`
- **externalParameters**: image name, version, source image, source digest
- **resolvedDependencies**: source image digest (SHA-256)
- **builder.id**: workflow identity (`promote-reusable.yml@refs/heads/main`)
- **invocationId**: GitHub Actions run ID

## Using registry.json for Discovery

The [`registry.json`](registry.json) file is the single source of truth for
all promoted images. Each entry contains:

| Field | Description |
|---|---|
| `digest` | OCI index digest — use for `cosign verify` (image signature) |
| `cosign_identity` | The signing identity URL |
| `sbom_ref` | Platform-to-digest map — use these refs for `verify-attestation --type spdxjson` |
| `provenance_ref` | Platform-to-digest map — use these refs for `verify-attestation --type slsaprovenance1` |
| `scan.status` | CVE scan result (`clean` or `findings`) |

## Verification in CI/CD

For automated verification in your pipelines:

```yaml
# GitHub Actions example
- name: Verify GWShield image
  run: |
    cosign verify \
      --certificate-identity-regexp='.github/workflows/.*@refs/heads/main' \
      --certificate-oidc-issuer='https://token.actions.githubusercontent.com' \
      ghcr.io/gwshield/postgres@sha256:${{ env.IMAGE_DIGEST }}
```

## Trust Transparency Log

Image signatures are recorded in the [Sigstore Rekor](https://rekor.sigstore.dev/)
transparency log. SLSA provenance attestations are also in Rekor. SBOM
attestations are stored only in GHCR (no tlog entry due to size).

## Questions or Issues

If you encounter verification failures or have questions about our supply
chain security practices, please open an issue at
[gwshield/images](https://github.com/gwshield/images/issues).
