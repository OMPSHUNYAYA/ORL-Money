#!/usr/bin/env python3

import argparse
import hashlib
import itertools
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from copy import deepcopy

VERSION = "2.1.0"
ARCHITECTURE_PROFILE = "ORL-MONEY-ARCH-2-D02"
RULESET_PROFILE = "ORL-MONEY-RULES-2-D02"
BALANCE_SCHEMA = "ORL-MONEY-BALANCE-2-D02"
FRAGMENT_SCHEMA = "ORL-FRAGMENT-2-D02"
OBSERVATION_SCHEMA = "ORL-MONEY-OBSERVATION-2-D02"
TRANSACTION_RECEIPT_PROFILE = "ORL-MONEY-TX-RECEIPT-2-D02"
PROJECTION_PROFILE = "ORL-MONEY-PROJECTION-2-D02"
COMPATIBILITY_PROFILE = "ORL-MONEY-BALANCE-COMPAT-GROSS-1-D02"
BOUNDARY_PROFILE = "ORL-MONEY-BOUNDARY-1-D02"
BUNDLE_PROFILE = "ORL-MONEY-BUNDLE-2-D02"
VERIFICATION_PROFILE = "ORL-MONEY-VERIFICATION-1-D02"
AUDIT_PROFILE = "ORL-MONEY-AUDIT-2-D03"
MAX_AMOUNT_DIGITS = 78
MAX_IDENTIFIER_LENGTH = 128
UNIT_PATTERN = re.compile(r"^[A-Z][A-Z0-9_-]{0,15}$")
AMOUNT_ZERO_PATTERN = re.compile(r"^(0|[1-9][0-9]{0,77})$")
AMOUNT_POSITIVE_PATTERN = re.compile(r"^[1-9][0-9]{0,77}$")


def canonical_json(value):
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def identity(prefix, profile, value):
    basis = {
        "profile": profile,
        "value": value,
    }
    return prefix + "_" + sha256_text(canonical_json(basis))


def is_nfc(value):
    return unicodedata.normalize("NFC", value) == value


def has_forbidden_character(value):
    for char in value:
        category = unicodedata.category(char)
        if category in ("Cc", "Cf", "Cs"):
            return True
    return False


def validate_identifier(value, field_name):
    errors = []
    if not isinstance(value, str):
        return [field_name + ": must be a string"]
    if value == "":
        errors.append(field_name + ": must not be empty")
    if len(value) > MAX_IDENTIFIER_LENGTH:
        errors.append(field_name + ": exceeds maximum length")
    if value != value.strip():
        errors.append(field_name + ": leading or trailing whitespace is not allowed")
    if not is_nfc(value):
        errors.append(field_name + ": must be NFC-normalized")
    if has_forbidden_character(value):
        errors.append(field_name + ": control, format, and surrogate characters are not allowed")
    return errors


def validate_unit(value):
    if not isinstance(value, str):
        return ["unit: must be a string"]
    if not UNIT_PATTERN.fullmatch(value):
        return ["unit: must match " + UNIT_PATTERN.pattern]
    return []


def validate_amount_minor(value, allow_zero):
    if not isinstance(value, str):
        return ["amount_minor: must be a decimal integer string"]
    pattern = AMOUNT_ZERO_PATTERN if allow_zero else AMOUNT_POSITIVE_PATTERN
    if not pattern.fullmatch(value):
        if len(value) > MAX_AMOUNT_DIGITS and value.isdigit():
            return ["amount_minor: exceeds maximum digit length"]
        if not allow_zero and value == "0":
            return ["amount_minor: zero is not supported for transaction claims"]
        return ["amount_minor: invalid canonical decimal integer string"]
    return []


def exact_fields(record, expected_fields, record_name):
    if not isinstance(record, dict):
        return [record_name + ": must be an object"]
    actual = set(record.keys())
    expected = set(expected_fields)
    errors = []
    for field in sorted(expected - actual):
        errors.append(record_name + ": missing field " + field)
    for field in sorted(actual - expected):
        errors.append(record_name + ": unsupported field " + field)
    return errors


def validate_balance_record(record):
    fields = ["schema", "account", "amount_minor", "unit"]
    errors = exact_fields(record, fields, "balance")
    if errors:
        return errors
    if record["schema"] != BALANCE_SCHEMA:
        errors.append("balance.schema: unsupported schema")
    errors.extend(validate_identifier(record["account"], "balance.account"))
    errors.extend(validate_amount_minor(record["amount_minor"], allow_zero=True))
    errors.extend(validate_unit(record["unit"]))
    return errors


def validate_fragment_record(record):
    fields = ["schema", "tx", "side", "account", "amount_minor", "unit"]
    errors = exact_fields(record, fields, "fragment")
    if errors:
        return errors
    if record["schema"] != FRAGMENT_SCHEMA:
        errors.append("fragment.schema: unsupported schema")
    errors.extend(validate_identifier(record["tx"], "fragment.tx"))
    if record["side"] not in ("debit", "credit"):
        errors.append("fragment.side: must be debit or credit")
    errors.extend(validate_identifier(record["account"], "fragment.account"))
    errors.extend(validate_amount_minor(record["amount_minor"], allow_zero=False))
    errors.extend(validate_unit(record["unit"]))
    return errors


def validate_observation_record(record):
    fields = ["schema", "observation_ref", "source", "fragment"]
    errors = exact_fields(record, fields, "observation")
    if errors:
        return errors
    if record["schema"] != OBSERVATION_SCHEMA:
        errors.append("observation.schema: unsupported schema")
    errors.extend(validate_identifier(record["observation_ref"], "observation.observation_ref"))
    errors.extend(validate_identifier(record["source"], "observation.source"))
    errors.extend(validate_fragment_record(record["fragment"]))
    return errors


def make_balance(account, amount_minor, unit="UNIT"):
    return {
        "schema": BALANCE_SCHEMA,
        "account": account,
        "amount_minor": str(amount_minor),
        "unit": unit,
    }


def make_fragment(tx, side, account, amount_minor, unit="UNIT"):
    return {
        "schema": FRAGMENT_SCHEMA,
        "tx": tx,
        "side": side,
        "account": account,
        "amount_minor": str(amount_minor),
        "unit": unit,
    }


def make_observation(source, observation_ref, fragment):
    return {
        "schema": OBSERVATION_SCHEMA,
        "observation_ref": observation_ref,
        "source": source,
        "fragment": deepcopy(fragment),
    }


def signed_decimal(value):
    return str(int(value))


def balance_record_id(record):
    return identity("balance", BALANCE_SCHEMA, record)


def claim_id(fragment):
    return identity("claim", FRAGMENT_SCHEMA, fragment)


def observation_id(observation):
    basis = {
        "schema": observation["schema"],
        "observation_ref": observation["observation_ref"],
        "source": observation["source"],
        "claim_id": claim_id(observation["fragment"]),
    }
    return identity("observation", OBSERVATION_SCHEMA, basis)


def resolve_balance_basis(balance_records):
    errors = []
    validated = []
    for index, record in enumerate(balance_records):
        record_errors = validate_balance_record(record)
        if record_errors:
            for error in record_errors:
                errors.append("balances[" + str(index) + "]: " + error)
        else:
            validated.append(deepcopy(record))

    if errors:
        return {
            "validation_state": "REFUSED",
            "errors": errors,
        }

    exact_unique = {}
    for record in validated:
        exact_unique[balance_record_id(record)] = record

    by_account_unit = defaultdict(dict)
    for record_id, record in exact_unique.items():
        key = (record["account"], record["unit"])
        by_account_unit[key][record["amount_minor"]] = record_id

    balances = []
    conflicts = []
    for key in sorted(by_account_unit.keys()):
        amount_map = by_account_unit[key]
        account, unit = key
        if len(amount_map) == 1:
            amount_minor = next(iter(amount_map.keys()))
            record = make_balance(account, amount_minor, unit)
            balances.append({
                "record_id": balance_record_id(record),
                "account": account,
                "amount_minor": amount_minor,
                "unit": unit,
            })
        else:
            conflicts.append({
                "account": account,
                "unit": unit,
                "amount_minor_values": sorted(amount_map.keys(), key=lambda item: (len(item), item)),
                "record_ids": sorted(amount_map.values()),
            })

    basis_state = "CONFLICT" if conflicts else "RESOLVED"
    snapshot_basis = {
        "profile": BALANCE_SCHEMA,
        "state": basis_state,
        "balances": balances,
        "conflicts": conflicts,
    }
    snapshot_id = identity("balance_snapshot", BALANCE_SCHEMA, snapshot_basis)

    return {
        "validation_state": "ACCEPTED",
        "state": basis_state,
        "raw_record_count": len(balance_records),
        "unique_record_count": len(exact_unique),
        "exact_duplicate_count": len(balance_records) - len(exact_unique),
        "balances": balances,
        "conflicts": conflicts,
        "balance_snapshot_id": snapshot_id,
    }


def prepare_observations(observations):
    errors = []
    validated = []
    for index, record in enumerate(observations):
        record_errors = validate_observation_record(record)
        if record_errors:
            for error in record_errors:
                errors.append("observations[" + str(index) + "]: " + error)
        else:
            validated.append(deepcopy(record))

    if errors:
        return {
            "validation_state": "REFUSED",
            "errors": errors,
        }

    unique_observations = {}
    for record in validated:
        oid = observation_id(record)
        unique_observations[oid] = record

    claims = {}
    claim_observations = defaultdict(list)
    claim_sources = defaultdict(set)
    for oid in sorted(unique_observations.keys()):
        observation = unique_observations[oid]
        cid = claim_id(observation["fragment"])
        claims[cid] = deepcopy(observation["fragment"])
        claim_observations[cid].append(oid)
        claim_sources[cid].add(observation["source"])

    claim_records = []
    for cid in sorted(claims.keys()):
        claim_records.append({
            "claim_id": cid,
            "fragment": claims[cid],
            "observation_ids": sorted(claim_observations[cid]),
            "sources": sorted(claim_sources[cid]),
            "observation_count": len(claim_observations[cid]),
        })

    observation_records = []
    for oid in sorted(unique_observations.keys()):
        observation = unique_observations[oid]
        observation_records.append({
            "observation_id": oid,
            "observation_ref": observation["observation_ref"],
            "source": observation["source"],
            "claim_id": claim_id(observation["fragment"]),
        })

    claim_set_basis = {
        "profile": FRAGMENT_SCHEMA,
        "claim_ids": sorted(claims.keys()),
    }
    observation_set_basis = {
        "profile": OBSERVATION_SCHEMA,
        "observation_ids": sorted(unique_observations.keys()),
    }

    return {
        "validation_state": "ACCEPTED",
        "raw_observation_count": len(observations),
        "unique_observation_count": len(unique_observations),
        "exact_observation_duplicate_count": len(observations) - len(unique_observations),
        "unique_claim_count": len(claims),
        "observation_multiplicity_count": len(unique_observations) - len(claims),
        "claims": claim_records,
        "observations": observation_records,
        "claim_set_id": identity("claim_set", FRAGMENT_SCHEMA, claim_set_basis),
        "observation_set_id": identity("observation_set", OBSERVATION_SCHEMA, observation_set_basis),
    }


def tx_receipt_id(receipt_without_id):
    return identity("tx_receipt", TRANSACTION_RECEIPT_PROFILE, receipt_without_id)


def resolve_transactions(claim_records):
    by_tx = defaultdict(list)
    claim_index = {}
    for claim in claim_records:
        cid = claim["claim_id"]
        fragment = claim["fragment"]
        claim_index[cid] = claim
        by_tx[fragment["tx"]].append(cid)

    receipts = []
    for tx in sorted(by_tx.keys()):
        tx_claim_ids = sorted(by_tx[tx])
        debits = [cid for cid in tx_claim_ids if claim_index[cid]["fragment"]["side"] == "debit"]
        credits = [cid for cid in tx_claim_ids if claim_index[cid]["fragment"]["side"] == "credit"]

        state = None
        reason_code = None
        witness = {}
        contributions = []

        if len(debits) > 1 and len(credits) > 1:
            state = "ABSTAIN"
            reason_code = "MULTIPLE_DEBIT_AND_CREDIT_CLAIMS"
            witness = {
                "conflicting_claim_ids": sorted(debits + credits),
            }
        elif len(debits) > 1:
            state = "ABSTAIN"
            reason_code = "MULTIPLE_DEBIT_CLAIMS"
            witness = {
                "conflicting_claim_ids": sorted(debits),
                "credit_claim_ids": sorted(credits),
            }
        elif len(credits) > 1:
            state = "ABSTAIN"
            reason_code = "MULTIPLE_CREDIT_CLAIMS"
            witness = {
                "debit_claim_ids": sorted(debits),
                "conflicting_claim_ids": sorted(credits),
            }
        elif not debits:
            state = "INCOMPLETE"
            reason_code = "MISSING_DEBIT_CLAIM"
            witness = {
                "present_claim_ids": sorted(credits),
                "missing_requirement": "ONE_COMPATIBLE_DEBIT_CLAIM",
            }
        elif not credits:
            state = "INCOMPLETE"
            reason_code = "MISSING_CREDIT_CLAIM"
            witness = {
                "present_claim_ids": sorted(debits),
                "missing_requirement": "ONE_COMPATIBLE_CREDIT_CLAIM",
            }
        else:
            debit = claim_index[debits[0]]["fragment"]
            credit = claim_index[credits[0]]["fragment"]
            if debit["unit"] != credit["unit"]:
                state = "ABSTAIN"
                reason_code = "UNIT_MISMATCH"
                witness = {
                    "debit_claim_id": debits[0],
                    "credit_claim_id": credits[0],
                    "debit_unit": debit["unit"],
                    "credit_unit": credit["unit"],
                }
            elif debit["amount_minor"] != credit["amount_minor"]:
                state = "ABSTAIN"
                reason_code = "AMOUNT_MISMATCH"
                witness = {
                    "debit_claim_id": debits[0],
                    "credit_claim_id": credits[0],
                    "debit_amount_minor": debit["amount_minor"],
                    "credit_amount_minor": credit["amount_minor"],
                    "unit": debit["unit"],
                }
            else:
                state = "RESOLVED"
                reason_code = "MATCHED_DEBIT_CREDIT_PAIR"
                witness = {
                    "debit_claim_id": debits[0],
                    "credit_claim_id": credits[0],
                }
                contributions = [
                    {
                        "account": debit["account"],
                        "delta_minor": "-" + debit["amount_minor"],
                        "side": "debit",
                        "unit": debit["unit"],
                    },
                    {
                        "account": credit["account"],
                        "delta_minor": credit["amount_minor"],
                        "side": "credit",
                        "unit": credit["unit"],
                    },
                ]

        evidence_basis = {
            "tx": tx,
            "claim_ids": tx_claim_ids,
        }
        receipt = {
            "profile": TRANSACTION_RECEIPT_PROFILE,
            "ruleset_profile": RULESET_PROFILE,
            "tx": tx,
            "transaction_evidence_id": identity("tx_evidence", RULESET_PROFILE, evidence_basis),
            "claim_ids": tx_claim_ids,
            "state": state,
            "reason_code": reason_code,
            "witness": witness,
            "contributions": contributions,
        }
        receipt["transaction_receipt_id"] = tx_receipt_id(receipt)
        receipts.append(receipt)

    counts = Counter(receipt["state"] for receipt in receipts)
    receipt_root_basis = {
        "profile": TRANSACTION_RECEIPT_PROFILE,
        "transaction_receipt_ids": sorted(receipt["transaction_receipt_id"] for receipt in receipts),
    }
    return {
        "receipts": receipts,
        "state_counts": {
            "RESOLVED": counts.get("RESOLVED", 0),
            "INCOMPLETE": counts.get("INCOMPLETE", 0),
            "ABSTAIN": counts.get("ABSTAIN", 0),
        },
        "transaction_receipt_root": identity(
            "tx_receipt_root",
            TRANSACTION_RECEIPT_PROFILE,
            receipt_root_basis,
        ),
    }


def balance_map_from_snapshot(balance_snapshot):
    result = {}
    for record in balance_snapshot.get("balances", []):
        result[(record["account"], record["unit"])] = int(record["amount_minor"])
    return result


def build_projection(balance_snapshot, transaction_receipts):
    if balance_snapshot["state"] != "RESOLVED":
        unavailable_basis = {
            "profile": PROJECTION_PROFILE,
            "state": "UNAVAILABLE",
            "reason_code": "BALANCE_BASIS_CONFLICT",
            "balance_snapshot_id": balance_snapshot["balance_snapshot_id"],
        }
        return {
            "profile": PROJECTION_PROFILE,
            "state": "UNAVAILABLE",
            "reason_code": "BALANCE_BASIS_CONFLICT",
            "account_receipts": [],
            "unit_receipts": [],
            "projection_root": identity("projection", PROJECTION_PROFILE, unavailable_basis),
        }

    initial_map = balance_map_from_snapshot(balance_snapshot)
    contributions_by_key = defaultdict(list)
    affected_keys = set(initial_map.keys())

    for receipt in transaction_receipts:
        if receipt["state"] != "RESOLVED":
            continue
        for contribution in receipt["contributions"]:
            key = (contribution["account"], contribution["unit"])
            affected_keys.add(key)
            contributions_by_key[key].append({
                "transaction_receipt_id": receipt["transaction_receipt_id"],
                "tx": receipt["tx"],
                "delta_minor": contribution["delta_minor"],
            })

    account_receipts = []
    for account, unit in sorted(affected_keys):
        initial = initial_map.get((account, unit), 0)
        contributions = sorted(
            contributions_by_key.get((account, unit), []),
            key=lambda item: (item["tx"], item["transaction_receipt_id"], item["delta_minor"]),
        )
        delta = sum(int(item["delta_minor"]) for item in contributions)
        final = initial + delta
        receipt_without_id = {
            "profile": PROJECTION_PROFILE,
            "account": account,
            "unit": unit,
            "initial_amount_minor": signed_decimal(initial),
            "contributions": contributions,
            "net_delta_minor": signed_decimal(delta),
            "final_amount_minor": signed_decimal(final),
        }
        receipt = dict(receipt_without_id)
        receipt["account_projection_id"] = identity(
            "account_projection",
            PROJECTION_PROFILE,
            receipt_without_id,
        )
        account_receipts.append(receipt)

    units = sorted(set(receipt["unit"] for receipt in account_receipts))
    unit_receipts = []
    for unit in units:
        accounts = [receipt for receipt in account_receipts if receipt["unit"] == unit]
        initial_total = sum(int(receipt["initial_amount_minor"]) for receipt in accounts)
        final_total = sum(int(receipt["final_amount_minor"]) for receipt in accounts)
        net_delta = sum(int(receipt["net_delta_minor"]) for receipt in accounts)
        unit_without_id = {
            "profile": PROJECTION_PROFILE,
            "unit": unit,
            "account_projection_ids": sorted(receipt["account_projection_id"] for receipt in accounts),
            "initial_total_minor": signed_decimal(initial_total),
            "net_delta_minor": signed_decimal(net_delta),
            "final_total_minor": signed_decimal(final_total),
            "conservation_ok": initial_total == final_total and net_delta == 0,
        }
        unit_receipt = dict(unit_without_id)
        unit_receipt["unit_projection_id"] = identity(
            "unit_projection",
            PROJECTION_PROFILE,
            unit_without_id,
        )
        unit_receipts.append(unit_receipt)

    projection_basis = {
        "profile": PROJECTION_PROFILE,
        "state": "AVAILABLE",
        "balance_snapshot_id": balance_snapshot["balance_snapshot_id"],
        "account_projection_ids": sorted(receipt["account_projection_id"] for receipt in account_receipts),
        "unit_projection_ids": sorted(receipt["unit_projection_id"] for receipt in unit_receipts),
    }

    return {
        "profile": PROJECTION_PROFILE,
        "state": "AVAILABLE",
        "account_receipts": account_receipts,
        "unit_receipts": unit_receipts,
        "projection_root": identity("projection", PROJECTION_PROFILE, projection_basis),
    }


def evaluate_balance_compatibility(balance_snapshot, transaction_receipts):
    initial_map = balance_map_from_snapshot(balance_snapshot) if balance_snapshot["state"] == "RESOLVED" else {}
    outgoing = defaultdict(list)

    for receipt in transaction_receipts:
        if receipt["state"] != "RESOLVED":
            continue
        for contribution in receipt["contributions"]:
            if contribution["side"] == "debit":
                key = (contribution["account"], contribution["unit"])
                outgoing[key].append({
                    "transaction_receipt_id": receipt["transaction_receipt_id"],
                    "tx": receipt["tx"],
                    "amount_minor": contribution["delta_minor"][1:],
                })

    assessments = []
    if balance_snapshot["state"] == "CONFLICT":
        overall_state = "CONFLICT"
        for conflict in balance_snapshot["conflicts"]:
            assessments.append({
                "account": conflict["account"],
                "unit": conflict["unit"],
                "state": "CONFLICT",
                "reason_code": "AMBIGUOUS_DECLARED_BALANCE_BASIS",
                "amount_minor_values": conflict["amount_minor_values"],
            })
    else:
        for key in sorted(outgoing.keys()):
            account, unit = key
            entries = sorted(outgoing[key], key=lambda item: (item["tx"], item["transaction_receipt_id"]))
            gross_outflow = sum(int(item["amount_minor"]) for item in entries)
            if key not in initial_map:
                assessments.append({
                    "account": account,
                    "unit": unit,
                    "state": "UNASSESSED",
                    "reason_code": "NO_DECLARED_BALANCE_BASIS",
                    "resolved_gross_outflow_minor": signed_decimal(gross_outflow),
                    "contributing_transactions": entries,
                })
            else:
                initial = initial_map[key]
                remaining = initial - gross_outflow
                if gross_outflow > initial:
                    state = "CONFLICT"
                    reason_code = "RESOLVED_GROSS_OUTFLOW_EXCEEDS_DECLARED_BALANCE_BASIS"
                else:
                    state = "COMPATIBLE"
                    reason_code = "RESOLVED_GROSS_OUTFLOW_WITHIN_DECLARED_BALANCE_BASIS"
                assessments.append({
                    "account": account,
                    "unit": unit,
                    "state": state,
                    "reason_code": reason_code,
                    "declared_balance_minor": signed_decimal(initial),
                    "resolved_gross_outflow_minor": signed_decimal(gross_outflow),
                    "remaining_declared_basis_minor": signed_decimal(remaining),
                    "deficit_minor": signed_decimal(max(0, -remaining)),
                    "contributing_transactions": entries,
                })

        states = [item["state"] for item in assessments]
        if "CONFLICT" in states:
            overall_state = "CONFLICT"
        elif "UNASSESSED" in states:
            overall_state = "UNASSESSED"
        else:
            overall_state = "COMPATIBLE"

    receipt_without_id = {
        "profile": COMPATIBILITY_PROFILE,
        "rule": "resolved_gross_outflow <= declared_initial_balance",
        "balance_snapshot_id": balance_snapshot["balance_snapshot_id"],
        "state": overall_state,
        "assessments": assessments,
    }
    receipt = dict(receipt_without_id)
    receipt["compatibility_receipt_id"] = identity(
        "compatibility",
        COMPATIBILITY_PROFILE,
        receipt_without_id,
    )
    return receipt


def make_boundary_receipt(state, claim_set_id_value):
    if state not in ("OPEN", "SEALED"):
        raise ValueError("boundary_state must be OPEN or SEALED")
    receipt_without_id = {
        "profile": BOUNDARY_PROFILE,
        "state": state,
        "observed_claim_set_id": claim_set_id_value,
        "declared_sealed_claim_set_id": claim_set_id_value if state == "SEALED" else None,
    }
    receipt = dict(receipt_without_id)
    receipt["boundary_receipt_id"] = identity(
        "boundary",
        BOUNDARY_PROFILE,
        receipt_without_id,
    )
    return receipt


def build_evidence_maturity(observation_result, transaction_result, boundary_receipt):
    counts = transaction_result["state_counts"]
    return {
        "accepted_claims": observation_result["unique_claim_count"],
        "unique_observations": observation_result["unique_observation_count"],
        "observation_multiplicity": observation_result["observation_multiplicity_count"],
        "resolved_transactions": counts["RESOLVED"],
        "incomplete_transactions": counts["INCOMPLETE"],
        "abstain_transactions": counts["ABSTAIN"],
        "boundary_state": boundary_receipt["state"],
    }


def bundle_core(bundle):
    core = deepcopy(bundle)
    core.pop("self_verification", None)
    return core


def make_refusal(errors):
    refusal = {
        "profile": BUNDLE_PROFILE,
        "version": VERSION,
        "result": "REFUSED",
        "architecture_profile": ARCHITECTURE_PROFILE,
        "ruleset_profile": RULESET_PROFILE,
        "errors": list(errors),
    }
    refusal["refusal_id"] = identity("refusal", BUNDLE_PROFILE, refusal)
    return refusal


def resolve_financial_bundle(balance_records, observations, boundary_state="OPEN", run_self_verify=True):
    intake_errors = []
    if not isinstance(balance_records, list):
        intake_errors.append("balances: must be an array")
    if not isinstance(observations, list):
        intake_errors.append("observations: must be an array")
    if boundary_state not in ("OPEN", "SEALED"):
        intake_errors.append("boundary_state must be OPEN or SEALED")
    if intake_errors:
        return make_refusal(intake_errors)

    balance_snapshot = resolve_balance_basis(balance_records)
    observation_result = prepare_observations(observations)

    validation_errors = []
    if balance_snapshot["validation_state"] == "REFUSED":
        validation_errors.extend(balance_snapshot["errors"])
    if observation_result["validation_state"] == "REFUSED":
        validation_errors.extend(observation_result["errors"])

    if validation_errors:
        return make_refusal(validation_errors)

    transaction_result = resolve_transactions(observation_result["claims"])
    projection = build_projection(balance_snapshot, transaction_result["receipts"])
    compatibility = evaluate_balance_compatibility(balance_snapshot, transaction_result["receipts"])
    boundary_receipt = make_boundary_receipt(boundary_state, observation_result["claim_set_id"])
    maturity = build_evidence_maturity(observation_result, transaction_result, boundary_receipt)

    financial_resolution_basis = {
        "profile": BUNDLE_PROFILE,
        "version": VERSION,
        "architecture_profile": ARCHITECTURE_PROFILE,
        "ruleset_profile": RULESET_PROFILE,
        "compatibility_profile": COMPATIBILITY_PROFILE,
        "balance_snapshot_id": balance_snapshot["balance_snapshot_id"],
        "claim_set_id": observation_result["claim_set_id"],
        "transaction_receipt_root": transaction_result["transaction_receipt_root"],
        "projection_root": projection["projection_root"],
        "compatibility_receipt_id": compatibility["compatibility_receipt_id"],
        "boundary_receipt_id": boundary_receipt["boundary_receipt_id"],
    }
    financial_resolution_id = identity(
        "financial_resolution",
        BUNDLE_PROFILE,
        financial_resolution_basis,
    )

    full_bundle_basis = {
        "profile": BUNDLE_PROFILE,
        "financial_resolution_id": financial_resolution_id,
        "observation_set_id": observation_result["observation_set_id"],
    }
    financial_bundle_id = identity("financial_bundle", BUNDLE_PROFILE, full_bundle_basis)

    bundle = {
        "profile": BUNDLE_PROFILE,
        "version": VERSION,
        "result": "ACCEPTED",
        "architecture_profile": ARCHITECTURE_PROFILE,
        "ruleset_profile": RULESET_PROFILE,
        "compatibility_profile": COMPATIBILITY_PROFILE,
        "inputs": {
            "balances": deepcopy(balance_records),
            "observations": deepcopy(observations),
            "boundary_state": boundary_state,
        },
        "balance_basis": balance_snapshot,
        "evidence": observation_result,
        "transactions": transaction_result,
        "structural_projection": projection,
        "declared_balance_compatibility": compatibility,
        "boundary": boundary_receipt,
        "evidence_maturity": maturity,
        "financial_resolution_id": financial_resolution_id,
        "financial_bundle_id": financial_bundle_id,
    }

    if run_self_verify:
        bundle["self_verification"] = verify_bundle(bundle)

    return bundle


def verify_bundle(bundle):
    if not isinstance(bundle, dict):
        return {
            "profile": VERIFICATION_PROFILE,
            "valid": False,
            "errors": ["bundle must be an object"],
        }
    if bundle.get("result") != "ACCEPTED":
        return {
            "profile": VERIFICATION_PROFILE,
            "valid": False,
            "errors": ["only accepted bundles are verifiable by this function"],
        }
    inputs = bundle.get("inputs")
    if not isinstance(inputs, dict):
        return {
            "profile": VERIFICATION_PROFILE,
            "valid": False,
            "errors": ["missing inputs"],
        }

    expected = resolve_financial_bundle(
        inputs.get("balances", []),
        inputs.get("observations", []),
        inputs.get("boundary_state", "OPEN"),
        run_self_verify=False,
    )

    errors = []
    if expected.get("result") != "ACCEPTED":
        errors.append("embedded inputs do not reconstruct an accepted bundle")
    elif canonical_json(bundle_core(bundle)) != canonical_json(bundle_core(expected)):
        checks = [
            "financial_resolution_id",
            "financial_bundle_id",
        ]
        for field in checks:
            if bundle.get(field) != expected.get(field):
                errors.append(field + " mismatch")
        nested_checks = [
            ("balance_basis", "balance_snapshot_id"),
            ("evidence", "claim_set_id"),
            ("evidence", "observation_set_id"),
            ("transactions", "transaction_receipt_root"),
            ("structural_projection", "projection_root"),
            ("declared_balance_compatibility", "compatibility_receipt_id"),
            ("boundary", "boundary_receipt_id"),
        ]
        for section, field in nested_checks:
            left = bundle.get(section, {}).get(field)
            right = expected.get(section, {}).get(field)
            if left != right:
                errors.append(section + "." + field + " mismatch")
        if not errors:
            errors.append("bundle content mismatch")

    return {
        "profile": VERIFICATION_PROFILE,
        "valid": not errors,
        "errors": errors,
        "expected_financial_resolution_id": expected.get("financial_resolution_id"),
        "expected_financial_bundle_id": expected.get("financial_bundle_id"),
    }


def merge_observation_sets(*observation_sets):
    merged = {}
    for observation_set in observation_sets:
        for observation in observation_set:
            errors = validate_observation_record(observation)
            if errors:
                raise ValueError("cannot merge invalid observation")
            merged[observation_id(observation)] = deepcopy(observation)
    return [merged[oid] for oid in sorted(merged.keys())]


def transaction_state_map(bundle):
    return {
        receipt["tx"]: receipt["state"]
        for receipt in bundle.get("transactions", {}).get("receipts", [])
    }


def transaction_reason_map(bundle):
    return {
        receipt["tx"]: receipt["reason_code"]
        for receipt in bundle.get("transactions", {}).get("receipts", [])
    }


def final_balance_map(bundle):
    result = {}
    for receipt in bundle.get("structural_projection", {}).get("account_receipts", []):
        result[(receipt["account"], receipt["unit"])] = receipt["final_amount_minor"]
    return result


def unit_conservation_map(bundle):
    return {
        receipt["unit"]: receipt["conservation_ok"]
        for receipt in bundle.get("structural_projection", {}).get("unit_receipts", [])
    }


def scenario_two_node():
    balances = [
        make_balance("VillageA", "1000"),
        make_balance("VillageB", "1000"),
    ]

    node_a = [
        make_observation("Node-A", "A-001", make_fragment("M100", "debit", "VillageA", "500")),
        make_observation("Node-A", "A-002", make_fragment("M300", "debit", "VillageA", "120")),
        make_observation("Node-A", "A-003", make_fragment("M400", "debit", "VillageA", "400")),
        make_observation("Node-A", "A-004", make_fragment("M500", "debit", "VillageA", "250")),
    ]

    node_b = [
        make_observation("Node-B", "B-001", make_fragment("M100", "credit", "VillageB", "500")),
        make_observation("Node-B", "B-002", make_fragment("M100", "credit", "VillageB", "500")),
        make_observation("Node-B", "B-003", make_fragment("M200", "credit", "VillageB", "300")),
        make_observation("Node-B", "B-004", make_fragment("M400", "credit", "VillageB", "450")),
        make_observation("Node-B", "B-005", make_fragment("M500", "credit", "VillageB", "250")),
        make_observation("Node-B", "B-006", make_fragment("M500", "credit", "VillageB_Alt", "250")),
    ]

    merged = merge_observation_sets(node_a, node_b)
    return {
        "name": "two-node",
        "balances": balances,
        "node_sets": {
            "Node-A": node_a,
            "Node-B": node_b,
        },
        "merged_observations": merged,
        "boundary_state": "OPEN",
    }


def scenario_three_node():
    balances = [
        make_balance("VillageA", "1000"),
        make_balance("VillageB", "1000"),
        make_balance("VillageC", "1000"),
    ]

    node_a = [
        make_observation("Node-A", "A-001", make_fragment("M100", "debit", "VillageA", "500")),
        make_observation("Node-A", "A-002", make_fragment("M300", "credit", "VillageA", "150")),
        make_observation("Node-A", "A-003", make_fragment("M400", "debit", "VillageA", "300")),
        make_observation("Node-A", "A-004", make_fragment("M500", "credit", "VillageA", "250")),
    ]

    node_b = [
        make_observation("Node-B", "B-001", make_fragment("M100", "credit", "VillageB", "500")),
        make_observation("Node-B", "B-002", make_fragment("M200", "debit", "VillageB", "200")),
        make_observation("Node-B", "B-003", make_fragment("M500", "debit", "VillageB", "250")),
        make_observation("Node-B", "B-004", make_fragment("M500", "debit", "VillageB_conflict", "250")),
    ]

    node_c = [
        make_observation("Node-C", "C-001", make_fragment("M200", "credit", "VillageC", "200")),
        make_observation("Node-C", "C-002", make_fragment("M300", "debit", "VillageC", "150")),
        make_observation("Node-C", "C-003", make_fragment("M400", "credit", "VillageC", "350")),
    ]

    merged = merge_observation_sets(node_a, node_b, node_c)
    return {
        "name": "three-node",
        "balances": balances,
        "node_sets": {
            "Node-A": node_a,
            "Node-B": node_b,
            "Node-C": node_c,
        },
        "merged_observations": merged,
        "boundary_state": "OPEN",
    }


def scenario_balance_conflict():
    balances = [
        make_balance("A", "100", "USD"),
        make_balance("B", "0", "USD"),
        make_balance("C", "0", "USD"),
    ]
    observations = [
        make_observation("Node-1", "O-001", make_fragment("T1", "debit", "A", "80", "USD")),
        make_observation("Node-2", "O-002", make_fragment("T1", "credit", "B", "80", "USD")),
        make_observation("Node-1", "O-003", make_fragment("T2", "debit", "A", "60", "USD")),
        make_observation("Node-3", "O-004", make_fragment("T2", "credit", "C", "60", "USD")),
    ]
    return {
        "name": "balance-conflict",
        "balances": balances,
        "node_sets": {
            "Node-1": [observations[0], observations[2]],
            "Node-2": [observations[1]],
            "Node-3": [observations[3]],
        },
        "merged_observations": observations,
        "boundary_state": "OPEN",
    }


def scenario_multi_unit():
    balances = [
        make_balance("A", "1000", "USD"),
        make_balance("B", "0", "USD"),
        make_balance("A", "500", "EUR"),
        make_balance("C", "0", "EUR"),
    ]
    observations = [
        make_observation("Node-A", "U-001", make_fragment("USD-1", "debit", "A", "200", "USD")),
        make_observation("Node-B", "U-002", make_fragment("USD-1", "credit", "B", "200", "USD")),
        make_observation("Node-A", "U-003", make_fragment("EUR-1", "debit", "A", "50", "EUR")),
        make_observation("Node-C", "U-004", make_fragment("EUR-1", "credit", "C", "50", "EUR")),
    ]
    return {
        "name": "multi-unit",
        "balances": balances,
        "node_sets": {},
        "merged_observations": observations,
        "boundary_state": "SEALED",
    }


def get_scenario(name):
    scenarios = {
        "two-node": scenario_two_node,
        "three-node": scenario_three_node,
        "balance-conflict": scenario_balance_conflict,
        "multi-unit": scenario_multi_unit,
    }
    if name not in scenarios:
        raise ValueError("unknown scenario")
    return scenarios[name]()


def simulate_three_node_rounds(scenario):
    node_a = scenario["node_sets"]["Node-A"]
    node_b = scenario["node_sets"]["Node-B"]
    node_c = scenario["node_sets"]["Node-C"]

    def round_exchange(a, b, c):
        return (
            merge_observation_sets(a, c),
            merge_observation_sets(b, a),
            merge_observation_sets(c, b),
        )

    before = [
        resolve_financial_bundle(scenario["balances"], node_a, "OPEN", False),
        resolve_financial_bundle(scenario["balances"], node_b, "OPEN", False),
        resolve_financial_bundle(scenario["balances"], node_c, "OPEN", False),
    ]
    a1, b1, c1 = round_exchange(node_a, node_b, node_c)
    round1 = [
        resolve_financial_bundle(scenario["balances"], a1, "OPEN", False),
        resolve_financial_bundle(scenario["balances"], b1, "OPEN", False),
        resolve_financial_bundle(scenario["balances"], c1, "OPEN", False),
    ]
    a2, b2, c2 = round_exchange(a1, b1, c1)
    round2 = [
        resolve_financial_bundle(scenario["balances"], a2, "OPEN", False),
        resolve_financial_bundle(scenario["balances"], b2, "OPEN", False),
        resolve_financial_bundle(scenario["balances"], c2, "OPEN", False),
    ]

    def all_match(bundles):
        ids = [bundle["financial_resolution_id"] for bundle in bundles]
        return len(set(ids)) == 1

    return {
        "before_match": all_match(before),
        "round_1_match": all_match(round1),
        "round_2_match": all_match(round2),
        "round_2_bundles": round2,
    }


def scenario_bundle(name, boundary_override=None):
    scenario = get_scenario(name)
    boundary_state = boundary_override or scenario["boundary_state"]
    bundle = resolve_financial_bundle(
        scenario["balances"],
        scenario["merged_observations"],
        boundary_state,
        True,
    )
    return scenario, bundle


def format_state_counts(counts):
    return "R:{0} I:{1} A:{2}".format(
        counts.get("RESOLVED", 0),
        counts.get("INCOMPLETE", 0),
        counts.get("ABSTAIN", 0),
    )


def print_line(label, value, width=34):
    print("  " + label.ljust(width) + " : " + str(value))


def print_bundle_summary(scenario, bundle):
    print("=" * 96)
    print("ORL-Money v" + VERSION + " | Deterministic Bounded Financial Reconciliation")
    print("=" * 96)
    print_line("Scenario", scenario["name"])
    print_line("Result", bundle["result"])
    if bundle["result"] != "ACCEPTED":
        for error in bundle.get("errors", []):
            print("  REFUSED: " + error)
        return

    print_line("Architecture profile", ARCHITECTURE_PROFILE)
    print_line("Ruleset profile", RULESET_PROFILE)
    print_line("Compatibility profile", COMPATIBILITY_PROFILE)
    print_line("Boundary", bundle["boundary"]["state"])
    print()

    evidence = bundle["evidence"]
    counts = bundle["transactions"]["state_counts"]
    print("Evidence")
    print("-" * 96)
    print_line("Raw observations", evidence["raw_observation_count"])
    print_line("Unique observations", evidence["unique_observation_count"])
    print_line("Unique financial claims", evidence["unique_claim_count"])
    print_line("Observation multiplicity", evidence["observation_multiplicity_count"])
    print_line("Claim set ID", evidence["claim_set_id"])
    print()

    print("Transaction Resolution")
    print("-" * 96)
    for receipt in bundle["transactions"]["receipts"]:
        print("  {0:<16} {1:<11} {2}".format(
            receipt["tx"],
            receipt["state"],
            receipt["reason_code"],
        ))
    print_line("State summary", format_state_counts(counts))
    print()

    print("Declared Balance Compatibility")
    print("-" * 96)
    print_line("State", bundle["declared_balance_compatibility"]["state"])
    for assessment in bundle["declared_balance_compatibility"]["assessments"]:
        suffix = ""
        if assessment["state"] == "CONFLICT" and "deficit_minor" in assessment:
            suffix = " deficit=" + assessment["deficit_minor"]
        print("  {0:<20} {1:<8} {2}{3}".format(
            assessment["account"],
            assessment["unit"],
            assessment["state"],
            suffix,
        ))
    print()

    print("Structural Projection")
    print("-" * 96)
    if bundle["structural_projection"]["state"] != "AVAILABLE":
        print_line("State", bundle["structural_projection"]["state"])
    else:
        for receipt in bundle["structural_projection"]["account_receipts"]:
            print("  {0:<20} {1:<8} initial={2:<16} delta={3:<16} final={4}".format(
                receipt["account"],
                receipt["unit"],
                receipt["initial_amount_minor"],
                receipt["net_delta_minor"],
                receipt["final_amount_minor"],
            ))
        for unit_receipt in bundle["structural_projection"]["unit_receipts"]:
            print("  {0:<13} total_initial={1:<16} total_final={2:<16} conservation={3}".format(
                unit_receipt["unit"],
                unit_receipt["initial_total_minor"],
                unit_receipt["final_total_minor"],
                unit_receipt["conservation_ok"],
            ))
    print()

    print("Deterministic Identities")
    print("-" * 96)
    print_line("Balance snapshot ID", bundle["balance_basis"]["balance_snapshot_id"])
    print_line("Transaction receipt root", bundle["transactions"]["transaction_receipt_root"])
    print_line("Projection root", bundle["structural_projection"]["projection_root"])
    print_line("Financial resolution ID", bundle["financial_resolution_id"])
    print_line("Financial bundle ID", bundle["financial_bundle_id"])
    print_line("Self verification", bundle["self_verification"]["valid"])

    if scenario["name"] == "three-node":
        rounds = simulate_three_node_rounds(scenario)
        print()
        print("Three-Node Reconstruction")
        print("-" * 96)
        print_line("Before match", rounds["before_match"])
        print_line("Round 1 match", rounds["round_1_match"])
        print_line("Round 2 match", rounds["round_2_match"])


class AuditRunner:
    def __init__(self):
        self.results = defaultdict(list)

    def check(self, group, name, condition, detail=""):
        passed = bool(condition)
        self.results[group].append({
            "name": name,
            "passed": passed,
            "detail": detail,
        })
        return passed

    def totals(self):
        passed = 0
        total = 0
        for items in self.results.values():
            for item in items:
                total += 1
                if item["passed"]:
                    passed += 1
        return passed, total

    def report(self):
        print("ORL-Money Audit | " + AUDIT_PROFILE)
        print("=" * 96)
        for group in self.results:
            items = self.results[group]
            passed = sum(1 for item in items if item["passed"])
            total = len(items)
            status = "PASS" if passed == total else "FAIL"
            print("{0:<34} {1:>4}/{2:<4} {3}".format(group, passed, total, status))
            if status == "FAIL":
                for item in items:
                    if not item["passed"]:
                        print("  FAIL " + item["name"] + (" | " + item["detail"] if item["detail"] else ""))
        passed, total = self.totals()
        print("-" * 96)
        print("TOTAL {0}/{1} {2}".format(passed, total, "PASS" if passed == total else "FAIL"))
        return passed == total


def audit_validation(audit):
    valid_balance = make_balance("A", "0", "USD")
    valid_fragment = make_fragment("T1", "debit", "A", "1", "USD")
    valid_observation = make_observation("N1", "R1", valid_fragment)
    audit.check("VALIDATION", "valid balance", not validate_balance_record(valid_balance))
    audit.check("VALIDATION", "valid fragment", not validate_fragment_record(valid_fragment))
    audit.check("VALIDATION", "valid observation", not validate_observation_record(valid_observation))

    invalid_balance_amounts = [1, "", "-1", "+1", "01", "1.0", "1e3", " 1", "1 ", "9" * 79]
    for index, value in enumerate(invalid_balance_amounts):
        record = make_balance("A", "0", "USD")
        record["amount_minor"] = value
        audit.check("VALIDATION", "invalid balance amount " + str(index), bool(validate_balance_record(record)))

    invalid_fragment_amounts = [0, "0", "", "-1", "+1", "01", "1.0", "1e3", "9" * 79]
    for index, value in enumerate(invalid_fragment_amounts):
        record = make_fragment("T", "debit", "A", "1", "USD")
        record["amount_minor"] = value
        audit.check("VALIDATION", "invalid fragment amount " + str(index), bool(validate_fragment_record(record)))

    fragment_78 = make_fragment("T", "debit", "A", "9" * 78, "USD")
    audit.check("VALIDATION", "78 digit amount accepted", not validate_fragment_record(fragment_78))

    record = make_fragment("T", "debit", "A", "1", "USD")
    record["extra"] = "x"
    audit.check("VALIDATION", "unknown fragment field refused", bool(validate_fragment_record(record)))

    record = make_fragment("T", "other", "A", "1", "USD")
    audit.check("VALIDATION", "invalid side refused", bool(validate_fragment_record(record)))

    record = make_fragment("T", "debit", "A", "1", "usd")
    audit.check("VALIDATION", "lowercase unit refused", bool(validate_fragment_record(record)))

    record = make_fragment(" T", "debit", "A", "1", "USD")
    audit.check("VALIDATION", "leading identifier whitespace refused", bool(validate_fragment_record(record)))

    decomposed = "Cafe\u0301"
    record = make_fragment(decomposed, "debit", "A", "1", "USD")
    audit.check("VALIDATION", "non NFC identifier refused", bool(validate_fragment_record(record)))

    record = make_fragment("T\n1", "debit", "A", "1", "USD")
    audit.check("VALIDATION", "control character refused", bool(validate_fragment_record(record)))

    record = make_fragment("T\ud800", "debit", "A", "1", "USD")
    audit.check("VALIDATION", "lone high surrogate refused", bool(validate_fragment_record(record)))

    record = make_fragment("T\udfff", "debit", "A", "1", "USD")
    audit.check("VALIDATION", "lone low surrogate refused", bool(validate_fragment_record(record)))

    record = make_fragment("T😀", "debit", "A", "1", "USD")
    audit.check("VALIDATION", "valid astral Unicode identifier accepted", not validate_fragment_record(record))

    record = make_fragment("T", "debit", "A", "1", "USD")
    record["schema"] = "OTHER"
    audit.check("VALIDATION", "schema mismatch refused", bool(validate_fragment_record(record)))

    refused = resolve_financial_bundle(
        [make_balance("A", "10", "USD")],
        [make_observation("N", "R", make_fragment("T", "debit", "A", "0", "USD"))],
        "OPEN",
        False,
    )
    audit.check("VALIDATION", "invalid bundle input produces refusal", refused["result"] == "REFUSED")

    surrogate_refusal = resolve_financial_bundle(
        [make_balance("A\ud800", "10", "USD")],
        [],
        "OPEN",
        False,
    )
    audit.check("VALIDATION", "surrogate bundle input produces refusal", surrogate_refusal["result"] == "REFUSED")

    non_array_balances = resolve_financial_bundle({}, [], "OPEN", False)
    audit.check("VALIDATION", "non-array balances refused", non_array_balances["result"] == "REFUSED")

    non_array_observations = resolve_financial_bundle([], {}, "OPEN", False)
    audit.check("VALIDATION", "non-array observations refused", non_array_observations["result"] == "REFUSED")


def audit_canonicalization(audit):
    left = {"b": 2, "a": 1, "nested": {"z": 3, "x": 2}}
    right = {"nested": {"x": 2, "z": 3}, "a": 1, "b": 2}
    audit.check("CANONICALIZATION", "object key order canonical", canonical_json(left) == canonical_json(right))
    audit.check("CANONICALIZATION", "identity key order stable", identity("x", "p", left) == identity("x", "p", right))
    audit.check("CANONICALIZATION", "UTF-8 canonical repeatable", canonical_json({"x": "தமிழ்"}) == canonical_json({"x": "தமிழ்"}))
    audit.check("CANONICALIZATION", "empty object hash stable", sha256_text(canonical_json({})) == sha256_text("{}"))
    audit.check("CANONICALIZATION", "array order preserved", canonical_json([1, 2]) != canonical_json([2, 1]))
    for index in range(10):
        value = {"k": index, "a": [index, index + 1]}
        audit.check("CANONICALIZATION", "repeat identity " + str(index), identity("r", "p", value) == identity("r", "p", deepcopy(value)))


def audit_claim_observation(audit):
    balances = [make_balance("A", "100", "USD"), make_balance("B", "0", "USD")]
    fragment = make_fragment("T1", "debit", "A", "20", "USD")
    o1 = make_observation("N1", "R1", fragment)
    o2 = make_observation("N2", "R2", fragment)
    result = prepare_observations([o1, o2])
    audit.check("CLAIM / OBSERVATION", "two observations one claim", result["unique_claim_count"] == 1)
    audit.check("CLAIM / OBSERVATION", "two observations preserved", result["unique_observation_count"] == 2)
    audit.check("CLAIM / OBSERVATION", "observation multiplicity counted", result["observation_multiplicity_count"] == 1)
    audit.check("CLAIM / OBSERVATION", "claim identity independent of origin", claim_id(o1["fragment"]) == claim_id(o2["fragment"]))
    audit.check("CLAIM / OBSERVATION", "observation identity depends on origin", observation_id(o1) != observation_id(o2))

    duplicate_result = prepare_observations([o1, deepcopy(o1)])
    audit.check("CLAIM / OBSERVATION", "exact observation duplicate absorbed", duplicate_result["unique_observation_count"] == 1)
    audit.check("CLAIM / OBSERVATION", "exact observation duplicate counted", duplicate_result["exact_observation_duplicate_count"] == 1)

    credit = make_observation("N3", "R3", make_fragment("T1", "credit", "B", "20", "USD"))
    bundle_a = resolve_financial_bundle(balances, [o1, credit], "OPEN", False)
    bundle_b = resolve_financial_bundle(balances, [o2, credit], "OPEN", False)
    audit.check("CLAIM / OBSERVATION", "provenance-neutral financial resolution", bundle_a["financial_resolution_id"] == bundle_b["financial_resolution_id"])
    audit.check("CLAIM / OBSERVATION", "provenance-sensitive evidence bundle", bundle_a["financial_bundle_id"] != bundle_b["financial_bundle_id"])

    ref_changed = make_observation("N1", "R9", fragment)
    audit.check("CLAIM / OBSERVATION", "reference changes observation identity", observation_id(o1) != observation_id(ref_changed))
    audit.check("CLAIM / OBSERVATION", "reference does not change claim identity", claim_id(o1["fragment"]) == claim_id(ref_changed["fragment"]))

    source_changed = make_observation("N9", "R1", fragment)
    audit.check("CLAIM / OBSERVATION", "source changes observation identity", observation_id(o1) != observation_id(source_changed))
    audit.check("CLAIM / OBSERVATION", "source does not change claim identity", claim_id(o1["fragment"]) == claim_id(source_changed["fragment"]))


def simple_bundle(fragments, balances=None, boundary="OPEN"):
    if balances is None:
        balances = [
            make_balance("A", "1000000", "USD"),
            make_balance("B", "1000000", "USD"),
            make_balance("C", "1000000", "USD"),
            make_balance("D", "1000000", "EUR"),
        ]
    observations = [
        make_observation("N" + str(index % 3), "R" + str(index), fragment)
        for index, fragment in enumerate(fragments)
    ]
    return resolve_financial_bundle(balances, observations, boundary, False)


def audit_resolution(audit):
    cases = [
        (
            "matching pair",
            [make_fragment("T", "debit", "A", "10", "USD"), make_fragment("T", "credit", "B", "10", "USD")],
            "RESOLVED",
            "MATCHED_DEBIT_CREDIT_PAIR",
        ),
        (
            "missing debit",
            [make_fragment("T", "credit", "B", "10", "USD")],
            "INCOMPLETE",
            "MISSING_DEBIT_CLAIM",
        ),
        (
            "missing credit",
            [make_fragment("T", "debit", "A", "10", "USD")],
            "INCOMPLETE",
            "MISSING_CREDIT_CLAIM",
        ),
        (
            "amount mismatch",
            [make_fragment("T", "debit", "A", "10", "USD"), make_fragment("T", "credit", "B", "11", "USD")],
            "ABSTAIN",
            "AMOUNT_MISMATCH",
        ),
        (
            "unit mismatch",
            [make_fragment("T", "debit", "A", "10", "USD"), make_fragment("T", "credit", "B", "10", "EUR")],
            "ABSTAIN",
            "UNIT_MISMATCH",
        ),
        (
            "multiple debit",
            [make_fragment("T", "debit", "A", "10", "USD"), make_fragment("T", "debit", "C", "10", "USD"), make_fragment("T", "credit", "B", "10", "USD")],
            "ABSTAIN",
            "MULTIPLE_DEBIT_CLAIMS",
        ),
        (
            "multiple credit",
            [make_fragment("T", "debit", "A", "10", "USD"), make_fragment("T", "credit", "B", "10", "USD"), make_fragment("T", "credit", "C", "10", "USD")],
            "ABSTAIN",
            "MULTIPLE_CREDIT_CLAIMS",
        ),
        (
            "multiple both",
            [make_fragment("T", "debit", "A", "10", "USD"), make_fragment("T", "debit", "C", "10", "USD"), make_fragment("T", "credit", "B", "10", "USD"), make_fragment("T", "credit", "D", "10", "USD")],
            "ABSTAIN",
            "MULTIPLE_DEBIT_AND_CREDIT_CLAIMS",
        ),
    ]
    for name, fragments, expected_state, expected_reason in cases:
        bundle = simple_bundle(fragments)
        receipt = bundle["transactions"]["receipts"][0]
        audit.check("RESOLUTION", name + " state", receipt["state"] == expected_state)
        audit.check("RESOLUTION", name + " reason", receipt["reason_code"] == expected_reason)
        if expected_state == "RESOLVED":
            audit.check("RESOLUTION", name + " has two contributions", len(receipt["contributions"]) == 2)
        else:
            audit.check("RESOLUTION", name + " has no contributions", receipt["contributions"] == [])

    self_transfer = simple_bundle([
        make_fragment("SELF", "debit", "A", "10", "USD"),
        make_fragment("SELF", "credit", "A", "10", "USD"),
    ])
    audit.check("RESOLUTION", "self transfer structurally resolves", transaction_state_map(self_transfer)["SELF"] == "RESOLVED")
    audit.check("RESOLUTION", "self transfer net zero", final_balance_map(self_transfer)[("A", "USD")] == "1000000")

    precedence = simple_bundle([
        make_fragment("P", "debit", "A", "10", "USD"),
        make_fragment("P", "debit", "C", "11", "EUR"),
        make_fragment("P", "credit", "B", "12", "USD"),
        make_fragment("P", "credit", "D", "13", "EUR"),
    ])
    audit.check(
        "RESOLUTION",
        "multiplicity precedence before amount or unit",
        transaction_reason_map(precedence)["P"] == "MULTIPLE_DEBIT_AND_CREDIT_CLAIMS",
    )


def audit_exact_money(audit):
    huge = "9" * 78
    balances = [make_balance("A", huge, "USD"), make_balance("B", "0", "USD")]
    amount = "1" + "0" * 76
    fragments = [
        make_fragment("H", "debit", "A", amount, "USD"),
        make_fragment("H", "credit", "B", amount, "USD"),
    ]
    bundle = simple_bundle(fragments, balances)
    finals = final_balance_map(bundle)
    expected_a = str(int(huge) - int(amount))
    audit.check("EXACT MONEY", "78 digit initial exact", finals[("A", "USD")] == expected_a)
    audit.check("EXACT MONEY", "77 digit transfer exact", finals[("B", "USD")] == amount)
    audit.check("EXACT MONEY", "huge conservation", unit_conservation_map(bundle)["USD"] is True)

    for digits in [1, 2, 10, 25, 50, 78]:
        value = "1" if digits == 1 else "1" + "0" * (digits - 1)
        fragment = make_fragment("T" + str(digits), "debit", "A", value, "USD")
        audit.check("EXACT MONEY", "canonical amount length " + str(digits), not validate_fragment_record(fragment))

    bundle = simple_bundle([
        make_fragment("X", "debit", "A", "9007199254740993", "USD"),
        make_fragment("X", "credit", "B", "9007199254740993", "USD"),
    ])
    audit.check("EXACT MONEY", "above JavaScript safe integer preserved", transaction_state_map(bundle)["X"] == "RESOLVED")


def audit_balance_basis(audit):
    exact_duplicate = resolve_balance_basis([
        make_balance("A", "10", "USD"),
        make_balance("A", "10", "USD"),
    ])
    audit.check("BALANCE BASIS", "exact duplicate balance absorbed", exact_duplicate["state"] == "RESOLVED")
    audit.check("BALANCE BASIS", "exact duplicate balance counted", exact_duplicate["exact_duplicate_count"] == 1)

    conflict = resolve_balance_basis([
        make_balance("A", "10", "USD"),
        make_balance("A", "11", "USD"),
    ])
    audit.check("BALANCE BASIS", "conflicting balance explicit", conflict["state"] == "CONFLICT")
    audit.check("BALANCE BASIS", "conflicting balance witness present", len(conflict["conflicts"]) == 1)

    units = resolve_balance_basis([
        make_balance("A", "10", "USD"),
        make_balance("A", "11", "EUR"),
    ])
    audit.check("BALANCE BASIS", "same account different units independent", units["state"] == "RESOLVED")
    audit.check("BALANCE BASIS", "two unit records preserved", len(units["balances"]) == 2)

    reordered_a = resolve_balance_basis([make_balance("A", "10", "USD"), make_balance("B", "20", "USD")])
    reordered_b = resolve_balance_basis([make_balance("B", "20", "USD"), make_balance("A", "10", "USD")])
    audit.check("BALANCE BASIS", "balance order independent", reordered_a["balance_snapshot_id"] == reordered_b["balance_snapshot_id"])


def audit_merge_algebra(audit):
    scenario = scenario_two_node()
    observations = scenario["merged_observations"][:5]
    base = resolve_financial_bundle(scenario["balances"], observations, "OPEN", False)
    base_resolution = base["financial_resolution_id"]
    base_bundle = base["financial_bundle_id"]

    for index, permutation in enumerate(itertools.permutations(observations)):
        bundle = resolve_financial_bundle(scenario["balances"], list(permutation), "OPEN", False)
        audit.check("MERGE ALGEBRA", "permutation resolution " + str(index), bundle["financial_resolution_id"] == base_resolution)
        audit.check("MERGE ALGEBRA", "permutation evidence bundle " + str(index), bundle["financial_bundle_id"] == base_bundle)

    pieces = [[observations[0]], [observations[1], observations[2]], [observations[3], observations[4]]]
    merged_left = merge_observation_sets(pieces[0], merge_observation_sets(pieces[1], pieces[2]))
    merged_right = merge_observation_sets(merge_observation_sets(pieces[0], pieces[1]), pieces[2])
    audit.check("MERGE ALGEBRA", "associative merge identity", prepare_observations(merged_left)["observation_set_id"] == prepare_observations(merged_right)["observation_set_id"])

    merged_ab = merge_observation_sets(pieces[0], pieces[1])
    merged_ba = merge_observation_sets(pieces[1], pieces[0])
    audit.check("MERGE ALGEBRA", "commutative merge identity", prepare_observations(merged_ab)["observation_set_id"] == prepare_observations(merged_ba)["observation_set_id"])

    merged_idempotent = merge_observation_sets(observations, observations)
    audit.check("MERGE ALGEBRA", "idempotent exact observation merge", prepare_observations(merged_idempotent)["observation_set_id"] == prepare_observations(observations)["observation_set_id"])

    four = observations[:4]
    target = prepare_observations(four)["claim_set_id"]
    for mask in range(16):
        left = []
        right = []
        for index, observation in enumerate(four):
            if mask & (1 << index):
                left.append(observation)
            else:
                right.append(observation)
        merged = merge_observation_sets(left, right)
        audit.check("MERGE ALGEBRA", "partition claim set " + str(mask), prepare_observations(merged)["claim_set_id"] == target)


def audit_multi_unit(audit):
    scenario, bundle = scenario_bundle("multi-unit")
    states = transaction_state_map(bundle)
    finals = final_balance_map(bundle)
    audit.check("MULTI-UNIT", "USD transaction resolves", states["USD-1"] == "RESOLVED")
    audit.check("MULTI-UNIT", "EUR transaction resolves", states["EUR-1"] == "RESOLVED")
    audit.check("MULTI-UNIT", "USD sender final", finals[("A", "USD")] == "800")
    audit.check("MULTI-UNIT", "USD receiver final", finals[("B", "USD")] == "200")
    audit.check("MULTI-UNIT", "EUR sender final", finals[("A", "EUR")] == "450")
    audit.check("MULTI-UNIT", "EUR receiver final", finals[("C", "EUR")] == "50")
    conservation = unit_conservation_map(bundle)
    audit.check("MULTI-UNIT", "USD conservation", conservation["USD"] is True)
    audit.check("MULTI-UNIT", "EUR conservation", conservation["EUR"] is True)

    mismatch = simple_bundle([
        make_fragment("U", "debit", "A", "10", "USD"),
        make_fragment("U", "credit", "B", "10", "EUR"),
    ])
    audit.check("MULTI-UNIT", "cross-unit pair abstains", transaction_state_map(mismatch)["U"] == "ABSTAIN")
    audit.check("MULTI-UNIT", "cross-unit reason", transaction_reason_map(mismatch)["U"] == "UNIT_MISMATCH")


def audit_compatibility(audit):
    two_scenario, two_bundle = scenario_bundle("two-node")
    audit.check("BALANCE COMPATIBILITY", "reference compatible", two_bundle["declared_balance_compatibility"]["state"] == "COMPATIBLE")

    conflict_scenario, conflict_bundle = scenario_bundle("balance-conflict")
    audit.check("BALANCE COMPATIBILITY", "aggregate outflow conflict", conflict_bundle["declared_balance_compatibility"]["state"] == "CONFLICT")
    states = transaction_state_map(conflict_bundle)
    audit.check("BALANCE COMPATIBILITY", "T1 remains structurally resolved", states["T1"] == "RESOLVED")
    audit.check("BALANCE COMPATIBILITY", "T2 remains structurally resolved", states["T2"] == "RESOLVED")
    assessment = conflict_bundle["declared_balance_compatibility"]["assessments"][0]
    audit.check("BALANCE COMPATIBILITY", "conflict deficit exact", assessment["deficit_minor"] == "40")
    audit.check("BALANCE COMPATIBILITY", "conflict witness lists both transactions", len(assessment["contributing_transactions"]) == 2)

    missing_basis = simple_bundle(
        [make_fragment("T", "debit", "Z", "10", "USD"), make_fragment("T", "credit", "B", "10", "USD")],
        [make_balance("B", "0", "USD")],
    )
    audit.check("BALANCE COMPATIBILITY", "missing basis unassessed", missing_basis["declared_balance_compatibility"]["state"] == "UNASSESSED")

    incoming_does_not_offset = simple_bundle(
        [
            make_fragment("T1", "debit", "A", "80", "USD"),
            make_fragment("T1", "credit", "B", "80", "USD"),
            make_fragment("T2", "debit", "A", "60", "USD"),
            make_fragment("T2", "credit", "C", "60", "USD"),
            make_fragment("T3", "debit", "B", "100", "USD"),
            make_fragment("T3", "credit", "A", "100", "USD"),
        ],
        [make_balance("A", "100", "USD"), make_balance("B", "1000", "USD"), make_balance("C", "0", "USD")],
    )
    audit.check("BALANCE COMPATIBILITY", "incoming does not offset gross profile", incoming_does_not_offset["declared_balance_compatibility"]["state"] == "CONFLICT")

    permuted_ids = set()
    observations = conflict_scenario["merged_observations"]
    for permutation in itertools.permutations(observations):
        bundle = resolve_financial_bundle(conflict_scenario["balances"], list(permutation), "OPEN", False)
        permuted_ids.add(bundle["declared_balance_compatibility"]["compatibility_receipt_id"])
    audit.check("BALANCE COMPATIBILITY", "conflict receipt order independent", len(permuted_ids) == 1)


def audit_projection(audit):
    scenario, bundle = scenario_bundle("two-node")
    finals = final_balance_map(bundle)
    audit.check("PROJECTION", "VillageA final 500", finals[("VillageA", "UNIT")] == "500")
    audit.check("PROJECTION", "VillageB final 1500", finals[("VillageB", "UNIT")] == "1500")
    audit.check("PROJECTION", "unit conserved", unit_conservation_map(bundle)["UNIT"] is True)

    non_resolved = simple_bundle([
        make_fragment("I", "debit", "A", "10", "USD"),
        make_fragment("X", "debit", "A", "20", "USD"),
        make_fragment("X", "credit", "B", "21", "USD"),
    ])
    finals = final_balance_map(non_resolved)
    audit.check("PROJECTION", "incomplete no effect A", finals[("A", "USD")] == "1000000")
    audit.check("PROJECTION", "abstain no effect B", finals[("B", "USD")] == "1000000")

    for account_receipt in bundle["structural_projection"]["account_receipts"]:
        calculated = int(account_receipt["initial_amount_minor"]) + sum(
            int(item["delta_minor"]) for item in account_receipt["contributions"]
        )
        audit.check(
            "PROJECTION",
            "lineage arithmetic " + account_receipt["account"],
            calculated == int(account_receipt["final_amount_minor"]),
        )

    conflicting_basis = resolve_financial_bundle(
        [make_balance("A", "10", "USD"), make_balance("A", "11", "USD")],
        [
            make_observation("N", "R1", make_fragment("T", "debit", "A", "1", "USD")),
            make_observation("N", "R2", make_fragment("T", "credit", "B", "1", "USD")),
        ],
        "OPEN",
        False,
    )
    audit.check("PROJECTION", "conflicting balance basis projection unavailable", conflicting_basis["structural_projection"]["state"] == "UNAVAILABLE")


def audit_boundary(audit):
    scenario = scenario_two_node()
    open_bundle = resolve_financial_bundle(scenario["balances"], scenario["merged_observations"], "OPEN", False)
    sealed_bundle = resolve_financial_bundle(scenario["balances"], scenario["merged_observations"], "SEALED", False)
    audit.check("BOUNDARY", "open state", open_bundle["boundary"]["state"] == "OPEN")
    audit.check("BOUNDARY", "sealed state", sealed_bundle["boundary"]["state"] == "SEALED")
    audit.check("BOUNDARY", "sealed binds current claim set", sealed_bundle["boundary"]["declared_sealed_claim_set_id"] == sealed_bundle["evidence"]["claim_set_id"])
    audit.check("BOUNDARY", "open has no sealed claim set", open_bundle["boundary"]["declared_sealed_claim_set_id"] is None)
    audit.check("BOUNDARY", "boundary does not change transaction states", transaction_state_map(open_bundle) == transaction_state_map(sealed_bundle))
    audit.check("BOUNDARY", "boundary changes financial resolution identity", open_bundle["financial_resolution_id"] != sealed_bundle["financial_resolution_id"])
    invalid = resolve_financial_bundle(scenario["balances"], scenario["merged_observations"], "OTHER", False)
    audit.check("BOUNDARY", "invalid boundary refused", invalid["result"] == "REFUSED")


def audit_receipts_and_tamper(audit):
    scenario, bundle = scenario_bundle("two-node")
    audit.check("RECEIPTS / TAMPER", "self verification pass", bundle["self_verification"]["valid"] is True)
    audit.check("RECEIPTS / TAMPER", "direct verification pass", verify_bundle(bundle)["valid"] is True)

    for receipt in bundle["transactions"]["receipts"]:
        known_claims = set(bundle["evidence"]["claims"][index]["claim_id"] for index in range(len(bundle["evidence"]["claims"])))
        audit.check(
            "RECEIPTS / TAMPER",
            "transaction witness claims known " + receipt["tx"],
            set(receipt["claim_ids"]).issubset(known_claims),
        )

    for account_receipt in bundle["structural_projection"]["account_receipts"]:
        receipt_without_id = {k: v for k, v in account_receipt.items() if k != "account_projection_id"}
        expected = identity("account_projection", PROJECTION_PROFILE, receipt_without_id)
        audit.check(
            "RECEIPTS / TAMPER",
            "account receipt identity " + account_receipt["account"],
            account_receipt["account_projection_id"] == expected,
        )

    tamper_cases = []
    tampered = deepcopy(bundle)
    tampered["financial_resolution_id"] = "financial_resolution_bad"
    tamper_cases.append(("financial resolution id", tampered))

    tampered = deepcopy(bundle)
    tampered["transactions"]["receipts"][0]["state"] = "ABSTAIN"
    tamper_cases.append(("transaction state", tampered))

    tampered = deepcopy(bundle)
    tampered["evidence"]["claims"][0]["fragment"]["amount_minor"] = "999"
    tamper_cases.append(("claim amount", tampered))

    tampered = deepcopy(bundle)
    tampered["structural_projection"]["account_receipts"][0]["final_amount_minor"] = "999"
    tamper_cases.append(("projection final", tampered))

    tampered = deepcopy(bundle)
    tampered["declared_balance_compatibility"]["state"] = "CONFLICT"
    tamper_cases.append(("compatibility state", tampered))

    tampered = deepcopy(bundle)
    tampered["boundary"]["state"] = "SEALED"
    tamper_cases.append(("boundary state", tampered))

    tampered = deepcopy(bundle)
    tampered["inputs"]["observations"][0]["source"] = "Other-Node"
    tamper_cases.append(("embedded observation source", tampered))

    tampered = deepcopy(bundle)
    tampered["financial_bundle_id"] = "financial_bundle_bad"
    tamper_cases.append(("financial bundle id", tampered))

    for name, tampered_bundle in tamper_cases:
        audit.check("RECEIPTS / TAMPER", "tamper rejected: " + name, verify_bundle(tampered_bundle)["valid"] is False)


def audit_reference_scenarios(audit):
    two_scenario, two_bundle = scenario_bundle("two-node")
    states = transaction_state_map(two_bundle)
    expected_two = {
        "M100": "RESOLVED",
        "M200": "INCOMPLETE",
        "M300": "INCOMPLETE",
        "M400": "ABSTAIN",
        "M500": "ABSTAIN",
    }
    audit.check("REFERENCE SCENARIOS", "two-node states", states == expected_two)
    audit.check("REFERENCE SCENARIOS", "two-node counts", two_bundle["transactions"]["state_counts"] == {"RESOLVED": 1, "INCOMPLETE": 2, "ABSTAIN": 2})
    finals = final_balance_map(two_bundle)
    audit.check("REFERENCE SCENARIOS", "two-node VillageA", finals[("VillageA", "UNIT")] == "500")
    audit.check("REFERENCE SCENARIOS", "two-node VillageB", finals[("VillageB", "UNIT")] == "1500")
    audit.check("REFERENCE SCENARIOS", "two-node compatibility", two_bundle["declared_balance_compatibility"]["state"] == "COMPATIBLE")
    audit.check("REFERENCE SCENARIOS", "two-node observation multiplicity", two_bundle["evidence"]["observation_multiplicity_count"] == 1)
    two_repeat = resolve_financial_bundle(two_scenario["balances"], two_scenario["merged_observations"], "OPEN", False)
    audit.check("REFERENCE SCENARIOS", "two-node resolution repeatable", two_repeat["financial_resolution_id"] == two_bundle["financial_resolution_id"])
    audit.check("REFERENCE SCENARIOS", "two-node bundle repeatable", two_repeat["financial_bundle_id"] == two_bundle["financial_bundle_id"])

    three_scenario, three_bundle = scenario_bundle("three-node")
    expected_three = {
        "M100": "RESOLVED",
        "M200": "RESOLVED",
        "M300": "RESOLVED",
        "M400": "ABSTAIN",
        "M500": "ABSTAIN",
    }
    audit.check("REFERENCE SCENARIOS", "three-node states", transaction_state_map(three_bundle) == expected_three)
    audit.check("REFERENCE SCENARIOS", "three-node counts", three_bundle["transactions"]["state_counts"] == {"RESOLVED": 3, "INCOMPLETE": 0, "ABSTAIN": 2})
    finals = final_balance_map(three_bundle)
    audit.check("REFERENCE SCENARIOS", "three-node VillageA", finals[("VillageA", "UNIT")] == "650")
    audit.check("REFERENCE SCENARIOS", "three-node VillageB", finals[("VillageB", "UNIT")] == "1300")
    audit.check("REFERENCE SCENARIOS", "three-node VillageC", finals[("VillageC", "UNIT")] == "1050")
    audit.check("REFERENCE SCENARIOS", "three-node compatibility", three_bundle["declared_balance_compatibility"]["state"] == "COMPATIBLE")
    rounds = simulate_three_node_rounds(three_scenario)
    audit.check("REFERENCE SCENARIOS", "three-node before mismatch", rounds["before_match"] is False)
    audit.check("REFERENCE SCENARIOS", "three-node round1 mismatch", rounds["round_1_match"] is False)
    audit.check("REFERENCE SCENARIOS", "three-node round2 match", rounds["round_2_match"] is True)

    conflict_scenario, conflict_bundle = scenario_bundle("balance-conflict")
    audit.check("REFERENCE SCENARIOS", "balance conflict transactions resolved", all(state == "RESOLVED" for state in transaction_state_map(conflict_bundle).values()))
    audit.check("REFERENCE SCENARIOS", "balance conflict explicit", conflict_bundle["declared_balance_compatibility"]["state"] == "CONFLICT")
    conflict_finals = final_balance_map(conflict_bundle)
    audit.check("REFERENCE SCENARIOS", "balance conflict structural A negative", conflict_finals[("A", "USD")] == "-40")


def audit_origin_neutrality(audit):
    balances = [make_balance("A", "100", "USD"), make_balance("B", "0", "USD")]
    debit = make_fragment("T", "debit", "A", "10", "USD")
    credit = make_fragment("T", "credit", "B", "10", "USD")
    variants = []
    for index in range(20):
        observations = [
            make_observation("Debit-Source-" + str(index), "D-" + str(index), debit),
            make_observation("Credit-Source-" + str(19 - index), "C-" + str(index), credit),
        ]
        variants.append(resolve_financial_bundle(balances, observations, "OPEN", False))
    resolution_ids = set(bundle["financial_resolution_id"] for bundle in variants)
    bundle_ids = set(bundle["financial_bundle_id"] for bundle in variants)
    audit.check("ORIGIN NEUTRALITY", "all financial resolutions equal", len(resolution_ids) == 1)
    audit.check("ORIGIN NEUTRALITY", "provenance bundles remain distinguishable", len(bundle_ids) == 20)


def audit_known_regressions(audit):
    scenario = scenario_two_node()
    base = resolve_financial_bundle(scenario["balances"], scenario["merged_observations"], "OPEN", False)

    duplicate_claim_new_observation = deepcopy(scenario["merged_observations"])
    duplicate_claim_new_observation.append(
        make_observation("Node-C", "C-DUP", make_fragment("M100", "credit", "VillageB", "500"))
    )
    duplicate_bundle = resolve_financial_bundle(scenario["balances"], duplicate_claim_new_observation, "OPEN", False)
    audit.check("KNOWN REGRESSIONS", "duplicate claim observation leaves resolution unchanged", duplicate_bundle["financial_resolution_id"] == base["financial_resolution_id"])
    audit.check("KNOWN REGRESSIONS", "duplicate claim observation changes provenance bundle", duplicate_bundle["financial_bundle_id"] != base["financial_bundle_id"])

    exact_duplicate_observation = deepcopy(scenario["merged_observations"])
    exact_duplicate_observation.append(deepcopy(exact_duplicate_observation[0]))
    exact_duplicate_bundle = resolve_financial_bundle(scenario["balances"], exact_duplicate_observation, "OPEN", False)
    audit.check("KNOWN REGRESSIONS", "exact observation duplicate leaves full bundle unchanged", exact_duplicate_bundle["financial_bundle_id"] == base["financial_bundle_id"])

    all_reversed = list(reversed(scenario["merged_observations"]))
    reversed_bundle = resolve_financial_bundle(list(reversed(scenario["balances"])), all_reversed, "OPEN", False)
    audit.check("KNOWN REGRESSIONS", "balance and observation order do not alter resolution", reversed_bundle["financial_resolution_id"] == base["financial_resolution_id"])
    audit.check("KNOWN REGRESSIONS", "balance and observation order do not alter bundle", reversed_bundle["financial_bundle_id"] == base["financial_bundle_id"])

    incomplete = simple_bundle([make_fragment("I", "debit", "A", "10", "USD")])
    complete = simple_bundle([
        make_fragment("I", "debit", "A", "10", "USD"),
        make_fragment("I", "credit", "B", "10", "USD"),
    ])
    conflict = simple_bundle([
        make_fragment("I", "debit", "A", "10", "USD"),
        make_fragment("I", "credit", "B", "10", "USD"),
        make_fragment("I", "credit", "C", "10", "USD"),
    ])
    audit.check("KNOWN REGRESSIONS", "evidence growth incomplete to resolved", transaction_state_map(incomplete)["I"] == "INCOMPLETE" and transaction_state_map(complete)["I"] == "RESOLVED")
    audit.check("KNOWN REGRESSIONS", "evidence growth resolved to abstain", transaction_state_map(complete)["I"] == "RESOLVED" and transaction_state_map(conflict)["I"] == "ABSTAIN")

    surrogate = resolve_financial_bundle(
        [make_balance("A\ud800", "10", "USD")],
        [],
        "OPEN",
        False,
    )
    audit.check("KNOWN REGRESSIONS", "lone surrogate is refused without hashing crash", surrogate.get("result") == "REFUSED")

    sealed = resolve_financial_bundle(scenario["balances"], scenario["merged_observations"], "SEALED", False)
    audit.check("KNOWN REGRESSIONS", "sealed does not imply different transaction truth", transaction_state_map(sealed) == transaction_state_map(base))
    audit.check("KNOWN REGRESSIONS", "sealed is identity-distinct boundary declaration", sealed["financial_resolution_id"] != base["financial_resolution_id"])


def run_audit():
    audit = AuditRunner()
    audit_validation(audit)
    audit_canonicalization(audit)
    audit_balance_basis(audit)
    audit_claim_observation(audit)
    audit_resolution(audit)
    audit_exact_money(audit)
    audit_merge_algebra(audit)
    audit_multi_unit(audit)
    audit_compatibility(audit)
    audit_projection(audit)
    audit_boundary(audit)
    audit_receipts_and_tamper(audit)
    audit_reference_scenarios(audit)
    audit_origin_neutrality(audit)
    audit_known_regressions(audit)
    return audit.report()


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="ORL-Money deterministic bounded financial reconciliation reference kernel"
    )
    parser.add_argument(
        "--scenario",
        choices=["two-node", "three-node", "balance-conflict", "multi-unit"],
        default="two-node",
    )
    parser.add_argument(
        "--boundary",
        choices=["OPEN", "SEALED"],
        default=None,
    )
    parser.add_argument(
        "--audit",
        action="store_true",
    )
    parser.add_argument(
        "--json",
        action="store_true",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv if argv is not None else sys.argv[1:])
    if args.audit:
        return 0 if run_audit() else 1

    scenario, bundle = scenario_bundle(args.scenario, args.boundary)
    if args.json:
        print(canonical_json(bundle))
    else:
        print_bundle_summary(scenario, bundle)
    return 0 if bundle.get("result") == "ACCEPTED" else 1


if __name__ == "__main__":
    sys.exit(main())
