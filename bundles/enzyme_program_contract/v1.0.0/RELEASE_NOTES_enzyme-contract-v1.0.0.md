Enzyme Program Contract v1.0.0

This tag freezes Enzyme Program Contract v1 as a reproducible, policy-gated, offline-verifiable artifact bundle format.

Highlights
- Frozen v1 schemas + pinned schema digest; bundles embed a self-contained schema pack
- Deterministic artifacts build for directory + zip (D0) and tolerance-aware comparison for D1
- Strict manifest verification (no extra files), tamper detection, traversal/symlink hardening, case-collision guard
- Policy gating with deterministic failure ordering and “unknown ⇒ fail”
- Authenticity hook: `helix-cli enzyme verify --expected-bundle-sha256 ...`
- Tooling: `verify --json-out` (helix.enzyme.verify_result.v1) and `diff [--json-out]`

Golden test vector
- Asset: golden_bundle.zip
- Expected bundle SHA-256: 669d81dd53c7fdd8d67d7438b217aa850974fa75ed71d03684f1b11a329c0899
- Verify:
  `helix-cli enzyme verify golden_bundle.zip --expected-bundle-sha256 669d81dd53c7fdd8d67d7438b217aa850974fa75ed71d03684f1b11a329c0899`

References
- Contract doc: `docs/contracts/enzyme_program_contract_v1.md`
- Compatibility: `COMPATIBILITY.md`
