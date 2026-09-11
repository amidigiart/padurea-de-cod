from __future__ import annotations

from datetime import date
from typing import Any

ARTIFACT_TYPES = {"paper", "code", "story", "protocol", "product", "framework", "tool"}

REQUIRED = {
    "artifact": {"id", "version", "type"},
    "purpose": {"why_this_exists", "problem_solved"},
    "intent": {"canonical_goal", "non_goals", "invariants", "success_criteria"},
    "dependencies": {"requires", "influences", "influenced_by"},
    "evidence": {"tests", "publications", "blockchain_anchor", "reviews"},
    "status": {"canonical", "experimental", "deprecated", "last_reviewed"},
    "human_authority": {"decision_owner", "succession_plan", "intent_documentation"},
}


def _is_bool(v: Any) -> bool:
    return isinstance(v, bool)


def validate_schema(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if not isinstance(record, dict):
        return ["record must be a mapping"]

    root = record.get("canonical_intent")
    if not isinstance(root, dict):
        return ["missing canonical_intent mapping"]

    for section, fields in REQUIRED.items():
        value = root.get(section)
        if not isinstance(value, dict):
            errors.append(f"{section}: missing mapping")
            continue
        for field in fields:
            if field not in value:
                errors.append(f"{section}.{field}: missing")

    artifact = root.get("artifact", {})
    if artifact.get("type") not in ARTIFACT_TYPES:
        errors.append(f"artifact.type: unsupported value {artifact.get('type')!r}")

    for path in (
        ("artifact", "id"),
        ("artifact", "version"),
        ("purpose", "why_this_exists"),
        ("purpose", "problem_solved"),
        ("intent", "canonical_goal"),
        ("human_authority", "decision_owner"),
        ("human_authority", "succession_plan"),
        ("human_authority", "intent_documentation"),
    ):
        section, field = path
        val = root.get(section, {}).get(field)
        if not isinstance(val, str) or not val.strip():
            errors.append(f"{section}.{field}: must be a non-empty string")

    for field in ("non_goals", "invariants", "success_criteria"):
        value = root.get("intent", {}).get(field)
        if not isinstance(value, list) or not all(isinstance(x, str) and x.strip() for x in value):
            errors.append(f"intent.{field}: must be a list of non-empty strings")

    for field in ("requires", "influences", "influenced_by"):
        value = root.get("dependencies", {}).get(field)
        if not isinstance(value, list) or not all(isinstance(x, str) and x.strip() for x in value):
            errors.append(f"dependencies.{field}: must be a list of non-empty strings")

    for field in ("tests", "publications", "reviews"):
        value = root.get("evidence", {}).get(field)
        if not isinstance(value, list) or not all(isinstance(x, str) and x.strip() for x in value):
            errors.append(f"evidence.{field}: must be a list of non-empty strings")

    status = root.get("status", {})
    for field in ("canonical", "experimental", "deprecated"):
        if not _is_bool(status.get(field)):
            errors.append(f"status.{field}: must be boolean")
    if status.get("canonical") and status.get("deprecated"):
        errors.append("status: canonical and deprecated cannot both be true")
    if status.get("deprecated") and status.get("experimental"):
        errors.append("status: deprecated and experimental cannot both be true")

    reviewed = status.get("last_reviewed")
    if not isinstance(reviewed, str):
        errors.append("status.last_reviewed: must be ISO date string")
    else:
        try:
            date.fromisoformat(reviewed)
        except ValueError:
            errors.append("status.last_reviewed: invalid ISO date")

    return errors
