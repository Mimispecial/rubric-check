from pathlib import Path
import json

CONTRACT = Path(__file__).resolve().parents[2] / "contracts" / "rubric_check.py"
SDK = "v0.2.16"
PROMPT = "Audit one complete rubric document"
USE = "Calibrate a low-stakes peer-feedback rubric for short project explanations. The audit checks the rubric wording and never grades a participant or submission."
DOCUMENT = "Criterion CLAIM: the explanation states one falsifiable project claim a reader can identify without inference. Criterion EVIDENCE: the explanation names one observable artifact or result and explicitly connects it to that claim. Score each criterion separately as present or absent; do not evaluate writing style, identity, or personal traits."


def address(account):
    return "0x" + account.hex()


def case(vm, direct_deploy, designer, first, second):
    vm.sender = designer
    contract = direct_deploy(str(CONTRACT), address(first), address(second), "Project explanation feedback rubric", USE, sdk_version=SDK)
    contract.submit_rubric_document(DOCUMENT)
    return contract


def test_clear_audit_two_calibrators_and_publication(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    contract = case(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie)
    direct_vm.mock_llm(PROMPT, json.dumps({"audit_label": "CLEAR", "issue_code": "NONE"}))
    contract.audit_current_document()
    leader = direct_vm._captured_validators[-1][0]
    assert direct_vm.run_validator(leader_result=leader) is True
    direct_vm.sender = direct_bob
    contract.vote_as_first_calibrator("ACCEPT", "The criteria have distinct observable boundaries and cover the intended feedback use.")
    direct_vm.sender = direct_charlie
    contract.vote_as_second_calibrator("ACCEPT", "The complete rubric document is clear enough for consistent peer calibration.")
    direct_vm.sender = direct_alice
    contract.resolve_votes()
    assert contract.get_state()["publication_result"] == "PUBLISHED"


def test_nonunanimous_round_allows_one_revised_document(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    contract = case(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie)
    direct_vm.mock_llm(PROMPT, json.dumps({"audit_label": "OVERLAP", "issue_code": "REDUNDANCY"}))
    contract.audit_current_document()
    direct_vm.sender = direct_bob
    contract.vote_as_first_calibrator("REVISE", "The claim and evidence wording overlap because each currently restates the same observable result.")
    direct_vm.sender = direct_charlie
    contract.vote_as_second_calibrator("ACCEPT", "The second calibrator records acceptance while preserving the nonunanimous outcome.")
    direct_vm.sender = direct_alice
    contract.resolve_votes()
    contract.submit_revised_document(DOCUMENT + " The revised boundary forbids counting the same phrase as both the claim and its evidence.")
    assert contract.get_state()["version_number"] == 2
    assert contract.get_state()["revision_used"] is True


def test_fixed_calibrator_role_and_inconsistent_issue_fail_closed(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    contract = case(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie)
    direct_vm.mock_llm(PROMPT, json.dumps({"audit_label": "CLEAR", "issue_code": "COVERAGE"}))
    with direct_vm.expect_revert("clear_requires_none"):
        contract.audit_current_document()
    direct_vm.clear_mocks()
    direct_vm.mock_llm(PROMPT, json.dumps({"audit_label": "CLEAR", "issue_code": "NONE"}))
    contract.audit_current_document()
    direct_vm.sender = direct_charlie
    with direct_vm.expect_revert("only_first_calibrator"):
        contract.vote_as_first_calibrator("ACCEPT", "The second calibrator cannot occupy the first calibrator's fixed vote slot.")
