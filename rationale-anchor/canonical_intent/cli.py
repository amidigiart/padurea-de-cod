from __future__ import annotations

import argparse
import sys
import io
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from .validator import (
    load_yaml,
    validate_record,
    validate_directory,
    check_invariants,
    detect_conflicts,
)


def cmd_validate(path: str) -> int:
    path_obj = Path(path)
    if path_obj.is_dir():
        errors, warnings = validate_directory(path)
        print("PASS" if not errors else "FAIL")
        for e in errors:
            print(f"  ERROR: {e}")
        for w in warnings:
            print(f"  WARNING: {w}")
        return 0 if not errors else 1

    result = validate_record(load_yaml(path))
    print("PASS" if result.ok else "FAIL")
    for e in result.errors:
        print(f"  ERROR: {e}")
    for w in result.warnings:
        print(f"  WARNING: {w}")
    return 0 if result.ok else 1


def cmd_graph(path: str) -> int:
    errors, warnings = validate_directory(path)
    print("DEPENDENCY GRAPH")
    for p in sorted(Path(path).glob("*.yaml")):
        record = load_yaml(p)["canonical_intent"]
        aid = record["artifact"]["id"]
        for target in record["dependencies"]["influences"]:
            print(f"  {aid} --influences--> {target}")
    for x in errors:
        print(f"  ERROR: {x}")
    for x in warnings:
        print(f"  WARNING: {x}")
    return 0 if not errors else 1


def cmd_drift(path: str) -> int:
    record = load_yaml(path)["canonical_intent"]
    print(f"Artifact: {record['artifact']['id']}")
    print(f"Canonical: {record['status']['canonical']}")
    print(f"Last reviewed: {record['status']['last_reviewed']}")
    print(f"Invariants: {len(record['intent']['invariants'])}")
    inv_errors = check_invariants(
        load_yaml(path), Path(path).parent
    )
    if inv_errors:
        print("DRIFT DETECTED")
        for e in inv_errors:
            print(f"  {e}")
        return 1
    print("DRIFT CHECK: structural record valid; semantic drift requires an evaluator.")
    return 0


def cmd_diff(a: str, b: str) -> int:
    ra = load_yaml(a)["canonical_intent"]
    rb = load_yaml(b)["canonical_intent"]
    changes: list[tuple[str, object, object]] = []

    def walk(x: dict, y: dict, prefix: str = "") -> None:
        keys = set(x) | set(y)
        for k in sorted(keys):
            px = x.get(k)
            py = y.get(k)
            path = f"{prefix}.{k}" if prefix else k
            if isinstance(px, dict) and isinstance(py, dict):
                walk(px, py, path)
            elif px != py:
                changes.append((path, px, py))

    walk(ra, rb)
    if not changes:
        print("NO CHANGES")
        return 0
    for path, old, new in changes:
        print(f"{path}:")
        print(f"  - {old!r}")
        print(f"  + {new!r}")
    return 0


def cmd_intent_governance(path: str) -> int:
    path_obj = Path(path)
    if path_obj.is_file():
        record = load_yaml(path)
        records = {record["canonical_intent"]["artifact"]["id"]: record}
        base = path_obj.parent
    else:
        errors, _ = validate_directory(path)
        if errors:
            print("ERROR: directory validation failed")
            for e in errors:
                print(f"  {e}")
            return 1
        records = {}
        for p in sorted(path_obj.glob("*.yaml")):
            record = load_yaml(p)
            records[record["canonical_intent"]["artifact"]["id"]] = record
        base = path_obj

    violations: list[str] = []
    for aid, record in records.items():
        inv_errors = check_invariants(record, base)
        violations.extend(f"{aid}: {e}" for e in inv_errors)

        succ = record["canonical_intent"]["human_authority"]["succession_plan"]
        templates = ["Heritage Agent manages succession", "TBD", "TODO"]
        if any(t in succ for t in templates):
            violations.append(f"{aid}: succession_plan is a template, not executable")

    if violations:
        print("GOVERNANCE VIOLATIONS")
        for v in violations:
            print(f"  {v}")
        return 1
    print("GOVERNANCE COMPLIANT")
    return 0


def cmd_conflict_check(path: str) -> int:
    errors, _ = validate_directory(path)
    if errors:
        for e in errors:
            print(f"  ERROR: {e}")
        return 1

    records = {}
    for p in sorted(Path(path).glob("*.yaml")):
        record = load_yaml(p)
        records[record["canonical_intent"]["artifact"]["id"]] = record

    conflicts = detect_conflicts(records)
    if conflicts:
        print("CONFLICTS DETECTED")
        for c in conflicts:
            print(f"  {c}")
        return 1
    print("NO CONFLICTS")
    return 0


def cmd_succession_plan(path: str) -> int:
    record = load_yaml(path)["canonical_intent"]
    aid = record["artifact"]["id"]
    succ = record["human_authority"]["succession_plan"]

    print(f"Artifact: {aid}")
    print(f"Decision owner: {record['human_authority']['decision_owner']}")
    print(f"Succession plan: {succ}")

    templates = ["Heritage Agent manages succession", "TBD", "TODO"]
    if any(t in succ for t in templates):
        print("STATUS: Plan is a template — not directly executable")
        print("RECOMMEND: Add successor name + trigger condition")
        return 1
    print("STATUS: Plan appears executable")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="canonical-intent")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("validate")
    p.add_argument("path")

    p = sub.add_parser("graph")
    p.add_argument("path")

    p = sub.add_parser("check-drift")
    p.add_argument("path")

    p = sub.add_parser("diff")
    p.add_argument("old")
    p.add_argument("new")

    p = sub.add_parser("intent-governance")
    p.add_argument("path")

    p = sub.add_parser("conflict-check")
    p.add_argument("path")

    p = sub.add_parser("succession-plan")
    p.add_argument("path")

    args = parser.parse_args()
    commands = {
        "validate": lambda: cmd_validate(args.path),
        "graph": lambda: cmd_graph(args.path),
        "check-drift": lambda: cmd_drift(args.path),
        "diff": lambda: cmd_diff(args.old, args.new),
        "intent-governance": lambda: cmd_intent_governance(args.path),
        "conflict-check": lambda: cmd_conflict_check(args.path),
        "succession-plan": lambda: cmd_succession_plan(args.path),
    }
    return commands[args.command]()
