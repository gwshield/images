# gwshield-redis v7.4.8

**Profile:** standard — single-node server
**Registry:** `ghcr.io/gwshield/redis:v7.4.8`
**Scan date:** 2026-03-01 — 0 HIGH / 0 CRITICAL CVEs

---

## Scan delta vs. upstream

| Metric | Upstream `redis:7.4.8` (Debian) | gwshield-redis:v7.4.8 |
|---|---|---|
| HIGH CVEs | 3 | **0** |
| CRITICAL CVEs | 41 | **0** |
| Total H/C CVEs | **44** | **0** |
| Image base | debian/bookworm-slim | FROM scratch |
| Shell present | Yes (`/bin/bash`) | No |
| gosu binary | Yes (Go 1.18.2 — 41 CVEs) | No |
| Lua scripting | Yes | No (disabled at compile time) |
| Listening ports | 6379 | 6379 |

### CVEs eliminated

| CVE | Severity | Component | Upstream status | Fix |
|---|---|---|---|---|
| CVE-2026-0861 | HIGH | glibc (libc6) | affected, no fix | Eliminated — musl/scratch, no glibc |
| CVE-2023-45853 | CRITICAL | zlib1g | will_not_fix | Eliminated — statically linked patched zlib |
| 41 CVEs in gosu | HIGH/CRITICAL | gosu (Go 1.18.2 stdlib) | will_not_fix | Eliminated — gosu not included |

> **Note on `-` scan results:** `FROM scratch` images have no OS package tree.
> Trivy and Grype show `-` — correct and expected. The redis-server binary is scanned
> separately as a C binary; 0 findings.

---

## What was done

### Source compilation

Redis v7.4.8 compiled from source with hardened flags:

```
-fstack-protector-strong  -D_FORTIFY_SOURCE=2  -fPIE -pie
-Wl,-z,relro,-z,now
```

### Static linking

- `libm` statically linked: `LDFLAGS="-Wl,-Bstatic -lm -Wl,-Bdynamic"`
- Only musl dynamic loader (`ld-musl-*.so.1`) retained in runtime
- Verified: `readelf -d redis-server | grep NEEDED | grep -v musl` → empty

### gosu eliminated

Non-root execution via `USER 65532:65532` — no gosu or su-exec, no Go binary
carrying 41 stdlib CVEs.

### Scripting disabled

`DISABLE_SCRIPTING=yes` at compile time — Lua/LuaJIT not compiled in.

### Minimal runtime (FROM scratch)

- `redis-server` binary
- `/lib/ld-musl-x86_64.so.1` — musl dynamic loader (only shared dep)
- `/etc/ssl/certs/ca-certificates.crt`, `/usr/share/zoneinfo`
- `/etc/passwd` and `/etc/group` — non-root user entries

No shell, no package manager, no curl, wget, or nc.

### Non-root execution

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

| Dimension | Upstream (redis:7.4.8) | gwshield-redis:v7.4.8 |
|---|---|---|
| Runtime base | Debian bookworm-slim | **scratch** |
| Shell | yes | **no** |
| gosu | yes (41 CVEs) | **no** |
| Lua scripting | yes | **no** (compile-time disabled) |
| CRITICAL CVEs | 41 | **0** |
| HIGH CVEs | 3 | **0** |
| Non-root UID | not enforced | **65532** |
