# gwshield-valkey v8.1.6-cluster

**Profile:** cluster — Valkey Cluster mode
**Registry:** `ghcr.io/gwshield/valkey:v8.1.6-cluster`
**Scan date:** 2026-03-13 — 0 HIGH / 0 CRITICAL CVEs

---

## Scan delta vs. upstream

| Metric | Upstream `valkey/valkey:8-alpine` | gwshield-valkey:v8.1.6-cluster |
|---|---|---|
| HIGH CVEs | varies | **0** |
| CRITICAL CVEs | varies | **0** |
| Image base | Alpine (full) | FROM scratch |
| Shell present | Yes | No |
| Cluster-mode | requires config | enabled by default |
| Listening ports | 6379 | 6379 + 16379 (cluster bus) |

> **Note on `-` scan results:** `FROM scratch` images have no OS package tree.
> Trivy and Grype show `-` — correct and expected. Binary scanned separately; 0 findings.

---

## What was done

### Cluster mode is a config-level feature

Valkey Cluster mode uses the **same binary** as the standard profile — activated by
`cluster-enabled yes` in `valkey.conf`. Same hardened build flags and static linking apply.

### Key cluster config

- `cluster-enabled yes`
- `cluster-config-file /data/nodes.conf` — auto-generated at startup
- `protected-mode no` — required for inter-node handshake in container networks

### Security note on `protected-mode no`

Must be compensated at the network layer:

- Deploy nodes within a private network (Kubernetes NetworkPolicy, Docker overlay)
- Restrict ports 6379 and 16379 to cluster-internal traffic only
- Always set `requirepass` or ACL for client authentication
- Never expose port 16379 (cluster bus) externally

### Non-root execution

Runs as UID/GID **65532** (`nonroot`).

---

## Source pins

| Component | Version | Digest |
|---|---|---|
| Valkey source | 8.1.6 | `https://github.com/valkey-io/valkey/archive/refs/tags/8.1.6.tar.gz` |
| Alpine base | 3.23 | `sha256:25109184c71bdad752c8312a8623239686a9a2071e8825f20acb8f2198c3f659` |
| Build date | 2026-03-13 | — |

---

## Delta summary

| Dimension | Upstream (valkey:8-alpine) | gwshield-valkey:v8.1.6-cluster |
|---|---|---|
| Runtime base | Alpine (full) | **scratch** |
| Shell | yes | **no** |
| Cluster-mode | requires config | **enabled by default** |
| protected-mode | yes | **no** (network controls required) |
| CRITICAL CVEs | varies | **0** |
| HIGH CVEs | varies | **0** |
| Non-root UID | not enforced | **65532** |
