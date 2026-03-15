# gwshield-otelcol v0.147.0

**Profile:** contrib — all receivers, processors, exporters, extensions
**Registry:** `ghcr.io/gwshield/otelcol:v0.147.0`
**Scan date:** 2026-03-14 — 0 HIGH / 0 CRITICAL CVEs

---

## Scan delta vs. upstream

| Metric | Upstream `otel/opentelemetry-collector-contrib:0.147.0` | gwshield-otelcol:v0.147.0 |
|---|---|---|
| HIGH CVEs | varies | **0** |
| CRITICAL CVEs | varies | **0** |
| Image base | Debian-based (full) | distroless/static-debian12:nonroot |
| Shell present | Yes | No |
| Package manager | Yes | No |
| Binary deps | dynamic | **fully static (0 NEEDED)** |

---

## What was done

The pre-built upstream `otelcol-contrib` static binary is downloaded and SHA256-verified
per architecture (amd64, arm64), then placed into a `distroless/static-debian12:nonroot`
runtime. No source compilation.

Binary verified: `readelf -d otelcol-contrib | grep NEEDED` → **empty output**.

### Runtime base: distroless/static-debian12:nonroot

Correct base for fully static Go binaries — no libc, no shell, no package manager.
`nonroot` user (UID 65532) pre-configured.

### Bundled config

A minimal config skeleton is bundled at `/etc/otelcol/config.yaml` enabling:
- `otlp` receiver (gRPC `:4317` + HTTP `:4318`)
- `health_check` extension (`:13133`)
- `prometheus` exporter (self-telemetry `:8888`)
- `batch` processor

Operators mount a production config via volume.

### Ports

| Port | Purpose |
|---|---|
| `:4317` | OTLP gRPC receiver |
| `:4318` | OTLP HTTP receiver |
| `:8888` | Prometheus self-telemetry |
| `:13133` | `health_check` extension |

---

## Source pins

| Component | Version | SHA256 |
|---|---|---|
| otelcol-contrib (amd64) | 0.147.0 | `17cc9a8f2e44e80ceff0e0647aec18b28a6b1b17823040e362ddc4a9fd017ccc` |
| otelcol-contrib (arm64) | 0.147.0 | `1ab4a5b12327466b7395582eb6ea0732810acb2b5e4ea9b464bd336527e85e38` |
| distroless/static-debian12:nonroot | — | `sha256:a9329520abc449e3b14d5bc3a6ffae065bdde0f02667fa10880c49b35c109fd1` |
| Build date | 2026-03-14 | — |

---

## Delta summary

| Dimension | Upstream otelcol-contrib | gwshield-otelcol:v0.147.0 |
|---|---|---|
| Runtime base | Debian-based (full) | **distroless/static-debian12:nonroot** |
| Shell | yes | **no** |
| Package manager | yes | **no** |
| Binary deps | dynamic | **fully static (0 NEEDED)** |
| CRITICAL CVEs | varies | **0** |
| HIGH CVEs | varies | **0** |
| Non-root UID | not enforced | **65532** |
