# ⭐ ORL-Money — Quickstart

**Deterministic Bounded Financial Reconciliation**

ORL-Money v2.1.0 is a deterministic reference architecture for bounded reconciliation of validated money claims, declared balances, provenance, transaction structure, and structural projections.

The governing relation is:

`same validated balance basis + same canonical money claim set + same ruleset + same compatibility profile + same boundary declaration -> same bounded financial resolution`

ORL-Money is developed within the Shunyaya Framework.

---

## 1. Requirements

Python:

- Python 3.9 or later
- Python standard library only

Browser:

- a modern browser
- no server required for the basic local browser laboratory

No external Python package is required by the reference kernel or independent verifier.

### Command Conventions

Repository paths in this guide use forward slashes because they work naturally on Linux and macOS and are also accepted by Python on Windows.

Where this guide shows:

`python`

Linux and macOS systems may use:

`python3`

depending on how Python is installed.

Commands that create or remove temporary files are shown separately for Windows and POSIX shells where the syntax differs.

---

## 2. Run the Python Reference Kernel

From the repository root:

```text
python demo/ORL_Money_Reference_Kernel_v2_1_0.py
```

The default scenario is:

`two-node`

Expected result:

```text
Result: ACCEPTED
Boundary: OPEN
State summary: R:1 I:2 A:2
Declared-balance compatibility: COMPATIBLE
Self verification: True
```

Expected final projection:

```text
VillageA|UNIT = 500
VillageB|UNIT = 1500
```

---

## 3. Run the Python Full Audit

Run:

```text
python demo/ORL_Money_Reference_Kernel_v2_1_0.py --audit
```

Expected:

```text
TOTAL 451/451 PASS
```

The current audit includes:

```text
VALIDATION 37/37 PASS
CANONICALIZATION 15/15 PASS
BALANCE BASIS 7/7 PASS
CLAIM / OBSERVATION 13/13 PASS
RESOLUTION 27/27 PASS
EXACT MONEY 10/10 PASS
MERGE ALGEBRA 259/259 PASS
MULTI-UNIT 10/10 PASS
BALANCE COMPATIBILITY 9/9 PASS
PROJECTION 8/8 PASS
BOUNDARY 7/7 PASS
RECEIPTS / TAMPER 17/17 PASS
REFERENCE SCENARIOS 20/20 PASS
ORIGIN NEUTRALITY 2/2 PASS
KNOWN REGRESSIONS 10/10 PASS
```

---

## 4. Run the Other Python Scenarios

Three-node:

```text
python demo/ORL_Money_Reference_Kernel_v2_1_0.py --scenario three-node
```

Declared-balance conflict:

```text
python demo/ORL_Money_Reference_Kernel_v2_1_0.py --scenario balance-conflict
```

Multi-unit:

```text
python demo/ORL_Money_Reference_Kernel_v2_1_0.py --scenario multi-unit
```

---

## 5. Open the Browser Laboratory

Open:

`demo/ORL_Money_Structural_Lab_v2_1_0.html`

The browser laboratory allows inspection of:

- canonical financial claims
- observation provenance
- transaction states and witnesses
- exact duplicate behavior
- declared-balance compatibility
- account projections
- unit projections
- OPEN and SEALED evidence boundaries
- tamper rejection
- evidence-order changes
- provenance-origin changes
- completion of missing transaction structure

A Chromium `file://` unique-security-origin warning may appear when the file is opened directly.

The demonstrated browser audits execute successfully under the local-file workflow despite that warning.

---

## 6. Run the Browser Full Audit

Open the browser developer console and run:

```text
await ORL_MONEY_AUDIT.runAll()
```

Expected:

```text
TOTAL 487/487 PASS
```

The full audit includes:

```text
PYTHON / BROWSER PARITY 36/36 PASS
```

---

## 7. Run the Browser Quick Audit

Run:

```text
ORL_MONEY_AUDIT.quick()
```

Expected:

```text
passed = 143
total = 143
pass = true
```

View the most recent audit result with:

```text
ORL_MONEY_AUDIT.last()
```

---

## 8. Inspect the Two-Node Scenario in the Browser

Run:

```text
ORLMoneyCore.transactionStateMap(
  ORLMoneyCore.scenarioBundle("two-node")[1]
)
```

Expected:

```text
M100 = RESOLVED
M200 = INCOMPLETE
M300 = INCOMPLETE
M400 = ABSTAIN
M500 = ABSTAIN
```

Run:

```text
ORLMoneyCore.finalBalanceMap(
  ORLMoneyCore.scenarioBundle("two-node")[1]
)
```

Expected:

```text
VillageA|UNIT = 500
VillageB|UNIT = 1500
```

Verify the bundle:

```text
ORLMoneyCore.verifyBundle(
  ORLMoneyCore.scenarioBundle("two-node")[1]
)
```

Expected:

```text
valid = true
```

---

## 9. Understand Observation and Claim Separation

The two-node scenario contains:

```text
raw observations = 10
unique observations = 10
unique financial claims = 9
observation multiplicity = 1
```

The core relation is:

`observation multiplicity != financial multiplicity`

Two different observations may carry the same financial claim without creating two financial transfers.

---

## 10. Understand the Three Transaction States

### RESOLVED

A transaction has:

- exactly one debit claim
- exactly one credit claim
- matching unit
- matching amount

Only `RESOLVED` transactions contribute to the structural projection.

### INCOMPLETE

A required debit or credit claim is missing.

The resolver does not invent the missing structure.

### ABSTAIN

The canonical claim structure conflicts with the rules.

Examples include:

- multiple debit claims
- multiple credit claims
- amount mismatch
- unit mismatch

The resolver does not silently choose a winner.

---

## 11. Exact Money and Identifier Validation

Amounts are represented using integer strings in:

`amount_minor`

Examples:

```text
"1"
"250"
"1000"
```

The Python kernel uses exact integers.

The browser laboratory uses `BigInt`.

Examples rejected by the declared amount grammar include:

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

is refused.

Identifiers must also be NFC-normalized and reject Unicode categories:

```text
Cc
Cf
Cs
```

NFC normalization ensures that canonically equivalent Unicode spellings do not silently produce different structural identities.

The `Cs` exclusion refuses lone surrogate code points while valid astral Unicode scalar values remain eligible.

NFC normalization does not by itself prevent visually confusable or homoglyph identifiers.

---

## 12. Declared-Balance Compatibility

ORL-Money separates transaction resolution from declared-balance compatibility.

The current rule is:

`resolved_gross_outflow <= declared_initial_balance`

The compatibility states are:

```text
COMPATIBLE
CONFLICT
UNASSESSED
```

A transaction may be structurally:

`RESOLVED`

while the overall declared-balance compatibility is:

`CONFLICT`

This prevents arrival order from silently acting as allocation authority.

---

## 13. Check the Declared-Balance Conflict Scenario

In the browser console:

```text
ORLMoneyCore.transactionStateMap(
  ORLMoneyCore.scenarioBundle("balance-conflict")[1]
)
```

Expected:

```text
T1 = RESOLVED
T2 = RESOLVED
```

Inspect:

```text
ORLMoneyCore.scenarioBundle(
  "balance-conflict"
)[1].declared_balance_compatibility
```

Expected:

```text
state = CONFLICT
```

The declared deficit is:

```text
40
```

No arrival-order winner is selected.

---

## 14. Check Multi-Unit Isolation

Run:

```text
ORLMoneyCore.finalBalanceMap(
  ORLMoneyCore.scenarioBundle("multi-unit")[1]
)
```

Expected:

```text
A|EUR = 450
A|USD = 800
B|USD = 200
C|EUR = 50
```

Run:

```text
ORLMoneyCore.unitConservationMap(
  ORLMoneyCore.scenarioBundle("multi-unit")[1]
)
```

Expected:

```text
EUR = true
USD = true
```

The scenario uses:

```text
boundary = SEALED
```

---

## 15. Run the Independent Verifier Self-Test

From the repository root:

```text
python verifier/ORL_Money_Independent_Verifier_v2_1_0.py --self-test
```

Expected:

```text
TOTAL 85/85 PASS
```

The independent verifier does not import the producer reference kernel.

---

## 16. Independently Verify a Temporary Bundle

### Windows Command Prompt

Create a temporary bundle outside the repository artifact folders:

```text
python demo/ORL_Money_Reference_Kernel_v2_1_0.py --scenario two-node --json > "%TEMP%\ORL_Money_two_node_v2_1_0_test.json"
```

Verify it:

```text
python verifier/ORL_Money_Independent_Verifier_v2_1_0.py --bundle "%TEMP%\ORL_Money_two_node_v2_1_0_test.json"
```

Delete the temporary file:

```text
del "%TEMP%\ORL_Money_two_node_v2_1_0_test.json"
```

### Linux / macOS

Create a temporary file and generate the bundle:

```text
TMP_FILE="$(mktemp "${TMPDIR:-/tmp}/orl-money-bundle.XXXXXX.json")"
python3 demo/ORL_Money_Reference_Kernel_v2_1_0.py --scenario two-node --json > "$TMP_FILE"
```

Verify it:

```text
python3 verifier/ORL_Money_Independent_Verifier_v2_1_0.py --bundle "$TMP_FILE"
```

Delete the temporary file:

```text
rm -f "$TMP_FILE"
```

Expected:

```text
Result: PASS
Reason code: VERIFIED
Independent reconstruction: True
Producer implementation imported: False
```

The supplied and reconstructed:

```text
financial_resolution_id
financial_bundle_id
```

must match.

---

## 17. Verify Exact Canonical JSON Bytes

A redirected CLI bundle normally contains a trailing newline, so it may pass semantic verification while failing strict byte canonicality.

The distinction is:

`semantic reconstruction != exact canonical-byte identity`

### Windows Command Prompt

Create an exact canonical-byte test bundle:

```text
python -c "import importlib.util,pathlib; p=r'demo/ORL_Money_Reference_Kernel_v2_1_0.py'; s=importlib.util.spec_from_file_location('orl',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); b=m.scenario_bundle('two-node')[1]; pathlib.Path(r'%TEMP%\ORL_Money_two_node_v2_1_0_canonical.json').write_text(m.canonical_json(b),encoding='utf-8')"
```

Verify it:

```text
python verifier/ORL_Money_Independent_Verifier_v2_1_0.py --bundle "%TEMP%\ORL_Money_two_node_v2_1_0_canonical.json" --strict-canonical
```

Delete the temporary file:

```text
del "%TEMP%\ORL_Money_two_node_v2_1_0_canonical.json"
```

### Linux / macOS

Create a temporary file:

```text
TMP_FILE="$(mktemp "${TMPDIR:-/tmp}/orl-money-canonical.XXXXXX.json")"
```

Write the exact canonical JSON bytes:

```text
TMP_FILE="$TMP_FILE" python3 -c "import importlib.util,os,pathlib; p='demo/ORL_Money_Reference_Kernel_v2_1_0.py'; s=importlib.util.spec_from_file_location('orl',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); b=m.scenario_bundle('two-node')[1]; pathlib.Path(os.environ['TMP_FILE']).write_text(m.canonical_json(b),encoding='utf-8')"
```

Verify it:

```text
python3 verifier/ORL_Money_Independent_Verifier_v2_1_0.py --bundle "$TMP_FILE" --strict-canonical
```

Delete the temporary file:

```text
rm -f "$TMP_FILE"
```

Expected:

```text
Result: PASS
Reason code: VERIFIED
Independent reconstruction: True
```

---

## 18. Verify Duplicate-Key Rejection

The independent verifier rejects duplicate JSON object keys during parsing.

### Windows Command Prompt

Create a temporary duplicate-key document:

```text
echo {"result":"ACCEPTED","result":"REFUSED"}>"%TEMP%\orl_money_duplicate.json"
```

Verify it:

```text
python verifier/ORL_Money_Independent_Verifier_v2_1_0.py --bundle "%TEMP%\orl_money_duplicate.json"
```

Delete the temporary file:

```text
del "%TEMP%\orl_money_duplicate.json"
```

### Linux / macOS

Create a temporary file:

```text
TMP_FILE="$(mktemp "${TMPDIR:-/tmp}/orl-money-duplicate.XXXXXX.json")"
```

Write the duplicate-key JSON exactly:

```text
printf '%s' '{"result":"ACCEPTED","result":"REFUSED"}' > "$TMP_FILE"
```

Verify it:

```text
python3 verifier/ORL_Money_Independent_Verifier_v2_1_0.py --bundle "$TMP_FILE"
```

Delete the temporary file:

```text
rm -f "$TMP_FILE"
```

Expected:

```text
Failure stage: PARSE
Reason code: DUPLICATE_JSON_KEY
```

---

## 19. Verify the Complete Frozen Corpus

Run:

```text
python verifier/ORL_Money_Independent_Verifier_v2_1_0.py --corpus corpus/ORL_Money_Frozen_Corpus_Manifest_v2_1_0.json --strict-canonical
```

Expected:

```text
Result: PASS
Summary: 4/4 PASS
Reason code: VERIFIED
```

Expected scenarios:

```text
two-node = PASS
three-node = PASS
balance-conflict = PASS
multi-unit = PASS
```

Expected manifest ID:

`corpus_manifest_e549dcf1ff970db2ffd1422da39cfba328860f1afae55970229a051d9c80b05e`

The human-readable corpus result is:

`docs/ORL_Money_Frozen_Corpus_Verification_Report_v2_1_0.txt`

---

## 20. Verifier Exit Codes

The command-line verifier uses:

```text
0 = verification or self-test PASS
1 = verification, corpus, data, intake, or file-access FAIL
2 = command-line usage error or missing mode
```

Missing files, unreadable files, invalid UTF-8, malformed JSON, duplicate JSON keys, canonicalization failures, and verification mismatches therefore return exit code `1`.

Exit code `2` is reserved for command-line usage errors, such as invoking the verifier without selecting a supported verification mode.

These values allow the verifier to be used reliably in scripts and continuous verification workflows.

---

## 21. Artifact Identity

The repository uses one checksum file:

```text
hashes/SHA256SUMS.txt
```

The declared frozen artifact set includes:

```text
demo/ORL_Money_Reference_Kernel_v2_1_0.py
demo/ORL_Money_Structural_Lab_v2_1_0.html
verifier/ORL_Money_Independent_Verifier_v2_1_0.py
corpus/ORL_Money_Frozen_Corpus_Manifest_v2_1_0.json
corpus/ORL_Money_two_node_bundle_v2_1_0.json
corpus/ORL_Money_three_node_bundle_v2_1_0.json
corpus/ORL_Money_balance_conflict_bundle_v2_1_0.json
corpus/ORL_Money_multi_unit_bundle_v2_1_0.json
```

Documentation is outside this declared frozen executable-and-corpus checksum set unless the repository explicitly chooses otherwise.

The published checksum file records the final byte identities of these eight artifacts. If any file in this declared frozen set changes, its checksum entry must be regenerated.

---

## 22. Repository Structure

```text
ORL-Money/
│
├── LICENSE
├── README.md
│
├── demo/
│   ├── ORL_Money_Reference_Kernel_v2_1_0.py
│   └── ORL_Money_Structural_Lab_v2_1_0.html
│
├── verifier/
│   └── ORL_Money_Independent_Verifier_v2_1_0.py
│
├── corpus/
│   ├── ORL_Money_Frozen_Corpus_Manifest_v2_1_0.json
│   ├── ORL_Money_two_node_bundle_v2_1_0.json
│   ├── ORL_Money_three_node_bundle_v2_1_0.json
│   ├── ORL_Money_balance_conflict_bundle_v2_1_0.json
│   └── ORL_Money_multi_unit_bundle_v2_1_0.json
│
├── docs/
│   ├── FAQ.md
│   ├── Quickstart.md
│   ├── ORL_Money_Core_Architecture_v2_1_0.txt
│   ├── ORL_Money_Conformance_v2_1_0.txt
│   ├── ORL_Money_Verification_Guide_v2_1_0.txt
│   ├── ORL_Money_Frozen_Corpus_Verification_Report_v2_1_0.txt
│   ├── ORL_Money_v2_1_0_Console_Audit_Commands.txt
│   └── ORL-Money-Structural-Overview.png
│
└── hashes/
    └── SHA256SUMS.txt
```

---

## 23. Current Verification Summary

Python reference kernel:

```text
451/451 PASS
```

Browser laboratory:

```text
487/487 PASS
```

Python/browser parity:

```text
36/36 PASS
```

Browser quick audit:

```text
143/143 PASS
```

Independent verifier self-test:

```text
85/85 PASS
```

Frozen corpus with strict canonical verification:

```text
4/4 PASS
```

---

## 24. Build Your Own Reconciliation

The frozen scenarios provide reproducible reference evidence, but the same model-building functions can also be used to construct a small custom reconciliation.

The following example declares two USD balances and two observations describing one matching transfer.

Save the example as a temporary Python file, or run the same statements from a Python session started at the repository root:

```python
import importlib.util

kernel_path = "demo/ORL_Money_Reference_Kernel_v2_1_0.py"

spec = importlib.util.spec_from_file_location("orl_money", kernel_path)
orl_money = importlib.util.module_from_spec(spec)
spec.loader.exec_module(orl_money)

balances = [
    orl_money.make_balance("AccountA", "1000", "USD"),
    orl_money.make_balance("AccountB", "0", "USD"),
]

observations = [
    orl_money.make_observation(
        "Source-A",
        "OBS-001",
        orl_money.make_fragment(
            "TX-001",
            "debit",
            "AccountA",
            "250",
            "USD",
        ),
    ),
    orl_money.make_observation(
        "Source-B",
        "OBS-002",
        orl_money.make_fragment(
            "TX-001",
            "credit",
            "AccountB",
            "250",
            "USD",
        ),
    ),
]

bundle = orl_money.resolve_financial_bundle(
    balances,
    observations,
    "OPEN",
)

print(bundle["result"])
print(orl_money.transaction_state_map(bundle))
print(orl_money.final_balance_map(bundle))
print(bundle["declared_balance_compatibility"]["state"])
print(bundle["self_verification"]["valid"])
```

Expected structural result:

```text
result = ACCEPTED
TX-001 = RESOLVED
AccountA|USD = 750
AccountB|USD = 250
declared-balance compatibility = COMPATIBLE
self verification = true
```

The basic construction path is:

`balances + observations -> resolve_financial_bundle -> inspect transaction state and projection`

The supplied observations remain evidence inputs.

ORL-Money does not interpret them as proof of account ownership, authorization, execution, posting, clearing, or settlement.

---

## 25. What ORL-Money Establishes

For the declared v2.1.0 reference contract, ORL-Money demonstrates:

- strict supported-input validation
- non-array collection refusal
- Unicode scalar-safe identifier validation
- exact integer-string money representation
- canonical structural identities
- claim identity separated from observation provenance
- exact observation deduplication
- deterministic transaction resolution
- explicit incompleteness
- explicit abstention
- witness-carrying transaction receipts
- account and unit projections
- unit-local conservation checks
- declared-balance compatibility
- OPEN and SEALED evidence boundaries
- merge-algebra invariants
- Python/browser reference parity
- independent reconstruction without producer import
- stable verifier failure reporting
- duplicate-key-safe JSON intake
- optional exact canonical-byte verification
- canonical frozen-corpus verification

---

## 26. What ORL-Money Does Not Establish

ORL-Money does not by itself establish:

- source-data truth
- account ownership
- authorization
- actual available funds
- reservations or holds
- payment execution
- account posting
- clearing
- settlement
- legal finality
- fraud prevention
- complete double-spend prevention
- consensus
- reliable broadcast
- Byzantine fault tolerance
- regulatory compliance
- production security
- universal financial correctness

---

## 27. Where to Read More

Core architecture:

```text
docs/ORL_Money_Core_Architecture_v2_1_0.txt
```

Conformance contract:

```text
docs/ORL_Money_Conformance_v2_1_0.txt
```

Verification procedure:

```text
docs/ORL_Money_Verification_Guide_v2_1_0.txt
```

Browser and console commands:

```text
docs/ORL_Money_v2_1_0_Console_Audit_Commands.txt
```

Frequently asked questions:

```text
docs/FAQ.md
```

---

## ⭐ One-Line Summary

ORL-Money transforms validated balance records and canonical money claims into deterministic witness-carrying financial resolutions, structural projections, compatibility results, evidence-boundary receipts, and independently reconstructable identities while keeping provenance and arrival order separate from financial multiplicity and transaction-classification authority.
