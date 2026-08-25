from pathlib import Path
import json

from gltest import get_contract_factory, get_validator_factory
from gltest.accounts import create_accounts
from gltest.assertions import tx_execution_succeeded
from gltest.types import TransactionStatus
from gltest.utils import extract_contract_address

PROMPT = "Audit one complete rubric document"


def context():
    validators = get_validator_factory().batch_create_mock_validators(5, mock_llm_response={"nondet_exec_prompt": {PROMPT: json.dumps({"audit_label": "CLEAR", "issue_code": "NONE"})}})
    return {"validators": [validator.to_dict() for validator in validators]}


def ok(receipt):
    assert tx_execution_succeeded(receipt)


def test_five_validator_two_calibrator_rubric():
    designer_account, first_account, second_account = create_accounts(3)
    factory = get_contract_factory(contract_file_path=Path(__file__).resolve().parents[2] / "contracts" / "rubric_check.py")
    deployed = factory.deploy_contract_tx(args=[first_account.address, second_account.address, "Project explanation feedback rubric", "Calibrate a low-stakes peer-feedback rubric for short project explanations; the audit checks wording and never grades a participant."], account=designer_account, wait_transaction_status=TransactionStatus.FINALIZED)
    ok(deployed)
    address = extract_contract_address(deployed)
    designer = factory.build_contract(address, account=designer_account)
    first = factory.build_contract(address, account=first_account)
    second = factory.build_contract(address, account=second_account)
    document = "Criterion CLAIM: state one falsifiable project claim without inference. Criterion EVIDENCE: name one observable artifact or result and connect it to the claim. Score each criterion separately as present or absent; never evaluate identity or personal traits."
    ok(designer.submit_rubric_document(args=[document]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(designer.audit_current_document(args=[]).transact(transaction_context=context(), wait_transaction_status=TransactionStatus.FINALIZED))
    ok(first.vote_as_first_calibrator(args=["ACCEPT", "The criteria have distinct observable boundaries and cover the intended feedback use."]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(second.vote_as_second_calibrator(args=["ACCEPT", "The complete document is clear enough for consistent peer calibration."]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(designer.resolve_votes(args=[]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    assert designer.get_state(args=[]).call()["publication_result"] == "PUBLISHED"
