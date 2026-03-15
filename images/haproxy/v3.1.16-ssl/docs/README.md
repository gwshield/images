# gwshield-haproxy v3.1.16-ssl

**Profile:** ssl — TLS termination (TLSv1.2+), ECDHE+AEAD ciphers, HSTS
**Registry:** `ghcr.io/gwshield/haproxy:v3.1.16-ssl`
**Scan date:** 2026-03-11 — 0 HIGH / 0 CRITICAL CVEs

---

## Scan delta vs. upstream

| Metric | Upstream `haproxy:3.1-alpine` | gwshield-haproxy:v3.1.16-ssl |
|---|---|---|
| HIGH CVEs | 0 | **0** |
| CRITICAL CVEs | 0 | **0** |
| Total H/C CVEs | **0** | **0** |
| Image base | Alpine 3.x (full) | FROM scratch |
| Shell present | Yes (`/bin/ash`) | No |
| Package manager | Yes (`apk`) | No |
| TLS frontend | Not configured | TLSv1.2+ on `:8443` |

> **Note on `-` scan results:** `FROM scratch` images have no OS package tree.
> Trivy and Grype show `-` — correct and expected. The binary is scanned separately; 0 findings.

---

## What was done

### Source rebuild

The ssl profile uses the **identical binary** as the standard profile — SSL is activated
at the config level via `bind *:8443 ssl crt <pemfile>`, not by a separate compilation.

Same static linking flags as the standard profile: OpenSSL, PCRE2 (JIT), and zlib
statically linked. Only the musl libc loader is retained as a shared dependency.

### TLS hardening

| Setting | Value |
|---|---|
| Minimum TLS version | TLSv1.2 (TLS 1.0/1.1, SSLv3 disabled) |
| Cipher suites | `ECDHE+AESGCM:ECDHE+CHACHA20` (forward-secret, AEAD only) |
| TLS 1.3 ciphersuites | AES-128/256-GCM, CHACHA20-POLY1305 |
| ALPN | h2, http/1.1 |
| HSTS | `max-age=63072000; includeSubDomains; preload` (2 years) |
| Certificate | Bind-mounted PEM at runtime — not baked in |

### Certificate handling

Certificates are **not included** in the image. Supply a PEM at runtime:

```bash
cat server.crt chain.crt server.key > /run/certs/server.pem
docker run -v ./server.pem:/etc/haproxy/certs/server.pem:ro ...
```

Without a certificate the process will fail to bind `:8443` at startup.

### Non-root execution

Runs as UID/GID **65532** (`nonroot`).

---

## Known limitations

- Certificate must be bind-mounted — no default cert included.
- Lua scripting not enabled in this profile.
- mTLS (client certificate auth) not configured by default — add `verify required ca-file` to the bind directive.

---

## Source pins

| Component | Version | SHA256 |
|---|---|---|
| HAProxy source | 3.1.16 | `ef48aec8c884af4eace2669a639b57038e2bebcad22eb506d713725e9d9a445a` |
| Alpine base | 3.22 | `sha256:55ae5d250caebc548793f321534bc6a8ef1d116f334f18f4ada1b2daad3251b2` |
| Build date | 2026-03-11 | — |

---

## Delta summary

| Dimension | Upstream (haproxy:3.1-alpine) | gwshield-haproxy:v3.1.16-ssl |
|---|---|---|
| Runtime base | Alpine 3.x (full) | scratch (minimal) |
| Shell | yes | **no** |
| Package manager | yes | **no** |
| TLS frontend | not configured | **TLSv1.2+ on :8443** |
| TLS 1.0/1.1 | allowed | **disabled** |
| HSTS | no | **63072000s + preload** |
| CRITICAL CVEs | 0 | **0** |
| HIGH CVEs | 0 | **0** |
| Non-root UID | not enforced | **65532** |
