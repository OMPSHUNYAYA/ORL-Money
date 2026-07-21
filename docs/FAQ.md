# ⭐ FAQ — ORL-Money

**Deterministic Bounded Financial Reconciliation**

ORL-Money v2.1.0 is a deterministic reference architecture for bounded reconciliation of validated money claims, declared balances, observation provenance, transaction structure, and structural projections.

The governing relation is:

`same validated balance basis + same canonical money claim set + same ruleset + same compatibility profile + same boundary declaration -> same bounded financial resolution`

ORL-Money is developed within the Shunyaya Framework.

---

## SECTION A — Purpose and Positioning

### A1. What is ORL-Money?

ORL-Money is a bounded financial reconciliation reference architecture.

It accepts validated balance records and money-claim observations, constructs canonical identities, resolves transaction structure, produces account and unit projections, evaluates declared-balance compatibility, and emits independently reconstructable financial bundles.

The primary transaction states are:

- `RESOLVED`
- `INCOMPLETE`
- `ABSTAIN`

The architecture also keeps other state dimensions separate, including:

- input acceptance
- declared-balance compatibility
- evidence-boundary state
- verification state

---

### A2. What problem does ORL-Money explore?

ORL-Money explores how financial claims can be reconciled when observations may arrive:

- in different orders
- from different sources
- with repeated exact observations
- with incomplete transaction structure
- with conflicting transaction structure
- across multiple units
- under a declared evidence boundary

The resolver derives its bounded result from canonical structure and declared rules rather than using observation arrival position as transaction-classification authority.

---

### A3. What is the core idea in one line?

`canonical financial structure + deterministic rules -> bounded financial resolution`

---

### A4. What does “orderless” mean here?

It means that, within the declared model, the order in which equivalent validated observations are supplied is not intended to determine transaction classification or the resulting bounded financial resolution.

The current implementation is exercised by automated merge-algebra testing covering:

- commutativity
- associativity
- idempotence
- permutation independence
- partition independence
- merge-tree independence
- origin neutrality for financial resolution

ORL-Money does not claim that operational sequencing is unnecessary in all financial systems.

---

### A5. Is ORL-Money saying that time is irrelevant?

No.

Time may still be important for:

- legal records
- user interfaces
- deadlines
- audit history
- operational monitoring
- payment execution
- settlement

The narrower architectural claim is that the declared resolver does not use wall-clock time or arrival position as authority for the bounded transaction-resolution rules implemented here.

---

### A6. Is ORL-Money a banking system?

No.

It is not:

- a banking core
- a payment network
- a settlement system
- an account-posting engine
- an authorization system
- a fraud-control platform
- a production financial service

It is a deterministic reference architecture with executable implementations, audits, a canonical frozen verification corpus, and independent reconstruction.

---

### A7. Does ORL-Money move real money?

No.

It computes a bounded structural reconciliation and projection.

It does not:

- authorize payment
- debit a real account
- credit a real account
- clear a payment
- settle a payment

---

### A8. Can ORL-Money be integrated with other systems?

Conceptually, yes.

A separate downstream system could use an ORL-Money financial bundle as an input to layers responsible for:

- authorization
- policy
- dependency checks
- execution
- posting
- settlement

Those functions remain outside the ORL-Money v2.1.0 contract.

---

## SECTION B — Data Model

### B1. What is a balance record?

A supported balance record contains exactly:

```text
schema
account
amount_minor
unit
```

The required schema is:

`ORL-MONEY-BALANCE-2-D02`

Example:

```json
{"schema":"ORL-MONEY-BALANCE-2-D02","account":"VillageA","amount_minor":"1000","unit":"UNIT"}
```

---

### B2. What is a money fragment?

A supported money fragment contains exactly:

```text
schema
tx
side
account
amount_minor
unit
```

The required schema is:

`ORL-FRAGMENT-2-D02`

Supported sides are:

`debit`

`credit`

Example:

```json
{"schema":"ORL-FRAGMENT-2-D02","tx":"M100","side":"debit","account":"VillageA","amount_minor":"500","unit":"UNIT"}
```

---

### B3. What is an observation?

An observation contains:

```text
schema
observation_ref
source
fragment
```

The required schema is:

`ORL-MONEY-OBSERVATION-2-D02`

The observation preserves provenance around a financial claim.

---

### B4. What is the difference between a claim and an observation?

A financial claim is identified from the canonical money fragment.

An observation is identified from:

- observation schema
- observation reference
- source
- financial claim identity

Therefore, multiple observations may refer to the same financial claim.

The key relation is:

`observation multiplicity != financial multiplicity`

---

### B5. Why is that separation important?

It prevents repeated or independently observed evidence from being silently counted as additional money movement.

The resolver can preserve provenance while still resolving over unique canonical financial claims.

---

## SECTION C — Exact Money and Validation

### C1. How are amounts represented?

Amounts use decimal integer strings in `amount_minor`.

Examples:

`"1"`

`"250"`

`"1000000"`

The Python implementation uses exact integers.

The browser implementation uses `BigInt`.

This avoids binary floating-point arithmetic in the financial amount path.

---

### C2. Are negative values allowed?

No.

Transaction claim amounts must be strictly positive canonical decimal integer strings.

Balance records may contain zero.

---

### C3. Are decimal values such as `1.50` allowed?

No.

The current format uses integer minor units.

For example, a system using cents would represent:

`1.50`

as:

`"150"`

under a separately understood unit convention.

---

### C4. What malformed amount forms are refused?

Examples include:

`01`

`+1`

`-1`

`1.0`

`1e3`

Transaction amount:

`0`

is also refused.

---

### C5. Are identifiers validated?

Yes.

Supported identifiers must:

- be strings
- be non-empty
- have no leading or trailing whitespace
- be NFC-normalized
- contain no Unicode characters in categories `Cc`, `Cf`, or `Cs`
- remain within the declared length bound

NFC normalization ensures that canonically equivalent Unicode spellings do not silently produce different structural identities.

The `Cs` exclusion means lone surrogate code points are refused before hashing.

Valid astral Unicode scalar values may still be accepted.

NFC normalization does not by itself prevent visually confusable or homoglyph identifiers.

---

### C6. Are unknown fields accepted?

No.

The declared balance, fragment, and observation structures require exact field sets.

Missing or extra fields are refused.

---

### C7. What happens if balances or observations are not arrays?

They are deterministically refused.

The current producer implementations reject non-array top-level balance and observation inputs rather than allowing those shapes to reach array-processing logic.

---

## SECTION D — Transaction Resolution

### D1. When does a transaction become RESOLVED?

A transaction becomes `RESOLVED` when the unique canonical claim set contains:

- exactly one debit claim
- exactly one credit claim
- the same unit
- the same amount

The reason code is:

`MATCHED_DEBIT_CREDIT_PAIR`

---

### D2. When does a transaction become INCOMPLETE?

A transaction becomes `INCOMPLETE` when exactly one required side is missing.

Possible reason codes include:

`MISSING_DEBIT_CLAIM`

`MISSING_CREDIT_CLAIM`

The resolver does not invent the missing structure.

---

### D3. When does a transaction become ABSTAIN?

The v2.1.0 ruleset includes explicit abstention cases such as:

`MULTIPLE_DEBIT_AND_CREDIT_CLAIMS`

`MULTIPLE_DEBIT_CLAIMS`

`MULTIPLE_CREDIT_CLAIMS`

`UNIT_MISMATCH`

`AMOUNT_MISMATCH`

The resolver does not silently select a winner from conflicting structure.

---

### D4. What happens to INCOMPLETE and ABSTAIN transactions?

They produce no structural projection contribution.

Only `RESOLVED` transactions contribute to account projections.

---

### D5. Does every transaction receipt explain its result?

Yes.

Each transaction receipt carries:

- state
- reason code
- participating claim identities
- structural witness
- projection contributions when resolved

This makes resolution inspectable rather than merely returning a label.

---

## SECTION E — Structural Projection

### E1. How is the projection calculated?

For a resolved transaction amount `x`:

`debit contribution = -x`

`credit contribution = +x`

For each account-unit pair:

`final_amount_minor = initial_amount_minor + sum(resolved contribution deltas)`

---

### E2. Do incomplete or conflicting transactions affect balances?

No.

`INCOMPLETE -> no projection contribution`

`ABSTAIN -> no projection contribution`

---

### E3. Does ORL-Money preserve transaction lineage?

Yes.

Each account projection records the transaction receipt identities that contributed to its change.

This supports an explainable relation such as:

`final balance = declared initial balance + resolved transaction contributions`

---

### E4. Does ORL-Money support multiple units?

Yes.

The reference implementation keeps projections separated by unit.

The frozen multi-unit scenario demonstrates independent `USD` and `EUR` projections.

---

### E5. What does unit conservation mean?

For each unit, the reference projection checks:

`initial_total_minor = final_total_minor`

and:

`net_delta_minor = 0`

This is a structural conservation check for the declared resolved transaction model.

It is not a universal monetary theorem.

---

## SECTION F — Declared-Balance Compatibility

### F1. Does ORL-Money check sufficient funds?

Not in the banking or authorization sense.

It performs a separate deterministic assessment against the declared initial balance basis.

The current rule is:

`resolved_gross_outflow <= declared_initial_balance`

---

### F2. What compatibility states exist?

The current compatibility assessment uses:

`COMPATIBLE`

`CONFLICT`

`UNASSESSED`

---

### F3. Can a transaction be RESOLVED while compatibility is CONFLICT?

Yes.

This is intentional.

For example, two transactions may each be structurally complete and therefore `RESOLVED`, while their combined gross outflow exceeds the declared balance basis.

The key relation is:

`transaction resolution != declared balance compatibility`

---

### F4. Why not simply accept the first transaction that arrived?

Because that would make arrival order act as hidden allocation authority.

ORL-Money instead preserves both structurally resolved transactions and separately reports the compatibility conflict.

---

### F5. Does COMPATIBLE mean the account really has sufficient funds?

No.

It means the resolved gross outflow is compatible with the supplied declared balance basis under the current profile.

It does not prove actual account state, reservations, holds, overdraft rules, or external commitments.

---

## SECTION G — Evidence Boundary

### G1. What boundary states exist?

`OPEN`

`SEALED`

---

### G2. What does OPEN mean?

`OPEN` means the current evidence set is evaluated without declaring the current claim set as sealed.

---

### G3. What does SEALED mean?

`SEALED` means the current observed claim set is explicitly declared as the sealed claim set for that bounded evaluation.

---

### G4. Does SEALED mean settlement finality?

No.

It does not mean:

- legal finality
- payment finality
- immutable global completeness
- proof that no evidence exists elsewhere

It is a structural boundary declaration.

---

## SECTION H — Deterministic Identity

### H1. What objects receive deterministic identities?

The architecture assigns deterministic identities to structural objects including:

- balance records
- balance snapshots
- financial claims
- observations
- claim sets
- observation sets
- transaction evidence
- transaction receipts
- transaction receipt roots
- account projections
- unit projections
- projection roots
- compatibility receipts
- boundary receipts
- financial resolutions
- financial bundles
- refusals

---

### H2. What is the financial resolution identity?

The financial resolution identity commits to the bounded financial structure, including:

- bundle profile and version
- balance basis
- canonical claim set
- ruleset
- projection
- compatibility result
- boundary declaration

Conceptually:

`financial_resolution_id = H(financial structure)`

---

### H3. What is the financial bundle identity?

The financial bundle identity additionally commits to observation provenance.

Conceptually:

`financial_bundle_id = H(financial_resolution_id + observation_set_id)`

---

### H4. Can provenance change without changing financial resolution?

Yes.

When canonical financial claims remain the same but observation provenance changes:

`financial resolution identity may remain the same`

while:

`financial bundle identity changes`

This preserves a clean distinction between financial structure and evidence provenance.

---

## SECTION I — Determinism and Merge Algebra

### I1. Is ORL-Money deterministic?

Yes, within the declared input grammar, canonicalization rules, profiles, and implementation contract.

The governing relation is:

`same validated balance basis + same canonical money claim set + same ruleset + same compatibility profile + same boundary declaration -> same bounded financial resolution`

---

### I2. Is arrival order tested?

Yes.

The Python and browser audit suites include extensive merge-algebra coverage.

The current audit evidence includes:

`MERGE ALGEBRA 259/259 PASS`

---

### I3. What properties are tested?

The current audit exercises properties including:

- commutativity
- associativity
- idempotence
- permutation independence
- partition independence
- merge-tree independence
- origin neutrality for financial resolution

---

### I4. Does same financial structure always mean the same bundle identity?

No.

Different observation provenance may preserve the same financial resolution while changing the financial bundle identity.

---

## SECTION J — Verification

### J1. What verification layers are included?

ORL-Money v2.1.0 includes:

- Python producer self-verification
- Python full audit
- browser full audit
- Python/browser reference parity
- independent Python reconstruction
- stable machine-readable verifier results
- duplicate-key-safe and UTF-8-safe JSON intake
- optional strict canonical-byte verification
- one-command canonical frozen-corpus verification
- one consolidated SHA-256 artifact manifest

---

### J2. What does the Python reference audit report?

The current reference result is:

`TOTAL 451/451 PASS`

under:

`ORL-MONEY-AUDIT-2-D03`

---

### J3. What does the browser audit report?

The current browser result is:

`TOTAL 487/487 PASS`

under:

`ORL-MONEY-AUDIT-2-D04`

The quick browser audit reports:

`143/143 PASS`

---

### J4. Is Python/browser parity checked?

Yes.

The browser full audit includes:

`PYTHON / BROWSER PARITY 36/36 PASS`

This establishes parity for the declared reference identities and audited scenarios.

---

### J5. Is there an independent verifier?

Yes.

The independent Python verifier does not import the producer reference kernel.

Its self-test reports:

`TOTAL 85/85 PASS`

under:

`ORL-MONEY-INDEPENDENT-VERIFIER-SELF-TEST-1-D02`

---

### J6. What does the frozen corpus contain?

The corpus contains:

- one deterministic manifest
- two-node bundle
- three-node bundle
- declared-balance conflict bundle
- multi-unit bundle

The current corpus result is:

`4/4 PASS`

under:

`ORL-MONEY-CORPUS-VERIFICATION-1-D01`

The canonical corpus also passes strict canonical-byte verification.

---

### J7. What does independent verification prove?

It confirms that the separate verifier reconstructs the supplied bundle from its embedded inputs and reproduces the declared bounded structure and deterministic identities under its implementation of the v2.1.0 contract.

It is stronger than relying only on producer self-verification.

---

### J8. What does independent verification not prove?

It does not prove:

- the source observations are true
- an account belongs to a specific person
- a payment is authorized
- a payment was executed
- legal validity
- settlement
- universal financial correctness
- production security

---

### J9. What is strict canonical verification?

Ordinary independent verification asks whether the parsed bundle reconstructs to the same declared structure.

Strict canonical verification additionally asks whether the supplied file bytes are exactly the canonical UTF-8 JSON serialization.

A semantically equivalent JSON file with extra whitespace or a trailing newline may therefore:

`pass ordinary independent verification`

while:

`fail --strict-canonical`

The frozen v2.1.0 corpus is stored in exact canonical JSON form.

---

### J10. Does the verifier reject duplicate JSON keys?

Yes.

The independent verifier rejects duplicate JSON object keys recursively during parsing.

A duplicate-key input produces a deterministic failure such as:

`failure_stage = PARSE`

`reason_code = DUPLICATE_JSON_KEY`

---

### J11. What happens with malformed or non-bundle JSON?

The verifier returns a bounded failure result with a stable result shape.

Declared failure stages include:

`READ`

`DECODE`

`PARSE`

`CANONICALIZATION`

`INTAKE`

`RECONSTRUCTION`

`COMPARE`

`INTERNAL`

The normal public CLI path is designed to report declared failures without an ordinary traceback.

---

### J12. What do SHA-256 files prove?

A matching SHA-256 proves byte identity against the recorded digest.

The repository uses:

`hashes/SHA256SUMS.txt`

for the declared frozen implementation, verifier, and corpus artifact set.

The published checksum file records the final byte identities of eight declared frozen artifacts:

- two reference implementations
- one independent verifier
- one frozen corpus manifest
- four frozen corpus bundles

If any file in that declared frozen set changes, its checksum entry must be regenerated.

Behavioral verification and artifact identity verification remain separate.

---

### J13. What exit codes does the independent verifier use?

The command-line verifier uses:

`0 = verification or self-test PASS`

`1 = verification, corpus, data, intake, or file-access FAIL`

`2 = command-line usage error or missing mode`

Missing files, unreadable files, invalid UTF-8, malformed JSON, duplicate JSON keys, canonicalization failures, and verification mismatches therefore return exit code `1`.

Exit code `2` is reserved for command-line usage errors, such as invoking the verifier without selecting a supported verification mode.

---

## SECTION K — Reference Scenarios

### K1. What does the two-node scenario demonstrate?

Expected transaction states:

```text
M100 -> RESOLVED
M200 -> INCOMPLETE
M300 -> INCOMPLETE
M400 -> ABSTAIN
M500 -> ABSTAIN
```

Expected summary:

`R:1 I:2 A:2`

Expected final projection:

```text
VillageA|UNIT = 500
VillageB|UNIT = 1500
```

Financial resolution identity:

`financial_resolution_a22b3ac1bea76f7f7573f539a8a2c76c257d149fc5b8a965fe17b0314f2154c0`

Financial bundle identity:

`financial_bundle_675d2d0d6fd03e48c7839efcf7cf35b802ea6741aacdb0fd3682c3c599d27c38`

---

### K2. What does the three-node scenario demonstrate?

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

Financial resolution identity:

`financial_resolution_eff3518564740a56633fe54188412bed95fa6730806d1c9a417f7e9edce48750`

Financial bundle identity:

`financial_bundle_cecf58e08d1094ca544933bb41224f0b62eb45361d2cab3cc51db724453da5a7`

---

### K3. What does the declared-balance conflict scenario demonstrate?

Both:

`T1`

and:

`T2`

are structurally:

`RESOLVED`

while the overall declared-balance compatibility state is:

`CONFLICT`

The declared deficit is:

`40`

No arrival-order winner is selected.

---

### K4. What does the multi-unit scenario demonstrate?

Expected final projection:

```text
A|USD = 800
B|USD = 200
A|EUR = 450
C|EUR = 50
```

Expected unit conservation:

```text
USD = true
EUR = true
```

Expected boundary:

`SEALED`

---

## SECTION L — Practical Scope

### L1. What is ORL-Money suitable for?

The current repository is suitable for:

- deterministic reconciliation research
- structural financial evidence modeling
- offline bundle inspection
- provenance-preserving duplicate analysis
- deterministic discrepancy classification
- independently reconstructable reference receipts
- canonical corpus verification
- pre-execution structural checks
- education and experimentation

---

### L2. Is ORL-Money ready for real payments?

No.

The current implementation is not a complete financial production system.

---

### L3. What additional systems would real deployment require?

Depending on the use case:

- authentication
- authorization
- account ownership controls
- current balance authority
- reservations and holds
- policy
- secure transport
- replay protection across external systems
- accounting controls
- execution
- posting
- settlement
- monitoring
- security review
- legal review
- regulatory compliance

---

### L4. Does ORL-Money require Windows?

No.

The Python reference kernel and independent verifier use the Python standard library and can be run on supported Python installations across Windows, Linux, and macOS.

The browser laboratory is opened in a modern browser.

The Quickstart, Verification Guide, and Console Audit Commands provide cross-platform command guidance where shell syntax differs.

Checksum commands vary by platform, but the verification target remains the same recorded SHA-256 values.

---

## SECTION M — Boundaries and Skeptical Questions

### M1. Does deterministic output imply correct real-world output?

No.

Determinism means the same declared inputs and rules produce the same bounded result.

Real-world correctness also depends on:

- truthful inputs
- appropriate rules
- authorized actors
- complete domain controls
- correct integration

---

### M2. Is same-evidence equality the same as consensus?

No.

Consensus concerns agreement under a defined distributed-system and fault model.

ORL-Money concerns deterministic reconstruction once the relevant canonical inputs are defined.

---

### M3. Does ORL-Money prevent double spending?

No universal double-spend prevention claim is made.

It deterministically identifies certain duplicate and conflicting structures within its bounded model.

External authorization, reservation, execution, and settlement remain separate concerns.

---

### M4. Does ORL-Money prove that clocks are unnecessary in finance?

No.

It demonstrates that the current bounded resolver can classify its declared structures without using wall-clock time or arrival position as classification authority.

---

### M5. Does ORL-Money replace accounting systems?

No.

It produces a bounded structural projection and reconciliation bundle.

It is not a complete accounting ledger, posting engine, or financial control system.

---

### M6. What is the strongest justified current interpretation?

ORL-Money v2.1.0 is an executable deterministic reference architecture in which validated balance records and canonical money claims are transformed into witness-carrying transaction receipts, structural projections, declared-balance compatibility results, evidence-boundary receipts, and independently reconstructable financial identities without using observation arrival order as transaction-classification authority.

Its current assurance evidence includes cross-runtime reference parity, an independent verifier that does not import the producer kernel, stable failure reporting for declared verifier inputs, and a four-scenario canonical corpus that passes strict corpus verification.

---

## ⭐ Final One-Line Summary

ORL-Money deterministically reconciles validated financial claims into witness-carrying bounded financial resolutions while separating provenance, transaction state, declared-balance compatibility, evidence closure, projection, and verification so that the same declared canonical structure can be independently reconstructed without making arrival order the hidden source of financial authority.
