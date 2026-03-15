# gwshield-traefik v3.6.9

**Profile:** standard — cloud-native edge router, static binary
**Registry:** `ghcr.io/gwshield/traefik:v3.6.9`
**Scan date:** 2026-02-28 — 0 effective HIGH / 0 CRITICAL CVEs

---

## Scan delta vs. upstream

| Metric | Upstream `traefik:v3.3` (Go 1.23.8) | gwshield-traefik:v3.6.9 |
|---|---|---|
| CRITICAL CVEs | 1 | **0** |
| HIGH CVEs | 8 | **0 effective** (1 scanner finding = false positive) |
| Total H/C CVEs | **9** | **0 effective** |
| Go toolchain | 1.23.8 (embedded stdlib CVEs) | 1.25.7 (all stdlib CVEs fixed) |
| Image base | Alpine 3.x (full) | FROM scratch |
| Shell present | Yes (`/bin/sh`, `/bin/ash`) | No |
| Package manager | Yes (`apk`) | No |
| Network tools | Yes (curl, wget) | No |

### CVEs eliminated

| CVE | Severity | Component | Fix |
|---|---|---|---|
| CVE-2025-68121 | CRITICAL | Go stdlib crypto/tls | Rebuilt with Go 1.25.7 |
| CVE-2025-47907 | HIGH | Go stdlib database/sql | Rebuilt with Go 1.25.7 |
| CVE-2025-58183 | HIGH | Go stdlib archive/tar | Rebuilt with Go 1.25.7 |
| CVE-2025-61726 | HIGH | Go stdlib net/url | Rebuilt with Go 1.25.7 |
| CVE-2025-61728 | HIGH | Go stdlib archive/zip | Rebuilt with Go 1.25.7 |
| CVE-2025-61729 | HIGH | Go stdlib crypto/x509 | Rebuilt with Go 1.25.7 |
| CVE-2025-61730 | HIGH | Go stdlib crypto/tls | Rebuilt with Go 1.25.7 |
| CVE-2025-59530 | HIGH | quic-go | Resolved in Traefik v3.6.9 |

### Accepted finding

| CVE | Severity | Component | Verdict |
|---|---|---|---|
| CVE-2026-24051 | HIGH | `go.opentelemetry.io/otel/sdk v1.39.0` | **False positive** — Darwin-only code path (`host_id_darwin.go`), not compiled on linux/amd64. Binary verified: `strings /traefik \| grep ioreg` → NOT FOUND. |

---

## What was done

### Source compilation

Traefik v3.6.9 compiled from the upstream tagged release using Go 1.25.7 — the latest
patch of the minor version required by Traefik's own `go.mod` (`go 1.25.0`). This is
the primary mitigation: the official Traefik image for v3.3 was compiled with Go 1.23.8,
which embedded 9 CVEs. All 7 stdlib CVEs are resolved in Go 1.25.7.

Build flags:

| Flag | Value | Purpose |
|---|---|---|
| `CGO_ENABLED` | `0` | Fully static binary; no libc runtime dependency |
| `-trimpath` | set | Strips local build paths (reproducibility) |
| `-s -w` | set | Strips debug info and DWARF; reduces binary size |

Binary verified fully static: `readelf -d traefik | grep NEEDED` → **empty output**.

### Minimal runtime (FROM scratch)

- `/traefik` — compiled static binary
- `/etc/ssl/certs/ca-certificates.crt` — TLS certificate validation
- `/usr/share/zoneinfo` — timezone data
- `/etc/passwd` and `/etc/group` — non-root user entries
- `/tmp` and `/data` declared as VOLUME

No shell, no package manager, no curl, wget, or nc.

### Non-root execution

Runs as UID/GID **65532** (`nonroot`).

### Healthcheck

`/traefik healthcheck --ping` — requires `ping.entryPoint` configured in Traefik config.

---

## Known limitations

- The admin dashboard web UI assets may be absent — the WebUI requires a Node/Yarn
  pipeline not included in this build. The API is fully functional; the static
  web assets may not render. Verify if the dashboard UI is required in your deployment.
- `go.sum` verification relies on the upstream tagged release's `go.sum` file. No
  additional module lock override is applied.

---

## Source pins

| Component | Version | SHA256 / Digest |
|---|---|---|
| Traefik source | v3.6.9 | upstream git tag (SHA verified at clone) |
| Go toolchain | `golang:1.25.7-alpine3.23` | `sha256:f6751d823c26342f9506c03797d2527668d095b0a15f1862cddb4d927a7a4ced` |
| Alpine base | 3.23 | `sha256:25109184c71bdad752c8312a8623239686a9a2071e8825f20acb8f2198c3f659` |
| Build date | 2026-02-28 | — |

---

## Delta summary

| Dimension | Upstream (traefik:v3.3) | gwshield-traefik:v3.6.9 |
|---|---|---|
| Go toolchain | 1.23.8 | **1.25.7** |
| Runtime base | Alpine 3.x (full) | **scratch** |
| Shell | yes | **no** |
| Package manager | yes | **no** |
| Binary deps | dynamic | **fully static (0 NEEDED)** |
| CRITICAL CVEs | 1 | **0** |
| HIGH CVEs | 8 | **0 effective** |
| Non-root UID | not enforced | **65532** |
