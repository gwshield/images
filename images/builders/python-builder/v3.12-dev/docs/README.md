# gwshield python-builder v3.12-dev

**Profile:** dev (install + lint + test + format + audit)
**Registry:** `ghcr.io/gwshield/python-builder:v3.12-dev`
**Scan date:** 2026-03-08 — 0 HIGH / 0 CRITICAL CVEs

> **Builder image** — use as `FROM ghcr.io/gwshield/python-builder:v3.12-dev AS ci`
> in CI pipelines. Not deployed as a runtime container.

---

## Overview

Extends `gwshield/python-builder:v3.12` with the full Python CI toolchain.

| Tool | Version | Purpose |
|---|---|---|
| Base image | `python:3.12-alpine3.22` (3.12.13) | — |
| ruff | 0.15.5 | Linter + formatter |
| mypy | 1.19.1 | Static type checker |
| pytest | 9.0.2 | Test runner |
| pip-audit | 2.10.0 | Dependency CVE scanner (PyPA) |
| black | 26.3.0 | Opinionated formatter |
| isort | 8.0.1 | Import sorter |

All tools installed via `pip install` with pinned versions.

---

## CVE baseline

Inherits 0 HIGH / 0 CRITICAL from `python-builder:v3.12`. Dev tools are pure
Python packages — no additional C dependencies or system libraries.

---

## Build strategy

Three-stage build:
1. **deps** — creates nonroot identity (UID 65532)
2. **tool-installer** — installs all dev tools via pip as root
3. **python-builder-dev** — final stage; copies identity + tool binaries +
   site-packages from earlier stages; sets all hardening ENVs + `USER 65532:65532`

The final stage is self-contained and works with both the upstream `python` base
and the promoted `ghcr.io/gwshield/python-builder:v3.12` base.

---

## Source pins

| Component | Version | Digest |
|---|---|---|
| Base image | `python:3.12-alpine3.22` | `sha256:f6973b8f9395204414a7f25d99a50ba1c7306064771d11a8c2a848e9af3697a6` |
| ruff | 0.15.5 | — |
| mypy | 1.19.1 | — |
| pytest | 9.0.2 | — |
| pip-audit | 2.10.0 | — |
| black | 26.3.0 | — |
| isort | 8.0.1 | — |
| Build date | 2026-03-08 | — |

---

## Rebuild trigger

- New Python 3.12.x patch release
- New tool release with security fixes
- Alpine 3.22 update in the base image
