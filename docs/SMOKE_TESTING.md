# Smoke Testing

Every GWShield image ships with a smoke test that validates the image starts
correctly, runs as the expected user, and meets the hardening baseline before
it is promoted to the public registry.

This document describes how the smoke tests work, what they check, and how to
run them against your own pulled images.

---

## What a smoke test covers

A smoke test is not an integration test or a load test. It is a fast, binary
gate that answers one question: **does this image satisfy the GWShield hardening
contract?**

Each smoke test produces a structured JSON result (`smoke-result.json`) that
feeds directly into the GWShield Hub for badge rendering and audit history.

---

## Trinity-Layer Architecture

Smoke tests follow a three-layer model. Each layer increases in specificity and
decreases in reuse.

### Layer 1 -- Standard Checks

These checks apply to **every** GWShield image. They are determined by the
image's runtime type and are identical across all images of that type.

| Check | What it verifies | scratch | distroless | debian | builder |
|---|---|---|---|---|---|
| **banner** | gwshield-init startup shim is present | yes | yes | yes | -- |
| **binary_present** | service binary exists at declared path | yes | yes | yes | yes |
| **version_string** | `--gws-version` output matches expected pattern | yes | yes | yes | yes |
| **nonroot** | container runs as UID 65532 | yes | yes | yes | yes |
| **no_shell** | `/bin/sh` is not executable | yes | yes | -- | -- |
| **no_curl** | `curl` and `wget` are absent | -- | -- | yes | yes |

Scratch and distroless images have **no shell** -- this is verified as a
security property. Debian and builder images retain a shell for operational
reasons but must not ship network download tools.

Checks marked `--` are not applicable to that runtime type and are not run.

### Layer 2 -- Service-Type Checks

These checks are specific to the kind of service the image provides. A web
server has different functional requirements than a database or a key-value
store.

| Service Type | Checks | Examples |
|---|---|---|
| **web-server** | config_validate, health_endpoint | caddy, nginx, openresty, haproxy, traefik |
| **database** | db_connect, extension_present | postgres (all versions and profiles) |
| **kv-store** | ping_response, set_get_roundtrip, dangerous_cmd_blocked | redis, valkey |
| **messaging** | health_endpoint, data_dir_present | nats |
| **collector** | health_endpoint, config_present | otelcol |
| **builder** | toolchain_version, compile_hello_world, linter_present | go-builder, python-builder, rust-builder |

Each check has a structured parameter set. For example, a health endpoint check
specifies the URL and the expected response body:

```
health_endpoint:
  url: http://localhost:18081/healthz
  expect_body: "ok"
```

A database connectivity check specifies the tool, connection arguments, and the
sidecar it connects to:

```
db_connect:
  tool: /usr/local/bin/pg_isready
  args: ["-h", "upstream-pg", "-U", "smoke"]
  sidecar: upstream-pg
```

### Layer 3 -- Custom Checks

Some images have unique requirements that do not fit into a standard check type.
These are expressed as inline test logic that sets a pass/fail result and a
human-readable detail string.

For example, OpenResty has a LuaJIT functional test that hits a Lua content
endpoint:

```
lua_functional:
  Verifies that GET /lua-check returns "lua:ok" from a content_by_lua_block.
  This confirms the LuaJIT runtime is loaded and the nginx config routes
  to Lua correctly.
```

Custom checks have access to the same test infrastructure as standard checks
(the running container, the Docker network, all helper functions) but their
logic is specific to the individual image.

---

## What the checks mean

### Security checks

| Check | Why it matters |
|---|---|
| **banner** | The gwshield-init startup shim proves the image was built through the GWShield pipeline. It prints a banner, then `exec()`s the service binary. After exec, PID 1 is the service itself -- no extra process. |
| **nonroot** | UID 65532 from the start. No root start with privilege drop. No `su` or `gosu`. The container process is never root. |
| **no_shell** | A shell in a runtime image enables arbitrary command execution if the container is compromised. Scratch and distroless images must not have one. |
| **no_curl** | Network download tools (curl, wget, nc) in a runtime image enable exfiltration. Even images with a shell (Debian, builder) must not ship them. |

### Integrity checks

| Check | Why it matters |
|---|---|
| **binary_present** | The service binary must exist at the declared path. A missing binary means a broken build -- the multi-stage COPY failed. |
| **version_string** | `--gws-version` must report the correct version. A mismatch means the wrong source was compiled or the wrong binary was copied into the runtime layer. |
| **static_binary** | Go binaries with `CGO_ENABLED=0` must have zero dynamic dependencies. Any NEEDED entry in `readelf` output means the binary was incorrectly linked. |
| **ca_bundle** | TLS clients need `/etc/ssl/certs/ca-certificates.crt`. Missing CA bundle breaks HTTPS connections. |

### Functional checks

| Check | Why it matters |
|---|---|
| **health_endpoint** | The service must start and respond to a health probe. Failure means the bundled configuration is broken or the binary crashes on startup. |
| **config_validate** | `nginx -t`, `caddy validate`, `haproxy -c` -- the service's own config checker must accept the bundled default configuration. |
| **db_connect** | `pg_isready` from the hardened image must connect to an upstream database. Failure means client libraries or pg_hba.conf are misconfigured. |
| **ping_response** | Redis and Valkey must respond to PING with PONG. Basic smoke for the in-memory engine. |

---

## How to run smoke tests

Every image has a smoke test at `images/<name>/<version>/tests/smoke.sh`.

### Prerequisites

- Docker (or compatible runtime)
- bash 4+
- curl (on the host, for HTTP probes)
- python3 (for structured JSON output)

### Pull and test

```bash
# Pull the image
docker pull ghcr.io/gwshield/caddy:v2.11.2

# Tag it for the smoke test (the script expects a local tag)
docker tag ghcr.io/gwshield/caddy:v2.11.2 gwshield/caddy:smoke-test

# Run the smoke test
bash images/caddy/v2.11.2/tests/smoke.sh gwshield/caddy:smoke-test
```

### Output

Console output shows each check result:

```
[PASS] gwshield-init banner present                      /usr/local/bin/gwshield-init
[PASS] service binary present at declared path           /usr/bin/caddy
[PASS] version string correct                            got: v2.11.2 ...
[PASS] runs as non-root UID 65532                        uid=65532
[PASS] no shell in runtime layer                         entrypoint /bin/sh blocked
[PASS] static binary (zero NEEDED entries)               zero NEEDED entries
[PASS] CA bundle present                                 /etc/ssl/certs/ca-certificates.crt
[PASS] config syntax validation passes                   Valid configuration ...
[PASS] bundled config skeleton present                   /etc/caddy/Caddyfile
[PASS] data directory present                            /data present=true  /config present=true

10/10 passed, 0 failed, 0 skipped
```

The structured result is written to `tests/smoke-result.json` for machine consumption.

### Images with infrastructure requirements

Some smoke tests create Docker resources (networks, sidecar containers, tmpfs
mounts) for live testing. These are cleaned up automatically via a bash EXIT
trap. If a test is interrupted, you may need to clean up manually:

```bash
# List any leftover smoke containers
docker ps -a --filter "name=smoke-" --format "{{.Names}}"

# List any leftover smoke networks
docker network ls --filter "name=smoke-" --format "{{.Name}}"
```

---

## Check catalog

The full check catalog with IDs, categories, and descriptions is maintained in
the build pipeline. The checks relevant to each image are listed in that image's
`tests/smoke.manifest.json` file.

### Check categories

| Category | Purpose | Blocks promotion? |
|---|---|---|
| **security** | Hardening properties (nonroot, no_shell, banner) | Yes |
| **integrity** | Build correctness (binary_present, version_string, static_binary) | Yes |
| **functional** | Runtime behavior (health_endpoint, db_connect, ping_response) | Yes |
| **toolchain** | Builder image tools (compile_hello_world, linter_present) | Yes |

All checks are promotion-blocking by default. A failed check prevents the image
from being promoted to the public registry. Informational (non-blocking) checks
can be marked as such in the manifest.

---

## Service type reference

### web-server

Applies to: caddy, nginx, openresty, haproxy, traefik, pomerium

Standard checks plus:
- **config_validate** -- the service's own config syntax checker must accept the bundled configuration
- **health_endpoint** -- an HTTP GET to the health/readiness endpoint must return 200

Some web-server profiles add:
- **module_present** / **module_absent** -- compiled nginx modules match the profile
- **tls_connect** -- TLS handshake succeeds (TLS/SSL profiles)

### database

Applies to: postgres (v15, v17, v18 -- standard, tls, cli, vector, timescale)

Standard checks plus:
- **db_connect** -- pg_isready from the hardened image reaches an upstream server
- **extension_present** -- pgvector/timescaledb .so and .control files exist (extension profiles)
- **server_binary_absent** -- CLI-only profiles must not contain the server binary

### kv-store

Applies to: redis, valkey (standard, tls, cluster, cli)

Standard checks plus:
- **ping_response** -- PING returns PONG
- **set_get_roundtrip** -- SET a key, GET it back
- **dangerous_cmd_blocked** -- FLUSHALL and CONFIG are renamed
- **cluster_mode** -- cluster_enabled:1 in CLUSTER INFO (cluster profiles)
- **tls_connect** -- TLS handshake with self-signed cert (TLS profiles)

### messaging

Applies to: nats

Standard checks plus:
- **health_endpoint** -- GET /healthz returns 200
- **data_dir_present** -- /data/jetstream directory exists

### collector

Applies to: otelcol

Standard checks plus:
- **health_endpoint** -- health probe endpoint responds
- **config_present** -- default collector configuration file exists

### builder

Applies to: go-builder, python-builder, rust-builder

Does **not** include banner or no_shell checks. Builders intentionally retain a
shell from Alpine.

Standard checks plus:
- **toolchain_version** -- language runtime reports expected version
- **compile_hello_world** -- a trivial program compiles successfully
- **cgo_disabled** -- CGO_ENABLED=0 (Go builders)
- **trimpath** -- GOFLAGS contains -trimpath (Go builders)
- **linter_present** -- golangci-lint/ruff/clippy present (dev profiles)
- **formatter_present** -- gofumpt/black/rustfmt present (dev profiles)
- **vuln_scanner_present** -- govulncheck/pip-audit/cargo-audit present (dev profiles)

---

## Manifest format

Each image's `tests/smoke.manifest.json` provides metadata for the checks. The
smoke test runtime (`smoke-lib.sh`) uses this to label console output and to
produce structured JSON results for the Hub.

```json
{
  "$schema": "https://gwshield.io/schemas/smoke-manifest/v1.json",
  "image": "caddy",
  "version": "v2.11.2",
  "profile": "",
  "runtime_type": "scratch",
  "binary_path": "/usr/bin/caddy",
  "checks": [
    {
      "id": "binary_present",
      "label": "service binary present at declared path",
      "category": "integrity",
      "required": true,
      "since": "2026-03-15"
    }
  ]
}
```

The `id` field is the stable join key between the manifest, the smoke test
script, and the Supabase smoke_results table. Check IDs never change once set.
