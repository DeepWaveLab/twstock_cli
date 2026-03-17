"""Data-driven integration test runner.

Reads test cases from ``test_cases.json`` and validates each command
invocation against the real TWSE API (or deterministically for cases
that don't require network access).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from twstock_cli.cli import cli

CASES_FILE = Path(__file__).parent / "test_cases.json"


def _load_cases() -> list[tuple[str, dict]]:
    raw: list[dict] = json.loads(CASES_FILE.read_text())
    # Filter out comment-only entries (have _comment but no id).
    cases = [c for c in raw if "id" in c]
    # Sort so deterministic (requires_api=false) run first.
    cases.sort(key=lambda c: c.get("requires_api", True))
    return [(c["id"], c) for c in cases]


def _parse_output(output: str, fmt: str) -> list[dict]:
    """Parse CLI stdout into a list of records based on *fmt*."""
    if fmt == "envelope":
        envelope = json.loads(output)
        return envelope.get("data", [])
    if fmt == "ndjson":
        return [json.loads(line) for line in output.strip().split("\n") if line.strip()]
    if fmt == "array":
        return json.loads(output)
    if fmt == "object":
        return [json.loads(output)]
    raise ValueError(f"Unknown output format: {fmt}")


# ---------------------------------------------------------------------------
# Parametrised test
# ---------------------------------------------------------------------------

_CASES = _load_cases()


@pytest.mark.integration
@pytest.mark.parametrize("case_id,case", _CASES, ids=[c[0] for c in _CASES])
def test_integration(case_id: str, case: dict) -> None:
    expected = case["expected"]
    runner = CliRunner()

    # Stdin support
    kwargs: dict = {}
    if case.get("stdin"):
        stdin = case["stdin"]
        kwargs["input"] = json.dumps(stdin) if isinstance(stdin, dict) else stdin

    result = runner.invoke(cli, case["command"], catch_exceptions=False, **kwargs)

    # -- 1. Exit code -------------------------------------------------------
    assert result.exit_code == expected["exit_code"], (
        f"[{case_id}] exit_code: expected {expected['exit_code']}, "
        f"got {result.exit_code}\nstdout: {result.output[:500]}"
    )

    # -- 2. Error assertions (exit != 0) ------------------------------------
    if result.exit_code != 0:
        if expected.get("error_code"):
            envelope = json.loads(result.output)
            assert envelope["error"]["code"] == expected["error_code"], (
                f"[{case_id}] error_code: expected {expected['error_code']}, "
                f"got {envelope['error']['code']}"
            )
            if expected.get("error_message_contains"):
                assert expected["error_message_contains"] in envelope["error"]["message"]
        return  # Nothing more to check for error cases

    # -- 3. Parse output ----------------------------------------------------
    # Skip parsing when no output-dependent assertions exist.
    needs_parse = any(
        expected.get(k)
        for k in ("ok", "min_records", "max_records", "required_fields",
                   "absent_fields", "contains_keys", "field_types")
    )
    fmt = expected.get("output_format", "envelope")
    records: list[dict] = _parse_output(result.output, fmt) if needs_parse else []

    # -- 4. Envelope ok field -----------------------------------------------
    if fmt == "envelope" and "ok" in expected:
        envelope = json.loads(result.output)
        assert envelope["ok"] == expected["ok"], (
            f"[{case_id}] ok: expected {expected['ok']}, got {envelope['ok']}"
        )

    # -- 5. Record count ----------------------------------------------------
    allow_empty = expected.get("allow_empty", False)
    if expected.get("min_records") is not None and not allow_empty:
        assert len(records) >= expected["min_records"], (
            f"[{case_id}] min_records: expected >= {expected['min_records']}, "
            f"got {len(records)}"
        )
    if expected.get("max_records") is not None:
        assert len(records) <= expected["max_records"], (
            f"[{case_id}] max_records: expected <= {expected['max_records']}, "
            f"got {len(records)}"
        )

    # -- 6. Field presence / absence ----------------------------------------
    if records:
        first = records[0]
        if expected.get("required_fields"):
            for field in expected["required_fields"]:
                assert field in first, f"[{case_id}] missing field: {field}"
        if expected.get("absent_fields"):
            for field in expected["absent_fields"]:
                assert field not in first, f"[{case_id}] unexpected field: {field}"

    # -- 7. Top-level key assertions ----------------------------------------
    if expected.get("contains_keys"):
        parsed = json.loads(result.output)
        if isinstance(parsed, list):
            # For array outputs, check keys on first element
            target = parsed[0] if parsed else {}
        else:
            target = parsed
        for key in expected["contains_keys"]:
            assert key in target, f"[{case_id}] missing key: {key}"

    # -- 8. Field type assertions (--normalize) -----------------------------
    if expected.get("field_types") and records:
        first = records[0]
        for field, expected_type in expected["field_types"].items():
            val = first.get(field)
            if val is None:
                continue
            if expected_type == "int":
                assert isinstance(val, int), (
                    f"[{case_id}] {field}: expected int, got {type(val).__name__} ({val!r})"
                )
            elif expected_type == "float":
                assert isinstance(val, (int, float)), (
                    f"[{case_id}] {field}: expected float, got {type(val).__name__} ({val!r})"
                )
            elif expected_type == "str":
                assert isinstance(val, str), (
                    f"[{case_id}] {field}: expected str, got {type(val).__name__} ({val!r})"
                )
