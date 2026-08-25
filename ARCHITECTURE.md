# Architecture

## Deployment boundary

Deploy once per rubric calibration. Reuse the reviewed source by deploying a new instance for another rubric, purpose, and calibrator pair.

Constructor data establishes the deployment subject and fixed role boundary. Later writes add only the bounded records permitted by the lifecycle; a completed instance cannot be reopened.

## Participants

The deployer is the rubric designer and names two distinct calibrators. Only the designer submits or revises; each calibrator casts its own vote.

Addresses are normalized before authorization comparisons. Role checks and lifecycle gates execute before semantic assessment.

## State machine

`AWAITING_RUBRIC → READY_FOR_AUDIT → CALIBRATOR_VOTES → COMPLETE or REVISION_REQUESTED → READY_FOR_AUDIT`

The phase-like field is the primary lifecycle lock. Each write advances that path, performs a documented bounded loop, or fails with an `[EXPECTED]` user error.

## Evidence assembly

The stored rubric title, low-stakes purpose boundary, and entire current rubric document. No learner, applicant, worker, or submission is evaluated.

Before consensus, the contract normalizes bounded text, copies required storage into plain local values, serializes a sorted JSON packet, and places it between explicit START/END delimiters. Nondeterministic callbacks do not read contract storage.

## Consensus boundary

Return CLEAR, OVERLAP, or GAPS with one closed issue code for the whole frozen document.

The leader callback validates exact JSON shape, field types, closed labels, masks or codes, and length bounds. A validator reruns the same semantic operation and rejects disagreement before state is committed.

## Deterministic boundary

Versioning, one-revision limit, fixed calibrator authorization, vote recording, unanimity checks, and publication result are deterministic.

Important invariants:

- Only a complete document version can enter an audit round.
- Each fixed calibrator votes once per round and cannot impersonate the other.
- Publication requires a CLEAR audit plus two ACCEPT votes.
- AI audits rubric wording and never grades a person or submission.

No method sends value, pays rewards, escrows assets, deletes external data, calls another contract, or invokes a webhook.

## Failure model

- Invalid caller input or lifecycle use raises `[EXPECTED]` and leaves state unchanged.
- Malformed or out-of-policy model output raises `[LLM_ERROR]` and cannot be stored.
- Validator disagreement cannot commit the semantic result.
- StudioNet proof reads explicitly target `LATEST_FINAL`, avoiding stale pre-final state.
