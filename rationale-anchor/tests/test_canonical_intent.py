from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from canonical_intent.validator import (
    load_yaml,
    validate_record,
    validate_directory,
    check_invariants,
    detect_conflicts,
)


def test_kce_valid():
    record = load_yaml(Path(__file__).resolve().parent.parent / "examples" / "kce.yaml")
    result = validate_record(record)
    assert result.ok, f"KCE validation failed: {result.errors}"


def test_camp_valid():
    record = load_yaml(Path(__file__).resolve().parent.parent / "examples" / "camp.yaml")
    result = validate_record(record)
    assert result.ok, f"CAMP validation failed: {result.errors}"


def test_signa_valid():
    record = load_yaml(Path(__file__).resolve().parent.parent / "examples" / "signa.yaml")
    result = validate_record(record)
    assert result.ok, f"SIGNA validation failed: {result.errors}"


def test_directory_bidirectional_links():
    examples_dir = Path(__file__).resolve().parent.parent / "examples"
    errors, warnings = validate_directory(examples_dir)
    assert not errors, f"Bidirectional link errors: {errors}"


def test_canonical_deprecated_conflict():
    from canonical_intent.schema import validate_schema

    bad_record = {
        "canonical_intent": {
            "artifact": {"id": "TEST", "version": "1.0", "type": "framework"},
            "purpose": {"why_this_exists": "test", "problem_solved": "test"},
            "intent": {
                "canonical_goal": "test",
                "non_goals": ["none"],
                "invariants": ["test"],
                "success_criteria": ["test"],
            },
            "dependencies": {
                "requires": ["X"],
                "influences": ["Y"],
                "influenced_by": ["Z"],
            },
            "evidence": {
                "tests": ["1/1"],
                "publications": ["none"],
                "blockchain_anchor": "none",
                "reviews": ["none"],
            },
            "status": {
                "canonical": True,
                "experimental": False,
                "deprecated": True,
                "last_reviewed": "2026-09-11",
            },
            "human_authority": {
                "decision_owner": "Test Owner",
                "succession_plan": "Test Plan",
                "intent_documentation": "Test Doc",
            },
        }
    }
    errors = validate_schema(bad_record)
    assert any("canonical and deprecated" in e for e in errors), \
        f"Should detect canonical+deprecated conflict, got: {errors}"


def test_invariants_check():
    record = load_yaml(Path(__file__).resolve().parent.parent / "examples" / "kce.yaml")
    errors = check_invariants(record)
    assert errors == [], f"Unexpected invariant errors: {errors}"


def test_conflict_detection():
    examples_dir = Path(__file__).resolve().parent.parent / "examples"
    records = {}
    for p in sorted(examples_dir.glob("*.yaml")):
        record = load_yaml(p)
        aid = record["canonical_intent"]["artifact"]["id"]
        records[aid] = record
    conflicts = detect_conflicts(records)
    assert conflicts == [], f"Unexpected conflicts: {conflicts}"


if __name__ == "__main__":
    tests = [
        test_kce_valid,
        test_camp_valid,
        test_signa_valid,
        test_directory_bidirectional_links,
        test_canonical_deprecated_conflict,
        test_invariants_check,
        test_conflict_detection,
    ]
    passed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
            passed += 1
        except Exception as exc:
            print(f"  FAIL  {t.__name__}: {exc}")
    print(f"\n{passed}/{len(tests)} tests passed")
    raise SystemExit(0 if passed == len(tests) else 1)
