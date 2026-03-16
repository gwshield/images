#!/usr/bin/env python3
"""
make_smoke_result.py — synthesise smoke-result.json from smoke.sh output.

Usage:
  python3 make_smoke_result.py <smoke_out_file> <image_ref> <overall>
                               <pass_count> <fail_count> <duration_ms>
                               <out_path>

Called by promote.yml after running the post-promote smoke test.  The
smoke_out_file contains the captured stdout/stderr of smoke.sh; this script
parses [PASS] / [FAIL] lines into structured check entries and writes a
smoke-result.json compatible with supabase_ingress.py's 'smoke' subcommand.
"""

import datetime
import json
import sys


def main() -> None:
    (
        smoke_out_file,
        image_ref,
        overall,
        pass_count,
        fail_count,
        duration_ms,
        out_path,
    ) = sys.argv[1:8]

    checks: list[dict] = []
    with open(smoke_out_file) as fh:
        for line in fh:
            s = line.strip()
            if s.startswith("[PASS]"):
                checks.append({"id": s[6:].strip()[:80], "status": "passed"})
            elif s.startswith("[FAIL]"):
                checks.append({"id": s[6:].strip()[:80], "status": "failed"})

    result = {
        "schema_version": "1.0",
        "image_ref": image_ref,
        "manifest": None,
        "manifest_schema": None,
        "ran_at": datetime.datetime.now(datetime.timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        ),
        "overall_status": overall,
        "pass_count": int(pass_count or 0),
        "fail_count": int(fail_count or 0),
        "skip_count": 0,
        "duration_ms": int(duration_ms or 0),
        "checks": checks,
    }

    with open(out_path, "w") as fh:
        json.dump(result, fh, indent=2)

    print(
        f"smoke-result.json written: {result['overall_status']} "
        f"({result['pass_count']}P/{result['fail_count']}F)"
    )


if __name__ == "__main__":
    main()
