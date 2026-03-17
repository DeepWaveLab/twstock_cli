#!/usr/bin/env python3
"""Generate integration test cases for all endpoints in the registry.

Reads the ENDPOINTS dict from twstock_cli/endpoints.py, checks which
endpoints already have test cases in tests/integration/test_cases.json,
and generates smoke + dry-run test cases for uncovered endpoints.

Output files:
    tests/integration/test_cases_twse_gen.json   — TWSE OpenAPI
    tests/integration/test_cases_tpex_gen.json   — TPEX OpenAPI
    tests/integration/test_cases_web_gen.json    — TWSE Web API

Usage:
    uv run python scripts/generate_integration_tests.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Add project root to path so we can import twstock_cli
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from twstock_cli.endpoints import ENDPOINTS, TPEX_BASE_URL, EndpointDef  # noqa: E402

INTEGRATION_DIR = PROJECT_ROOT / "tests" / "integration"

# A recent known trading day for web endpoint tests (Monday 2026-03-16).
WEB_DEFAULT_DATE = "20260316"
# Well-known stock codes for --code filter tests.
TWSE_STOCK_CODE = "2330"  # TSMC
TPEX_STOCK_CODE = "6547"  # A known OTC stock

# Endpoints known to be broken server-side (return HTML/redirect/empty body).
# These are excluded from smoke tests entirely (only dry-run is generated).
KNOWN_BROKEN_ENDPOINTS: set[str] = {
    "company.t187ap46-l-12",  # Returns 302 redirect (nginx) instead of JSON
}


def classify_exchange(ep: EndpointDef) -> str:
    """Classify an endpoint as 'twse', 'tpex', or 'web'."""
    if ep.date_param is not None:
        return "web"
    if ep.base_url == TPEX_BASE_URL:
        return "tpex"
    return "twse"


def _load_existing_endpoint_refs() -> set[str]:
    """Return set of dotted endpoint names already covered by hand-written tests."""
    existing = set()
    cases_file = INTEGRATION_DIR / "test_cases.json"
    if not cases_file.exists():
        return existing
    raw = json.loads(cases_file.read_text())
    for case in raw:
        if "id" not in case:
            continue
        cmd = case.get("command", [])
        # Look for endpoint refs in fetch commands: ["fetch", "stock.stock-day-all", ...]
        if len(cmd) >= 2 and cmd[0] == "fetch" and "." in cmd[1] and not cmd[1].startswith("-"):
            existing.add(cmd[1])
        # Look for domain shortcut commands: ["stock", "stock-day-all", ...]
        # Reconstruct dotted name from group + cli_name
        if len(cmd) >= 2 and not cmd[0].startswith("-") and cmd[0] != "fetch":
            group = cmd[0]
            cli_name = cmd[1] if not cmd[1].startswith("-") else None
            if cli_name:
                dotted = f"{group}.{cli_name}"
                existing.add(dotted)
    return existing


def _make_smoke_id(key: str) -> str:
    """Convert endpoint key like 'otc.mainboard-daily-close-quotes' to test ID."""
    return f"smoke-gen-{key.replace('.', '-')}"


def _make_dryrun_id(key: str) -> str:
    return f"dryrun-gen-{key.replace('.', '-')}"


def _required_fields(ep: EndpointDef) -> list[str] | None:
    """Determine required_fields for the smoke test.

    Only use explicitly declared ``ep.fields`` — these are known to appear
    in the API response.  Do NOT use ``code_field`` because many endpoints
    define a code_field for filtering but the response may not contain it
    (e.g. market index endpoints, aggregate summaries).
    """
    if ep.fields:
        return ep.fields[:3]
    return None


def _make_dryrun_case(key: str, ep: EndpointDef, exchange: str) -> dict:
    """Generate a dry-run test case (no API needed)."""
    return {
        "id": _make_dryrun_id(key),
        "description": f"Dry-run: {key} URL construction",
        "tags": ["dry-run-gen", exchange, ep.group],
        "exchange": exchange,
        "requires_api": False,
        "command": ["fetch", key, "--dry-run"],
        "expected": {
            "exit_code": 0,
            "output_format": "object",
            "contains_keys": ["dry_run", "method", "url"],
        },
    }


def _make_smoke_case(key: str, ep: EndpointDef, exchange: str) -> dict:
    """Generate a smoke test case (live API)."""
    command = ["fetch", key, "--json", "--limit", "3"]

    # Web endpoints need --date; some also need --stock-no.
    if exchange == "web":
        command.extend(["--date", WEB_DEFAULT_DATE])
        if ep.stock_param:
            command.extend(["--stock-no", TWSE_STOCK_CODE])

    expected: dict = {
        "exit_code": 0,
        "output_format": "envelope",
        "ok": True,
        "allow_empty": True,
        "max_records": 3,
    }

    # Only assert required_fields for non-web endpoints or web endpoints
    # with a stock_param (per-stock endpoints have predictable field names).
    # Web aggregate endpoints (mi-index, bfi82u, etc.) use tables/special
    # formats where field names don't match ep.fields after alias mapping.
    rf = _required_fields(ep)
    if rf and exchange != "web":
        expected["required_fields"] = rf
    elif rf and exchange == "web" and ep.stock_param:
        expected["required_fields"] = rf

    return {
        "id": _make_smoke_id(key),
        "description": f"Smoke: {key} ({ep.description})",
        "tags": ["smoke-gen", exchange, ep.group],
        "exchange": exchange,
        "requires_api": True,
        "command": command,
        "expected": expected,
    }


def generate() -> dict[str, list[dict]]:
    """Generate test cases grouped by exchange."""
    existing_refs = _load_existing_endpoint_refs()
    print(f"Found {len(existing_refs)} endpoints already covered in test_cases.json")

    buckets: dict[str, list[dict]] = {"twse": [], "tpex": [], "web": []}
    generated_ids: set[str] = set()
    skipped = 0

    for key, ep in sorted(ENDPOINTS.items()):
        exchange = classify_exchange(ep)

        # Always generate dry-run (even if endpoint has existing smoke tests)
        dryrun = _make_dryrun_case(key, ep, exchange)
        assert dryrun["id"] not in generated_ids, f"Duplicate ID: {dryrun['id']}"
        generated_ids.add(dryrun["id"])
        buckets[exchange].append(dryrun)

        # Generate smoke test only if not already covered and not known-broken
        dotted = f"{ep.group}.{ep.cli_name}"
        if key in KNOWN_BROKEN_ENDPOINTS:
            skipped += 1
        elif key not in existing_refs and dotted not in existing_refs:
            smoke = _make_smoke_case(key, ep, exchange)
            assert smoke["id"] not in generated_ids, f"Duplicate ID: {smoke['id']}"
            generated_ids.add(smoke["id"])
            buckets[exchange].append(smoke)
        else:
            skipped += 1

    print(f"Skipped {skipped} endpoints already covered by hand-written tests")
    for exchange, cases in buckets.items():
        dryrun_count = sum(1 for c in cases if not c["requires_api"])
        smoke_count = sum(1 for c in cases if c["requires_api"])
        print(f"  {exchange}: {dryrun_count} dry-run + {smoke_count} smoke = {len(cases)} total")

    return buckets


def write_output(buckets: dict[str, list[dict]]) -> None:
    """Write generated test cases to JSON files."""
    for exchange, cases in buckets.items():
        if not cases:
            continue
        # Add a leading comment entry for readability
        output = [
            {"_comment": f"=== AUTO-GENERATED {exchange.upper()} tests — do not edit manually ==="},
            *cases,
        ]
        outfile = INTEGRATION_DIR / f"test_cases_{exchange}_gen.json"
        outfile.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
        print(f"Wrote {len(cases)} test cases to {outfile.relative_to(PROJECT_ROOT)}")


def main() -> None:
    buckets = generate()
    write_output(buckets)

    total = sum(len(cases) for cases in buckets.values())
    print(f"\nTotal generated: {total} test cases across {len(ENDPOINTS)} endpoints")


if __name__ == "__main__":
    main()
