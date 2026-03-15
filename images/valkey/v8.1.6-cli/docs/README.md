# gwshield-valkey v8.1.6-cli

**Profile:** cli — valkey-cli only, no server binary
**Registry:** `ghcr.io/gwshield/valkey:v8.1.6-cli`
**Scan date:** 2026-03-13 — 0 HIGH / 0 CRITICAL CVEs

---

## Scan delta vs. upstream

| Metric | Upstream `valkey/valkey:8-alpine` | gwshield-valkey:v8.1.6-cli |
|---|---|---|
| HIGH CVEs | varies | **0** |
| CRITICAL CVEs | varies | **0** |
| Image base | Alpine (full) | FROM scratch |
| Shell present | Yes | No |
| Server binary | Yes | **No** |
| Listening ports | 6379 | **None** |

> **Note on `-` scan results:** `FROM scratch` images have no OS package tree.
> Trivy and Grype show `-` — correct and expected. Binary scanned separately; 0 findings.

---

## What was done

### Client-only build

The full Valkey v8.1.6 source is compiled but only the `valkey-cli` binary is extracted
into the runtime image. `valkey-server`, `valkey-sentinel`, `valkey-benchmark`, and
`valkey-check-*` are discarded. This is a **client-only tool** — initiates outbound TCP
connections, holds no persistent state, opens no inbound ports.

### Static linking

- `libm` statically linked: `LDFLAGS="-Wl,-Bstatic -lm -Wl,-Bdynamic"`
- Only musl dynamic loader retained
- Verified: `readelf -d valkey-cli | grep NEEDED | grep -v musl` → empty

### Non-root execution

Runs as UID/GID **65532** (`nonroot`). No writable volumes required.

---

## Usage

```bash
# Ad-hoc ping against a Valkey or Redis server
docker run --rm ghcr.io/gwshield/valkey:v8.1.6-cli -h <host> ping

# Kubernetes ephemeral debug
kubectl debug -it <pod> \
  --image=ghcr.io/gwshield/valkey:v8.1.6-cli \
  -- -h valkey-service ping
```

---

## Source pins

| Component | Version | Digest |
|---|---|---|
| Valkey source | 8.1.6 | `https://github.com/valkey-io/valkey/archive/refs/tags/8.1.6.tar.gz` |
| Alpine base | 3.23 | `sha256:25109184c71bdad752c8312a8623239686a9a2071e8825f20acb8f2198c3f659` |
| Build date | 2026-03-13 | — |

---

## Delta summary

| Dimension | Upstream (valkey:8-alpine) | gwshield-valkey:v8.1.6-cli |
|---|---|---|
| Runtime base | Alpine (full) | **scratch** |
| Shell | yes | **no** |
| Server binary | yes | **no** |
| Inbound ports | 6379 | **none** |
| CRITICAL CVEs | varies | **0** |
| HIGH CVEs | varies | **0** |
| Non-root UID | not enforced | **65532** |
