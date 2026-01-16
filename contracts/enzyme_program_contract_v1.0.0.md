# Enzyme Program Contract v1.0.0

This contract defines a **bytes-on-disk** artifact bundle for “cell-free enzyme design” that is deterministic (within a declared determinism class), policy-gated, replayable, and verifiable offline.

This does **not** prove biological truth, activity, yield, or safety. It proves compute provenance, the declared assumptions, and exactly what was computed under a pinned policy + semantics.

Compatibility and versioning rules for v1 are documented in `contracts/COMPATIBILITY_enzyme_contract_v1.md`.

## Quickstart (60 seconds)

Verify the golden test vector (from this repo):

```bash
git clone https://github.com/omniscoder/helix-public-assets
cd helix-public-assets/bundles/enzyme_program_contract/v1.0.0

sha256sum -c SHA256SUMS.txt
python3 ../../../../tools/verify_artifact_bundle.py golden_bundle.zip
```

Optional Helix CLI verification (integrity + schema + policy bindings):

```bash
pip install helix-governance==1.1.5
EXPECTED_BUNDLE_SHA="$(awk '{print $1}' golden_bundle.zip.sha256)"
helix-cli enzyme verify golden_bundle.zip --expected-bundle-sha256 "$EXPECTED_BUNDLE_SHA"
```

Build from the golden config/policy:

```bash
pip install helix-governance==1.1.5
helix-cli enzyme artifacts build --config golden_config.json --policy golden_policy.json --outdir out_bundle --backend cpu --zip
helix-cli enzyme verify out_bundle.zip
```

## CI integration (copy/paste)

Minimal verify in CI (self-contained schemas + machine-readable report):

```bash
helix-cli enzyme verify "$BUNDLE" --use-bundle-schemas --json-out verify_result.json
jq -e '.ok == true' verify_result.json
```

Verify with an authenticity anchor:

```bash
helix-cli enzyme verify "$BUNDLE" --expected-bundle-sha256 "$EXPECTED_SHA" --json-out verify_result.json
jq -e '.ok == true' verify_result.json
```

## Contract status (v1.0.0)

- Contract: Enzyme Program Contract v1.0.0
- Golden vector: `bundles/enzyme_program_contract/v1.0.0/golden_bundle.zip`
- Compatibility: `contracts/COMPATIBILITY_enzyme_contract_v1.md`
- Roadmap / patch policy: `contracts/ROADMAP_enzyme_contract.md`

## Published assets (v1.0.0)

Golden test vector:

- Asset: `golden_bundle.zip`
- Expected `bundle_sha256` (for `--expected-bundle-sha256`): `669d81dd53c7fdd8d67d7438b217aa850974fa75ed71d03684f1b11a329c0899`
- Verify:
  `helix-cli enzyme verify golden_bundle.zip --expected-bundle-sha256 669d81dd53c7fdd8d67d7438b217aa850974fa75ed71d03684f1b11a329c0899`

Note: `bundle_sha256` is the contract bundle digest (recomputed from `manifest.json` entries), not the SHA-256 of the zip file bytes.

## What an Enzyme Program is

An **Enzyme Program** is the unit of value: a long-lived, audit-ready decision stream.

Inputs → evidence → policy gate → (optional) exports → report → **artifact bundle** (manifest + hashes).

## Policy gating (the “no export without evidence” rule)

Policy is an explicit, pinned requirement set. Export artifacts are emitted **only if** the policy gate passes.

Baseline semantics:

- Evidence modules have `status: ok|fail|unknown`.
- **Unknown means fail** unless the policy explicitly allows unknown.
- Gate failures must be deterministic and audit-friendly (stable ordering, stable strings).

## Determinism classes

- **D0**: bitwise outputs (byte-identical artifacts expected).
- **D1**: deterministic within declared float tolerances (requires tolerance metadata).
- **D2**: distribution-stable (verifier enforces declared distribution checks).

## Bundle layout (v1)

Bundles are stable-path directories (or zips) with a `manifest.json` and per-file SHA-256.

Key paths:

- `inputs/config.json` (simulate config)
- `inputs/policy.json` (pinned policy)
- `inputs/ir.json` (compiled IR + semantic anchor)
- `inputs/model_semantics.json` (scorers + versions + tolerances)
- `inputs/schema_digest.json` (hashes of the schema set used for validation)
- `session/session.helix.json` (run ledger: ok/gated/failed + file refs)
- `evidence/<run_id>.evidence.json` (machine-readable “show your work”)
- `exports/<run_id>.export.json` (+ optional PNG + provenance sidecar)
- `reports/helix_enzyme_report_<run_id>.html`

## Offline verification

Offline verify must:

- Validate `manifest.json` integrity (per-file SHA-256 + bundle SHA).
- Validate JSON schema `kind/version` for every artifact.
- Enforce header bindings:
  - `policyHash` matches `inputs/policy.json`
  - `semanticHash` matches canonical `inputs/ir.json`
- Enforce trust labels (never upgrade across artifacts).
- Enforce schema-set integrity via `inputs/schema_digest.json` (prevents silent schema drift).

Integrity vs authenticity:

- `verify` proves **internal integrity** (hash-consistent, schema-valid, policy/semantic/schema hashes line up).
- Authenticity requires an **external trust anchor** (e.g., a published `bundle_sha256` or a signature).

Minimal authenticity anchor:

`helix-cli enzyme verify --expected-bundle-sha256 <bundle_sha256> <bundle_dir_or_zip>`

Schema pack modes:

- Installed-schema mode (default): verifier expects the installed schema pack to match the bundle.
- Bundle-schema mode: verifier validates using `schemas/enzyme/*.json` embedded in the bundle.

Wheel install note:

- Schemas are loaded from packaged resources (`helix.schema/enzyme`) when Helix is installed (wheel/venv).
- Repo-root `schemas/enzyme/` is for development/readability and must match the packaged set (CI enforces this).
- Bundle-schema mode is self-contained only if you authenticate the bundle (`--expected-bundle-sha256` or a signature/ledger anchor).

## Current evidence modules (v1 skeleton)

- `E_SEQ_001`: sequence sanity (length, forbidden motifs, fixed positions interpretation)
- `E_CELLFREE_001`: environment/cofactor compatibility checks
- `E_UNC_001`: explicit uncertainty/limits placeholder (must exist; “unknown” is still audit-relevant)

## How to build a bundle

Deterministic mode:

`PYTHONHASHSEED=0 HELIX_DETERMINISTIC=1 helix-cli enzyme artifacts build --config <config.json> --policy <policy.json> --outdir <bundle_dir> --backend cpu`

Zipped bundle (deterministic metadata):

`PYTHONHASHSEED=0 HELIX_DETERMINISTIC=1 helix-cli enzyme artifacts build --config <config.json> --policy <policy.json> --outdir <bundle_dir> --backend cpu --zip`

Skip embedding schemas (not recommended for long-term audits):

`helix-cli enzyme artifacts build --config <config.json> --policy <policy.json> --outdir <bundle_dir> --no-schemas`

## How to verify offline

`helix-cli enzyme verify <bundle_dir_or_zip>`

Verify using embedded bundle schemas (forward-compatible audits):

`helix-cli enzyme verify --use-bundle-schemas <bundle_dir_or_zip>`

Machine-readable verification report:

`helix-cli enzyme verify <bundle_dir_or_zip> --json-out verify_result.json`

## Bundle diff (developer tool)

Diff two bundles (dir or zip) to see what changed:

`helix-cli enzyme diff <bundleA> <bundleB>`

Machine-readable diff report:

`helix-cli enzyme diff <bundleA> <bundleB> --json-out diff_result.json`

## Conformance packs (anti-rot guardrails)

Contract v1 is expected to ship with:

- **D0 pack**: byte-identical rebuild + verify pass.
- **D1 pack**: tolerance metadata required + numeric comparisons within declared tolerances.
