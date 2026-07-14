# ⭐ ORL-Money — Quickstart

**Deterministic Bounded Financial Reconciliation**

ORL-Money is a public deterministic reference model for bounded reconciliation of supported money fragments.

The governing relation is:

`same initial balances + same deduplicated supported money fragments + same resolver rules -> same bounded financial snapshot`

ORL-Money is developed within the Shunyaya Framework.

---

## 1. Run the Two-Node Reference Demo

From the repository root:

```text
python demo/orl_money_demo_reference.py
```

The demo uses:

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
R:1 I:2 A:2
```

Expected final demonstrated balances:

```text
VillageA = 500
VillageB = 1500
```

Expected equality result:

```text
all_nodes_equal = True
```

---

## 2. Open the Browser Demo

Open:

`demo/orl_money_demo_v1.html`

Then select:

**Run Full Demo**

The browser demonstration moves through:

1. local fragmentation
2. bounded structural sharing
3. final same-evidence equality

Expected final browser result:

```text
MATCH = TRUE
```

The browser and two-node Python demonstrations use the same main scenario.

---

## 3. Run the Three-Node Demo

From the repository root:

```text
python demo/orl_money_demo_multinode.py
```

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
R:3 I:0 A:2
```

Expected final demonstrated balances:

```text
VillageA = 650
VillageB = 1300
VillageC = 1050
```

Expected equality progression:

```text
before_match  = False
round_1_match = False
round_2_match = True
```

The two sharing rounds are a scripted test sequence.

They are not a consensus, reliable-broadcast, networking, or settlement protocol.

---

## 4. Core Resolution Model

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

For the current supplied model:

`one debit + one credit + matching amount -> RESOLVED`

`missing counterpart -> INCOMPLETE`

`debit_credit_mismatch OR demonstrated_same_transaction_multiplicity_conflict -> ABSTAIN`

Only `RESOLVED` transactions contribute to the demonstrated balance projection.

---

## 5. Meaning of the Three States

### RESOLVED

A supported transaction has:

- one debit
- one credit
- matching amounts

The resolver applies equal and opposite balance effects.

`from_account_delta = -amount`

`to_account_delta = +amount`

### INCOMPLETE

A supported transaction is missing its debit or credit counterpart.

Expected demonstrated balance effect:

`0`

### ABSTAIN

The committed scenarios demonstrate `ABSTAIN` for:

- debit-credit amount mismatch
- same-transaction multiplicity conflict

Expected demonstrated balance effect:

`0`

`ABSTAIN` is a bounded resolver classification.

It is not settlement rejection, fraud detection, or legal invalidation.

---

## 6. Exact Duplicate Absorption

The two-node scenario includes the same `M100` credit fragment twice.

The duplicate key is:

`(tx, side, account, amount)`

Expected behavior:

```text
node_b_raw_fragments    = 6
node_b_unique_fragments = 5
```

The exact duplicate does not create an additional balance effect.

The justified relation is:

`D(D(E)) = D(E)`

This is exact-fragment deduplication.

It is not complete payment replay or double-spend prevention.

---

## 7. Same-Evidence Equality

Let:

- `B` be an initial balance snapshot
- `E` be a supported money-fragment collection
- `D(E)` be exact-duplicate absorption
- `F_v(B,E)` be the resolver snapshot under ruleset version `v`

For two nodes:

`B_i = B_j AND D(E_i) = D(E_j) -> F_v(B_i,E_i) = F_v(B_j,E_j)`

This means nodes with the same initial balances, same deduplicated supported evidence, and same resolver rules produce the same bounded output.

ORL-Money does not claim that nodes with permanently different evidence must produce the same result.

---

## 8. Arrival-Order Independence

For a supported permutation `P(E)` of the same fragment content, the intended current-model invariant is:

`F_v(B,P(E)) = F_v(B,E)`

The current resolver classifies fragments from their content rather than their arrival position.

A future stronger release should test this across an automated permutation corpus and cross-language conformance vectors.

---

## 9. Demonstrated Balance Preservation

For each demonstrated resolved pair:

`debit_amount = credit_amount = x`

Therefore:

`(-x) + (+x) = 0`

Across all demonstrated resolved pairs:

`sum(resolved_balance_effects) = 0`

For the supplied scenarios:

`sum(final_balances) = sum(initial_balances)`

This is demonstrated net-balance conservation for matching debit-credit pairs.

It is not a universal money-conservation theorem.

---

## 10. What to Check in the Two-Node Demo

Run:

```text
python demo/orl_money_demo_reference.py
```

Confirm:

```text
all_nodes_equal            = True
money_conserved            = True
duplicate_safe             = True
no_loss_forced             = True
mismatch_contained         = True
conflict_contained         = True
total_money_initial        = 2000
total_money_final          = 2000
net_resolved_balance_delta = 0
```

Also confirm:

```text
state_summary = {'ABSTAIN': 2, 'INCOMPLETE': 2, 'RESOLVED': 1}
```

---

## 11. What to Check in the Three-Node Demo

Run:

```text
python demo/orl_money_demo_multinode.py
```

Confirm:

```text
round_2_match              = True
money_conserved            = True
total_money_initial        = 3000
total_money_final          = 3000
net_resolved_balance_delta = 0
```

Confirm the final state summary:

```text
R:3 I:0 A:2
```

---

## 12. Repeatability Check

Run each Python demonstration multiple times without modifying the source or scenario data.

Expected observations:

- identical transaction states
- identical state summaries
- identical balance effects
- identical final demonstrated balances
- identical node-equality results
- identical total-balance checks

This establishes repeatability for the unchanged supplied scenarios.

It does not establish universal cross-platform or independent-implementation conformance.

---

## 13. Artifact Identity Check

Follow:

`verify/VERIFY.txt`

Compare the committed files against:

`verify/FREEZE_DEMO_SHA256.txt`

The applicable relation is:

`same bytes -> same SHA-256 hash`

A matching hash proves artifact identity.

It does not by itself prove:

- expected behavioral output
- complete conformance
- cross-engine equality
- financial correctness
- security
- production safety

---

## 14. Minimum Requirements

For the Python demonstrations:

- Python 3.9 or later
- Python standard library
- no external Python package required

For the browser demonstration:

- a modern browser
- no server required
- no live internet connection required after download

The demos do not require GPS, NTP, a database, or a remote service to execute locally.

---

## 15. Repository Structure

```text
ORL-Money/
├── README.md
├── LICENSE
├── demo/
│   ├── orl_money_demo_reference.py
│   ├── orl_money_demo_multinode.py
│   └── orl_money_demo_v1.html
├── docs/
│   ├── FAQ.md
│   ├── Quickstart.md
│   ├── Test-Guide.md
│   ├── Proof-Sketch.md
│   └── ORL-Money-Structural-Overview.png
└── verify/
    ├── VERIFY.txt
    └── FREEZE_DEMO_SHA256.txt
```

---

## 16. What the Current Demonstrations Establish

For the committed scenarios, ORL-Money demonstrates:

- different initial node views
- deterministic output under unchanged supported inputs
- same-evidence node equality
- exact duplicate absorption
- explicit incompleteness
- abstention for the demonstrated amount mismatch
- abstention for the demonstrated multiplicity conflict
- no balance effect from demonstrated `INCOMPLETE` or `ABSTAIN` transactions
- net-zero resolved balance effects for matching debit-credit pairs
- no use of timestamps or fragment arrival position as classification authority
- local execution without GPS, NTP, database access, or a live server after download

These are bounded scenario claims.

---

## 17. What ORL-Money Does Not Establish

The current demonstrations do not implement or prove:

- authorization
- identity or account ownership
- available-funds verification
- overdraft policy
- account posting
- payment execution
- clearing or settlement
- immutable finality
- fraud prevention
- cryptographic signatures
- consensus
- Byzantine fault tolerance
- reliable broadcast
- complete double-spend prevention
- complete malformed-input validation
- regulatory compliance
- production readiness
- universal financial correctness
- universal order independence
- safe operation on arbitrary or hostile input

The current demonstrations should not be used to move real money.

---

## 18. Current Input Limitations

The current implementations do not fully reject or define:

- negative amounts
- zero amounts
- malformed amount types
- unsupported side values
- unsafe identifiers
- delimiter collisions
- self-transfers
- insufficient funds
- unauthorized accounts
- hostile input

Use only the committed supported scenarios when verifying the current release.

---

## 19. Cross-Language Limitations

The Python and browser implementations are intended to express the same supplied two-node scenario.

Universal equivalence is not established.

Potential divergence areas include:

- Python integers versus JavaScript `Number`
- delimiter-based keys
- locale-sensitive sorting
- malformed-value handling
- implicit numeric conversion
- identifier encoding

A future conformance release should define:

- formal schemas
- canonical serialization
- exact amount representation
- byte-wise ordering
- refusal rules
- shared vectors
- assertion-based Python and browser tests

---

## 20. Future Technical Direction

A stronger revision should add:

- a formal supported-input schema
- explicit invalid-input refusal
- non-negative and domain-specific amount rules
- exact cross-language amount representation
- canonical serialization
- delimiter-safe identifiers
- deterministic byte-wise ordering
- assertion-based expected outputs
- permutation vectors
- malformed-input vectors
- adversarial conflict vectors
- Python-browser conformance tests
- versioned resolver receipts
- independent reconstruction
- a separately defined structural-closure layer

Future target relation:

`same validated initial balances + same validated canonical money fragments + same ruleset version -> same independently verified bounded financial snapshot`

This stronger target is not part of the current demonstrations.

---

## ⭐ One-Line Summary

ORL-Money is a public deterministic reference model showing that nodes can begin with different supported money fragments and, after receiving the same deduplicated evidence under the same resolver rules and initial balances, produce the same bounded transaction states and demonstrated balance projection without using timestamps or fragment arrival order as classification authority, while leaving authorization, payment execution, settlement, consensus, finality, and production safety outside the current implementation.
