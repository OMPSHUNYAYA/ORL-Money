# 🧩 ORL-Money Proof Sketch (Deterministic Structural Guarantees)

This document provides a minimal proof sketch for the deterministic structural guarantees of **ORL-Money** under its resolver rules.

**ORL-Money is intentionally minimal.**

Its correctness does not come from sequence, timing, or coordination.  
It comes from **structural acceptance rules applied deterministically to the same evidence.**

---

## 1. Convergence

Each node applies the same resolver rules to the same final structural set.

The union operation used for bounded sharing is **order-independent**:

`structure_A ∪ structure_B = structure_B ∪ structure_A`

After sufficient bounded sharing and deduplication, nodes converge to the same structural evidence set.

Since `resolve(...)` is deterministic, identical input structure produces identical output:

`if S_A = S_B, then resolve(S_A) = resolve(S_B)`

Thus, convergence reduces to **structural equality**, not temporal coordination.

So convergence does not depend on:

• message order  
• arrival timing  
• synchronization  
• coordinator authority  

It depends only on **eventual access to the same structural fragments.**

---

## 2. Conservation

A transaction becomes **RESOLVED** only when exactly one valid debit and one matching credit exist with equal amount.

Every **RESOLVED** transaction contributes exactly one debit and one matching credit of equal amount:

`debit(x)` and `credit(x)` with equal amount

This implies:

`sum(resolved_debits) = sum(resolved_credits)`

Therefore, resolved financial movement is internally balanced.

Since incomplete or conflicting transactions do not move balances, unresolved structure contributes no false state change.

Hence:

`total_money_initial = total_money_final`

No valid execution path exists inside the resolver for **silent creation or loss of money.**

---

## 3. Deduplication Safety

ORL-Money applies **structural deduplication** before resolution.

Repeated copies of the same fragment do not create additional financial effect:

`deduplicate(S ∪ S) = deduplicate(S)`

and therefore:

`resolve(S) = resolve(deduplicate(S))`

This means replayed fragments, duplicate transmissions, or repeated bounded sharing do not multiply balances.

---

## 4. Incomplete Safety

If required structural counterparts are missing, the transaction is marked **INCOMPLETE**.

That means the resolver **withholds financial effect rather than guessing.**

So for incomplete structure:

`INCOMPLETE -> no movement`

This prevents premature acceptance from partial evidence.

The system remains open to later completion, but does not force correctness before structure is sufficient.

---

## 5. Conflict Safety

If the structure contains contradiction, mismatch, or competing incompatible claims, the transaction is marked **ABSTAIN**.

So for conflicting structure:

`ABSTAIN -> no movement`

This prevents corruption under disagreement.

Instead of forcing a false result, ORL-Money contains the conflict structurally until valid resolution is possible outside the current evidence set.

---

## 6. Monotonic Safety

Money only moves when structure crosses the acceptance boundary into valid completeness.

Before that point:

• incomplete structure causes no movement  
• conflicting structure causes no movement  

So unresolved evidence cannot accidentally degrade into false balance mutation.

This gives ORL-Money **monotonic safety**:

`invalid_or_incomplete -> no movement`  
`valid_complete        -> deterministic movement`

---

## 7. Conservative Extension

ORL-Money does not redefine financial correctness.

It preserves the classical valid outcome whenever the required financial structure is complete and consistent:

`classical result = ORL result`

Its innovation is not changing truth.

Its innovation is **changing the acceptance condition for truth under disorder.**

---

## 8. Summary

This proof sketch shows that ORL-Money has four core properties:

• **deterministic convergence** from shared structure  
• **conservation** from matched debit-credit resolution  
• **replay safety** from deduplication  
• **abstention safety** from explicit non-forcing states  

Therefore, ORL-Money deterministically reconciles fragmented financial evidence using **structure alone**, without reliance on time, order, synchronization, or coordination guarantees.

---

## Scope Note

This proof sketch applies to the ORL-Money resolver model as defined in the reference implementation.

It does **not** replace formal verification or domain-specific regulatory validation required for production systems.
