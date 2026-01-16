# Enzyme Program Contract Roadmap (v1.x)

This file is the public “anti-scope-creep” guardrail for Enzyme Program Contract v1.

Core rule: **v1 is frozen**. We do not change v1 schemas/layout/hashing/determinism rules in place. Breaking changes ship as v2.

## Allowed in v1 patch releases (v1.0.x)

Patch releases are strictly:

- Documentation improvements (examples, quickstarts, clarifications)
- CLI ergonomics (flags, output formatting, better error messages)
- Additional **optional** evidence modules (behind policy gates)
- Bug fixes that do **not** change the determinism envelope or hash/normalization rules

## Breaking changes (v2)

Anything that changes one of these is a v2:

- Bundle layout / stable paths
- Hash normalization rules (canonical JSON / pixel digest rules / zip metadata rules)
- Required header fields
- Determinism class semantics (D0/D1/D2 envelopes)

## Shipped

### v1.0.1 (patch)

- Docs: “60 second success” quickstart everywhere
- CI: website docs drift guard (quickstart + CI integration snippet)

### v1.0.2 (patch)

- Add `E_FOLD_001` stability proxy (explicit assumptions domain, bounded metrics, uncertainty block)
- Keep module gated behind policy (`requiredEvidence`) so old policies remain valid

## Next

### v1.0.3 (patch)

- Add a minimal **D2 conformance pack stub** (distribution-summary output + verifier checks)
- Improve `helix-cli enzyme diff` output (paths + tolerance reporting quality)

### v1.1.0 (minor; additive only)

- Add cascade kinetics evidence module (shape/contract only; still policy-gated)
- Expand conformance coverage (more negative cases + tamper vectors)
