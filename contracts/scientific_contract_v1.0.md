# Scientific Contract v1.0 (canonical)
Contract revision: 2025-12-24 — This page is the single source for what Helix guarantees (and does not guarantee) for v1 artifacts. Verification instructions live in the [Trust Kit](trust_kit.md).

## Scope
Applies to all Helix v1 artifacts and bundles emitted by CLI/Studio when headers are present. Meta files (`manifest.json`, `policy.json`, `model_semantics.json`, `ir.json`, `SHA256SUMS.txt`) remain hash-enforced but do not carry headers.

## Determinism classes
- **D0** best-effort; nondeterminism allowed.
- **D1** deterministic within declared float tolerances; seeded RNG, fixed locale.
- **D2** distribution-stable: verifier enforces policy metrics (below) under deterministic seeding; bitwise parity not required.

## Trust labels
- **core_verified**, **core_unverified**, **plugin_derived**, **viz_derived**. Trust can only downgrade; plugin/viz touch marks data as tainted.

## Guarantees (v1)
- Every artifact with a header includes: `artifactVersion`, `runId`, `createdUtc`, `engineVersion`, `policyHash`, `policyPath`, `policyName`, `semanticHash`, `backend`, `determinismClass`, `trust`, `trustCheckVersion` (`trust-check/v1`).
- Policy must be pinned (default) and match `policyHash`; semantic hash must match. Headers failing those hashes fail verification.
- Determinism class in header must align with policy; verifier enforces it.
- Trust labels must never upgrade across transforms; plugin-derived or viz-derived stays tainted.
- D2 policies must include `distributionChecks`; verifier computes all declared metrics plus `probMassSum` with declared tolerances and fails on drift.
- Pinned policy location: by default D2 policies must live under `policies/` (or `repro/policies/`); setting `HELIX_ALLOW_UNPINNED_POLICY=1` is an explicit, auditable downgrade (“not D2 pinned compliant”).
- Replay/headers are verified offline; no network required.
- escape hatch: if `HELIX_ALLOW_UNPINNED_POLICY=1` is set, the run is **not D2 pinned compliant** and must be treated as downgraded trust.

## Explicit non-guarantees
- Bitwise float parity across heterogeneous hardware (especially GPU); D2 is tolerance-based.
- Cross-vendor GPU equivalence or stability across arbitrary driver versions.
- OS-level sandboxing of arbitrary Python outside the plugin/extension host model.
- Automatic detection of all taint flows beyond declared headers.

## Compliance checklist (copy/paste)
- Policy file in `policies/`, `policyHash/Name/Path` present in artifact header.
- `trustCheckVersion = trust-check/v1` present.
- Profile used: `audit-strict` (or documented exception) via `HELIX_POLICY_PATH`; locale fixed (C.UTF-8).
- Trust-smoke CI passed (cpu-reference; native-cpu when available); docs build required.
- escape hatch (`HELIX_ALLOW_UNPINNED_POLICY=1`) not set; if set, run is non-compliant for D2 audits.

## GPU determinism envelope (v1 stance)
- **Guaranteed:** determinism within D1/D2 tolerances when run on the *same GPU architecture + driver range + math mode* recorded in `env_fingerprint`. Headers capture backend and env; use them for replay.
- **Required conditions:** recorded backend class, SM family/driver versions, deterministic math (no TF32/fast-math unless policy allows).
- **Not guaranteed:** byte-identical results across vendors, across major driver branches, or across differing GPU architectures.
- **Verification rule:** when `backend.kind = gpu`, trust verification fails unless the fingerprint contains driver, runtime, device UUID/compute capability, device_count, and math-mode flags (`tf32_allowed`, `fast_math_allowed`).

Example backend fingerprint (excerpt):

```json
{
  "backend": {
    "kind": "gpu",
    "details": {
      "os": "Linux-6.6.0-xyz",
      "python": "3.12.3",
      "cuda": {
        "available": true,
        "driver": "535.104",
        "runtime": "12.2",
        "device_count": 1,
        "tf32_allowed": false,
        "fast_math_allowed": false,
        "devices": [
          {"index": 0, "name": "A100-PCIE-40GB", "uuid": "GPU-abc", "compute_capability": "8.0"}
        ]
      },
      "complete": true
    }
  }
}
```

GPU fingerprint fields (canonical, schema_version=`backend-fingerprint/v1`)

| Field path | Required | Notes |
| --- | --- | --- |
| backend.kind | yes | `"gpu"` for GPU runs |
| backend.details.schema_version | yes | Must equal `backend-fingerprint/v1` |
| backend.details.os | yes | Host platform string |
| backend.details.python | yes | Python version |
| backend.details.cuda.schema_version | yes | Must equal `backend-fingerprint/v1` |
| backend.details.cuda.available | yes | Boolean |
| backend.details.cuda.driver | yes | CUDA driver version |
| backend.details.cuda.runtime | yes | CUDA runtime version |
| backend.details.cuda.device_count | yes | Integer >= 1 |
| backend.details.cuda.tf32_allowed | yes | Boolean (math mode) |
| backend.details.cuda.fast_math_allowed | yes | Boolean (math mode) |
| backend.details.cuda.devices[].name | yes | GPU model |
| backend.details.cuda.devices[].uuid or compute_capability | yes | At least one hardware identifier per device |
| backend.details.complete | yes | Computed completeness flag |

Compatibility: adding a new *required* fingerprint field increments the schema version; `backend-fingerprint/v1` is stable and enforced by verification. `backend-fingerprint/v1` is frozen—new required fields must use `backend-fingerprint/v2` (or later).***

## D2 distribution metrics (normative)
- Probability source: `probability`, else `probability_1e4/10000`.
- Metrics: `topKMass(k)`, `entropyBase2`, `noEditRate` (default predicate or policy selector), `scoreQuantiles(q)`, `probMassSum` (always checked).
- Defaults when tolerances omitted: topKMass abs 0.002 / rel 0.002; entropy abs 0.01 / rel 0.01; noEditRate abs 0.002 / rel 0.002; scoreQuantiles abs 0.02 / rel 0.01 (normalized: abs/rel 0.005); probMassSum abs 0.001 / rel 0.0.
- Ordering/tie-breaks: probability desc; ties broken by label → score → edited_sequence → diff hash.
- Replay hooks: `sampleCount` required; `requireDeterministicReplay` and `replaySampler` may be set; `requireDistributionHeaders` enforces headers on expected distributions.

## Verification path
- For humans: run `helix trust check --backend cpu-reference` (see [Trust Kit](trust_kit.md)).
- For CI: `trust-smoke` job (cpu-reference; native-cpu when available) + `docs-build` required; `HELIX_POLICY_PATH=policies/audit-strict.json` set.

## Temporary header exemptions
| Artifact type | Reason | Still enforced | Not present |
| --- | --- | --- | --- |
| manifest.json, policy.json, model_semantics.json, ir.json, SHA256SUMS.txt | Identity/meta only | File hashes | Contract header |
| *.helix session snapshots | Legacy UI payload | File hashes, schema invariants | Contract header (will be added in a future rev) |
