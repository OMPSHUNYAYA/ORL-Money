# 🧩 ORL-Money Model and Invariant Sketch

This document describes the current ORL-Money resolver model and the conditional properties that follow from its declared rules.

It is a **model and invariant sketch**, not a formal proof of universal financial correctness, production safety, settlement validity, or cross-implementation conformance.

ORL-Money is developed within the Shunyaya Framework.

---

## 1. Scope

ORL-Money is a deterministic reference model for bounded reconciliation of supported money fragments.

The governing relation is:

`same initial balances + same deduplicated supported money fragments + same resolver rules -> same bounded financial snapshot`

The current model demonstrates:

- exact duplicate absorption
- deterministic classification of supported fragments
- explicit `RESOLVED`, `INCOMPLETE`, and demonstrated `ABSTAIN` outcomes
- balance effects only for `RESOLVED` transactions
- same-evidence node equality
- demonstrated net-balance conservation for matching debit-credit pairs

The current model does not establish:

- authorization
- identity or account ownership
- available funds
- account posting
- payment execution
- clearing or settlement
- finality
- fraud prevention
- cryptographic security
- consensus
- reliable broadcast
- complete double-spend prevention
- complete malformed-input validation
- production readiness
- universal order independence
- universal financial correctness

---

## 2. Definitions

Let:

- `B` be an initial balance snapshot
- `E` be a collection of supported money fragments
- `D(E)` be exact-duplicate absorption
- `P(E)` be a supported permutation of `E`
- `v` be a fixed resolver-ruleset version
- `R_v(E)` be the transaction-state resolver under version `v`
- `A(B,R_v(E))` be application of resolved balance effects to `B`
- `F_v(B,E)` be the complete bounded financial snapshot

Define:

`F_v(B,E) = (R_v(D(E)), A(B,R_v(D(E))))`

The snapshot may include:

- transaction states
- resolved balance effects
- final demonstrated balances
- state counts
- equality checks

---

## 3. Current Supported Fragment Shape

The committed demonstrations use fragments with four fields:

```text
tx
side
account
amount
```

Example:

```text
{"tx": "M100", "side": "debit", "account": "VillageA", "amount": 500}
```

The current demonstrations expect values shaped like the committed examples.

A formal schema and explicit invalid-input refusal are not yet implemented.

---

## 4. Current Transaction Classification Rule

For each transaction identifier, the resolver groups exact-duplicate-absorbed fragments by side.

For the current supplied model:

`one debit + one credit + matching amount -> RESOLVED`

`missing debit OR missing credit -> INCOMPLETE`

`debit_credit_mismatch -> ABSTAIN`

`demonstrated_same_transaction_multiplicity_conflict -> ABSTAIN`

Only `RESOLVED` transactions produce demonstrated balance effects.

Other malformed, unsupported, or untested conflict forms remain outside the current conformance claim.

---

## 5. Conditional Determinism

For a fixed supported input and a fixed resolver version, the current resolver has no probabilistic branch.

Therefore:

`E_i = E_j AND v_i = v_j -> R_v(E_i) = R_v(E_j)`

For the complete bounded financial snapshot:

`B_i = B_j AND D(E_i) = D(E_j) -> F_v(B_i,E_i) = F_v(B_j,E_j)`

This is a conditional determinism statement.

It does not prove that:

- the inputs are valid
- the resolver rules are financially sufficient
- independently written implementations are conformant
- the output is authorized or legally valid

---

## 6. Same-Evidence Node Equality

Suppose two nodes use:

- the same initial balances
- the same deduplicated supported fragment set
- the same resolver rules

Then both evaluate the same deterministic function over the same inputs.

Therefore:

`B_i = B_j AND D(E_i) = D(E_j) -> F_v(B_i,E_i) = F_v(B_j,E_j)`

The node-equality claim begins only after the nodes hold the same relevant evidence.

ORL-Money does not claim equality when nodes permanently hold materially different evidence.

---

## 7. Arrival-Order Independence

Let `P(E)` be a supported permutation of the same fragment collection.

The current resolver groups and classifies fragments from their content rather than their arrival position.

The intended current-model invariant is:

`R_v(P(E)) = R_v(E)`

and therefore:

`F_v(B,P(E)) = F_v(B,E)`

This statement is limited to:

- the declared supported fragment model
- a fixed ruleset version
- identical initial balances
- permutations containing the same fragment content

A future release should verify this invariant across a declared permutation corpus and cross-language conformance vectors.

---

## 8. Exact Duplicate Absorption

The duplicate key in the current model consists of:

`(tx, side, account, amount)`

Applying exact-duplicate absorption twice has the same result as applying it once:

`D(D(E)) = D(E)`

Therefore, for the current deterministic resolver:

`R_v(D(D(E))) = R_v(D(E))`

For the supplied examples:

`F_v(B,E) = F_v(B,D(E))`

This means an identical repeated fragment is not counted twice in the demonstrated model.

It does not prove:

- general payment replay prevention
- external idempotency
- nonce safety
- complete duplicate-payment prevention
- complete double-spend prevention

---

## 9. Resolved-Pair Balance Preservation

For each demonstrated `RESOLVED` transaction, the model requires:

`debit_amount = credit_amount = x`

The applied effects are:

`from_account_delta = -x`

`to_account_delta = +x`

Therefore, for that resolved pair:

`(-x) + (+x) = 0`

Summed across all demonstrated resolved pairs:

`sum(resolved_balance_effects) = 0`

When those effects are applied to the initial balance snapshot:

`sum(final_balances) = sum(initial_balances)`

This is demonstrated net-balance conservation for matching debit-credit pairs.

It is not a universal money-conservation theorem because the current resolver does not fully validate:

- amount domains
- external postings
- hidden evidence
- authorization
- sufficient funds
- malformed values
- complete transaction semantics

---

## 10. INCOMPLETE Has No Demonstrated Balance Effect

For the current model:

`missing counterpart -> INCOMPLETE`

The current resolver applies no balance effect for an `INCOMPLETE` transaction.

Therefore:

`state(tx) = INCOMPLETE -> demonstrated_balance_effect(tx) = 0`

This prevents the current resolver from inventing a missing debit or credit.

It does not guarantee that the missing fragment does not exist elsewhere.

---

## 11. Demonstrated ABSTAIN Has No Balance Effect

For the supplied amount-mismatch and multiplicity-conflict examples:

`demonstrated conflict -> ABSTAIN`

The current resolver applies no balance effect for an `ABSTAIN` transaction.

Therefore, for the demonstrated conflict classes:

`state(tx) = ABSTAIN -> demonstrated_balance_effect(tx) = 0`

This is bounded abstention behavior.

It is not proof that every malformed or adversarial conflict is safely recognized.

---

## 12. Evidence Growth Is Not Acceptance-Monotonic

The original model should not be described as having universal monotonic acceptance.

Adding evidence can change classification.

Examples include:

`INCOMPLETE -> RESOLVED`

when a matching counterpart arrives.

It can also produce:

`RESOLVED -> ABSTAIN`

when later evidence introduces a demonstrated multiplicity conflict.

Therefore:

`E subset E'` does not imply that `state_E(tx) = state_E'(tx)`

The evidence set may grow monotonically while the resolver state changes non-monotonically.

This is an important reason not to describe a local `RESOLVED` state as immutable finality.

---

## 13. No Settlement Finality Follows From RESOLVED

Within the current model, `RESOLVED` means:

- exactly one demonstrated debit
- exactly one demonstrated credit
- equal demonstrated amounts
- no demonstrated multiplicity conflict in the evaluated set

It does not mean:

- authorized
- funded
- legally valid
- posted
- cleared
- settled
- immutable
- globally complete

A later structural-closure layer would be required to make a separate finality claim.

---

## 14. Relationship to Ordinary Arithmetic

For a supported matching debit-credit pair, ORL-Money applies the ordinary arithmetic effect:

`-x + x = 0`

The current model does not alter that arithmetic.

Its contribution is the explicit classification boundary that determines whether the demonstrated pair is:

- `RESOLVED`
- `INCOMPLETE`
- `ABSTAIN`

The justified relationship is:

`supported matching pair -> ordinary equal debit-credit arithmetic`

It is not:

`all classical financial outcomes = all ORL-Money outcomes`

---

## 15. Two-Node Reference Scenario

Initial balances:

```text
VillageA = 1000
VillageB = 1000
```

Expected final transaction states:

```text
M100 -> RESOLVED
M200 -> INCOMPLETE
M300 -> INCOMPLETE
M400 -> ABSTAIN
M500 -> ABSTAIN
```

Expected state summary:

```text
RESOLVED   = 1
INCOMPLETE = 2
ABSTAIN    = 2
```

Expected resolved balance effects:

```text
VillageA = -500
VillageB = +500
```

Expected final demonstrated balances:

```text
VillageA = 500
VillageB = 1500
```

Expected node equality:

```text
all_nodes_equal = True
```

For this scenario:

`sum(initial_balances) = 2000`

`sum(final_balances) = 2000`

---

## 16. Three-Node Scenario

Expected final transaction states:

```text
M100 -> RESOLVED
M200 -> RESOLVED
M300 -> RESOLVED
M400 -> ABSTAIN
M500 -> ABSTAIN
```

Expected state summary:

```text
RESOLVED = 3
ABSTAIN  = 2
```

Expected final demonstrated balances:

```text
VillageA = 650
VillageB = 1300
VillageC = 1050
```

Expected equality after round 2:

```text
round_2_match = True
```

For this scenario:

`sum(initial_balances) = 3000`

`sum(final_balances) = 3000`

The two sharing rounds are a committed test sequence.

They are not a proof of a general networking, consensus, or reliable-broadcast protocol.

---

## 17. Current Verification Status

The committed demonstrations can be checked against the documented expected:

- transaction states
- state summaries
- resolved balance effects
- final demonstrated balances
- same-evidence node equality
- demonstrated net-balance conservation

The committed SHA-256 values identify the frozen demo files.

`same bytes -> same SHA-256 hash`

Hash equality proves artifact identity.

It does not by itself prove:

- behavioral correctness
- complete conformance
- cross-engine equality
- production safety
- universal financial correctness

---

## 18. Cross-Implementation Limits

The current Python and browser demonstrations are intended to express the same supplied scenario.

Universal equivalence is not established.

Potential divergence areas include:

- Python integers versus JavaScript `Number`
- delimiter-based keys
- locale-sensitive sorting
- malformed values
- unsupported side values
- amount coercion
- identifier encoding

A future conformance profile should define:

- formal schemas
- canonical serialization
- exact amount representation
- byte-wise ordering
- validation rules
- refusal rules
- ruleset versioning
- shared test vectors

---

## 19. Future Proof Obligations

A stronger ORL-Money release should establish and test:

### 19.1 Schema Validity

`validate(input) -> ACCEPTED_INPUT OR REFUSED_INPUT`

### 19.2 Canonicalization

`canonicalize(E_i) = canonicalize(E_j)` for semantically identical supported inputs.

### 19.3 Cross-Language Equality

`F_v_python(B,E) = F_v_browser(B,E)`

for every declared conformance vector.

### 19.4 Permutation Invariance

`for all declared P(E): F_v(B,P(E)) = F_v(B,E)`

### 19.5 Malformed-Input Refusal

Unsupported values must not be silently coerced into a valid state.

### 19.6 Independent Reconstruction

An independent verifier should reconstruct:

- canonical fragment root
- transaction states
- balance effects
- final bounded snapshot
- versioned resolver receipt

### 19.7 Structural Closure

A separate closure model should distinguish:

`resolution_state = RESOLVED | INCOMPLETE | ABSTAIN`

from:

`closure_state = OPEN | SEALED`

A possible future condition is:

`STRUCTURALLY_FINAL iff RESOLVED AND SEALED AND EVIDENCE_ROOT_VERIFIED`

This is not implemented in the current release.

---

## 20. Summary of Justified Current Properties

Under the declared supported model and fixed resolver rules:

### Conditional Determinism

`same supported input + same rules -> same output`

### Same-Evidence Node Equality

`same initial balances + same deduplicated evidence + same rules -> same bounded financial snapshot`

### Exact Duplicate Idempotence

`D(D(E)) = D(E)`

### Intended Arrival-Order Independence

`F_v(B,P(E)) = F_v(B,E)`

for supported permutations of the same fragment content.

### Demonstrated Resolved-Pair Conservation

`sum(resolved_balance_effects) = 0`

### Explicit Non-Effect States

`INCOMPLETE -> no demonstrated balance effect`

`demonstrated ABSTAIN -> no demonstrated balance effect`

These are bounded model properties.

They are not universal financial, security, settlement, or production guarantees.

---

## Scope Note

This sketch applies only to the current ORL-Money reference model and committed scenarios.

It does not replace:

- formal verification
- complete conformance testing
- security review
- financial audit
- accounting validation
- legal review
- regulatory approval
- production engineering

The strongest justified current relation is:

`same initial balances + same deduplicated supported money fragments + same resolver rules -> same bounded transaction states and demonstrated balance projection`
