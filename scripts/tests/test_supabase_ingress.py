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
# write_findings — row-dict construction (mock DB, no network)
# =============================================================================

class _MockDB:
    """
    Minimal SupabaseClient stand-in for write_findings tests.
    Records every upsert() call in self.rows for inspection.
    table_exists() and _suppression_cols_exist probe are controlled
    via constructor flags.
    """

    def __init__(self, table_exists: bool = True, suppress_cols: bool = True):
        self._table_exists  = table_exists
        self._suppress_cols = suppress_cols
        self.rows: list[dict] = []
        self.deleted: list[dict] = []
        # Expose attributes that _suppression_cols_exist probes
        self.base    = "http://mock/rest/v1"
        self.headers = {}

    def table_exists(self, table: str) -> bool:
        return self._table_exists

    def upsert(self, table: str, row: dict, on_conflict: str) -> dict:
        self.rows.append(dict(row))
        return row

    def delete(self, table: str, filters: dict) -> None:
        self.deleted.append(filters)


def _write_findings_with_mock(findings, suppress_cols=True, table_exists=True, replace=True):
    """
    Helper: run write_findings() with a MockDB, patching the global
    suppression-column cache so we don't need a real HTTP probe.
    Returns (written_count, rows_written).
    """
    db = _MockDB(table_exists=table_exists, suppress_cols=suppress_cols)

    # Patch global cache for this call
    orig = _si._suppression_columns_available
    _si._suppression_columns_available = suppress_cols
    try:
        n = _si.write_findings(db, "test-version-uuid-0001", findings, replace=replace)
    finally:
        _si._suppression_columns_available = orig

    return n, db.rows


class TestWriteFindings(unittest.TestCase):
    """
    write_findings() row-dict construction tests.
    No network — uses _MockDB.  Tests cover:
      - core columns always present
      - suppression columns present when suppress_cols=True
      - suppression columns absent when suppress_cols=False (pre-migration)
      - is_suppressed default is False for real findings
      - suppressed findings correctly flagged
      - empty findings → 0 written
      - table not yet migrated → 0 written, no upsert called
      - replace=True triggers a delete before upsert
    """

    _REAL_FINDING = {
        "cve_id":          "CVE-2025-REAL",
        "severity":        "HIGH",
        "package_name":    "some-pkg",
        "package_version": "1.2.3",
        "fixed_version":   "1.2.4",
        "description":     "A real vuln",
        "mitigation_type": "pkg_upgrade",
        "layer":           "base_image",
        "component":       "alpine-pkg",
    }

    _SUPPRESSED_FINDING = {
        "cve_id":               "CVE-2025-SUPP",
        "severity":             "LOW",
        "package_name":         "go.opentelemetry.io/otel/sdk",
        "package_version":      "v1.39.0",
        "fixed_version":        None,
        "description":          "Darwin-only — suppressed.",
        "mitigation_type":      "allowlisted",
        "layer":                "base_image",
        "component":            "go-module",
        "is_suppressed":        True,
        "suppression_reason":   "FALSE_POSITIVE_LINUX_BUILD",
        "suppression_detail":   "macOS only, not compiled on linux/amd64.",
        "suppression_evidence": ["build tag: darwin only"],
        "review_date":          "2026-06-30",
    }

    def test_empty_findings_returns_zero(self):
        n, rows = _write_findings_with_mock([])
        self.assertEqual(n, 0)
        self.assertEqual(rows, [])

    def test_table_not_exists_returns_zero(self):
        n, rows = _write_findings_with_mock([self._REAL_FINDING], table_exists=False)
        self.assertEqual(n, 0)
        self.assertEqual(rows, [])

    def test_core_columns_always_present(self):
        n, rows = _write_findings_with_mock([self._REAL_FINDING])
        self.assertEqual(n, 1)
        row = rows[0]
        for col in ("image_version_id", "cve_id", "severity", "package_name",
                    "package_version", "fixed_version", "description",
                    "mitigation_type", "layer", "component"):
            self.assertIn(col, row, f"Core column missing: {col}")

    def test_image_version_id_injected(self):
        _, rows = _write_findings_with_mock([self._REAL_FINDING])
        self.assertEqual(rows[0]["image_version_id"], "test-version-uuid-0001")

    def test_suppression_cols_written_when_available(self):
        _, rows = _write_findings_with_mock([self._SUPPRESSED_FINDING], suppress_cols=True)
        row = rows[0]
        self.assertIn("is_suppressed",        row)
        self.assertIn("suppression_reason",   row)
        self.assertIn("suppression_detail",   row)
        self.assertIn("suppression_evidence", row)
        self.assertIn("review_date",          row)
        self.assertTrue(row["is_suppressed"])
        self.assertEqual(row["suppression_reason"], "FALSE_POSITIVE_LINUX_BUILD")

    def test_suppression_cols_absent_when_migration_pending(self):
        """Before migration 0044 — suppression columns must NOT be sent to DB."""
        _, rows = _write_findings_with_mock([self._SUPPRESSED_FINDING], suppress_cols=False)
        row = rows[0]
        self.assertNotIn("is_suppressed",      row)
        self.assertNotIn("suppression_reason", row)
        self.assertNotIn("suppression_detail", row)

    def test_real_finding_is_suppressed_defaults_false(self):
        """Real finding has no is_suppressed key → written as False."""
        _, rows = _write_findings_with_mock([self._REAL_FINDING], suppress_cols=True)
        self.assertFalse(rows[0]["is_suppressed"])

    def test_mixed_findings_written_in_order(self):
        findings = [self._REAL_FINDING, self._SUPPRESSED_FINDING]
        n, rows  = _write_findings_with_mock(findings, suppress_cols=True)
        self.assertEqual(n, 2)
        cves = [r["cve_id"] for r in rows]
        self.assertIn("CVE-2025-REAL", cves)
        self.assertIn("CVE-2025-SUPP", cves)

    def test_replace_true_triggers_delete(self):
        db = _MockDB(suppress_cols=True)
        orig = _si._suppression_columns_available
        _si._suppression_columns_available = True
        try:
            _si.write_findings(db, "ver-001", [self._REAL_FINDING], replace=True)
        finally:
            _si._suppression_columns_available = orig
        self.assertEqual(len(db.deleted), 1)
        self.assertEqual(db.deleted[0], {"image_version_id": "ver-001"})

    def test_replace_false_no_delete(self):
        db = _MockDB(suppress_cols=True)
        orig = _si._suppression_columns_available
        _si._suppression_columns_available = True
        try:
            _si.write_findings(db, "ver-001", [self._REAL_FINDING], replace=False)
        finally:
            _si._suppression_columns_available = orig
        self.assertEqual(len(db.deleted), 0)


# =============================================================================
# _suppression_cols_exist — probe + cache behaviour (mock HTTP)
# =============================================================================

class TestSuppressionColsProbe(unittest.TestCase):
    """
    _suppression_cols_exist() probes via HTTP GET and caches the result.
    Tests:
      - successful probe → True cached
      - failed probe (exception) → False cached (graceful fallback)
      - result is cached (probe called only once per cache reset)
    """

    def _reset_cache(self):
        """Reset the global cache between tests."""
        _si._suppression_columns_available = None

    def test_probe_success_returns_true(self):
        """When the HTTP probe succeeds, result is True."""
        self._reset_cache()

        class _OkDB(_MockDB):
            pass  # table_exists not used; we mock urllib directly

        import unittest.mock as _mock
        import urllib.request as _ur

        fake_resp = _mock.MagicMock()
        fake_resp.__enter__ = lambda s: s
        fake_resp.__exit__  = _mock.MagicMock(return_value=False)
        fake_resp.read      = _mock.MagicMock(return_value=b"[]")

        db = _OkDB()
        with _mock.patch.object(_ur, "urlopen", return_value=fake_resp):
            result = _si._suppression_cols_exist(db)

        self.assertTrue(result)
        self.assertTrue(_si._suppression_columns_available)

    def test_probe_failure_returns_false(self):
        """When the HTTP probe raises, fallback is False — never propagates."""
        self._reset_cache()

        import unittest.mock as _mock
        import urllib.request as _ur

        db = _MockDB()
        with _mock.patch.object(_ur, "urlopen", side_effect=Exception("network error")):
            result = _si._suppression_cols_exist(db)

        self.assertFalse(result)
        self.assertFalse(_si._suppression_columns_available)

    def test_probe_cached_after_first_call(self):
        """Second call must not issue another HTTP request."""
        self._reset_cache()

        import unittest.mock as _mock
        import urllib.request as _ur

        call_count = {"n": 0}

        fake_resp = _mock.MagicMock()
        fake_resp.__enter__ = lambda s: s
        fake_resp.__exit__  = _mock.MagicMock(return_value=False)
        fake_resp.read      = _mock.MagicMock(return_value=b"[]")

        def _counting_urlopen(req, **kw):
            call_count["n"] += 1
            return fake_resp

        db = _MockDB()
        with _mock.patch.object(_ur, "urlopen", side_effect=_counting_urlopen):
            _si._suppression_cols_exist(db)
            _si._suppression_cols_exist(db)  # second call — must hit cache

        self.assertEqual(call_count["n"], 1, "urlopen called more than once — cache not working")

    def tearDown(self):
        # Always reset cache so other tests are not affected
        _si._suppression_columns_available = None


# =============================================================================
# gen-trivyignore integration: _entry_to_finding (tested via gen-trivyignore.py)
# =============================================================================

# ---------------------------------------------------------------------------
# Path resolution for gen-trivyignore.py — CI-compatible.
# Candidate search order:
#   1. TEST_GEN_SCRIPT env var (explicit override — local dev / docker)
#   2. relative to this test file in-repo: ../../shared/scripts/gen-trivyignore.py
#      (works when tests run from scripts/tests/ inside gwshield-images checkout)
#   3. relative 4 levels up (legacy path kept for backward compat)
# The module is loaded once at import time and cached in _GEN_MOD.
# If not found, _GEN_MOD is None and all TestAllowlistEntryConversion tests skip.
# ---------------------------------------------------------------------------

def _find_gen_script() -> Path | None:
    import importlib.util as _ilu
    candidates = []

    env_override = _os.environ.get("TEST_GEN_SCRIPT")
    if env_override:
        candidates.append(Path(env_override))

    this_file = Path(__file__).resolve()
    # In-repo layout: scripts/tests/test_supabase_ingress.py
    candidates.append(this_file.parent.parent.parent / "shared" / "scripts" / "gen-trivyignore.py")
    # Legacy / flat layout (test run from repo root or /tmp)
    candidates.append(this_file.parent.parent.parent.parent / "shared" / "scripts" / "gen-trivyignore.py")

    for p in candidates:
        if p.exists():
            return p
    return None


def _load_gen_trivyignore() -> object | None:
    import importlib.util as _ilu
    script = _find_gen_script()
    if script is None:
        return None
    spec = _ilu.spec_from_file_location("gen_trivyignore", script)
    mod  = _ilu.module_from_spec(spec)
    _orig = sys.argv
    sys.argv = ["gen-trivyignore.py"]
    try:
        spec.loader.exec_module(mod)
    except SystemExit:
        pass
    finally:
        sys.argv = _orig
    return mod


_GEN_MOD = _load_gen_trivyignore()


class TestAllowlistEntryConversion(unittest.TestCase):
    """
    Verifies the contract between gen-trivyignore.py's _entry_to_finding()
    output and what _merge_with_allowlist() + write_findings() expect.

    _GEN_MOD is resolved at import time via _load_gen_trivyignore() using
    a multi-candidate path search — works in CI (in-repo layout) and local
    dev (TEST_GEN_SCRIPT override or legacy path).  All tests in this class
    skip uniformly when the script cannot be located.
    """

    # Full allowlist entry matching the allowlist.yaml schema
    _MINIMAL_ENTRY = {
        "cve":               "CVE-2026-24051",
        "severity":          "HIGH",
        "component":         "gobinary/go.opentelemetry.io/otel/sdk",
        "installed_version": "v1.39.0",
        "fixed_version":     "1.40.0",
        "verdict":           "FALSE_POSITIVE_LINUX_BUILD",
        "analysis":          "Darwin-only code path. Build tag gated. Not compiled on linux/amd64.",
        "evidence":          ["Build tag: darwin only", "Binary: ioreg NOT FOUND"],
        "review_date":       "2026-06-30",
    }

    def setUp(self):
        if _GEN_MOD is None:
            self.skipTest("gen-trivyignore.py not found — set TEST_GEN_SCRIPT to enable")

    def _finding(self, entry=None, path="images/traefik/v3.6.9/scan/allowlist.yaml"):
        return _GEN_MOD._entry_to_finding(entry or self._MINIMAL_ENTRY, Path(path))

    # --- schema contract ---

    def test_entry_produces_required_fields(self):
        finding = self._finding()
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
        finding = self._finding()
        self.assertTrue(finding["is_suppressed"])
        self.assertEqual(finding["mitigation_type"], "allowlisted")

    def test_entry_cve_id_mapped(self):
        self.assertEqual(self._finding()["cve_id"], "CVE-2026-24051")

    def test_entry_suppression_reason_mapped(self):
        self.assertEqual(self._finding()["suppression_reason"], "FALSE_POSITIVE_LINUX_BUILD")

    def test_entry_review_date_mapped(self):
        self.assertEqual(self._finding()["review_date"], "2026-06-30")

    def test_entry_component_classified_as_go_module(self):
        self.assertEqual(self._finding()["component"], "go-module")

    def test_entry_alpine_pkg_classified(self):
        entry = dict(self._MINIMAL_ENTRY, component="apk/musl")
        self.assertEqual(self._finding(entry)["component"], "alpine-pkg")

    def test_entry_rust_crate_classified(self):
        entry = dict(self._MINIMAL_ENTRY, component="cargo/ring")
        self.assertEqual(self._finding(entry)["component"], "rust-crate")

    def test_entry_python_pkg_classified(self):
        entry = dict(self._MINIMAL_ENTRY, component="pypi/requests")
        self.assertEqual(self._finding(entry)["component"], "python-pkg")

    def test_entry_unknown_component_is_other(self):
        entry = dict(self._MINIMAL_ENTRY, component="")
        self.assertEqual(self._finding(entry)["component"], "other")

    # --- truncation ---

    def test_entry_description_truncated_to_500(self):
        entry = dict(self._MINIMAL_ENTRY, analysis="x" * 600)
        self.assertLessEqual(len(self._finding(entry)["description"]), 500)

    def test_entry_suppression_detail_truncated_to_2000(self):
        entry = dict(self._MINIMAL_ENTRY, analysis="y" * 2500)
        self.assertLessEqual(len(self._finding(entry)["suppression_detail"]), 2000)

    def test_entry_suppression_detail_exact_2000_boundary(self):
        entry = dict(self._MINIMAL_ENTRY, analysis="z" * 2000)
        self.assertEqual(len(self._finding(entry)["suppression_detail"]), 2000)

    # --- evidence handling ---

    def test_entry_evidence_is_list(self):
        self.assertIsInstance(self._finding()["suppression_evidence"], list)

    def test_entry_evidence_string_wrapped_in_list(self):
        """When evidence is a plain string (not a list), it must still produce a list."""
        entry = dict(self._MINIMAL_ENTRY, evidence="single string evidence")
        ev = self._finding(entry)["suppression_evidence"]
        self.assertIsInstance(ev, list)
        self.assertEqual(len(ev), 1)

    def test_entry_evidence_empty_list(self):
        entry = dict(self._MINIMAL_ENTRY, evidence=[])
        # Empty list → None (falsy guard in _entry_to_finding)
        ev = self._finding(entry)["suppression_evidence"]
        self.assertIsNone(ev)

    def test_entry_no_evidence_key(self):
        entry = {k: v for k, v in self._MINIMAL_ENTRY.items() if k != "evidence"}
        ev = self._finding(entry)["suppression_evidence"]
        self.assertIsNone(ev)

    def test_entry_compensating_controls_fallback(self):
        """compensating_controls is accepted as a deprecated alias for evidence."""
        entry = {k: v for k, v in self._MINIMAL_ENTRY.items() if k != "evidence"}
        entry["compensating_controls"] = ["control A", "control B"]
        ev = self._finding(entry)["suppression_evidence"]
        self.assertIsInstance(ev, list)
        self.assertEqual(ev, ["control A", "control B"])

    def test_entry_evidence_takes_precedence_over_compensating_controls(self):
        """When both evidence and compensating_controls are present, evidence wins."""
        entry = dict(
            self._MINIMAL_ENTRY,
            evidence=["evidence item"],
            compensating_controls=["control item"],
        )
        ev = self._finding(entry)["suppression_evidence"]
        self.assertEqual(ev, ["evidence item"])

    def test_entry_compensating_controls_empty_list_is_none(self):
        """Empty compensating_controls (fallback) produces None, consistent with evidence."""
        entry = {k: v for k, v in self._MINIMAL_ENTRY.items() if k != "evidence"}
        entry["compensating_controls"] = []
        ev = self._finding(entry)["suppression_evidence"]
        self.assertIsNone(ev)

    # --- edge cases ---

    def test_entry_missing_severity_defaults_to_unknown(self):
        entry = {k: v for k, v in self._MINIMAL_ENTRY.items() if k != "severity"}
        self.assertEqual(self._finding(entry)["severity"], "UNKNOWN")

    def test_entry_severity_normalised_to_upper(self):
        entry = dict(self._MINIMAL_ENTRY, severity="high")
        self.assertEqual(self._finding(entry)["severity"], "HIGH")

    def test_entry_no_review_date_is_none(self):
        entry = {k: v for k, v in self._MINIMAL_ENTRY.items() if k != "review_date"}
        self.assertIsNone(self._finding(entry)["review_date"])

    def test_entry_no_fixed_version_is_none(self):
        entry = {k: v for k, v in self._MINIMAL_ENTRY.items() if k != "fixed_version"}
        self.assertIsNone(self._finding(entry)["fixed_version"])

    def test_entry_layer_always_base_image(self):
        self.assertEqual(self._finding()["layer"], "base_image")

    # --- integration with merge ---

    def test_entry_compatible_with_merge(self):
        """A finding from gen-trivyignore passes cleanly through _merge_with_allowlist."""
        suppressed = self._finding()
        result = _si._merge_with_allowlist([], [suppressed])
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0]["is_suppressed"])

    def test_entry_compatible_with_write_findings(self):
        """A finding from gen-trivyignore is written correctly by write_findings."""
        suppressed = self._finding()
        n, rows = _write_findings_with_mock([suppressed], suppress_cols=True)
        self.assertEqual(n, 1)
        self.assertTrue(rows[0]["is_suppressed"])
        self.assertEqual(rows[0]["suppression_reason"], "FALSE_POSITIVE_LINUX_BUILD")



# =============================================================================
# Migration 0053 — Multi-platform ingest + image size fields
# =============================================================================
# =============================================================================
# parse_platforms (migration 0053)
# =============================================================================

class TestParsePlatforms(unittest.TestCase):
    """
    parse_platforms() converts JSON platform args to list[str].
    Empty / missing → [] (legacy mode).
    Single string → ["linux/amd64"].
    Array → ["linux/amd64", "linux/arm64"].
    """

    def _p(self, s):
        return _si.parse_platforms(s)

    def test_none_returns_empty_list(self):
        self.assertEqual(self._p(None), [])

    def test_empty_string_returns_empty_list(self):
        self.assertEqual(self._p(""), [])

    def test_json_array_dual_arch(self):
        result = self._p('["linux/amd64","linux/arm64"]')
        self.assertEqual(result, ["linux/amd64", "linux/arm64"])

    def test_json_array_single_platform(self):
        result = self._p('["linux/amd64"]')
        self.assertEqual(result, ["linux/amd64"])

    def test_json_string_single_platform(self):
        """A bare JSON string (not array) is accepted as a single-element list."""
        result = self._p('"linux/amd64"')
        self.assertEqual(result, ["linux/amd64"])

    def test_json_empty_array(self):
        self.assertEqual(self._p("[]"), [])

    def test_json_array_filters_empty_strings(self):
        """Null / empty slots in the JSON array are dropped."""
        result = self._p('["linux/amd64", "", "linux/arm64"]')
        self.assertEqual(result, ["linux/amd64", "linux/arm64"])

    def test_order_preserved(self):
        result = self._p('["linux/arm64","linux/amd64"]')
        self.assertEqual(result[0], "linux/arm64")
        self.assertEqual(result[1], "linux/amd64")


# =============================================================================
# parse_size_map (migration 0053)
# =============================================================================

class TestParseSizeMap(unittest.TestCase):
    """
    parse_size_map() converts platform→size JSON to dict[str, int].
    None / "" → {}.
    Null values in the JSON are dropped.
    Values are coerced to int.
    """

    def _p(self, s):
        return _si.parse_size_map(s)

    def test_none_returns_empty_dict(self):
        self.assertEqual(self._p(None), {})

    def test_empty_string_returns_empty_dict(self):
        self.assertEqual(self._p(""), {})

    def test_empty_json_object(self):
        self.assertEqual(self._p("{}"), {})

    def test_dual_arch_map(self):
        result = self._p('{"linux/amd64":12345678,"linux/arm64":12100000}')
        self.assertEqual(result["linux/amd64"], 12345678)
        self.assertEqual(result["linux/arm64"], 12100000)

    def test_null_value_dropped(self):
        """Null values must not appear in the result dict."""
        result = self._p('{"linux/amd64":12345678,"linux/arm64":null}')
        self.assertIn("linux/amd64", result)
        self.assertNotIn("linux/arm64", result)

    def test_float_coerced_to_int(self):
        """JSON numbers like 1.23e7 should be coerced to int."""
        result = self._p('{"linux/amd64":12345678.0}')
        self.assertIsInstance(result["linux/amd64"], int)
        self.assertEqual(result["linux/amd64"], 12345678)

    def test_zero_value_kept(self):
        """Zero is a valid size (e.g. scratch image with no layers)."""
        result = self._p('{"linux/amd64":0}')
        self.assertIn("linux/amd64", result)
        self.assertEqual(result["linux/amd64"], 0)


# =============================================================================
# parse_ref_map (migration 0053)
# =============================================================================

class TestParseRefMap(unittest.TestCase):
    """
    parse_ref_map() converts platform→OCI-ref JSON to dict[str, str].
    None / "" → {}.
    Null / empty string values in the JSON are dropped.
    """

    def _p(self, s):
        return _si.parse_ref_map(s)

    def test_none_returns_empty_dict(self):
        self.assertEqual(self._p(None), {})

    def test_empty_string_returns_empty_dict(self):
        self.assertEqual(self._p(""), {})

    def test_empty_json_object(self):
        self.assertEqual(self._p("{}"), {})

    def test_dual_arch_refs(self):
        result = self._p(
            '{"linux/amd64":"ghcr.io/gwshield/redis:v7.4.8@sha256:aaa",'
            '"linux/arm64":"ghcr.io/gwshield/redis:v7.4.8@sha256:bbb"}'
        )
        self.assertEqual(result["linux/amd64"], "ghcr.io/gwshield/redis:v7.4.8@sha256:aaa")
        self.assertEqual(result["linux/arm64"], "ghcr.io/gwshield/redis:v7.4.8@sha256:bbb")

    def test_null_value_dropped(self):
        result = self._p('{"linux/amd64":"ghcr.io/gwshield/redis:v7.4.8@sha256:aaa","linux/arm64":null}')
        self.assertIn("linux/amd64", result)
        self.assertNotIn("linux/arm64", result)

    def test_empty_string_value_dropped(self):
        result = self._p('{"linux/amd64":"","linux/arm64":"ghcr.io/gwshield/redis:v7.4.8@sha256:bbb"}')
        self.assertNotIn("linux/amd64", result)
        self.assertIn("linux/arm64", result)


# =============================================================================
# _build_snapshot_payload (migration 0053)
# =============================================================================

class TestBuildSnapshotPayload(unittest.TestCase):
    """
    _build_snapshot_payload() constructs the image_metadata_snapshots insert dict.

    Core behaviour:
    - Always includes image_id, version_id, sbom_ref, provenance_ref,
      raw_payload, snapshotted_at, cve_count (None), scan_status, scanner.
    - Migration 0053 columns (platform, arch, image_size_bytes,
      runnable_size_bytes) are ONLY included in the dict when non-None.
      This ensures backward-compat with pre-0053 DB schemas.
    """

    _COMMON_KWARGS = dict(
        image_id="img-001",
        version_id="ver-001",
        sbom_ref="ghcr.io/gwshield/redis:v7.4.8",
        provenance="https://github.com/gwshield/images/...",
        promoted_at="2026-03-14T10:00:00Z",
        name="redis",
        version="v7.4.8",
        base_version="v7.4.8",
        profile="",
        digest="sha256:abc123",
        tags="ghcr.io/gwshield/redis:v7.4.8",
        cosign_id="https://github.com/gwshield/images/...",
        image_type="service",
    )

    def test_core_columns_present(self):
        payload = _si._build_snapshot_payload(**self._COMMON_KWARGS)
        for col in ("image_id", "version_id", "sbom_ref", "provenance_ref",
                    "raw_payload", "snapshotted_at", "cve_count", "scan_status"):
            self.assertIn(col, payload, f"Core column missing: {col}")

    def test_platform_absent_when_none(self):
        """Without platform kwarg, 'platform' must NOT appear in payload."""
        payload = _si._build_snapshot_payload(**self._COMMON_KWARGS)
        self.assertNotIn("platform", payload)

    def test_arch_absent_when_none(self):
        payload = _si._build_snapshot_payload(**self._COMMON_KWARGS)
        self.assertNotIn("arch", payload)

    def test_image_size_bytes_absent_when_none(self):
        payload = _si._build_snapshot_payload(**self._COMMON_KWARGS)
        self.assertNotIn("image_size_bytes", payload)

    def test_runnable_size_bytes_absent_when_none(self):
        payload = _si._build_snapshot_payload(**self._COMMON_KWARGS)
        self.assertNotIn("runnable_size_bytes", payload)

    def test_platform_present_when_supplied(self):
        payload = _si._build_snapshot_payload(
            **self._COMMON_KWARGS, platform="linux/amd64", arch="amd64"
        )
        self.assertEqual(payload["platform"], "linux/amd64")
        self.assertEqual(payload["arch"], "amd64")

    def test_image_size_bytes_present_when_supplied(self):
        payload = _si._build_snapshot_payload(
            **self._COMMON_KWARGS, image_size_bytes=12345678
        )
        self.assertEqual(payload["image_size_bytes"], 12345678)

    def test_runnable_size_bytes_present_when_supplied(self):
        payload = _si._build_snapshot_payload(
            **self._COMMON_KWARGS, runnable_size_bytes=26000000
        )
        self.assertEqual(payload["runnable_size_bytes"], 26000000)

    def test_all_0053_columns_when_fully_supplied(self):
        payload = _si._build_snapshot_payload(
            **self._COMMON_KWARGS,
            platform="linux/arm64",
            arch="arm64",
            image_size_bytes=11800000,
            runnable_size_bytes=25000000,
        )
        self.assertEqual(payload["platform"], "linux/arm64")
        self.assertEqual(payload["arch"], "arm64")
        self.assertEqual(payload["image_size_bytes"], 11800000)
        self.assertEqual(payload["runnable_size_bytes"], 25000000)

    def test_cve_count_initially_none(self):
        """Snapshot is created before scanning — cve_count must be None."""
        payload = _si._build_snapshot_payload(**self._COMMON_KWARGS)
        self.assertIsNone(payload["cve_count"])

    def test_scan_status_initially_unknown(self):
        payload = _si._build_snapshot_payload(**self._COMMON_KWARGS)
        self.assertEqual(payload["scan_status"], "unknown")

    def test_snapshotted_at_matches_promoted_at(self):
        payload = _si._build_snapshot_payload(**self._COMMON_KWARGS)
        self.assertEqual(payload["snapshotted_at"], "2026-03-14T10:00:00Z")

    def test_raw_payload_contains_name_and_version(self):
        payload = _si._build_snapshot_payload(**self._COMMON_KWARGS)
        rp = payload["raw_payload"]
        self.assertEqual(rp["name"], "redis")
        self.assertEqual(rp["version"], "v7.4.8")


# =============================================================================
# cmd_promote — per-platform path (migration 0053)
# =============================================================================

class _MockDBForPromote:
    """
    Minimal SupabaseClient stand-in for cmd_promote tests.
    Records all insert / upsert / update / delete / select calls.
    """

    def __init__(self):
        self.inserted_tables: dict[str, list[dict]] = {}
        self.upserted_tables: dict[str, list[dict]] = {}
        self.updated_tables: dict[str, list[dict]] = {}
        self.deleted_tables: dict[str, list[dict]] = {}
        self.selected_tables: dict[str, list] = {}
        self._row_counter = 0

    def _next_id(self, prefix="row"):
        self._row_counter += 1
        return f"{prefix}-{self._row_counter:04d}-uuid"

    def upsert_image(self, slug, insert_fields, update_fields):
        row = {"id": self._next_id("img"), "slug": slug,
               **insert_fields, **update_fields}
        self.upserted_tables.setdefault("images", []).append(row)
        return row

    def upsert(self, table, row, on_conflict):
        rid = row.get("id", self._next_id(table[:3]))
        stored = dict(row, id=rid)
        self.upserted_tables.setdefault(table, []).append(stored)
        return stored

    def insert(self, table, row):
        stored = dict(row, id=self._next_id(table[:3]))
        self.inserted_tables.setdefault(table, []).append(stored)
        return stored

    def select(self, table, filters):
        return self.selected_tables.get(table, [])

    def update(self, table, filters, row):
        self.updated_tables.setdefault(table, []).append((filters, row))

    def delete(self, table, filters):
        self.deleted_tables.setdefault(table, []).append(filters)


def _make_promote_args(
    name="redis",
    version="v7.4.8",
    base_version="v7.4.8",
    profile="",
    digest="sha256:abc123",
    tags="ghcr.io/gwshield/redis:v7.4.8",
    cosign_identity="https://github.com/gwshield/images/...",
    promoted_at="2026-03-14T10:00:00Z",
    image_type=None,
    platforms=None,
    image_size_json=None,
    runnable_size_json=None,
    sbom_refs_json=None,
    provenance_refs_json=None,
):
    """Build a minimal argparse-like Namespace for cmd_promote."""
    import argparse
    return argparse.Namespace(
        name=name,
        version=version,
        base_version=base_version,
        profile=profile,
        digest=digest,
        tags=tags,
        cosign_identity=cosign_identity,
        promoted_at=promoted_at,
        image_type=image_type,
        platforms=platforms,
        image_size_json=image_size_json,
        runnable_size_json=runnable_size_json,
        sbom_refs_json=sbom_refs_json,
        provenance_refs_json=provenance_refs_json,
    )


class TestCmdPromoteLegacyPath(unittest.TestCase):
    """
    cmd_promote with no --platforms → legacy single-row snapshot.
    Verifies:
      - Exactly 1 snapshot row inserted
      - No 'platform' column in snapshot payload
      - No 'platforms' column in version payload
      - arch tag uses legacy "linux/amd64,linux/arm64" string
    """

    def setUp(self):
        self.db = _MockDBForPromote()
        args = _make_promote_args()
        _si.cmd_promote(args, self.db)

    def test_exactly_one_snapshot_inserted(self):
        snaps = self.db.inserted_tables.get("image_metadata_snapshots", [])
        self.assertEqual(len(snaps), 1)

    def test_snapshot_has_no_platform_field(self):
        snap = self.db.inserted_tables["image_metadata_snapshots"][0]
        self.assertNotIn("platform", snap)

    def test_snapshot_has_no_image_size_bytes_field(self):
        snap = self.db.inserted_tables["image_metadata_snapshots"][0]
        self.assertNotIn("image_size_bytes", snap)

    def test_version_has_no_platforms_field(self):
        """image_versions.platforms must be absent in legacy mode."""
        ver_rows = self.db.upserted_tables.get("image_versions", [])
        self.assertTrue(len(ver_rows) > 0)
        ver = ver_rows[0]
        self.assertNotIn("platforms", ver)

    def test_arch_tag_is_legacy_string(self):
        """Legacy path uses the hardcoded 'linux/amd64,linux/arm64' arch tag."""
        arch_tags = [
            t["tag_value"]
            for t in self.db.upserted_tables.get("image_tags", [])
            if t["tag_key"] == "arch"
        ]
        self.assertEqual(len(arch_tags), 1)
        self.assertEqual(arch_tags[0], "linux/amd64,linux/arm64")


class TestCmdPromotePerPlatformPath(unittest.TestCase):
    """
    cmd_promote with --platforms '["linux/amd64","linux/arm64"]' →
    two snapshot rows, one per platform.
    Verifies:
      - Exactly 2 snapshot rows inserted
      - Each row has 'platform' and 'arch' fields
      - Correct platform→arch derivation (amd64, arm64)
      - image_versions.platforms field populated
      - Size fields present when supplied, absent when not
      - arch tag reflects the platforms list (joined)
    """

    def setUp(self):
        self.db = _MockDBForPromote()
        args = _make_promote_args(
            platforms='["linux/amd64","linux/arm64"]',
            image_size_json='{"linux/amd64":12345678,"linux/arm64":12100000}',
            runnable_size_json='{"linux/amd64":26000000,"linux/arm64":25900000}',
            sbom_refs_json=(
                '{"linux/amd64":"ghcr.io/gwshield/redis:v7.4.8@sha256:aaa",'
                '"linux/arm64":"ghcr.io/gwshield/redis:v7.4.8@sha256:bbb"}'
            ),
        )
        _si.cmd_promote(args, self.db)

    def test_exactly_two_snapshots_inserted(self):
        snaps = self.db.inserted_tables.get("image_metadata_snapshots", [])
        self.assertEqual(len(snaps), 2)

    def test_snapshot_platforms_are_correct(self):
        snaps = self.db.inserted_tables["image_metadata_snapshots"]
        platforms = {s["platform"] for s in snaps}
        self.assertEqual(platforms, {"linux/amd64", "linux/arm64"})

    def test_snapshot_arch_derived_from_platform(self):
        snaps = self.db.inserted_tables["image_metadata_snapshots"]
        for snap in snaps:
            expected_arch = snap["platform"].split("/")[1]
            self.assertEqual(snap["arch"], expected_arch)

    def test_snapshot_image_size_bytes_populated(self):
        snaps = self.db.inserted_tables["image_metadata_snapshots"]
        sizes = {s["platform"]: s["image_size_bytes"] for s in snaps}
        self.assertEqual(sizes["linux/amd64"], 12345678)
        self.assertEqual(sizes["linux/arm64"], 12100000)

    def test_snapshot_runnable_size_bytes_populated(self):
        snaps = self.db.inserted_tables["image_metadata_snapshots"]
        sizes = {s["platform"]: s["runnable_size_bytes"] for s in snaps}
        self.assertEqual(sizes["linux/amd64"], 26000000)
        self.assertEqual(sizes["linux/arm64"], 25900000)

    def test_snapshot_sbom_ref_per_platform(self):
        snaps = self.db.inserted_tables["image_metadata_snapshots"]
        refs = {s["platform"]: s["sbom_ref"] for s in snaps}
        self.assertEqual(refs["linux/amd64"], "ghcr.io/gwshield/redis:v7.4.8@sha256:aaa")
        self.assertEqual(refs["linux/arm64"], "ghcr.io/gwshield/redis:v7.4.8@sha256:bbb")

    def test_version_platforms_field_populated(self):
        ver_rows = self.db.upserted_tables.get("image_versions", [])
        self.assertTrue(len(ver_rows) > 0)
        ver = ver_rows[0]
        self.assertIn("platforms", ver)
        self.assertIsInstance(ver["platforms"], list)
        self.assertIn("linux/amd64", ver["platforms"])
        self.assertIn("linux/arm64", ver["platforms"])

    def test_arch_tag_is_joined_platform_list(self):
        arch_tags = [
            t["tag_value"]
            for t in self.db.upserted_tables.get("image_tags", [])
            if t["tag_key"] == "arch"
        ]
        self.assertEqual(len(arch_tags), 1)
        # Both platforms appear in the arch tag value
        self.assertIn("linux/amd64", arch_tags[0])
        self.assertIn("linux/arm64", arch_tags[0])


class TestCmdPromoteSinglePlatform(unittest.TestCase):
    """
    cmd_promote with --platforms '["linux/amd64"]' (amd64-only image).
    Verifies:
      - Exactly 1 snapshot row with platform='linux/amd64'
      - image_versions.platforms = ['linux/amd64']
      - Size fields present when supplied
    """

    def setUp(self):
        self.db = _MockDBForPromote()
        args = _make_promote_args(
            name="postgres",
            version="v15.17",
            base_version="v15.17",
            profile="",
            platforms='["linux/amd64"]',
            image_size_json='{"linux/amd64":34567890}',
            runnable_size_json='{"linux/amd64":80000000}',
        )
        _si.cmd_promote(args, self.db)

    def test_one_snapshot_with_correct_platform(self):
        snaps = self.db.inserted_tables.get("image_metadata_snapshots", [])
        self.assertEqual(len(snaps), 1)
        self.assertEqual(snaps[0]["platform"], "linux/amd64")
        self.assertEqual(snaps[0]["arch"], "amd64")

    def test_image_size_populated(self):
        snap = self.db.inserted_tables["image_metadata_snapshots"][0]
        self.assertEqual(snap["image_size_bytes"], 34567890)

    def test_runnable_size_populated(self):
        snap = self.db.inserted_tables["image_metadata_snapshots"][0]
        self.assertEqual(snap["runnable_size_bytes"], 80000000)

    def test_version_platforms_single_element(self):
        ver_rows = self.db.upserted_tables.get("image_versions", [])
        self.assertTrue(len(ver_rows) > 0)
        self.assertEqual(ver_rows[0]["platforms"], ["linux/amd64"])


class TestCmdPromoteSizeFieldsOptional(unittest.TestCase):
    """
    cmd_promote with --platforms but without size/ref JSON args.
    Size fields must not appear in snapshot payload (no spurious None writes).
    """

    def setUp(self):
        self.db = _MockDBForPromote()
        args = _make_promote_args(
            platforms='["linux/amd64","linux/arm64"]',
            # no image_size_json, runnable_size_json, sbom_refs_json
        )
        _si.cmd_promote(args, self.db)

    def test_two_snapshots_created(self):
        snaps = self.db.inserted_tables.get("image_metadata_snapshots", [])
        self.assertEqual(len(snaps), 2)

    def test_image_size_bytes_absent_when_not_supplied(self):
        for snap in self.db.inserted_tables["image_metadata_snapshots"]:
            self.assertNotIn("image_size_bytes", snap)

    def test_runnable_size_bytes_absent_when_not_supplied(self):
        for snap in self.db.inserted_tables["image_metadata_snapshots"]:
            self.assertNotIn("runnable_size_bytes", snap)

    def test_platforms_still_populated_on_version(self):
        ver_rows = self.db.upserted_tables.get("image_versions", [])
        self.assertIn("platforms", ver_rows[0])




class TestBuildSnapshotPayloadProvenanceRef(unittest.TestCase):
    """
    _build_snapshot_payload() correctly sets provenance_ref.

    provenance_ref receives the per-platform OCI attestation ref from
    --provenance-refs-json (or falls back to cosign_id in legacy mode).
    These tests verify the field is correctly carried into the snapshot dict.
    """

    _BASE = dict(
        image_id="img-001",
        version_id="ver-001",
        sbom_ref="ghcr.io/gwshield/redis:v7.4.8@sha256:sbomaaa",
        promoted_at="2026-03-14T10:00:00Z",
        name="redis",
        version="v7.4.8",
        base_version="v7.4.8",
        profile="",
        digest="sha256:abc123",
        tags="ghcr.io/gwshield/redis:v7.4.8",
        cosign_id="https://github.com/gwshield/images/.github/workflows/promote.yml@refs/heads/main",
        image_type="service",
    )

    def test_provenance_ref_set_from_explicit_value(self):
        """An explicit provenance OCI ref is stored verbatim."""
        prov_ref = "ghcr.io/gwshield/redis:v7.4.8@sha256:provaaa"
        payload = _si._build_snapshot_payload(**self._BASE, provenance=prov_ref)
        self.assertEqual(payload["provenance_ref"], prov_ref)

    def test_provenance_ref_none_when_not_supplied(self):
        """provenance=None must produce provenance_ref=None in payload."""
        payload = _si._build_snapshot_payload(**self._BASE, provenance=None)
        self.assertIsNone(payload["provenance_ref"])

    def test_provenance_ref_distinct_from_sbom_ref(self):
        """provenance_ref and sbom_ref must be independent fields."""
        payload = _si._build_snapshot_payload(
            **self._BASE,
            provenance="ghcr.io/gwshield/redis:v7.4.8@sha256:provXXX",
        )
        self.assertNotEqual(payload["provenance_ref"], payload["sbom_ref"])


class TestCmdPromoteProvenanceRefs(unittest.TestCase):
    """
    cmd_promote correctly routes --provenance-refs-json into snapshot rows.

    Mirrors the sbom_ref test pattern in TestCmdPromotePerPlatformPath:
    each platform snapshot must carry the matching provenance OCI ref.
    """

    def setUp(self):
        self.db = _MockDBForPromote()
        args = _make_promote_args(
            platforms='["linux/amd64","linux/arm64"]',
            sbom_refs_json=(
                '{"linux/amd64":"ghcr.io/gwshield/redis:v7.4.8@sha256:sbomaaa",'
                '"linux/arm64":"ghcr.io/gwshield/redis:v7.4.8@sha256:sbombbb"}'
            ),
            provenance_refs_json=(
                '{"linux/amd64":"ghcr.io/gwshield/redis:v7.4.8@sha256:provaaa",'
                '"linux/arm64":"ghcr.io/gwshield/redis:v7.4.8@sha256:provbbb"}'
            ),
        )
        _si.cmd_promote(args, self.db)

    def test_provenance_ref_per_platform_amd64(self):
        snaps = self.db.inserted_tables["image_metadata_snapshots"]
        refs = {s["platform"]: s["provenance_ref"] for s in snaps}
        self.assertEqual(refs["linux/amd64"], "ghcr.io/gwshield/redis:v7.4.8@sha256:provaaa")

    def test_provenance_ref_per_platform_arm64(self):
        snaps = self.db.inserted_tables["image_metadata_snapshots"]
        refs = {s["platform"]: s["provenance_ref"] for s in snaps}
        self.assertEqual(refs["linux/arm64"], "ghcr.io/gwshield/redis:v7.4.8@sha256:provbbb")

    def test_provenance_ref_independent_of_sbom_ref(self):
        snaps = self.db.inserted_tables["image_metadata_snapshots"]
        for snap in snaps:
            self.assertNotEqual(snap["provenance_ref"], snap["sbom_ref"])

    def test_provenance_ref_present_in_all_snapshots(self):
        snaps = self.db.inserted_tables["image_metadata_snapshots"]
        for snap in snaps:
            self.assertIn("provenance_ref", snap)
            self.assertIsNotNone(snap["provenance_ref"])


class TestCmdPromoteProvenanceRefFallback(unittest.TestCase):
    """
    When --provenance-refs-json is absent, provenance_ref falls back to
    cosign_identity (legacy single-row behaviour).
    """

    def setUp(self):
        self.db = _MockDBForPromote()
        # No provenance_refs_json — legacy single-row path
        args = _make_promote_args()  # no platforms, no provenance_refs_json
        _si.cmd_promote(args, self.db)

    def test_provenance_ref_falls_back_to_cosign_id(self):
        snaps = self.db.inserted_tables["image_metadata_snapshots"]
        self.assertEqual(len(snaps), 1)
        # In legacy path, provenance= is set to cosign_id in _build_snapshot_payload
        snap = snaps[0]
        self.assertIn("provenance_ref", snap)
        # cosign_id from _make_promote_args default
        self.assertEqual(
            snap["provenance_ref"],
            "https://github.com/gwshield/images/...",
        )


class TestParseRefMapProvenanceRefs(unittest.TestCase):
    """
    parse_ref_map() handles provenance_refs_json correctly.
    (Reuses the same function as sbom_refs_json — verify it works for provenance too.)
    """

    def test_parse_two_platform_refs(self):
        result = _si.parse_ref_map(
            '{"linux/amd64":"ghcr.io/gwshield/redis:v7.4.8@sha256:provaaa",'
            '"linux/arm64":"ghcr.io/gwshield/redis:v7.4.8@sha256:provbbb"}'
        )
        self.assertEqual(result["linux/amd64"], "ghcr.io/gwshield/redis:v7.4.8@sha256:provaaa")
        self.assertEqual(result["linux/arm64"], "ghcr.io/gwshield/redis:v7.4.8@sha256:provbbb")

    def test_empty_string_returns_empty_dict(self):
        self.assertEqual(_si.parse_ref_map(""), {})

    def test_none_returns_empty_dict(self):
        self.assertEqual(_si.parse_ref_map(None), {})

    def test_null_values_dropped(self):
        result = _si.parse_ref_map('{"linux/amd64":"ghcr.io/gwshield/redis@sha256:aaa","linux/arm64":null}')
        self.assertIn("linux/amd64", result)
        self.assertNotIn("linux/arm64", result)


# =============================================================================
# Entry point — can be run without pytest
# =============================================================================

if __name__ == "__main__":
    loader  = unittest.TestLoader()
    suite   = loader.loadTestsFromModule(sys.modules[__name__])
    runner  = unittest.TextTestRunner(verbosity=2)
    result  = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
