# gwshield-redis v7.4.8-cluster

**Profile:** cluster — Redis Cluster mode
**Registry:** `ghcr.io/gwshield/redis:v7.4.8-cluster`
**Scan date:** 2026-03-01 — 0 HIGH / 0 CRITICAL CVEs

---

## Scan delta vs. upstream

| Metric | Upstream `redis:7.4.8` (Debian) | gwshield-redis:v7.4.8-cluster |
|---|---|---|
| HIGH CVEs | 3 | **0** |
| CRITICAL CVEs | 41 | **0** |
| Total H/C CVEs | **44** | **0** |
| Image base | debian/bookworm-slim | FROM scratch |
| Shell present | Yes (`/bin/bash`) | No |
| gosu binary | Yes (Go 1.18.2 — 41 CVEs) | No |
| Cluster-mode | requires config | enabled by default |
| Listening ports | 6379 | 6379 + 16379 (cluster bus) |

### CVEs eliminated

| CVE | Severity | Component | Upstream status | Fix |
|---|---|---|---|---|
| CVE-2026-0861 | HIGH | glibc (libc6) | affected, no fix | Eliminated — musl/scratch |
| CVE-2023-45853 | CRITICAL | zlib1g | will_not_fix | Eliminated — statically linked patched zlib |
| 41 CVEs in gosu | HIGH/CRITICAL | gosu (Go 1.18.2 stdlib) | will_not_fix | Eliminated — gosu not included |

> **Note on `-` scan results:** `FROM scratch` images have no OS package tree.
> Trivy and Grype show `-` — correct and expected. The redis-server binary is scanned
> separately as a C binary; 0 findings.

---

## What was done

### Cluster mode is a config-level feature

Redis Cluster mode uses the **same binary** as the standard profile — there is no
separate compilation for cluster. The cluster is activated by `cluster-enabled yes`
in `redis.conf`. The same hardened build flags and static linking apply.

### Key cluster config

- `cluster-enabled yes`
- `cluster-config-file /data/nodes.conf` — auto-generated at startup, persisted in `/data`
- `protected-mode no` — required for inter-node handshake in container networks

### Security note on `protected-mode no`

`protected-mode yes` blocks inter-node connections — nodes cannot handshake. This setting
is intentionally `no` in this profile. This must be compensated at the network layer:

- Deploy nodes within a private network (Kubernetes NetworkPolicy, Docker overlay)
- Restrict ports 6379 and 16379 to cluster-internal traffic only
- Always set `requirepass` or ACL for client authentication
- Never expose port 16379 (cluster bus) externally

### Static linking and non-root execution

Same as the standard profile — only musl loader dynamic, `libm` static.
Runs as UID/GID **65532** (`nonroot`).

---

## Source pins

| Component | Version | Digest |
|---|---|---|
| Redis source | 7.4.8 | `https://download.redis.io/releases/` (PGP-verified) |
| Alpine base | 3.23 | `sha256:25109184c71bdad752c8312a8623239686a9a2071e8825f20acb8f2198c3f659` |
| Build date | 2026-03-01 | — |

---

## Delta summary

| Dimension | Upstream (redis:7.4.8) | gwshield-redis:v7.4.8-cluster |
|---|---|---|
| Runtime base | Debian bookworm-slim | **scratch** |
| Shell | yes | **no** |
| gosu | yes (41 CVEs) | **no** |
| Cluster-mode | requires config | **enabled by default** |
| protected-mode | yes | **no** (required — network controls compensate) |
| CRITICAL CVEs | 41 | **0** |
| HIGH CVEs | 3 | **0** |
| Non-root UID | not enforced | **65532** |
