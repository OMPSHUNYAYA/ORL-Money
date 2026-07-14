# ⭐ ORL-Money — Test Guide

**Deterministic Bounded Financial Reconciliation**

This guide explains how to run and inspect the current ORL-Money reference demonstrations.

The governing relation is:

`same initial balances + same deduplicated supported money fragments + same resolver rules -> same bounded financial snapshot`

ORL-Money is developed within the Shunyaya Framework.

---

## 1. Verification Scope

The current demonstrations are designed to show:

- different initial node views
- exact duplicate absorption
- deterministic classification of supported fragments
- explicit `RESOLVED`, `INCOMPLETE`, and demonstrated `ABSTAIN` outcomes
- balance effects only for `RESOLVED` transactions
- same-evidence node equality
- demonstrated net-balance conservation for matching debit-credit pairs
- local execution without GPS, NTP, database access, or a live server after download

The demonstrations do not prove:

- authorization
- identity or account ownership
- available funds
- payment execution
- account posting
- clearing or settlement
- immutable finality
- fraud prevention
- consensus
- reliable broadcast
- complete double-spend prevention
- complete malformed-input validation
- production readiness
- universal financial correctness
- universal order independence

---

## 2. Repository Demonstrations

The repository contains three demonstrations:

### Browser Demonstration

`demo/orl_money_demo_v1.html`

### Two-Node Python Reference Demonstration

`demo/orl_money_demo_reference.py`

### Three-Node Python Demonstration

`demo/orl_money_demo_multinode.py`

The browser and two-node Python demonstrations use the same main scenario.

The three-node Python demonstration uses a separate multi-round scenario.

---

## 3. Quick Browser Test

Open:

`demo/orl_money_demo_v1.html`

Then select:

**Run Full Demo**

The browser demonstration moves through:

1. local fragmentation
2. bounded structural sharing
3. final same-evidence equality

No installation or server is required.

---

## 4. Browser Controls

### Next Step

Moves forward by one stage.

Use it to inspect the transition between:

- different local fragment sets
- shared evidence
- identical resolver snapshots

### Run Full Demo

Runs the staged demonstration automatically.

### Reset

Returns the browser demonstration to its initial local views.

### Jump to Final Equality

Moves directly to the stage where both nodes hold the same merged fragment set.

This is a convenience control.

It is not a network, consensus, or settlement operation.

---

## 5. Browser Stage 1 — Local Fragmentation

At the initial stage, Node A and Node B hold different supported fragments.

Node A begins with debit-side fragments.

Node B begins with credit-side fragments, including one exact duplicate.

Because the nodes hold materially different evidence, their local resolver snapshots are not expected to match.

Observe:

- different visible fragment collections
- different local transaction states
- `MATCH = FALSE`
- no claim of shared finality
- incomplete local evidence

This stage demonstrates partial visibility, not failure.

---

## 6. Browser Stage 2 — Bounded Structural Sharing

The browser merges the available fragments into each node's local evidence set.

The sharing operation is a scripted test mechanism.

It demonstrates:

- duplicate-absorbing fragment union
- increased evidence visibility
- deterministic reclassification
- visibility of matching, missing, and conflicting fragment patterns

It does not demonstrate:

- reliable broadcast
- consensus
- adversarial networking
- delivery guarantees
- settlement coordination

---

## 7. Browser Stage 3 — Same-Evidence Equality

At the final stage, both nodes hold the same deduplicated supported fragment set and use the same resolver rules.

Expected result:

`MATCH = TRUE`

Both nodes should show the same:

- transaction states
- state summary
- resolved balance effects
- final demonstrated balances

The correct interpretation is:

`same evidence + same rules + same initial balances -> same bounded financial snapshot`

The result is not universal financial truth or settlement finality.

---

## 8. Two-Node Scenario Inputs

Initial balances:

```text
VillageA = 1000
VillageB = 1000
```

Node A begins with:

```text
M100 debit  VillageA 500
M300 debit  VillageA 120
M400 debit  VillageA 400
M500 debit  VillageA 250
```

Node B begins with:

```text
M100 credit VillageB     500
M100 credit VillageB     500
M200 credit VillageB     300
M400 credit VillageB     450
M500 credit VillageB     250
M500 credit VillageB_Alt 250
```

The second `M100` credit is an exact duplicate.

---

## 9. Two-Node Expected Transaction States

After both nodes hold the same merged supported fragment set:

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

Equivalent compact summary:

`R:1 I:2 A:2`

---

## 10. Two-Node Expected Balance Results

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

Expected total balance check:

```text
total_money_initial = 2000
total_money_final   = 2000
```

Expected net resolved balance delta:

```text
net_resolved_balance_delta = 0
```

Expected equality result:

```text
all_nodes_equal = True
```

---

## 11. Two-Node Transaction Interpretation

### M100 — Matching Pair and Exact Duplicate Absorption

M100 contains:

- one debit of `500`
- two identical copies of the same credit of `500`

The exact duplicate is absorbed.

Expected result:

`M100 -> RESOLVED`

Expected effect:

```text
VillageA = -500
VillageB = +500
```

This demonstrates exact-fragment deduplication.

It does not demonstrate complete payment replay or double-spend prevention.

---

### M200 — Missing Debit

M200 contains a credit but no debit.

Expected result:

`M200 -> INCOMPLETE`

Expected balance effect:

`0`

---

### M300 — Missing Credit

M300 contains a debit but no credit.

Expected result:

`M300 -> INCOMPLETE`

Expected balance effect:

`0`

---

### M400 — Amount Mismatch

M400 contains:

```text
debit  = 400
credit = 450
```

Expected result:

`M400 -> ABSTAIN`

Expected balance effect:

`0`

---

### M500 — Same-Transaction Multiplicity Conflict

M500 contains one debit and two different credit-account claims.

Expected result:

`M500 -> ABSTAIN`

Expected balance effect:

`0`

This is a demonstrated multiplicity conflict.

It is not a complete demonstration of general double-spend prevention.

---

## 12. Run the Two-Node Python Demonstration

From the repository root:

```text
python demo/orl_money_demo_reference.py
```

Check the output for:

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

Also check:

```text
state_summary = {'ABSTAIN': 2, 'INCOMPLETE': 2, 'RESOLVED': 1}
```

Dictionary display order may depend on the committed implementation, but the counts must match.

---

## 13. Three-Node Scenario

Run:

```text
python demo/orl_money_demo_multinode.py
```

Initial balances:

```text
VillageA = 1000
VillageB = 1000
VillageC = 1000
```

The three nodes begin with different supported fragment sets.

They exchange fragments through two scripted rounds.

---

## 14. Three-Node Expected Transaction States

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

Equivalent compact summary:

`R:3 I:0 A:2`

---

## 15. Three-Node Expected Balance Results

Expected final demonstrated balances:

```text
VillageA = 650
VillageB = 1300
VillageC = 1050
```

Expected total balance check:

```text
total_money_initial = 3000
total_money_final   = 3000
```

Expected net resolved balance delta:

```text
net_resolved_balance_delta = 0
```

Expected equality progression:

```text
before_match  = False
round_1_match = False
round_2_match = True
```

The important result is:

```text
round_2_match = True
```

---

## 16. What the Three-Node Demonstration Shows

The three-node scenario demonstrates:

- different starting fragment sets
- deterministic fragment absorption
- two scripted sharing rounds
- incomplete transactions becoming resolved after receiving matching counterparts
- demonstrated conflicts remaining abstained
- same-evidence equality after round 2
- net-zero resolved balance effects
- preservation of the demonstrated total balance

It does not prove general multi-node convergence under arbitrary network conditions.

---

## 17. State Definitions

### RESOLVED

For the current supplied model:

`one debit + one credit + matching amount -> RESOLVED`

A `RESOLVED` transaction contributes to the demonstrated balance projection.

`RESOLVED` does not mean:

- authorized
- funded
- posted
- cleared
- settled
- immutable
- globally complete

---

### INCOMPLETE

For the current supplied model:

`missing counterpart -> INCOMPLETE`

Expected demonstrated balance effect:

`0`

An `INCOMPLETE` state may become `RESOLVED` if a matching supported counterpart later becomes available.

---

### ABSTAIN

The committed scenarios demonstrate `ABSTAIN` for:

- amount mismatch
- same-transaction multiplicity conflict

Expected demonstrated balance effect:

`0`

The current model does not define a complete conflict-repair lifecycle.

---

## 18. Exact Duplicate Test

The committed two-node scenario includes the same `M100` credit twice.

Expected behavior:

```text
node_b_raw_fragments    = 6
node_b_unique_fragments = 5
```

Expected transaction result:

`M100 -> RESOLVED`

The duplicate must not create an additional balance effect.

The justified property is:

`D(D(E)) = D(E)`

and, for the supplied example:

`F_v(B,E) = F_v(B,D(E))`

---

## 19. Repeatability Test

Run each Python demonstration multiple times without modifying the code or scenario data.

Expected observations:

- identical transaction states
- identical state counts
- identical resolved balance effects
- identical final demonstrated balances
- identical node-equality results
- identical total-balance checks

This establishes repeatability for the unchanged supplied scenario.

It does not establish universal cross-platform or cross-implementation conformance.

---

## 20. Manual Arrival-Order Check

The intended current-model invariant is:

`F_v(B,P(E)) = F_v(B,E)`

where `P(E)` is a supported permutation containing the same fragment content.

A simple manual check can be performed by reordering committed fragment entries without changing their values.

Expected result:

- transaction states remain unchanged
- balance effects remain unchanged
- final demonstrated balances remain unchanged

This is an informal test.

A future release should include an automated permutation corpus.

---

## 21. Evidence-Growth Test

The model is not acceptance-monotonic.

Adding evidence can produce:

`INCOMPLETE -> RESOLVED`

It can also produce:

`RESOLVED -> ABSTAIN`

if later evidence introduces a demonstrated multiplicity conflict.

Therefore, do not interpret a local `RESOLVED` state as immutable finality.

---

## 22. Browser Certificate Labels

The current browser interface includes certificate-style labels such as:

- Match
- Money Conserved
- No Duplication
- No False Movement

These labels must be interpreted narrowly.

### Match

Means that the two browser nodes currently produce identical resolver snapshots.

### Money Conserved

Means that the demonstrated final balance total equals the demonstrated initial balance total for the supplied matching-pair scenario.

### No Duplication

Means that the committed exact duplicate does not create an additional demonstrated balance effect.

It does not prove complete duplicate-payment or double-spend prevention.

### No False Movement

Means that the demonstrated `INCOMPLETE` and `ABSTAIN` transactions produce no balance effect in the supplied scenario.

It does not establish authorization, fraud prevention, or universal financial safety.

---

## 23. No-Time and No-Arrival-Order Check

Inspect the current resolver path.

For the supplied scenarios, transaction classification does not consult:

- timestamps
- wall-clock time
- GPS
- NTP
- fragment arrival position
- coordinator state

This is a bounded implementation observation.

It does not mean time, order, or coordination are unnecessary in every financial system component.

---

## 24. Current Input Limitations

The current demonstrations do not fully reject or define:

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

Do not treat successful execution on the committed examples as proof of safe behavior on arbitrary inputs.

---

## 25. Cross-Language Limitations

The Python and browser demonstrations are intended to express the same supplied scenario.

Universal equality is not established.

Potential divergence areas include:

- Python integers versus JavaScript `Number`
- delimiter-based fragment keys
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

## 26. SHA-256 Artifact Identity

Follow:

`verify/VERIFY.txt`

Compare the committed demo files against:

`verify/FREEZE_DEMO_SHA256.txt`

The applicable relation is:

`same bytes -> same SHA-256 hash`

A matching hash proves that the local file bytes match the frozen artifact.

It does not by itself prove:

- expected behavioral output
- complete conformance
- cross-engine equality
- security
- financial correctness
- production safety

---

## 27. GitHub Actions Scope

The GitHub Actions workflow should be understood as a reference-demo execution workflow unless it explicitly asserts all documented expected values.

A successful workflow run does not automatically establish:

- complete conformance
- universal order independence
- malformed-input safety
- cross-language equivalence
- settlement validity
- production readiness

---

## 28. Recommended Test Sequence

### Step 1 — Browser Demonstration

Open:

`demo/orl_money_demo_v1.html`

Select:

**Run Full Demo**

Confirm:

- different local views at the start
- final `MATCH = TRUE`
- expected final balances
- expected state counts

### Step 2 — Two-Node Python Demonstration

Run:

```text
python demo/orl_money_demo_reference.py
```

Confirm:

```text
all_nodes_equal = True
total_money_initial = 2000
total_money_final = 2000
```

Confirm:

```text
R:1 I:2 A:2
```

### Step 3 — Three-Node Python Demonstration

Run:

```text
python demo/orl_money_demo_multinode.py
```

Confirm:

```text
round_2_match = True
total_money_initial = 3000
total_money_final = 3000
```

Confirm:

```text
R:3 I:0 A:2
```

### Step 4 — Artifact Identity

Compare the demo hashes using:

`verify/VERIFY.txt`

---

## 29. Pass Criteria

The current supplied release passes its documented scenario check when:

### Two-Node Scenario

```text
M100 = RESOLVED
M200 = INCOMPLETE
M300 = INCOMPLETE
M400 = ABSTAIN
M500 = ABSTAIN
```

```text
VillageA = 500
VillageB = 1500
```

```text
all_nodes_equal = True
total_money_initial = 2000
total_money_final = 2000
net_resolved_balance_delta = 0
```

### Three-Node Scenario

```text
M100 = RESOLVED
M200 = RESOLVED
M300 = RESOLVED
M400 = ABSTAIN
M500 = ABSTAIN
```

```text
VillageA = 650
VillageB = 1300
VillageC = 1050
```

```text
round_2_match = True
total_money_initial = 3000
total_money_final = 3000
net_resolved_balance_delta = 0
```

### Artifact Identity

Every frozen file hash matches the committed value.

---

## 30. Failure Conditions

Treat the current supplied scenario check as failed if any of the following occurs:

- a committed demo does not execute
- a documented transaction state differs
- a documented final balance differs
- the two-node equality check is false after sharing
- the three-node equality check is false after round 2
- the total demonstrated balance changes
- an `INCOMPLETE` or `ABSTAIN` transaction produces a balance effect
- the committed frozen hash does not match the local file

A failed check indicates either:

- modified artifacts
- implementation drift
- environment incompatibility
- documentation mismatch
- an implementation defect

It does not by itself identify the cause.

---

## 31. Future Test Expansion

A stronger release should add automated tests for:

- all declared scenario outputs
- fragment permutations
- exact duplicates
- amount mismatches
- debit multiplicity
- credit multiplicity
- unsupported side values
- zero amounts
- negative amounts
- malformed amounts
- unsafe identifiers
- self-transfers
- very large exact amounts
- Python-browser equality
- canonical serialization
- independent reconstruction
- versioned resolver receipts
- structural closure

Future target relation:

`same validated initial balances + same validated canonical money fragments + same ruleset version -> same independently verified bounded financial snapshot`

This stronger target is not part of the current demonstrations.

---

## ⭐ Final Test Summary

The current ORL-Money demonstrations should be interpreted as bounded reference scenarios.

They show that, for the committed supported inputs:

`same initial balances + same deduplicated supported money fragments + same resolver rules -> same bounded transaction states and demonstrated balance projection`

The tests do not establish authorization, payment execution, settlement, consensus, immutable finality, universal financial correctness, or production safety.
