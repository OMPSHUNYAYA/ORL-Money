# ⭐ ORL-Money

## **Deterministic Bounded Financial Reconciliation**

![ORL-Money](https://img.shields.io/badge/ORL--Money-Bounded%20Financial%20Reconciliation-black)
![Version](https://img.shields.io/badge/Version-2.1.0-blue)
![Python Audit](https://img.shields.io/badge/Python%20Audit-451%2F451%20PASS-green)
![Browser Audit](https://img.shields.io/badge/Browser%20Audit-487%2F487%20PASS-green)
![Parity](https://img.shields.io/badge/Python%20%2F%20Browser%20Parity-36%2F36%20PASS-green)
![Independent Verifier](https://img.shields.io/badge/Independent%20Verifier-85%2F85%20PASS-green)
![Frozen Corpus](https://img.shields.io/badge/Frozen%20Corpus-4%2F4%20PASS-green)
![Canonical Corpus](https://img.shields.io/badge/Canonical%20Corpus-Strict%20Verification%20PASS-green)
![Exact Money](https://img.shields.io/badge/Money-Exact%20Integer%20Strings-purple)
![Orderless Resolution](https://img.shields.io/badge/Arrival%20Order-Not%20Resolution%20Authority-lightgrey)
![Open Use](https://img.shields.io/badge/Reference%20Implementation-Open%20Use-blue)

[![Deterministic Verification](https://github.com/OMPSHUNYAYA/ORL-Money/actions/workflows/orl-money-verify.yml/badge.svg)](https://github.com/OMPSHUNYAYA/ORL-Money/actions/workflows/orl-money-verify.yml)

**Validated financial observations become canonical claims. Canonical claims become witness-carrying transaction receipts. Resolved structure becomes an inspectable financial projection.**

ORL-Money v2.1.0 is a deterministic reference architecture for bounded reconciliation of validated balance records, money claims, observation provenance, transaction structure, and structural projections.

The governing relation is:

`same validated balance basis + same canonical money claim set + same ruleset + same compatibility profile + same boundary declaration -> same bounded financial resolution`

ORL-Money is developed within the Shunyaya Framework.

---

## ⚡ Try It

The commands below use forward-slash repository paths, which work naturally on Linux and macOS and are also accepted by Python on Windows. Linux and macOS systems may use `python3` instead of `python`, depending on the installation.

Run the Python reference kernel:

```text
python demo/ORL_Money_Reference_Kernel_v2_1_0.py
```

Run the full Python audit:

```text
python demo/ORL_Money_Reference_Kernel_v2_1_0.py --audit
```

Expected:

```text
TOTAL 451/451 PASS
```

Open the browser laboratory:

[ORL-Money Structural Lab](demo/ORL_Money_Structural_Lab_v2_1_0.html)

Then run in the browser console:

```text
await ORL_MONEY_AUDIT.runAll()
```

Expected:

```text
TOTAL 487/487 PASS
```

Run the independent verifier self-test:

```text
python verifier/ORL_Money_Independent_Verifier_v2_1_0.py --self-test
```

Expected:

```text
TOTAL 85/85 PASS
```

Verify the complete frozen corpus with strict canonical-byte checking:

```text
python verifier/ORL_Money_Independent_Verifier_v2_1_0.py --corpus corpus/ORL_Money_Frozen_Corpus_Manifest_v2_1_0.json --strict-canonical
```

Expected:

```text
Result  : PASS
Summary : 4/4 PASS
```

---

## 🧭 Visual Overview

![ORL-Money Structural Overview](docs/ORL-Money-Structural-Overview.png)

---

## 🔗 Quick Links

### 📘 Documentation

- [Quickstart](docs/Quickstart.md)
- [FAQ](docs/FAQ.md)
- [Core Architecture](docs/ORL_Money_Core_Architecture_v2_1_0.txt)
- [Conformance](docs/ORL_Money_Conformance_v2_1_0.txt)
- [Verification Guide](docs/ORL_Money_Verification_Guide_v2_1_0.txt)
- [Console Audit Commands](docs/ORL_Money_v2_1_0_Console_Audit_Commands.txt)
- [Frozen Corpus Verification Report](docs/ORL_Money_Frozen_Corpus_Verification_Report_v2_1_0.txt)
- [Structural Overview](docs/ORL-Money-Structural-Overview.png)

### ⚙️ Reference Implementations

- [Python Reference Kernel](demo/ORL_Money_Reference_Kernel_v2_1_0.py)
- [Browser Structural Lab](demo/ORL_Money_Structural_Lab_v2_1_0.html)

### 🔍 Independent Verification

- [Independent Python Verifier](verifier/ORL_Money_Independent_Verifier_v2_1_0.py)
- [Frozen Corpus Manifest](corpus/ORL_Money_Frozen_Corpus_Manifest_v2_1_0.json)
- [Two-Node Bundle](corpus/ORL_Money_two_node_bundle_v2_1_0.json)
- [Three-Node Bundle](corpus/ORL_Money_three_node_bundle_v2_1_0.json)
- [Declared-Balance Conflict Bundle](corpus/ORL_Money_balance_conflict_bundle_v2_1_0.json)
- [Multi-Unit Bundle](corpus/ORL_Money_multi_unit_bundle_v2_1_0.json)
- [SHA-256 Checksums](hashes/SHA256SUMS.txt)

---

## 🧩 Core Architecture

ORL-Money separates concepts that are often collapsed into one financial result:

`observation != financial claim`

`transaction resolution != declared balance compatibility`

`resolution != evidence-boundary closure`

`financial reconciliation != authorization`

`financial reconciliation != execution`

`financial reconciliation != settlement`

The reference processing path is:

`raw balance records + raw observations`

`-> validate collection shape`

`-> validate records and Unicode scalar structure`

`-> canonicalize`

`-> identify claims and observations`

`-> absorb exact observation duplicates`

`-> resolve unique financial claims`

`-> construct transaction receipts and witnesses`

`-> construct account and unit projections`

`-> evaluate declared-balance compatibility`

`-> construct evidence-boundary receipt`

`-> construct deterministic financial identities`

`-> self-verify or independently reconstruct`

The independent verification path is separate:

`JSON bytes`

`-> bounded intake`

`-> UTF-8 validation`

`-> duplicate-key-safe parsing`

`-> optional exact canonical-byte check`

`-> independent reconstruction`

`-> deterministic comparison`

---

## 💰 Exact Money

Money values use canonical decimal integer strings in:

`amount_minor`

Examples:

```text
"1"
"250"
"1000"
```

The Python reference kernel uses exact integers.

The browser laboratory uses `BigInt`.

The declared grammar refuses forms such as:

```text
01
+1
-1
1.0
1e3
```

Transaction amount:

```text
0
```

is also refused.

This keeps the reference financial amount path outside binary floating-point arithmetic.

---

## 🔤 Validation and Unicode Safety

The declared balance and observation inputs must be arrays.

Supported identifiers must:

- be strings
- be non-empty
- have no leading or trailing whitespace
- be NFC-normalized
- remain within the declared length limit
- contain no Unicode characters in categories `Cc`, `Cf`, or `Cs`

The `Cs` exclusion means lone surrogate code points are deterministically refused before canonical hashing.

Valid astral Unicode scalar values remain eligible when all other identifier rules are satisfied.

The producer implementations also deterministically refuse non-array balance or observation collections instead of allowing those invalid shapes to reach array-processing logic.

---

## 🧾 Claim Identity and Observation Provenance

A financial claim is identified from the canonical money fragment.

An observation is identified from:

- observation schema
- observation reference
- source
- financial claim identity

Therefore, multiple observations can refer to one financial claim.

The core relation is:

`observation multiplicity != financial multiplicity`

The supplied two-node scenario contains:

```text
10 unique observations
9 unique financial claims
1 additional observation of an already observed financial claim
```

The resolver preserves observation provenance while resolving financial structure from the unique canonical claim set.

---

## 🧠 Deterministic Transaction Resolution

For each transaction identifier, the current ruleset applies explicit deterministic precedence.

Possible results include:

### `RESOLVED`

Exactly one debit claim and one credit claim are present with:

- the same amount
- the same unit

Reason:

`MATCHED_DEBIT_CREDIT_PAIR`

### `INCOMPLETE`

Required structure is missing.

Examples:

`MISSING_DEBIT_CLAIM`

`MISSING_CREDIT_CLAIM`

### `ABSTAIN`

The supplied canonical claim structure conflicts with the rules.

Examples:

`MULTIPLE_DEBIT_AND_CREDIT_CLAIMS`

`MULTIPLE_DEBIT_CLAIMS`

`MULTIPLE_CREDIT_CLAIMS`

`UNIT_MISMATCH`

`AMOUNT_MISMATCH`

The resolver does not invent missing claims and does not silently choose a winner from conflicting claims.

Only `RESOLVED` transactions contribute to the structural projection.

---

## 🧾 Witness-Carrying Receipts

Every transaction receipt carries:

- transaction identifier
- participating claim identities
- transaction state
- deterministic reason code
- structural witness
- projection contributions when resolved
- transaction receipt identity

A `RESOLVED` witness identifies the matching debit and credit claims.

An `INCOMPLETE` witness identifies the present claims and missing requirement.

An `ABSTAIN` witness identifies the conflicting claim structure or mismatch.

This makes the result inspectable rather than returning only a status label.

---

## 🧮 Structural Projection

For a resolved amount `x`:

`debit contribution = -x`

`credit contribution = +x`

For each account-unit pair:

`final_amount_minor = initial_amount_minor + sum(resolved contribution deltas)`

Each account projection preserves the identities of the transaction receipts that contributed to its change.

Unit projections aggregate account projections by unit.

The current unit-local conservation condition is:

`initial_total_minor = final_total_minor`

and:

`net_delta_minor = 0`

---

## ⚖️ Declared-Balance Compatibility

ORL-Money keeps transaction resolution separate from declared-balance compatibility.

The current compatibility rule is:

`resolved_gross_outflow <= declared_initial_balance`

Possible compatibility states are:

`COMPATIBLE`

`CONFLICT`

`UNASSESSED`

A transaction may be structurally:

`RESOLVED`

while the declared-balance compatibility result is:

`CONFLICT`

This is intentional.

The dedicated balance-conflict scenario demonstrates two structurally resolved transactions whose combined gross outflow exceeds the declared initial balance basis.

No arrival-order winner is selected.

The key relation is:

`transaction resolution != declared balance compatibility`

This compatibility check is not a claim of actual available funds.

---

## 🔒 OPEN and SEALED Evidence Boundaries

The current evidence-boundary states are:

`OPEN`

`SEALED`

For `OPEN`, the current claim set is evaluated without being declared sealed.

For `SEALED`, the current observed claim set is explicitly declared as the sealed claim set for that bounded evaluation.

`SEALED` does not mean:

- legal finality
- settlement finality
- immutable global completeness
- proof that no evidence exists elsewhere

It is a structural boundary declaration.

---

## 🔀 Merge Algebra

ORL-Money tests more than simple list-order independence.

The current audit suite exercises properties including:

- commutativity
- associativity
- idempotence
- permutation independence
- partition independence
- merge-tree independence
- origin neutrality for financial resolution

Current merge-algebra result:

```text
259/259 PASS
```

This supports the bounded design principle that equivalent canonical financial structure should not derive its resolution authority from the path by which observations were combined.

---

## 🧬 Financial Resolution Identity and Bundle Identity

ORL-Money intentionally separates financial structure from observation provenance.

The financial resolution identity commits to the bounded financial structure, including:

- bundle profile and version
- balance snapshot
- canonical claim set
- transaction receipt root
- structural projection
- declared-balance compatibility
- evidence-boundary receipt
- declared profiles

Conceptually:

`financial_resolution_id = H(financial structure)`

The financial bundle identity additionally commits to observation provenance:

`financial_bundle_id = H(financial_resolution_id + observation_set_id)`

Therefore:

`same canonical financial structure + different provenance -> same financial resolution identity may coexist with a different financial bundle identity`

---

## 🧪 Four Reference Scenarios

### Two-Node Reconciliation

Expected transaction states:

```text
M100 -> RESOLVED
M200 -> INCOMPLETE
M300 -> INCOMPLETE
M400 -> ABSTAIN
M500 -> ABSTAIN
```

Expected summary:

```text
R:1 I:2 A:2
```

Expected final projection:

```text
VillageA|UNIT = 500
VillageB|UNIT = 1500
```

Reference identities:

```text
financial_resolution_a22b3ac1bea76f7f7573f539a8a2c76c257d149fc5b8a965fe17b0314f2154c0

financial_bundle_675d2d0d6fd03e48c7839efcf7cf35b802ea6741aacdb0fd3682c3c599d27c38
```

### Three-Node Reconstruction

Expected final states:

```text
M100 -> RESOLVED
M200 -> RESOLVED
M300 -> RESOLVED
M400 -> ABSTAIN
M500 -> ABSTAIN
```

Expected final projection:

```text
VillageA|UNIT = 650
VillageB|UNIT = 1300
VillageC|UNIT = 1050
```

Expected reconstruction progression:

```text
before_match = false
round_1_match = false
round_2_match = true
```

### Declared-Balance Conflict

Expected transaction states:

```text
T1 -> RESOLVED
T2 -> RESOLVED
```

Expected compatibility:

```text
CONFLICT
```

Expected declared deficit:

```text
40
```

No transaction winner is selected from arrival order.

### Multi-Unit Isolation

Expected final projection:

```text
A|USD = 800
B|USD = 200
A|EUR = 450
C|EUR = 50
```

Expected conservation:

```text
USD = true
EUR = true
```

Expected evidence boundary:

```text
SEALED
```

---

## 🔍 Verification Architecture

ORL-Money v2.1.0 uses distinct verification layers.

### Python Reference Audit

```text
451/451 PASS
```

Audit profile:

`ORL-MONEY-AUDIT-2-D03`

### Browser Audit

```text
487/487 PASS
```

Audit profile:

`ORL-MONEY-AUDIT-2-D04`

The browser quick audit reports:

```text
143/143 PASS
```

### Python / Browser Reference Parity

```text
36/36 PASS
```

### Independent Verifier Self-Test

```text
85/85 PASS
```

Profile:

`ORL-MONEY-INDEPENDENT-VERIFIER-SELF-TEST-1-D02`

### Frozen Corpus

```text
4/4 PASS
```

Corpus verification profile:

`ORL-MONEY-CORPUS-VERIFICATION-1-D01`

The independent verifier reconstructs supplied bundles without importing the producer reference kernel.

The canonical frozen corpus also passes exact canonical-byte verification.

A successful independent reconstruction confirms agreement under the declared v2.1.0 reference contract.

It does not prove the truth or authority of source observations.

---

## 🧊 Canonical Frozen Verification Corpus

The frozen corpus provides four canonical reference bundles and a deterministic manifest.

The corpus covers:

- partial and conflicting transaction structure
- observation multiplicity
- three-node reconstruction
- declared-balance conflict
- multi-unit projection
- OPEN and SEALED evidence boundaries

The manifest records key structural identities for each scenario, including:

- balance snapshot identity
- claim set identity
- observation set identity
- transaction receipt root
- projection root
- compatibility receipt identity
- boundary receipt identity
- financial resolution identity
- financial bundle identity
- bundle SHA-256

Current manifest ID:

```text
corpus_manifest_e549dcf1ff970db2ffd1422da39cfba328860f1afae55970229a051d9c80b05e
```

Verify the complete corpus with:

```text
python verifier/ORL_Money_Independent_Verifier_v2_1_0.py --corpus corpus/ORL_Money_Frozen_Corpus_Manifest_v2_1_0.json --strict-canonical
```

Expected:

```text
two-node         PASS
three-node       PASS
balance-conflict PASS
multi-unit       PASS

Summary: 4/4 PASS
```

---

## 🛡 Independent Verifier Hardening

The independent verifier has a separate public-input verification boundary.

It includes:

- independent reconstruction without importing the producer kernel
- a stable machine-readable result shape
- deterministic `failure_stage` and `reason_code`
- UTF-8 validation
- duplicate JSON key rejection
- bounded input-file size
- non-object and unsupported bundle-result refusal
- optional exact canonical-byte checking
- one-command corpus verification
- path-safety checks for manifest bundle filenames
- deterministic failure handling for declared public-input errors

Representative failure stages include:

```text
READ
DECODE
PARSE
CANONICALIZATION
INTAKE
RECONSTRUCTION
COMPARE
INTERNAL
```

Representative reason codes include:

```text
FILE_NOT_FOUND
INVALID_UTF8
INVALID_JSON
DUPLICATE_JSON_KEY
NON_CANONICAL_JSON_BYTES
NON_OBJECT_ROOT
UNSUPPORTED_BUNDLE_RESULT
MISSING_INPUTS
INCOMPLETE_INPUTS
EMBEDDED_INPUTS_REFUSED
BUNDLE_CONTENT_MISMATCH
VERIFIED
```

Semantic verification and byte identity remain separate:

`semantic reconstruction != exact canonical-byte identity`

A valid JSON file with extra whitespace or a trailing newline may pass ordinary independent reconstruction while failing `--strict-canonical`.

---

## 🔐 Artifact Identity

The repository uses:

[SHA256SUMS](hashes/SHA256SUMS.txt)

for the declared frozen implementation, verifier, and corpus artifact set.

The checksum surface covers:

- `demo/ORL_Money_Reference_Kernel_v2_1_0.py`
- `demo/ORL_Money_Structural_Lab_v2_1_0.html`
- `verifier/ORL_Money_Independent_Verifier_v2_1_0.py`
- all five files in the declared `corpus/` set

Documentation and presentation materials remain outside this declared frozen executable-and-corpus identity surface unless explicitly added later.

The published `hashes/SHA256SUMS.txt` records the final byte identities of these eight declared frozen artifacts. If any file in this set changes, its checksum entry must be regenerated.

The applicable relation is:

`same bytes -> same SHA-256`

A matching digest proves byte identity.

It does not by itself prove behavioral correctness.

---

## ✅ What ORL-Money Establishes

For the declared v2.1.0 reference contract, ORL-Money demonstrates:

- strict supported-input validation
- explicit non-array collection refusal
- Unicode scalar-safe identifier validation
- exact integer-string financial amounts
- canonical deterministic identities
- claim identity separated from observation provenance
- exact observation duplicate absorption
- deterministic transaction-resolution precedence
- explicit incompleteness
- explicit abstention
- witness-carrying transaction receipts
- account and unit structural projections
- transaction lineage within account projections
- unit-local conservation checks
- declared-balance compatibility
- OPEN and SEALED evidence boundaries
- merge-algebra invariants
- deterministic financial resolution and bundle identities
- Python and browser reference parity for the audited scenarios
- independent reconstruction without producer import
- stable verifier failure reporting
- duplicate-key-safe JSON intake
- exact canonical-byte verification
- canonical four-scenario corpus verification

These are bounded reference-contract claims.

---

## 🛡 What ORL-Money Does Not Establish

ORL-Money does not by itself establish:

- source-data truth
- account ownership
- identity proof
- authorization
- actual available funds
- reservations or holds
- overdraft policy
- payment execution
- account posting
- clearing
- settlement
- legal finality
- fraud prevention
- complete double-spend prevention
- consensus
- Byzantine fault tolerance
- reliable broadcast
- regulatory compliance
- production security
- universal financial correctness

The reference implementation should not be treated as a complete payment or banking system.

---

## 🔬 Research and Integration Direction

ORL-Money may inform work in:

- bounded financial reconciliation
- provenance-preserving evidence exchange
- deterministic audit reconstruction
- disconnected-system comparison
- pre-execution structural checks
- independently reconstructable financial receipts
- multi-source claim reconciliation
- deterministic discrepancy classification
- canonical verification bundles

A downstream system may consume an ORL-Money financial bundle for separate:

- policy
- dependency checks
- authorization
- execution
- posting
- settlement

Those downstream authorities remain outside the ORL-Money v2.1.0 contract.

---

# 📜 **License**

See: [LICENSE](LICENSE)

The ORL-Money reference implementation and associated verification artifacts are free to use, copy, modify, test, study, and redistribute without a license fee, subject to the license terms stated in the repository.

Documentation, architecture materials, specifications, diagrams, and explanatory content are subject to the separate terms stated in the LICENSE.

This repository does not claim recognition as a formal technical standard, security certification, production qualification, or third-party verification.

---

## 🔗 Related Structural References

- [ORL](https://github.com/OMPSHUNYAYA/Orderless-Ledger)
- [STINT-Money](https://github.com/OMPSHUNYAYA/STINT-Money)

---

## 🧭 Final Statement

ORL-Money v2.1.0 demonstrates a bounded structural approach to financial reconciliation in which validated observations become canonical claims, claims become witness-carrying transaction receipts, resolved structure becomes an inspectable projection, declared-balance compatibility remains separate from transaction resolution, and provenance remains separate from financial multiplicity.

The governing relation is:

`same validated balance basis + same canonical money claim set + same ruleset + same compatibility profile + same boundary declaration -> same bounded financial resolution`

Missing structure is not guessed.

Conflicting structure is not forced.

Arrival order is not silently promoted into transaction-classification authority.

The resulting bounded financial structure can be independently reconstructed without importing the producer implementation, while strict canonical verification separately checks the exact bytes of the declared frozen corpus.
