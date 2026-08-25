# Rubric Check

Audits one complete, versioned rubric document for criterion overlap or coverage gaps before two fixed human calibrators vote on publication.

## Why it is an Intelligent Contract

Return CLEAR, OVERLAP, or GAPS with one closed issue code for the whole frozen document. GenLayer validators independently replay that semantic judgment before it becomes shared state. Versioning, one-revision limit, fixed calibrator authorization, vote recording, unanimity checks, and publication result are deterministic.

## Reusable deployment model

Deploy once per rubric calibration. Reuse the reviewed source by deploying a new instance for another rubric, purpose, and calibrator pair.

A completed deployment is an auditable record and is not reset or silently repurposed. Reuse means deploying the same reviewed source with new constructor data.

## Roles and workflow

The deployer is the rubric designer and names two distinct calibrators. Only the designer submits or revises; each calibrator casts its own vote.

State path: `AWAITING_RUBRIC → READY_FOR_AUDIT → CALIBRATOR_VOTES → COMPLETE or REVISION_REQUESTED → READY_FOR_AUDIT`

## Evidence boundary

The stored rubric title, low-stakes purpose boundary, and entire current rubric document. No learner, applicant, worker, or submission is evaluated.

## Core invariants

- Only a complete document version can enter an audit round.
- Each fixed calibrator votes once per round and cannot impersonate the other.
- Publication requires a CLEAR audit plus two ACCEPT votes.
- AI audits rubric wording and never grades a person or submission.

## Public interface

Write methods: `audit_current_document, resolve_votes, submit_revised_document, submit_rubric_document, vote_as_first_calibrator, vote_as_second_calibrator`

View methods: `get_document_version, get_policy, get_state`

`get_policy` exposes the machine-readable operating boundary and confirms that this contract never custodies funds.

## Verification

Pinned GenVM runner: `py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6`

```powershell
python -m pip install -r requirements.txt
genvm-lint check contracts/rubric_check.py
genvm-lint typecheck contracts/rubric_check.py
pytest tests/direct -q
python tests/run_glsim.py --port 4000 --validators 5 --no-browser
gltest tests/integration/test_glsim_consensus.py --network localnet -q
```

The StudioNet smoke test is opt-in and uses three disposable Mimi-only accounts protected outside the workspace. It asserts finalized successful execution and reads committed state with `LATEST_FINAL`.

## Final StudioNet proof

- Contract: https://explorer-studio.genlayer.com/address/0x8d35B6784E8d0E068b17dA4A1b4316863B2cC62C
- Studio import: https://studio.genlayer.com/?import-contract=0x8d35B6784E8d0E068b17dA4A1b4316863B2cC62C
- Deployment transaction: https://explorer-studio.genlayer.com/tx/0x79b8cd19cbf5fab933ef5b456ae95b83dc2b0bffe0e52eee59d557f1f554176f
- Intelligent transaction: https://explorer-studio.genlayer.com/tx/0xfd528686c42c4e1b6a8115c4bd712471dcd70eb264865ad2830b2b67aa3cfc98
- Observed committed state: `{"audit_label":"CLEAR","issue_code":"NONE"}`
- Audited source SHA-256: `45bfcdb8b4144c45fbe9cc89eccf01d7cf88278355115e33b3d47d525c161423`

## Limitations

- The audit cannot prove real-world inter-rater reliability or fairness.
- A CLEAR result is limited to the stored document and declared purpose.
- The workflow is for low-stakes rubric calibration, not employment, admission, credit, or legal decisions.

## Repository map

- `contracts/rubric_check.py` — Intelligent Contract source
- `tests/direct` — hardened leader/validator and lifecycle tests
- `tests/integration/test_glsim_consensus.py` — five-validator simulator flow
- `tests/integration/test_studionet_smoke.py` — live opt-in proof
- `deployments/studionet.json` — source-bound public deployment evidence
- `ARCHITECTURE.md`, `SOURCE_POLICY.md`, `SECURITY.md`, `AUDIT.md` — reviewer material

License: MIT.
