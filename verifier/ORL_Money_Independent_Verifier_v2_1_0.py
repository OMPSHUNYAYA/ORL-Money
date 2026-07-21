#!/usr/bin/env python3

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory

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
PRODUCER_VERIFICATION_PROFILE = "ORL-MONEY-VERIFICATION-1-D02"
INDEPENDENT_VERIFICATION_PROFILE = "ORL-MONEY-INDEPENDENT-VERIFICATION-1-D02"
SELF_TEST_PROFILE = "ORL-MONEY-INDEPENDENT-VERIFIER-SELF-TEST-1-D02"
CORPUS_PROFILE = "ORL-MONEY-FROZEN-CORPUS-1-D02"
CORPUS_MANIFEST_PROFILE = "ORL-MONEY-FROZEN-CORPUS-MANIFEST-1-D02"
CORPUS_VERIFICATION_PROFILE = "ORL-MONEY-CORPUS-VERIFICATION-1-D01"
MAX_AMOUNT_DIGITS = 78
MAX_IDENTIFIER_LENGTH = 128
MAX_INPUT_BYTES = 16 * 1024 * 1024
UNIT_PATTERN = re.compile(r"^[A-Z][A-Z0-9_-]{0,15}$")
AMOUNT_ZERO_PATTERN = re.compile(r"^(0|[1-9][0-9]{0,77})$")
AMOUNT_POSITIVE_PATTERN = re.compile(r"^[1-9][0-9]{0,77}$")

FROZEN_REFERENCE_IDS = {'two-node': {'financial_resolution_id': 'financial_resolution_a22b3ac1bea76f7f7573f539a8a2c76c257d149fc5b8a965fe17b0314f2154c0',
              'financial_bundle_id': 'financial_bundle_675d2d0d6fd03e48c7839efcf7cf35b802ea6741aacdb0fd3682c3c599d27c38',
              'balance_snapshot_id': 'balance_snapshot_9b22eae82a25f700aec1a4efd7162fc64ac07f37d173cd0cda7e90b4d84bfcdc',
              'claim_set_id': 'claim_set_dc35cbd895ede4ae674ccd06eea26fef0fab6dec877d7f3cc54b977e04e1d77a',
              'observation_set_id': 'observation_set_79e6c890d4247e714365e70202b2160c16a06e8db261b29fbc41421891b29f24',
              'transaction_receipt_root': 'tx_receipt_root_b2980313d76866ac9832fa09c71fe8257b9cf37ae5ffda44e304798ad4cbcfad',
              'projection_root': 'projection_dd0a38dd97ebf7978ba78aca28238a1dd9569122a060445b2ebadb21f4eccdda',
              'compatibility_receipt_id': 'compatibility_c2b31eec3ce977d86072a383c80b49afe6a95058a47e4790f34db69672bf05a5',
              'boundary_receipt_id': 'boundary_a3f06eb5ebf8a8928b8b416ce4318e1401a872e4293e21377c4b0443041eb839'},
 'three-node': {'financial_resolution_id': 'financial_resolution_eff3518564740a56633fe54188412bed95fa6730806d1c9a417f7e9edce48750',
                'financial_bundle_id': 'financial_bundle_cecf58e08d1094ca544933bb41224f0b62eb45361d2cab3cc51db724453da5a7',
                'balance_snapshot_id': 'balance_snapshot_f28ea94c26f4f6545df0e502061bba76cddc1bd2273071f6a1720276b3850415',
                'claim_set_id': 'claim_set_0610ef7862d55eda653f6015504959a4777c0315a19f81983d95eb3d870e73f4',
                'observation_set_id': 'observation_set_ae4910812fb2a2f9e481007dcc4a55900225114273d8e168d26775187160b9eb',
                'transaction_receipt_root': 'tx_receipt_root_6a152ff1b5bd531665daeff95ba9fa5383030d74aecdf6b38d9154b8a3418afa',
                'projection_root': 'projection_150a82a83850cf6bce644bf0f769e2b8467da50a60369e385cd41c74e1346364',
                'compatibility_receipt_id': 'compatibility_3f37ee6303bd2de2894fe5fecace000ce9df7f183e15ea03d04dbe3d85d7f994',
                'boundary_receipt_id': 'boundary_92ee06f6bdc5452c2f90709620f985ea7141901b627141b6df1d08ea7914d125'},
 'balance-conflict': {'financial_resolution_id': 'financial_resolution_953a07db0963a353a6f842d9e27ec1ebe8179f5c62dc575a7469dcec006ff563',
                      'financial_bundle_id': 'financial_bundle_e417834eda2b546169ecba938edd341c189211dc57a4191ab5f2a19f1ae8a797',
                      'balance_snapshot_id': 'balance_snapshot_366218c3fc3855a8e874e51070127eac631149d31ae3c457eadeef7b98083210',
                      'claim_set_id': 'claim_set_d8f19cb41eaaf0ff52dfbbe277a67c65c1067d5812621e35cd38d44953e96e40',
                      'observation_set_id': 'observation_set_e0317befe68327fac969f6d981cce20e61b3879ce7f1be6d4a6879a46f31af2e',
                      'transaction_receipt_root': 'tx_receipt_root_4c9c2d45f93557343867015d52a353cf94551213c41543ae23de360921cce1a4',
                      'projection_root': 'projection_c806bc38c736d8f54fa806ebc69180c88f24e61766e5d3b339614c47c398eb30',
                      'compatibility_receipt_id': 'compatibility_a72a4655c319ac08b479fa70b947e3469c063f1058eeb87fcdb6351a9e58a741',
                      'boundary_receipt_id': 'boundary_58d247ff17833bd2898f555cad989a243da43f29f0f673b3ae5211b0d0c8ff0b'},
 'multi-unit': {'financial_resolution_id': 'financial_resolution_1044b8ce1f2c1c96883421e663bb9a4712d9d836a2a89225d4695f9119efd86e',
                'financial_bundle_id': 'financial_bundle_a3a4ebc088c10eeef2bae5d82284e837038f8810fef1e682f24a91a398f99de8',
                'balance_snapshot_id': 'balance_snapshot_4755809a2c5f71b37f958967eb6e757bbea61f249ea081907686aff42bad28e6',
                'claim_set_id': 'claim_set_00da9646d7539c7b067b7c51af1ad142320d7e5eefb3f913772f3eb8a1428b69',
                'observation_set_id': 'observation_set_85fa59d846290337782087b4cb7c14ae1c891e7db36441c5b858ba8842a4b9bb',
                'transaction_receipt_root': 'tx_receipt_root_dc111c501cc06f4ed1bbb7b6ccd1af937e727db467e567a8a18171e9f18736d1',
                'projection_root': 'projection_f83e1f239f36f00f99e46143a11001bbe664f013987ba69e349cc7f3e4bbd523',
                'compatibility_receipt_id': 'compatibility_6353e463399ebd5b5dbd8beedb4ab736cc79743f982c20706ab900fe7e470d46',
                'boundary_receipt_id': 'boundary_43cb9cecdf8b1f56729c0e566f6a7c6dcf135a9ba3fc0e746bab26aa0aa07cb7'}}


def canonical_json(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":"))


def hash_text(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def make_identity(prefix, profile, value):
    return prefix + "_" + hash_text(canonical_json({"profile": profile, "value": value}))


def is_nfc(value):
    return unicodedata.normalize("NFC", value) == value


def contains_forbidden_control(value):
    return any(unicodedata.category(char) in ("Cc", "Cf", "Cs") for char in value)


def exact_field_errors(record, fields, name):
    if not isinstance(record, dict):
        return [name + ": must be an object"]
    actual = set(record)
    expected = set(fields)
    errors = []
    for field in sorted(expected - actual):
        errors.append(name + ": missing field " + field)
    for field in sorted(actual - expected):
        errors.append(name + ": unsupported field " + field)
    return errors


def identifier_errors(value, field):
    if not isinstance(value, str):
        return [field + ": must be a string"]
    errors = []
    if value == "":
        errors.append(field + ": must not be empty")
    if len(value) > MAX_IDENTIFIER_LENGTH:
        errors.append(field + ": exceeds maximum length")
    if value != value.strip():
        errors.append(field + ": leading or trailing whitespace is not allowed")
    if not is_nfc(value):
        errors.append(field + ": must be NFC-normalized")
    if contains_forbidden_control(value):
        errors.append(field + ": control, format, and surrogate characters are not allowed")
    return errors


def unit_errors(value):
    if not isinstance(value, str):
        return ["unit: must be a string"]
    if not UNIT_PATTERN.fullmatch(value):
        return ["unit: must match " + UNIT_PATTERN.pattern]
    return []


def amount_errors(value, allow_zero):
    if not isinstance(value, str):
        return ["amount_minor: must be a decimal integer string"]
    pattern = AMOUNT_ZERO_PATTERN if allow_zero else AMOUNT_POSITIVE_PATTERN
    if pattern.fullmatch(value):
        return []
    if len(value) > MAX_AMOUNT_DIGITS and value.isdigit():
        return ["amount_minor: exceeds maximum digit length"]
    if not allow_zero and value == "0":
        return ["amount_minor: zero is not supported for transaction claims"]
    return ["amount_minor: invalid canonical decimal integer string"]


def validate_balance(record):
    errors = exact_field_errors(record, ["schema", "account", "amount_minor", "unit"], "balance")
    if errors:
        return errors
    if record["schema"] != BALANCE_SCHEMA:
        errors.append("balance.schema: unsupported schema")
    errors.extend(identifier_errors(record["account"], "balance.account"))
    errors.extend(amount_errors(record["amount_minor"], True))
    errors.extend(unit_errors(record["unit"]))
    return errors


def validate_fragment(record):
    errors = exact_field_errors(record, ["schema", "tx", "side", "account", "amount_minor", "unit"], "fragment")
    if errors:
        return errors
    if record["schema"] != FRAGMENT_SCHEMA:
        errors.append("fragment.schema: unsupported schema")
    errors.extend(identifier_errors(record["tx"], "fragment.tx"))
    if record["side"] not in ("debit", "credit"):
        errors.append("fragment.side: must be debit or credit")
    errors.extend(identifier_errors(record["account"], "fragment.account"))
    errors.extend(amount_errors(record["amount_minor"], False))
    errors.extend(unit_errors(record["unit"]))
    return errors


def validate_observation(record):
    errors = exact_field_errors(record, ["schema", "observation_ref", "source", "fragment"], "observation")
    if errors:
        return errors
    if record["schema"] != OBSERVATION_SCHEMA:
        errors.append("observation.schema: unsupported schema")
    errors.extend(identifier_errors(record["observation_ref"], "observation.observation_ref"))
    errors.extend(identifier_errors(record["source"], "observation.source"))
    errors.extend(validate_fragment(record["fragment"]))
    return errors


def balance_record_identity(record):
    return make_identity("balance", BALANCE_SCHEMA, record)


def fragment_claim_identity(fragment):
    return make_identity("claim", FRAGMENT_SCHEMA, fragment)


def source_observation_identity(observation):
    basis = {
        "schema": observation["schema"],
        "observation_ref": observation["observation_ref"],
        "source": observation["source"],
        "claim_id": fragment_claim_identity(observation["fragment"]),
    }
    return make_identity("observation", OBSERVATION_SCHEMA, basis)


def reconstruct_balance_basis(records):
    if not isinstance(records, list):
        return {
            "validation_state": "REFUSED",
            "errors": ["balances: must be an array"],
        }

    errors = []
    accepted = []
    for index, record in enumerate(records):
        found = validate_balance(record)
        if found:
            errors.extend("balances[" + str(index) + "]: " + item for item in found)
        else:
            accepted.append(deepcopy(record))
    if errors:
        return {"validation_state": "REFUSED", "errors": errors}

    unique = {balance_record_identity(record): record for record in accepted}
    grouped = defaultdict(dict)
    for record_id, record in unique.items():
        grouped[(record["account"], record["unit"])][record["amount_minor"]] = record_id

    balances = []
    conflicts = []
    for account, unit in sorted(grouped):
        amount_map = grouped[(account, unit)]
        if len(amount_map) == 1:
            amount_minor = next(iter(amount_map))
            canonical_record = {
                "schema": BALANCE_SCHEMA,
                "account": account,
                "amount_minor": amount_minor,
                "unit": unit,
            }
            balances.append({
                "record_id": balance_record_identity(canonical_record),
                "account": account,
                "amount_minor": amount_minor,
                "unit": unit,
            })
        else:
            conflicts.append({
                "account": account,
                "unit": unit,
                "amount_minor_values": sorted(amount_map, key=lambda item: (len(item), item)),
                "record_ids": sorted(amount_map.values()),
            })

    state = "CONFLICT" if conflicts else "RESOLVED"
    basis = {
        "profile": BALANCE_SCHEMA,
        "state": state,
        "balances": balances,
        "conflicts": conflicts,
    }
    return {
        "validation_state": "ACCEPTED",
        "state": state,
        "raw_record_count": len(records),
        "unique_record_count": len(unique),
        "exact_duplicate_count": len(records) - len(unique),
        "balances": balances,
        "conflicts": conflicts,
        "balance_snapshot_id": make_identity("balance_snapshot", BALANCE_SCHEMA, basis),
    }


def reconstruct_evidence(observations):
    if not isinstance(observations, list):
        return {
            "validation_state": "REFUSED",
            "errors": ["observations: must be an array"],
        }

    errors = []
    accepted = []
    for index, record in enumerate(observations):
        found = validate_observation(record)
        if found:
            errors.extend("observations[" + str(index) + "]: " + item for item in found)
        else:
            accepted.append(deepcopy(record))
    if errors:
        return {"validation_state": "REFUSED", "errors": errors}

    unique_observations = {source_observation_identity(record): record for record in accepted}
    claims = {}
    claim_observations = defaultdict(list)
    claim_sources = defaultdict(set)
    for observation_id in sorted(unique_observations):
        observation = unique_observations[observation_id]
        claim_id = fragment_claim_identity(observation["fragment"])
        claims[claim_id] = deepcopy(observation["fragment"])
        claim_observations[claim_id].append(observation_id)
        claim_sources[claim_id].add(observation["source"])

    claim_records = []
    for claim_id in sorted(claims):
        claim_records.append({
            "claim_id": claim_id,
            "fragment": claims[claim_id],
            "observation_ids": sorted(claim_observations[claim_id]),
            "sources": sorted(claim_sources[claim_id]),
            "observation_count": len(claim_observations[claim_id]),
        })

    observation_records = []
    for observation_id in sorted(unique_observations):
        observation = unique_observations[observation_id]
        observation_records.append({
            "observation_id": observation_id,
            "observation_ref": observation["observation_ref"],
            "source": observation["source"],
            "claim_id": fragment_claim_identity(observation["fragment"]),
        })

    claim_set_basis = {
        "profile": FRAGMENT_SCHEMA,
        "claim_ids": sorted(claims),
    }
    observation_set_basis = {
        "profile": OBSERVATION_SCHEMA,
        "observation_ids": sorted(unique_observations),
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
        "claim_set_id": make_identity("claim_set", FRAGMENT_SCHEMA, claim_set_basis),
        "observation_set_id": make_identity("observation_set", OBSERVATION_SCHEMA, observation_set_basis),
    }


def reconstruct_transactions(claim_records):
    by_tx = defaultdict(list)
    claim_index = {}
    for claim in claim_records:
        claim_id = claim["claim_id"]
        claim_index[claim_id] = claim
        by_tx[claim["fragment"]["tx"]].append(claim_id)

    receipts = []
    for tx in sorted(by_tx):
        claim_ids = sorted(by_tx[tx])
        debits = [claim_id for claim_id in claim_ids if claim_index[claim_id]["fragment"]["side"] == "debit"]
        credits = [claim_id for claim_id in claim_ids if claim_index[claim_id]["fragment"]["side"] == "credit"]
        contributions = []

        if len(debits) > 1 and len(credits) > 1:
            state = "ABSTAIN"
            reason = "MULTIPLE_DEBIT_AND_CREDIT_CLAIMS"
            witness = {"conflicting_claim_ids": sorted(debits + credits)}
        elif len(debits) > 1:
            state = "ABSTAIN"
            reason = "MULTIPLE_DEBIT_CLAIMS"
            witness = {"conflicting_claim_ids": sorted(debits), "credit_claim_ids": sorted(credits)}
        elif len(credits) > 1:
            state = "ABSTAIN"
            reason = "MULTIPLE_CREDIT_CLAIMS"
            witness = {"debit_claim_ids": sorted(debits), "conflicting_claim_ids": sorted(credits)}
        elif not debits:
            state = "INCOMPLETE"
            reason = "MISSING_DEBIT_CLAIM"
            witness = {"present_claim_ids": sorted(credits), "missing_requirement": "ONE_COMPATIBLE_DEBIT_CLAIM"}
        elif not credits:
            state = "INCOMPLETE"
            reason = "MISSING_CREDIT_CLAIM"
            witness = {"present_claim_ids": sorted(debits), "missing_requirement": "ONE_COMPATIBLE_CREDIT_CLAIM"}
        else:
            debit = claim_index[debits[0]]["fragment"]
            credit = claim_index[credits[0]]["fragment"]
            if debit["unit"] != credit["unit"]:
                state = "ABSTAIN"
                reason = "UNIT_MISMATCH"
                witness = {
                    "debit_claim_id": debits[0],
                    "credit_claim_id": credits[0],
                    "debit_unit": debit["unit"],
                    "credit_unit": credit["unit"],
                }
            elif debit["amount_minor"] != credit["amount_minor"]:
                state = "ABSTAIN"
                reason = "AMOUNT_MISMATCH"
                witness = {
                    "debit_claim_id": debits[0],
                    "credit_claim_id": credits[0],
                    "debit_amount_minor": debit["amount_minor"],
                    "credit_amount_minor": credit["amount_minor"],
                    "unit": debit["unit"],
                }
            else:
                state = "RESOLVED"
                reason = "MATCHED_DEBIT_CREDIT_PAIR"
                witness = {"debit_claim_id": debits[0], "credit_claim_id": credits[0]}
                contributions = [
                    {"account": debit["account"], "delta_minor": "-" + debit["amount_minor"], "side": "debit", "unit": debit["unit"]},
                    {"account": credit["account"], "delta_minor": credit["amount_minor"], "side": "credit", "unit": credit["unit"]},
                ]

        evidence_basis = {"tx": tx, "claim_ids": claim_ids}
        receipt = {
            "profile": TRANSACTION_RECEIPT_PROFILE,
            "ruleset_profile": RULESET_PROFILE,
            "tx": tx,
            "transaction_evidence_id": make_identity("tx_evidence", RULESET_PROFILE, evidence_basis),
            "claim_ids": claim_ids,
            "state": state,
            "reason_code": reason,
            "witness": witness,
            "contributions": contributions,
        }
        receipt["transaction_receipt_id"] = make_identity("tx_receipt", TRANSACTION_RECEIPT_PROFILE, receipt)
        receipts.append(receipt)

    counts = Counter(receipt["state"] for receipt in receipts)
    root_basis = {
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
        "transaction_receipt_root": make_identity("tx_receipt_root", TRANSACTION_RECEIPT_PROFILE, root_basis),
    }


def snapshot_balance_map(snapshot):
    return {(record["account"], record["unit"]): int(record["amount_minor"]) for record in snapshot.get("balances", [])}


def signed_decimal(value):
    return str(int(value))


def reconstruct_projection(balance_basis, transaction_receipts):
    if balance_basis["state"] != "RESOLVED":
        basis = {
            "profile": PROJECTION_PROFILE,
            "state": "UNAVAILABLE",
            "reason_code": "BALANCE_BASIS_CONFLICT",
            "balance_snapshot_id": balance_basis["balance_snapshot_id"],
        }
        return {
            "profile": PROJECTION_PROFILE,
            "state": "UNAVAILABLE",
            "reason_code": "BALANCE_BASIS_CONFLICT",
            "account_receipts": [],
            "unit_receipts": [],
            "projection_root": make_identity("projection", PROJECTION_PROFILE, basis),
        }

    initial = snapshot_balance_map(balance_basis)
    by_key = defaultdict(list)
    affected = set(initial)
    for receipt in transaction_receipts:
        if receipt["state"] != "RESOLVED":
            continue
        for contribution in receipt["contributions"]:
            key = (contribution["account"], contribution["unit"])
            affected.add(key)
            by_key[key].append({
                "transaction_receipt_id": receipt["transaction_receipt_id"],
                "tx": receipt["tx"],
                "delta_minor": contribution["delta_minor"],
            })

    account_receipts = []
    for account, unit in sorted(affected):
        start = initial.get((account, unit), 0)
        contributions = sorted(by_key.get((account, unit), []), key=lambda item: (item["tx"], item["transaction_receipt_id"], item["delta_minor"]))
        delta = sum(int(item["delta_minor"]) for item in contributions)
        receipt_basis = {
            "profile": PROJECTION_PROFILE,
            "account": account,
            "unit": unit,
            "initial_amount_minor": signed_decimal(start),
            "contributions": contributions,
            "net_delta_minor": signed_decimal(delta),
            "final_amount_minor": signed_decimal(start + delta),
        }
        receipt = dict(receipt_basis)
        receipt["account_projection_id"] = make_identity("account_projection", PROJECTION_PROFILE, receipt_basis)
        account_receipts.append(receipt)

    unit_receipts = []
    for unit in sorted({receipt["unit"] for receipt in account_receipts}):
        accounts = [receipt for receipt in account_receipts if receipt["unit"] == unit]
        initial_total = sum(int(receipt["initial_amount_minor"]) for receipt in accounts)
        final_total = sum(int(receipt["final_amount_minor"]) for receipt in accounts)
        net_delta = sum(int(receipt["net_delta_minor"]) for receipt in accounts)
        basis = {
            "profile": PROJECTION_PROFILE,
            "unit": unit,
            "account_projection_ids": sorted(receipt["account_projection_id"] for receipt in accounts),
            "initial_total_minor": signed_decimal(initial_total),
            "net_delta_minor": signed_decimal(net_delta),
            "final_total_minor": signed_decimal(final_total),
            "conservation_ok": initial_total == final_total and net_delta == 0,
        }
        receipt = dict(basis)
        receipt["unit_projection_id"] = make_identity("unit_projection", PROJECTION_PROFILE, basis)
        unit_receipts.append(receipt)

    basis = {
        "profile": PROJECTION_PROFILE,
        "state": "AVAILABLE",
        "balance_snapshot_id": balance_basis["balance_snapshot_id"],
        "account_projection_ids": sorted(receipt["account_projection_id"] for receipt in account_receipts),
        "unit_projection_ids": sorted(receipt["unit_projection_id"] for receipt in unit_receipts),
    }
    return {
        "profile": PROJECTION_PROFILE,
        "state": "AVAILABLE",
        "account_receipts": account_receipts,
        "unit_receipts": unit_receipts,
        "projection_root": make_identity("projection", PROJECTION_PROFILE, basis),
    }


def reconstruct_compatibility(balance_basis, transaction_receipts):
    initial = snapshot_balance_map(balance_basis) if balance_basis["state"] == "RESOLVED" else {}
    outgoing = defaultdict(list)
    for receipt in transaction_receipts:
        if receipt["state"] != "RESOLVED":
            continue
        for contribution in receipt["contributions"]:
            if contribution["side"] == "debit":
                outgoing[(contribution["account"], contribution["unit"])].append({
                    "transaction_receipt_id": receipt["transaction_receipt_id"],
                    "tx": receipt["tx"],
                    "amount_minor": contribution["delta_minor"][1:],
                })

    assessments = []
    if balance_basis["state"] == "CONFLICT":
        state = "CONFLICT"
        for conflict in balance_basis["conflicts"]:
            assessments.append({
                "account": conflict["account"],
                "unit": conflict["unit"],
                "state": "CONFLICT",
                "reason_code": "AMBIGUOUS_DECLARED_BALANCE_BASIS",
                "amount_minor_values": conflict["amount_minor_values"],
            })
    else:
        for account, unit in sorted(outgoing):
            entries = sorted(outgoing[(account, unit)], key=lambda item: (item["tx"], item["transaction_receipt_id"]))
            gross = sum(int(item["amount_minor"]) for item in entries)
            key = (account, unit)
            if key not in initial:
                assessments.append({
                    "account": account,
                    "unit": unit,
                    "state": "UNASSESSED",
                    "reason_code": "NO_DECLARED_BALANCE_BASIS",
                    "resolved_gross_outflow_minor": signed_decimal(gross),
                    "contributing_transactions": entries,
                })
            else:
                declared = initial[key]
                remaining = declared - gross
                if gross > declared:
                    item_state = "CONFLICT"
                    reason = "RESOLVED_GROSS_OUTFLOW_EXCEEDS_DECLARED_BALANCE_BASIS"
                else:
                    item_state = "COMPATIBLE"
                    reason = "RESOLVED_GROSS_OUTFLOW_WITHIN_DECLARED_BALANCE_BASIS"
                assessments.append({
                    "account": account,
                    "unit": unit,
                    "state": item_state,
                    "reason_code": reason,
                    "declared_balance_minor": signed_decimal(declared),
                    "resolved_gross_outflow_minor": signed_decimal(gross),
                    "remaining_declared_basis_minor": signed_decimal(remaining),
                    "deficit_minor": signed_decimal(max(0, -remaining)),
                    "contributing_transactions": entries,
                })
        states = [item["state"] for item in assessments]
        if "CONFLICT" in states:
            state = "CONFLICT"
        elif "UNASSESSED" in states:
            state = "UNASSESSED"
        else:
            state = "COMPATIBLE"

    basis = {
        "profile": COMPATIBILITY_PROFILE,
        "rule": "resolved_gross_outflow <= declared_initial_balance",
        "balance_snapshot_id": balance_basis["balance_snapshot_id"],
        "state": state,
        "assessments": assessments,
    }
    receipt = dict(basis)
    receipt["compatibility_receipt_id"] = make_identity("compatibility", COMPATIBILITY_PROFILE, basis)
    return receipt


def reconstruct_boundary(state, claim_set_id):
    if state not in ("OPEN", "SEALED"):
        raise ValueError("boundary_state must be OPEN or SEALED")
    basis = {
        "profile": BOUNDARY_PROFILE,
        "state": state,
        "observed_claim_set_id": claim_set_id,
        "declared_sealed_claim_set_id": claim_set_id if state == "SEALED" else None,
    }
    receipt = dict(basis)
    receipt["boundary_receipt_id"] = make_identity("boundary", BOUNDARY_PROFILE, basis)
    return receipt


def reconstruct_bundle(balance_records, observations, boundary_state):
    if boundary_state not in ("OPEN", "SEALED"):
        refusal = {
            "profile": BUNDLE_PROFILE,
            "version": VERSION,
            "result": "REFUSED",
            "architecture_profile": ARCHITECTURE_PROFILE,
            "ruleset_profile": RULESET_PROFILE,
            "errors": ["boundary_state must be OPEN or SEALED"],
        }
        refusal["refusal_id"] = make_identity("refusal", BUNDLE_PROFILE, refusal)
        return refusal

    balance_basis = reconstruct_balance_basis(balance_records)
    evidence = reconstruct_evidence(observations)
    errors = []
    if balance_basis["validation_state"] == "REFUSED":
        errors.extend(balance_basis["errors"])
    if evidence["validation_state"] == "REFUSED":
        errors.extend(evidence["errors"])
    if errors:
        refusal = {
            "profile": BUNDLE_PROFILE,
            "version": VERSION,
            "result": "REFUSED",
            "architecture_profile": ARCHITECTURE_PROFILE,
            "ruleset_profile": RULESET_PROFILE,
            "errors": errors,
        }
        refusal["refusal_id"] = make_identity("refusal", BUNDLE_PROFILE, refusal)
        return refusal

    transactions = reconstruct_transactions(evidence["claims"])
    projection = reconstruct_projection(balance_basis, transactions["receipts"])
    compatibility = reconstruct_compatibility(balance_basis, transactions["receipts"])
    boundary = reconstruct_boundary(boundary_state, evidence["claim_set_id"])
    counts = transactions["state_counts"]
    maturity = {
        "accepted_claims": evidence["unique_claim_count"],
        "unique_observations": evidence["unique_observation_count"],
        "observation_multiplicity": evidence["observation_multiplicity_count"],
        "resolved_transactions": counts["RESOLVED"],
        "incomplete_transactions": counts["INCOMPLETE"],
        "abstain_transactions": counts["ABSTAIN"],
        "boundary_state": boundary["state"],
    }

    resolution_basis = {
        "profile": BUNDLE_PROFILE,
        "version": VERSION,
        "architecture_profile": ARCHITECTURE_PROFILE,
        "ruleset_profile": RULESET_PROFILE,
        "compatibility_profile": COMPATIBILITY_PROFILE,
        "balance_snapshot_id": balance_basis["balance_snapshot_id"],
        "claim_set_id": evidence["claim_set_id"],
        "transaction_receipt_root": transactions["transaction_receipt_root"],
        "projection_root": projection["projection_root"],
        "compatibility_receipt_id": compatibility["compatibility_receipt_id"],
        "boundary_receipt_id": boundary["boundary_receipt_id"],
    }
    financial_resolution_id = make_identity(
        "financial_resolution",
        BUNDLE_PROFILE,
        resolution_basis,
    )
    bundle_basis = {
        "profile": BUNDLE_PROFILE,
        "financial_resolution_id": financial_resolution_id,
        "observation_set_id": evidence["observation_set_id"],
    }
    financial_bundle_id = make_identity(
        "financial_bundle",
        BUNDLE_PROFILE,
        bundle_basis,
    )

    return {
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
        "balance_basis": balance_basis,
        "evidence": evidence,
        "transactions": transactions,
        "structural_projection": projection,
        "declared_balance_compatibility": compatibility,
        "boundary": boundary,
        "evidence_maturity": maturity,
        "financial_resolution_id": financial_resolution_id,
        "financial_bundle_id": financial_bundle_id,
    }


def make_verification_result(
    valid=False,
    errors=None,
    failure_stage=None,
    reason_code=None,
    independent_reconstruction=False,
    producer_self_verification_present=False,
    producer_self_verification_valid=None,
    supplied_financial_resolution_id=None,
    reconstructed_financial_resolution_id=None,
    supplied_financial_bundle_id=None,
    reconstructed_financial_bundle_id=None,
):
    return {
        "profile": INDEPENDENT_VERIFICATION_PROFILE,
        "version": VERSION,
        "valid": bool(valid),
        "status": "PASS" if valid else "FAIL",
        "errors": list(errors or []),
        "failure_stage": failure_stage,
        "reason_code": reason_code,
        "independent_reconstruction": bool(independent_reconstruction),
        "producer_import_used": False,
        "producer_self_verification_present": bool(producer_self_verification_present),
        "producer_self_verification_valid": producer_self_verification_valid,
        "supplied_financial_resolution_id": supplied_financial_resolution_id,
        "reconstructed_financial_resolution_id": reconstructed_financial_resolution_id,
        "supplied_financial_bundle_id": supplied_financial_bundle_id,
        "reconstructed_financial_bundle_id": reconstructed_financial_bundle_id,
    }


def bundle_without_producer_self_verification(bundle):
    result = deepcopy(bundle)
    result.pop("self_verification", None)
    return result


def compare_bundle(bundle):
    try:
        return _compare_bundle(bundle)
    except Exception as exc:
        return make_verification_result(
            valid=False,
            errors=["unexpected verifier error: " + type(exc).__name__ + ": " + str(exc)],
            failure_stage="INTERNAL",
            reason_code="UNEXPECTED_VERIFIER_ERROR",
        )


def _compare_bundle(bundle):
    if not isinstance(bundle, dict):
        return make_verification_result(
            valid=False,
            errors=["bundle must be an object"],
            failure_stage="INTAKE",
            reason_code="NON_OBJECT_ROOT",
        )

    producer_self_verification = bundle.get("self_verification")
    producer_self_verification_present = isinstance(producer_self_verification, dict)
    producer_self_verification_valid = (
        producer_self_verification.get("valid")
        if producer_self_verification_present
        else None
    )
    common = {
        "producer_self_verification_present": producer_self_verification_present,
        "producer_self_verification_valid": producer_self_verification_valid,
        "supplied_financial_resolution_id": bundle.get("financial_resolution_id"),
        "supplied_financial_bundle_id": bundle.get("financial_bundle_id"),
    }

    if bundle.get("result") != "ACCEPTED":
        return make_verification_result(
            valid=False,
            errors=["only ACCEPTED bundles can be reconstructed by this verifier"],
            failure_stage="INTAKE",
            reason_code="UNSUPPORTED_BUNDLE_RESULT",
            **common,
        )

    inputs = bundle.get("inputs")
    if not isinstance(inputs, dict):
        return make_verification_result(
            valid=False,
            errors=["missing inputs"],
            failure_stage="INTAKE",
            reason_code="MISSING_INPUTS",
            **common,
        )

    if "balances" not in inputs or "observations" not in inputs or "boundary_state" not in inputs:
        return make_verification_result(
            valid=False,
            errors=["inputs must contain balances, observations, and boundary_state"],
            failure_stage="INTAKE",
            reason_code="INCOMPLETE_INPUTS",
            **common,
        )

    reconstructed = reconstruct_bundle(
        inputs["balances"],
        inputs["observations"],
        inputs["boundary_state"],
    )
    reconstructed_resolution_id = reconstructed.get("financial_resolution_id")
    reconstructed_bundle_id = reconstructed.get("financial_bundle_id")

    if reconstructed.get("result") != "ACCEPTED":
        return make_verification_result(
            valid=False,
            errors=["embedded inputs do not reconstruct an ACCEPTED bundle"]
            + list(reconstructed.get("errors", [])),
            failure_stage="RECONSTRUCTION",
            reason_code="EMBEDDED_INPUTS_REFUSED",
            independent_reconstruction=False,
            reconstructed_financial_resolution_id=reconstructed_resolution_id,
            reconstructed_financial_bundle_id=reconstructed_bundle_id,
            **common,
        )

    errors = []
    supplied_core = bundle_without_producer_self_verification(bundle)
    if canonical_json(supplied_core) != canonical_json(reconstructed):
        checks = [
            (None, "financial_resolution_id"),
            (None, "financial_bundle_id"),
            ("balance_basis", "balance_snapshot_id"),
            ("evidence", "claim_set_id"),
            ("evidence", "observation_set_id"),
            ("transactions", "transaction_receipt_root"),
            ("structural_projection", "projection_root"),
            ("declared_balance_compatibility", "compatibility_receipt_id"),
            ("boundary", "boundary_receipt_id"),
        ]
        for section, field in checks:
            supplied = (
                bundle.get(field)
                if section is None
                else (bundle.get(section) or {}).get(field)
            )
            expected = (
                reconstructed.get(field)
                if section is None
                else (reconstructed.get(section) or {}).get(field)
            )
            label = field if section is None else section + "." + field
            if supplied != expected:
                errors.append(label + " mismatch")
        if not errors:
            errors.append("bundle content mismatch")

    return make_verification_result(
        valid=not errors,
        errors=errors,
        failure_stage=None if not errors else "COMPARE",
        reason_code="VERIFIED" if not errors else "BUNDLE_MISMATCH",
        independent_reconstruction=True,
        reconstructed_financial_resolution_id=reconstructed_resolution_id,
        reconstructed_financial_bundle_id=reconstructed_bundle_id,
        **common,
    )


def make_balance(account, amount_minor, unit="UNIT"):
    return {"schema": BALANCE_SCHEMA, "account": account, "amount_minor": str(amount_minor), "unit": unit}


def make_fragment(tx, side, account, amount_minor, unit="UNIT"):
    return {"schema": FRAGMENT_SCHEMA, "tx": tx, "side": side, "account": account, "amount_minor": str(amount_minor), "unit": unit}


def make_observation(source, observation_ref, fragment):
    return {"schema": OBSERVATION_SCHEMA, "observation_ref": observation_ref, "source": source, "fragment": deepcopy(fragment)}


def merge_observations(*sets):
    merged = {}
    for observations in sets:
        for observation in observations:
            if validate_observation(observation):
                raise ValueError("cannot merge invalid observation")
            merged[source_observation_identity(observation)] = deepcopy(observation)
    return [merged[key] for key in sorted(merged)]


def self_test_scenarios():
    two_a = [
        make_observation("Node-A", "A-001", make_fragment("M100", "debit", "VillageA", "500")),
        make_observation("Node-A", "A-002", make_fragment("M300", "debit", "VillageA", "120")),
        make_observation("Node-A", "A-003", make_fragment("M400", "debit", "VillageA", "400")),
        make_observation("Node-A", "A-004", make_fragment("M500", "debit", "VillageA", "250")),
    ]
    two_b = [
        make_observation("Node-B", "B-001", make_fragment("M100", "credit", "VillageB", "500")),
        make_observation("Node-B", "B-002", make_fragment("M100", "credit", "VillageB", "500")),
        make_observation("Node-B", "B-003", make_fragment("M200", "credit", "VillageB", "300")),
        make_observation("Node-B", "B-004", make_fragment("M400", "credit", "VillageB", "450")),
        make_observation("Node-B", "B-005", make_fragment("M500", "credit", "VillageB", "250")),
        make_observation("Node-B", "B-006", make_fragment("M500", "credit", "VillageB_Alt", "250")),
    ]
    three_a = [
        make_observation("Node-A", "A-001", make_fragment("M100", "debit", "VillageA", "500")),
        make_observation("Node-A", "A-002", make_fragment("M300", "credit", "VillageA", "150")),
        make_observation("Node-A", "A-003", make_fragment("M400", "debit", "VillageA", "300")),
        make_observation("Node-A", "A-004", make_fragment("M500", "credit", "VillageA", "250")),
    ]
    three_b = [
        make_observation("Node-B", "B-001", make_fragment("M100", "credit", "VillageB", "500")),
        make_observation("Node-B", "B-002", make_fragment("M200", "debit", "VillageB", "200")),
        make_observation("Node-B", "B-003", make_fragment("M500", "debit", "VillageB", "250")),
        make_observation("Node-B", "B-004", make_fragment("M500", "debit", "VillageB_conflict", "250")),
    ]
    three_c = [
        make_observation("Node-C", "C-001", make_fragment("M200", "credit", "VillageC", "200")),
        make_observation("Node-C", "C-002", make_fragment("M300", "debit", "VillageC", "150")),
        make_observation("Node-C", "C-003", make_fragment("M400", "credit", "VillageC", "350")),
    ]
    balance_conflict = [
        make_observation("Node-1", "O-001", make_fragment("T1", "debit", "A", "80", "USD")),
        make_observation("Node-2", "O-002", make_fragment("T1", "credit", "B", "80", "USD")),
        make_observation("Node-1", "O-003", make_fragment("T2", "debit", "A", "60", "USD")),
        make_observation("Node-3", "O-004", make_fragment("T2", "credit", "C", "60", "USD")),
    ]
    multi = [
        make_observation("Node-A", "U-001", make_fragment("USD-1", "debit", "A", "200", "USD")),
        make_observation("Node-B", "U-002", make_fragment("USD-1", "credit", "B", "200", "USD")),
        make_observation("Node-A", "U-003", make_fragment("EUR-1", "debit", "A", "50", "EUR")),
        make_observation("Node-C", "U-004", make_fragment("EUR-1", "credit", "C", "50", "EUR")),
    ]
    return {
        "two-node": (
            [make_balance("VillageA", "1000"), make_balance("VillageB", "1000")],
            merge_observations(two_a, two_b),
            "OPEN",
        ),
        "three-node": (
            [make_balance("VillageA", "1000"), make_balance("VillageB", "1000"), make_balance("VillageC", "1000")],
            merge_observations(three_a, three_b, three_c),
            "OPEN",
        ),
        "balance-conflict": (
            [make_balance("A", "100", "USD"), make_balance("B", "0", "USD"), make_balance("C", "0", "USD")],
            balance_conflict,
            "OPEN",
        ),
        "multi-unit": (
            [make_balance("A", "1000", "USD"), make_balance("B", "0", "USD"), make_balance("A", "500", "EUR"), make_balance("C", "0", "EUR")],
            multi,
            "SEALED",
        ),
    }


class SelfTest:
    def __init__(self):
        self.passed = 0
        self.total = 0
        self.failures = []

    def check(self, name, condition):
        self.total += 1
        if condition:
            self.passed += 1
        else:
            self.failures.append(name)


def run_self_test(json_output=False):
    test = SelfTest()
    scenarios = self_test_scenarios()
    bundles = {}
    fields = [
        (None, "financial_resolution_id"),
        (None, "financial_bundle_id"),
        ("balance_basis", "balance_snapshot_id"),
        ("evidence", "claim_set_id"),
        ("evidence", "observation_set_id"),
        ("transactions", "transaction_receipt_root"),
        ("structural_projection", "projection_root"),
        ("declared_balance_compatibility", "compatibility_receipt_id"),
        ("boundary", "boundary_receipt_id"),
    ]

    for name, (balances, observations, boundary) in scenarios.items():
        bundle = reconstruct_bundle(balances, observations, boundary)
        bundles[name] = bundle
        test.check(name + " accepted", bundle.get("result") == "ACCEPTED")
        expected = FROZEN_REFERENCE_IDS[name]
        for section, field in fields:
            actual = bundle.get(field) if section is None else bundle.get(section, {}).get(field)
            test.check(name + " " + field, actual == expected[field])

    two = bundles["two-node"]
    states = {receipt["tx"]: receipt["state"] for receipt in two["transactions"]["receipts"]}
    test.check("two-node M100 resolved", states.get("M100") == "RESOLVED")
    test.check("two-node M200 incomplete", states.get("M200") == "INCOMPLETE")
    test.check("two-node M300 incomplete", states.get("M300") == "INCOMPLETE")
    test.check("two-node M400 abstain", states.get("M400") == "ABSTAIN")
    test.check("two-node M500 abstain", states.get("M500") == "ABSTAIN")
    test.check("two-node 10 observations", two["evidence"]["unique_observation_count"] == 10)
    test.check("two-node 9 claims", two["evidence"]["unique_claim_count"] == 9)
    test.check("two-node multiplicity 1", two["evidence"]["observation_multiplicity_count"] == 1)
    test.check("two-node compatible", two["declared_balance_compatibility"]["state"] == "COMPATIBLE")

    conflict = bundles["balance-conflict"]
    conflict_states = {receipt["tx"]: receipt["state"] for receipt in conflict["transactions"]["receipts"]}
    test.check("balance conflict T1 resolved", conflict_states.get("T1") == "RESOLVED")
    test.check("balance conflict T2 resolved", conflict_states.get("T2") == "RESOLVED")
    test.check("balance compatibility conflict", conflict["declared_balance_compatibility"]["state"] == "CONFLICT")
    assessment = conflict["declared_balance_compatibility"]["assessments"][0]
    test.check("balance conflict deficit 40", assessment.get("deficit_minor") == "40")

    multi = bundles["multi-unit"]
    conservation = {item["unit"]: item["conservation_ok"] for item in multi["structural_projection"]["unit_receipts"]}
    test.check("USD conserved", conservation.get("USD") is True)
    test.check("EUR conserved", conservation.get("EUR") is True)
    test.check("multi boundary sealed", multi["boundary"]["state"] == "SEALED")

    duplicate_observations = list(scenarios["two-node"][1]) + [deepcopy(scenarios["two-node"][1][0])]
    duplicate_bundle = reconstruct_bundle(scenarios["two-node"][0], duplicate_observations, "OPEN")
    test.check("exact observation duplicate bundle stable", duplicate_bundle["financial_bundle_id"] == two["financial_bundle_id"])

    altered = deepcopy(scenarios["two-node"][1])
    altered[0]["source"] = "Node-X"
    altered_bundle = reconstruct_bundle(scenarios["two-node"][0], altered, "OPEN")
    test.check("origin change resolution stable", altered_bundle["financial_resolution_id"] == two["financial_resolution_id"])
    test.check("origin change provenance bundle changes", altered_bundle["financial_bundle_id"] != two["financial_bundle_id"])

    supplied = deepcopy(two)
    supplied["self_verification"] = {
        "profile": PRODUCER_VERIFICATION_PROFILE,
        "valid": True,
        "errors": [],
    }
    verify_result = compare_bundle(supplied)
    test.check("independent reconstruction accepts valid bundle", verify_result["valid"] is True)
    test.check("independent verifier uses no producer import", verify_result["producer_import_used"] is False)

    tampered = deepcopy(supplied)
    tampered["financial_bundle_id"] = "financial_bundle_tampered"
    test.check("tampered bundle id rejected", compare_bundle(tampered)["valid"] is False)

    tampered = deepcopy(supplied)
    tampered["transactions"]["receipts"][0]["state"] = "ABSTAIN"
    test.check("tampered transaction state rejected", compare_bundle(tampered)["valid"] is False)

    tampered = deepcopy(supplied)
    tampered["structural_projection"]["account_receipts"][0]["final_amount_minor"] = "999999"
    test.check("tampered projection rejected", compare_bundle(tampered)["valid"] is False)

    malformed = deepcopy(scenarios["two-node"][1])
    malformed[0]["fragment"]["amount_minor"] = "01"
    test.check("malformed amount refused", reconstruct_bundle(scenarios["two-node"][0], malformed, "OPEN")["result"] == "REFUSED")
    test.check("invalid boundary refused", reconstruct_bundle(scenarios["two-node"][0], scenarios["two-node"][1], "FINAL")["result"] == "REFUSED")

    high_surrogate = reconstruct_bundle(
        [make_balance("A" + chr(0xD800), "10", "USD")],
        [],
        "OPEN",
    )
    test.check("lone high surrogate refused", high_surrogate.get("result") == "REFUSED")

    low_surrogate = reconstruct_bundle(
        [make_balance("A" + chr(0xDFFF), "10", "USD")],
        [],
        "OPEN",
    )
    test.check("lone low surrogate refused", low_surrogate.get("result") == "REFUSED")

    astral = make_fragment("T😀", "debit", "A", "1", "USD")
    test.check("valid astral identifier accepted", validate_fragment(astral) == [])

    test.check(
        "non-array balances refused",
        reconstruct_bundle({}, [], "OPEN").get("result") == "REFUSED",
    )
    test.check(
        "non-array observations refused",
        reconstruct_bundle([], {}, "OPEN").get("result") == "REFUSED",
    )

    schema_keys = set(make_verification_result().keys())
    early_results = [
        compare_bundle([]),
        compare_bundle({}),
        compare_bundle({"result": "REFUSED"}),
        compare_bundle({"result": "ACCEPTED"}),
    ]
    test.check(
        "non-object verification uses complete schema",
        set(early_results[0].keys()) == schema_keys,
    )
    test.check(
        "empty object verification uses complete schema",
        set(early_results[1].keys()) == schema_keys,
    )
    test.check(
        "REFUSED bundle verification uses complete schema",
        set(early_results[2].keys()) == schema_keys,
    )
    test.check(
        "missing inputs verification uses complete schema",
        set(early_results[3].keys()) == schema_keys,
    )
    test.check(
        "valid verification uses complete schema",
        set(verify_result.keys()) == schema_keys,
    )
    test.check(
        "tampered verification uses complete schema",
        set(compare_bundle(tampered).keys()) == schema_keys,
    )

    with TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)

        duplicate_path = temp_root / "duplicate.json"
        duplicate_path.write_text(
            '{"result":"ACCEPTED","result":"REFUSED"}',
            encoding="utf-8",
        )
        try:
            read_bundle(duplicate_path)
            duplicate_refused = False
        except VerificationInputError as exc:
            duplicate_refused = exc.reason_code == "DUPLICATE_JSON_KEY"
        test.check("duplicate JSON key refused", duplicate_refused)

        invalid_utf8_path = temp_root / "invalid_utf8.json"
        invalid_utf8_path.write_bytes(b"\xff\xfe")
        try:
            read_bundle(invalid_utf8_path)
            invalid_utf8_refused = False
        except VerificationInputError as exc:
            invalid_utf8_refused = exc.reason_code == "INVALID_UTF8"
        test.check("invalid UTF-8 refused", invalid_utf8_refused)

        truncated_path = temp_root / "truncated.json"
        truncated_path.write_text('{"result":', encoding="utf-8")
        try:
            read_bundle(truncated_path)
            truncated_refused = False
        except VerificationInputError as exc:
            truncated_refused = exc.reason_code == "INVALID_JSON"
        test.check("truncated JSON refused", truncated_refused)

        canonical_path = temp_root / "canonical.json"
        canonical_path.write_bytes(canonical_json(supplied).encode("utf-8"))
        try:
            strict_value = read_bundle(canonical_path, strict_canonical=True)
            strict_accepts = strict_value.get("result") == "ACCEPTED"
        except VerificationInputError:
            strict_accepts = False
        test.check("strict canonical bytes accepted", strict_accepts)

        pretty_path = temp_root / "pretty.json"
        pretty_path.write_text(
            json.dumps(supplied, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        try:
            read_bundle(pretty_path, strict_canonical=True)
            strict_rejects_pretty = False
        except VerificationInputError as exc:
            strict_rejects_pretty = exc.reason_code == "NON_CANONICAL_JSON_BYTES"
        test.check("strict canonical mode rejects presentation variants", strict_rejects_pretty)

        corpus_root = temp_root / "corpus"
        corpus_root.mkdir()
        entries = []
        for scenario_name, (balances, observations, boundary) in scenarios.items():
            corpus_bundle = reconstruct_bundle(balances, observations, boundary)
            filename = "ORL_Money_" + scenario_name.replace("-", "_") + "_bundle_v2_1_0.json"
            bundle_path = corpus_root / filename
            bundle_bytes = canonical_json(corpus_bundle).encode("utf-8")
            bundle_path.write_bytes(bundle_bytes)
            entries.append({
                "balance_snapshot_id": corpus_bundle["balance_basis"]["balance_snapshot_id"],
                "boundary_receipt_id": corpus_bundle["boundary"]["boundary_receipt_id"],
                "boundary_state": corpus_bundle["boundary"]["state"],
                "claim_set_id": corpus_bundle["evidence"]["claim_set_id"],
                "compatibility_receipt_id": corpus_bundle["declared_balance_compatibility"]["compatibility_receipt_id"],
                "filename": filename,
                "financial_bundle_id": corpus_bundle["financial_bundle_id"],
                "financial_resolution_id": corpus_bundle["financial_resolution_id"],
                "independent_verification": "PASS",
                "observation_set_id": corpus_bundle["evidence"]["observation_set_id"],
                "projection_root": corpus_bundle["structural_projection"]["projection_root"],
                "result": "ACCEPTED",
                "scenario": scenario_name,
                "sha256": hashlib.sha256(bundle_bytes).hexdigest(),
                "transaction_receipt_root": corpus_bundle["transactions"]["transaction_receipt_root"],
            })

        manifest = {
            "architecture_profile": ARCHITECTURE_PROFILE,
            "compatibility_profile": COMPATIBILITY_PROFILE,
            "corpus_profile": CORPUS_PROFILE,
            "profile": CORPUS_MANIFEST_PROFILE,
            "ruleset_profile": RULESET_PROFILE,
            "scenario_count": len(entries),
            "scenarios": entries,
        }
        manifest["manifest_id"] = "corpus_manifest_" + hash_text(canonical_json(manifest))
        manifest_path = corpus_root / "ORL_Money_Frozen_Corpus_Manifest_v2_1_0.json"
        manifest_path.write_bytes(canonical_json(manifest).encode("utf-8"))

        corpus_result = verify_corpus_manifest(manifest_path, strict_canonical=True)
        test.check("corpus mode verifies generated manifest", corpus_result["valid"] is True)
        test.check("corpus mode reports four of four", corpus_result["passed"] == 4 and corpus_result["total"] == 4)

        entries[0]["sha256"] = "0" * 64
        bad_manifest = {
            "architecture_profile": ARCHITECTURE_PROFILE,
            "compatibility_profile": COMPATIBILITY_PROFILE,
            "corpus_profile": CORPUS_PROFILE,
            "profile": CORPUS_MANIFEST_PROFILE,
            "ruleset_profile": RULESET_PROFILE,
            "scenario_count": len(entries),
            "scenarios": entries,
        }
        bad_manifest["manifest_id"] = "corpus_manifest_" + hash_text(canonical_json(bad_manifest))
        bad_manifest_path = corpus_root / "bad_manifest.json"
        bad_manifest_path.write_bytes(canonical_json(bad_manifest).encode("utf-8"))
        bad_corpus_result = verify_corpus_manifest(bad_manifest_path, strict_canonical=True)
        test.check("corpus mode rejects hash mismatch", bad_corpus_result["valid"] is False)

    result = {
        "profile": SELF_TEST_PROFILE,
        "version": VERSION,
        "passed": test.passed,
        "total": test.total,
        "pass": test.passed == test.total,
        "failures": test.failures,
    }
    if json_output:
        print(canonical_json(result))
    else:
        print("ORL-Money Independent Verifier Self-Test | " + SELF_TEST_PROFILE)
        print("=" * 96)
        print("TOTAL " + str(test.passed) + "/" + str(test.total) + " " + ("PASS" if result["pass"] else "FAIL"))
        if test.failures:
            print("-" * 96)
            for failure in test.failures:
                print("FAIL " + failure)
    return result["pass"]


class VerificationInputError(ValueError):
    def __init__(self, message, failure_stage, reason_code):
        super().__init__(message)
        self.failure_stage = failure_stage
        self.reason_code = reason_code


class DuplicateKeyError(ValueError):
    pass


def reject_duplicate_object_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError("duplicate JSON key: " + str(key))
        result[key] = value
    return result


def reject_nonstandard_constant(value):
    raise ValueError("non-standard JSON numeric constant: " + str(value))


def read_json_document(path, strict_canonical=False, label="JSON document"):
    document_path = Path(path)
    try:
        raw = document_path.read_bytes()
    except FileNotFoundError:
        raise VerificationInputError(
            label + " file not found: " + str(path),
            "READ",
            "FILE_NOT_FOUND",
        )
    except OSError as exc:
        raise VerificationInputError(
            "unable to read " + label + ": " + str(exc),
            "READ",
            "READ_ERROR",
        )

    if len(raw) > MAX_INPUT_BYTES:
        raise VerificationInputError(
            label + " exceeds verifier input byte limit",
            "INTAKE",
            "INPUT_TOO_LARGE",
        )

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise VerificationInputError(
            "invalid UTF-8 " + label + ": " + str(exc),
            "DECODE",
            "INVALID_UTF8",
        )

    try:
        value = json.loads(
            text,
            object_pairs_hook=reject_duplicate_object_pairs,
            parse_constant=reject_nonstandard_constant,
        )
    except DuplicateKeyError as exc:
        raise VerificationInputError(
            str(exc),
            "PARSE",
            "DUPLICATE_JSON_KEY",
        )
    except json.JSONDecodeError as exc:
        raise VerificationInputError(
            "invalid JSON " + label + ": " + str(exc),
            "PARSE",
            "INVALID_JSON",
        )
    except RecursionError:
        raise VerificationInputError(
            label + " exceeds supported JSON nesting depth",
            "PARSE",
            "JSON_NESTING_TOO_DEEP",
        )
    except ValueError as exc:
        raise VerificationInputError(
            "invalid JSON " + label + ": " + str(exc),
            "PARSE",
            "INVALID_JSON_VALUE",
        )

    if strict_canonical:
        try:
            expected = canonical_json(value).encode("utf-8")
        except (TypeError, ValueError, UnicodeEncodeError) as exc:
            raise VerificationInputError(
                "unable to canonicalize " + label + ": " + str(exc),
                "CANONICALIZATION",
                "CANONICALIZATION_FAILED",
            )
        if raw != expected:
            raise VerificationInputError(
                label + " bytes are not in canonical JSON form",
                "CANONICALIZATION",
                "NON_CANONICAL_JSON_BYTES",
            )

    return value


def read_bundle(path, strict_canonical=False):
    return read_json_document(
        path,
        strict_canonical=strict_canonical,
        label="bundle",
    )


def make_corpus_result(
    valid=False,
    errors=None,
    manifest_path=None,
    manifest_id=None,
    passed=0,
    total=0,
    entries=None,
    failure_stage=None,
    reason_code=None,
):
    return {
        "profile": CORPUS_VERIFICATION_PROFILE,
        "version": VERSION,
        "valid": bool(valid),
        "status": "PASS" if valid else "FAIL",
        "errors": list(errors or []),
        "failure_stage": failure_stage,
        "reason_code": reason_code,
        "manifest_path": None if manifest_path is None else str(manifest_path),
        "manifest_id": manifest_id,
        "passed": int(passed),
        "total": int(total),
        "entries": list(entries or []),
    }


def verify_corpus_manifest(path, strict_canonical=False):
    try:
        manifest = read_json_document(
            path,
            strict_canonical=strict_canonical,
            label="corpus manifest",
        )
    except VerificationInputError as exc:
        return make_corpus_result(
            valid=False,
            errors=[str(exc)],
            manifest_path=path,
            failure_stage=exc.failure_stage,
            reason_code=exc.reason_code,
        )
    except Exception as exc:
        return make_corpus_result(
            valid=False,
            errors=["unexpected verifier error: " + type(exc).__name__ + ": " + str(exc)],
            manifest_path=path,
            failure_stage="INTERNAL",
            reason_code="UNEXPECTED_VERIFIER_ERROR",
        )

    try:
        if not isinstance(manifest, dict):
            return make_corpus_result(
                valid=False,
                errors=["corpus manifest must be an object"],
                manifest_path=path,
                failure_stage="INTAKE",
                reason_code="NON_OBJECT_MANIFEST",
            )

        expected_manifest_fields = {
            "architecture_profile",
            "compatibility_profile",
            "corpus_profile",
            "manifest_id",
            "profile",
            "ruleset_profile",
            "scenario_count",
            "scenarios",
        }
        if set(manifest) != expected_manifest_fields:
            return make_corpus_result(
                valid=False,
                errors=["corpus manifest fields do not match the required schema"],
                manifest_path=path,
                manifest_id=manifest.get("manifest_id"),
                failure_stage="INTAKE",
                reason_code="MANIFEST_FIELD_MISMATCH",
            )

        profile_checks = [
            ("profile", CORPUS_MANIFEST_PROFILE),
            ("corpus_profile", CORPUS_PROFILE),
            ("architecture_profile", ARCHITECTURE_PROFILE),
            ("ruleset_profile", RULESET_PROFILE),
            ("compatibility_profile", COMPATIBILITY_PROFILE),
        ]
        profile_errors = [
            field + " mismatch"
            for field, expected in profile_checks
            if manifest.get(field) != expected
        ]
        if profile_errors:
            return make_corpus_result(
                valid=False,
                errors=profile_errors,
                manifest_path=path,
                manifest_id=manifest.get("manifest_id"),
                failure_stage="INTAKE",
                reason_code="MANIFEST_PROFILE_MISMATCH",
            )

        scenarios = manifest.get("scenarios")
        if not isinstance(scenarios, list):
            return make_corpus_result(
                valid=False,
                errors=["manifest.scenarios must be an array"],
                manifest_path=path,
                manifest_id=manifest.get("manifest_id"),
                failure_stage="INTAKE",
                reason_code="INVALID_SCENARIO_LIST",
            )
        if manifest.get("scenario_count") != len(scenarios):
            return make_corpus_result(
                valid=False,
                errors=["scenario_count does not match scenarios length"],
                manifest_path=path,
                manifest_id=manifest.get("manifest_id"),
                failure_stage="INTAKE",
                reason_code="SCENARIO_COUNT_MISMATCH",
            )

        manifest_basis = dict(manifest)
        supplied_manifest_id = manifest_basis.pop("manifest_id")
        expected_manifest_id = "corpus_manifest_" + hash_text(canonical_json(manifest_basis))
        if supplied_manifest_id != expected_manifest_id:
            return make_corpus_result(
                valid=False,
                errors=["manifest_id mismatch"],
                manifest_path=path,
                manifest_id=supplied_manifest_id,
                failure_stage="COMPARE",
                reason_code="MANIFEST_ID_MISMATCH",
            )

        expected_entry_fields = {
            "balance_snapshot_id",
            "boundary_receipt_id",
            "boundary_state",
            "claim_set_id",
            "compatibility_receipt_id",
            "filename",
            "financial_bundle_id",
            "financial_resolution_id",
            "independent_verification",
            "observation_set_id",
            "projection_root",
            "result",
            "scenario",
            "sha256",
            "transaction_receipt_root",
        }

        seen_scenarios = set()
        seen_filenames = set()
        entries = []
        errors = []
        manifest_dir = Path(path).resolve().parent

        for index, entry in enumerate(scenarios):
            entry_label = "scenarios[" + str(index) + "]"
            entry_errors = []
            if not isinstance(entry, dict):
                entry_errors.append(entry_label + ": must be an object")
                entries.append({
                    "scenario": None,
                    "filename": None,
                    "valid": False,
                    "errors": entry_errors,
                })
                errors.extend(entry_errors)
                continue

            if set(entry) != expected_entry_fields:
                entry_errors.append(entry_label + ": fields do not match the required schema")

            scenario_name = entry.get("scenario")
            filename = entry.get("filename")
            if not isinstance(scenario_name, str) or not scenario_name:
                entry_errors.append(entry_label + ": invalid scenario")
            elif scenario_name in seen_scenarios:
                entry_errors.append(entry_label + ": duplicate scenario")
            else:
                seen_scenarios.add(scenario_name)

            if not isinstance(filename, str) or not filename:
                entry_errors.append(entry_label + ": invalid filename")
            else:
                candidate = Path(filename)
                if candidate.is_absolute() or candidate.name != filename or "/" in filename or "\\" in filename:
                    entry_errors.append(entry_label + ": unsafe bundle filename")
                elif filename in seen_filenames:
                    entry_errors.append(entry_label + ": duplicate filename")
                else:
                    seen_filenames.add(filename)

            if entry.get("result") != "ACCEPTED":
                entry_errors.append(entry_label + ": result must be ACCEPTED")
            if entry.get("independent_verification") != "PASS":
                entry_errors.append(entry_label + ": independent_verification must be PASS")

            if entry_errors:
                entries.append({
                    "scenario": scenario_name,
                    "filename": filename,
                    "valid": False,
                    "errors": entry_errors,
                })
                errors.extend(entry_errors)
                continue

            bundle_path = manifest_dir / filename
            try:
                bundle_bytes = bundle_path.read_bytes()
            except FileNotFoundError:
                entry_errors.append(entry_label + ": bundle file not found")
                bundle_bytes = None
            except OSError as exc:
                entry_errors.append(entry_label + ": unable to read bundle file: " + str(exc))
                bundle_bytes = None

            if bundle_bytes is not None:
                actual_sha256 = hashlib.sha256(bundle_bytes).hexdigest()
                if actual_sha256 != entry.get("sha256"):
                    entry_errors.append(entry_label + ": sha256 mismatch")

            if not entry_errors:
                try:
                    bundle = read_bundle(
                        bundle_path,
                        strict_canonical=strict_canonical,
                    )
                except VerificationInputError as exc:
                    entry_errors.append(
                        entry_label + ": " + exc.reason_code + ": " + str(exc)
                    )
                    bundle = None
            else:
                bundle = None

            verification = compare_bundle(bundle) if bundle is not None else None
            if verification is not None and not verification["valid"]:
                entry_errors.extend(
                    entry_label + ": " + item
                    for item in verification["errors"]
                )

            if bundle is not None and verification is not None and verification["valid"]:
                field_checks = [
                    ("financial_resolution_id", bundle.get("financial_resolution_id")),
                    ("financial_bundle_id", bundle.get("financial_bundle_id")),
                    ("balance_snapshot_id", (bundle.get("balance_basis") or {}).get("balance_snapshot_id")),
                    ("claim_set_id", (bundle.get("evidence") or {}).get("claim_set_id")),
                    ("observation_set_id", (bundle.get("evidence") or {}).get("observation_set_id")),
                    ("transaction_receipt_root", (bundle.get("transactions") or {}).get("transaction_receipt_root")),
                    ("projection_root", (bundle.get("structural_projection") or {}).get("projection_root")),
                    ("compatibility_receipt_id", (bundle.get("declared_balance_compatibility") or {}).get("compatibility_receipt_id")),
                    ("boundary_receipt_id", (bundle.get("boundary") or {}).get("boundary_receipt_id")),
                    ("boundary_state", (bundle.get("boundary") or {}).get("state")),
                ]
                for field, actual in field_checks:
                    if entry.get(field) != actual:
                        entry_errors.append(entry_label + ": " + field + " mismatch")

            entry_valid = not entry_errors
            entries.append({
                "scenario": scenario_name,
                "filename": filename,
                "valid": entry_valid,
                "errors": entry_errors,
            })
            errors.extend(entry_errors)

        passed = sum(1 for entry in entries if entry["valid"])
        total = len(entries)
        return make_corpus_result(
            valid=not errors and passed == total,
            errors=errors,
            manifest_path=path,
            manifest_id=supplied_manifest_id,
            passed=passed,
            total=total,
            entries=entries,
            failure_stage=None if not errors else "CORPUS",
            reason_code="VERIFIED" if not errors else "CORPUS_VERIFICATION_FAILED",
        )
    except Exception as exc:
        return make_corpus_result(
            valid=False,
            errors=["unexpected verifier error: " + type(exc).__name__ + ": " + str(exc)],
            manifest_path=path,
            manifest_id=manifest.get("manifest_id") if isinstance(manifest, dict) else None,
            failure_stage="INTERNAL",
            reason_code="UNEXPECTED_VERIFIER_ERROR",
        )


def print_verification(result, path):
    print("ORL-Money Independent Verification | " + INDEPENDENT_VERIFICATION_PROFILE)
    print("=" * 96)
    print("  Bundle                             : " + str(path))
    print("  Result                             : " + result.get("status", "FAIL"))
    print("  Failure stage                      : " + str(result.get("failure_stage")))
    print("  Reason code                        : " + str(result.get("reason_code")))
    print("  Independent reconstruction         : " + str(result.get("independent_reconstruction")))
    print("  Producer implementation imported   : " + str(result.get("producer_import_used")))
    print("  Producer self verification present : " + str(result.get("producer_self_verification_present")))
    if result.get("producer_self_verification_present"):
        print("  Producer self verification valid   : " + str(result.get("producer_self_verification_valid")))
    print("-" * 96)
    print("  Supplied resolution ID             : " + str(result.get("supplied_financial_resolution_id")))
    print("  Reconstructed resolution ID        : " + str(result.get("reconstructed_financial_resolution_id")))
    print("  Supplied bundle ID                 : " + str(result.get("supplied_financial_bundle_id")))
    print("  Reconstructed bundle ID            : " + str(result.get("reconstructed_financial_bundle_id")))
    if result.get("errors"):
        print("-" * 96)
        for error in result["errors"]:
            print("  ERROR                              : " + str(error))


def print_corpus_verification(result):
    print("ORL-Money Corpus Verification | " + CORPUS_VERIFICATION_PROFILE)
    print("=" * 96)
    print("  Manifest                           : " + str(result.get("manifest_path")))
    print("  Result                             : " + result.get("status", "FAIL"))
    print("  Manifest ID                        : " + str(result.get("manifest_id")))
    print("  Summary                            : " + str(result.get("passed", 0)) + "/" + str(result.get("total", 0)) + " PASS")
    if result.get("failure_stage") is not None:
        print("  Failure stage                      : " + str(result.get("failure_stage")))
    if result.get("reason_code") is not None:
        print("  Reason code                        : " + str(result.get("reason_code")))
    for entry in result.get("entries", []):
        print(
            "  "
            + str(entry.get("scenario")).ljust(34)
            + " : "
            + ("PASS" if entry.get("valid") else "FAIL")
        )
    if result.get("errors"):
        print("-" * 96)
        for error in result["errors"]:
            print("  ERROR                              : " + str(error))


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Independent verifier for ORL-Money v2.1.0 financial bundles"
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--bundle", help="path to an ORL-Money JSON bundle")
    mode.add_argument("--corpus", help="path to an ORL-Money frozen corpus manifest")
    mode.add_argument("--self-test", action="store_true")
    parser.add_argument(
        "--strict-canonical",
        action="store_true",
        help="require exact canonical JSON bytes for supplied bundle or corpus files",
    )
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(sys.argv[1:] if argv is None else argv)

    if args.self_test:
        return 0 if run_self_test(args.json) else 1

    if args.corpus:
        result = verify_corpus_manifest(
            args.corpus,
            strict_canonical=args.strict_canonical,
        )
        if args.json:
            print(canonical_json(result))
        else:
            print_corpus_verification(result)
        return 0 if result["valid"] else 1

    if not args.bundle:
        print(
            "Use --bundle <path>, --corpus <manifest>, or --self-test.",
            file=sys.stderr,
        )
        return 2

    try:
        bundle = read_bundle(
            args.bundle,
            strict_canonical=args.strict_canonical,
        )
        result = compare_bundle(bundle)
    except VerificationInputError as exc:
        result = make_verification_result(
            valid=False,
            errors=[str(exc)],
            failure_stage=exc.failure_stage,
            reason_code=exc.reason_code,
        )
    except Exception as exc:
        result = make_verification_result(
            valid=False,
            errors=["unexpected verifier error: " + type(exc).__name__ + ": " + str(exc)],
            failure_stage="INTERNAL",
            reason_code="UNEXPECTED_VERIFIER_ERROR",
        )

    if args.json:
        print(canonical_json(result))
    else:
        print_verification(result, args.bundle)
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
