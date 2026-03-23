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
            f"{entry['account']:<18} "
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


def count_new_fragments(existing_entries, incoming_entries):
    existing_keys = {entry_key(entry) for entry in deduplicate(existing_entries)}
    incoming_keys = {entry_key(entry) for entry in deduplicate(incoming_entries)}
    return len(incoming_keys - existing_keys)


def print_round_exchange_summary(round_label, node_a, node_b, node_c):
    sent_c_to_a = count_unique_fragments(node_c)
    new_c_to_a = count_new_fragments(node_a, node_c)

    sent_a_to_b = count_unique_fragments(node_a)
    new_a_to_b = count_new_fragments(node_b, node_a)

    sent_b_to_c = count_unique_fragments(node_b)
    new_b_to_c = count_new_fragments(node_c, node_b)

    total_sent = sent_c_to_a + sent_a_to_b + sent_b_to_c
    total_new = new_c_to_a + new_a_to_b + new_b_to_c

    print(f"{round_label} exchange summary:")
    print("-" * 84)
    print(f"  Node-C -> Node-A : sent {sent_c_to_a} unique fragments | new at receiver = {new_c_to_a}")
    print(f"  Node-A -> Node-B : sent {sent_a_to_b} unique fragments | new at receiver = {new_a_to_b}")
    print(f"  Node-B -> Node-C : sent {sent_b_to_c} unique fragments | new at receiver = {new_b_to_c}")
    print(f"  Total unique fragments sent this round = {total_sent}")
    print(f"  Total newly absorbed at receivers       = {total_new}")
    if total_new == 0:
        print("  No new fragments were absorbed in this round.")


def scenario():
    initial_balances = {
        "VillageA": 1000,
        "VillageB": 1000,
        "VillageC": 1000,
    }

    node_a = [
        {"tx": "M100", "side": "debit",  "account": "VillageA", "amount": 500},
        {"tx": "M300", "side": "credit", "account": "VillageA", "amount": 150},
        {"tx": "M400", "side": "debit",  "account": "VillageA", "amount": 300},
        {"tx": "M500", "side": "credit", "account": "VillageA", "amount": 250},
    ]

    node_b = [
        {"tx": "M100", "side": "credit", "account": "VillageB",          "amount": 500},
        {"tx": "M200", "side": "debit",  "account": "VillageB",          "amount": 200},
        {"tx": "M500", "side": "debit",  "account": "VillageB",          "amount": 250},
        {"tx": "M500", "side": "debit",  "account": "VillageB_conflict", "amount": 250},
    ]

    node_c = [
        {"tx": "M200", "side": "credit", "account": "VillageC", "amount": 200},
        {"tx": "M300", "side": "debit",  "account": "VillageC", "amount": 150},
        {"tx": "M400", "side": "credit", "account": "VillageC", "amount": 350},
    ]

    return initial_balances, node_a, node_b, node_c


def classify_certificate(tx_state):
    resolved_tx_count = sum(1 for info in tx_state.values() if info["state"] == "RESOLVED")
    abstain_tx_count = sum(1 for info in tx_state.values() if info["state"] == "ABSTAIN")
    incomplete_tx_count = sum(1 for info in tx_state.values() if info["state"] == "INCOMPLETE")

    return {
        "mismatch_contained": tx_state.get("M400", {}).get("state") == "ABSTAIN",
        "conflict_contained": tx_state.get("M500", {}).get("state") == "ABSTAIN",
        "resolved_tx_count": resolved_tx_count,
        "abstain_tx_count": abstain_tx_count,
        "incomplete_tx_count": incomplete_tx_count,
    }


def print_outcome_summary():
    print("\nOutcome Interpretation")
    print("-" * 84)
    print("  M100  RESOLVED   VillageA -> VillageB converges correctly across fragmented nodes")
    print("  M200  RESOLVED   VillageB -> VillageC resolves after bounded multi-round sharing")
    print("  M300  RESOLVED   VillageC -> VillageA resolves after bounded multi-round sharing")
    print("  M400  ABSTAIN    mismatch detected, therefore the ledger stays uncorrupted")
    print("  M500  ABSTAIN    conflicting debit structure detected, therefore no false value appears")


def print_story_block():
    print("Three independent village systems begin with different money fragments.")
    print("They do not share a clock.")
    print("They do not share a transaction order.")
    print("They do not rely on a coordinator.")
    print("They exchange only bounded structure across multiple rounds.")
    print()
    print("And yet:")
    print("  valid money resolves")
    print("  missing structure becomes complete through bounded sharing")
    print("  conflicting structure is not forced")
    print("  final truth still converges across all nodes")


def round_exchange(node_a, node_b, node_c):
    next_a = bounded_union(deepcopy(node_a), node_c)
    next_b = bounded_union(deepcopy(node_b), node_a)
    next_c = bounded_union(deepcopy(node_c), node_b)
    return next_a, next_b, next_c


def simulate():
    initial_balances, node_a, node_b, node_c = scenario()

    print_header("ORL-Money Multi-Node")
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

    balances_c_before, state_c_before = print_node_snapshot(
        "Node-C | local structural view",
        node_c,
    )

    signature_a_before = ledger_signature(balances_a_before, state_a_before)
    signature_b_before = ledger_signature(balances_b_before, state_b_before)
    signature_c_before = ledger_signature(balances_c_before, state_c_before)

    print_header("Fragment Absorption Check")
    print(f"  node_a_raw_fragments      = {len(node_a)}")
    print(f"  node_a_unique_fragments   = {count_unique_fragments(node_a)}")
    print(f"  node_b_raw_fragments      = {len(node_b)}")
    print(f"  node_b_unique_fragments   = {count_unique_fragments(node_b)}")
    print(f"  node_c_raw_fragments      = {len(node_c)}")
    print(f"  node_c_unique_fragments   = {count_unique_fragments(node_c)}")
    print("  duplicate fragments are absorbed before structural resolution begins")

    print_header("Bounded Sharing Phase | Round 1")
    print("Node-A absorbs Node-C.")
    print("Node-B absorbs Node-A.")
    print("Node-C absorbs Node-B.")
    print("No timestamps are used.")
    print("No ordering authority is used.")
    print("No coordinator is used.")
    print()
    print_round_exchange_summary("Round 1", node_a, node_b, node_c)

    node_a_r1, node_b_r1, node_c_r1 = round_exchange(node_a, node_b, node_c)

    balances_a_r1, state_a_r1 = print_node_snapshot(
        "Node-A | after round 1",
        node_a_r1,
    )

    balances_b_r1, state_b_r1 = print_node_snapshot(
        "Node-B | after round 1",
        node_b_r1,
    )

    balances_c_r1, state_c_r1 = print_node_snapshot(
        "Node-C | after round 1",
        node_c_r1,
    )

    signature_a_r1 = ledger_signature(balances_a_r1, state_a_r1)
    signature_b_r1 = ledger_signature(balances_b_r1, state_b_r1)
    signature_c_r1 = ledger_signature(balances_c_r1, state_c_r1)

    print_header("Bounded Sharing Phase | Round 2")
    print("Node-A absorbs Node-C again.")
    print("Node-B absorbs Node-A again.")
    print("Node-C absorbs Node-B again.")
    print()
    print_round_exchange_summary("Round 2", node_a_r1, node_b_r1, node_c_r1)

    node_a_r2, node_b_r2, node_c_r2 = round_exchange(node_a_r1, node_b_r1, node_c_r1)

    balances_a_r2, state_a_r2 = print_node_snapshot(
        "Node-A | after round 2",
        node_a_r2,
    )

    balances_b_r2, state_b_r2 = print_node_snapshot(
        "Node-B | after round 2",
        node_b_r2,
    )

    balances_c_r2, state_c_r2 = print_node_snapshot(
        "Node-C | after round 2",
        node_c_r2,
    )

    signature_a_r2 = ledger_signature(balances_a_r2, state_a_r2)
    signature_b_r2 = ledger_signature(balances_b_r2, state_b_r2)
    signature_c_r2 = ledger_signature(balances_c_r2, state_c_r2)

    print_header("Convergence Check")
    print(f"  before_match = {signature_a_before == signature_b_before == signature_c_before}")
    print(f"  round_1_match = {signature_a_r1 == signature_b_r1 == signature_c_r1}")
    print(f"  round_2_match = {signature_a_r2 == signature_b_r2 == signature_c_r2}")

    final_balance_effects, final_tx_state = resolve(node_a_r2)
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
    print(f"  all_nodes_equal            = {signature_a_r2 == signature_b_r2 == signature_c_r2}")
    print(f"  money_conserved            = {money_conserved}")
    print(f"  mismatch_contained         = {certificate['mismatch_contained']}")
    print(f"  conflict_contained         = {certificate['conflict_contained']}")
    print(f"  total_money_initial        = {total_money(initial_balances)}")
    print(f"  total_money_final          = {total_money(final_balances)}")
    print(f"  net_resolved_balance_delta = {final_effect_total}")
    print(f"  resolved_tx_count          = {certificate['resolved_tx_count']}")
    print(f"  abstain_tx_count           = {certificate['abstain_tx_count']}")
    print(f"  incomplete_tx_count        = {certificate['incomplete_tx_count']}")
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
    print("  money was never falsely moved from conflicting structure")
    print("  bounded multi-round sharing completed valid transfers")
    print("  all three isolated nodes reached the same final truth")


if __name__ == "__main__":
    simulate()