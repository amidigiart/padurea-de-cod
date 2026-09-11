from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import re

from .schema import validate_schema


@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def _root(record: dict[str, Any]) -> dict[str, Any]:
    return record["canonical_intent"]


def validate_record(record: dict[str, Any]) -> ValidationResult:
    errors = validate_schema(record)
    warnings: list[str] = []
    if errors:
        return ValidationResult(errors, warnings)

    root = _root(record)
    deps = root["dependencies"]
    artifact_id = root["artifact"]["id"]

    if artifact_id in deps["influences"]:
        errors.append("dependencies.influences: artifact cannot influence itself")
    if artifact_id in deps["influenced_by"]:
        errors.append("dependencies.influenced_by: artifact cannot be influenced by itself")
    if artifact_id in deps["requires"]:
        errors.append("dependencies.requires: artifact cannot require itself")

    if root["status"]["canonical"] and not root["human_authority"]["decision_owner"]:
        errors.append("canonical artifact requires a decision_owner")

    if root["evidence"]["blockchain_anchor"] in (None, "", "pending"):
        warnings.append("blockchain_anchor is pending; this does not invalidate the intent record")

    if not root["evidence"]["reviews"]:
        warnings.append("no external reviews recorded")

    return ValidationResult(errors, warnings)


def load_yaml(path: str | Path) -> dict[str, Any]:
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore
        data = yaml.safe_load(text)
        if not isinstance(data, dict):
            raise ValueError("YAML root must be a mapping")
        return data
    except ImportError:
        return _minimal_yaml(text)


def _scalar(value: str) -> Any:
    value = value.strip()
    if value in ("true", "True"):
        return True
    if value in ("false", "False"):
        return False
    if value in ("null", "Null", "NULL", "~"):
        return None
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        return [] if not inner else [_scalar(x.strip()) for x in inner.split(",")]
    return value


def _minimal_yaml(text: str) -> dict[str, Any]:
    lines = [x.rstrip() for x in text.splitlines()
             if x.strip() and not x.lstrip().startswith("#")]
    root: dict[str, Any] = {}
    stack: list[tuple[int, Any]] = [(-1, root)]
    i = 0
    while i < len(lines):
        line = lines[i]
        indent = len(line) - len(line.lstrip(" "))
        content = line.strip()

        if ":" not in content and not content.startswith("- "):
            i += 1
            continue

        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]

        if content.startswith("- "):
            if isinstance(parent, list):
                parent.append(_scalar(content[2:]))
            i += 1
            continue

        key, raw = content.split(":", 1)
        key, raw = key.strip(), raw.strip()

        if raw:
            parent[key] = _scalar(raw)
        else:
            next_line = lines[i + 1].strip() if i + 1 < len(lines) else ""
            child: Any = [] if next_line.startswith("- ") else {}
            parent[key] = child
            stack.append((indent, child))
        i += 1
    return root


def validate_directory(directory: str | Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    paths = sorted(Path(directory).glob("*.yaml"))
    records: dict[str, dict[str, Any]] = {}

    for path in paths:
        try:
            record = load_yaml(path)
            result = validate_record(record)
            errors.extend(f"{path.name}: {e}" for e in result.errors)
            warnings.extend(f"{path.name}: {w}" for w in result.warnings)
            if not result.errors:
                records[record["canonical_intent"]["artifact"]["id"]] = record
        except Exception as exc:
            errors.append(f"{path.name}: load error: {exc}")

    for aid, record in records.items():
        deps = record["canonical_intent"]["dependencies"]
        for target in deps["influences"]:
            if target not in records:
                warnings.append(f"{aid}: influences unknown artifact {target}")
                continue
            reverse = records[target]["canonical_intent"]["dependencies"]["influenced_by"]
            if aid not in reverse:
                errors.append(f"{aid} -> {target}: missing reverse influenced_by link")

    return errors, warnings


def check_invariants(record: dict[str, Any], workspace: Path = Path(".")) -> list[str]:
    errors: list[str] = []
    root = _root(record)
    invariants = root["intent"]["invariants"]

    for inv in invariants:
        if inv.startswith("regex:"):
            pattern = inv[6:].strip()
            try:
                re.compile(pattern)
            except re.error as e:
                errors.append(f"invalid regex in invariant: {pattern} ({e})")
        elif inv.startswith("file_exists:"):
            filepath = inv[12:].strip()
            if not (workspace / filepath).exists():
                errors.append(f"file not found for invariant: {filepath}")

    return errors


def detect_conflicts(records: dict[str, dict[str, Any]]) -> list[str]:
    conflicts: list[str] = []
    inv_owners: dict[str, list[str]] = {}

    for aid, record in records.items():
        root = _root(record)
        for inv in root["intent"]["invariants"]:
            inv_owners.setdefault(inv, []).append(aid)

    for inv, owners in inv_owners.items():
        if len(owners) > 1:
            conflicts.append(
                f"shared invariant across {', '.join(owners)}: {inv!r}"
            )

    return conflicts
