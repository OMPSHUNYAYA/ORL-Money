# ⭐ FAQ — ORL-Money

**Deterministic Bounded Financial Reconciliation**

ORL-Money is a public deterministic reference model for bounded reconciliation of supported money fragments.

The governing relation is:

`same initial balances + same deduplicated supported money fragments + same resolver rules -> same bounded financial snapshot`

ORL-Money is developed within the Shunyaya Framework.

---

## SECTION A — Purpose and Positioning

### A1. What is ORL-Money?

ORL-Money is a bounded financial-fragment reconciliation reference model.

It classifies supported debit and credit fragments into:

- `RESOLVED`
- `INCOMPLETE`
- `ABSTAIN`

For the supplied scenarios, nodes that hold the same initial balances, the same deduplicated supported fragments, and the same resolver rules produce the same demonstrated transaction states and balance projection.

---

### A2. What problem does ORL-Money explore?

ORL-Money explores how supported financial fragments can be reconciled when systems begin with:

- different local views
- partial visibility
- delayed fragment sharing
- repeated exact duplicates
- inconsistent arrival order
- demonstrated amount or multiplicity conflicts

The current resolver uses fragment content rather than timestamps or fragment arrival position as transaction-classification authority.

---

### A3. What does “order-independent” mean here?

It means that, for the declared supported model, changing the arrival order of the same fragment set is not intended to change the resolver output.

For a supported fragment collection `E`, a supported permutation `P(E)`, and resolver version `v`:

`F_v(B,P(E)) = F_v(B,E)`

Where `B` is the same initial balance snapshot.

This does not mean that all financial systems can eliminate operational ordering.

---

### A4. Is ORL-Money saying that time is irrelevant?

No.

Time can still be useful for:

- user display
- audit history
- deadlines
- monitoring
- legal records
- operations

The narrower claim is that the current resolver does not use timestamps or wall-clock time as transaction-classification authority for the supplied scenarios.

---

### A5. What is the core idea in one line?

`bounded financial resolution = structure + rules + initial balances`

---

### A6. Is ORL-Money a banking system?

No.

It is not:

- a banking core
- a payment network
- a settlement system
- an account-posting engine
- a fraud-control platform
- a production financial service

It is a reference model and demonstration.

---

### A7. Is ORL-Money only relevant to finance?

The current repository is financial in terminology and examples.

The underlying bounded reconciliation pattern may also inform research in:

- record matching
- audit reconstruction
- offline evidence synchronization
- disconnected-system comparison
- discrepancy classification

Those broader uses require their own domain rules and validation.

---

### A8. Does ORL-Money preserve ordinary arithmetic for the supplied resolved transfers?

Yes.

For each demonstrated resolved pair:

`debit_amount = credit_amount`

The balance effects are:

`from_account_delta = -amount`

`to_account_delta = +amount`

Therefore:

`sum(resolved_balance_effects) = 0`

This is demonstrated arithmetic preservation for the committed matching-pair scenarios.

It is not a universal theorem about arbitrary financial systems.

---

### A9. Can ORL-Money be added to existing systems?

Conceptually, it may inform a future reconciliation or audit layer.

The current implementation should not be inserted directly into production financial infrastructure.

Any real integration would require additional:

- input validation
- identity
- authorization
- accounting controls
- security
- networking
- legal review
- regulatory controls
- operational testing

---

## SECTION B — Current Structural Model

### B1. What is a transaction fragment?

The committed demonstrations use entries with four fields:

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

---

### B2. What fragment values are supported?

The current demonstrations expect values shaped like the committed examples.

A formal schema is not yet enforced.

Future hardening should define:

- identifier rules
- supported side values
- amount type
- amount range
- zero-value policy
- negative-value policy
- account-name rules
- malformed-input refusal

---

### B3. When does a transaction become RESOLVED?

For the current supplied model:

`one debit + one credit + matching amount -> RESOLVED`

The resolver then produces a debit effect and a credit effect of equal magnitude.

---

### B4. When does a transaction become INCOMPLETE?

For the current supplied model:

`missing counterpart -> INCOMPLETE`

Examples include:

- a debit with no credit
- a credit with no debit

The resolver does not invent the missing counterpart.

---

### B5. When does a transaction become ABSTAIN?

The supplied scenarios demonstrate `ABSTAIN` for:

- debit-credit amount mismatch
- same-transaction multiplicity conflict

Conceptually:

`debit_credit_mismatch OR demonstrated_same_transaction_multiplicity_conflict -> ABSTAIN`

Other malformed, unsupported, or untested conflict forms are outside the current conformance claim.

---

### B6. What happens to INCOMPLETE and ABSTAIN transactions?

In the committed demonstrations:

`INCOMPLETE -> no demonstrated balance effect`

`ABSTAIN -> no demonstrated balance effect`

Only `RESOLVED` transactions contribute to the demonstrated balance projection.

---

### B7. Why does the resolver not guess missing fragments?

Because the model prefers explicit incompleteness over an invented financial conclusion.

`missing evidence -> INCOMPLETE`

---

### B8. Why does the resolver not automatically repair conflicts?

Because automatic repair would require additional policy, authority, or evidence that the current model does not define.

The current behavior is to classify the demonstrated conflict as `ABSTAIN`.

---

## SECTION C — Initial Balances and Financial Snapshot

### C1. Why are initial balances part of the governing relation?

Because final absolute balances depend on both:

- the initial balance snapshot
- the resolved balance effects

Two nodes with the same fragments but different initial balances would not produce the same final absolute balances.

Therefore the precise relation is:

`same initial balances + same deduplicated fragments + same rules -> same bounded financial snapshot`

---

### C2. What is a bounded financial snapshot?

It is the demonstrated output produced from:

- an initial balance snapshot
- a supported fragment set
- the current resolver rules

The snapshot contains:

- transaction states
- resolved balance effects
- demonstrated final balances
- state counts
- node-equality results

It is not settlement finality.

---

### C3. Does ORL-Money prove money conservation?

It demonstrates net-balance conservation for the committed matching debit-credit scenarios.

For each resolved pair:

`sum(resolved_balance_effects) = 0`

For the supplied examples:

`sum(final_balances) = sum(initial_balances)`

This does not prove universal money conservation under arbitrary inputs or external account-posting systems.

---

### C4. Does ORL-Money verify sufficient funds?

No.

The current resolver does not check:

- available balance
- overdraft limits
- reservations
- holds
- credit limits
- prior authorized commitments

---

### C5. Does ORL-Money move real money?

No.

The current demonstrations only calculate a balance projection.

They do not execute, clear, post, or settle a payment.

---

## SECTION D — Same-Evidence Node Equality

### D1. Why do nodes begin with different data?

Each node represents a system with partial local visibility.

This allows the demonstrations to show the transition from different local views to the same merged evidence.

---

### D2. Do nodes need identical data at the beginning?

No.

The demonstrations intentionally begin with different local fragment sets.

---

### D3. When do nodes produce the same output?

When they hold:

- the same initial balances
- the same deduplicated supported fragment set
- the same resolver rules

Then:

`B_i = B_j AND D(E_i) = D(E_j) -> F_v(B_i,E_i) = F_v(B_j,E_j)`

---

### D4. Does ORL-Money guarantee convergence when nodes permanently hold different evidence?

No.

Same-evidence node equality requires the relevant nodes to hold the same deduplicated supported evidence.

---

### D5. Is continuous communication required?

No continuous connection is required to run the local demonstrations.

However, nodes cannot reach the same evidence state unless the required fragments are eventually shared by some mechanism.

---

### D6. Is a central coordinator required?

The current resolver does not consult coordinator state as transaction-classification authority.

The demonstrations use scripted sharing to distribute fragments.

That script is a test mechanism, not proof that every real network can operate without coordination services.

---

### D7. Does ORL-Money support more than two nodes?

The repository includes a three-node demonstration.

It shows:

- three different starting fragment sets
- two scripted sharing rounds
- same-evidence equality after round 2
- three resolved transactions
- two abstained transactions

This is a bounded demonstration, not a general distributed-systems proof.

---

### D8. Is the sharing mechanism a consensus protocol?

No.

It is not:

- consensus
- reliable broadcast
- Byzantine agreement
- leader election
- network finality
- settlement coordination

It is a deterministic test sequence that merges available fragments.

---

## SECTION E — Exact Duplicate Absorption

### E1. What is exact duplicate absorption?

A fragment with the same:

- transaction identifier
- side
- account
- amount

is treated as the same exact fragment in the committed resolver.

---

### E2. What property does deduplication provide?

Let `D(E)` be exact-duplicate absorption.

Then:

`D(D(E)) = D(E)`

For the committed examples:

`F_v(B,E) = F_v(B,D(E))`

---

### E3. Does exact duplicate absorption prevent all duplicate payments?

No.

It only absorbs identical repeated fragments in the current resolver model.

It is not a complete system for:

- payment replay prevention
- transaction authorization
- double-spend prevention
- nonce control
- idempotency across external systems

---

### E4. What duplicate is shown in the two-node demo?

`M100` contains the same credit fragment twice.

The duplicate is absorbed, and the transaction resolves once.

---

## SECTION F — Demonstration Results

### F1. What does the two-node reference demo contain?

Initial balances:

```text
VillageA = 1000
VillageB = 1000
```

Final expected transaction states:

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

Expected final demonstrated balances:

```text
VillageA = 500
VillageB = 1500
```

Expected node equality:

```text
all_nodes_equal = True
```

---

### F2. What does the three-node demo contain?

Expected final states:

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

---

### F3. What does M400 demonstrate?

M400 contains a debit-credit amount mismatch.

The committed resolver classifies it as:

`ABSTAIN`

It produces no demonstrated balance effect.

---

### F4. What does M500 demonstrate?

M500 contains a same-transaction multiplicity conflict.

The committed resolver classifies it as:

`ABSTAIN`

It is not a complete demonstration of general double-spend prevention.

---

### F5. What does M100 demonstrate?

M100 demonstrates:

- a matching debit-credit pair
- exact duplicate absorption
- one resolved balance transfer
- identical output after the nodes hold the same evidence

---

### F6. What do M200 and M300 demonstrate in the two-node demo?

They each lack a counterpart.

They remain:

`INCOMPLETE`

They produce no demonstrated balance effect.

---

## SECTION G — Determinism and Order Independence

### G1. Is ORL-Money deterministic?

For unchanged supported inputs and unchanged resolver rules, the current implementation produces repeatable output.

---

### G2. What is the current determinism condition?

`same supported input + same resolver rules -> same demonstrated output`

For the full financial snapshot:

`same initial balances + same deduplicated supported fragments + same rules -> same bounded financial snapshot`

---

### G3. Will all independent implementations necessarily match today?

Not automatically.

Independent implementations can diverge unless they also share:

- a formal input schema
- canonical serialization
- exact amount representation
- deterministic ordering rules
- identical validation and refusal behavior
- a versioned ruleset
- conformance vectors

Those are future technical targets.

---

### G4. Is the Python implementation guaranteed to match the browser implementation for every possible input?

No.

The current examples are intended to match, but universal cross-language equivalence is not established.

Potential divergence areas include:

- Python integers versus JavaScript `Number`
- delimiter-based keys
- locale-sensitive ordering
- unsupported input handling
- malformed values

---

### G5. Is the current arrival-order law fully tested?

No.

The intended invariant is documented:

`F_v(B,P(E)) = F_v(B,E)`

A future release should test it across:

- many permutations
- malformed vectors
- adversarial vectors
- cross-language vectors

---

### G6. Is ORL-Money probabilistic?

No probabilistic or heuristic rule is used in the current resolver.

That does not by itself establish complete correctness or conformance.

---

## SECTION H — Safety and Current Limitations

### H1. Does ORL-Money validate hostile or malformed input?

Not completely.

The current demonstrations were designed around committed example data, not arbitrary hostile input.

---

### H2. What important validations are missing?

The current implementation does not fully enforce:

- non-negative amounts
- zero-value policy
- numeric amount types
- exact decimal representation
- supported side values
- safe identifier syntax
- account-name constraints
- self-transfer policy
- sufficient-funds policy
- transaction authorization

---

### H3. Can negative amounts cause incorrect behavior?

The current resolver does not reject them.

This is one reason the demonstrations must be treated as bounded reference scenarios rather than production financial software.

---

### H4. Can malformed values cause runtime errors?

Some malformed or non-numeric values may not be handled safely.

Explicit invalid-input refusal is a future hardening requirement.

---

### H5. Does ABSTAIN cover every possible conflict?

No.

It covers the conflict forms demonstrated by the committed scenarios.

Other conflict forms remain untested or unsupported.

---

### H6. Can an ABSTAIN state later become RESOLVED?

The current demonstrations do not define a conflict-repair authority or lifecycle.

A future system could define a new validated evidence set and rerun a versioned resolver, but that process is outside the current model.

---

### H7. Can an INCOMPLETE state later become RESOLVED?

Yes, within the demonstrated model, if the missing supported counterpart later becomes available and the resulting structure matches the resolver rules.

---

### H8. Does ORL-Money prevent fraud?

No.

It does not establish:

- identity
- authorization
- ownership
- intent
- legal validity
- source-of-funds legitimacy
- fraud detection

---

### H9. Does ORL-Money prevent double spending?

No complete double-spend prevention claim is made.

The demonstrations only show exact duplicate absorption and one same-transaction multiplicity conflict.

---

## SECTION I — Verification

### I1. How can the reference demo be run?

```text
python demo/orl_money_demo_reference.py
```

---

### I2. How can the multi-node demo be run?

```text
python demo/orl_money_demo_multinode.py
```

---

### I3. What should be checked in the reference demo?

Check the documented expected:

- transaction states
- state summary
- resolved balance effects
- final demonstrated balances
- node equality
- net resolved balance delta

---

### I4. What should be checked in the multi-node demo?

Check the documented expected:

- round-by-round equality status
- final transaction states
- final state summary
- final demonstrated balances
- money-conservation result
- `round_2_match = True`

---

### I5. What do the SHA-256 hashes prove?

The committed SHA-256 values identify the frozen demo files.

`same bytes -> same SHA-256 hash`

A successful comparison proves artifact identity.

---

### I6. What do the hashes not prove?

They do not by themselves prove:

- behavioral correctness
- complete conformance
- cross-engine equality
- production safety
- universal financial correctness
- security
- settlement validity

---

### I7. Is the GitHub Actions workflow a complete conformance suite?

No.

The current workflow should be understood as reference-demo execution unless and until it asserts a complete declared vector set.

---

## SECTION J — Practical Use and Research Direction

### J1. What is a reasonable current use?

The current repository is suitable for:

- education
- research
- inspection
- deterministic scenario replay
- model discussion
- future conformance design

---

### J2. What areas may benefit from the underlying idea?

Possible research directions include:

- back-office discrepancy classification
- offline evidence synchronization
- deterministic audit reconstruction
- disconnected-system comparison
- canonical financial-fragment exchange
- independently verifiable resolver receipts

These are directions, not production claims.

---

### J3. Is ORL-Money ready for real payments?

No.

The current demonstrations should not be used to move real money.

---

### J4. What would a real deployment require?

At minimum:

- formal schemas
- explicit refusal rules
- exact decimal or integer amount representation
- authentication
- authorization
- account ownership
- sufficient-funds checks
- accounting controls
- secure transport
- replay protection
- audit controls
- operational monitoring
- legal review
- regulatory compliance
- production testing

---

### J5. Does ORL-Money replace existing financial infrastructure?

No.

It is a reference model that may inform later reconciliation designs.

---

## SECTION K — Comparison Questions

### K1. Is ORL-Money a blockchain?

No.

It does not provide:

- a blockchain
- distributed consensus
- immutable ordering
- proof of work
- proof of stake
- chain finality

---

### K2. Is ORL-Money an eventual-consistency protocol?

No.

It does not define a general replica protocol.

It demonstrates that nodes with the same deduplicated supported evidence and rules produce the same bounded resolver snapshot.

---

### K3. Is ORL-Money a classical reconciliation engine?

It is a simplified reference model for structural classification and balance projection.

It does not include the full controls of a production reconciliation engine.

---

### K4. Does ORL-Money prove that order is unnecessary in finance?

No.

It demonstrates that fragment arrival order is not used as transaction-classification authority in the supplied resolver scenarios.

Many financial operations still require sequencing, authorization, posting order, legal time, and settlement rules.

---

### K5. Does ORL-Money prove that clocks are unnecessary in finance?

No.

It demonstrates that the current bounded resolver does not require timestamps or wall-clock time to classify the supplied fragments.

---

## SECTION L — Boundaries

### L1. What does ORL-Money not implement or prove?

ORL-Money does not implement or prove:

- universal financial correctness
- universal order independence
- universal time independence
- authorization
- identity or ownership
- sufficient funds
- account posting
- payment execution
- clearing
- settlement
- finality
- fraud prevention
- cryptographic security
- consensus
- Byzantine fault tolerance
- reliable broadcast
- complete double-spend prevention
- complete malformed-input validation
- regulatory compliance
- production readiness
- safe operation on arbitrary input

---

### L2. Is the model anti-time or anti-order?

No.

It separates the resolver's bounded classification rule from timestamp and fragment-arrival authority.

Time and order may remain important elsewhere in a complete system.

---

### L3. Is continuous connectivity unnecessary in every sense?

No.

The demos run locally after download and do not require a live service.

However, nodes need some eventual mechanism to exchange evidence if they are to reach the same evidence state.

---

### L4. Is “final truth” an appropriate description?

No.

The more precise term is:

`bounded financial snapshot`

The current result is a deterministic resolver output for the declared inputs and rules, not universal financial truth or settlement finality.

---

### L5. Is “financial correctness” an appropriate universal claim?

No.

The current repository demonstrates bounded structural classification and balance projection for supplied scenarios.

---

## SECTION M — Future Technical Direction

### M1. What should the next technical revision add?

A stronger revision should add:

- a formal supported-input schema
- explicit invalid-input refusal
- amount-domain rules
- exact cross-language amount representation
- canonical serialization
- delimiter-safe identifiers
- deterministic byte-wise ordering
- assertion-based expected outputs
- permutation vectors
- malformed-input vectors
- adversarial conflict vectors
- Python and browser conformance tests
- versioned resolver receipts
- independent reconstruction
- structural-closure semantics

---

### M2. What is the future target relation?

`same validated initial balances + same validated canonical money fragments + same ruleset version -> same independently verified bounded financial snapshot`

---

### M3. Is that stronger target already implemented?

No.

It is a future technical direction.

---

## SECTION N — Skeptical Questions

### N1. Is this just waiting for more data?

Not exactly.

The model explicitly distinguishes:

- structurally resolvable
- incomplete
- demonstrated conflict

However, missing evidence may remain `INCOMPLETE` until more supported evidence becomes available.

---

### N2. Is the current result merely a set union?

The sharing step uses duplicate-absorbing union, but the output also depends on deterministic transaction classification and balance projection rules.

---

### N3. Could the same idea be implemented without the ORL-Money name?

Yes.

The repository is a reference model and naming framework, not a claim of exclusivity over reconciliation logic.

---

### N4. Could the current demos fail on real-world data?

Yes.

Real-world financial data is broader, more adversarial, and more regulated than the supplied scenarios.

---

### N5. Why are the demonstrations small?

The small scenarios make the resolver behavior inspectable.

They are not presented as scale benchmarks.

---

### N6. Does deterministic output imply correct output?

No.

Determinism means the same declared inputs and rules produce the same output.

Correctness also depends on:

- valid inputs
- correct rules
- appropriate domain assumptions
- complete evidence
- correct implementation

---

### N7. Is same-evidence equality the same as consensus?

No.

Consensus concerns how distributed participants agree under a defined network and fault model.

Same-evidence equality concerns deterministic output after the nodes already hold the same supported evidence and rules.

---

### N8. What is the most conservative interpretation of ORL-Money?

A compact deterministic reference model for classifying supported debit-credit fragments and projecting balances without using timestamps or fragment arrival position as classification authority.

---

### N9. What is the strongest justified current interpretation?

For the committed scenarios:

`same initial balances + same deduplicated supported money fragments + same resolver rules -> same bounded transaction states and balance projection`

---

## ⭐ Final One-Line Summary

ORL-Money is a public deterministic reference model showing that nodes can begin with different supported money fragments and, after receiving the same deduplicated evidence under the same resolver rules and initial balances, produce the same bounded transaction states and demonstrated balance projection without using timestamps or fragment arrival order as classification authority, while leaving authorization, payment execution, settlement, consensus, finality, and production safety outside the current implementation.
