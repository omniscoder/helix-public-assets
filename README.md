# Helix Public Assets

This repository is Helix’s public, stable distribution surface for artifacts that must be:

- Public
- Stable (additive-only; old assets do not change)
- Downloadable without context
- Cryptographically checkable (SHA-256)
- Usable by buyers, auditors, reviewers, and CI bots

This is not a development repo and not a mirror. Treat it as a trust anchor.

## Layout

- `schemas/`: Public JSON Schemas + `schemas/SHA256SUMS.txt`
- `contracts/`: Public, frozen contract docs + `contracts/SHA256SUMS.txt`
- `bundles/`: Golden/demo bundles (zips + hash anchors) + per-bundle `SHA256SUMS.txt`
- `tools/`: Minimal, Helix-independent verification helpers

## Verify (repo integrity)

```bash
python3 tools/verify_repo.py
```

## Verify (single artifact bundle)

```bash
python3 tools/verify_artifact_bundle.py bundles/enzyme_program_contract/v1.0.0/golden_bundle.zip
```

## Bundles (current)

- Enzyme contract golden: `bundles/enzyme_program_contract/v1.0.0/`
- Demo CRISPR (Helix v1.1.5): `bundles/helix_demo/v1.1.5/crispr/`
- Demo Prime (Helix v1.1.5): `bundles/helix_demo/v1.1.5/prime/`
