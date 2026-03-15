# gwshield-valkey v8.1.6

**Profile:** standard — single-node server
**Registry:** `ghcr.io/gwshield/valkey:v8.1.6`
**Scan date:** 2026-03-13 — 0 HIGH / 0 CRITICAL CVEs

---

## What is Valkey

Valkey is an open-source, Linux Foundation fork of Redis 7.x. The gwshield build
follows the same hardening strategy as `gwshield-redis`: compiled from source,
statically linked, `FROM scratch` runtime, no gosu, no shell.

---

## Scan delta vs. upstream

| Metric | Upstream `valkey/valkey:8-alpine` | gwshield-valkey:v8.1.6 |
|---|---|---|
| HIGH CVEs | varies (Alpine base) | **0** |
| CRITICAL CVEs | varies | **0** |
| Image base | Alpine (full) | FROM scratch |
| Shell present | Yes | No |
| Package manager | Yes (`apk`) | No |
| gosu binary | Yes | No |
| Lua scripting | Yes | No (disabled at compile time) |
| Listening ports | 6379 | 6379 |

> **Note on `-` scan results:** `FROM scratch` images have no OS package tree.
> Trivy and Grype show `-` — correct and expected. The valkey-server binary is
> scanned separately as a C binary; 0 findings.

---

## What was done

### Source compilation

Valkey v8.1.6 compiled from the upstream source tarball
(`https://github.com/valkey-io/valkey/archive/refs/tags/8.1.6.tar.gz`).
Same hardened flags as gwshield-redis:

```
-fstack-protector-strong  -D_FORTIFY_SOURCE=2  -fPIE -pie
-Wl,-z,relro,-z,now
```

### Static linking

- `libm` statically linked: `LDFLAGS="-Wl,-Bstatic -lm -Wl,-Bdynamic"`
- Only musl dynamic loader (`ld-musl-*.so.1`) retained in runtime
- Verified: `readelf -d valkey-server | grep NEEDED | grep -v musl` → empty

### gosu eliminated

Non-root execution via `USER 65532:65532` — no gosu or su-exec.

### Scripting disabled

`DISABLE_SCRIPTING=yes` at compile time — Lua/LuaJIT not compiled in.

### Minimal runtime (FROM scratch)

- `valkey-server` binary
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
| Valkey source | 8.1.6 | `https://github.com/valkey-io/valkey/archive/refs/tags/8.1.6.tar.gz` |
| Alpine base | 3.23 | `sha256:25109184c71bdad752c8312a8623239686a9a2071e8825f20acb8f2198c3f659` |
| Build date | 2026-03-13 | — |

---

## Delta summary

| Dimension | Upstream (valkey:8-alpine) | gwshield-valkey:v8.1.6 |
|---|---|---|
| Runtime base | Alpine (full) | **scratch** |
| Shell | yes | **no** |
| Package manager | yes | **no** |
| gosu | yes | **no** |
| Lua scripting | yes | **no** (compile-time disabled) |
| CRITICAL CVEs | varies | **0** |
| HIGH CVEs | varies | **0** |
| Non-root UID | not enforced | **65532** |
