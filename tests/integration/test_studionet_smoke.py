import json
from pathlib import Path

import pytest
from gltest import get_contract_factory
from gltest.assertions import tx_execution_succeeded
from gltest.types import TransactionHashVariant, TransactionStatus
from gltest.utils import extract_contract_address


def ok(receipt):
    assert tx_execution_succeeded(receipt)
    assert receipt.get("status_name") == TransactionStatus.FINALIZED.value
    assert receipt.get("result_name") in (None, "AGREE", "MAJORITY_AGREE")
    assert receipt.get("tx_execution_result_name") in (None, "FINISHED_WITH_RETURN")
    return receipt


@pytest.mark.integration
def test_studionet_rubric_audit(default_account, secondary_account, tertiary_account):
    factory = get_contract_factory(contract_file_path=Path(__file__).resolve().parents[2] / "contracts" / "rubric_check.py")
    deployed = ok(factory.deploy_contract_tx(args=[secondary_account.address, tertiary_account.address, "Project explanation feedback rubric", "Calibrate a low-stakes peer-feedback rubric for short project explanations; the audit checks wording and never grades a participant."], account=default_account, wait_transaction_status=TransactionStatus.FINALIZED))
    address = extract_contract_address(deployed)
    designer = factory.build_contract(address, account=default_account)
    document = "Criterion CLAIM: state one falsifiable project claim without inference. Criterion EVIDENCE: name one observable artifact or result and connect it to the claim. Score each criterion separately as present or absent; never evaluate identity or personal traits."
    ok(designer.submit_rubric_document(args=[document]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    intelligent = ok(designer.audit_current_document(args=[]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    state = designer.get_state(args=[]).call(transaction_hash_variant=TransactionHashVariant.LATEST_FINAL)
    assert state["status"] == "CALIBRATOR_VOTES"
    assert state["audit_label"] in ("CLEAR", "OVERLAP", "GAPS")
    assert state["issue_code"] in ("NONE", "BOUNDARY", "COVERAGE", "REDUNDANCY")
    observed = {"audit_label": state["audit_label"], "issue_code": state["issue_code"]}
    print("STUDIONET_RECORD=" + json.dumps({"address": address, "deploy_tx": deployed["hash"], "intelligent_tx": intelligent["hash"], "observed": observed}, sort_keys=True))
