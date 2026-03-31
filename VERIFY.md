# Verifying GWShield Images

All GWShield container images are signed, attested with SBOMs, and carry SLSA
provenance. This document explains how to verify these trust signals.

## Prerequisites

Install [cosign](https://docs.sigstore.dev/system_config/installation/)
(v2.0+ required):

```bash
# macOS
brew install cosign

# Linux (download binary)
curl -sL https://github.com/sigstore/cosign/releases/latest/download/cosign-linux-amd64 -o /usr/local/bin/cosign
chmod +x /usr/local/bin/cosign
```

## Signing Identity

All images are signed using **keyless signing** (Sigstore Fulcio + Rekor).
The signing identity is the GitHub Actions OIDC token from the promote
workflow:

| Field | Value |
|---|---|
| **Certificate Identity** | `https://github.com/gwshield/images/.github/workflows/promote.yml@refs/heads/main` |
| **OIDC Issuer** | `https://token.actions.githubusercontent.com` |

## 1. Verify Image Signature

```bash
# Replace <name> and <digest> with the image name and digest from registry.json
cosign verify \
  --certificate-identity='https://github.com/gwshield/images/.github/workflows/promote.yml@refs/heads/main' \
  --certificate-oidc-issuer='https://token.actions.githubusercontent.com' \
  ghcr.io/gwshield/<name>@<digest>
```

Example (postgres v15.17):

```bash
cosign verify \
  --certificate-identity='https://github.com/gwshield/images/.github/workflows/promote.yml@refs/heads/main' \
  --certificate-oidc-issuer='https://token.actions.githubusercontent.com' \
  ghcr.io/gwshield/postgres@sha256:<digest>
```

A successful verification prints the Sigstore certificate chain and returns
exit code 0.

## 2. Verify SBOM Attestation

Each image carries an SPDX SBOM attested via cosign. Verify it:

```bash
cosign verify-attestation \
  --type spdx \
  --certificate-identity='https://github.com/gwshield/images/.github/workflows/promote.yml@refs/heads/main' \
  --certificate-oidc-issuer='https://token.actions.githubusercontent.com' \
  ghcr.io/gwshield/<name>@<digest>
```

To extract the SBOM payload:

```bash
cosign verify-attestation \
  --type spdx \
  --certificate-identity='https://github.com/gwshield/images/.github/workflows/promote.yml@refs/heads/main' \
  --certificate-oidc-issuer='https://token.actions.githubusercontent.com' \
  ghcr.io/gwshield/<name>@<digest> \
  | jq -r '.payload' | base64 -d | jq '.predicate'
```

## 3. Verify SLSA Provenance

Each image carries an SLSA v1.0 provenance attestation:

```bash
cosign verify-attestation \
  --type slsaprovenance1 \
  --certificate-identity='https://github.com/gwshield/images/.github/workflows/promote.yml@refs/heads/main' \
  --certificate-oidc-issuer='https://token.actions.githubusercontent.com' \
  ghcr.io/gwshield/<name>@<digest>
```

The provenance predicate contains:
- **buildType**: `https://github.com/gwshield/images/build@v1`
- **externalParameters**: image name, version, source image, source digest
- **resolvedDependencies**: source image digest (SHA-256)
- **builder.id**: workflow identity (promote.yml)
- **invocationId**: GitHub Actions run ID

## Using registry.json for Discovery

The [`registry.json`](registry.json) file is the single source of truth for
all promoted images. Each entry contains:

| Field | Description |
|---|---|
| `digest` | OCI manifest digest (use this for all verification commands) |
| `cosign_identity` | The signing identity URL |
| `sbom_ref` | Platform-to-digest map for SBOM attestation references |
| `provenance_ref` | Platform-to-digest map for SLSA provenance references |
| `scan.status` | CVE scan result (`clean` or `findings`) |

Example: look up the digest for an image and verify it:

```bash
DIGEST=$(jq -r '.images["postgres:v15.17"].digest' registry.json)
cosign verify \
  --certificate-identity='https://github.com/gwshield/images/.github/workflows/promote.yml@refs/heads/main' \
  --certificate-oidc-issuer='https://token.actions.githubusercontent.com' \
  "ghcr.io/gwshield/postgres@${DIGEST}"
```

## Verification in CI/CD

For automated verification in your pipelines:

```yaml
# GitHub Actions example
- name: Verify GWShield image
  run: |
    cosign verify \
      --certificate-identity='https://github.com/gwshield/images/.github/workflows/promote.yml@refs/heads/main' \
      --certificate-oidc-issuer='https://token.actions.githubusercontent.com' \
      ghcr.io/gwshield/postgres@sha256:${{ env.IMAGE_DIGEST }}
```

## Trust Transparency Log

All signatures are recorded in the [Sigstore Rekor](https://rekor.sigstore.dev/)
transparency log. You can search for GWShield entries:

```bash
rekor-cli search --email "gwshield" --rekor_server https://rekor.sigstore.dev
```

## Questions or Issues

If you encounter verification failures or have questions about our supply
chain security practices, please open an issue at
[gwshield/images](https://github.com/gwshield/images/issues).
