#!/usr/bin/env python3
# =============================================================================
# tests/test_supabase_ingress.py — Unit tests for supabase_ingress.py
#
# Tests all pure (no-network) helper functions.
# Designed to run in CI immediately before any supabase_ingress.py invocation
# so that a logic regression is caught before it touches the database.
#
# Run:
#   python3 -m pytest scripts/tests/test_supabase_ingress.py -v
#   # or without pytest (stdlib only):
#   python3 scripts/tests/test_supabase_ingress.py
#
# No external dependencies — stdlib unittest only.
# =============================================================================

import importlib.util
import sys
import unittest
from pathlib import Path

# ---------------------------------------------------------------------------
# Module loader — import supabase_ingress without triggering main()
# The script lives one directory up from this test file.
# ---------------------------------------------------------------------------

_SCRIPT = Path(__file__).resolve().parent.parent / "supabase_ingress.py"

# When running against the local development copy (e.g. /tmp/supabase_ingress_new.py),
# override via env var: TEST_INGRESS_SCRIPT=/tmp/supabase_ingress_new.py
import os as _os
_override = _os.environ.get("TEST_INGRESS_SCRIPT")
if _override:
    _SCRIPT = Path(_override)


def _load_module():
    spec = importlib.util.spec_from_file_location("supabase_ingress", _SCRIPT)
    mod  = importlib.util.module_from_spec(spec)
    # Patch sys.argv so argparse doesn't try to parse pytest args
    _orig_argv = sys.argv
    sys.argv   = ["supabase_ingress.py"]
    try:
        spec.loader.exec_module(mod)
    except SystemExit:
        pass
    finally:
        sys.argv = _orig_argv
    return mod


_si = _load_module()


# =============================================================================
# derive_version_group
# =============================================================================

class TestDeriveVersionGroup(unittest.TestCase):
    """
    Heuristic: major >= 10 → only major.  major < 10 → major.minor.

    Edge cases that motivated this function:
    - postgres v15.17 and v17.9 exist as separate image families — the Hub needs
      to group them by major only ("15", "17"), not patch.
    - python-builder v3.12 / v3.13 are separate families — Hub groups by
      major.minor ("3.12", "3.13") because major (3) is the same for all Python.
    - Redis v7.4.8 — major < 10, so "7.4" (not "7").
    - Versions without leading 'v' prefix must also be handled (pipeline emits
      both forms depending on the caller).
    - A future postgres v100.x should still return "100" (major >= 10 check).
    """

    def _g(self, s):
        return _si.derive_version_group(s)

    # --- major >= 10: only major ---

    def test_postgres_v15_patch(self):
        self.assertEqual(self._g("v15.17"), "15")

    def test_postgres_v15_another_patch(self):
        # v15.16 → same group, different patch — must be idempotent
        self.assertEqual(self._g("v15.16"), "15")

    def test_postgres_v17(self):
        self.assertEqual(self._g("v17.9"), "17")

    def test_postgres_major_only_no_minor(self):
        # Hypothetical: only major provided
        self.assertEqual(self._g("v15"), "15")

    def test_large_major_future_proof(self):
        # e.g. postgres v100.1 — major >= 10
        self.assertEqual(self._g("v100.1"), "100")

    # --- major < 10: major.minor ---

    def test_redis_v7(self):
        self.assertEqual(self._g("v7.4.8"), "7.4")

    def test_nginx_v1_28(self):
        self.assertEqual(self._g("1.28.2"), "1.28")

    def test_python_v3_12(self):
        self.assertEqual(self._g("v3.12.4"), "3.12")

    def test_python_v3_13(self):
        self.assertEqual(self._g("v3.13.0"), "3.13")

    def test_go_builder_v1_24(self):
        self.assertEqual(self._g("v1.24.2"), "1.24")

    def test_go_builder_v1_25(self):
        self.assertEqual(self._g("v1.25.8"), "1.25")

    def test_rust_builder_v1_87(self):
        # v1.87 — only two parts (major.minor), no patch
        self.assertEqual(self._g("v1.87"), "1.87")

    def test_traefik_v3_6(self):
        self.assertEqual(self._g("v3.6.9"), "3.6")

    def test_caddy_v2_11(self):
        self.assertEqual(self._g("v2.11.2"), "2.11")

    def test_haproxy_v3_1(self):
        self.assertEqual(self._g("v3.1.16"), "3.1")

    def test_no_v_prefix(self):
        # Pipeline sometimes emits bare version strings without 'v'
        self.assertEqual(self._g("3.12.4"), "3.12")

    def test_single_digit_major_no_minor(self):
        # Edge: only major, no minor — returns just major
        self.assertEqual(self._g("v7"), "7")

    def test_boundary_major_9(self):
        # 9 < 10 → major.minor
        self.assertEqual(self._g("v9.6.1"), "9.6")

    def test_boundary_major_10(self):
        # 10 >= 10 → major only
        self.assertEqual(self._g("v10.0.1"), "10")


# =============================================================================
# derive_slug
# =============================================================================

class TestDeriveSlug(unittest.TestCase):
    """
    Slug derivation must stay in sync with gwshield-hub seed-images.ts CATALOG.

    Edge cases that caused prod mismatches:
    - nginx with empty profile must map to 'nginx-http' (not 'nginx') — the Hub
      CATALOG key is 'nginx-http'; using 'nginx' would create a dangling row.
    - python-builder profiles like 'v3.12' contain dots — they must be
      normalised to 'v312' to match the Hub slug 'python-builder-v312'.
    - go-builder / rust-builder slugs embed the version (go-builder-v124,
      rust-builder-v187) to prevent multi-version slug collisions in the DB.
    - postgres slug depends on major from base_version, not profile.
    """

    def _s(self, name, profile, base_version="v1.0"):
        return _si.derive_slug(name, profile, base_version)

    # --- nginx ---

    def test_nginx_empty_profile_is_http(self):
        # Critical: empty profile → nginx-http, NOT nginx
        self.assertEqual(self._s("nginx", ""), "nginx-http")

    def test_nginx_http_profile(self):
        self.assertEqual(self._s("nginx", "http"), "nginx-http")

    def test_nginx_http2(self):
        self.assertEqual(self._s("nginx", "http2"), "nginx-http2")

    def test_nginx_http3(self):
        self.assertEqual(self._s("nginx", "http3"), "nginx-http3")

    # --- postgres ---

    def test_postgres_v15_standard(self):
        self.assertEqual(self._s("postgres", "", "v15.17"), "postgres-v15")

    def test_postgres_v15_tls(self):
        self.assertEqual(self._s("postgres", "tls", "v15.17"), "postgres-v15-tls")

    def test_postgres_v15_cli(self):
        self.assertEqual(self._s("postgres", "cli", "v15.17"), "postgres-v15-cli")

    def test_postgres_v15_vector(self):
        self.assertEqual(self._s("postgres", "vector", "v15.17"), "postgres-v15-vector")

    def test_postgres_v15_timescale(self):
        self.assertEqual(self._s("postgres", "timescale", "v15.17"), "postgres-v15-timescale")

    def test_postgres_v17_standard(self):
        self.assertEqual(self._s("postgres", "", "v17.9"), "postgres-v17")

    def test_postgres_v17_tls(self):
        self.assertEqual(self._s("postgres", "tls", "v17.9"), "postgres-v17-tls")

    def test_postgres_v17_vector(self):
        self.assertEqual(self._s("postgres", "vector", "v17.9"), "postgres-v17-vector")

    # --- python-builder ---
    # Hub slugs always embed the version: python-builder-v312, python-builder-v312-dev etc.
    #
    # release-public.yml dispatches one of two real shapes:
    #   profile=""    base_version="v3.12"   (canonical build — dir v3.12)
    #   profile="dev" base_version="v3.12"   (dev build     — dir v3.12-dev, stripped to "dev")
    # Legacy explicit shapes (profile contains the full version string) also supported.

    def test_python_builder_canonical_v312(self):
        # Real dispatch: profile="" base_version="v3.12" → python-builder-v312
        self.assertEqual(self._s("python-builder", "", "v3.12"), "python-builder-v312")

    def test_python_builder_canonical_v313(self):
        self.assertEqual(self._s("python-builder", "", "v3.13"), "python-builder-v313")

    def test_python_builder_dev_v312(self):
        # Real dispatch: profile="dev" base_version="v3.12" → python-builder-v312-dev
        self.assertEqual(self._s("python-builder", "dev", "v3.12"), "python-builder-v312-dev")

    def test_python_builder_dev_v313(self):
        self.assertEqual(self._s("python-builder", "dev", "v3.13"), "python-builder-v313-dev")

    def test_python_builder_empty_profile_no_base_version(self):
        # Defensive: no base_version at all → bare name
        self.assertEqual(self._s("python-builder", "", ""), "python-builder")

    def test_python_builder_legacy_explicit_v312(self):
        # Legacy: profile="v3.12" (explicit) → same result
        self.assertEqual(self._s("python-builder", "v3.12", "v3.12"), "python-builder-v312")

    def test_python_builder_legacy_explicit_v312_dev(self):
        # Legacy: profile="v3.12-dev" → python-builder-v312-dev
        self.assertEqual(self._s("python-builder", "v3.12-dev", "v3.12"), "python-builder-v312-dev")

    def test_python_builder_legacy_explicit_v313(self):
        self.assertEqual(self._s("python-builder", "v3.13", "v3.13"), "python-builder-v313")

    def test_python_builder_legacy_explicit_v313_dev(self):
        self.assertEqual(self._s("python-builder", "v3.13-dev", "v3.13"), "python-builder-v313-dev")

    # --- go-builder ---
    # Versioned slugs: go-builder-v124, go-builder-v124-dev, go-builder-v125, …
    # Same pattern as python-builder — version always embedded to prevent
    # v1.24 and v1.25 from collapsing onto the same DB row.

    def test_go_builder_v124_empty_profile(self):
        self.assertEqual(self._s("go-builder", "", "v1.24"), "go-builder-v124")

    def test_go_builder_v124_compile_profile(self):
        # 'compile' is the internal canonical name → no suffix in slug
        self.assertEqual(self._s("go-builder", "compile", "v1.24"), "go-builder-v124")

    def test_go_builder_v124_dev(self):
        self.assertEqual(self._s("go-builder", "dev", "v1.24"), "go-builder-v124-dev")

    def test_go_builder_v125_empty_profile(self):
        self.assertEqual(self._s("go-builder", "", "v1.25"), "go-builder-v125")

    def test_go_builder_v125_compile_profile(self):
        self.assertEqual(self._s("go-builder", "compile", "v1.25"), "go-builder-v125")

    def test_go_builder_v125_dev(self):
        self.assertEqual(self._s("go-builder", "dev", "v1.25"), "go-builder-v125-dev")

    def test_go_builder_no_base_version_empty(self):
        # Fallback when base_version is absent
        self.assertEqual(self._s("go-builder", "", ""), "go-builder")

    def test_go_builder_no_base_version_dev(self):
        self.assertEqual(self._s("go-builder", "dev", ""), "go-builder-dev")

    # --- rust-builder ---
    # Same versioned-slug pattern: rust-builder-v187, rust-builder-v187-dev

    def test_rust_builder_v187_empty(self):
        self.assertEqual(self._s("rust-builder", "", "v1.87"), "rust-builder-v187")

    def test_rust_builder_v187_compile(self):
        self.assertEqual(self._s("rust-builder", "compile", "v1.87"), "rust-builder-v187")

    def test_rust_builder_v187_dev(self):
        self.assertEqual(self._s("rust-builder", "dev", "v1.87"), "rust-builder-v187-dev")

    def test_rust_builder_no_base_version_empty(self):
        self.assertEqual(self._s("rust-builder", "", ""), "rust-builder")

    def test_rust_builder_no_base_version_dev(self):
        self.assertEqual(self._s("rust-builder", "dev", ""), "rust-builder-dev")

    # --- redis ---

    def test_redis_standard(self):
        self.assertEqual(self._s("redis", ""), "redis")

    def test_redis_tls(self):
        self.assertEqual(self._s("redis", "tls"), "redis-tls")

    def test_redis_cluster(self):
        self.assertEqual(self._s("redis", "cluster"), "redis-cluster")

    def test_redis_cli(self):
        self.assertEqual(self._s("redis", "cli"), "redis-cli")

    # --- caddy ---

    def test_caddy_standard(self):
        self.assertEqual(self._s("caddy", ""), "caddy")

    def test_caddy_cloudflare(self):
        self.assertEqual(self._s("caddy", "cloudflare"), "caddy-cloudflare")

    def test_caddy_crowdsec(self):
        self.assertEqual(self._s("caddy", "crowdsec"), "caddy-crowdsec")

    def test_caddy_security(self):
        self.assertEqual(self._s("caddy", "security"), "caddy-security")

    def test_caddy_ratelimit(self):
        self.assertEqual(self._s("caddy", "ratelimit"), "caddy-ratelimit")

    def test_caddy_l4(self):
        self.assertEqual(self._s("caddy", "l4"), "caddy-l4")

    # --- haproxy ---

    def test_haproxy_standard(self):
        self.assertEqual(self._s("haproxy", ""), "haproxy")

    def test_haproxy_ssl(self):
        self.assertEqual(self._s("haproxy", "ssl"), "haproxy-ssl")

    # --- traefik ---

    def test_traefik(self):
        self.assertEqual(self._s("traefik", ""), "traefik")


# =============================================================================
# derive_image_type / resolve_image_type
# =============================================================================

class TestDeriveImageType(unittest.TestCase):
    """
    image_type drives the DB CHECK constraint (migration 0033).
    Wrong values cause an insert failure and a failed promote run.

    Edge cases:
    - 'cli' profile images (redis-cli, postgres-cli) must be 'tooling', not 'service'
    - All *-builder families must be 'builder', not 'service'
    - Everything else defaults to 'service'
    - CLI arg always wins over auto-detect (admin override path)
    """

    def _t(self, name, profile):
        return _si.derive_image_type(name, profile)

    def test_go_builder_is_builder(self):
        self.assertEqual(self._t("go-builder", ""), "builder")

    def test_go_builder_dev_is_builder(self):
        self.assertEqual(self._t("go-builder", "dev"), "builder")

    def test_python_builder_is_builder(self):
        self.assertEqual(self._t("python-builder", "v3.12"), "builder")

    def test_rust_builder_is_builder(self):
        self.assertEqual(self._t("rust-builder", "dev"), "builder")

    def test_redis_cli_is_tooling(self):
        self.assertEqual(self._t("redis", "cli"), "tooling")

    def test_postgres_cli_is_tooling(self):
        self.assertEqual(self._t("postgres", "cli"), "tooling")

    def test_nginx_is_service(self):
        self.assertEqual(self._t("nginx", ""), "service")

    def test_caddy_is_service(self):
        self.assertEqual(self._t("caddy", "cloudflare"), "service")

    def test_haproxy_is_service(self):
        self.assertEqual(self._t("haproxy", "ssl"), "service")

    def test_postgres_standard_is_service(self):
        self.assertEqual(self._t("postgres", ""), "service")

    def test_traefik_is_service(self):
        self.assertEqual(self._t("traefik", ""), "service")


class TestResolveImageType(unittest.TestCase):
    """
    CLI arg wins over auto-detect.
    None / empty CLI arg falls through to auto-detect.
    """

    def test_cli_arg_overrides_auto(self):
        # Auto would return 'service' for nginx, but CLI arg says 'tooling'
        self.assertEqual(_si.resolve_image_type("tooling", "nginx", ""), "tooling")

    def test_cli_arg_none_falls_through(self):
        self.assertEqual(_si.resolve_image_type(None, "go-builder", ""), "builder")

    def test_cli_arg_empty_string_falls_through(self):
        # Empty string is falsy in Python — treated same as None
        self.assertEqual(_si.resolve_image_type("", "redis", "cli"), "tooling")

    def test_cli_arg_service_explicit(self):
        # Even for a builder family, explicit CLI arg wins
        self.assertEqual(_si.resolve_image_type("service", "go-builder", ""), "service")


# =============================================================================
# derive_os_tag
# =============================================================================

class TestDeriveOsTag(unittest.TestCase):
    """
    OS tag is used by the Hub for filter chips and badge rendering.
    Wrong values don't break a promote but do corrupt the catalog view.
    """

    def test_postgres_is_distroless(self):
        self.assertEqual(_si.derive_os_tag("postgres"), "distroless")

    def test_caddy_is_scratch(self):
        self.assertEqual(_si.derive_os_tag("caddy"), "scratch")

    def test_traefik_is_scratch(self):
        self.assertEqual(_si.derive_os_tag("traefik"), "scratch")

    def test_nginx_is_alpine(self):
        self.assertEqual(_si.derive_os_tag("nginx"), "alpine")

    def test_redis_is_alpine(self):
        self.assertEqual(_si.derive_os_tag("redis"), "alpine")

    def test_haproxy_is_alpine(self):
        self.assertEqual(_si.derive_os_tag("haproxy"), "alpine")

    def test_go_builder_is_alpine(self):
        self.assertEqual(_si.derive_os_tag("go-builder"), "alpine")

    def test_python_builder_is_alpine(self):
        self.assertEqual(_si.derive_os_tag("python-builder"), "alpine")

    def test_rust_builder_is_alpine(self):
        self.assertEqual(_si.derive_os_tag("rust-builder"), "alpine")


# =============================================================================
# extract_findings_from_trivy (pure JSON parsing — no network)
# =============================================================================

class TestExtractFindingsFromTrivy(unittest.TestCase):
    """
    Edge cases from real Trivy output shapes:
    - Results with Vulnerabilities=None must not crash (clean image output)
    - Layer DiffID mapping: unknown DiffID defaults to 'base_image'
    - FixedVersion absent → mitigation_type='not_applicable'
    - FixedVersion present → mitigation_type='pkg_upgrade'
    - Description truncated to 500 chars
    - PkgIdentifier.PURL fallback when PkgID is absent
    """

    _MINIMAL_TRIVY = {
        "Metadata": {
            "DiffIDs": [],
            "ImageConfig": {"history": []},
        },
        "Results": [],
    }

    def test_empty_results_returns_empty_list(self):
        findings = _si.extract_findings_from_trivy(self._MINIMAL_TRIVY)
        self.assertEqual(findings, [])

    def test_none_vulnerabilities_skipped(self):
        doc = {
            "Metadata": {"DiffIDs": [], "ImageConfig": {"history": []}},
            "Results": [{"Type": "alpine", "Vulnerabilities": None}],
        }
        findings = _si.extract_findings_from_trivy(doc)
        self.assertEqual(findings, [])

    def test_finding_with_fixed_version(self):
        doc = {
            "Metadata": {"DiffIDs": ["sha256:aaa"], "ImageConfig": {"history": [
                {"created_by": "/bin/sh -c apk add musl", "empty_layer": False}
            ]}},
            "Results": [{
                "Type": "alpine",
                "Vulnerabilities": [{
                    "VulnerabilityID": "CVE-2025-1234",
                    "Severity": "HIGH",
                    "PkgName": "musl",
                    "InstalledVersion": "1.2.3",
                    "FixedVersion": "1.2.4",
                    "Title": "musl heap overflow",
                    "Layer": {"DiffID": "sha256:aaa"},
                }],
            }],
        }
        findings = _si.extract_findings_from_trivy(doc)
        self.assertEqual(len(findings), 1)
        f = findings[0]
        self.assertEqual(f["cve_id"],          "CVE-2025-1234")
        self.assertEqual(f["severity"],         "HIGH")
        self.assertEqual(f["package_name"],     "musl")
        self.assertEqual(f["fixed_version"],    "1.2.4")
        self.assertEqual(f["mitigation_type"],  "pkg_upgrade")
        self.assertEqual(f["component"],        "alpine-pkg")

    def test_finding_without_fixed_version(self):
        doc = {
            "Metadata": {"DiffIDs": [], "ImageConfig": {"history": []}},
            "Results": [{
                "Type": "gomod",
                "Vulnerabilities": [{
                    "VulnerabilityID": "CVE-2024-9999",
                    "Severity": "CRITICAL",
                    "PkgName": "stdlib",
                    "InstalledVersion": "go1.21.0",
                    "Title": "Go stdlib CVE",
                    "Layer": {"DiffID": "sha256:unknown"},
                }],
            }],
        }
        findings = _si.extract_findings_from_trivy(doc)
        self.assertEqual(len(findings), 1)
        f = findings[0]
        self.assertIsNone(f["fixed_version"])
        self.assertEqual(f["mitigation_type"], "not_applicable")
        self.assertEqual(f["component"],       "go-module")
        self.assertEqual(f["layer"],           "base_image")  # unknown DiffID → base_image

    def test_description_truncated_to_500_chars(self):
        long_desc = "x" * 600
        doc = {
            "Metadata": {"DiffIDs": [], "ImageConfig": {"history": []}},
            "Results": [{
                "Type": "alpine",
                "Vulnerabilities": [{
                    "VulnerabilityID": "CVE-2025-TRUNC",
                    "Severity": "LOW",
                    "PkgName": "pkg",
                    "InstalledVersion": "1.0",
                    "Title": long_desc,
                    "Layer": {},
                }],
            }],
        }
        findings = _si.extract_findings_from_trivy(doc)
        self.assertLessEqual(len(findings[0]["description"]), 500)

    def test_purl_fallback_for_component(self):
        # PkgID absent, PkgIdentifier.PURL present
        doc = {
            "Metadata": {"DiffIDs": [], "ImageConfig": {"history": []}},
            "Results": [{
                "Type": "cargo",
                "Vulnerabilities": [{
                    "VulnerabilityID": "CVE-2025-RUST",
                    "Severity": "MEDIUM",
                    "PkgName": "openssl",
                    "InstalledVersion": "0.10.55",
                    "PkgIdentifier": {"PURL": "pkg:cargo/openssl@0.10.55"},
                    "Layer": {},
                }],
            }],
        }
        findings = _si.extract_findings_from_trivy(doc)
        self.assertEqual(findings[0]["component"], "rust-crate")


# =============================================================================
# _component_type
# =============================================================================

class TestComponentType(unittest.TestCase):
    """Taxonomy mapping used in CVE findings rows."""

    def _c(self, pkg_id, vuln_type):
        return _si._component_type(pkg_id, vuln_type)

    def test_alpine_pkg(self):
        self.assertEqual(self._c("pkg:apk/musl@1.2.3", "alpine"), "alpine-pkg")

    def test_alpine_by_type(self):
        self.assertEqual(self._c("", "apk"), "alpine-pkg")

    def test_debian_pkg(self):
        self.assertEqual(self._c("pkg:deb/libc6@2.31", "debian"), "debian-pkg")

    def test_rust_crate_by_purl(self):
        self.assertEqual(self._c("pkg:cargo/openssl@0.10", ""), "rust-crate")

    def test_rust_crate_by_type(self):
        self.assertEqual(self._c("", "cargo"), "rust-crate")

    def test_go_module_by_purl(self):
        self.assertEqual(self._c("pkg:golang/golang.org/x/net@v0.0.1", ""), "go-module")

    def test_go_module_by_type(self):
        self.assertEqual(self._c("", "gomod"), "go-module")

    def test_python_pkg(self):
        self.assertEqual(self._c("pkg:pypi/requests@2.28.0", ""), "python-pkg")

    def test_npm_pkg(self):
        self.assertEqual(self._c("pkg:npm/lodash@4.17.21", ""), "npm-pkg")

    def test_unknown_falls_to_other(self):
        self.assertEqual(self._c("", ""), "other")


# =============================================================================
# derive_profile_tag
# =============================================================================

class TestDeriveProfileTag(unittest.TestCase):
    """
    Canonical profiles must be normalised to "standard" so the Hub renders
    them as primary/parent rows.

    Mappings:
      nginx        "" or "http"    → "standard"
      go-builder   "" or "compile" → "standard"
      rust-builder "" or "compile" → "standard"
      All other name+profile combinations pass through unchanged.
    """

    def _tag(self, name: str, profile: str) -> str:
        return _si.derive_profile_tag(name, profile)

    # nginx ---------------------------------------------------------------
    def test_nginx_empty_is_standard(self):
        self.assertEqual(self._tag("nginx", ""), "standard")

    def test_nginx_http_is_standard(self):
        self.assertEqual(self._tag("nginx", "http"), "standard")

    def test_nginx_http2_passthrough(self):
        self.assertEqual(self._tag("nginx", "http2"), "http2")

    def test_nginx_http3_passthrough(self):
        self.assertEqual(self._tag("nginx", "http3"), "http3")

    # go-builder ----------------------------------------------------------
    def test_go_builder_empty_is_standard(self):
        self.assertEqual(self._tag("go-builder", ""), "standard")

    def test_go_builder_compile_is_standard(self):
        self.assertEqual(self._tag("go-builder", "compile"), "standard")

    def test_go_builder_dev_passthrough(self):
        self.assertEqual(self._tag("go-builder", "dev"), "dev")

    # rust-builder --------------------------------------------------------
    def test_rust_builder_empty_is_standard(self):
        self.assertEqual(self._tag("rust-builder", ""), "standard")

    def test_rust_builder_compile_is_standard(self):
        self.assertEqual(self._tag("rust-builder", "compile"), "standard")

    def test_rust_builder_dev_passthrough(self):
        self.assertEqual(self._tag("rust-builder", "dev"), "dev")

    # other families — passthrough ----------------------------------------
    def test_postgres_tls_passthrough(self):
        self.assertEqual(self._tag("postgres", "tls"), "tls")

    def test_postgres_standard_passthrough(self):
        self.assertEqual(self._tag("postgres", "standard"), "standard")

    def test_redis_tls_passthrough(self):
        self.assertEqual(self._tag("redis", "tls"), "tls")

    def test_caddy_cloudflare_passthrough(self):
        self.assertEqual(self._tag("caddy", "cloudflare"), "cloudflare")

    def test_haproxy_ssl_passthrough(self):
        self.assertEqual(self._tag("haproxy", "ssl"), "ssl")

    def test_empty_name_empty_profile_passthrough(self):
        self.assertEqual(self._tag("", ""), "")

    def test_python_builder_dev_passthrough(self):
        self.assertEqual(self._tag("python-builder", "dev"), "dev")


# =============================================================================
# CLI guard: missing env vars → exit(1)
# =============================================================================

class TestMainEnvGuard(unittest.TestCase):
    """
    main() must exit with code 1 when SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY
    are not set.  This guards against accidental dry runs in environments without
    the secrets wired up.
    """

    def test_missing_env_exits_nonzero(self):
        import os
        import subprocess
        env = {**os.environ, "SUPABASE_URL": "", "SUPABASE_SERVICE_ROLE_KEY": ""}
        result = subprocess.run(
            [sys.executable, str(_SCRIPT), "promote",
             "--name", "nginx", "--version", "v1.28.2",
             "--base-version", "v1.28.2", "--profile", ""],
            capture_output=True, text=True, env=env,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("SUPABASE_URL", result.stderr)


# =============================================================================
# _merge_with_allowlist
# =============================================================================

class TestMergeWithAllowlist(unittest.TestCase):
    """
    _merge_with_allowlist merges real Trivy findings with suppressed allowlist
    entries.  Key invariants:

    1. Trivy findings are never modified.
    2. Suppressed entries are appended when their CVE ID is not in the Trivy set.
    3. When a CVE appears in both (Trivy still emitted it despite .trivyignore),
       the Trivy finding takes precedence and the allowlist entry is skipped.
    4. Empty inputs on either side produce correct output.
    5. Suppressed entries always have is_suppressed=True.
    """

    def _make_trivy_finding(self, cve_id: str, severity: str = "HIGH") -> dict:
        return {
            "cve_id":          cve_id,
            "severity":        severity,
            "package_name":    "some-pkg",
            "package_version": "1.0.0",
            "fixed_version":   "1.0.1",
            "description":     "A real finding",
            "mitigation_type": "pkg_upgrade",
            "layer":           "base_image",
            "component":       "alpine-pkg",
        }

    def _make_suppressed(self, cve_id: str, reason: str = "FALSE_POSITIVE_LINUX_BUILD") -> dict:
        return {
            "cve_id":               cve_id,
            "severity":             "HIGH",
            "package_name":         "go.opentelemetry.io/otel/sdk",
            "package_version":      "v1.39.0",
            "fixed_version":        "1.40.0",
            "description":          "Darwin-only, suppressed.",
            "mitigation_type":      "allowlisted",
            "layer":                "base_image",
            "component":            "go-module",
            "is_suppressed":        True,
            "suppression_reason":   reason,
            "suppression_detail":   "macOS only — not compiled on linux/amd64.",
            "suppression_evidence": ["build tag: darwin only"],
            "review_date":          "2026-06-30",
        }

    # --- basic merge ---

    def test_empty_trivy_empty_allowlist(self):
        result = _si._merge_with_allowlist([], [])
        self.assertEqual(result, [])

    def test_trivy_only_no_allowlist(self):
        findings = [self._make_trivy_finding("CVE-2025-001")]
        result   = _si._merge_with_allowlist(findings, [])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["cve_id"], "CVE-2025-001")

    def test_allowlist_only_no_trivy(self):
        suppressed = [self._make_suppressed("CVE-2025-SUPP")]
        result     = _si._merge_with_allowlist([], suppressed)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["cve_id"],       "CVE-2025-SUPP")
        self.assertTrue(result[0]["is_suppressed"])

    def test_disjoint_merge(self):
        # 2 real + 1 suppressed → 3 total, order: real first
        real = [
            self._make_trivy_finding("CVE-2025-001"),
            self._make_trivy_finding("CVE-2025-002"),
        ]
        supp = [self._make_suppressed("CVE-2025-SUPP")]
        result = _si._merge_with_allowlist(real, supp)
        self.assertEqual(len(result), 3)
        cves = [f["cve_id"] for f in result]
        self.assertIn("CVE-2025-001",  cves)
        self.assertIn("CVE-2025-002",  cves)
        self.assertIn("CVE-2025-SUPP", cves)

    # --- Trivy precedence ---

    def test_overlap_trivy_takes_precedence(self):
        # Same CVE ID in both lists — Trivy finding wins, allowlist entry dropped
        cve = "CVE-2025-OVERLAP"
        real = [self._make_trivy_finding(cve)]
        supp = [self._make_suppressed(cve)]
        result = _si._merge_with_allowlist(real, supp)
        self.assertEqual(len(result), 1)
        # The surviving entry must be the Trivy one (mitigation_type != allowlisted)
        self.assertNotEqual(result[0].get("mitigation_type"), "allowlisted")

    def test_partial_overlap(self):
        # 1 real + 1 suppressed, but 1 suppressed overlaps with real
        real = [
            self._make_trivy_finding("CVE-2025-REAL"),
            self._make_trivy_finding("CVE-2025-OVERLAP"),
        ]
        supp = [
            self._make_suppressed("CVE-2025-OVERLAP"),   # will be dropped
            self._make_suppressed("CVE-2025-UNIQUE"),    # will be appended
        ]
        result = _si._merge_with_allowlist(real, supp)
        self.assertEqual(len(result), 3)
        cves = [f["cve_id"] for f in result]
        self.assertIn("CVE-2025-REAL",    cves)
        self.assertIn("CVE-2025-OVERLAP", cves)
        self.assertIn("CVE-2025-UNIQUE",  cves)

    # --- invariants ---

    def test_trivy_findings_not_mutated(self):
        original = self._make_trivy_finding("CVE-2025-ORIG")
        original_copy = dict(original)
        _si._merge_with_allowlist([original], [self._make_suppressed("CVE-2025-OTHER")])
        self.assertEqual(original, original_copy)

    def test_suppressed_entry_missing_cve_id_skipped(self):
        # Entry without cve_id should be silently skipped
        bad_entry = {"severity": "HIGH", "package_name": "pkg", "package_version": "1.0"}
        result = _si._merge_with_allowlist([], [bad_entry])
        self.assertEqual(result, [])

    def test_multiple_suppressed_all_appended(self):
        supp = [
            self._make_suppressed(f"CVE-2025-{i:04d}")
            for i in range(10)
        ]
        result = _si._merge_with_allowlist([], supp)
        self.assertEqual(len(result), 10)
        for entry in result:
            self.assertTrue(entry["is_suppressed"])


# =============================================================================
# gen-trivyignore integration: _entry_to_finding (tested via gen-trivyignore.py)
# =============================================================================

class TestAllowlistEntryConversion(unittest.TestCase):
    """
    Verifies the contract between gen-trivyignore.py's _entry_to_finding()
    output and what _merge_with_allowlist() + write_findings() expect.

    We test the shape of the produced findings dict to ensure it's compatible
    with the cve_findings row schema and the merge logic.
    """

    # Minimal allowlist entry (only required fields)
    _MINIMAL_ENTRY = {
        "cve":      "CVE-2026-24051",
        "severity": "HIGH",
        "component": "gobinary/go.opentelemetry.io/otel/sdk",
        "installed_version": "v1.39.0",
        "fixed_version": "1.40.0",
        "verdict": "FALSE_POSITIVE_LINUX_BUILD",
        "analysis": "Darwin-only code path. Build tag gated. Not compiled on linux/amd64.",
        "evidence": ["Build tag: darwin only", "Binary: ioreg NOT FOUND"],
        "review_date": "2026-06-30",
    }

    def _load_gen_script(self):
        """Load gen-trivyignore.py as a module."""
        import importlib.util
        script = (Path(__file__).resolve().parent.parent.parent.parent
                  / "shared" / "scripts" / "gen-trivyignore.py")
        # Try env-override path as well
        env_override = _os.environ.get("TEST_GEN_SCRIPT")
        if env_override:
            script = Path(env_override)
        if not script.exists():
            self.skipTest(f"gen-trivyignore.py not found at {script}")
        spec = importlib.util.spec_from_file_location("gen_trivyignore", script)
        mod  = importlib.util.module_from_spec(spec)
        import sys as _sys
        _orig = _sys.argv
        _sys.argv = ["gen-trivyignore.py"]
        try:
            spec.loader.exec_module(mod)
        except SystemExit:
            pass
        finally:
            _sys.argv = _orig
        return mod

    def test_entry_produces_required_fields(self):
        gen = self._load_gen_script()
        import pathlib as _pl
        fake_path = _pl.Path("images/traefik/v3.6.9/scan/allowlist.yaml")
        finding = gen._entry_to_finding(self._MINIMAL_ENTRY, fake_path)

        required = [
            "cve_id", "severity", "package_name", "package_version",
            "fixed_version", "description", "layer", "component",
            "mitigation_type", "mitigation_detail",
            "is_suppressed", "suppression_reason", "suppression_detail",
            "suppression_evidence", "review_date",
        ]
        for field in required:
            self.assertIn(field, finding, f"Missing field: {field}")

    def test_entry_is_suppressed_true(self):
        gen = self._load_gen_script()
        import pathlib as _pl
        finding = gen._entry_to_finding(
            self._MINIMAL_ENTRY,
            _pl.Path("images/traefik/v3.6.9/scan/allowlist.yaml")
        )
        self.assertTrue(finding["is_suppressed"])
        self.assertEqual(finding["mitigation_type"], "allowlisted")

    def test_entry_cve_id_mapped(self):
        gen = self._load_gen_script()
        import pathlib as _pl
        finding = gen._entry_to_finding(
            self._MINIMAL_ENTRY,
            _pl.Path("images/traefik/v3.6.9/scan/allowlist.yaml")
        )
        self.assertEqual(finding["cve_id"], "CVE-2026-24051")

    def test_entry_component_classified_as_go_module(self):
        gen = self._load_gen_script()
        import pathlib as _pl
        finding = gen._entry_to_finding(
            self._MINIMAL_ENTRY,
            _pl.Path("images/traefik/v3.6.9/scan/allowlist.yaml")
        )
        self.assertEqual(finding["component"], "go-module")

    def test_entry_description_truncated_to_500(self):
        gen = self._load_gen_script()
        import pathlib as _pl
        long_entry = dict(self._MINIMAL_ENTRY)
        long_entry["analysis"] = "x" * 600
        finding = gen._entry_to_finding(
            long_entry,
            _pl.Path("images/x/v1.0/scan/allowlist.yaml")
        )
        self.assertLessEqual(len(finding["description"]), 500)

    def test_entry_suppression_detail_truncated_to_2000(self):
        gen = self._load_gen_script()
        import pathlib as _pl
        long_entry = dict(self._MINIMAL_ENTRY)
        long_entry["analysis"] = "y" * 2500
        finding = gen._entry_to_finding(
            long_entry,
            _pl.Path("images/x/v1.0/scan/allowlist.yaml")
        )
        self.assertLessEqual(len(finding["suppression_detail"]), 2000)

    def test_entry_evidence_is_list(self):
        gen = self._load_gen_script()
        import pathlib as _pl
        finding = gen._entry_to_finding(
            self._MINIMAL_ENTRY,
            _pl.Path("images/traefik/v3.6.9/scan/allowlist.yaml")
        )
        self.assertIsInstance(finding["suppression_evidence"], list)

    def test_entry_compatible_with_merge(self):
        """A finding from gen-trivyignore passes cleanly through _merge_with_allowlist."""
        gen = self._load_gen_script()
        import pathlib as _pl
        suppressed = gen._entry_to_finding(
            self._MINIMAL_ENTRY,
            _pl.Path("images/traefik/v3.6.9/scan/allowlist.yaml")
        )
        result = _si._merge_with_allowlist([], [suppressed])
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0]["is_suppressed"])


# =============================================================================
# Entry point — can be run without pytest
# =============================================================================

if __name__ == "__main__":
    loader  = unittest.TestLoader()
    suite   = loader.loadTestsFromModule(sys.modules[__name__])
    runner  = unittest.TextTestRunner(verbosity=2)
    result  = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
