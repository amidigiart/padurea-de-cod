# RationaleAnchor v0.2

**Preserving Architectural Intent Across Human and AI Transitions**

Executable reference implementation for preserving **why artifacts exist**.
Extension of Knowledge Continuity Engineering (KCE) as Layer Zero.

Formerly: Canonical Intent Layer (CIL).

## What's new in v0.2

- **Intent Governance** — automated verification of invariants and succession plans
- **Conflict Resolution** — detection of contradictory invariants across artifacts
- **Succession Planning** — validates plans are executable, not templates
- **Improved Drift Detection** — structural + invariant checking

## CLI Commands

```bash
# Validate single file or directory
python -m canonical_intent validate examples/kce.yaml
python -m canonical_intent validate examples/

# Dependency graph
python -m canonical_intent graph examples/

# Drift detection
python -m canonical_intent check-drift examples/kce.yaml

# Diff between two records
python -m canonical_intent diff examples/kce.yaml examples/camp.yaml

# Intent governance check
python -m canonical_intent intent-governance examples/

# Conflict detection
python -m canonical_intent conflict-check examples/

# Succession plan validation
python -m canonical_intent succession-plan examples/kce.yaml
```

No third-party runtime dependency is required. PyYAML is optional; the implementation
contains a minimal YAML reader for the included schema/examples.

## Design Principle

RationaleAnchor does not claim artifacts are true merely because intent records are valid.
It verifies structural integrity and ensures continuity mechanisms are operational.

## Naming

"Rationale" links to design rationale literature (Tang 2007, 363 citations on ScienceDirect).
"Anchor" connects to existing vocabulary: Human Anchor, Ω_Om, "Ancora de Aur".
Zero collisions as compound camelCase token — verified by Qwen.

## Origin

Concept proposed by ChatGPT (Sept 11, 2026), reconstructed with corrections by Claude.
v0.2 features proposed by Qwen, integrated with corrections by Claude.
Name "RationaleAnchor" selected by Qwen, confirmed by Claude and Mihai.
Cross-model friction applied: 4 models contributed, human arbiter (Mihai Roșca) holds authority.
