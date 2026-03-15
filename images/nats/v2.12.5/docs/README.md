# gwshield-nats v2.12.5

**Profile:** standard — NATS Server with JetStream, monitoring
**Registry:** `ghcr.io/gwshield/nats:v2.12.5`
**Scan date:** 2026-03-14 — 0 HIGH / 0 CRITICAL CVEs

---

## Scan delta vs. upstream

| Metric | Upstream `nats:2.12.5` | gwshield-nats:v2.12.5 |
|---|---|---|
| HIGH CVEs | varies | **0** |
| CRITICAL CVEs | varies | **0** |
| Image base | Alpine-based | distroless/static-debian12:nonroot |
| Shell present | Yes | No |
| Package manager | Yes | No |
| Binary deps | dynamic | **fully static (0 NEEDED)** |

---

## What was done

The pre-built upstream `nats-server` static binary is downloaded and SHA256-verified
per architecture (amd64, arm64), then placed into a `distroless/static-debian12:nonroot`
runtime. No source compilation.

Binary verified: `readelf -d nats-server | grep NEEDED` → **empty output**.

### JetStream storage

JetStream persistent storage at `/data/jetstream` — pre-created, owned by UID 65532.
Mount a persistent volume here for durable streams.

### Health probing

No shell or curl in the runtime image. Use an orchestrator-level HTTP probe:

- **Kubernetes:** `httpGet` on `port: 8222`, `path: /healthz`
- **Docker / ECS:** HTTP health check on `http://localhost:8222/healthz`

### Ports

| Port | Purpose |
|---|---|
| `:4222` | Client connections (NATS protocol) |
| `:6222` | Cluster routing (inter-node) |
| `:8222` | Monitoring API (`/healthz`, `/varz`, `/connz`) |

---

## Source pins

| Component | Version | SHA256 |
|---|---|---|
| nats-server (amd64) | 2.12.5 | `f1967bea3fbf6c86273f1a2edf5be65165d795716ae1ac2a14824f19cdc35c20` |
| nats-server (arm64) | 2.12.5 | `85caf0500b011a31b105fb04992cb350236e2d5935a4d2ea7cc1efe9203aafc2` |
| distroless/static-debian12:nonroot | — | `sha256:a9329520abc449e3b14d5bc3a6ffae065bdde0f02667fa10880c49b35c109fd1` |
| Build date | 2026-03-14 | — |

---

## Delta summary

| Dimension | Upstream nats:2.12.5 | gwshield-nats:v2.12.5 |
|---|---|---|
| Runtime base | Alpine-based | **distroless/static-debian12:nonroot** |
| Shell | yes | **no** |
| Package manager | yes | **no** |
| Binary deps | dynamic | **fully static (0 NEEDED)** |
| CRITICAL CVEs | varies | **0** |
| HIGH CVEs | varies | **0** |
| Non-root UID | not enforced | **65532** |
| Health probe | internal | **orchestrator HTTP GET :8222/healthz** |
