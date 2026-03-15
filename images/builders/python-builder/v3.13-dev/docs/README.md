# gwshield python-builder v3.13-dev

**Profile:** dev (install + lint + test + format + audit)
**Registry:** `ghcr.io/gwshield/python-builder:v3.13-dev`
**Scan date:** 2026-03-08 — 0 HIGH / 0 CRITICAL CVEs

> **Builder image** — use as `FROM ghcr.io/gwshield/python-builder:v3.13-dev AS ci`
> in CI pipelines. Not deployed as a runtime container.

---

## Overview

Extends `gwshield/python-builder:v3.13` with the full Python CI toolchain.

| Tool | Version | Purpose |
|---|---|---|
| Base image | `python:3.13-alpine3.22` (3.13.12) | — |
| ruff | 0.15.5 | Linter + formatter |
| mypy | 1.19.1 | Static type checker |
| pytest | 9.0.2 | Test runner |
| pip-audit | 2.10.0 | Dependency CVE scanner (PyPA) |
| black | 26.3.0 | Opinionated formatter |
| isort | 8.0.1 | Import sorter |

All tools installed via `pip install` with pinned versions.
Same tool versions as `v3.12-dev` — all tools support both Python 3.12 and 3.13.

---

## CVE baseline

Inherits 0 HIGH / 0 CRITICAL from `python-builder:v3.13`. Dev tools are pure
Python packages — no additional C dependencies or system libraries.

---

## Build strategy

Two-stage build:
1. **tool-installer** — installs all dev tools via pip as root on top of the pinned base
2. **python-builder-dev** — final stage; copies tool binaries + site-packages from
   tool-installer; self-contained (works with both upstream python base and promoted
   gwshield base)

---

## Source pins

| Component | Version | Digest |
|---|---|---|
| Base image | `python:3.13-alpine3.22` | `sha256:41351b07080ccfaa27bf38dde20de79ee6a0ac74a58c00c6d7a7d96ac4e69716` |
| ruff | 0.15.5 | — |
| mypy | 1.19.1 | — |
| pytest | 9.0.2 | — |
| pip-audit | 2.10.0 | — |
| black | 26.3.0 | — |
| isort | 8.0.1 | — |
| Build date | 2026-03-08 | — |

---

## Rebuild trigger

- New Python 3.13.x patch release
- New tool release with security fixes
- Alpine 3.22 update in the base image
