# RationaleAnchor Governance Policy v0.2

## Mandatory Requirements

1. **Human authority is non-delegable.** No automated system may change the `canonical` status of an intent record. Only the named `decision_owner` (or their documented successor) may promote, demote, or deprecate an artifact's canonical status.

2. **Artifacts exceeding 100 hours MUST have a canonical intent record.** Safety-critical artifacts require one regardless of effort invested.

3. **Intent records are append-only in production.** Once an intent record is published with a blockchain anchor, its historical state is immutable. Updates create new versions; they do not overwrite previous ones.

4. **Bidirectional links are mandatory.** If artifact A declares that it `influences` artifact B, then B must declare that it is `influenced_by` A. The validator enforces this symmetry.

5. **Blockchain anchors prove existence, not correctness.** A Tezos hash proves that an intent record existed at a point in time. It does not validate the content. Semantic validation remains a human responsibility.

6. **Cross-model friction is required for canonical promotion.** Before an artifact's status can be set to `canonical: true`, its intent record must have been reviewed by at least 2 independent AI models (recorded in `evidence.reviews`). This is the CAMP principle applied to intent governance.

7. **Invariants are contracts.** The `intent.invariants` list defines conditions that must hold across all versions. Violating an invariant without updating the intent record is a governance failure, not a technical bug. Invariants MUST be verifiable (regex, file_exists, test_passes, or manual_review).

## Succession Planning

Succession plans MUST be executable, not templates. Must include:
- Successor identified by name (person), not role or agent
- Trigger condition (dormancy period, explicit handoff)
- Verification method (how to confirm successor is operational)

## Intent Review

Intent records must be reviewed quarterly by the decision_owner. Deprecation requires a migration rationale documented in the intent record.

## Versioning

This policy follows the same version as the RationaleAnchor specification. Changes to governance rules require a new version number and a blockchain anchor.

## Authority

Policy owner: Mihai Roșca
First effective: 2026-09-11
