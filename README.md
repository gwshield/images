# Gatewarden Shield — Hardened Container Images

Zero-CVE, production-hardened container images and secure build baselines.
Built from source, signed with cosign, SBOM attached.

All runtime images run as non-root (UID 65532) with no shell, no package
manager, and no network utilities in the runtime layer.

→ **[Full image catalog with CVE status and digests](CATALOG.md)**

---

## What this repository is

This is the **public distribution endpoint** for the Gatewarden Shield image stack.

The build pipeline — Dockerfiles, CI workflows, scan configuration, allowlist
management, and the promotion automation — is developed privately. This repository
receives images after they have been built, scanned, and verified in that pipeline.
It is intentionally a read-only view of the output: promoted images, their digests,
CVE scan results, cosign signatures, and SBOMs.

**This is an intermediate state.** The full pipeline will be open-sourced once the
build stack reaches a stable, documented release. Until then this repository serves as:

- the canonical registry for `ghcr.io/gwshield/*` images
- the reference point for smoke tests, build patterns, and CVE transparency
- the place to request new image targets or report issues

---

## What you can do with this repository

### Pull and use images

Every image is available at `ghcr.io/gwshield/<name>:<version>`. See [CATALOG.md](CATALOG.md)
for the full list with digests and CVE status.

```bash
docker pull ghcr.io/gwshield/traefik:v3.6.9
docker pull ghcr.io/gwshield/postgres:v15.17
docker pull ghcr.io/gwshield/go-builder:v1.25
```

### Verify signatures and SBOMs

All images are cosign-signed with a keyless Sigstore OIDC identity. No long-lived key material.

```bash
cosign verify \
  --certificate-identity-regexp='https://github.com/gwshield/images.*' \
  --certificate-oidc-issuer='https://token.actions.githubusercontent.com' \
  ghcr.io/gwshield/traefik:v3.6.9

cosign download sbom ghcr.io/gwshield/traefik:v3.6.9
```

See [CATALOG.md](CATALOG.md) for the full cosign verify table across all images.

### Read and adapt smoke tests

Each image ships with a smoke test under `images/<name>/<version>/tests/smoke.sh`.
The smoke tests are the canonical reference for:

- verifying the image starts correctly
- asserting non-root execution (UID 65532)
- confirming no shell is present in the runtime layer
- checking the version string and binary reachability

You can use these as a starting point for your own validation pipelines, adapt them
to different container runtimes, or extend them with application-level checks.

### Use build patterns as reference

The multi-stage build pattern used across this stack is documented in each image's
`images/<name>/<version>/docs/public/README.md`. These cover:

- source pinning and SHA-256 verification
- static linking decisions (which libraries, why)
- runtime layer contents (exactly what is copied in)
- known limitations and rebuild triggers

The builder images (`go-builder`, `python-builder`, `rust-builder`) are designed for
direct use in downstream multi-stage Dockerfiles:

```dockerfile
FROM ghcr.io/gwshield/go-builder:v1.25 AS builder
COPY . /build/myapp
RUN go build -o /build/myapp .

FROM scratch
COPY --from=builder /build/myapp /myapp
USER 65532:65532
ENTRYPOINT ["/myapp"]
```

### Understand the CVE delta

Each image's `docs/public/README.md` contains a scan delta table showing:

- upstream image CVE count vs. hardened image CVE count
- which specific CVEs were eliminated and how
- any accepted findings with documented justification

### Request new image targets

Open an issue with the image name, version, and use case. Priority is given to
images that are commonly deployed in security-sensitive environments and have a
significant CVE surface in their upstream form.

---

## Build philosophy

### From source, from scratch — no vendor base images

Every image is compiled **directly from the upstream source tarball** (SHA-256
verified, pinned to a specific release tag). We do not start from a vendor-supplied
image and patch over it. Starting from a vendor base inherits its full CVE surface —
including vulnerabilities in compiled binaries that OS package upgrades can never reach.

The build follows a strict multi-stage pattern:

```
Stage 1 — builder (Alpine)   compile from source with hardening flags
Stage 2 — deps               /etc/passwd, CA bundle, runtime directories
Stage 3 — banner             startup shim (exec-and-disappear, see below)
Stage 4 — runtime            FROM scratch or distroless — binary only
```

### Runtime base

| Family | Runtime base | Reason |
|---|---|---|
| Traefik, Caddy | `FROM scratch` | Go + `CGO_ENABLED=0` → fully static, zero loader needed |
| nginx, Redis, Valkey, HAProxy | `FROM scratch` + musl loader | C binary, dynamically linked against musl only |
| PostgreSQL | `gcr.io/distroless/cc-debian12` | glibc dependency; distroless supplies the minimal runtime |
| Pomerium, OTel Collector, NATS | `gcr.io/distroless/static-debian12` or `cc-debian12` | Go static or embedded C++ (Envoy) |

### Static linking

Third-party libraries (OpenSSL, PCRE2, zlib, …) are linked **statically** where the
build system allows it, so they cannot be replaced at runtime and do not appear as
separate OS packages for scanners to report.

Verification: `readelf -d <binary> | grep NEEDED` — only the musl loader (C images)
or empty output (Go images) should appear.

### Specialised profiles are independent images

When a service has meaningful variants (TLS, extension sets, client-only), each variant
is a **fully independent image build** — not a layer on top of a standard image. Every
profile has its own CVE baseline, SBOM, and smoke test.

### What we deliberately do not provide

Images in this registry are **security-first, not convenience-first**:

| Feature | Status |
|---|---|
| Environment-variable driven init (`POSTGRES_PASSWORD`, …) | not provided |
| Automatic database / service initialisation on first start | not provided |
| `entrypoint.sh` wrapper with branching logic | not provided |
| Shell in runtime image | never |
| Package manager in runtime image | never |
| Root start + privilege drop | never — UID 65532 from the start |

Configuration is the operator's responsibility: mount a config file or rely on the
service binary's own environment-variable support where it exists.

### Startup shim

The only addition to every runtime image (excluding builder images) is a small C binary
(`gwshield-init`) that prints a startup banner and immediately calls `execve()` on the
service binary. After `exec()`, there is no extra process running. **PID 1 is the
service itself.** Signal handling and Kubernetes lifecycle hooks behave exactly as with
a direct entrypoint.

---

## Hardening principles

**Runtime images**
- Compiled from upstream source tarballs with SHA-256 verification
- Multi-stage builds — `FROM scratch` or distroless runtime layer
- No shell, no package manager, no `curl`/`wget` in the runtime layer
- Non-root execution: UID/GID 65532
- Hardened compiler flags: `-fstack-protector-strong`, `-D_FORTIFY_SOURCE=2`, RELRO, NOW

**Builder images**
- Digest-pinned toolchain base (golang:alpine, python:alpine, rust:alpine)
- `CGO_ENABLED=0` and `-trimpath` set by default
- Non-root execution: UID/GID 65532
- No test runners or linters in compile-only profiles
- Shell retained intentionally for downstream `RUN` steps

**All images**
- Trivy + Grype CVE scan gate — 0 unfixed HIGH/CRITICAL at release time
- cosign keyless signed (Sigstore / OIDC) — no long-lived key material
- SBOM attached to OCI manifest (CycloneDX + SPDX)

---

## Repository layout

```
images/
  <name>/<version>/
    docs/
      public/README.md   per-image CVE delta, build decisions, source pins
    tests/
      smoke.sh           smoke test (startup, non-root, no-shell, version)
CATALOG.md               auto-generated — image list, digests, CVE status
README.md                this file — static, never auto-generated
registry.json            machine-readable image metadata (auto-generated)
CHANGELOG.md             release notes
ROADMAP.md               planned targets
```

---

## License

Apache-2.0 — Gatewarden / RelicFrog Foundation
