# Enzyme Program Contract v1 Compatibility

This repo contains a **frozen** Enzyme Program Contract v1.0.0 surface (schemas, hashing rules, bundle layout, and conformance tests).

If a change would make an existing v1 bundle unverifiable or change any of the hashed semantics, it must land as **v2** (new schema versions + explicit migration story), not as a “tweak” to v1.

## What’s stable in v1.0.0

- Bundle layout and required paths under `inputs/`, `session/`, `evidence/`, `exports/`, `reports/`.
- Canonical JSON hashing rules used for:
  - `policyHash = sha256(canonical_json(inputs/policy.json))`
  - `semanticHash = sha256(canonical_json(inputs/ir.json))`
  - schema pack digest (`inputs/schema_digest.json`)
- Manifest semantics:
  - every file is hashed in `manifest.json`
  - `bundle_sha256` is recomputed from the manifest entry list (path+sha256)
- Determinism class meaning for produced artifacts (D0/D1/D2) and the D0/D1 conformance expectations in `tests/test_enzyme_contract_v1.py`.
- Enzyme schema pack:
  - `schemas/enzyme/*_v1.json` and `schemas/enzyme/schema_digest_v1.json` are treated as immutable for v1.

## What can be added without breaking v1

- New **optional** fields in non-contract tooling outputs (e.g., CLI JSON reports), as long as existing fields keep their meaning.
- New evidence modules and new optional assets **as new files** (hashed in the manifest) when they don’t change existing required file formats.
- New CLI commands that do not change bundle writers/verifiers.

## What is breaking (requires v2)

- Any change to canonicalization or hashing (policy/semantic/schema digest, bundle hash rules).
- Any change to required file paths or naming rules in the bundle layout.
- Any change to required header fields, trust label semantics, or determinism envelope semantics.
- Any change to the v1 schema pack that would change `schema_digest_v1.json` or invalidate existing bundles in installed-schema verification mode.

## Verification modes (installed vs bundle schemas)

- **Installed-schema mode** (default): verification expects the installed schema pack digest to match the bundle’s declared digest.
- **Bundle-schema mode** (`helix-cli enzyme verify --use-bundle-schemas`): verification uses the schema pack embedded in the bundle.

Bundle-schema mode is intended for long-lived audits, but should be paired with an authenticity anchor (for example `--expected-bundle-sha256` or a signature/ledger record).

