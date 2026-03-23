from collections import defaultdict
from copy import deepcopy


def entry_key(entry):
    return (
        entry["tx"],
        entry["side"],
        entry["account"],
        entry["amount"],
    )


def deduplicate(entries):
    unique = {}
    for entry in entries:
        unique[entry_key(entry)] = entry
    return list(unique.values())


def resolve(entries):
    unique_entries = deduplicate(entries)
    by_tx = defaultdict(list)

    for entry in unique_entries:
        by_tx[entry["tx"]].append(entry)

    balances = defaultdict(int)
    tx_state = {}

    for tx in sorted(by_tx):
        group = by_tx[tx]
        debits = {(e["account"], e["amount"]) for e in group if e["side"] == "debit"}
        credits = {(e["account"], e["amount"]) for e in group if e["side"] == "credit"}

        if len(debits) == 1 and len(credits) == 1:
            (from_acct, debit_amt), = debits
            (to_acct, credit_amt), = credits

            if debit_amt == credit_amt:
                balances[from_acct] -= debit_amt
                balances[to_acct] += credit_amt
                tx_state[tx] = {
                    "state": "RESOLVED",
                    "from": from_acct,
                    "to": to_acct,
                    "amount": debit_amt,
                }
            else:
                tx_state[tx] = {
                    "state": "ABSTAIN",
                    "reason": "debit_credit_mismatch",
                }

        elif not debits or not credits:
            tx_state[tx] = {
                "state": "INCOMPLETE",
                "reason": "missing_counterpart",
            }
        else:
            tx_state[tx] = {
                "state": "ABSTAIN",
                "reason": "conflicting_structure",
            }

    return dict(sorted(balances.items())), dict(sorted(tx_state.items()))


def bounded_union(node_entries, incoming_entries):
    return deduplicate(node_entries + incoming_entries)


def ledger_signature(balances, tx_state):
    return (
        tuple(sorted(balances.items())),
        tuple(sorted((tx, tuple(sorted(info.items()))) for tx, info in tx_state.items())),
    )


def summarize_states(tx_state):
    counts = defaultdict(int)
    for info in tx_state.values():
        counts[info["state"]] += 1
    return dict(sorted(counts.items()))


def print_header(title):
    print("\n" + "=" * 84)
    print(title)
    print("=" * 84)


def print_balances(label, balances):
    print(label)
    print("-" * 84)
    if not balances:
        print("  (no resolved balances)")
        return
    for account, amount in balances.items():
        sign = "+" if amount >= 0 else ""
        print(f"  {account:>12} : {sign}{amount}")


def print_absolute_balances(label, balances):
    print(label)
    print("-" * 84)
    for account, amount in sorted(balances.items()):
        print(f"  {account:>12} : {amount}")


def apply_effects(initial_balances, balance_effects):
    final_balances = dict(initial_balances)
    for account, delta in balance_effects.items():
        final_balances[account] = final_balances.get(account, 0) + delta
    return dict(sorted(final_balances.items()))


def print_states(tx_state):
    print("\nTransaction States")
    print("-" * 84)
    for tx, info in tx_state.items():
        if info["state"] == "RESOLVED":
            print(
                f"  {tx:<10} RESOLVED    "
                f"{info['from']} -> {info['to']}    amount={info['amount']}"
            )
        else:
            print(
                f"  {tx:<10} {info['state']:<11} "
                f"reason={info['reason']}"
            )


def print_node_snapshot(name, entries):
    balances, tx_state = resolve(entries)

    print_header(name)
    print("Visible Fragments")
    print("-" * 84)
    for entry in deduplicate(entries):
        print(
            f"  {entry['tx']:<10} "
            f"{entry['side']:<6} "
            f"{entry['account']:<12} "
            f"amount={entry['amount']}"
        )

    print()
    print_balances("Resolved Balance Effects", balances)
    print_states(tx_state)
    print(f"\nState Summary: {summarize_states(tx_state)}")

    return balances, tx_state


def total_money(balances):
    return sum(balances.values())


def count_unique_fragments(entries):
    return len(deduplicate(entries))


def scenario():
    initial_balances = {
        "VillageA": 1000,
        "VillageB": 1000,
    }

    node_a = [
        {"tx": "M100", "side": "debit",  "account": "VillageA", "amount": 500},
        {"tx": "M300", "side": "debit",  "account": "VillageA", "amount": 120},
        {"tx": "M400", "side": "debit",  "account": "VillageA", "amount": 400},
        {"tx": "M500", "side": "debit",  "account": "VillageA", "amount": 250},
    ]

    node_b = [
        {"tx": "M100", "side": "credit", "account": "VillageB",     "amount": 500},
        {"tx": "M100", "side": "credit", "account": "VillageB",     "amount": 500},
        {"tx": "M200", "side": "credit", "account": "VillageB",     "amount": 300},
        {"tx": "M400", "side": "credit", "account": "VillageB",     "amount": 450},
        {"tx": "M500", "side": "credit", "account": "VillageB",     "amount": 250},
        {"tx": "M500", "side": "credit", "account": "VillageB_Alt", "amount": 250},
    ]

    return initial_balances, node_a, node_b


def classify_certificate(tx_state):
    duplicate_safe = tx_state.get("M100", {}).get("state") == "RESOLVED"
    no_loss_forced = (
        tx_state.get("M200", {}).get("state") == "INCOMPLETE"
        and tx_state.get("M300", {}).get("state") == "INCOMPLETE"
    )
    mismatch_contained = tx_state.get("M400", {}).get("state") == "ABSTAIN"
    conflict_contained = tx_state.get("M500", {}).get("state") == "ABSTAIN"

    return {
        "duplicate_safe": duplicate_safe,
        "no_loss_forced": no_loss_forced,
        "mismatch_contained": mismatch_contained,
        "conflict_contained": conflict_contained,
    }


def print_outcome_summary():
    print("\nOutcome Interpretation")
    print("-" * 84)
    print("  M100  RESOLVED   valid transfer converges correctly across isolated nodes")
    print("  M200  INCOMPLETE missing debit, therefore no forced money movement occurs")
    print("  M300  INCOMPLETE missing credit, therefore no forced money movement occurs")
    print("  M400  ABSTAIN    mismatch detected, therefore the ledger stays uncorrupted")
    print("  M500  ABSTAIN    conflicting credit structure detected, therefore no false value appears")


def print_story_block():
    print("Two independent village systems begin with different money fragments.")
    print("They do not share a clock.")
    print("They do not share a transaction order.")
    print("They do not rely on a coordinator.")
    print()
    print("And yet:")
    print("  valid money resolves")
    print("  missing structure is not guessed")
    print("  conflicting structure is not forced")
    print("  final truth still converges")


def simulate():
    initial_balances, node_a, node_b = scenario()

    print_header("ORL-Money")
    print("Offline money reconciliation through deterministic structural resolution")
    print()
    print_story_block()
    print()
    print("Core principle:")
    print("  correctness = resolve(structure)")
    print()
    print("Structural law:")
    print("  valid structure -> RESOLVED")
    print("  missing structure -> INCOMPLETE")
    print("  conflicting structure -> ABSTAIN")
    print()
    print("Money conservation target:")
    print(f"  total_money_initial = {total_money(initial_balances)}")

    print_header("Initial Absolute Balances")
    print_absolute_balances("Starting Money", initial_balances)

    balances_a_before, state_a_before = print_node_snapshot(
        "Node-A | local structural view",
        node_a,
    )

    balances_b_before, state_b_before = print_node_snapshot(
        "Node-B | local structural view",
        node_b,
    )

    signature_a_before = ledger_signature(balances_a_before, state_a_before)
    signature_b_before = ledger_signature(balances_b_before, state_b_before)

    print_header("Fragment Absorption Check")
    print(f"  node_b_raw_fragments      = {len(node_b)}")
    print(f"  node_b_unique_fragments   = {count_unique_fragments(node_b)}")
    print("  duplicate fragments are absorbed before structural resolution begins")

    print_header("Bounded Sharing Phase")
    print("Node-A and Node-B exchange only available structure.")
    print("No timestamps are used.")
    print("No ordering authority is used.")
    print("No coordinator is used.")

    node_a_after = bounded_union(deepcopy(node_a), node_b)
    node_b_after = bounded_union(deepcopy(node_b), node_a)

    balances_a_after, state_a_after = print_node_snapshot(
        "Node-A | after bounded sharing",
        node_a_after,
    )

    balances_b_after, state_b_after = print_node_snapshot(
        "Node-B | after bounded sharing",
        node_b_after,
    )

    signature_a_after = ledger_signature(balances_a_after, state_a_after)
    signature_b_after = ledger_signature(balances_b_after, state_b_after)

    print_header("Convergence Check")
    print(f"  before_match = {signature_a_before == signature_b_before}")
    print(f"  after_match  = {signature_a_after == signature_b_after}")

    final_balance_effects, final_tx_state = resolve(node_a_after)
    final_balances = apply_effects(initial_balances, final_balance_effects)
    final_effect_total = sum(final_balance_effects.values())
    money_conserved = total_money(final_balances) == total_money(initial_balances)
    certificate = classify_certificate(final_tx_state)

    print_header("Final Shared Truth")
    print_balances("Final Resolved Balance Effects", final_balance_effects)
    print_absolute_balances("Final Absolute Balances", final_balances)
    print_states(final_tx_state)
    print_outcome_summary()

    print_header("Global Certificate")
    print(f"  all_nodes_equal            = {signature_a_after == signature_b_after}")
    print(f"  money_conserved            = {money_conserved}")
    print(f"  duplicate_safe             = {certificate['duplicate_safe']}")
    print(f"  no_loss_forced             = {certificate['no_loss_forced']}")
    print(f"  mismatch_contained         = {certificate['mismatch_contained']}")
    print(f"  conflict_contained         = {certificate['conflict_contained']}")
    print(f"  total_money_initial        = {total_money(initial_balances)}")
    print(f"  total_money_final          = {total_money(final_balances)}")
    print(f"  net_resolved_balance_delta = {final_effect_total}")
    print(f"  state_summary              = {summarize_states(final_tx_state)}")

    print_header("Final Verdict")
    print("Money was not made correct by coordination.")
    print("Money was not made correct by time.")
    print("Money was not made correct by transaction order.")
    print()
    print("Correctness emerged from structure.")
    print()
    print("In this demonstration:")
    print("  money was never duplicated")
    print("  money was never falsely moved from incomplete structure")
    print("  conflicts did not corrupt the ledger")
    print("  both isolated nodes reached the same final truth")


if __name__ == "__main__":
    simulate()