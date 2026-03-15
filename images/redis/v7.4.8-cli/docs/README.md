# gwshield-redis v7.4.8-cli

**Profile:** cli — redis-cli only, no server binary
**Registry:** `ghcr.io/gwshield/redis:v7.4.8-cli`
**Scan date:** 2026-03-01 — 0 HIGH / 0 CRITICAL CVEs

---

## Scan delta vs. upstream

| Metric | Upstream `redis:7.4.8` (Debian) | gwshield-redis:v7.4.8-cli |
|---|---|---|
| HIGH CVEs | 3 | **0** |
| CRITICAL CVEs | 41 | **0** |
| Total H/C CVEs | **44** | **0** |
| Image base | debian/bookworm-slim | FROM scratch |
| Shell present | Yes (`/bin/bash`) | No |
| gosu binary | Yes (Go 1.18.2 — 41 CVEs) | No |
| Server binary | Yes | **No** |
| Listening ports | 6379 | **None** |

### CVEs eliminated

| CVE | Severity | Component | Upstream status | Fix |
|---|---|---|---|---|
| CVE-2026-0861 | HIGH | glibc (libc6) | affected, no fix | Eliminated — musl/scratch |
| CVE-2023-45853 | CRITICAL | zlib1g | will_not_fix | Eliminated — statically linked patched zlib |
| 41 CVEs in gosu | HIGH/CRITICAL | gosu (Go 1.18.2 stdlib) | will_not_fix | Eliminated — gosu not included |

> **Note on `-` scan results:** `FROM scratch` images have no OS package tree.
> Trivy and Grype show `-` — correct and expected. The redis-cli binary is scanned
> separately as a C binary; 0 findings.

---

## What was done

### Client-only build

The full Redis v7.4.8 source is compiled but only the `redis-cli` binary is extracted
into the runtime image. `redis-server`, `redis-sentinel`, `redis-benchmark`, and
`redis-check-*` are discarded. This is a **client-only tool** — it initiates outbound
TCP connections and holds no persistent state. No inbound ports.

### Static linking

- `libm` statically linked: `LDFLAGS="-Wl,-Bstatic -lm -Wl,-Bdynamic"`
- Only musl dynamic loader retained
- Verified: `readelf -d redis-cli | grep NEEDED | grep -v musl` → empty

### Non-root execution

Runs as UID/GID **65532** (`nonroot`). No writable volumes required.

### TLS note

This build does not include TLS client support (`BUILD_TLS=no`). For TLS-encrypted
connections (e.g. against `gwshield-redis:v7.4.8-tls`), a separate `cli-tls` profile
is listed in ROADMAP.

---

## Usage

```bash
# Ad-hoc ping
docker run --rm ghcr.io/gwshield/redis:v7.4.8-cli -h <redis-host> ping

# Kubernetes ephemeral debug
kubectl debug -it <pod> \
  --image=ghcr.io/gwshield/redis:v7.4.8-cli \
  -- -h redis-service ping
```

---

## Source pins

| Component | Version | Digest |
|---|---|---|
| Redis source | 7.4.8 | `https://download.redis.io/releases/` (PGP-verified) |
| Alpine base | 3.23 | `sha256:25109184c71bdad752c8312a8623239686a9a2071e8825f20acb8f2198c3f659` |
| Build date | 2026-03-01 | — |

---

## Delta summary

| Dimension | Upstream (redis:7.4.8) | gwshield-redis:v7.4.8-cli |
|---|---|---|
| Runtime base | Debian bookworm-slim | **scratch** |
| Shell | yes | **no** |
| gosu | yes (41 CVEs) | **no** |
| Server binary | yes | **no** |
| Inbound ports | 6379 | **none** |
| CRITICAL CVEs | 41 | **0** |
| HIGH CVEs | 3 | **0** |
| Non-root UID | not enforced | **65532** |
