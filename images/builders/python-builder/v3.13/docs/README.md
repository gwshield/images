# gwshield python-builder v3.13

**Profile:** install-only
**Registry:** `ghcr.io/gwshield/python-builder:v3.13`
**Scan date:** 2026-03-08 — 0 HIGH / 0 CRITICAL CVEs

> **Builder image** — use as `FROM ghcr.io/gwshield/python-builder:v3.13 AS builder`
> in downstream multi-stage Dockerfiles. Not deployed as a runtime container.

---

## Overview

| Field | Value |
|---|---|
| Python version | 3.13.12 |
| Base image | `python:3.13-alpine3.22` |
| Non-root UID | 65532 |
| Shell | retained (`/bin/sh`) — required for downstream `RUN` steps |

---

## CVE baseline

Python 3.13.12 is the current latest patch in the 3.13.x line.
Alpine 3.22 ships OpenSSL 3.3.6+, resolving all known CRITICAL/HIGH OpenSSL
CVEs from Alpine 3.21 and earlier. **Result: 0 HIGH / 0 CRITICAL CVEs.**

---

## Hardening applied

| Control | Detail |
|---|---|
| Digest-pinned base | `python:3.13-alpine3.22` pinned by SHA256 |
| Non-root identity | UID/GID 65532 (`nonroot`) |
| `PYTHONDONTWRITEBYTECODE=1` | No `.pyc` accumulation in image layers |
| `PYTHONUNBUFFERED=1` | No log loss on crash |
| `PYTHONFAULTHANDLER=1` | Segfault tracebacks enabled |
| `PYTHONHASHSEED=random` | Hash-collision DoS mitigation |
| `PIP_NO_CACHE_DIR=1` | No persistent pip cache in image layer |
| Writable paths scoped | `/build` and `/app` only |

---

## Source pins

| Component | Version | Digest |
|---|---|---|
| Python toolchain | `python:3.13-alpine3.22` (3.13.12) | `sha256:41351b07080ccfaa27bf38dde20de79ee6a0ac74a58c00c6d7a7d96ac4e69716` |
| Alpine base | 3.22 | `sha256:55ae5d250caebc548793f321534bc6a8ef1d116f334f18f4ada1b2daad3251b2` |
| Build date | 2026-03-08 | — |

---

## Rebuild trigger

- New Python 3.13.x patch release
- Alpine 3.22 package update for a HIGH/CRITICAL CVE
- Upstream digest change for `python:3.13-alpine3.22`
